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

if __name__ == "__main__":
    pytest.main([__file__])
