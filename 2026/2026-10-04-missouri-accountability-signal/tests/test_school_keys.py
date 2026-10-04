"""
tests/test_school_keys.py

Verifies that the canonical school key:
(school_year, district_code, building_code)
is uniquely identified and correctly formatted across the master panel.
"""

from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_PATH = BASE_DIR / "data" / "processed" / "mo_school_accountability_panel.parquet"


@pytest.fixture(scope="module")
def panel_data():
    assert PANEL_PATH.exists(), f"Master panel missing at {PANEL_PATH}"
    return pd.read_parquet(PANEL_PATH)


def test_primary_key_uniqueness(panel_data):
    """Checks that (school_year, district_code, building_code) is unique across the entire panel."""
    key_cols = ["school_year", "district_code", "building_code"]
    dup_mask = panel_data.duplicated(subset=key_cols, keep=False)
    duplicates = panel_data[dup_mask]
    assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate records for key {key_cols}"


def test_key_formats(panel_data):
    """Checks district_code length (6 chars) and building_code length (4 chars)."""
    # District code should be 6 digits
    dist_lens = panel_data["district_code"].str.len().unique()
    assert list(dist_lens) == [6], f"Unexpected district_code lengths: {dist_lens}"

    # Building code should be 4 digits
    bldg_lens = panel_data["building_code"].str.len().unique()
    assert list(bldg_lens) == [4], f"Unexpected building_code lengths: {bldg_lens}"

    # Years should be in 2022, 2023, 2024, 2025
    years = sorted(panel_data["school_year"].unique().tolist())
    assert years == [2022, 2023, 2024, 2025], f"Unexpected school years in panel: {years}"
