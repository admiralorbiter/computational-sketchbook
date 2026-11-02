"""
tests/test_join_coverage.py

Verifies that merging auxiliary context data (demographics, FRPL, attendance, mobility)
with the APR universe achieves > 98% match rate (less than 2% join loss)
for conventional public schools (Sample B).
"""

from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_PATH = BASE_DIR / "data" / "processed" / "mo_school_accountability_panel.parquet"


@pytest.fixture(scope="module")
def sample_b():
    df = pd.read_parquet(PANEL_PATH)
    return df[df["sample_b_conventional"] == 1].copy()


def test_demographics_join_coverage(sample_b):
    missing_pct = sample_b["enrollment"].isna().mean() * 100.0
    assert missing_pct < 2.0, f"Demographics join missing rate {missing_pct:.2f}% exceeds 2% threshold"


def test_frpl_join_coverage(sample_b):
    missing_pct = sample_b["frpl_pct"].isna().mean() * 100.0
    assert missing_pct < 2.0, f"FRPL join missing rate {missing_pct:.2f}% exceeds 2% threshold"


def test_attendance_join_coverage(sample_b):
    missing_pct = sample_b["proportional_attendance_pct"].isna().mean() * 100.0
    assert missing_pct < 2.0, f"Attendance join missing rate {missing_pct:.2f}% exceeds 2% threshold"


def test_mobility_join_coverage(sample_b):
    missing_pct = sample_b["mobility_pct"].isna().mean() * 100.0
    assert missing_pct < 2.0, f"Mobility join missing rate {missing_pct:.2f}% exceeds 2% threshold"
