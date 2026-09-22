import pandas as pd

from ravenstack_churn.diagnosis import (
    build_claim_checks,
    build_diagnostic_snapshot,
    evaluate_candidates,
    rank_findings,
)


def test_diagnostic_snapshot_uses_one_common_cutoff() -> None:
    panel = pd.DataFrame(
        [
            {
                "account_id": "A-churned",
                "cutoff": pd.Timestamp("2024-10-31"),
                "churn_next_30d": 1,
                "has_active_subscription": True,
            },
            {
                "account_id": "A-active",
                "cutoff": pd.Timestamp("2024-10-31"),
                "churn_next_30d": 0,
                "has_active_subscription": True,
            },
            {
                "account_id": "A-active",
                "cutoff": pd.Timestamp("2024-11-30"),
                "churn_next_30d": 0,
                "has_active_subscription": True,
            },
        ]
    )
    snapshot = build_diagnostic_snapshot(panel)
    assert snapshot.account_id.tolist() == ["A-active"]
    assert snapshot.cutoff.nunique() == 1
    assert snapshot.cutoff.iloc[0] == pd.Timestamp("2024-11-30")


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


def test_segment_metrics_include_relative_risk(candidate_frames) -> None:
    observed, strict, churn_events = candidate_frames
    _, segments = evaluate_candidates(observed, strict, churn_events)
    assert {"overall_churn_rate", "churn_rate_delta", "relative_risk"}.issubset(segments)


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


def test_usage_status_uses_endpoint_change_not_regression_slope(claim_panel) -> None:
    churn = claim_panel["churn_next_30d"].eq(1)
    monthly_daily_usage = dict(
        zip(sorted(claim_panel.cutoff.unique()), [10, 1, 1, 1, 100, 9], strict=True)
    )
    claim_panel.loc[churn, "usage_count_30d"] = (
        claim_panel.loc[churn, "cutoff"].map(monthly_daily_usage) * 30
    )
    row = (
        build_claim_checks(claim_panel)
        .set_index(["claim_id", "cohort"])
        .loc[("C-usage-growth", "churn_next_30d")]
    )
    assert row["slope"] > 0
    assert row["status"] == "down"
