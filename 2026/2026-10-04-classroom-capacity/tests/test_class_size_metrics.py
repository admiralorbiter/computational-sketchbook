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

if __name__ == "__main__":
    pytest.main([__file__])
