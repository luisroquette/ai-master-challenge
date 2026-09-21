from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import DEFAULT_CUTOFFS, SCORING_CUTOFF
from .contracts import load_raw_tables, validate_contracts
from .diagnosis import build_claim_checks, evaluate_candidates
from .modeling import evaluate_model
from .panel import build_account_panel
from .publish import AnalysisResult, publish_artifacts, validate_artifact_set
from .quality import build_quality_report


def reproduce(raw_dir: Path, output_dir: Path) -> dict[str, Path]:
    tables = load_raw_tables(raw_dir)
    warnings = validate_contracts(tables)
    quality = build_quality_report(tables)
    quality["contract_warnings"] = warnings.to_dict(orient="records")

    cutoffs = DEFAULT_CUTOFFS.append(pd.DatetimeIndex([SCORING_CUTOFF]))
    observed = build_account_panel(tables, cutoffs, "observed")
    strict = build_account_panel(tables, cutoffs, "strict")
    findings, segments = evaluate_candidates(observed, strict, tables["churn_events"])
    claims = build_claim_checks(strict)
    model_evaluation, model_scores = evaluate_model(strict)
    result = AnalysisResult(
        quality_report=quality,
        panel=pd.concat([observed, strict], ignore_index=True),
        claim_checks=claims,
        findings=findings,
        segment_metrics=segments,
        model_evaluation=model_evaluation,
        model_scores=model_scores,
    )
    paths = publish_artifacts(result, output_dir)
    validate_artifact_set(output_dir)
    print(f"artifacts={output_dir.resolve()}")
    print(
        f"findings_accepted={int(findings['confidence'].eq('accepted').sum())} "
        f"publish_model={bool(model_evaluation.get('publish_model'))}"
    )
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(prog="ravenstack-churn")
    commands = parser.add_subparsers(dest="command", required=True)
    reproduce_parser = commands.add_parser("reproduce")
    reproduce_parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    reproduce_parser.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    if args.command == "reproduce":
        reproduce(args.raw_dir, args.output_dir)


if __name__ == "__main__":
    main()
