"""
tests/test_institutional_incentives.py

Automated integrity tests for Kansas City Institutional Incentive Study (Phase 2):
- Verifies chronological policy registry schema, dates, and non-imputation status.
- Asserts mathematical properties and boundaries of the Graduation–Achievement Rank Difference.
- Validates Pearson r = 0.682 and Spearman rho = 0.667 correlation fidelity.
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
    """Validates schema, dates, and temporal status of the district policy registry."""
    policy_path = SOURCES_DIR / "kc_district_policy_registry.csv"
    assert policy_path.exists(), f"Missing policy registry: {policy_path}"
    
    df = pd.read_csv(policy_path)
    expected_cols = [
        "district_code",
        "district_name",
        "policy_code",
        "policy_name",
        "effective_school_year",
        "status_in_2022_benchmark",
        "grading_model_2022",
        "grading_floor_policy_2022",
        "current_or_subsequent_policy",
        "subsequent_effective_year",
        "source_document_title",
        "source_url",
        "verification_status"
    ]
    assert list(df.columns) == expected_cols, f"Columns do not match expected schema: {df.columns.tolist()}"
    assert len(df) >= 8, f"Expected at least 8 LEA entries, got {len(df)}"
    assert not df["district_code"].duplicated().any(), "Duplicate district codes in policy registry"
    
    # Assert temporal status: KCPS 40% floor and NKC SBL were NOT in effect during 2022 benchmark
    kcps = df[df["district_code"] == "048-078"].iloc[0]
    assert kcps["status_in_2022_benchmark"] == "NOT_IN_EFFECT", "KCPS 40% floor misclassified as in effect in 2022"
    assert kcps["subsequent_effective_year"] == "2023-2024", "KCPS floor effective year must be 2023-2024"
    
    nkc = df[df["district_code"] == "024-093"].iloc[0]
    assert nkc["status_in_2022_benchmark"] == "NOT_IN_EFFECT", "NKC SBL misclassified as in effect in 2022"
    assert nkc["subsequent_effective_year"] == "2025-2026", "NKC SBL pilot effective year must be 2025-2026"


def test_decoupling_table4_integrity():
    """Asserts that Table 4 contains all 45 high schools, valid rank differences, and correct correlations."""
    t4_path = TABLES_DIR / "table4_kc_institutional_decoupling_summary.csv"
    assert t4_path.exists(), f"Missing Table 4: {t4_path}"
    
    df = pd.read_csv(t4_path)
    assert len(df) == 45, f"Expected 45 high schools in 2022 panel, got {len(df)}"
    
    # Mathematical boundaries
    assert df["4-Yr Grad Rate (%)"].between(0.0, 100.0).all(), "Graduation rates out of [0, 100] range"
    assert df["Math Status MPI"].between(100.0, 500.0).all(), "Math MPI out of [100, 500] range"
    assert df["Grad Rate Pctile"].between(0.0, 100.0).all(), "Grad rate percentile out of [0, 100]"
    assert df["Math MPI Pctile"].between(0.0, 100.0).all(), "Math MPI percentile out of [0, 100]"
    assert df["Grad-Math Rank Diff (Pctile Pts)"].between(-100.0, 100.0).all(), "Rank difference out of [-100, 100]"
    
    # Arithmetic consistency
    calc_gap = df["Grad Rate Pctile"] - df["Math MPI Pctile"]
    diff = (df["Grad-Math Rank Diff (Pctile Pts)"] - calc_gap).abs()
    assert (diff < 1e-5).all(), "Rank diff does not match Grad Rate Pctile minus Math MPI Pctile"
    
    # Unweighted mean of difference between uniform percentiles is ~0
    assert abs(df["Grad-Math Rank Diff (Pctile Pts)"].mean()) < 1e-5, "Mean rank difference must be zero"
    
    # Pearson and Spearman correlation checks
    pearson_r = df["4-Yr Grad Rate (%)"].corr(df["Math Status MPI"], method="pearson")
    spearman_rho = df["4-Yr Grad Rate (%)"].corr(df["Math Status MPI"], method="spearman")
    assert abs(pearson_r - 0.6817) < 0.005, f"Pearson r {pearson_r:.4f} does not match expected ~0.682"
    assert abs(spearman_rho - 0.6668) < 0.005, f"Spearman rho {spearman_rho:.4f} does not match expected ~0.667"


def test_table5_district_matrix_integrity():
    """Asserts that Table 5 correctly aggregates districts, preserves audit roles, and avoids default imputation."""
    t5_path = TABLES_DIR / "table5_district_policy_matrix.csv"
    assert t5_path.exists(), f"Missing Table 5: {t5_path}"
    
    df = pd.read_csv(t5_path)
    assert len(df) >= 20, f"Expected at least 20 districts/LEAs in panel, got {len(df)}"
    assert df["High Schools (N)"].sum() == 45, f"Total high schools across districts must equal 45, got {df['High Schools (N)'].sum()}"
    
    # Ensure research roles exist for Case Study A and Case Study B
    kcps_row = df[df["District Name"] == "KANSAS CITY 33"].iloc[0]
    assert "Case Study A" in kcps_row["Research Study Role"], "KCPS not assigned Case Study A role"
    
    nkc_row = df[df["District Name"] == "NORTH KANSAS CITY 74"].iloc[0]
    assert "Case Study B" in nkc_row["Research Study Role"], "NKC not assigned Case Study B role"
    
    # Verify unverified districts are labeled as pending audit rather than given fake defaults
    unverified = df[df["Audit Status"] == "PENDING_AUDIT"]
    assert len(unverified) > 0, "Unverified districts should exist without imputed defaults"


def test_figure4_output_validity():
    """Verifies that Figure 4 is generated and has a valid file size (> 50 KB)."""
    fig_path = FIG_DIR / "04_kc_signaling_decoupling_gap.png"
    assert fig_path.exists(), f"Figure 4 missing: {fig_path}"
    file_size_kb = fig_path.stat().st_size / 1024.0
    assert file_size_kb > 50.0, f"Figure 4 appears corrupted or empty: {file_size_kb:.1f} KB"
