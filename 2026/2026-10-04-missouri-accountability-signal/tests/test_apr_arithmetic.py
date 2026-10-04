"""
tests/test_apr_arithmetic.py

Verifies internal arithmetic consistency of APR calculations:
- Points earned <= Points possible (with small tolerance for rounding)
- Percentage earned roughly equals (earned / possible) * 100
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_PATH = BASE_DIR / "data" / "processed" / "mo_school_accountability_panel.parquet"


@pytest.fixture(scope="module")
def panel():
    return pd.read_parquet(PANEL_PATH)


def test_apr_points_earned_le_possible(panel):
    valid = panel.dropna(subset=["apr_points_earned", "apr_points_possible"]).copy()
    valid = valid[valid["apr_points_possible"] > 0]
    # Allow 0.05 point margin for rounding
    excess = valid[valid["apr_points_earned"] > valid["apr_points_possible"] + 0.05]
    assert len(excess) == 0, f"Found {len(excess)} schools where earned points exceed possible points"


def test_apr_percentage_calculation(panel):
    valid = panel.dropna(subset=["apr_points_earned", "apr_points_possible", "apr_pct"]).copy()
    valid = valid[valid["apr_points_possible"] > 0]
    calc_pct = (valid["apr_points_earned"] / valid["apr_points_possible"]) * 100.0
    diff = (calc_pct - valid["apr_pct"]).abs()
    # Due to DESE rounding of components before summing, differences are within 1.0 percentage point
    assert (diff <= 1.0).all(), f"Found discrepancies between calc_pct and apr_pct > 1.0 pt. Max diff: {diff.max()}"
