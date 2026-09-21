import pandas as pd

from ravenstack_churn.diagnosis import build_claim_checks, evaluate_candidates, rank_findings


def test_unstable_candidate_is_not_ranked(candidate_frames) -> None:
    findings, _ = evaluate_candidates(*candidate_frames)
    unstable = findings.loc[findings.finding_id.eq("F-product-usage-drop")].iloc[0]
    assert unstable["confidence"] == "inconclusive"
    assert pd.isna(unstable["priority_rank"])


def test_rank_uses_mrr_then_reach_then_actionability(accepted_findings) -> None:
    ranked = rank_findings(accepted_findings)
    assert ranked.finding_id.tolist() == [
        "F-support-escalation",
        "F-commercial-renewal",
    ]


def test_zero_variance_candidate_is_inconclusive(candidate_frames) -> None:
    observed, strict, churn_events = candidate_frames
    observed = observed.assign(error_rate_30d=0.0)
    strict = strict.assign(error_rate_30d=0.0)
    findings, _ = evaluate_candidates(observed, strict, churn_events)
    row = findings.loc[findings.finding_id.eq("F-product-errors")].iloc[0]
    assert row["confidence"] == "inconclusive"
    assert row["failure_reason"] == "zero_variance"


def test_claim_checks_expose_aggregate_contradictions(claim_panel) -> None:
    checks = build_claim_checks(claim_panel).set_index(["claim_id", "cohort"])
    assert checks.loc[("C-usage-growth", "overall"), "status"] == "up"
    assert checks.loc[("C-usage-growth", "churn_next_30d"), "status"] == "down"
    assert checks.loc[("C-satisfaction-ok", "overall"), "status"] == "ok"
    assert checks.loc[("C-satisfaction-ok", "churn_next_30d"), "status"] == "concern"
