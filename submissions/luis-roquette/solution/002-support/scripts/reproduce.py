"""Build sanitized development artifacts; never consume final-test features."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import tempfile
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from support_copilot.analytics import (
    add_operational_fields,
    grouped_bottlenecks,
    operational_summary,
    recoverable_excess_hours,
    satisfaction_associations,
)
from support_copilot.data import (
    CUSTOMER_TAXONOMY,
    GROUPING_VERSION,
    IT_TAXONOMY,
    SANITIZER_VERSION,
    atomic_json,
    content_hash,
    load_customer_tickets,
    load_it_tickets,
    make_split,
    write_manifest,
)


def _atomic_csv(frame: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=destination.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            frame.to_csv(stream, index=False, lineterminator="\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except OSError:
        raise ValueError("artifact_write_failed") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.to_json(orient="records"))


def _register_artifact(manifest: dict, output: Path, key: str, relative: str,
                       artifact_type: str, logical_value: object) -> None:
    destination = output / relative
    manifest["artifacts"][key] = {
        "path": relative, "type": artifact_type, "schema_version": 1,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "logical_sha256": content_hash(logical_value), "domain": "customer",
        "dependencies": ["data.customer.train", "data.customer.calibration"],
        "status": "ready", "reason": None,
    }


def reproduce(customer: Path, it: Path, output: Path) -> dict:
    configuration = {"seed": 42, "sanitizer": SANITIZER_VERSION, "grouping": GROUPING_VERSION,
                     "mode": "development_only"}
    solution = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=solution, text=True
    ).strip()
    # Include uncommitted/untracked implementation bytes, not raw/runtime/artifacts.
    code_files = sorted([*solution.joinpath("src").rglob("*.py"),
                         *solution.joinpath("scripts").rglob("*.py"),
                         solution / "pyproject.toml", solution / "Makefile"])
    fingerprint = content_hash({
        str(p.relative_to(solution)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in code_files
    })
    manifest = {
        "schema_version": 1, "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "code_revision": f"{revision}+code.{fingerprint}",
        "configuration_sha256": content_hash(configuration),
        "lock_sha256": hashlib.sha256((solution / "requirements.lock").read_bytes()).hexdigest(),
        "runtime": {"python": platform.python_version(), "dependencies": {
            name: importlib.metadata.version(name)
            for name in ("pandas", "scikit-learn", "streamlit", "joblib", "pytest", "ruff")
        }},
        "sources": {}, "splits": {}, "models": {},
        "retrieval": {
            "status": "unavailable", "reason": "not_implemented_human_review_pending",
            "reference_split": None, "index_version": None, "policy_version": None,
            "packet_ids": [], "rubric_sha256": {}, "lock_sha256": None,
            "threshold": None, "eligible_queries": None, "reviewed_queries": 0,
        },
        "artifacts": {},
    }
    customer_frame = None
    customer_split = None
    for domain, path, loader, taxonomy in (
        ("customer", customer, load_customer_tickets, CUSTOMER_TAXONOMY),
        ("it", it, load_it_tickets, IT_TAXONOMY),
    ):
        frame = loader(path)
        split = make_split(frame, "target")
        if domain == "customer":
            customer_frame, customer_split = frame, split
        manifest["sources"][domain] = frame.attrs["source"]
        manifest["splits"][domain] = split.manifest
        manifest["models"][domain] = {
            "status": "unavailable", "reason": "not_implemented", "candidate": None,
            "features": ["text"], "taxonomy": list(taxonomy), "cv": None,
            "calibration": None, "model_version": None, "automation_enabled": False,
            "threshold": None, "configuration_lock_sha256": None,
        }
        # Analytics may use the development rows, never the withheld test payload.
        for partition in ("train", "calibration"):
            part = getattr(split, partition)
            relative = f"data/{domain}-{partition}.json"
            records = part.to_dict("records")
            destination = output / relative
            atomic_json(records, destination)
            manifest["artifacts"][f"data.{domain}.{partition}"] = {
                "path": relative, "type": "sanitized-frame", "schema_version": 1,
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                "logical_sha256": content_hash(records), "domain": domain,
                "dependencies": [f"sources.{domain}", f"splits.{domain}"],
                "status": "ready", "reason": None,
            }
        for key in (f"models.{domain}", f"queue.{domain}"):
            manifest["artifacts"][key] = {
                "path": None, "type": "future", "schema_version": 1,
                "sha256": None, "logical_sha256": None, "domain": domain,
                "dependencies": [], "status": "unavailable",
                "reason": "not_implemented_test_sealed",
            }

    if customer_frame is None or customer_split is None:
        raise ValueError("analytics_customer_data_unavailable")
    development = pd.concat(
        [customer_split.train, customer_split.calibration], ignore_index=True
    )
    development.attrs["source"] = customer_frame.attrs["source"]
    development.attrs["split"] = {
        "representatives": customer_split.manifest["exclusions"]["representatives"],
        "development_rows": len(development),
        "test_rows": len(customer_split.test),
    }
    operational = add_operational_fields(development)
    operational.attrs = development.attrs.copy()
    bottlenecks = grouped_bottlenecks(operational)
    waste = recoverable_excess_hours(operational)
    satisfaction = satisfaction_associations(operational)
    summary = operational_summary(operational)
    summary_payload = asdict(summary)
    satisfaction_payload = asdict(satisfaction)
    reports = {
        "analytics.operational_summary": (
            "analytics/operational-summary.json", "operational-summary", summary_payload
        ),
        "analytics.satisfaction_model": (
            "analytics/satisfaction-model.json", "satisfaction-model", satisfaction_payload
        ),
    }
    for key, (relative, artifact_type, payload) in reports.items():
        atomic_json(payload, output / relative)
        _register_artifact(manifest, output, key, relative, artifact_type, payload)

    association_columns = [
        "feature", "level", "n", "mean_rating", "median_rating", "evidence_kind"
    ]
    associations = pd.DataFrame(satisfaction.univariate_effects, columns=association_columns)
    automation = pd.DataFrame([{
        "opportunity": "cross_domain_automation_evidence",
        "customer_evidence": "operational_diagnostic_available",
        "it_evidence": "operational_outcomes_absent",
        "relationship": "aggregate_only_no_record_join",
        "status": "unavailable",
        "reason": "Dataset IT não contém desfecho operacional nem chave com Customer Support.",
    }])
    tables = {
        "analytics.bottlenecks": ("analytics/bottlenecks.csv", bottlenecks),
        "analytics.waste_opportunities": ("analytics/waste-opportunities.csv", waste),
        "analytics.satisfaction_associations": (
            "analytics/satisfaction-associations.csv", associations
        ),
        "analytics.automation_opportunities": (
            "analytics/automation-opportunities.csv", automation
        ),
    }
    for key, (relative, table) in tables.items():
        _atomic_csv(table, output / relative)
        _register_artifact(manifest, output, key, relative, "csv-report", _records(table))
    write_manifest(manifest, output / "manifest.json")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--customer", type=Path,
                        default=Path("data/raw/customer_support_tickets.csv"))
    parser.add_argument("--it", type=Path,
                        default=Path("data/raw/all_tickets_processed_improved_v3.csv"))
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    try:
        manifest = reproduce(args.customer, args.it, args.output)
    except (ValueError, OSError, importlib.metadata.PackageNotFoundError) as error:
        parser.exit(2, f"Reprodução indisponível: {error}. Corrija e execute make reproduce.\n")
    for domain in ("customer", "it"):
        source = manifest["sources"][domain]
        split = manifest["splits"][domain]
        print(f"{domain}: source={source['total_rows']}, "
              f"sanitized={source['quality']['sanitized_rows']}, split={split['status']}")
    analytics = manifest["artifacts"]["analytics.operational_summary"]
    print(f"diagnóstico de desenvolvimento: {analytics['status']} ({analytics['path']})")
    print("Teste lacrado; satisfação selecionada; revisão humana de amostras pendente.")


if __name__ == "__main__":
    main()
