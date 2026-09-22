import pandas as pd

from ravenstack_churn.panel import (
    build_account_panel,
    first_terminal_churn,
    mrr_lost_at_churn,
)


def test_first_terminal_churn_ignores_reactivation(mini_tables) -> None:
    result = first_terminal_churn(mini_tables["churn_events"])
    assert result["A-1"] == pd.Timestamp("2024-06-15")


def test_panel_excludes_events_after_cutoff(mini_tables) -> None:
    panel = build_account_panel(
        mini_tables, pd.DatetimeIndex(["2024-05-31"]), chronology="observed"
    )
    row = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert row["tickets_30d"] == 1
    assert row["usage_count_30d"] == 4
    assert row["churn_next_30d"] == 1


def test_support_outcomes_remain_hidden_until_they_occur(mini_tables) -> None:
    ticket = mini_tables["support_tickets"]["ticket_id"].eq("T-recent")
    mini_tables["support_tickets"].loc[ticket, "closed_at"] = "2024-06-02"
    mini_tables["support_tickets"].loc[ticket, "first_response_time_minutes"] = 20_000
    mini_tables["support_tickets"].loc[ticket, "escalation_flag"] = True
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    row = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert row["tickets_30d"] == 1
    assert row["escalations_30d"] == 0
    assert pd.isna(row["mean_first_response_30d"])
    assert pd.isna(row["mean_resolution_30d"])
    assert pd.isna(row["mean_satisfaction_30d"])
    assert row["satisfaction_responses_30d"] == 0


def test_strict_panel_excludes_pre_lifecycle_events(mini_tables) -> None:
    observed = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "observed")
    strict = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    observed_a1 = observed.loc[observed.account_id.eq("A-1")].iloc[0]
    strict_a1 = strict.loc[strict.account_id.eq("A-1")].iloc[0]
    strict_a2 = strict.loc[strict.account_id.eq("A-2")].iloc[0]
    assert strict_a1["usage_count_90d"] < observed_a1["usage_count_90d"]
    assert pd.isna(strict_a2["tickets_90d"])
    assert not bool(strict_a2["support_coverage_90d"])


def test_strict_panel_excludes_usage_after_subscription_end(mini_tables) -> None:
    mini_tables["subscriptions"].loc[
        mini_tables["subscriptions"].subscription_id.eq("S-1"), "end_date"
    ] = "2024-05-01"
    observed = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "observed")
    strict = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    observed_a1 = observed.loc[observed.account_id.eq("A-1")].iloc[0]
    strict_a1 = strict.loc[strict.account_id.eq("A-1")].iloc[0]
    assert observed_a1["usage_count_30d"] == 4
    assert strict_a1["usage_count_30d"] == 0


def test_annual_renewal_uses_next_start_anniversary(mini_tables) -> None:
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    annual = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert annual["next_annual_renewal"] == pd.Timestamp("2024-06-15")
    assert annual["days_to_annual_renewal"] == 15


def test_mrr_lost_is_active_revenue_immediately_before_churn(mini_tables) -> None:
    terminal = first_terminal_churn(mini_tables["churn_events"])
    lost = mrr_lost_at_churn(mini_tables["subscriptions"], terminal)
    assert lost["A-1"] == 1200
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    assert panel.loc[panel.account_id.eq("A-1"), "mrr_lost_next_30d"].iloc[0] == 1200


def test_concurrent_subscriptions_preserve_revenue_and_mixed_dimensions(mini_tables) -> None:
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    account = panel.loc[panel.account_id.eq("A-1")].iloc[0]
    assert account["mrr_active"] == 1200
    assert account["plan_tier"] == "mixed"
    assert account["billing_frequency"] == "mixed"


def test_incomplete_observation_window_is_null_not_zero(mini_tables) -> None:
    panel = build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")
    recent = panel.loc[panel.account_id.eq("A-2")].iloc[0]
    assert pd.isna(recent["usage_count_30d"])
    assert not bool(recent["usage_coverage_30d"])


def test_panel_key_is_unique(observed_panel, strict_panel) -> None:
    panel = pd.concat([observed_panel, strict_panel], ignore_index=True)
    assert not panel.duplicated(["account_id", "cutoff", "chronology"]).any()
