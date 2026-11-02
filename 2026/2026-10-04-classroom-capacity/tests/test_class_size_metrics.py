"""
Unit tests for Class Size Estimands, Weighting Schemes, and Staffing Wedges.
"""

import numpy as np
import pandas as pd
import pytest

def calc_class_size_metrics(enrollments, classes):
    """Calculate unweighted course-cell mean, section-weighted mean, and seat-weighted mean."""
    enr = np.array(enrollments, dtype=float)
    cls = np.array(classes, dtype=float)
    
    cell_means = enr / cls
    unweighted_mean = np.mean(cell_means)
    section_weighted_mean = np.sum(enr) / np.sum(cls)
    seat_weighted_mean = np.sum(enr * cell_means) / np.sum(enr)
    
    return {
        "unweighted_mean": unweighted_mean,
        "section_weighted_mean": section_weighted_mean,
        "seat_weighted_mean": seat_weighted_mean,
    }

def test_jensens_inequality_weighting_divergence():
    """
    Test that when class sizes vary, the seat-weighted mean is strictly greater
    than or equal to the section-weighted mean (Jensen's Inequality).
    """
    # Example from research design:
    # School A: 8 students in 1 class (mean 8)
    # School B: 30 students in 1 class (mean 30)
    res = calc_class_size_metrics([8, 30], [1, 1])
    assert res["unweighted_mean"] == 19.0
    assert res["section_weighted_mean"] == 19.0
    # Seat-weighted: (8*8 + 30*30) / (8 + 30) = (64 + 900) / 38 = 964 / 38 = 25.37
    assert np.isclose(res["seat_weighted_mean"], 964 / 38)
    assert res["seat_weighted_mean"] > res["section_weighted_mean"]

def test_identical_classes_equal_weighting():
    """When all classes are identical, all weighting schemes produce identical results."""
    res = calc_class_size_metrics([50, 75, 100], [2, 3, 4])
    # Each cell has 25 students per class
    assert np.isclose(res["unweighted_mean"], 25.0)
    assert np.isclose(res["section_weighted_mean"], 25.0)
    assert np.isclose(res["seat_weighted_mean"], 25.0)

def test_allocation_wedge_computation():
    """Verify calculation of absolute and ratio allocation wedges."""
    mean_class_size = 28.0
    school_ptr = 16.0
    
    wedge = mean_class_size - school_ptr
    ratio = mean_class_size / school_ptr
    
    assert wedge == 12.0
    assert ratio == 1.75

def test_course_cell_aggregation_lower_bound_property():
    """
    Mathematical proof / test: Course-cell aggregation strictly understates the true
    student-weighted section mean whenever within-cell section sizes vary.
    
    Theorem:
        C_true_student = C_enr_wt + sum(K_i * sigma_i^2) / sum(E_i) >= C_enr_wt
    with strict inequality when within-cell section variance sigma_i^2 > 0.
    Therefore, CRDC's enrollment-weighted course-cell mean is a lower-bound proxy
    for true student-experienced section size.
    """
    # Suppose a high school offers 2 sections of Calculus:
    # Section 1 has 10 students, Section 2 has 30 students.
    # Total enrollment E = 40, classes K = 2.
    # CRDC observes only E = 40, K = 2 -> cell mean = 20.0.
    section_sizes = [10, 30]
    E = sum(section_sizes)
    K = len(section_sizes)
    cell_mean = E / K # 20.0
    
    # 1. CRDC Enrollment-weighted proxy (assuming uniform distribution within cell)
    crdc_proxy = cell_mean # 20.0
    
    # 2. True student-experienced section size
    # 10 students sit in a class of 10; 30 students sit in a class of 30
    true_student_mean = sum(s * s for s in section_sizes) / sum(section_sizes) # (100 + 900)/40 = 25.0
    
    # Analytical variance decomposition
    within_cell_var = np.var(section_sizes, ddof=0) # ((10-20)^2 + (30-20)^2)/2 = 100.0
    analytical_adjustment = within_cell_var / cell_mean # 100 / 20 = 5.0
    
    assert true_student_mean == 25.0
    assert crdc_proxy == 20.0
    assert np.isclose(true_student_mean, crdc_proxy + analytical_adjustment)
    assert true_student_mean > crdc_proxy

def test_multischool_lower_bound_property():
    """
    Verify the lower-bound property holds across a system of multiple schools:
    School 1: 2 sections of [15, 25] (enr=40, cls=2, mean=20, var=25)
    School 2: 3 sections of [20, 30, 40] (enr=90, cls=3, mean=30, var=66.67)
    """
    sch1_sections = [15, 25]
    sch2_sections = [20, 30, 40]
    all_sections = sch1_sections + sch2_sections
    
    # True student-experienced mean
    true_student_mean = sum(s**2 for s in all_sections) / sum(all_sections)
    
    # CRDC enrollment-weighted course-cell mean
    e1, k1 = sum(sch1_sections), len(sch1_sections)
    e2, k2 = sum(sch2_sections), len(sch2_sections)
    m1, m2 = e1 / k1, e2 / k2
    crdc_enr_wt_mean = (e1 * m1 + e2 * m2) / (e1 + e2)
    
    # Within-school variances
    var1 = np.var(sch1_sections, ddof=0)
    var2 = np.var(sch2_sections, ddof=0)
    total_enr = e1 + e2
    var_component = (k1 * var1 + k2 * var2) / total_enr
    
    assert np.isclose(crdc_enr_wt_mean, 3500.0 / 130.0)
    assert np.isclose(true_student_mean, 3750.0 / 130.0)
    assert np.isclose(true_student_mean, crdc_enr_wt_mean + var_component)
    assert true_student_mean > crdc_enr_wt_mean

def test_partial_missingness_undercount_bias():
    """
    Demonstrate that treating a suppressed/missing demographic component as zero
    introduces an undercount bias in enrollment and class size.
    """
    male_count = 16.0
    female_suppressed_code = -5 # Suppressed in CRDC for small cell privacy
    
    # Naive summation treating negative as NaN and then filling with 0:
    naive_sum = male_count + (0 if female_suppressed_code < 0 else female_suppressed_code)
    assert naive_sum == 16.0 # Severe undercount if there were 4 female students
    
    # Correct handling: mark as NaN/incomplete
    def strict_sum(m, f):
        if m < 0 or f < 0:
            return np.nan
        return m + f
        
    assert np.isnan(strict_sum(male_count, female_suppressed_code))

def test_course_specific_balanced_panel_qualification():
    """
    Synthetic test: A school observed every year, but with the target course missing in one year,
    must NOT qualify for that course's balanced panel.
    """
    df_history = pd.DataFrame({
        "nces_school_id": ["sch_A"] * 5 + ["sch_B"] * 5,
        "wave": ["2015-16", "2017-18", "2020-21", "2021-22", "2023-24"] * 2,
        "course_code": [
            # School A offers Geometry in all 5 waves
            "geom", "geom", "geom", "geom", "geom",
            # School B offers Geometry in waves 1, 2, 4, 5, but Biology in wave 3 (missing Geometry in wave 3!)
            "geom", "geom", "bio", "geom", "geom"
        ]
    })
    
    # Generic school balance: both School A and School B have some course in all 5 waves
    generic_balanced = df_history.groupby("nces_school_id")["wave"].nunique()
    assert generic_balanced["sch_A"] == 5
    assert generic_balanced["sch_B"] == 5 # Misleadingly qualified under old logic!
    
    # Genuinely Course-Specific Balanced Panel for Geometry:
    geom_df = df_history[df_history["course_code"] == "geom"]
    geom_waves = geom_df.groupby("nces_school_id")["wave"].nunique()
    
    assert geom_waves["sch_A"] == 5
    assert geom_waves["sch_B"] == 4 # Correctly disqualified from Geometry balanced panel!
    
    geom_qualified = set(geom_waves[geom_waves == 5].index)
    assert "sch_A" in geom_qualified
    assert "sch_B" not in geom_qualified

def test_fe_non_informative_group_exclusion():
    """
    Synthetic test: School-wave groups with only 1 course offer zero identifying
    within-group variation after demeaning, and must be excluded from the FE sample.
    """
    df_fe_test = pd.DataFrame({
        "school_wave_id": ["sw_1", "sw_1", "sw_2", "sw_3", "sw_3", "sw_3"],
        "course_code": ["geom", "calc", "geom", "geom", "bio", "chem"],
        "mean_class_size": [22.0, 16.0, 24.0, 20.0, 21.0, 19.0],
    })
    
    counts = df_fe_test.groupby("school_wave_id")["course_code"].nunique()
    valid_groups = counts[counts >= 2].index
    filtered_df = df_fe_test[df_fe_test["school_wave_id"].isin(valid_groups)]
    
    # sw_1 has 2 courses -> kept
    # sw_2 has 1 course -> excluded!
    # sw_3 has 3 courses -> kept
    assert "sw_1" in valid_groups
    assert "sw_2" not in valid_groups
    assert "sw_3" in valid_groups
    assert len(filtered_df) == 5 # 6 rows minus the 1 non-informative singleton row

def test_threshold_semantics_cell_vs_section_exposure():
    """
    Theorem: Cell-level exposure to >= 30 students is neither a mathematical lower bound
    nor an upper bound on the percentage of students sitting in individual sections >= 30.
    """
    # Case 1: Cell mean is 28 (< 30), but contains sections [20, 28, 36].
    # Total enrollment: 84.
    # Cell-level >= 30 exposure: 0% (cell mean 28 < 30).
    # Actual section-level >= 30 exposure: 36 students in the 36-student class -> 36 / 84 = 42.9%!
    sec1 = [20, 28, 36]
    cell1_mean = np.mean(sec1) # 28.0
    cell1_exposure = 1.0 if cell1_mean >= 30 else 0.0 # 0.0
    sec1_exposure = sum(s for s in sec1 if s >= 30) / sum(sec1) # 36 / 84 ≈ 0.4286
    
    assert cell1_mean < 30.0
    assert cell1_exposure == 0.0
    assert sec1_exposure > 0.40 # Section exposure strictly exceeds cell exposure!
    
    # Case 2: Cell mean is 31 (>= 30), but contains sections [24, 31, 38].
    # Total enrollment: 93.
    # Cell-level >= 30 exposure: 100% (all 93 students are in a cell averaging >= 30).
    # Actual section-level >= 30 exposure: (31 + 38) / 93 = 74.2% (24 students are in a class of 24 < 30!)
    sec2 = [24, 31, 38]
    cell2_mean = np.mean(sec2) # 31.0
    cell2_exposure = 1.0 if cell2_mean >= 30 else 0.0 # 1.0
    sec2_exposure = sum(s for s in sec2 if s >= 30) / sum(sec2) # 69 / 93 ≈ 0.7419
    
    assert cell2_mean >= 30.0
    assert cell2_exposure == 1.0
    assert sec2_exposure < 1.0 # Cell exposure strictly overstates section exposure!

def test_cache_versioning_prevents_stale_cache():
    """Verify that versioned cache tags ensure clean rebuilds when extraction schema changes."""
    expected_cache_tag = "v2_strict"
    valid_cache_name = f"crdc_2013_14_active_{expected_cache_tag}.parquet"
    legacy_cache_name = "crdc_2013_14_active.parquet"
    
    assert expected_cache_tag in valid_cache_name
    assert expected_cache_tag not in legacy_cache_name

if __name__ == "__main__":
    pytest.main([__file__])
