"""
Unit tests for CRDC Variable Harmonization and Anomaly Rules (Phase 1 & 2).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest
from src.harmonize_crdc import clean_crdc_val, clean_series, sum_clean_series, clean_combokey

def test_negative_reserve_codes_converted_to_nan():
    """Negative CRDC reserve codes (-9, -5, -7, -1, etc.) must NEVER enter arithmetic."""
    assert np.isnan(clean_crdc_val("-9"))
    assert np.isnan(clean_crdc_val(-9))
    assert np.isnan(clean_crdc_val("-5"))
    assert np.isnan(clean_crdc_val("-7"))
    assert np.isnan(clean_crdc_val("-1"))
    assert np.isnan(clean_crdc_val("-11"))
    assert np.isnan(clean_crdc_val(""))
    assert np.isnan(clean_crdc_val(None))
    assert np.isnan(clean_crdc_val(np.nan))

def test_valid_numbers_preserved():
    """Non-negative values must be correctly converted to float."""
    assert clean_crdc_val("0") == 0.0
    assert clean_crdc_val("24") == 24.0
    assert clean_crdc_val(25.5) == 25.5
    assert clean_crdc_val(100) == 100.0

def test_vectorized_clean_series():
    """Series cleaning converts negatives and non-numerics to NaN while preserving valid counts."""
    s = pd.Series(["10", "-9", "0", "45", "-5", "abc", None])
    cleaned = clean_series(s)
    expected = pd.Series([10.0, np.nan, 0.0, 45.0, np.nan, np.nan, np.nan])
    pd.testing.assert_series_equal(cleaned, expected)

def test_sum_clean_series():
    """Summing demographic components ignores NaNs unless all components are NaN."""
    s1 = pd.Series([10.0, np.nan, np.nan, 5.0])
    s2 = pd.Series([15.0, 20.0, np.nan, 5.0])
    s3 = pd.Series([np.nan, np.nan, np.nan, 2.0])
    res = sum_clean_series(s1, s2, s3)
    expected = pd.Series([25.0, 20.0, np.nan, 12.0])
    pd.testing.assert_series_equal(res, expected)

def test_sum_clean_series_require_complete():
    """When require_complete=True, rows with partial missingness among active columns evaluate to NaN."""
    s1 = pd.Series([10.0, 15.0, np.nan, np.nan])
    s2 = pd.Series([20.0, np.nan, np.nan, 25.0]) # Row 1 has s1=15, s2=NaN -> partial missingness
    s3_uncollected = pd.Series([np.nan, np.nan, np.nan, np.nan]) # Uncollected column (e.g. nonbinary)
    res = sum_clean_series(s1, s2, s3_uncollected, require_complete=True)
    expected = pd.Series([30.0, np.nan, np.nan, np.nan])
    pd.testing.assert_series_equal(res, expected)

def test_combokey_cleaning():
    """Combokey must be standardized to a 12-digit string, resolving scientific notation and leading zeros."""
    s = pd.Series(["290531000170", "290531000170.0", "10000201705", "  290531000170  "])
    cleaned = clean_combokey(s)
    assert cleaned.iloc[0] == "290531000170"
    assert cleaned.iloc[1] == "290531000170"
    assert cleaned.iloc[2] == "010000201705" # Padded to 12 digits
    assert cleaned.iloc[3] == "290531000170"

if __name__ == "__main__":
    pytest.main([__file__])
