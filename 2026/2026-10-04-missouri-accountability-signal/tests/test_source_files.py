"""
tests/test_source_files.py

Verifies that all 19 raw data files cataloged in sources/source_registry.csv:
1. Exist on disk.
2. Have non-zero file size.
3. Match their recorded SHA-256 cryptographic hashes.
"""

from pathlib import Path
import hashlib
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = BASE_DIR / "sources" / "source_registry.csv"


def test_registry_exists():
    assert REGISTRY_PATH.exists(), f"Registry missing at {REGISTRY_PATH}"


def test_all_source_files_exist_and_match_hash():
    df = pd.read_csv(REGISTRY_PATH)
    assert len(df) == 22, f"Expected 22 registered sources, found {len(df)}"

    for _, row in df.iterrows():
        source_id = row["source_id"]
        file_name = row["file_name"]
        expected_hash = row["raw_hash"]

        matches = list(BASE_DIR.glob(f"data/raw/**/{file_name}"))
        assert len(matches) == 1, f"Expected exactly 1 match for {file_name}, found {len(matches)}"
        file_path = matches[0]
        assert file_path.stat().st_size > 0, f"Source file {source_id} is empty (0 bytes)"

        with open(file_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()

        assert actual_hash == expected_hash, (
            f"Hash mismatch for {source_id} ({file_name}): expected {expected_hash}, got {actual_hash}"
        )
