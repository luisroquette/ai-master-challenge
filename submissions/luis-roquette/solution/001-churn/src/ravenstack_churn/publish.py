from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import (
    DEFAULT_CUTOFFS,
    DEFAULT_WINDOWS,
    MIN_COVERAGE,
    MIN_SEGMENT_ACCOUNTS,
    MIN_SEGMENT_CHURNS,
    OBSERVATION_END,
    RAW_FILE_SHA256,
    SCORING_CUTOFF,
    sha256_file,
)
from .diagnosis import CANDIDATES, rank_findings

CLAIM_LABELS = {
    "C-usage-growth": "Uso da plataforma (C-usage-growth)",
    "C-satisfaction-ok": "Satisfação dos clientes (C-satisfaction-ok)",
}
COHORT_LABELS = {"overall": "Todas as contas", "churn_next_30d": "Churn em até 30 dias"}
STATUS_LABELS = {
    "up": "Aumentou",
    "down": "Caiu",
    "concern": "Exige atenção",
    "ok": "Adequada",
}
FINDING_LABELS = {
    "F-product-usage-drop": "Queda de uso",
    "F-product-errors": "Erros de produto",
    "F-support-escalation": "Escalações de suporte",
    "F-support-satisfaction": "Baixa satisfação",
    "F-commercial-downgrade": "Downgrade comercial",
    "F-commercial-renewal": "Renovação automática desligada",
}
FAILURE_LABELS = {
    "association_gate": "Associação insuficiente",
    "chronology_instability": "Instável entre cronologias",
    "sample_or_coverage_gate": "Amostra ou cobertura insuficiente",
    "cross_table_gate": "Sem confirmação entre tabelas",
    "model_failure:LinAlgError": "Modelo estatístico instável",
    "model_failure:ValueError": "Modelo estatístico inválido",
}
QUALITY_LABELS = {
    "usage_before_subscription": "Usos anteriores à assinatura",
    "usage_before_signup": "Usos anteriores ao cadastro",
    "tickets_before_signup": "Tickets anteriores ao cadastro",
    "accounts_flag_vs_terminal_event": "Flags de conta divergentes do evento",
    "usage_after_subscription": "Usos posteriores ao fim da assinatura",
    "subscription_accounts_flag_vs_terminal_event": "Flags de assinatura divergentes por conta",
    "duplicate_usage_id_groups": "Grupos de IDs de uso duplicados",
}
DIMENSION_LABELS = {
    "industry": "Indústria",
    "country": "País",
    "referral_source": "Origem",
    "plan_tier": "Plano",
    "billing_frequency": "Cobrança",
    "is_trial": "Trial",
    "mrr_band": "Faixa de MRR",
}
ELIGIBILITY_LABELS = {"eligible": "Elegível", "inconclusive": "Inconclusivo"}
MRR_BAND_LABELS = {"low": "Baixo", "mid": "Médio", "high": "Alto"}
SEGMENT_LABELS = {
    **MRR_BAND_LABELS,
    "mixed": "Misto",
    "annual": "Anual",
    "monthly": "Mensal",
    "True": "Sim",
    "False": "Não",
    "ads": "Anúncios",
    "event": "Eventos",
    "organic": "Orgânico",
    "other": "Outros",
    "partner": "Parceiros",
}


class ArtifactConsistencyError(ValueError):
    pass


@dataclass(frozen=True)
class AnalysisResult:
    quality_report: dict[str, Any]
    panel: pd.DataFrame
    claim_checks: pd.DataFrame
    findings: pd.DataFrame
    segment_metrics: pd.DataFrame
    model_evaluation: dict[str, Any]
    model_scores: pd.DataFrame | None = None


QUEUE_COLUMNS = (
    "account_id",
    "priority",
    "finding_id",
    "mrr_exposed_max",
    "plan_tier",
    "mrr_band",
    "risk_probability",
    "signals",
    "immediate_action",
    "structural_action",
    "owner",
    "status",
)
EXPECTED_ARTIFACT_FILENAMES = {
    "account_panel.csv",
    "account_queue.csv",
    "account_watchlist.csv",
    "claim_checks.csv",
    "findings.csv",
    "model_evaluation.json",
    "quality_report.json",
    "report.md",
    "segment_metrics.csv",
}


def _mrr_band(value: float) -> str:
    if value <= 500:
        return "low"
    if value <= 2_000:
        return "mid"
    return "high"


def _translated_signals(value: str) -> str:
    return ", ".join(FINDING_LABELS.get(signal, signal) for signal in value.split("|"))


def _json_default(value: object) -> object:
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if isinstance(value, (np.ndarray, pd.Series)):
        return value.tolist()
    if pd.isna(value):
        return None
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _json_text(value: object) -> str:
    return json.dumps(value, default=_json_default, ensure_ascii=False, indent=2, sort_keys=True)


def _accepted_findings(findings: pd.DataFrame) -> pd.DataFrame:
    return rank_findings(findings).loc[lambda frame: frame["confidence"].eq("accepted")]


def _exposed(values: pd.Series, operator: str, threshold: object) -> pd.Series:
    return {
        "le": values.le(threshold),
        "ge": values.ge(threshold),
        "eq": values.eq(threshold),
    }[operator].fillna(False)


def _scoring_accounts(panel: pd.DataFrame) -> pd.DataFrame:
    scoring = panel.loc[
        panel["cutoff"].eq(SCORING_CUTOFF) & panel["chronology"].eq("strict")
    ].copy()
    if "has_active_subscription" in scoring:
        scoring = scoring.loc[scoring["has_active_subscription"].fillna(False)]
    return scoring


def _build_queue(result: AnalysisResult) -> pd.DataFrame:
    accepted = _accepted_findings(result.findings)
    scoring = _scoring_accounts(result.panel)
    rows: list[dict[str, object]] = []
    for finding in accepted.itertuples(index=False):
        feature, _, _, operator, threshold = CANDIDATES[finding.finding_id]
        values = scoring[feature]
        exposed = _exposed(values, operator, threshold)
        for account in scoring.loc[exposed].itertuples(index=False):
            rows.append(
                {
                    "account_id": account.account_id,
                    "priority": finding.priority_rank,
                    "finding_id": finding.finding_id,
                    "mrr_exposed_max": account.mrr_active,
                    "plan_tier": getattr(account, "plan_tier", "n/d"),
                    "mrr_band": _mrr_band(float(account.mrr_active)),
                    "risk_probability": np.nan,
                    "signals": f"{feature}={getattr(account, feature)}",
                    "immediate_action": finding.immediate_action,
                    "structural_action": finding.structural_action,
                    "owner": finding.owner,
                    "status": "",
                }
            )
    queue = pd.DataFrame(rows, columns=QUEUE_COLUMNS)
    if queue.empty:
        return queue
    if result.model_scores is not None and result.model_evaluation.get("publish_model"):
        queue = queue.drop(columns="risk_probability").merge(
            result.model_scores[["account_id", "risk_probability"]],
            on="account_id",
            how="left",
            validate="many_to_one",
        )
    return (
        queue.sort_values(
            ["priority", "mrr_exposed_max", "risk_probability", "account_id"],
            ascending=[True, False, False, True],
            na_position="last",
        )
        .drop_duplicates("account_id")
        .loc[:, QUEUE_COLUMNS]
        .reset_index(drop=True)
    )


def _build_watchlist(result: AnalysisResult) -> pd.DataFrame:
    scoring = _scoring_accounts(result.panel)
    signal_map: dict[str, list[str]] = {str(account_id): [] for account_id in scoring.account_id}
    for finding_id, (feature, _, _, operator, threshold) in CANDIDATES.items():
        if feature not in scoring:
            continue
        exposed_accounts = scoring.loc[
            _exposed(scoring[feature], operator, threshold), "account_id"
        ]
        for account_id in exposed_accounts:
            signal_map[str(account_id)].append(finding_id)

    rows = []
    for account in scoring.itertuples(index=False):
        signals = signal_map[str(account.account_id)]
        if not signals:
            continue
        mrr = float(account.mrr_active)
        rows.append(
            {
                "account_id": account.account_id,
                "signal_count": len(signals),
                "mrr_exposed_max": mrr,
                "plan_tier": getattr(account, "plan_tier", "n/d"),
                "mrr_band": _mrr_band(mrr),
                "signals": "|".join(signals),
                "status": "validation_only",
            }
        )
    columns = (
        "account_id",
        "validation_rank",
        "signal_count",
        "mrr_exposed_max",
        "plan_tier",
        "mrr_band",
        "signals",
        "status",
    )
    if not rows:
        return pd.DataFrame(columns=columns)
    watchlist = pd.DataFrame(rows).sort_values(
        ["signal_count", "mrr_exposed_max", "account_id"], ascending=[False, False, True]
    )
    watchlist.insert(1, "validation_rank", range(1, len(watchlist) + 1))
    return watchlist.loc[:, columns].reset_index(drop=True)


def _value(value: object) -> str:
    if pd.isna(value):
        return "n/d"
    if isinstance(value, (float, np.floating)):
        return f"{value:.3f}"
    return str(value).replace("|", r"\|").replace("\n", "<br>")


def _markdown_table(frame: pd.DataFrame, columns: tuple[str, ...]) -> list[str]:
    if frame.empty:
        return ["Sem linhas elegíveis."]
    labels = [column.replace("_", " ") for column in columns]
    lines = ["| " + " | ".join(labels) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    lines.extend(
        "| " + " | ".join(_value(row[column]) for column in columns) + " |"
        for _, row in frame.loc[:, columns].iterrows()
    )
    return lines


def _build_report(result: AnalysisResult, queue: pd.DataFrame, watchlist: pd.DataFrame) -> str:
    accepted = _accepted_findings(result.findings)
    renewal_accounts = int(
        result.findings.set_index("finding_id").loc["F-commercial-renewal", "affected_accounts"]
    )
    decision = (
        f"Priorizar {FINDING_LABELS.get(accepted.iloc[0]['finding_id'], accepted.iloc[0]['finding_id'])}."
        if not accepted.empty
        else "Evidência insuficiente para priorizar uma causa"
    )
    lines = ["# Diagnóstico executivo de churn", "", "## Decisão executiva", "", decision, ""]

    claim_index = result.claim_checks.set_index(["claim_id", "cohort"])
    usage_overall = STATUS_LABELS[claim_index.loc[("C-usage-growth", "overall"), "status"]]
    usage_churn = STATUS_LABELS[claim_index.loc[("C-usage-growth", "churn_next_30d"), "status"]]
    satisfaction = STATUS_LABELS[claim_index.loc[("C-satisfaction-ok", "overall"), "status"]]
    lines.extend(
        [
            (
                "**Leitura em uma frase:** uso "
                f"{usage_overall.lower()} no agregado e {usage_churn.lower()} na coorte que "
                "churnará em 30 dias; "
                f"satisfação {satisfaction.lower()}, mas nenhuma hipótese causal passou todos os gates."
            ),
            "",
        ]
    )

    lines.extend(["## O que não bate", ""])
    claims = result.claim_checks.loc[
        result.claim_checks["cohort"].isin(["overall", "churn_next_30d"])
    ].copy()
    claims = claims.replace(
        {"claim_id": CLAIM_LABELS, "cohort": COHORT_LABELS, "status": STATUS_LABELS}
    ).rename(
        columns={
            "claim_id": "métrica",
            "cohort": "coorte",
            "start_value": "início",
            "end_value": "fim",
            "slope": "tendência",
            "status": "leitura",
            "coverage": "cobertura",
        }
    )
    lines.extend(
        _markdown_table(
            claims,
            ("métrica", "coorte", "início", "fim", "tendência", "leitura", "cobertura"),
        )
    )

    quality_rows = pd.DataFrame(
        [
            {"regra": rule, "linhas": count}
            for rule, count in result.quality_report.get("contradictions", {}).items()
            if count
        ],
        columns=["regra", "linhas"],
    ).sort_values("linhas", ascending=False)
    quality_rows["regra"] = quality_rows["regra"].replace(QUALITY_LABELS)
    lines.extend(["", "## Qualidade que limita a decisão", ""])
    lines.extend(_markdown_table(quality_rows, ("regra", "linhas")))

    lines.extend(["", "## Hipóteses avaliadas", ""])
    if accepted.empty:
        failed = (
            result.findings[["finding_id", "failure_reason"]]
            .replace({"finding_id": FINDING_LABELS, "failure_reason": FAILURE_LABELS})
            .rename(columns={"finding_id": "hipótese", "failure_reason": "por que não passou"})
        )
        lines.extend(_markdown_table(failed, ("hipótese", "por que não passou")))
    else:
        lines.extend(
            _markdown_table(
                accepted,
                (
                    "finding_id",
                    "confidence",
                    "mrr_exposed_max",
                    "affected_accounts",
                    "counterevidence",
                    "limitation",
                ),
            )
        )

    lines.extend(["", "## Segmentos descritivos", ""])
    segment_confidence = result.segment_metrics.get(
        "confidence", pd.Series("inconclusive", index=result.segment_metrics.index)
    )
    ordered_segments = result.segment_metrics.assign(_eligible=segment_confidence.eq("eligible"))
    segment_order = [
        column
        for column in ("_eligible", "relative_risk", "mrr_lost")
        if column in ordered_segments
    ]
    ordered_segments = ordered_segments.sort_values(segment_order, ascending=False)
    ordered_segments["confidence"] = segment_confidence
    ordered_segments["dimension"] = ordered_segments["dimension"].replace(DIMENSION_LABELS)
    ordered_segments["segment"] = ordered_segments["segment"].replace(SEGMENT_LABELS)
    ordered_segments["confidence"] = ordered_segments["confidence"].replace(ELIGIBILITY_LABELS)
    ordered_segments = ordered_segments.rename(
        columns={
            "dimension": "dimensão",
            "segment": "segmento",
            "sample_size": "contas",
            "churn_rate": "taxa de churn",
            "overall_churn_rate": "taxa geral",
            "relative_risk": "risco relativo",
            "mrr_lost": "MRR perdido",
            "confidence": "elegibilidade",
        }
    )
    segment_columns = tuple(
        column
        for column in (
            "dimensão",
            "segmento",
            "contas",
            "taxa de churn",
            "taxa geral",
            "risco relativo",
            "MRR perdido",
            "elegibilidade",
        )
        if column in ordered_segments
    )
    eligible_segments = ordered_segments.loc[ordered_segments["elegibilidade"].eq("Elegível")]
    if not eligible_segments.empty:
        top_segment = eligible_segments.sort_values("risco relativo", ascending=False).iloc[0]
        lines.append(
            "Entre os segmentos elegíveis, "
            f"{top_segment['dimensão']} / {top_segment['segmento']} tem o maior risco relativo "
            f"({top_segment['risco relativo']:.2f}x); valores maiores abaixo permanecem "
            "inconclusivos por amostra ou número de churns."
        )
        lines.append("")
    lines.extend(_markdown_table(ordered_segments.head(15), segment_columns))

    lines.extend(["", "## Contas para validação" if queue.empty else "## Contas prioritárias", ""])
    if queue.empty:
        lines.append(
            "Nenhuma conta está autorizada para intervenção: não há finding aceito. "
            "As contas abaixo servem somente para validação dos sinais e dos dados."
        )
        visible_watchlist = watchlist.head(10).copy()
        visible_watchlist["signals"] = visible_watchlist["signals"].map(_translated_signals)
        visible_watchlist["status"] = "Somente validação"
        visible_watchlist = visible_watchlist.rename(
            columns={
                "account_id": "conta",
                "validation_rank": "ordem de validação",
                "signal_count": "quantidade de sinais",
                "mrr_exposed_max": "MRR exposto máximo",
                "signals": "sinais",
                "status": "uso permitido",
            }
        )
        lines.extend(
            _markdown_table(
                visible_watchlist,
                (
                    "conta",
                    "ordem de validação",
                    "quantidade de sinais",
                    "MRR exposto máximo",
                    "sinais",
                    "uso permitido",
                ),
            )
        )
    else:
        lines.extend(
            _markdown_table(
                queue.head(20),
                ("account_id", "priority", "finding_id", "mrr_exposed_max", "risk_probability"),
            )
        )

    lines.extend(["", "## Plano de ação", ""])
    if accepted.empty:
        lines.extend(
            [
                (
                    "- **1 semana:** colocar eventos fora do ciclo de vida em quarentena analítica, "
                    f"auditar uma amostra das {renewal_accounts} contas com renovação automática "
                    "desligada e corrigir os vínculos de data."
                ),
                (
                    "- **30–90 dias:** instrumentar o ciclo de vida com chaves e relógios confiáveis, "
                    "acompanhar uma coorte prospectiva e repetir os gates antes de automatizar contato."
                ),
                (
                    "- **Medição:** cobertura temporal válida, estabilidade observed/strict e MRR "
                    "realmente perdido na coorte prospectiva."
                ),
            ]
        )
    else:
        top = accepted.iloc[0]
        lines.extend(
            [
                f"- **1 semana:** {top['immediate_action']}",
                f"- **30–90 dias:** {top['structural_action']}",
                f"- **Medição:** {top.get('success_metric', 'MRR perdido e evolução da coorte exposta')}",
            ]
        )

    lines.extend(
        [
            "",
            "## Metodologia e limitações",
            "",
            (
                "Painel conta-data de corte, leitura strict para decisão e observed apenas para "
                "sensibilidade. As associações não demonstram causalidade; MRR exposto é "
                "oportunidade máxima, não receita recuperável."
            ),
            "",
            (
                "O modelo preditivo só é publicado quando supera todos os gates fora do tempo. "
                f"Nesta execução: publish_model={bool(result.model_evaluation.get('publish_model'))}."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _dependency_versions() -> dict[str, str]:
    dependencies = {}
    for package in ("numpy", "pandas", "scikit-learn", "scipy", "statsmodels", "streamlit"):
        try:
            dependencies[package] = version(package)
        except PackageNotFoundError:
            dependencies[package] = "missing"
    return dependencies


def _git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def publish_artifacts(result: AnalysisResult, output_dir: Path) -> dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    queue = _build_queue(result)
    watchlist = _build_watchlist(result)
    payloads: dict[str, tuple[str, object]] = {
        "account_panel": ("csv", result.panel),
        "account_queue": ("csv", queue),
        "account_watchlist": ("csv", watchlist),
        "claim_checks": ("csv", result.claim_checks),
        "findings": ("csv", rank_findings(result.findings)),
        "segment_metrics": ("csv", result.segment_metrics),
        "quality_report": ("json", result.quality_report),
        "model_evaluation": ("json", result.model_evaluation),
        "report": ("md", _build_report(result, queue, watchlist)),
    }
    paths: dict[str, Path] = {}
    for key, (suffix, payload) in payloads.items():
        path = output_dir / f"{key}.{suffix}"
        temporary = path.with_suffix(path.suffix + ".tmp")
        if suffix == "csv":
            payload.to_csv(temporary, index=False)  # type: ignore[union-attr]
        elif suffix == "json":
            temporary.write_text(_json_text(payload) + "\n", encoding="utf-8")
        else:
            temporary.write_text(str(payload), encoding="utf-8")
        temporary.replace(path)
        paths[key] = path

    manifest = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source_git_sha": _git_sha(),
        "runtime": {"python": platform.python_version(), "dependencies": _dependency_versions()},
        "input_checksums": RAW_FILE_SHA256,
        "parameters": {
            "chronology_modes": ["observed", "strict"],
            "cutoffs": [str(DEFAULT_CUTOFFS.min().date()), str(DEFAULT_CUTOFFS.max().date())],
            "scoring_cutoff": str(SCORING_CUTOFF.date()),
            "windows_days": list(DEFAULT_WINDOWS),
            "min_segment_accounts": MIN_SEGMENT_ACCOUNTS,
            "min_segment_churns": MIN_SEGMENT_CHURNS,
            "min_coverage": MIN_COVERAGE,
            "observation_end": str(OBSERVATION_END.date()),
            "label_policy": result.quality_report.get("label_policy"),
        },
        "test_status": os.environ.get("RAVENSTACK_TEST_STATUS", "unknown"),
        "publish_model": bool(result.model_evaluation.get("publish_model")),
        "artifact_checksums": {path.name: sha256_file(path) for path in paths.values()},
    }
    manifest_path = output_dir / "run_manifest.json"
    temporary_manifest = manifest_path.with_suffix(".json.tmp")
    temporary_manifest.write_text(_json_text(manifest) + "\n", encoding="utf-8")
    temporary_manifest.replace(manifest_path)
    paths["run_manifest"] = manifest_path
    return paths


def validate_artifact_set(output_dir: Path) -> dict[str, object]:
    output_dir = Path(output_dir)
    manifest_path = output_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise ArtifactConsistencyError("run_manifest.json missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checksums = manifest.get("artifact_checksums", {})
    if not isinstance(checksums, dict):
        raise ArtifactConsistencyError("artifact_checksums must be an object")
    if set(checksums) != EXPECTED_ARTIFACT_FILENAMES:
        raise ArtifactConsistencyError("artifact manifest is incomplete or has unknown files")
    for filename, expected in checksums.items():
        path = output_dir / filename
        if not path.is_file():
            raise ArtifactConsistencyError(f"{filename} missing")
        if sha256_file(path) != expected:
            raise ArtifactConsistencyError(f"{filename} checksum mismatch")
    return manifest


def compare_artifact_sets(reference_dir: Path, candidate_dir: Path) -> None:
    reference = validate_artifact_set(reference_dir)
    candidate = validate_artifact_set(candidate_dir)
    ignored = {"generated_at_utc", "source_git_sha"}
    for manifest in (reference, candidate):
        for key in ignored:
            manifest.pop(key, None)
    if reference != candidate:
        raise ArtifactConsistencyError("artifact sets differ")
