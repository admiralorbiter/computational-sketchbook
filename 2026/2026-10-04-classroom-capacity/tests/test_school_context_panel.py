"""
Unit and Integration Tests for School Context & Instructional Load Panel (Phase 4.1 Calibration Patch).
Verifies:
1. Presence of uncollapsed context columns and regime indicators.
2. Enforcement of methodological guardrails (no composite index, no roster projections).
3. Split between incompatible federal chronic absenteeism regimes:
   - CRDC 15+ Days Missed (2013-14, 2015-16)
   - EDFacts >=10% of enrolled days (2017-18, 2020-21, 2021-22)
4. Denominator provenance and mobility flags (unclipped rates with flag_absent_gt_enrollment).
5. Outcome-specific balanced panels.
6. Weighting identities (school-weighted vs pooled student-weighted).
7. Strict reserve-code semantics for nonbinary (_X) reporting.
8. Canonical Kansas City PTR matching Phase 3 CCD metadata.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"
PARQUET_PATH = DATA_DIR / "school_context_panel.parquet"
COURSE_PARQUET_PATH = DATA_DIR / "crdc_course_panel.parquet"

from src.harmonize_crdc import sum_enrollment_with_nonbinary, clean_series


@pytest.fixture(scope="module")
def context_df():
    assert PARQUET_PATH.exists(), f"Missing processed file: {PARQUET_PATH}"
    return pd.read_parquet(PARQUET_PATH)


@pytest.fixture(scope="module")
def course_df():
    assert COURSE_PARQUET_PATH.exists(), f"Missing processed file: {COURSE_PARQUET_PATH}"
    return pd.read_parquet(COURSE_PARQUET_PATH)


def test_required_columns(context_df):
    """Verify presence of core uncollapsed context and calibrated linkage columns."""
    required = [
        "nces_school_id", "crdc_wave", "school_year", "state",
        "school_enrollment", "idea_count", "pct_idea",
        "sec504_count", "pct_sec504", "idea_or_504_count", "pct_idea_or_504",
        "el_count", "pct_el",
        "crdc_absent_15d_count", "pct_crdc_absent_15d",
        "edfacts_absent_10pct_count", "pct_edfacts_absent_10pct",
        "chronic_absent_count", "pct_chronic_absent", "pct_chronic_absent_clean",
        "flag_absent_gt_enrollment", "is_absent_waiver_year", "chronic_absent_regime",
        "school_teachers_fte", "school_ptr",
        "in_class_size_panel"
    ]
    for col in required:
        assert col in context_df.columns, f"Missing required column: {col}"


def test_no_composite_index(context_df):
    """Enforce methodological rule: do NOT create composite complexity index."""
    forbidden = ["complexity_index", "instructional_load_index", "composite_score"]
    for col in forbidden:
        assert col not in context_df.columns, f"Forbidden composite column found: {col}"


def test_primary_key_uniqueness(context_df):
    """School ID + Wave must uniquely identify rows."""
    dups = context_df.duplicated(subset=["nces_school_id", "crdc_wave"]).sum()
    assert dups == 0, f"Found {dups} duplicate (nces_school_id, crdc_wave) records."


def test_six_waves_present(context_df):
    """Verify all six CRDC collection waves exist with expected volume."""
    expected_waves = {"2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"}
    actual_waves = set(context_df["crdc_wave"].unique())
    assert expected_waves == actual_waves, f"Wave mismatch: {actual_waves} vs {expected_waves}"
    
    counts = context_df.groupby("crdc_wave")["nces_school_id"].count()
    for w, c in counts.items():
        assert c >= 90000, f"Wave {w} has unusually low school count: {c}"


def test_absenteeism_regimes(context_df):
    """Verify distinct federal chronic absenteeism regimes across waves."""
    sec = context_df[context_df["in_class_size_panel"]]
    
    # Regime 1: 2013-14 and 2015-16 have CRDC 15+ days counts, EDFacts 10% is NaN
    sub_r1 = sec[sec["crdc_wave"].isin(["2013-14", "2015-16"])]
    assert (sub_r1["crdc_absent_15d_count"].notna()).sum() > 45000
    assert sub_r1["edfacts_absent_10pct_count"].isna().all()
    assert (sub_r1["chronic_absent_regime"] == "crdc_15d").all()
    
    # Regime 2: 2017-18, 2020-21, 2021-22 have EDFacts counts, CRDC 15+ is NaN
    sub_r2 = sec[sec["crdc_wave"].isin(["2017-18", "2020-21", "2021-22"])]
    assert (sub_r2["edfacts_absent_10pct_count"].notna()).sum() > 40000
    assert sub_r2["crdc_absent_15d_count"].isna().all()
    assert (sub_r2["chronic_absent_regime"] == "edfacts_10pct").all()
    
    # Wave 2023-24 has no chronic absenteeism published
    sub_23 = sec[sec["crdc_wave"] == "2023-24"]
    assert sub_23["chronic_absent_count"].isna().all()
    assert sub_23["chronic_absent_regime"].isna().all()


def test_denominator_provenance_and_flags(context_df):
    """Verify denominator discordance flags and unclipped rate preservation."""
    sec = context_df[context_df["in_class_size_panel"]]
    
    # Unclipped rates exist where absent count > snapshot enrollment
    gt_enr_mask = sec["flag_absent_gt_enrollment"] == True
    assert gt_enr_mask.sum() > 0, "Expected schools with cumulative count > snapshot enrollment"
    
    # Clean rate must be NaN when flagged
    assert sec.loc[gt_enr_mask, "pct_chronic_absent_clean"].isna().all()
    
    # Non-flagged valid rates must match pct_chronic_absent and be <= 100
    clean_mask = sec["pct_chronic_absent_clean"].notna()
    assert (sec.loc[clean_mask, "pct_chronic_absent_clean"] == sec.loc[clean_mask, "pct_chronic_absent"]).all()
    assert (sec.loc[clean_mask, "pct_chronic_absent_clean"] <= 100.0).all()
    
    # 2020-21 is marked as waiver year
    assert (sec[sec["crdc_wave"] == "2020-21"]["is_absent_waiver_year"] == True).all()
    assert (sec[sec["crdc_wave"] != "2020-21"]["is_absent_waiver_year"] == False).all()


def test_outcome_specific_balanced_panels(context_df):
    """Verify construction and metrics of outcome-specific balanced panels."""
    sec = context_df[context_df["in_class_size_panel"]].copy()
    
    # 1. 6-wave balanced panel for accommodations
    valid_acc = (
        sec["school_enrollment"].notna() & (sec["school_enrollment"] > 0) &
        sec["idea_count"].notna() & sec["sec504_count"].notna() & sec["el_count"].notna()
    )
    acc_counts = sec[valid_acc].groupby("nces_school_id")["crdc_wave"].nunique()
    bal_acc_sids = acc_counts[acc_counts == 6].index
    assert len(bal_acc_sids) >= 11000, f"Expected >= 11,000 schools in 6-wave balanced panel, found {len(bal_acc_sids)}"
    
    # 2. Matched EDFacts absenteeism panel (2017-18 <-> 2021-22)
    s17 = set(sec[(sec["crdc_wave"] == "2017-18") & sec["edfacts_absent_10pct_count"].notna() & (sec["school_enrollment"] > 0)]["nces_school_id"])
    s21 = set(sec[(sec["crdc_wave"] == "2021-22") & sec["edfacts_absent_10pct_count"].notna() & (sec["school_enrollment"] > 0)]["nces_school_id"])
    matched_edf = s17.intersection(s21)
    assert len(matched_edf) >= 20000, f"Expected >= 20,000 matched schools, found {len(matched_edf)}"
    
    m17 = sec[(sec["crdc_wave"] == "2017-18") & sec["nces_school_id"].isin(matched_edf)]["pct_edfacts_absent_10pct"].median()
    m21 = sec[(sec["crdc_wave"] == "2021-22") & sec["nces_school_id"].isin(matched_edf)]["pct_edfacts_absent_10pct"].median()
    assert 18.0 <= m17 <= 20.0, f"Expected 2017-18 median ~19%, found {m17:.2f}%"
    assert 31.0 <= m21 <= 33.0, f"Expected 2021-22 median ~32%, found {m21:.2f}%"
    assert m21 > 1.6 * m17, "Expected ~69% relative surge in median chronic absenteeism"


def test_weighting_identities(context_df):
    """Verify mathematical relations between school-level rates and pooled student rates."""
    sec = context_df[context_df["in_class_size_panel"] & (context_df["crdc_wave"] == "2023-24")].copy()
    valid = sec[sec["school_enrollment"].notna() & (sec["school_enrollment"] > 0) & sec["idea_count"].notna() & sec["sec504_count"].notna()]
    
    # School-level addition holds: pct_idea_or_504 == pct_idea + pct_sec504
    diff = (valid["pct_idea_or_504"] - (valid["pct_idea"] + valid["pct_sec504"])).abs()
    assert (diff < 1e-5).all(), "School-level combined rate should equal sum of components"
    
    # Pooled student rate equals sum(counts) / sum(enrollment)
    pooled_comb = valid["idea_or_504_count"].sum() / valid["school_enrollment"].sum() * 100.0
    assert 18.0 <= pooled_comb <= 20.0, f"Expected pooled accommodations rate ~19%, found {pooled_comb:.2f}%"


def test_nonbinary_reserve_code_semantics():
    """Unit test strict handling of nonbinary reserve codes."""
    df = pd.DataFrame({
        "m": [20, 20, 20, 20, 20, 20, -5, 20],
        "f": [20, 20, 20, 20, 20, 20, 20, -3],
        "x": [10, 0, -9, -10, -12, -5, 0, 0]
    })
    res = sum_enrollment_with_nonbinary(df["m"], df["f"], df["x"], require_complete=True)
    
    # Case 1: valid positive X -> 20 + 20 + 10 = 50
    assert res.iloc[0] == 50.0
    # Case 2: zero X -> 20 + 20 + 0 = 40
    assert res.iloc[1] == 40.0
    # Case 3: -9 structurally not collected -> 20 + 20 = 40
    assert res.iloc[2] == 40.0
    # Case 4: -10 structurally not collected -> 20 + 20 = 40
    assert res.iloc[3] == 40.0
    # Case 5: -12 not applicable -> 20 + 20 = 40
    assert res.iloc[4] == 40.0
    # Case 6: -5 suppressed -> NaN (uncertain)
    assert pd.isna(res.iloc[5])
    # Case 7: M is suppressed -> NaN
    assert pd.isna(res.iloc[6])
    # Case 8: F is missing -> NaN
    assert pd.isna(res.iloc[7])


def test_kansas_city_canonical_ptr(context_df):
    """Verify KC secondary PTR carries forward canonical Phase 3 CCD values and resolves 20.91 anomaly."""
    sec = context_df[context_df["in_class_size_panel"] & context_df["is_kc_metro"]]
    kc_21_ptr = sec[sec["crdc_wave"] == "2021-22"]["school_ptr"].mean()
    assert 13.0 <= kc_21_ptr <= 15.0, f"KC 2021-22 PTR anomaly not resolved: {kc_21_ptr:.2f}"
    
    # All wave means should be between 13 and 16
    for w, grp in sec.groupby("crdc_wave"):
        m_ptr = grp["school_ptr"].mean()
        assert 13.0 <= m_ptr <= 16.0, f"Wave {w} KC PTR out of bounds: {m_ptr:.2f}"


def test_class_size_linkage_integrity(context_df, course_df):
    """Verify exact match of linked schools between course panel and context panel."""
    course_schools_by_wave = course_df.groupby("crdc_wave")["nces_school_id"].nunique()
    context_linked_by_wave = context_df[context_df["in_class_size_panel"]].groupby("crdc_wave")["nces_school_id"].nunique()
    
    for w in course_schools_by_wave.index:
        c_count = course_schools_by_wave[w]
        ctx_count = context_linked_by_wave.get(w, 0)
        assert c_count == ctx_count, f"Wave {w} school count mismatch: course={c_count}, context={ctx_count}"


def test_longitudinal_dimension_shifts(context_df):
    """Verify calibrated longitudinal shifts within valid regimes."""
    sec = context_df[context_df["in_class_size_panel"]]
    
    # 504 more than doubles in pooled student rate from 2013-14 (2.24%) to 2023-24 (5.45%)
    sub13 = sec[sec["crdc_wave"] == "2013-14"]
    sub23 = sec[sec["crdc_wave"] == "2023-24"]
    p504_13 = sub13["sec504_count"].sum() / sub13["school_enrollment"].sum() * 100.0
    p504_23 = sub23["sec504_count"].sum() / sub23["school_enrollment"].sum() * 100.0
    assert p504_23 > 2.0 * p504_13, f"Expected 504 pooled to double: {p504_13:.2f}% to {p504_23:.2f}%"
    
    # Class size eased over decade rather than remaining flat
    cs_13 = (sub13["stem_enrolled_tot"] * sub13["enr_weighted_class_size"]).sum() / sub13["stem_enrolled_tot"].sum()
    cs_23 = (sub23["stem_enrolled_tot"] * sub23["enr_weighted_class_size"]).sum() / sub23["stem_enrolled_tot"].sum()
    assert cs_23 < cs_13 - 2.0, f"Expected class size to ease from ~22.4 to ~19.7, found {cs_13:.2f} to {cs_23:.2f}"
