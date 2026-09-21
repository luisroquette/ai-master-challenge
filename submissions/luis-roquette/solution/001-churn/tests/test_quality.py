from pathlib import Path

from ravenstack_churn.contracts import add_usage_row_key, load_raw_tables
from ravenstack_churn.quality import build_quality_report


def test_conflicting_usage_ids_are_preserved_and_flagged(mini_tables) -> None:
    validated = add_usage_row_key(mini_tables["feature_usage"])
    assert validated["usage_row_id"].is_unique
    assert len(validated) == len(mini_tables["feature_usage"])
    report = build_quality_report({**mini_tables, "feature_usage": validated})
    assert report["contradictions"]["duplicate_usage_id_groups"] == 1


def test_churn_label_disagreement_is_reported(mini_tables) -> None:
    report = build_quality_report(mini_tables)
    assert report["contradictions"]["accounts_flag_vs_terminal_event"] == 2
    assert report["label_policy"] == "first_non_reactivation_event"


def test_vendored_data_keeps_known_quality_counts() -> None:
    report = build_quality_report(load_raw_tables(Path("data/raw")))
    assert report["rows"] == {
        "accounts": 500,
        "subscriptions": 5000,
        "feature_usage": 25000,
        "support_tickets": 2000,
        "churn_events": 600,
    }
    assert report["contradictions"]["duplicate_usage_id_groups"] == 21
    assert report["contradictions"]["usage_before_subscription"] == 19142
    assert report["contradictions"]["usage_before_signup"] == 13198
    assert report["contradictions"]["tickets_before_signup"] == 1077
