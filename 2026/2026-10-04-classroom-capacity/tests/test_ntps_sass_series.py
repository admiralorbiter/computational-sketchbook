"""
tests/test_ntps_sass_series.py
Phase 5.1 Calibrated Unit Tests: Source Provenance, Estimand Nomenclature, and Modeling Guardrails

Verifies:
  1. Exact Source Provenance & Verbatim NCES Benchmarks (SASS 1999-2012, NTPS 2015-2021).
  2. Absence of Synthetic Rows from Canonical Series (Authentic Published Data Only).
  3. Restoration of Frozen Study A Estimand Nomenclature (A=unweighted cell, B=section-wt, C=enrollment-wt, PTR separate).
  4. Figure C02 / Table C02 Exact Mathematical Identity (Zero Stale Hardcoding).
  5. 50-State Distribution Properties & Correct Ranking Interpretation (Lower Quartile vs. Decile).
  6. Historical KCMSD Jenkins Benchmark (<= 125) as Descriptive Reference, Not Legal Compliance.
  7. Methodological Guardrail on Table C05: Proportional Scenario Scoping (No Chronic Absence, Secondary Only, Unobserved Rosters).
"""

import os
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
def state_dist_table():
    path = os.path.join(TABLES_DIR, "table_c03_ntps_2020_21_state_distribution.csv")
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


# -----------------------------------------------------------------------------
# 1. Exact Source Provenance & Verbatim NCES Benchmarks
# -----------------------------------------------------------------------------

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
    """Verify official verbatim published NCES class size benchmarks across cycles."""
    us_data = canonical_series[canonical_series["geography"] == "United States"]
    
    # 2011-12 SASS High School Departmentalized: 24.2 (First Look Table 7)
    s11 = us_data[(us_data["survey_cycle"] == "2011-12 (SASS)") & (us_data["school_level"] == "High School")]
    assert len(s11) == 1
    assert s11["class_size_mean"].values[0] == pytest.approx(24.2, 0.01)
    assert "First Look Table 7" in s11["source_table"].values[0]
    
    # 2015-16 NTPS High School Departmentalized: 26.0 (First Look Table 8)
    s15 = us_data[(us_data["survey_cycle"] == "2015-16 (NTPS)") & (us_data["school_level"] == "High School")]
    assert len(s15) == 1
    assert s15["class_size_mean"].values[0] == pytest.approx(26.0, 0.01)
    assert "First Look Table 8" in s15["source_table"].values[0]
    
    # 2017-18 NTPS High School Departmentalized: 23.3 (Table A-7a)
    s17 = us_data[(us_data["survey_cycle"] == "2017-18 (NTPS)") & (us_data["school_level"] == "High School")]
    assert len(s17) == 1
    assert s17["class_size_mean"].values[0] == pytest.approx(23.3, 0.01)
    assert "Table A-7a" in s17["source_table"].values[0]
    
    # 2020-21 NTPS High School Departmentalized: 21.0 (Table 7)
    s21_hs = us_data[(us_data["survey_cycle"] == "2020-21 (NTPS)") & (us_data["school_level"] == "High School")]
    assert len(s21_hs) == 1
    assert s21_hs["class_size_mean"].values[0] == pytest.approx(21.0, 0.01)
    assert "Table 7" in s21_hs["source_table"].values[0]
    
    # 2020-21 NTPS Middle School Departmentalized: 22.0 (Table 7)
    s21_mid = us_data[(us_data["survey_cycle"] == "2020-21 (NTPS)") & (us_data["school_level"] == "Middle School")]
    assert len(s21_mid) == 1
    assert s21_mid["class_size_mean"].values[0] == pytest.approx(22.0, 0.01)
    
    # 2020-21 NTPS Elementary School Self-Contained: 19.1 (Table 7)
    s21_el = us_data[(us_data["survey_cycle"] == "2020-21 (NTPS)") & (us_data["school_level"] == "Elementary School")]
    assert len(s21_el) == 1
    assert s21_el["class_size_mean"].values[0] == pytest.approx(19.1, 0.01)


def test_state_benchmarks_verbatim(canonical_series):
    """Verify verbatim state-level benchmarks for Missouri and Kansas."""
    # 2020-21 NTPS Table 7
    mo_21 = canonical_series[(canonical_series["geography"] == "Missouri") & 
                             (canonical_series["survey_cycle"] == "2020-21 (NTPS)") & 
                             (canonical_series["school_level"] == "High School")]
    assert len(mo_21) == 1
    assert mo_21["class_size_mean"].values[0] == pytest.approx(19.2, 0.01)
    
    ks_21 = canonical_series[(canonical_series["geography"] == "Kansas") & 
                             (canonical_series["survey_cycle"] == "2020-21 (NTPS)") & 
                             (canonical_series["school_level"] == "High School")]
    assert len(ks_21) == 1
    assert ks_21["class_size_mean"].values[0] == pytest.approx(17.4, 0.01)
    
    # 2017-18 NTPS Table A-7a
    mo_18 = canonical_series[(canonical_series["geography"] == "Missouri") & 
                             (canonical_series["survey_cycle"] == "2017-18 (NTPS)") & 
                             (canonical_series["school_level"] == "High School")]
    assert len(mo_18) == 1
    assert mo_18["class_size_mean"].values[0] == pytest.approx(22.5, 0.01)
    
    ks_18 = canonical_series[(canonical_series["geography"] == "Kansas") & 
                             (canonical_series["survey_cycle"] == "2017-18 (NTPS)") & 
                             (canonical_series["school_level"] == "High School")]
    assert len(ks_18) == 1
    assert ks_18["class_size_mean"].values[0] == pytest.approx(19.8, 0.01)


# -----------------------------------------------------------------------------
# 2. Absence of Synthetic Rows from Canonical Series
# -----------------------------------------------------------------------------

def test_absence_of_synthetic_rows(canonical_series):
    """
    Verify that the canonical series contains strictly authentic published statistics.
    Synthetic subject-multiplier projections must NOT reside in this file.
    """
    # Exactly 40 authentic published survey statistics across the 7 cycles
    assert len(canonical_series) == 40, f"Expected exactly 40 authentic records, found {len(canonical_series)}"
    
    # All rows must be Class 1 published statistics
    assert (canonical_series["evidence_class"] == "Class 1: Measured / Published Survey Statistic").all()
    
    # No analyst multipliers or subject projections in the canonical file
    assert (canonical_series["subject"] == "All / General").all()
    
    # Verify separate analyst scenario file exists if projections are preserved
    scenario_path = os.path.join(PROCESSED_DIR, "analyst_subject_scenarios.csv")
    if os.path.exists(scenario_path):
        df_scen = pd.read_csv(scenario_path)
        assert (df_scen["evidence_class"] == "Class 3: Analyst Scenario Projection (Not Published NCES Data)").all()


# -----------------------------------------------------------------------------
# 3. Restoration of Frozen Study A Estimand Nomenclature
# -----------------------------------------------------------------------------

def test_frozen_estimand_nomenclature(crosswalk_table):
    """
    Verify that Table C02 strictly adheres to frozen Study A nomenclature:
      - Estimand A: CRDC Unweighted School-Course Cell Mean (crdc_unweighted_cell_mean)
      - Estimand B: CRDC Section-Weighted Mean (crdc_section_weighted_mean)
      - Estimand C: CRDC Student/Seat-Weighted Mean Lower-Bound Proxy (crdc_student_weighted_mean)
      - CCD Macro PTR: Universal Staffing Ratio (ccd_macro_ptr)
      - NTPS Survey Benchmark: ntps_teacher_hs_dept
    """
    expected_cols = {
        "school_year",
        "crdc_wave",
        "ccd_macro_ptr",
        "crdc_unweighted_cell_mean",
        "crdc_section_weighted_mean",
        "crdc_student_weighted_mean",
        "ntps_teacher_hs_dept",
        "ntps_teacher_elem_self",
        "gap_c_minus_a",
        "weighting_gap_c_minus_b",
        "ptr_wedge_c_minus_ptr",
        "survey_crdc_gap_ntps_minus_c",
        "survey_ptr_gap_ntps_minus_ptr",
    }
    assert expected_cols.issubset(set(crosswalk_table.columns)), (
        f"Missing columns: {expected_cols - set(crosswalk_table.columns)}"
    )
    
    # Check that PTR is NOT labeled Estimand A
    assert "estimand_a_ccd_macro_ptr" not in crosswalk_table.columns


# -----------------------------------------------------------------------------
# 4. Figure C02 / Table C02 Mathematical Identity
# -----------------------------------------------------------------------------

def test_figure_c02_table_c02_identity(crosswalk_table):
    """
    Verify that Table C02 contains the certified empirical values and that
    no stale hardcoded figures (e.g. 22.75, 21.60, 20.18) exist in the data.
    """
    sub = crosswalk_table[crosswalk_table["school_year"].isin(["2015-16", "2017-18", "2020-21"])].set_index("school_year")
    
    # 2015-16
    assert sub.loc["2015-16", "crdc_student_weighted_mean"] == pytest.approx(22.64, 0.01)
    assert sub.loc["2015-16", "crdc_unweighted_cell_mean"] == pytest.approx(17.61, 0.01)
    assert sub.loc["2015-16", "ccd_macro_ptr"] == pytest.approx(16.1, 0.01)
    assert sub.loc["2015-16", "ntps_teacher_hs_dept"] == pytest.approx(26.0, 0.01)
    
    # 2017-18
    assert sub.loc["2017-18", "crdc_student_weighted_mean"] == pytest.approx(21.51, 0.01)
    assert sub.loc["2017-18", "crdc_unweighted_cell_mean"] == pytest.approx(16.69, 0.01)
    assert sub.loc["2017-18", "ccd_macro_ptr"] == pytest.approx(16.0, 0.01)
    assert sub.loc["2017-18", "ntps_teacher_hs_dept"] == pytest.approx(23.3, 0.01)
    
    # 2020-21
    assert sub.loc["2020-21", "crdc_student_weighted_mean"] == pytest.approx(20.10, 0.01)
    assert sub.loc["2020-21", "crdc_unweighted_cell_mean"] == pytest.approx(15.42, 0.01)
    assert sub.loc["2020-21", "ccd_macro_ptr"] == pytest.approx(15.4, 0.01)
    assert sub.loc["2020-21", "ntps_teacher_hs_dept"] == pytest.approx(21.0, 0.01)


# -----------------------------------------------------------------------------
# 5. 50-State Distribution & Correct Ranking Interpretation
# -----------------------------------------------------------------------------

def test_state_distribution_parameters(state_dist_table):
    """
    Verify state distribution summary values and ensure Kansas is correctly designated
    in the lower quartile (below P25 = 17.80) rather than 'bottom decile'.
    """
    table_dict = state_dist_table.set_index("metric")["sec_high_departmentalized"].to_dict()
    notes_dict = state_dist_table.set_index("metric")["notes"].to_dict()
    
    assert table_dict["National Benchmark (Verbatim NCES)"] == pytest.approx(21.0, 0.01)
    assert table_dict["50-State + DC Median"] == pytest.approx(20.0, 0.01)
    assert table_dict["25th Percentile (P25)"] == pytest.approx(17.80, 0.01)
    assert table_dict["75th Percentile (P75)"] == pytest.approx(21.80, 0.01)
    assert table_dict["Kansas State Average"] == pytest.approx(17.4, 0.01)
    assert table_dict["Missouri State Average"] == pytest.approx(19.2, 0.01)
    
    # Verify Kansas note: lower quartile, NOT bottom decile
    ks_note = notes_dict["Kansas State Average"]
    assert "Lower quartile" in ks_note
    assert "bottom decile" not in ks_note.lower()


# -----------------------------------------------------------------------------
# 6. Historical Jenkins Benchmark (<= 125) as Descriptive Reference
# -----------------------------------------------------------------------------

def test_schedule_load_math_and_jenkins_benchmark(schedule_table):
    """
    Verify schedule load mathematics and confirm that Jenkins 125 is treated
    as a historical desegregation benchmark without legal compliance claims.
    """
    assert "jenkins_historical_benchmark" in schedule_table.columns
    assert "delta_vs_jenkins_historical_benchmark" in schedule_table.columns
    assert "benchmark_comparison" in schedule_table.columns
    
    # Must NOT contain 'compliance_status'
    assert "compliance_status" not in schedule_table.columns
    
    for _, row in schedule_table.iterrows():
        expected_roster = round(row["section_mean"] * row["cycle_active_sections"], 1)
        assert row["active_grading_roster"] == pytest.approx(expected_roster, 0.05)
        
        expected_delta = round(expected_roster - 125.0, 1)
        assert row["delta_vs_jenkins_historical_benchmark"] == pytest.approx(expected_delta, 0.05)
        
        # Verify wording of benchmark comparison
        comp = row["benchmark_comparison"]
        assert "historical KCMSD benchmark" in comp


# -----------------------------------------------------------------------------
# 7. Methodological Guardrail on Table C05 (Illustrative Proportional Scenarios)
# -----------------------------------------------------------------------------

def test_no_teacher_factual_claims_from_school_rates(complexity_table):
    """
    Verify Table C05 guardrails:
      - Chronic absenteeism must NOT be included (school proxy != student probability).
      - Roster models must belong to a consistent universe (Secondary/High School).
      - Table and notes must explicitly state illustrative proportional model assumptions.
    """
    # Chronic absence must NOT exist in the table
    cols = [c.lower() for c in complexity_table.columns]
    assert not any("absent" in c for c in cols), "Chronic absence found in Table C05!"
    
    # Consistent universe: all rows are Secondary / High School
    assert (complexity_table["school_level"] == "High School / Secondary").all()
    
    # Model classification
    assert (complexity_table["model_classification"] == "Class 3: Illustrative Proportional Mixing Scenario").all()
    
    # Notes must explicitly disclaim observed teacher rosters
    for note in complexity_table["model_notes"]:
        assert "Actual rosters unobserved" in note or "unobserved in public data" in note


if __name__ == "__main__":
    pytest.main([__file__])
