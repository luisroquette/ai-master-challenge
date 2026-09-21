from dataclasses import replace

import pandas as pd
import pytest

from ravenstack_churn.publish import (
    ArtifactConsistencyError,
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


def test_manifest_rejects_modified_artifact(analysis_result, tmp_path) -> None:
    publish_artifacts(analysis_result, tmp_path)
    (tmp_path / "findings.csv").write_text("changed")
    with pytest.raises(ArtifactConsistencyError, match="findings.csv checksum mismatch"):
        validate_artifact_set(tmp_path)


def test_no_accepted_finding_publishes_honest_empty_queue(analysis_result, tmp_path) -> None:
    result = replace(
        analysis_result,
        findings=analysis_result.findings.assign(confidence="inconclusive"),
    )
    paths = publish_artifacts(result, tmp_path)
    assert pd.read_csv(paths["account_queue"]).empty
    assert "Evidência insuficiente para priorizar uma causa" in paths["report"].read_text()
