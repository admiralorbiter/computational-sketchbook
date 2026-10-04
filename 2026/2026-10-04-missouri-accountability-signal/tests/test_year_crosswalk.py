"""
tests/test_year_crosswalk.py

Verifies structure and validity of docs/variable_crosswalk.csv:
- Contains all required fields per Research Design v0.1 Section 7
- Comparability classifications are from the allowed enum
- Covers major accountability and demographic variables
"""

from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
CROSSWALK_PATH = BASE_DIR / "docs" / "variable_crosswalk.csv"

ALLOWED_STATUSES = {
    "DIRECTLY_COMPARABLE",
    "COMPARABLE_WITH_CAVEAT",
    "NOT_COMPARABLE",
    "UNKNOWN",
}

REQUIRED_COLUMNS = [
    "canonical_variable",
    "year",
    "raw_file",
    "raw_column",
    "definition",
    "unit",
    "denominator",
    "suppression_rule",
    "comparability_status",
    "notes",
]


def test_crosswalk_exists_and_has_required_columns():
    assert CROSSWALK_PATH.exists(), f"Crosswalk missing at {CROSSWALK_PATH}"
    df = pd.read_csv(CROSSWALK_PATH)
    for col in REQUIRED_COLUMNS:
        assert col in df.columns, f"Required column {col} missing in crosswalk"


def test_crosswalk_comparability_statuses_valid():
    df = pd.read_csv(CROSSWALK_PATH)
    invalid_statuses = set(df["comparability_status"].unique()) - ALLOWED_STATUSES
    assert not invalid_statuses, f"Invalid comparability statuses found: {invalid_statuses}"


def test_crosswalk_covers_key_variables():
    df = pd.read_csv(CROSSWALK_PATH)
    vars_present = set(df["canonical_variable"].unique())
    key_vars = {
        "apr_pct", "apr_points_earned", "apr_points_possible",
        "ela_status_mpi", "math_status_mpi", "frpl_pct", "cep_flag",
        "enrollment", "iep_pct", "ell_pct"
    }
    missing_vars = key_vars - vars_present
    assert not missing_vars, f"Key variables missing from crosswalk: {missing_vars}"
