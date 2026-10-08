"""
tests/test_institutional_incentives.py

Automated integrity tests for Kansas City Institutional Incentive Study (Phase 2):
- Verifies policy registry schema and values.
- Asserts mathematical properties and boundaries of the Signaling Decoupling Gap.
- Validates the existence and completeness of generated tables and figures.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SOURCES_DIR = BASE_DIR / "sources"
TABLES_DIR = BASE_DIR / "artifacts" / "tables"
FIG_DIR = BASE_DIR / "artifacts" / "figures"


def test_policy_registry_schema_and_values():
    """Validates schema, required columns, and non-emptiness of the district policy registry."""
    policy_path = SOURCES_DIR / "kc_district_policy_registry.csv"
    assert policy_path.exists(), f"Missing policy registry: {policy_path}"
    
    df = pd.read_csv(policy_path)
    expected_cols = [
        "district_code",
        "district_name",
        "policy_code",
        "grading_model",
        "grade_floor_policy",
        "retake_rule",
        "homework_weight_cap",
        "eoc_grade_weight",
        "credit_recovery_platform",
        "credit_recovery_setting",
        "credit_recovery_cutoff",
        "source_url"
    ]
    assert list(df.columns) == expected_cols, f"Columns do not match expected schema: {df.columns.tolist()}"
    assert len(df) >= 10, f"Expected at least 10 LEA entries, got {len(df)}"
    assert not df["district_code"].duplicated().any(), "Duplicate district codes in policy registry"


def test_decoupling_table4_integrity():
    """Asserts that Table 4 contains all 45 high schools and valid mathematical ranges."""
    t4_path = TABLES_DIR / "table4_kc_institutional_decoupling_summary.csv"
    assert t4_path.exists(), f"Missing Table 4: {t4_path}"
    
    df = pd.read_csv(t4_path)
    assert len(df) == 45, f"Expected 45 high schools in 2022 panel, got {len(df)}"
    
    # Mathematical boundaries
    assert df["4-Yr Grad Rate (%)"].between(0.0, 100.0).all(), "Graduation rates out of [0, 100] range"
    assert df["Math Status MPI"].between(100.0, 500.0).all(), "Math MPI out of [100, 500] range"
    assert df["Grad Rate Pctile"].between(0.0, 100.0).all(), "Grad rate percentile out of [0, 100]"
    assert df["Math MPI Pctile"].between(0.0, 100.0).all(), "Math MPI percentile out of [0, 100]"
    assert df["Decoupling Gap (Pctile Pts)"].between(-100.0, 100.0).all(), "Decoupling gap out of [-100, 100]"
    
    # Arithmetic consistency
    calc_gap = df["Grad Rate Pctile"] - df["Math MPI Pctile"]
    diff = (df["Decoupling Gap (Pctile Pts)"] - calc_gap).abs()
    assert (diff < 1e-5).all(), "Decoupling gap does not match Grad Rate Pctile minus Math MPI Pctile"
    
    # Unweighted mean of difference between uniform percentiles is ~0
    assert abs(df["Decoupling Gap (Pctile Pts)"].mean()) < 1e-5, "Mean decoupling gap must be zero"


def test_table5_district_matrix_integrity():
    """Asserts that Table 5 correctly aggregates districts and preserves policy variables."""
    t5_path = TABLES_DIR / "table5_district_policy_matrix.csv"
    assert t5_path.exists(), f"Missing Table 5: {t5_path}"
    
    df = pd.read_csv(t5_path)
    assert len(df) >= 20, f"Expected at least 20 districts/LEAs in panel, got {len(df)}"
    assert df["High Schools (N)"].sum() == 45, f"Total high schools across districts must equal 45, got {df['High Schools (N)'].sum()}"


def test_figure4_output_validity():
    """Verifies that Figure 4 is generated and has a valid file size (> 50 KB)."""
    fig_path = FIG_DIR / "04_kc_signaling_decoupling_gap.png"
    assert fig_path.exists(), f"Figure 4 missing: {fig_path}"
    file_size_kb = fig_path.stat().st_size / 1024.0
    assert file_size_kb > 50.0, f"Figure 4 appears corrupted or empty: {file_size_kb:.1f} KB"
