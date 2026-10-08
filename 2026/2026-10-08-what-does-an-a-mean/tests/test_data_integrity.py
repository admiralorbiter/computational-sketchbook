"""
tests/test_data_integrity.py

Automated data integrity, provenance, and validity test suite for:
"What Does an A Actually Mean? Grades, Learning, and the Incentives Behind Both"
(`2026-10-08-what-does-an-a-mean`)
"""

from pathlib import Path
import pandas as pd
import numpy as np
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "artifacts" / "tables"


def test_unique_school_year_identifiers():
    """Verify that school-year keys are completely unique in the high school panels."""
    mo_path = PROCESSED_DIR / "mo_high_school_panel.parquet"
    kc_path = PROCESSED_DIR / "kc_high_school_panel.csv"

    assert mo_path.exists(), "Statewide high school panel missing"
    assert kc_path.exists(), "KC high school panel missing"

    df_mo = pd.read_parquet(mo_path)
    df_kc = pd.read_csv(kc_path)

    # Check uniqueness of district_code, building_code, school_year
    mo_dups = df_mo.duplicated(subset=["district_code", "building_code", "school_year"])
    assert not mo_dups.any(), f"Found {mo_dups.sum()} duplicate school-year records in statewide panel"

    kc_dups = df_kc.duplicated(subset=["district_code", "building_code", "school_year"])
    assert not kc_dups.any(), f"Found {kc_dups.sum()} duplicate school-year records in KC panel"


def test_no_placeholder_values_in_graduation_points():
    """Verify that 2022 graduation points do not contain artificial placeholder 100.0 values."""
    kc_path = PROCESSED_DIR / "kc_high_school_panel.csv"
    df_kc = pd.read_csv(kc_path)

    kc_2022 = df_kc[df_kc["school_year"] == 2022]
    # In 2022, grad_pts_pct MUST be NaN, because points were not assigned by DESE during the pilot year
    assert kc_2022["grad_pts_pct"].isna().all(), "Found non-null placeholder values in 2022 grad_pts_pct"


def test_graduation_rate_ranges_and_completeness():
    """Verify that 2022 KC continuous graduation rates are within [0, 100] and have 45 complete pairs."""
    kc_path = PROCESSED_DIR / "kc_high_school_panel.csv"
    df_kc = pd.read_csv(kc_path)

    kc_2022 = df_kc[df_kc["school_year"] == 2022].dropna(subset=["grad_rate_4yr", "math_status_mpi"])
    assert len(kc_2022) == 45, f"Expected 45 complete pairs in 2022 KC sample, found {len(kc_2022)}"

    assert (kc_2022["grad_rate_4yr"] >= 0).all() and (kc_2022["grad_rate_4yr"] <= 100).all(), "Grad rates out of bounds"
    assert (kc_2022["math_status_mpi"] >= 100).all() and (kc_2022["math_status_mpi"] <= 500).all(), "Math MPI out of bounds"


def test_correlations_match_audit_findings():
    """Verify that empirical correlations in 2022 KC sample match independently audited values."""
    t2_path = TABLES_DIR / "table2_kc_high_schools_2022_2025.csv"
    assert t2_path.exists(), "Table 2 benchmark table missing"

    df_t2 = pd.read_csv(t2_path)
    corr = df_t2[["Graduation Rate 2022 (%)", "High School Math MPI", "FRPL Poverty (%)", "Direct Certification (%)"]].corr()

    # Graduation vs Math MPI: r ~ +0.68
    r_grad_math = corr.loc["Graduation Rate 2022 (%)", "High School Math MPI"]
    assert 0.65 <= r_grad_math <= 0.71, f"Unexpected correlation between Grad and Math MPI: {r_grad_math}"

    # Graduation vs Poverty: r ~ -0.73 (FRPL), -0.81 (Direct Cert)
    r_grad_frpl = corr.loc["Graduation Rate 2022 (%)", "FRPL Poverty (%)"]
    assert -0.76 <= r_grad_frpl <= -0.70, f"Unexpected correlation between Grad and FRPL: {r_grad_frpl}"

    r_grad_dc = corr.loc["Graduation Rate 2022 (%)", "Direct Certification (%)"]
    assert -0.83 <= r_grad_dc <= -0.78, f"Unexpected correlation between Grad and Direct Cert: {r_grad_dc}"


def test_no_synthetic_data_in_gershenson_benchmark():
    """Verify that Figure 3 benchmark reflects Seth Gershenson's exact published percentages."""
    nc_path = PROCESSED_DIR / "gershenson_nc_algebra1_benchmark.csv"
    assert nc_path.exists(), "Gershenson benchmark file missing"

    df_nc = pd.read_csv(nc_path)
    assert len(df_nc) == 4, "Expected 4 course grade tiers (A, B, C, D)"

    row_b = df_nc[df_nc["course_grade"] == "B Grade"].iloc[0]
    assert row_b["pct_non_proficient"] == 36.0, f"Expected 36% non-proficient for 'B', got {row_b['pct_non_proficient']}"
    assert row_b["pct_proficient_or_above"] == 64.0, f"Expected 64% proficient for 'B', got {row_b['pct_proficient_or_above']}"

    row_a = df_nc[df_nc["course_grade"] == "A Grade"].iloc[0]
    assert row_a["pct_proficient_or_above"] == 92.0, f"Expected 92% proficient for 'A', got {row_a['pct_proficient_or_above']}"


def test_act_trend_exact_match():
    """Verify that ACT adjusted and unadjusted HSGPA values match Sanchez & Moore (2022)."""
    act_path = PROCESSED_DIR / "act_gpa_score_trends.csv"
    assert act_path.exists(), "ACT trends file missing"

    df_act = pd.read_csv(act_path)
    # Check 2010 and 2021 adjusted endpoints
    act_2010 = df_act[df_act["year"] == 2010].iloc[0]
    act_2021 = df_act[df_act["year"] == 2021].iloc[0]

    assert act_2010["adjusted_gpa"] == 3.17, f"Expected 3.17 in 2010, got {act_2010['adjusted_gpa']}"
    assert act_2021["adjusted_gpa"] == 3.36, f"Expected 3.36 in 2021, got {act_2021['adjusted_gpa']}"

    # Check intermediate published adjusted points: 2016=3.22, 2018=3.26, 2020=3.31
    assert df_act[df_act["year"] == 2016]["adjusted_gpa"].iloc[0] == 3.22
    assert df_act[df_act["year"] == 2018]["adjusted_gpa"].iloc[0] == 3.26
    assert df_act[df_act["year"] == 2020]["adjusted_gpa"].iloc[0] == 3.31

    # Check unadjusted endpoints: 2010=3.22, 2021=3.39
    assert act_2010["unadjusted_gpa"] == 3.22
    assert act_2021["unadjusted_gpa"] == 3.39


def test_naep_hsts_midlevel_score_correction():
    """Verify that NAEP midlevel curriculum math scores match official NCES values (158 to 153)."""
    naep_path = PROCESSED_DIR / "naep_hsts_trends.csv"
    assert naep_path.exists(), "NAEP HSTS file missing"

    df_naep = pd.read_csv(naep_path)
    mid_2009 = df_naep[(df_naep["curriculum"] == "Midlevel Curriculum") & (df_naep["year"] == 2009)].iloc[0]
    mid_2019 = df_naep[(df_naep["curriculum"] == "Midlevel Curriculum") & (df_naep["year"] == 2019)].iloc[0]

    assert mid_2009["naep_math_scale"] == 158.0, f"Expected 158.0 in 2009, got {mid_2009['naep_math_scale']}"
    assert mid_2019["naep_math_scale"] == 153.0, f"Expected 153.0 in 2019, got {mid_2019['naep_math_scale']}"
