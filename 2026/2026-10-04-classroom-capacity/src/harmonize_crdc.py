"""
Harmonization library for the Civil Rights Data Collection (CRDC) Course Panel.
Supports waves: 2013-14, 2015-16, 2017-18, 2020-21, 2021-22, 2023-24.

Strict adherence to data discipline:
- Never treat negative exception/reserve codes (-9, -5, -7, etc.) as real numbers.
- School-course mean class size = course_enrollment / number_of_classes.
- Explicitly flags cells with mean_class_size > 60 for auditing.
- Flags KC metro schools using established 9-county MARC geography.
"""

from pathlib import Path
import re
import zipfile
import numpy as np
import pandas as pd

# 9-county KC MARC FIPS set
KC_COUNTY_FIPS = {"20209", "20091", "20103", "20121", "29047", "29095", "29037", "29177", "29165"}

COURSE_SPECS = [
    {"code": "alg1", "name": "Algebra I", "subject": "Math", "level": "Foundation Core"},
    {"code": "geom", "name": "Geometry", "subject": "Math", "level": "Foundation Core"},
    {"code": "alg2", "name": "Algebra II", "subject": "Math", "level": "Foundation Core"},
    {"code": "advm", "name": "Advanced Mathematics", "subject": "Math", "level": "Advanced / Specialized"},
    {"code": "calc", "name": "Calculus", "subject": "Math", "level": "Advanced / Specialized"},
    {"code": "bio", "name": "Biology", "subject": "Science", "level": "Foundation Core"},
    {"code": "chem", "name": "Chemistry", "subject": "Science", "level": "Foundation Core"},
    {"code": "phys", "name": "Physics", "subject": "Science", "level": "Advanced / Specialized"},
]

def clean_crdc_val(val):
    """
    Parse numeric CRDC values, converting negative exception/reserve codes to NaN.
    Negative CRDC reserve codes (-1, -2, -3, -5, -7, -9, -11, -12) must never enter arithmetic.
    """
    if pd.isna(val) or val is None or val == "":
        return np.nan
    try:
        f = float(val)
        return f if f >= 0 else np.nan
    except (ValueError, TypeError):
        return np.nan

def clean_series(series):
    """Vectorized cleaning of a pandas series for non-negative numeric values."""
    s_num = pd.to_numeric(series, errors="coerce")
    return s_num.where(s_num >= 0, np.nan)

def sum_clean_series(*series_list):
    """Sum a list of pandas series element-wise, ignoring NaNs unless all are NaN."""
    cleaned = [clean_series(s) for s in series_list]
    combined = pd.concat(cleaned, axis=1)
    # If all values in a row are NaN, sum should be NaN, not 0
    all_nan = combined.isna().all(axis=1)
    res = combined.fillna(0).sum(axis=1)
    return res.mask(all_nan, np.nan)

def clean_combokey(key_series, leaid_series=None, schid_series=None):
    """
    Reconstruct 12-digit NCES ID, handling Excel floating-point scientific notation.
    """
    if leaid_series is not None and schid_series is not None:
        l_str = leaid_series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(7)
        s_str = schid_series.astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(5)
        # Use LEAID+SCHID if both look valid
        valid_composite = (l_str.str.len() == 7) & (s_str.str.len() == 5)
        if valid_composite.all():
            return l_str + s_str
            
    # Fallback to COMBOKEY cleaning
    cleaned = (
        key_series.astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"\s+", "", regex=True)
    )
    return cleaned.str.zfill(12)
