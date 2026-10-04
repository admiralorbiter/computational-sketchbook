"""
Unit and Integration Tests for School Context & Instructional Load Panel (Phase 4).
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"
PARQUET_PATH = DATA_DIR / "school_context_panel.parquet"
COURSE_PARQUET_PATH = DATA_DIR / "crdc_course_panel.parquet"


@pytest.fixture(scope="module")
def context_df():
    assert PARQUET_PATH.exists(), f"Missing processed file: {PARQUET_PATH}"
    return pd.read_parquet(PARQUET_PATH)


@pytest.fixture(scope="module")
def course_df():
    assert COURSE_PARQUET_PATH.exists(), f"Missing processed file: {COURSE_PARQUET_PATH}"
    return pd.read_parquet(COURSE_PARQUET_PATH)


def test_required_columns(context_df):
    """Verify presence of core uncollapsed context and linkage columns."""
    required = [
        "nces_school_id", "crdc_wave", "school_year", "state",
        "school_enrollment", "idea_count", "pct_idea",
        "sec504_count", "pct_sec504", "el_count", "pct_el",
        "chronic_absent_count", "pct_chronic_absent",
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
    
    # Each wave must have >= 90k schools
    counts = context_df.groupby("crdc_wave")["nces_school_id"].count()
    for w, c in counts.items():
        assert c >= 90000, f"Wave {w} has unusually low school count: {c}"


def test_percentage_ranges(context_df):
    """All percentage shares must fall within [0, 100] where valid."""
    for col in ["pct_idea", "pct_sec504", "pct_el", "pct_chronic_absent"]:
        valid = context_df[col].dropna()
        assert (valid >= 0).all(), f"Negative values found in {col}"
        assert (valid <= 100).all(), f"Values >100 found in {col}"


def test_class_size_linkage_integrity(context_df, course_df):
    """Verify exact match of linked schools between course panel and context panel."""
    course_schools_by_wave = course_df.groupby("crdc_wave")["nces_school_id"].nunique()
    context_linked_by_wave = context_df[context_df["in_class_size_panel"]].groupby("crdc_wave")["nces_school_id"].nunique()
    
    for w in course_schools_by_wave.index:
        c_count = course_schools_by_wave[w]
        ctx_count = context_linked_by_wave.get(w, 0)
        assert c_count == ctx_count, f"Wave {w} school count mismatch: course={c_count}, context={ctx_count}"


def test_longitudinal_dimension_shifts(context_df):
    """Verify known empirical shifts across waves (e.g. 504 expansion and chronic absenteeism jump)."""
    sec = context_df[context_df["in_class_size_panel"]]
    
    # 504 more than doubles from 2013-14 to 2021-22
    m504_13 = sec[sec["crdc_wave"] == "2013-14"]["pct_sec504"].mean()
    m504_21 = sec[sec["crdc_wave"] == "2021-22"]["pct_sec504"].mean()
    assert m504_21 > 2.0 * m504_13, f"Expected 504 to more than double: {m504_13:.2f}% to {m504_21:.2f}%"
    
    # Chronic absenteeism median jumps substantially post-COVID
    abs_med_13 = sec[sec["crdc_wave"] == "2013-14"]["pct_chronic_absent"].median()
    abs_med_21 = sec[sec["crdc_wave"] == "2021-22"]["pct_chronic_absent"].median()
    assert abs_med_21 > 1.8 * abs_med_13, f"Expected chronic absenteeism to surge: {abs_med_13:.1f}% to {abs_med_21:.1f}%"
