import json
import runpy
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import pytest

from support_copilot.analytics import (
    OperationalSummary,
    ScenarioAssumptions,
    _signal_status,
    add_operational_fields,
    grouped_bottlenecks,
    recoverable_excess_hours,
    satisfaction_associations,
    scenario_projection,
)
from support_copilot.data import CUSTOMER_COLUMNS, IT_TAXONOMY

ROOT = Path(__file__).parents[1]
reproduce = runpy.run_path(ROOT / "scripts" / "reproduce.py")["reproduce"]


def operational_frame(rows: list[dict] | None = None) -> pd.DataFrame:
    defaults = {
        "domain": "customer",
        "target": "Technical issue",
        "Ticket Status": "Closed",
        "Ticket Priority": "High",
        "Ticket Channel": "Email",
        "First Response Time": "2026-01-01T00:00:00Z",
        "Time to Resolution": "2026-01-01T01:00:00Z",
        "Customer Satisfaction Rating": None,
        "satisfaction_status": "missing",
    }
    source = rows or [{}]
    return pd.DataFrame([
        {**defaults, **row, "ticket_id": f"customer:{index + 1}"}
        for index, row in enumerate(source)
    ])


def summary() -> OperationalSummary:
    return OperationalSummary(
        1, "historical_observed", "development", "data-v1", 100, 80, 60, 48, 40,
        {"not_closed": 2, "missing": 2, "invalid_timestamp": 2, "negative": 2},
        1.0, 3.0, 1, "no_reliable_signal", 4, ("limitation",),
    )


def test_intervals_use_closed_valid_ordered_rows_and_reconcile_denominators() -> None:
    frame = operational_frame([
        {},
        {"Ticket Status": "Open", "First Response Time": "invalid",
         "Time to Resolution": "invalid"},
        {"First Response Time": None},
        {"First Response Time": "[INVALID_TIMESTAMP]"},
        {"First Response Time": "2026-01-02T00:00:00Z"},
    ])
    enriched = add_operational_fields(frame)
    assert enriched["interval_status"].tolist() == [
        "valid", "not_closed", "missing", "invalid_timestamp", "negative"
    ]
    assert enriched["post_response_hours"].tolist()[0] == 1
    assert enriched["post_response_hours"].isna().sum() == 4

    report = grouped_bottlenecks(enriched)
    assert set(report["grouping"]) == {
        "Ticket Channel", "Ticket Priority", "target",
        "Ticket Channel+Ticket Priority", "Ticket Channel+target",
        "Ticket Priority+target", "Ticket Channel+Ticket Priority+target",
    }
    for _, row in report.iterrows():
        assert row.n_total == row.n_eligible + row.n_excluded
        assert row.n_excluded == sum(row[f"excluded_{status}"] for status in (
            "not_closed", "missing", "invalid_timestamp", "negative"
        ))
        assert row.interval_name == "post_response_hours"
        assert not row.first_response_observable and not row.total_resolution_observable


@pytest.mark.parametrize("reverse", [False, True])
def test_intervals_accept_mixed_iso_timestamp_precision_in_any_order(reverse: bool) -> None:
    rows = [
        {"First Response Time": "2026-01-01T00:00:00Z",
         "Time to Resolution": "2026-01-01T00:00:01.123456Z"},
        {"First Response Time": "2026-01-01T00:00:00.500000Z",
         "Time to Resolution": "2026-01-01T00:00:02Z"},
    ]
    enriched = add_operational_fields(operational_frame(list(reversed(rows)) if reverse else rows))
    assert enriched["interval_status"].tolist() == ["valid", "valid"]
    assert sorted(enriched["post_response_hours"].tolist()) == pytest.approx(
        sorted([1.123456 / 3600, 1.5 / 3600])
    )


def test_waste_requires_30_valid_peers_and_never_has_negative_excess() -> None:
    rows = []
    for count, priority in ((29, "Low"), (30, "High")):
        rows.extend({
            "Ticket Priority": priority,
            "Time to Resolution": f"2026-01-02T{hour % 24:02d}:00:00Z",
        } for hour in range(count))
    report = recoverable_excess_hours(operational_frame(rows)).set_index("Ticket Priority")
    assert report.loc["Low", "status"] == "insufficient_support"
    assert pd.isna(report.loc["Low", "observed_excess_hours"])
    assert report.loc["High", "status"] == "supported"
    assert report.loc["High", "observed_excess_hours"] >= 0
    assert not report.loc["High", "realized_savings"]


def test_satisfaction_scarcity_and_two_percent_cut_are_honest() -> None:
    sparse = operational_frame([
        {"Customer Satisfaction Rating": value, "satisfaction_status": "valid"}
        for value in (1, 2, 3, 4)
    ] + [{} for _ in range(30)])
    report = satisfaction_associations(sparse)
    assert report.status == "insufficient_support"
    assert report.valid_ratings == 4
    assert report.missing_ratings == 30
    assert report.permutation_importance is None
    assert "causalidade" in report.selection_limitation

    assert _signal_status(1.0, 0.9801)[0] == "no_reliable_signal"
    status, improvement = _signal_status(1.0, 0.98)
    assert status == "supported"
    assert improvement == pytest.approx(0.02)


@pytest.mark.parametrize("valid_intervals", [0, 1])
def test_satisfaction_handles_interval_absence_inside_folds(valid_intervals: int) -> None:
    rows = []
    for index in range(10):
        rows.append({
            "Ticket Status": "Closed" if index < valid_intervals else "Open",
            "Customer Satisfaction Rating": index % 5 + 1,
            "satisfaction_status": "valid",
            "Ticket Channel": "Email" if index % 2 else "Chat",
        })
    report = satisfaction_associations(operational_frame(rows))
    assert report.status in {"supported", "no_reliable_signal"}
    assert report.cv["folds"] == 5
    assert report.cv["interval_feature_used_folds"] == (0 if valid_intervals == 0 else 4)


@pytest.mark.parametrize(
    "changes,field",
    [
        ({"annual_eligible_volume": -1}, "annual_eligible_volume"),
        ({"addressable_share": 1.1}, "addressable_share"),
        ({"minutes_saved": float("nan")}, "minutes_saved"),
        ({"hourly_cost": float("inf")}, "hourly_cost"),
    ],
)
def test_scenarios_reject_invalid_values(changes: dict, field: str) -> None:
    values = {"annual_eligible_volume": 1200, "addressable_share": 0.25,
              "minutes_saved": 6.0, "hourly_cost": 30.0, "name": "base"}
    with pytest.raises(ValueError, match=field):
        ScenarioAssumptions(**(values | changes))


def test_scenario_changes_only_projection_not_historical_summary() -> None:
    historical = summary()
    before = asdict(historical)
    result = scenario_projection(
        historical, ScenarioAssumptions(1200, 0.25, 6.0, 30.0, "base")
    )
    assert result.annual_hours == 30
    assert result.annual_cost == 900
    assert result.evidence_kind == "projected"
    assert asdict(historical) == before


def test_raw_or_wrong_domain_frames_are_rejected() -> None:
    raw = operational_frame().assign(**{"Customer Name": "Private"})
    with pytest.raises(ValueError, match="sanitized"):
        add_operational_fields(raw)
    with pytest.raises(ValueError, match="domain"):
        add_operational_fields(operational_frame().assign(domain="it"))


def test_reproduce_emits_typed_null_diagnostic_when_split_is_insufficient(
    tmp_path,
) -> None:
    customer = tmp_path / "customer.csv"
    row = dict.fromkeys(CUSTOMER_COLUMNS, "")
    row.update({
        "Ticket ID": "1", "Customer Name": "Example Person",
        "Customer Email": "example@example.invalid", "Customer Age": "31",
        "Customer Gender": "Other", "Ticket Type": "Technical issue",
        "Ticket Description": "device does not boot", "Ticket Status": "Closed",
        "Ticket Priority": "High", "Ticket Channel": "Email",
        "First Response Time": "2026-01-01T00:00:00Z",
        "Time to Resolution": "2026-01-01T01:00:00.123456Z",
        "Customer Satisfaction Rating": "4",
    })
    pd.DataFrame([row]).to_csv(customer, index=False)
    it = tmp_path / "it.csv"
    pd.DataFrame({
        "Document": [f"support request {index}" for index in range(len(IT_TAXONOMY))],
        "Topic_group": IT_TAXONOMY,
    }).to_csv(it, index=False)

    output = tmp_path / "artifacts"
    manifest = reproduce(customer, it, output)
    summary_payload = json.loads(
        (output / "analytics" / "operational-summary.json").read_text()
    )
    waste = pd.read_csv(output / "analytics" / "waste-opportunities.csv")
    bottlenecks = pd.read_csv(output / "analytics" / "bottlenecks.csv")

    assert manifest["splits"]["customer"]["status"] == "insufficient_support"
    assert summary_payload["status"] == "insufficient_support"
    assert summary_payload["reason"] == "no_sanitized_development_representatives"
    assert summary_payload["median_post_response_hours"] is None
    assert summary_payload["observed_excess_hours"] is None
    assert waste.empty and "status" in waste
    assert bottlenecks.empty and "n_eligible" in bottlenecks
