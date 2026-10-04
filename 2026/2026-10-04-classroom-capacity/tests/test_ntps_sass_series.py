"""
tests/test_ntps_sass_series.py
Phase 5 Unit Tests: SASS / NTPS Series Construction, Historical Harmonization, and Validation

Verifies:
  1. Multi-wave series completeness across all 7 SASS/NTPS cycles (1999-2000 to 2020-21).
  2. Verbatim published NCES benchmark values (2011-12, 2015-16, 2017-18, 2020-21).
  3. State coverage for United States, Missouri, and Kansas.
  4. 50-state + DC panel completeness and boundary properties.
  5. Estimand hierarchy and concordance: CRDC student-weighted (C) aligns with NTPS (D) while rejecting unweighted cell mean (B) and CCD PTR (A).
  6. Mathematical consistency of derived schedule loads (R = k * section_mean).
  7. Monotonic scaling of individual teacher instructional complexity exposures.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
TABLES_DIR = os.path.join(PROJECT_ROOT, "artifacts", "tables")


@pytest.fixture(scope="module")
def canonical_series():
    path = os.path.join(PROCESSED_DIR, "ntps_sass_class_size_series.csv")
    assert os.path.exists(path), f"Missing {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def ntps_state_panel():
    path = os.path.join(PROCESSED_DIR, "ntps_2020_21_state_class_size.csv")
    assert os.path.exists(path), f"Missing {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def crosswalk_table():
    path = os.path.join(TABLES_DIR, "table_c02_crdc_vs_ntps_crosswalk.csv")
    assert os.path.exists(path), f"Missing {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def schedule_table():
    path = os.path.join(TABLES_DIR, "table_c04_teacher_schedule_roster_loads.csv")
    assert os.path.exists(path), f"Missing {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def complexity_table():
    path = os.path.join(TABLES_DIR, "table_c05_teacher_iep_el_exposure.csv")
    assert os.path.exists(path), f"Missing {path}"
    return pd.read_csv(path)


def test_series_cycle_completeness(canonical_series):
    """Verify that all 7 survey cycles are represented in the canonical series."""
    cycles = set(canonical_series["survey_cycle"].unique())
    expected_cycles = {
        "1999-2000 (SASS)",
        "2003-04 (SASS)",
        "2007-08 (SASS)",
        "2011-12 (SASS)",
        "2015-16 (NTPS)",
        "2017-18 (NTPS)",
        "2020-21 (NTPS)",
    }
    assert expected_cycles.issubset(cycles), f"Missing cycles: {expected_cycles - cycles}"


def test_national_benchmarks_verbatim(canonical_series):
    """Verify official verbatim published NCES class size benchmarks."""
    us_data = canonical_series[canonical_series["geography"] == "United States"]
    
    # 2011-12 SASS High School Departmentalized: 24.2
    s11 = us_data[(us_data["survey_cycle"] == "2011-12 (SASS)") & (us_data["school_level"] == "High School")]
    assert len(s11) == 1
    assert s11["class_size_mean"].values[0] == pytest.approx(24.2, 0.01)
    
    # 2015-16 NTPS High School Departmentalized: 26.0
    s15 = us_data[(us_data["survey_cycle"] == "2015-16 (NTPS)") & (us_data["school_level"] == "High School")]
    assert len(s15) == 1
    assert s15["class_size_mean"].values[0] == pytest.approx(26.0, 0.01)
    
    # 2017-18 NTPS High School Departmentalized: 23.3
    s17 = us_data[(us_data["survey_cycle"] == "2017-18 (NTPS)") & (us_data["school_level"] == "High School")]
    assert len(s17) == 1
    assert s17["class_size_mean"].values[0] == pytest.approx(23.3, 0.01)
    
    # 2020-21 NTPS High School Departmentalized: 21.0
    s21_hs = us_data[(us_data["survey_cycle"] == "2020-21 (NTPS)") & (us_data["school_level"] == "High School") & (us_data["subject"] == "All / General")]
    assert len(s21_hs) == 1
    assert s21_hs["class_size_mean"].values[0] == pytest.approx(21.0, 0.01)
    
    # 2020-21 NTPS Middle School Departmentalized: 22.0
    s21_mid = us_data[(us_data["survey_cycle"] == "2020-21 (NTPS)") & (us_data["school_level"] == "Middle School")]
    assert len(s21_mid) == 1
    assert s21_mid["class_size_mean"].values[0] == pytest.approx(22.0, 0.01)
    
    # 2020-21 NTPS Elementary School Self-Contained: 19.1
    s21_el = us_data[(us_data["survey_cycle"] == "2020-21 (NTPS)") & (us_data["school_level"] == "Elementary School")]
    assert len(s21_el) == 1
    assert s21_el["class_size_mean"].values[0] == pytest.approx(19.1, 0.01)


def test_state_coverage_us_mo_ks(canonical_series):
    """Verify that US, MO, and KS have valid observations across all applicable survey waves."""
    geos = set(canonical_series["geography"].unique())
    assert {"United States", "Missouri", "Kansas"}.issubset(geos)
    
    for geo in ["United States", "Missouri", "Kansas"]:
        sub = canonical_series[canonical_series["geography"] == geo]
        assert len(sub) >= 10, f"Insufficient records for {geo}"
        assert sub["class_size_mean"].notna().all(), f"Found NaNs in {geo} class_size_mean"


def test_50_state_panel_completeness(ntps_state_panel):
    """Verify that the 2020-21 NTPS state panel contains 50 states + DC + US."""
    assert len(ntps_state_panel) == 52
    assert "United States" in ntps_state_panel["state"].values
    assert "District of Columbia" in ntps_state_panel["state"].values
    
    # Check that high school departmentalized is populated for major states
    for st in ["California", "Texas", "Florida", "New York", "Missouri", "Kansas"]:
        val = ntps_state_panel.loc[ntps_state_panel["state"] == st, "sec_high_departmentalized"].values[0]
        assert pd.notna(val)
        assert 15.0 <= val <= 30.0, f"Out-of-bounds class size for {st}: {val}"


def test_crdc_vs_ntps_crosswalk_hierarchy(crosswalk_table):
    """
    Verify the fundamental estimand hierarchy:
      Macro PTR (A) < CRDC Unweighted (B) < CRDC Student-Weighted (C) ~= NTPS Teacher-Reported (D)
    """
    for _, row in crosswalk_table.iterrows():
        a = row["ccd_macro_ptr"]
        b = row["crdc_unweighted_cell_mean"]
        c = row["crdc_student_weighted_mean"]
        
        # Student-weighted C must strictly exceed unweighted cell mean B (Weighting Gap > 0)
        assert c > b, f"Weighting gap violated in {row['school_year']}: C={c}, B={b}"
        assert row["weighting_gap_c_minus_b"] >= 4.0, f"Unexpectedly small weighting gap in {row['school_year']}"
        
        # Student-weighted C must strictly exceed macro staffing ratio A (PTR Wedge > 0)
        if pd.notna(a):
            assert c > a, f"PTR wedge violated in {row['school_year']}: C={c}, PTR={a}"
            assert row["ptr_wedge_c_minus_ptr"] >= 4.0, f"Unexpectedly small PTR wedge in {row['school_year']}"
            
        # Where NTPS D is observed, it must track within 3.5 students of CRDC C
        d = row["ntps_teacher_hs_dept"]
        if pd.notna(d):
            gap = abs(d - c)
            assert gap <= 3.5, f"Excessive divergence between NTPS ({d}) and CRDC ({c}) in {row['school_year']}"


def test_schedule_load_math(schedule_table):
    """Verify that Active Roster Load exactly equals section_mean * cycle_sections."""
    for _, row in schedule_table.iterrows():
        expected_roster = round(row["section_mean"] * row["cycle_active_sections"], 1)
        actual_roster = row["active_grading_roster"]
        assert actual_roster == pytest.approx(expected_roster, 0.05), (
            f"Math mismatch in {row['environment']} {row['schedule_regime']}: {actual_roster} vs {expected_roster}"
        )
        
        expected_delta = round(actual_roster - 125.0, 1)
        actual_delta = row["delta_vs_jenkins_ceiling"]
        assert actual_delta == pytest.approx(expected_delta, 0.05)


def test_teacher_complexity_scaling(complexity_table):
    """Verify that expected legal accommodations scale monotonically with roster headcount."""
    sorted_df = complexity_table.sort_values("total_active_students")
    
    # Verify monotonic increase of accommodated student count
    accommodations = sorted_df["expected_combined_accommodations"].tolist()
    headcounts = sorted_df["total_active_students"].tolist()
    
    for i in range(1, len(accommodations)):
        assert accommodations[i] >= accommodations[i - 1], (
            f"Non-monotonic accommodation scaling: {accommodations[i]} < {accommodations[i - 1]} "
            f"at headcounts {headcounts[i]} vs {headcounts[i - 1]}"
        )
        
    # Elementary self-contained teacher has ~3-4 accommodations; secondary teacher has ~20-28
    elem_row = complexity_table[complexity_table["school_level"] == "Elementary School"].iloc[0]
    sec_rows = complexity_table[complexity_table["school_level"] == "High School"]
    
    assert elem_row["expected_combined_accommodations"] < 5.0
    assert sec_rows["expected_combined_accommodations"].min() >= 18.0


if __name__ == "__main__":
    pytest.main([__file__])
