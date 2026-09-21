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
    RAW_FILE_SHA256,
    SCORING_CUTOFF,
    sha256_file,
)
from .diagnosis import CANDIDATES, rank_findings


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
    "risk_probability",
    "signals",
    "immediate_action",
    "structural_action",
    "owner",
    "status",
)


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


def _build_queue(result: AnalysisResult) -> pd.DataFrame:
    accepted = _accepted_findings(result.findings)
    scoring = result.panel.loc[
        result.panel["cutoff"].eq(SCORING_CUTOFF)
        & result.panel["chronology"].eq("strict")
    ].copy()
    rows: list[dict[str, object]] = []
    for finding in accepted.itertuples(index=False):
        feature, _, _, operator, threshold = CANDIDATES[finding.finding_id]
        values = scoring[feature]
        exposed = {
            "le": values.le(threshold),
            "ge": values.ge(threshold),
            "eq": values.eq(threshold),
        }[operator].fillna(False)
        for account in scoring.loc[exposed].itertuples(index=False):
            rows.append(
                {
                    "account_id": account.account_id,
                    "priority": finding.priority_rank,
                    "finding_id": finding.finding_id,
                    "mrr_exposed_max": account.mrr_active,
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


def _value(value: object) -> str:
    if pd.isna(value):
        return "n/d"
    if isinstance(value, (float, np.floating)):
        return f"{value:.3f}"
    return str(value)


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


def _build_report(result: AnalysisResult, queue: pd.DataFrame) -> str:
    accepted = _accepted_findings(result.findings)
    decision = (
        f"Priorizar {accepted.iloc[0]['finding_id']}."
        if not accepted.empty
        else "Evidência insuficiente para priorizar uma causa"
    )
    lines = ["# Diagnóstico executivo de churn", "", "## Decisão executiva", "", decision, ""]

    lines.extend(["## O que não bate", ""])
    claims = result.claim_checks.loc[
        result.claim_checks["cohort"].isin(["overall", "churn_next_30d"])
    ]
    lines.extend(
        _markdown_table(
            claims,
            ("claim_id", "cohort", "start_value", "end_value", "status", "coverage"),
        )
    )

    lines.extend(["", "## Evidências causais candidatas", ""])
    if accepted.empty:
        failed = result.findings[["finding_id", "failure_reason"]]
        lines.extend(_markdown_table(failed, ("finding_id", "failure_reason")))
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

    lines.extend(["", "## Segmentos", ""])
    segment_columns = tuple(
        column
        for column in ("dimension", "segment", "sample_size", "churn_rate", "mrr_lost", "confidence")
        if column in result.segment_metrics
    )
    lines.extend(_markdown_table(result.segment_metrics.head(15), segment_columns))

    lines.extend(["", "## Contas prioritárias", ""])
    if queue.empty:
        lines.append("Nenhuma conta nomeada: não há finding aceito.")
    else:
        lines.extend(
            _markdown_table(
                queue.head(20),
                ("account_id", "priority", "finding_id", "mrr_exposed_max", "risk_probability"),
            )
        )

    lines.extend(["", "## Plano de ação", ""])
    if accepted.empty:
        lines.append("Revisar qualidade, cobertura e estabilidade antes de direcionar uma intervenção.")
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
    payloads: dict[str, tuple[str, object]] = {
        "account_panel": ("csv", result.panel),
        "account_queue": ("csv", queue),
        "claim_checks": ("csv", result.claim_checks),
        "findings": ("csv", rank_findings(result.findings)),
        "segment_metrics": ("csv", result.segment_metrics),
        "quality_report": ("json", result.quality_report),
        "model_evaluation": ("json", result.model_evaluation),
        "report": ("md", _build_report(result, queue)),
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
    for filename, expected in manifest.get("artifact_checksums", {}).items():
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
