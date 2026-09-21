import pandas as pd
import pytest

from ravenstack_churn.config import RAW_TABLE_NAMES
from ravenstack_churn.contracts import SCHEMAS


@pytest.fixture
def mini_tables() -> dict[str, pd.DataFrame]:
    tables = {
        "accounts": pd.DataFrame(
            [
                ["A-1", "Acme", "FinTech", "BR", "2023-01-01", "organic", "Enterprise", 20, False, False],
                ["A-2", "Beta", "EdTech", "US", "2024-05-20", "partner", "Basic", 5, False, True],
            ],
            columns=SCHEMAS["accounts"],
        ),
        "subscriptions": pd.DataFrame(
            [
                ["S-1", "A-1", "2023-06-15", "2024-06-15", "Enterprise", 20, 1000, 12000, False, False, False, True, "annual", True],
                ["S-2", "A-1", "2024-04-01", None, "Pro", 10, 200, 2400, False, False, False, False, "monthly", True],
                ["S-3", "A-2", "2024-05-20", None, "Basic", 5, 300, 3600, False, False, False, False, "monthly", True],
            ],
            columns=SCHEMAS["subscriptions"],
        ),
        "feature_usage": pd.DataFrame(
            [
                ["U-before", "S-2", "2024-03-15", "feature_1", 2, 60, 0, False],
                ["U-duplicate", "S-1", "2024-05-15", "feature_1", 1, 120, 0, False],
                ["U-duplicate", "S-1", "2024-05-16", "feature_2", 3, 180, 1, False],
                ["U-future", "S-2", "2024-06-10", "feature_3", 2, 90, 0, True],
            ],
            columns=SCHEMAS["feature_usage"],
        ),
        "support_tickets": pd.DataFrame(
            [
                ["T-before", "A-2", "2024-05-10", "2024-05-11", 24.0, "high", 30, 2.0, False],
                ["T-recent", "A-1", "2024-05-20", "2024-05-21", 24.0, "medium", 20, 4.0, False],
                ["T-future", "A-1", "2024-06-10", "2024-06-11", 24.0, "low", 10, 5.0, False],
            ],
            columns=SCHEMAS["support_tickets"],
        ),
        "churn_events": pd.DataFrame(
            [
                ["C-1", "A-1", "2024-06-15", "product", 0.0, False, False, False, "missing feature"],
                ["C-2", "A-1", "2024-07-01", "reactivation", 0.0, False, False, True, "returned"],
            ],
            columns=SCHEMAS["churn_events"],
        ),
    }
    assert set(tables) == set(RAW_TABLE_NAMES)
    return tables


@pytest.fixture
def observed_panel(mini_tables) -> pd.DataFrame:
    from ravenstack_churn.panel import build_account_panel

    return build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "observed")


@pytest.fixture
def strict_panel(mini_tables) -> pd.DataFrame:
    from ravenstack_churn.panel import build_account_panel

    return build_account_panel(mini_tables, pd.DatetimeIndex(["2024-05-31"]), "strict")


@pytest.fixture
def candidate_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    for index in range(80):
        churn = int(index % 4 == 0)
        rows.append(
            {
                "account_id": f"A-{index:03d}",
                "cutoff": pd.Timestamp("2024-11-30"),
                "churn_next_30d": churn,
                "first_terminal_churn_date": (
                    pd.Timestamp("2024-12-15") if churn else pd.NaT
                ),
                "usage_change_30_vs_90": -0.5 if churn else -0.1,
                "error_rate_30d": 0.2 if churn else 0.02,
                "escalations_90d": 2 if churn else 0,
                "mean_satisfaction_90d": 2.5 if churn else 4.5,
                "downgrade_90d": bool(churn),
                "auto_renew_off": bool(churn),
                "industry": "FinTech" if index % 2 else "EdTech",
                "country": "BR" if index % 3 else "US",
                "referral_source": "organic",
                "plan_tier": "Pro",
                "billing_frequency": "monthly",
                "is_trial": False,
                "mrr_active": 100 + index,
                "seats": 10,
                "tenure_days": 400,
                "chronology": "observed",
            }
        )
    observed = pd.DataFrame(rows)
    strict = observed.copy()
    strict["chronology"] = "strict"
    strict.loc[strict.churn_next_30d.eq(1), "usage_change_30_vs_90"] = 0.2
    scoring = strict.assign(
        cutoff=pd.Timestamp("2024-12-31"),
        churn_next_30d=pd.NA,
        first_terminal_churn_date=pd.NaT,
    )
    strict = pd.concat([strict, scoring], ignore_index=True)
    churn_events = pd.DataFrame(
        {
            "churn_event_id": [f"C-{index:03d}" for index in range(20)],
            "account_id": [f"A-{index * 4:03d}" for index in range(20)],
            "churn_date": pd.Timestamp("2024-12-15"),
            "reason_code": ["product"] * 20,
            "refund_amount_usd": 0.0,
            "preceding_upgrade_flag": False,
            "preceding_downgrade_flag": False,
            "is_reactivation": False,
            "feedback_text": "fixture",
        }
    )
    return observed, strict, churn_events


@pytest.fixture
def accepted_findings() -> pd.DataFrame:
    common = {
        "confidence": "accepted",
        "evidence_level": "association_controlled",
        "actionability": "immediate",
    }
    return pd.DataFrame(
        [
            {
                **common,
                "finding_id": "F-commercial-renewal",
                "mrr_exposed_max": 8_000,
                "affected_accounts": 100,
            },
            {
                **common,
                "finding_id": "F-support-escalation",
                "mrr_exposed_max": 10_000,
                "affected_accounts": 50,
            },
        ]
    )


@pytest.fixture
def claim_panel() -> pd.DataFrame:
    rows = []
    cutoffs = pd.date_range("2024-06-30", periods=6, freq="ME")
    for month, cutoff in enumerate(cutoffs):
        for index in range(10):
            churn = int(index < 2)
            daily_usage = 60 - month * 5 if churn else 30 + month * 8
            rows.append(
                {
                    "account_id": f"A-{month}-{index}",
                    "cutoff": cutoff,
                    "churn_next_30d": churn,
                    "usage_count_30d": daily_usage * 30,
                    "usage_coverage_30d": True,
                    "mean_satisfaction_90d": 3.0 if churn else 4.5,
                    "satisfaction_responses_90d": 1,
                    "tickets_90d": 1,
                }
            )
    return pd.DataFrame(rows)


@pytest.fixture
def model_panel() -> pd.DataFrame:
    from hashlib import sha256

    rows = []
    cutoffs = pd.to_datetime(
        ["2024-08-31", "2024-09-30", "2024-10-31", "2024-11-30", "2024-12-31"]
    )
    for account_number in range(30):
        account_id = f"M-{account_number:03d}"
        for month, cutoff in enumerate(cutoffs):
            is_scoring = cutoff == pd.Timestamp("2024-12-31")
            positive = (account_number + month) % 5 == 0
            churn = pd.NA if is_scoring else int(positive)
            rows.append(
                {
                    "account_id": account_id,
                    "cutoff": cutoff,
                    "chronology": "strict",
                    "churn_next_30d": churn,
                    "mrr_active": 100 + account_number * 10,
                    "seats": 5 + account_number % 10,
                    "tenure_days": 300 + month * 30,
                    "days_to_annual_renewal": 60 - month * 5,
                    "usage_count_30d": 80 if positive else 100,
                    "usage_change_30_vs_90": -0.4 if positive else 0.1,
                    "error_rate_30d": 0.2 if positive else 0.02,
                    "feature_breadth_30d": 5,
                    "tickets_30d": 3 if positive else 1,
                    "ticket_change_30_vs_90": 0.5 if positive else -0.1,
                    "escalations_90d": 2 if positive else 0,
                    "mean_satisfaction_90d": 3.0 if positive else 4.5,
                    "downgrade_90d": positive,
                    "auto_renew_off": positive,
                    "industry": "FinTech" if account_number % 2 else "EdTech",
                    "country": "BR" if account_number % 3 else "US",
                    "referral_source": "organic",
                    "plan_tier": "Pro",
                    "billing_frequency": "monthly",
                    "is_trial": False,
                }
            )
    panel = pd.DataFrame(rows)
    buckets = {
        account_id: int(sha256(f"42:{account_id}".encode()).hexdigest()[:8], 16) % 100
        for account_id in panel.account_id.unique()
    }
    assert any(bucket < 80 for bucket in buckets.values())
    assert any(bucket >= 80 for bucket in buckets.values())
    return panel
