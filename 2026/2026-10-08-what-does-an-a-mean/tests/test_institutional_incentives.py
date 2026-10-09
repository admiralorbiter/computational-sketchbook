"""
tests/test_institutional_incentives.py

Automated integrity tests for Kansas City Institutional Incentive Study (Phase 2):
- Verifies chronological policy registry schema, dates, and non-imputation status.
- Asserts mathematical properties and boundaries of the Graduation–Achievement Rank Difference.
- Validates Pearson r = 0.682 and Spearman rho = 0.667 correlation fidelity.
- Validates the existence and completeness of generated tables and figures.
"""

import sys
from pathlib import Path

# Compatibility fix for PySide6 / Shiboken / Python 3.12 meta-path inspection
try:
    import six
    if hasattr(six, "_SixMetaPathImporter") and not hasattr(six._SixMetaPathImporter, "_path"):
        six._SixMetaPathImporter._path = None
except ImportError:
    pass

import numpy as np
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
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


def test_policy_exposure_evidence_register_integrity():
    """Validates 20-column auditable schema, provenance fields, secondary journalism labeling, and NKC/KCPS rules."""
    evidence_path = SOURCES_DIR / "kc_policy_exposure_evidence_register.csv"
    assert evidence_path.exists(), f"Missing evidence register: {evidence_path}"
    
    df = pd.read_csv(evidence_path)
    expected_cols = [
        "district_code",
        "district_name",
        "school_name",
        "academic_year",
        "effective_start",
        "effective_end",
        "course_track",
        "grading_model",
        "missing_work_rule",
        "attempted_work_floor",
        "engagement_weight_pct",
        "progress_weight_pct",
        "proficiency_weight_pct",
        "reassessment_rule",
        "policy_exposure_role",
        "source_document",
        "source_url",
        "source_page_or_section",
        "evidence_strength",
        "verification_status"
    ]
    assert list(df.columns) == expected_cols, f"Columns do not match expected schema: {df.columns.tolist()}"
    assert len(df) >= 25, f"Expected at least 25 evidence register records, got {len(df)}"
    
    # Auditability & Provenance checks: All records must have valid URLs, section citations, and valid date intervals
    assert df["source_url"].str.startswith("http").all(), "All records must contain direct HTTP/HTTPS source URLs"
    assert df["source_page_or_section"].str.strip().ne("").all(), "All records must specify a page or section reference"
    assert (df["effective_start"] <= df["effective_end"]).all(), "effective_start must be <= effective_end"
    
    # 1. Assert Secondary Journalistic Source distinction for KCUR reporting:
    kcur_records = df[df["source_url"].str.contains("kcur.org")]
    assert len(kcur_records) >= 5, "Expected at least 5 KCUR-sourced records for 2023-24 KCPS floor"
    assert (kcur_records["evidence_strength"] == "SECONDARY_JOURNALISTIC_RECORD").all(), "KCUR must be classified as SECONDARY_JOURNALISTIC_RECORD"
    assert (kcur_records["verification_status"] == "SECONDARY_VERIFIED").all(), "KCUR records must be labeled SECONDARY_VERIFIED, not primary source"
    
    # 2. Assert Primary Policy Document parameters for KCPS August 2024 manual (2024-25):
    kcps_2425 = df[(df["district_code"] == "048-078") & (df["academic_year"] == "2024-2025")]
    assert len(kcps_2425) >= 3, "Expected general, honors, and campus summary records for KCPS 2024-25"
    
    # Verify General Education track weights: 10% engagement, 40% progress, 50% proficiency
    general_track = kcps_2425[kcps_2425["course_track"] == "General Education"].iloc[0]
    eng = float(general_track["engagement_weight_pct"])
    prog = float(general_track["progress_weight_pct"])
    prof = float(general_track["proficiency_weight_pct"])
    assert (eng, prog, prof) == (10.0, 40.0, 50.0), f"Expected (10, 40, 50) weights, got ({eng}, {prog}, {prof})"
    assert general_track["missing_work_rule"] == "TRUE_ZERO_ALLOWED", "2024-25 policy requires 0% for missing work"
    assert general_track["attempted_work_floor"] == "40_PCT_MINIMUM"
    assert general_track["evidence_strength"] == "PRIMARY_POLICY_DOCUMENT"
    
    # Verify Honors/AP/IB exemption retains traditional failing range (0_NO_FLOOR)
    honors_track = kcps_2425[kcps_2425["course_track"].str.contains("Honors")].iloc[0]
    assert honors_track["attempted_work_floor"] == "0_NO_FLOOR", "Honors/AP/IB must retain 0-59% F range (0_NO_FLOOR)"
    assert honors_track["policy_exposure_role"] == "Case_A_Honors_Exemption_Track_2024_25"
    
    # Verify Lincoln College Prep mixed course exposure record
    lincoln_rec = kcps_2425[kcps_2425["school_name"] == "LINCOLN COLLEGE PREP."].iloc[0]
    assert lincoln_rec["policy_exposure_role"] == "Case_A_Mixed_Course_Exposure_2024_25"
    
    # 3. Assert NKC 74 school-specific pilot exposure for 2025-26 with corrected assumptions:
    nkc_2526 = df[(df["district_code"] == "024-093") & (df["academic_year"] == "2025-2026")]
    assert len(nkc_2526) == 4, f"Expected 4 NKC high schools in 2025-26, got {len(nkc_2526)}"
    
    # North Kansas City High is the specific pilot school
    nkc_pilot = nkc_2526[nkc_2526["school_name"] == "NORTH KANSAS CITY HIGH"].iloc[0]
    assert nkc_pilot["grading_model"] == "STANDARDS_BASED_SBL"
    assert nkc_pilot["policy_exposure_role"] == "Case_B_Pilot_Designated_Courses_2025_26"
    assert nkc_pilot["engagement_weight_pct"] == "NOT_APPLICABLE", "Proficiency-based SBL grading does not use conventional percentage weights"
    assert nkc_pilot["proficiency_weight_pct"] == "NOT_APPLICABLE"
    assert nkc_pilot["reassessment_rule"] == "NOT_YET_VERIFIED", "District FAQ does not establish universal mandatory retakes"
    
    # Oak Park, Staley, Winnetonka are within-district non-pilot comparison schools
    nkc_non_pilots = nkc_2526[nkc_2526["school_name"].isin(["OAK PARK HIGH", "STALEY HIGH", "WINNETONKA HIGH"])]
    assert len(nkc_non_pilots) == 3
    assert (nkc_non_pilots["grading_model"] == "TRADITIONAL_PCT").all(), "Non-pilot comparison schools must remain traditional in 2025-26"
    assert (nkc_non_pilots["policy_exposure_role"] == "Case_B_Within_District_Comparison_2025_26").all()


def test_table4_school_specific_exposure_integrity():
    """Asserts that Table 4 distinguishes NKC High pilot from non-pilot comparison schools and codes KCPS mixed exposure."""
    t4_path = TABLES_DIR / "table4_kc_institutional_decoupling_summary.csv"
    assert t4_path.exists(), f"Missing Table 4: {t4_path}"
    
    df = pd.read_csv(t4_path)
    
    # NKC High must be identified as the designated pilot school
    nkc_high = df[df["School Name"] == "NORTH KANSAS CITY HIGH"].iloc[0]
    assert "Pilot" in nkc_high["Subsequent Policy Adoption"]
    assert "2025-2026" in nkc_high["Subsequent Effective Year"]
    assert nkc_high["Research Audit Status"] == "VERIFIED_LONGITUDINAL_CASE_B_PILOT"
    assert nkc_high["Longitudinal Policy Exposure Role"] == "Case_B_Pilot_Designated_Courses_2025_26"
    
    # Staley, Oak Park, Winnetonka must be identified as within-district comparison schools
    for non_pilot in ["STALEY HIGH", "OAK PARK HIGH", "WINNETONKA HIGH"]:
        row = df[df["School Name"] == non_pilot].iloc[0]
        assert "Non-Pilot" in row["Subsequent Policy Adoption"]
        assert "2026-2027" in row["Subsequent Effective Year"]
        assert row["Research Audit Status"] == "VERIFIED_WITHIN_DISTRICT_COMPARISON"
        assert row["Longitudinal Policy Exposure Role"] == "Case_B_Within_District_Comparison_2025_26"
        
    # Lincoln College Prep must reflect course-level mixed exposure (NOT treated as an entire untreated school)
    lincoln = df[df["School Name"] == "LINCOLN COLLEGE PREP."].iloc[0]
    assert "Mixed" in lincoln["Subsequent Policy Adoption"]
    assert lincoln["Research Audit Status"] == "VERIFIED_LONGITUDINAL_CASE_A_MIXED"
    assert lincoln["Longitudinal Policy Exposure Role"] == "Case_A_Mixed_Course_Exposure_2024_25"
    
    # Comprehensive KCPS high schools must also reflect mixed course exposure
    for kcps_school in ["CENTRAL HIGH SCHOOL", "EAST HIGH SCHOOL", "PASEO ACAD. OF PERFORMING ARTS"]:
        row = df[df["School Name"] == kcps_school].iloc[0]
        assert "Mixed" in row["Subsequent Policy Adoption"]
        assert row["Research Audit Status"] == "VERIFIED_LONGITUDINAL_CASE_A_MIXED"
        assert row["Longitudinal Policy Exposure Role"] == "Case_A_Mixed_Course_Exposure_2024_25"


def test_evidence_register_is_single_source_of_truth():
    """Asserts that assign_school_policy_exposure dynamically derives all classifications from df_evidence."""
    from src.analyze_institutional_incentives import assign_school_policy_exposure
    
    evidence_path = SOURCES_DIR / "kc_policy_exposure_evidence_register.csv"
    df_evidence = pd.read_csv(evidence_path)
    
    # Normal lookup should return verified pilot for NKC High
    res_normal = assign_school_policy_exposure("NORTH KANSAS CITY HIGH", "024-093", df_evidence)
    assert res_normal["policy_exposure_role"] == "Case_B_Pilot_Designated_Courses_2025_26"
    assert res_normal["audit_status"] == "VERIFIED_LONGITUDINAL_CASE_B_PILOT"
    
    # If the pilot record is removed from df_evidence, the function MUST NOT return the pilot role from hard-coded memory!
    df_no_pilot = df_evidence[~df_evidence["policy_exposure_role"].str.contains("Pilot")]
    res_no_pilot = assign_school_policy_exposure("NORTH KANSAS CITY HIGH", "024-093", df_no_pilot)
    assert res_no_pilot["policy_exposure_role"] != "Case_B_Pilot_Designated_Courses_2025_26"
    
    # If df_evidence is empty, all schools must be labeled PENDING_AUDIT / Unverified
    df_empty = pd.DataFrame(columns=df_evidence.columns)
    res_empty = assign_school_policy_exposure("NORTH KANSAS CITY HIGH", "024-093", df_empty)
    assert res_empty["audit_status"] == "PENDING_AUDIT"
    assert res_empty["subsequent_policy"] == "Unverified"


