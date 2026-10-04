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

def sum_clean_series(*series_list, require_complete=True):
    """
    Sum a list of pandas series element-wise.
    - If require_complete=True, any row with partial missingness among active columns
      (i.e. some valid, some NaN) evaluates to NaN to prevent undercounting.
      Columns that are entirely NaN (e.g. uncollected nonbinary fields) are ignored.
    - If require_complete=False, ignores NaNs unless all are NaN (standard sum).
    """
    cleaned = [clean_series(s) for s in series_list]
    combined = pd.concat(cleaned, axis=1)
    
    if require_complete:
        active_cols = combined.dropna(how="all", axis=1)
        if active_cols.empty:
            return pd.Series(np.nan, index=combined.index)
        has_any_nan = active_cols.isna().any(axis=1)
        res = active_cols.fillna(0).sum(axis=1)
        return res.mask(has_any_nan, np.nan)
    else:
        all_nan = combined.isna().all(axis=1)
        res = combined.fillna(0).sum(axis=1)
        return res.mask(all_nan, np.nan)

def sum_enrollment_with_nonbinary(m_series, f_series, x_series=None, require_complete=True):
    """
    Sum male, female, and optional nonbinary counts with strict reserve-code semantics:
    - Base binary enrollment (M + F) is required.
      If M or F is missing/suppressed (< 0 or NaN), base evaluates to NaN (under require_complete=True).
    - If x_series is None: returns base sum (M + F).
    - If x_series is provided:
        x_raw = pd.to_numeric(x_series, errors='coerce')
        - x >= 0: valid reported nonbinary count, added to base (M + F + x).
        - x in [-9, -10, -12]: structurally not collected / not reported / not applicable.
          Nonbinary reporting was optional under federal OCR rules for schools/districts that
          did not collect it. Binary (M + F) fully represents total enrollment; added as 0.
        - x in [-5, -6]: privacy suppression (1-2 or 1-4 students). The true count is positive but
          unobserved. If require_complete=True, evaluates to NaN to prevent undercounting.
        - x in [-3, -8] or other negative/NaN: genuinely missing/unreported when required.
          If require_complete=True, evaluates to NaN.
    """
    m_clean = clean_series(m_series)
    f_clean = clean_series(f_series)
    
    if require_complete:
        base_valid = m_clean.notna() & f_clean.notna()
        base = pd.Series(np.where(base_valid, m_clean + f_clean, np.nan), index=m_series.index)
    else:
        base = m_clean.fillna(0) + f_clean.fillna(0)
        base = base.mask(m_clean.isna() & f_clean.isna(), np.nan)
        
    if x_series is None:
        return base
        
    x_num = pd.to_numeric(x_series, errors="coerce")
    if x_num.isna().all():
        return base
        
    is_valid_x = x_num >= 0
    is_struct_skip = x_num.isin([-9, -10, -12])
    is_suppressed_or_missing = ~is_valid_x & ~is_struct_skip
    
    if require_complete:
        row_invalid = base.isna() | is_suppressed_or_missing
        x_val = np.where(is_valid_x, x_num, 0)
        total = np.where(~row_invalid, base + x_val, np.nan)
        return pd.Series(total, index=m_series.index)
    else:
        x_val = np.where(is_valid_x, x_num, 0)
        return base + x_val


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
