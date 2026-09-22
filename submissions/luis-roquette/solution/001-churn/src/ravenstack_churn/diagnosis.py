from __future__ import annotations

import warnings
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.proportion import proportion_confint
from statsmodels.tools.sm_exceptions import (
    PerfectSeparationError,
    PerfectSeparationWarning,
    SingularMatrixWarning,
)

from .config import (
    BOOTSTRAP_REPLICATES,
    HISTORICAL_START,
    MIN_COVERAGE,
    MIN_SEGMENT_ACCOUNTS,
    MIN_SEGMENT_CHURNS,
    OBSERVATION_END,
    RANDOM_SEED,
    RECENT_PERIOD,
    REFERENCE_PERIOD,
    SCORING_CUTOFF,
)
from .contracts import _coerce_tables
from .panel import mrr_lost_at_churn, select_first_terminal_events

HISTORICAL_DIMENSIONS = (
    "industry",
    "country",
    "referral_source",
    "plan_tier",
    "billing_frequency",
    "is_trial",
    "mrr_band",
)

MONTHLY_CHURN_COLUMNS = (
    "evidence_id",
    "period_start",
    "period_end",
    "population",
    "chronology",
    "status",
    "limitation",
    "source_refs",
    "calculation",
    "period_kind",
    "dimension",
    "segment",
    "comparison_kind",
    "at_risk_accounts",
    "unique_accounts",
    "terminal_churns",
    "new_accounts",
    "entrant_churns",
    "excluded_events",
    "observation_complete",
    "churn_rate",
    "rate_unit",
    "ci_low",
    "ci_high",
    "ci_level",
    "ci_method",
    "comparator_id",
    "comparator_rate",
    "relative_risk",
    "rr_ci_low",
    "rr_ci_high",
    "rate_difference",
    "difference_ci_low",
    "difference_ci_high",
    "mrr_lost",
    "mrr_known_accounts",
    "mrr_unknown_accounts",
    "mrr_exposed",
    "mrr_exposed_as_of",
    "currency",
    "financial_unit",
)

REASON_DISTRIBUTION_COLUMNS = (
    "evidence_id",
    "period_start",
    "period_end",
    "population",
    "chronology",
    "status",
    "limitation",
    "source_refs",
    "calculation",
    "reason_code",
    "terminal_accounts",
    "eligible_events",
    "excluded_events",
    "share",
    "unit",
    "ci_low",
    "ci_high",
    "ci_method",
    "ci_level",
    "comparator_id",
    "mrr_lost",
    "mrr_known_accounts",
    "mrr_unknown_accounts",
    "currency",
)

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


def _wilson(count: int, total: int) -> tuple[float, float]:
    if total <= 0:
        return np.nan, np.nan
    low, high = proportion_confint(count, total, alpha=0.05, method="wilson")
    return float(low), float(high)


def _bootstrap_rate_contrast(
    account_months: pd.DataFrame,
    target: pd.Series,
    comparator: pd.Series | None,
    replicates: int = BOOTSTRAP_REPLICATES,
    seed: int = RANDOM_SEED,
) -> dict[str, object]:
    work = account_months.assign(
        _target=target,
        _comparator=False if comparator is None else comparator,
    )
    work = work.loc[work["_target"] | work["_comparator"]]
    accounts = pd.Index(work["account_id"].astype(str).unique())
    if len(accounts) < 2:
        return {"status": "unavailable", "limitation": "fewer_than_two_accounts"}

    grouped = work.groupby("account_id", sort=True)
    vectors = pd.DataFrame(
        {
            "target_den": grouped["_target"].sum(),
            "target_num": grouped.apply(
                lambda group: int((group["_target"] & group["is_terminal_churn"]).sum()),
                include_groups=False,
            ),
            "comparator_den": grouped["_comparator"].sum(),
            "comparator_num": grouped.apply(
                lambda group: int((group["_comparator"] & group["is_terminal_churn"]).sum()),
                include_groups=False,
            ),
        }
    ).reindex(accounts, fill_value=0)
    weights = np.random.default_rng(seed).multinomial(
        len(accounts), np.full(len(accounts), 1 / len(accounts)), size=replicates
    )
    target_den = weights @ vectors["target_den"].to_numpy()
    comparator_den = weights @ vectors["comparator_den"].to_numpy()
    target_rate = np.divide(
        weights @ vectors["target_num"].to_numpy(),
        target_den,
        out=np.full(replicates, np.nan),
        where=target_den > 0,
    )
    valid_target = target_rate[np.isfinite(target_rate)]
    if len(valid_target) < 0.95 * replicates:
        return {"status": "unavailable", "limitation": "insufficient_valid_bootstrap_replicates"}

    result: dict[str, object] = {
        "status": "available",
        "limitation": "",
        "target_ci_low": float(np.quantile(valid_target, 0.025)),
        "target_ci_high": float(np.quantile(valid_target, 0.975)),
    }
    if comparator is None:
        return result

    comparator_rate = np.divide(
        weights @ vectors["comparator_num"].to_numpy(),
        comparator_den,
        out=np.full(replicates, np.nan),
        where=comparator_den > 0,
    )
    difference = target_rate - comparator_rate
    ratio = np.divide(
        target_rate,
        comparator_rate,
        out=np.full(replicates, np.nan),
        where=comparator_rate > 0,
    )
    valid_difference = difference[np.isfinite(difference)]
    valid_ratio = ratio[np.isfinite(ratio)]
    if len(valid_difference) < 0.95 * replicates:
        return {"status": "unavailable", "limitation": "insufficient_valid_bootstrap_replicates"}

    result.update(
        difference_ci_low=float(np.quantile(valid_difference, 0.025)),
        difference_ci_high=float(np.quantile(valid_difference, 0.975)),
    )
    if len(valid_ratio) >= 0.95 * replicates:
        result.update(
            rr_ci_low=float(np.quantile(valid_ratio, 0.025)),
            rr_ci_high=float(np.quantile(valid_ratio, 0.975)),
        )
    else:
        result.update(rr_ci_low=np.nan, rr_ci_high=np.nan)
        result["limitation"] = "relative_risk_bootstrap_unavailable"
    return result


def _active_subscription_attributes(
    subscriptions: pd.DataFrame, account_ids: pd.Index, as_of: pd.Timestamp
) -> pd.DataFrame:
    active = subscriptions.loc[
        subscriptions["account_id"].isin(account_ids)
        & subscriptions["start_date"].le(as_of)
        & (subscriptions["end_date"].isna() | subscriptions["end_date"].gt(as_of))
    ].drop_duplicates("subscription_id")
    rows = []
    for account_id in account_ids:
        history = subscriptions.loc[subscriptions["account_id"].eq(account_id)]
        group = active.loc[active["account_id"].eq(account_id)]

        def one_or_mixed(column: str, active_group: pd.DataFrame = group) -> object:
            values = active_group[column].dropna().unique()
            if not len(values):
                return "unknown"
            return values[0] if len(values) == 1 else "mixed"

        mrr = group["mrr_amount"]
        mrr_active = np.nan if history.empty or mrr.isna().any() else float(mrr.sum())
        rows.append(
            {
                "account_id": account_id,
                "plan_tier": one_or_mixed("plan_tier"),
                "billing_frequency": one_or_mixed("billing_frequency"),
                "is_trial": one_or_mixed("is_trial"),
                "mrr_active": mrr_active,
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        return pd.DataFrame(
            columns=[
                "account_id",
                "plan_tier",
                "billing_frequency",
                "is_trial",
                "mrr_active",
                "mrr_band",
            ]
        )
    result["mrr_band"] = (
        pd.cut(
            result["mrr_active"],
            bins=[-np.inf, 500, 2_000, np.inf],
            labels=["low", "mid", "high"],
        )
        .astype("string")
        .fillna("unknown")
    )
    return result


def _historical_account_months(
    tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame
) -> pd.DataFrame:
    accounts = tables["accounts"]
    subscriptions = tables["subscriptions"]
    terminal = terminal_events.set_index("account_id")
    months = pd.date_range(HISTORICAL_START, RECENT_PERIOD[1], freq="MS")
    rows = []
    for month_start in months:
        month_end = month_start + pd.offsets.MonthBegin(1)
        churn_date = accounts["account_id"].map(terminal["churn_date"])
        eligible = accounts["signup_date"].le(month_start) & (
            churn_date.isna() | churn_date.ge(month_start)
        )
        at_risk = accounts.loc[eligible].drop(columns=["plan_tier", "is_trial"]).copy()
        attributes = _active_subscription_attributes(
            subscriptions, pd.Index(at_risk["account_id"]), month_start
        )
        at_risk = at_risk.merge(attributes, on="account_id", how="left", validate="one_to_one")
        at_risk[["plan_tier", "billing_frequency", "is_trial", "mrr_band"]] = at_risk[
            ["plan_tier", "billing_frequency", "is_trial", "mrr_band"]
        ].fillna("unknown")
        at_risk["period_start"] = month_start
        at_risk["period_end"] = month_end - pd.Timedelta(days=1)
        at_risk["terminal_date"] = at_risk["account_id"].map(terminal["churn_date"])
        at_risk["is_terminal_churn"] = at_risk["terminal_date"].ge(month_start) & at_risk[
            "terminal_date"
        ].lt(month_end)
        rows.append(at_risk)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def _financial_loss(lost: pd.Series, account_ids: pd.Series) -> tuple[float, int, int]:
    if account_ids.empty:
        return 0.0, 0, 0
    values = account_ids.map(lost)
    known = int(values.notna().sum())
    unknown = int(values.isna().sum())
    return (float(values.dropna().sum()) if known else np.nan, known, unknown)


def build_monthly_churn(
    tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame
) -> pd.DataFrame:
    parsed = _coerce_tables(tables)
    terminal = terminal_events.copy()
    if terminal.empty:
        terminal = terminal.reindex(columns=parsed["churn_events"].columns)
    selected, exclusions = select_first_terminal_events(
        parsed["accounts"], parsed["churn_events"], OBSERVATION_END
    )
    if set(terminal.get("churn_event_id", [])) != set(selected.get("churn_event_id", [])):
        raise ValueError("terminal_events must match shared terminal selection")
    account_months = _historical_account_months(parsed, terminal)
    terminal_series = terminal.set_index("account_id")["churn_date"]
    lost = mrr_lost_at_churn(parsed["subscriptions"], terminal_series)
    raw_exclusions = exclusions.merge(
        parsed["churn_events"][["churn_event_id", "churn_date"]],
        on="churn_event_id",
        how="left",
    )
    rows: list[dict[str, object]] = []

    def add_row(
        data: pd.DataFrame,
        period_start: pd.Timestamp,
        period_end: pd.Timestamp,
        period_kind: str,
        dimension: str,
        segment: str,
        comparison_kind: str = "none",
        comparator: pd.DataFrame | None = None,
        comparator_id: str | None = None,
    ) -> None:
        churned = data.loc[data["is_terminal_churn"]]
        count = len(churned)
        denominator = len(data)
        rate = count / denominator if denominator else np.nan
        ci_low, ci_high = _wilson(count, denominator)
        mrr_lost, known, unknown = _financial_loss(lost, churned["account_id"])
        is_month = period_kind == "month"
        new_mask = parsed["accounts"]["signup_date"].gt(period_start) & parsed["accounts"][
            "signup_date"
        ].le(period_end)
        new_accounts = int(new_mask.sum()) if dimension == "all" else 0
        entrant_ids = set(parsed["accounts"].loc[new_mask, "account_id"])
        entrant_churns = (
            int(
                (
                    terminal["account_id"].isin(entrant_ids)
                    & terminal["churn_date"].ge(period_start)
                    & terminal["churn_date"].le(period_end)
                ).sum()
            )
            if dimension == "all"
            else 0
        )
        excluded_events = (
            int(
                raw_exclusions.loc[
                    raw_exclusions["churn_date"].ge(period_start)
                    & raw_exclusions["churn_date"].le(period_end),
                    "churn_event_id",
                ].nunique()
            )
            if dimension == "all"
            else 0
        )
        status = "available" if denominator else "unavailable"
        limitation = "" if denominator else "zero_denominator"
        comparator_rate = relative_risk = rate_difference = np.nan
        rr_low = rr_high = diff_low = diff_high = np.nan
        target_mask = account_months.index.isin(data.index)
        if not is_month and denominator:
            period_bootstrap = _bootstrap_rate_contrast(account_months, target_mask, None)
            ci_low = period_bootstrap.get("target_ci_low", np.nan)
            ci_high = period_bootstrap.get("target_ci_high", np.nan)
            if period_bootstrap["status"] != "available":
                status = "inconclusive"
                limitation = str(period_bootstrap["limitation"])
        if comparator is not None and denominator:
            comparator_rate = (
                float(comparator["is_terminal_churn"].mean()) if len(comparator) else np.nan
            )
            relative_risk = (
                float(rate / comparator_rate)
                if pd.notna(rate) and pd.notna(comparator_rate) and comparator_rate > 0
                else np.nan
            )
            rate_difference = (
                float(rate - comparator_rate)
                if pd.notna(rate) and pd.notna(comparator_rate)
                else np.nan
            )
            contrast = _bootstrap_rate_contrast(
                account_months,
                target_mask,
                account_months.index.isin(comparator.index),
            )
            rr_low = contrast.get("rr_ci_low", np.nan)
            rr_high = contrast.get("rr_ci_high", np.nan)
            diff_low = contrast.get("difference_ci_low", np.nan)
            diff_high = contrast.get("difference_ci_high", np.nan)
            if contrast["status"] != "available":
                status = "inconclusive"
                limitation = str(contrast["limitation"])
            elif contrast.get("limitation"):
                limitation = str(contrast["limitation"])
            if comparison_kind == "segment_complement" and (
                data["account_id"].nunique() < MIN_SEGMENT_ACCOUNTS
                or count < MIN_SEGMENT_CHURNS
                or comparator["account_id"].nunique() < MIN_SEGMENT_ACCOUNTS
                or int(comparator["is_terminal_churn"].sum()) < MIN_SEGMENT_CHURNS
            ):
                status = "inconclusive"
                limitation = "insufficient_segment_or_complement_sample"
        mrr_exposed = (
            np.nan
            if not is_month or data["mrr_active"].isna().any()
            else float(data["mrr_active"].sum())
        )
        financial_limitations = []
        if unknown:
            financial_limitations.append("mrr_lost_unknown_for_some_accounts")
        if is_month and data["mrr_active"].isna().any():
            financial_limitations.append("mrr_exposed_unknown_for_some_accounts")
        if not is_month:
            financial_limitations.append("mrr_exposed_not_aggregated_across_months")
        if financial_limitations:
            limitation = "|".join(filter(None, [limitation, *financial_limitations]))
            if status == "available" and (
                unknown or (is_month and data["mrr_active"].isna().any())
            ):
                status = "partial"
        evidence_id = (
            f"churn:{period_kind}:{period_start.date()}:{period_end.date()}:"
            f"{dimension}:{segment}:{comparison_kind}"
        )
        rows.append(
            {
                "evidence_id": evidence_id,
                "period_start": period_start,
                "period_end": period_end,
                "population": "registered_at_start",
                "chronology": "shared",
                "status": status,
                "limitation": limitation,
                "source_refs": "accounts|subscriptions|churn_events",
                "calculation": "build_monthly_churn:v1",
                "period_kind": period_kind,
                "dimension": dimension,
                "segment": segment,
                "comparison_kind": comparison_kind,
                "at_risk_accounts": denominator,
                "unique_accounts": int(data["account_id"].nunique()),
                "terminal_churns": count,
                "new_accounts": new_accounts,
                "entrant_churns": entrant_churns,
                "excluded_events": excluded_events,
                "observation_complete": bool(period_end <= RECENT_PERIOD[1]),
                "churn_rate": rate,
                "rate_unit": "account_churn/account_month",
                "ci_low": ci_low,
                "ci_high": ci_high,
                "ci_level": 0.95,
                "ci_method": "wilson" if is_month else "cluster_bootstrap_account",
                "comparator_id": comparator_id,
                "comparator_rate": comparator_rate,
                "relative_risk": relative_risk,
                "rr_ci_low": rr_low,
                "rr_ci_high": rr_high,
                "rate_difference": rate_difference,
                "difference_ci_low": diff_low,
                "difference_ci_high": diff_high,
                "mrr_lost": mrr_lost,
                "mrr_known_accounts": known,
                "mrr_unknown_accounts": unknown,
                "mrr_exposed": mrr_exposed,
                "mrr_exposed_as_of": period_start if is_month else pd.NaT,
                "currency": "USD",
                "financial_unit": "monthly_recurring_revenue",
            }
        )

    for month_start in pd.date_range(HISTORICAL_START, RECENT_PERIOD[1], freq="MS"):
        month_data = account_months.loc[account_months["period_start"].eq(month_start)]
        month_end = month_start + pd.offsets.MonthEnd(1)
        add_row(month_data, month_start, month_end, "month", "all", "all")
        for dimension in HISTORICAL_DIMENSIONS:
            for segment in sorted(month_data[dimension].astype(str).unique()):
                add_row(
                    month_data.loc[month_data[dimension].astype(str).eq(segment)],
                    month_start,
                    month_end,
                    "month",
                    dimension,
                    segment,
                )

    periods = {"reference": REFERENCE_PERIOD, "recent": RECENT_PERIOD}
    period_data = {
        name: account_months.loc[
            account_months["period_start"].ge(start) & account_months["period_start"].le(end)
        ]
        for name, (start, end) in periods.items()
    }
    add_row(
        period_data["reference"],
        REFERENCE_PERIOD[0],
        REFERENCE_PERIOD[1],
        "comparison_period",
        "all",
        "all",
    )
    add_row(
        period_data["recent"],
        RECENT_PERIOD[0],
        RECENT_PERIOD[1],
        "comparison_period",
        "all",
        "all",
        "previous_period",
        period_data["reference"],
        f"churn:comparison_period:{REFERENCE_PERIOD[0].date()}:{REFERENCE_PERIOD[1].date()}:all:all:none",
    )
    for period_name, data in period_data.items():
        start, end = periods[period_name]
        for dimension in HISTORICAL_DIMENSIONS:
            for segment in sorted(data[dimension].astype(str).unique()):
                selected_segment = data.loc[data[dimension].astype(str).eq(segment)]
                complement = data.loc[~data[dimension].astype(str).eq(segment)]
                add_row(
                    selected_segment,
                    start,
                    end,
                    "comparison_period",
                    dimension,
                    segment,
                    "segment_complement",
                    complement,
                    f"complement:{period_name}:{dimension}:{segment}",
                )
                if period_name == "recent":
                    reference_segment = period_data["reference"].loc[
                        period_data["reference"][dimension].astype(str).eq(segment)
                    ]
                    add_row(
                        selected_segment,
                        start,
                        end,
                        "comparison_period",
                        dimension,
                        segment,
                        "previous_period",
                        reference_segment,
                        f"reference:{dimension}:{segment}",
                    )
    return pd.DataFrame(rows, columns=MONTHLY_CHURN_COLUMNS)


def build_reason_distribution(
    tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame
) -> pd.DataFrame:
    parsed = _coerce_tables(tables)
    terminal = terminal_events.copy()
    if terminal.empty:
        terminal = terminal.reindex(columns=parsed["churn_events"].columns)
    selected_terminal, exclusions = select_first_terminal_events(
        parsed["accounts"], parsed["churn_events"], OBSERVATION_END
    )
    if set(terminal.get("churn_event_id", [])) != set(selected_terminal.get("churn_event_id", [])):
        raise ValueError("terminal_events must match shared terminal selection")
    terminal_series = terminal.set_index("account_id")["churn_date"]
    lost = mrr_lost_at_churn(parsed["subscriptions"], terminal_series)
    diagnostic_cutoff = SCORING_CUTOFF - pd.Timedelta(days=31)
    windows = (
        (
            "reference_period",
            REFERENCE_PERIOD[0],
            REFERENCE_PERIOD[1],
            "registered_at_start",
            None,
        ),
        (
            "recent_period",
            RECENT_PERIOD[0],
            RECENT_PERIOD[1],
            "registered_at_start",
            None,
        ),
        (
            "diagnostic_horizon",
            diagnostic_cutoff + pd.Timedelta(days=1),
            diagnostic_cutoff + pd.Timedelta(days=30),
            "diagnostic_horizon",
            diagnostic_cutoff,
        ),
    )
    rows = []
    accounts = parsed["accounts"].set_index("account_id")
    raw_exclusions = exclusions.merge(
        parsed["churn_events"][["churn_event_id", "churn_date"]],
        on="churn_event_id",
        how="left",
    )
    for window_id, start, end, population, eligibility_cutoff in windows:
        in_window = terminal["churn_date"].ge(start) & terminal["churn_date"].le(end)
        selected = terminal.loc[in_window].copy()
        if population == "registered_at_start" and not selected.empty:
            month_start = selected["churn_date"].dt.to_period("M").dt.start_time
            signup = selected["account_id"].map(accounts["signup_date"])
            selected = selected.loc[signup.le(month_start)]
        elif population == "diagnostic_horizon" and not selected.empty:
            selected = selected.loc[
                selected["account_id"].map(accounts["signup_date"]).le(eligibility_cutoff)
            ]
        reasons = selected["reason_code"].astype("string").fillna("unknown")
        reason_values = sorted(set(reasons) | {"unknown"})
        excluded_count = int(
            raw_exclusions.loc[
                raw_exclusions["churn_date"].ge(start) & raw_exclusions["churn_date"].le(end),
                "churn_event_id",
            ].nunique()
        )
        for reason in reason_values:
            reason_events = selected.loc[reasons.eq(reason)]
            count = len(reason_events)
            denominator = len(selected)
            ci_low, ci_high = _wilson(count, denominator)
            mrr_lost, known, unknown = _financial_loss(lost, reason_events["account_id"])
            status = "available" if denominator else "unavailable"
            limitation = "" if denominator else "zero_eligible_events"
            if unknown:
                status = "partial" if status == "available" else status
                limitation = "|".join(
                    filter(None, [limitation, "mrr_lost_unknown_for_some_accounts"])
                )
            rows.append(
                {
                    "evidence_id": f"reason:{window_id}:{population}:{reason}",
                    "period_start": start,
                    "period_end": end,
                    "population": population,
                    "chronology": "shared",
                    "status": status,
                    "limitation": limitation,
                    "source_refs": "accounts|subscriptions|churn_events",
                    "calculation": "build_reason_distribution:v1",
                    "reason_code": reason,
                    "terminal_accounts": count,
                    "eligible_events": denominator,
                    "excluded_events": excluded_count,
                    "share": count / denominator if denominator else np.nan,
                    "unit": "share_of_first_valid_terminal_accounts",
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "ci_method": "wilson",
                    "ci_level": 0.95,
                    "comparator_id": None,
                    "mrr_lost": mrr_lost,
                    "mrr_known_accounts": known,
                    "mrr_unknown_accounts": unknown,
                    "currency": "USD",
                }
            )
    return pd.DataFrame(rows, columns=REASON_DISTRIBUTION_COLUMNS)


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
            lost_mrr = group.get("mrr_lost_next_30d", group["mrr_active"]).loc[churn.eq(1)]
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
                    "mrr_lost": (np.nan if lost_mrr.isna().any() else float(lost_mrr.sum())),
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
        diagnostic_churns = int(exposed_snapshot["churn_next_30d"].sum())
        if str(failure_reason).startswith("model_failure"):
            counterevidence = "O modelo estatístico não produziu uma estimativa estável."
        elif failure_reason == "chronology_instability":
            counterevidence = (
                f"Efeito observed={observed_effect:.3f}, strict={strict_effect:.3f}, "
                f"delta={sensitivity_delta:.3f}."
            )
        elif failure_reason == "sample_or_coverage_gate":
            counterevidence = (
                f"Amostra exposta={len(exposed_snapshot)}, churns={diagnostic_churns}, "
                f"cobertura={strict_fit.get('coverage', 0.0):.3f}."
            )
        elif failure_reason == "cross_table_gate":
            counterevidence = "Os motivos do primeiro churn não corroboraram o sinal."
        elif failure_reason == "association_gate":
            counterevidence = (
                f"OR={strict_fit.get('odds_ratio', np.nan):.3f}; intervalo de 95%="
                f"[{strict_fit.get('ci_low', np.nan):.3f}, "
                f"{strict_fit.get('ci_high', np.nan):.3f}]."
            )
        else:
            counterevidence = "Efeito, intervalo e cronologias passaram os gates definidos."
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
                "diagnostic_cutoff": strict_snapshot["cutoff"].max(),
                "horizon_days": 30,
                "exposure_rule": f"{feature} {operator} {threshold}",
                "diagnostic_exposed_accounts": len(exposed_snapshot),
                "diagnostic_exposed_churns": diagnostic_churns,
                "candidate_coverage": strict_fit.get("coverage", 0.0),
                "source_tables": "accounts|subscriptions|feature_usage|support_tickets|churn_events",
                "affected_accounts": len(exposed_scoring),
                "mrr_exposed_max": float(exposed_scoring["mrr_active"].sum()),
                "confidence": "accepted" if accepted else "inconclusive",
                "failure_reason": failure_reason,
                "counterevidence": counterevidence,
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
