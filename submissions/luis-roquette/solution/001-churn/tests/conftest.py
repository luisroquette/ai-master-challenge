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
