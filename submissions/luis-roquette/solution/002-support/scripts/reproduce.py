"""Build sanitized development artifacts; never consume final-test features."""

import argparse
import hashlib
import importlib.metadata
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path

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
    for domain, path, loader, taxonomy in (
        ("customer", customer, load_customer_tickets, CUSTOMER_TAXONOMY),
        ("it", it, load_it_tickets, IT_TAXONOMY),
    ):
        frame = loader(path)
        split = make_split(frame, "target")
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
    print("Desenvolvimento gravado; teste lacrado; revisão humana de amostras pendente.")


if __name__ == "__main__":
    main()
