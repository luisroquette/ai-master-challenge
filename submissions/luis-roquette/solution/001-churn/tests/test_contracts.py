from pathlib import Path

import pytest

from ravenstack_churn.config import RAW_FILE_SHA256, sha256_file
from ravenstack_churn.contracts import DataContractError, validate_contracts


def test_raw_files_match_published_checksums() -> None:
    raw_dir = Path("data/raw")
    actual = {name: sha256_file(raw_dir / name) for name in RAW_FILE_SHA256}
    assert actual == RAW_FILE_SHA256


def test_orphan_subscription_blocks_execution(mini_tables) -> None:
    mini_tables["subscriptions"].loc[0, "account_id"] = "A-missing"
    with pytest.raises(DataContractError, match=r"subscriptions\.account_id.*1 orphan"):
        validate_contracts(mini_tables)
