"""
tests/test_ranges.py

Verifies domain-specific valid value ranges for accountability and demographic metrics:
- Percentages within [0.0, 100.0]
- MPI values within [100.0, 500.0]
- Positive enrollment
- Valid sample flag values (0 or 1)
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


def test_percentage_ranges(panel):
    pct_cols = [
        "apr_pct", "frpl_pct", "proportional_attendance_pct", "chronic_absence_pct",
        "race_white_pct", "race_black_pct", "race_hispanic_pct", "race_asian_pct",
        "race_urm_pct", "ell_pct", "iep_pct"
    ]
    for col in pct_cols:
        if col in panel.columns:
            valid_vals = panel[col].dropna()
            min_v = valid_vals.min()
            max_v = valid_vals.max()
            assert min_v >= -0.01, f"{col} has value below 0: {min_v}"
            assert max_v <= 100.01, f"{col} has value above 100: {max_v}"


def test_mpi_ranges(panel):
    mpi_cols = ["ela_status_mpi", "math_status_mpi", "science_status_mpi", "achievement_measure"]
    for col in mpi_cols:
        if col in panel.columns:
            valid_vals = panel[col].dropna()
            assert len(valid_vals) > 0, f"No non-null values for {col}"
            assert valid_vals.min() >= 100.0, f"{col} has value below 100: {valid_vals.min()}"
            assert valid_vals.max() <= 500.0, f"{col} has value above 500: {valid_vals.max()}"


def test_enrollment_positive(panel):
    valid_enr = panel["enrollment"].dropna()
    assert len(valid_enr) > 0
    assert (valid_enr >= 0).all(), "Found negative enrollment values"


def test_sample_flags_binary(panel):
    for flag in ["sample_a_all", "sample_b_conventional", "sample_c_stable_panel", "cep_flag"]:
        assert set(panel[flag].dropna().unique()).issubset({0, 1}), f"{flag} contains non-binary values"
