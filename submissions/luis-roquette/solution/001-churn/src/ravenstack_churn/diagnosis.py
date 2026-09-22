from __future__ import annotations

import warnings
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tools.sm_exceptions import (
    PerfectSeparationError,
    PerfectSeparationWarning,
    SingularMatrixWarning,
)

from .config import MIN_COVERAGE, MIN_SEGMENT_ACCOUNTS, MIN_SEGMENT_CHURNS, SCORING_CUTOFF

CANDIDATES = {
    "F-product-usage-drop": ("usage_change_30_vs_90", "lower", "product", "le", -0.30),
    "F-product-errors": ("error_rate_30d", "higher", "product", "ge", 0.10),
    "F-support-escalation": ("escalations_90d", "higher", "support", "ge", 1),
    "F-support-satisfaction": (
        "mean_satisfaction_90d",
        "lower",
        "support",
        "le",
        3.0,
    ),
    "F-commercial-downgrade": (
        "downgrade_90d",
        "higher",
        "commercial",
        "eq",
        True,
    ),
    "F-commercial-renewal": (
        "auto_renew_off",
        "higher",
        "commercial",
        "eq",
        True,
    ),
}

ACTIONS = {
    "product": {
        "immediate_action": "CS revisa em 7 dias as contas expostas e confirma o fluxo que perdeu uso.",
        "structural_action": "Produto e Engenharia corrigem em 30–90 dias o fluxo corroborado e medem a coorte.",
        "owner": "Head de Produto",
        "success_metric": "MRR perdido e uso de 30 dias da coorte exposta",
    },
    "support": {
        "immediate_action": "Suporte revisa em 7 dias escaladas abertas das contas expostas e define responsável.",
        "structural_action": "Support Ops ajusta em 30–90 dias triagem e SLA da causa corroborada.",
        "owner": "Head de Suporte",
        "success_metric": "MRR perdido, taxa de escalada e satisfação da coorte exposta",
    },
    "commercial": {
        "immediate_action": "CS revisa em 7 dias renovações próximas e mudanças contratuais das contas expostas.",
        "structural_action": "RevOps testa em 30–90 dias o playbook comercial na coorte exposta.",
        "owner": "Head de Receita",
        "success_metric": "MRR perdido e renovação da coorte exposta",
    },
}

CONTROL_COLUMNS = (
    "industry",
    "country",
    "referral_source",
    "plan_tier",
    "billing_frequency",
    "is_trial",
    "mrr_active",
    "seats",
    "tenure_days",
)


def build_diagnostic_snapshot(panel: pd.DataFrame) -> pd.DataFrame:
    labeled = panel.loc[
        panel["churn_next_30d"].notna() & panel["cutoff"].le(pd.Timestamp("2024-11-30"))
    ].copy()
    if "has_active_subscription" in labeled:
        labeled = labeled.loc[labeled["has_active_subscription"].fillna(False)]
    if labeled.empty:
        return labeled.reset_index(drop=True)
    common_cutoff = labeled["cutoff"].max()
    return labeled.loc[labeled["cutoff"].eq(common_cutoff)].reset_index(drop=True)


def _fit_association(snapshot: pd.DataFrame, feature: str) -> dict[str, Any]:
    coverage = float(snapshot[feature].notna().mean()) if len(snapshot) else 0.0
    data = snapshot.loc[snapshot[feature].notna()].copy()
    if data[feature].nunique(dropna=True) < 2:
        return {"failure_reason": "zero_variance", "coverage": coverage}
    if data["churn_next_30d"].nunique(dropna=True) < 2:
        return {"failure_reason": "single_class", "coverage": coverage}

    candidate = data[feature].astype(float).rename("candidate")
    controls = data[[column for column in CONTROL_COLUMNS if column in data]].copy()
    controls["log_mrr_active"] = np.log1p(pd.to_numeric(controls.pop("mrr_active")))
    controls["cutoff_quarter"] = data["cutoff"].dt.to_period("Q").astype(str)
    categorical = [
        column
        for column in controls
        if controls[column].dtype == "object" or isinstance(controls[column].dtype, pd.StringDtype)
    ]
    controls = pd.get_dummies(controls, columns=categorical, drop_first=True, dtype=float)
    controls = controls.apply(pd.to_numeric, errors="coerce").astype(float)
    design = pd.concat([candidate, controls], axis=1).replace([np.inf, -np.inf], np.nan)
    usable = design.notna().all(axis=1)
    design = sm.add_constant(design.loc[usable], has_constant="add")
    outcome = data.loc[usable, "churn_next_30d"].astype(float)
    if outcome.nunique() < 2 or design["candidate"].nunique() < 2:
        return {"failure_reason": "insufficient_complete_cases", "coverage": coverage}

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = sm.GLM(outcome, design, family=sm.families.Binomial()).fit(cov_type="HC3")
        if any(
            issubclass(item.category, (PerfectSeparationWarning, SingularMatrixWarning))
            for item in caught
        ):
            raise ValueError("separation_or_singular_design")
        coefficient = float(result.params["candidate"])
        ci = result.conf_int().loc["candidate"]
        ci_low, ci_high = float(np.exp(ci.iloc[0])), float(np.exp(ci.iloc[1]))
        odds_ratio = float(np.exp(coefficient))
        if not result.converged or not np.isfinite([coefficient, ci_low, ci_high]).all():
            raise ValueError("non_finite_or_non_converged")
        return {
            "coefficient": coefficient,
            "odds_ratio": odds_ratio,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "coverage": coverage,
            "failure_reason": None,
        }
    except (ValueError, FloatingPointError, np.linalg.LinAlgError, PerfectSeparationError) as error:
        return {
            "failure_reason": f"model_failure:{type(error).__name__}",
            "coverage": coverage,
        }


def _exposure_mask(series: pd.Series, operator: str, threshold: object) -> pd.Series:
    if operator == "le":
        return series.le(threshold)
    if operator == "ge":
        return series.ge(threshold)
    if operator == "eq":
        return series.eq(threshold)
    raise ValueError(f"unknown exposure operator: {operator}")


def _reason_corroborates(
    driver_group: str,
    exposed_accounts: set[str],
    churn_events: pd.DataFrame,
) -> bool:
    terminal = (
        churn_events.loc[~churn_events["is_reactivation"].fillna(False)]
        .sort_values(["churn_date", "account_id"])
        .drop_duplicates("account_id", keep="first")
        .copy()
    )
    if len(terminal) < MIN_SEGMENT_CHURNS:
        return False
    patterns = {
        "product": r"product|feature|usability|technical",
        "support": r"support|service|sla",
        "commercial": r"price|pricing|competitor|budget|commercial",
    }
    reason_match = (
        terminal["reason_code"]
        .astype("string")
        .str.contains(patterns[driver_group], case=False, na=False, regex=True)
    )
    overall = float(reason_match.mean())
    exposed = terminal["account_id"].isin(exposed_accounts)
    if not exposed.any() or overall == 0:
        return False
    return bool(reason_match.loc[exposed].mean() / overall >= 1.25)


def rank_findings(findings: pd.DataFrame) -> pd.DataFrame:
    ranked = findings.copy()
    ranked["priority_rank"] = pd.Series(pd.NA, index=ranked.index, dtype="Int64")
    accepted = ranked["confidence"].eq("accepted")
    actionability = ranked.get("actionability", pd.Series("structural-only", index=ranked.index))
    ranked["_actionability_order"] = actionability.map(
        {"immediate": 0, "structural-only": 1}
    ).fillna(2)
    accepted_order = ranked.loc[accepted].sort_values(
        ["mrr_exposed_max", "affected_accounts", "_actionability_order"],
        ascending=[False, False, True],
    )
    ranked.loc[accepted_order.index, "priority_rank"] = range(1, len(accepted_order) + 1)
    return (
        ranked.sort_values(
            ["priority_rank", "mrr_exposed_max", "affected_accounts"],
            ascending=[True, False, False],
            na_position="last",
        )
        .drop(columns="_actionability_order")
        .reset_index(drop=True)
    )


def _segment_metrics(snapshot: pd.DataFrame) -> pd.DataFrame:
    if snapshot.empty:
        return pd.DataFrame()
    data = snapshot.copy()
    overall_churn_rate = float(data["churn_next_30d"].astype(int).mean())
    data["mrr_band"] = pd.cut(
        data["mrr_active"],
        bins=[-np.inf, 500, 2_000, np.inf],
        labels=["low", "mid", "high"],
    )
    rows = []
    for dimension in (
        "industry",
        "country",
        "referral_source",
        "plan_tier",
        "billing_frequency",
        "is_trial",
        "mrr_band",
    ):
        for value, group in data.groupby(dimension, dropna=False, observed=True):
            churn = group["churn_next_30d"].astype(int)
            churn_count = int(churn.sum())
            rows.append(
                {
                    "dimension": dimension,
                    "segment": str(value),
                    "sample_size": len(group),
                    "churn_count": churn_count,
                    "churn_rate": float(churn.mean()),
                    "overall_churn_rate": overall_churn_rate,
                    "churn_rate_delta": float(churn.mean() - overall_churn_rate),
                    "relative_risk": (
                        float(churn.mean() / overall_churn_rate) if overall_churn_rate else np.nan
                    ),
                    "mrr_lost": float(
                        group.get("mrr_lost_next_30d", group["mrr_active"])
                        .where(churn.eq(1), 0)
                        .sum()
                    ),
                    "mrr_exposed": float(group["mrr_active"].sum()),
                    "coverage": float(group["churn_next_30d"].notna().mean()),
                    "confidence": (
                        "eligible"
                        if len(group) >= MIN_SEGMENT_ACCOUNTS and churn_count >= MIN_SEGMENT_CHURNS
                        else "inconclusive"
                    ),
                }
            )
    return pd.DataFrame(rows)


def evaluate_candidates(
    observed: pd.DataFrame,
    strict: pd.DataFrame,
    churn_events: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    observed_snapshot = build_diagnostic_snapshot(observed)
    strict_snapshot = build_diagnostic_snapshot(strict)
    scoring = strict.loc[strict["cutoff"].eq(SCORING_CUTOFF)].copy()
    rows = []

    for finding_id, candidate in CANDIDATES.items():
        feature, expected_direction, driver_group, operator, threshold = candidate
        observed_fit = _fit_association(observed_snapshot, feature)
        strict_fit = _fit_association(strict_snapshot, feature)
        failure_reason = strict_fit.get("failure_reason") or observed_fit.get("failure_reason")
        observed_effect = observed_fit.get("coefficient", np.nan)
        strict_effect = strict_fit.get("coefficient", np.nan)
        sensitivity_delta = (
            abs(strict_effect - observed_effect) / max(abs(observed_effect), 1e-9)
            if pd.notna(observed_effect) and pd.notna(strict_effect)
            else np.nan
        )
        direction_stable = bool(
            pd.notna(observed_effect)
            and pd.notna(strict_effect)
            and np.sign(observed_effect) == np.sign(strict_effect)
            and sensitivity_delta <= 0.25
        )
        expected = strict_effect < 0 if expected_direction == "lower" else strict_effect > 0
        interval_passes = bool(
            strict_fit.get("ci_high", np.inf) < 1
            if expected_direction == "lower"
            else strict_fit.get("ci_low", -np.inf) > 1
        )
        exposure = _exposure_mask(strict_snapshot[feature], operator, threshold).fillna(False)
        exposed_snapshot = strict_snapshot.loc[exposure]
        exposed_accounts = set(exposed_snapshot["account_id"].astype(str))
        sample_passes = bool(
            len(exposed_snapshot) >= MIN_SEGMENT_ACCOUNTS
            and int(exposed_snapshot["churn_next_30d"].sum()) >= MIN_SEGMENT_CHURNS
            and strict_fit.get("coverage", 0.0) >= MIN_COVERAGE
        )
        corroborated = _reason_corroborates(driver_group, exposed_accounts, churn_events)
        accepted = bool(
            not failure_reason
            and direction_stable
            and expected
            and interval_passes
            and sample_passes
            and corroborated
        )
        if not failure_reason and not direction_stable:
            failure_reason = "chronology_instability"
        elif not failure_reason and not sample_passes:
            failure_reason = "sample_or_coverage_gate"
        elif not failure_reason and not corroborated:
            failure_reason = "cross_table_gate"
        elif not failure_reason and (not expected or not interval_passes):
            failure_reason = "association_gate"

        scoring_exposure = (
            _exposure_mask(scoring[feature], operator, threshold).fillna(False)
            if feature in scoring
            else pd.Series(False, index=scoring.index)
        )
        exposed_scoring = scoring.loc[scoring_exposure].drop_duplicates("account_id")
        actions = ACTIONS[driver_group]
        rows.append(
            {
                "finding_id": finding_id,
                "driver_group": driver_group,
                "claim": f"{feature} está associado ao churn futuro de 30 dias.",
                "evidence_level": "association_controlled" if accepted else "inconclusive",
                "adjusted_odds_ratio": strict_fit.get("odds_ratio", np.nan),
                "ci_low": strict_fit.get("ci_low", np.nan),
                "ci_high": strict_fit.get("ci_high", np.nan),
                "observed_effect": observed_effect,
                "strict_effect": strict_effect,
                "sensitivity_delta": sensitivity_delta,
                "source_tables": "accounts|subscriptions|feature_usage|support_tickets|churn_events",
                "affected_accounts": len(exposed_scoring),
                "mrr_exposed_max": float(exposed_scoring["mrr_active"].sum()),
                "confidence": "accepted" if accepted else "inconclusive",
                "failure_reason": failure_reason,
                "counterevidence": "A leitura observed/strict e o intervalo são mantidos juntos.",
                "limitation": "Dados observacionais sustentam associação, não causalidade comprovada.",
                "actionability": "immediate",
                **actions,
            }
        )

    return rank_findings(pd.DataFrame(rows)), _segment_metrics(strict_snapshot)


def _monthly_values(frame: pd.DataFrame, value_column: str) -> pd.Series:
    return frame.groupby("cutoff", observed=True)[value_column].mean().sort_index()


def build_claim_checks(strict_panel: pd.DataFrame) -> pd.DataFrame:
    labeled = strict_panel.loc[strict_panel["churn_next_30d"].notna()].copy()
    if "has_active_subscription" in labeled:
        labeled = labeled.loc[labeled["has_active_subscription"].fillna(False)]
    cutoffs = sorted(labeled["cutoff"].drop_duplicates())[-6:]
    labeled = labeled.loc[labeled["cutoff"].isin(cutoffs)]
    cohorts = {
        "overall": labeled,
        "retained": labeled.loc[labeled["churn_next_30d"].eq(0)],
        "churn_next_30d": labeled.loc[labeled["churn_next_30d"].eq(1)],
    }
    rows = []

    for cohort_name, cohort in cohorts.items():
        usage = cohort.loc[
            cohort["usage_coverage_30d"].fillna(False) & cohort["usage_count_30d"].notna()
        ].copy()
        usage["daily_usage"] = usage["usage_count_30d"] / 30
        monthly_usage = _monthly_values(usage, "daily_usage")
        if len(monthly_usage) >= 2:
            slope = float(np.polyfit(np.arange(len(monthly_usage)), monthly_usage.values, 1)[0])
            usage_start, usage_end = float(monthly_usage.iloc[0]), float(monthly_usage.iloc[-1])
            endpoint_change = usage_end - usage_start
            status = (
                "up" if endpoint_change > 1e-9 else "down" if endpoint_change < -1e-9 else "flat"
            )
        else:
            slope, usage_start, usage_end, status = np.nan, np.nan, np.nan, "insufficient"
        rows.append(
            {
                "claim_id": "C-usage-growth",
                "cohort": cohort_name,
                "start_value": usage_start,
                "end_value": usage_end,
                "slope": slope,
                "status": status,
                "coverage": float(len(usage) / len(cohort)) if len(cohort) else 0.0,
                "cutoff_start": min(cutoffs) if cutoffs else pd.NaT,
                "cutoff_end": max(cutoffs) if cutoffs else pd.NaT,
                "limitation": "Tendência descritiva; não identifica causa.",
            }
        )

        valid_satisfaction = cohort.loc[
            cohort["mean_satisfaction_90d"].notna() & cohort["satisfaction_responses_90d"].gt(0)
        ].copy()
        monthly_satisfaction = valid_satisfaction.groupby("cutoff", observed=True).apply(
            lambda group: np.average(
                group["mean_satisfaction_90d"],
                weights=group["satisfaction_responses_90d"],
            ),
            include_groups=False,
        )
        responses = float(valid_satisfaction["satisfaction_responses_90d"].sum())
        tickets = float(cohort.get("tickets_90d", pd.Series(0, index=cohort.index)).sum())
        coverage = responses / tickets if tickets else np.nan
        weighted_mean = (
            float(
                np.average(
                    valid_satisfaction["mean_satisfaction_90d"],
                    weights=valid_satisfaction["satisfaction_responses_90d"],
                )
            )
            if responses
            else np.nan
        )
        status = (
            "insufficient"
            if pd.isna(weighted_mean) or pd.isna(coverage)
            else "ok"
            if weighted_mean >= 4.0 and coverage >= MIN_COVERAGE
            else "concern"
        )
        rows.append(
            {
                "claim_id": "C-satisfaction-ok",
                "cohort": cohort_name,
                "start_value": (
                    float(monthly_satisfaction.iloc[0]) if len(monthly_satisfaction) else np.nan
                ),
                "end_value": (
                    float(monthly_satisfaction.iloc[-1]) if len(monthly_satisfaction) else np.nan
                ),
                "slope": np.nan,
                "status": status,
                "coverage": coverage,
                "cutoff_start": min(cutoffs) if cutoffs else pd.NaT,
                "cutoff_end": max(cutoffs) if cutoffs else pd.NaT,
                "limitation": "Média ponderada somente entre tickets com resposta.",
            }
        )

    return pd.DataFrame(rows)
