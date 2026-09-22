import json
from dataclasses import replace

import pandas as pd
import pytest

from ravenstack_churn.publish import (
    ArtifactConsistencyError,
    _markdown_table,
    compare_artifact_sets,
    publish_artifacts,
    validate_artifact_set,
)


def test_queue_and_report_use_same_finding_ids(analysis_result, tmp_path) -> None:
    paths = publish_artifacts(analysis_result, tmp_path)
    findings = pd.read_csv(paths["findings"])
    claim_checks = pd.read_csv(paths["claim_checks"])
    queue = pd.read_csv(paths["account_queue"])
    report = paths["report"].read_text()
    assert set(queue.finding_id).issubset(set(findings.finding_id))
    assert all(
        finding_id in report
        for finding_id in findings.query("confidence != 'inconclusive'").finding_id
    )
    assert set(claim_checks.claim_id) == {"C-usage-growth", "C-satisfaction-ok"}
    assert all(claim_id in report for claim_id in claim_checks.claim_id.unique())
    assert {"plan_tier", "mrr_band"}.issubset(queue.columns)
    assert "Qualidade que limita a decisão" in report
    assert "Entre os segmentos elegíveis" in report


def test_manifest_rejects_modified_artifact(analysis_result, tmp_path) -> None:
    publish_artifacts(analysis_result, tmp_path)
    (tmp_path / "findings.csv").write_text("changed")
    with pytest.raises(ArtifactConsistencyError, match="findings.csv checksum mismatch"):
        validate_artifact_set(tmp_path)


def test_manifest_rejects_missing_artifact_entry(analysis_result, tmp_path) -> None:
    publish_artifacts(analysis_result, tmp_path)
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["artifact_checksums"].pop("report.md")
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ArtifactConsistencyError, match="manifest is incomplete"):
        validate_artifact_set(tmp_path)


def test_no_accepted_finding_publishes_honest_empty_queue(analysis_result, tmp_path) -> None:
    result = replace(
        analysis_result,
        findings=analysis_result.findings.assign(confidence="inconclusive"),
    )
    paths = publish_artifacts(result, tmp_path)
    assert pd.read_csv(paths["account_queue"]).empty
    watchlist = pd.read_csv(paths["account_watchlist"])
    assert not watchlist.empty
    assert set(watchlist["status"]) == {"validation_only"}
    report = paths["report"].read_text()
    assert "Evidência insuficiente para priorizar uma causa" in report
    assert "uso aumentou no agregado e caiu na coorte" in report
    renewal_accounts = int(
        result.findings.set_index("finding_id").loc["F-commercial-renewal", "affected_accounts"]
    )
    assert f"amostra das {renewal_accounts} contas" in report


def test_inactive_accounts_never_enter_queue_or_watchlist(analysis_result, tmp_path) -> None:
    panel = analysis_result.panel.assign(
        has_active_subscription=lambda frame: frame["account_id"].ne("A-2")
    )
    paths = publish_artifacts(replace(analysis_result, panel=panel), tmp_path)
    assert "A-2" not in set(pd.read_csv(paths["account_queue"])["account_id"])
    assert "A-2" not in set(pd.read_csv(paths["account_watchlist"])["account_id"])


def test_markdown_table_escapes_cell_separators() -> None:
    table = _markdown_table(pd.DataFrame([{"signals": "usage|errors"}]), ("signals",))
    assert table[-1] == r"| usage\|errors |"


def test_equivalent_runs_compare_equal(analysis_result, tmp_path) -> None:
    reference = tmp_path / "reference"
    candidate = tmp_path / "candidate"
    publish_artifacts(analysis_result, reference)
    publish_artifacts(analysis_result, candidate)
    compare_artifact_sets(reference, candidate)
