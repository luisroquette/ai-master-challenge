from pathlib import Path

from ravenstack_churn.config import RAW_FILE_SHA256, sha256_file


def test_raw_files_match_published_checksums() -> None:
    raw_dir = Path("data/raw")
    actual = {name: sha256_file(raw_dir / name) for name in RAW_FILE_SHA256}
    assert actual == RAW_FILE_SHA256
