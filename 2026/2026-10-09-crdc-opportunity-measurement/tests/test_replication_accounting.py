"""
Pytest Suite: Auditable Replication & Accounting Tests
for Missouri CRDC Opportunity Measurement Studies (2021-22).
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PROCESSED = PROJECT_DIR / "data" / "processed"


@pytest.fixture(scope="module")
def panel():
    parquet_path = DATA_PROCESSED / "mo_high_school_crdc_measurement_panel_2021_22.parquet"
    assert parquet_path.exists(), f"Missing panel: {parquet_path}"
    return pd.read_parquet(parquet_path)


def test_population_funnel_counts(panel):
    """Verify the exact filtering funnel: 318 -> 317 -> 307 + 10 sensitivity schools."""
    # 1. Total rows in panel = initial 318
    assert len(panel) == 318

    # 2. Matched to CRDC = 317
    matched = panel[panel["flag_matched_crdc"]]
    assert len(matched) == 317

    # 3. Exactly 1 unmatched school
    unmatched = panel[~panel["flag_matched_crdc"]]
    assert len(unmatched) == 1
    assert "Hawthorn" in unmatched.iloc[0]["school_name"]

    # 4. Consistent 9-12 reporting = 307
    consistent = panel[panel["flag_consistent_9_12"]]
    assert len(consistent) == 307

    # 5. Conflicting grade-span records = 10
    conflicting = panel[panel["flag_conflicting_span"]]
    assert len(conflicting) == 10
    assert len(consistent) + len(conflicting) == 317


def test_study_1_ap_dual_contingency(panel):
    """
    Study 1 Replication:
    - 307 schools: 113 No AP, 194 Yes AP
    - Among 113 No-AP: 105 Yes Dual, 8 No Dual -> 105/113 = 92.920% (~92.9%)
    - Sensitivity (317 schools): 116 No AP, 201 Yes AP
    - Among 116 No-AP: 108 Yes Dual, 8 No Dual -> 108/116 = 93.103% (~93.1%)
    """
    df_307 = panel[panel["flag_consistent_9_12"]]
    no_ap_307 = df_307[df_307["ap_indicator_raw"] == "No"]
    assert len(no_ap_307) == 113

    dual_in_no_ap_307 = (no_ap_307["dual_indicator_raw"] == "Yes").sum()
    neither_307 = (no_ap_307["dual_indicator_raw"] == "No").sum()
    assert dual_in_no_ap_307 == 105
    assert neither_307 == 8

    pct_307 = dual_in_no_ap_307 / len(no_ap_307) * 100
    assert round(pct_307, 1) == 92.9
    assert pytest.approx(pct_307, 0.001) == 92.920

    # Sensitivity
    df_317 = panel[panel["flag_matched_crdc"]]
    no_ap_317 = df_317[df_317["ap_indicator_raw"] == "No"]
    assert len(no_ap_317) == 116

    dual_in_no_ap_317 = (no_ap_317["dual_indicator_raw"] == "Yes").sum()
    assert dual_in_no_ap_317 == 108

    pct_317 = dual_in_no_ap_317 / len(no_ap_317) * 100
    assert round(pct_317, 1) == 93.1
    assert pytest.approx(pct_317, 0.001) == 93.103


def test_study_2_ap_cs_concealment(panel):
    """
    Study 2 Replication:
    - 307 sample: 194 AP-participating schools
    - No AP CS: 127 (65.46%)
    - Yes AP CS: 67 (34.54%)
    """
    df_307 = panel[panel["flag_consistent_9_12"]]
    ap_schools = df_307[df_307["ap_participating"]]
    assert len(ap_schools) == 194

    no_cs = (ap_schools["ap_cs_indicator_raw"] == "No").sum()
    yes_cs = (ap_schools["ap_cs_indicator_raw"] == "Yes").sum()
    assert no_cs == 127
    assert yes_cs == 67
    assert no_cs + yes_cs == 194

    pct_no_cs = no_cs / len(ap_schools) * 100
    assert pytest.approx(pct_no_cs, 0.01) == 65.46


def test_study_3_physics_denominator_wedge(panel):
    """
    Study 3 Replication:
    - 307 sample: 101 schools report 0 physics classes (32.90%)
    - Total students = 225,889
    - Students in zero-physics schools = 40,707 (18.02%)
    - Denominator wedge = 32.90% - 18.02% = 14.88 percentage points
    """
    df_307 = panel[panel["flag_consistent_9_12"]]
    zero_phys = df_307["physics_classes"] == 0
    n_zero_schools = zero_phys.sum()
    assert n_zero_schools == 101

    school_pct = n_zero_schools / len(df_307) * 100
    assert pytest.approx(school_pct, 0.01) == 32.90

    total_enr = df_307["crdc_total_enrollment"].sum()
    zero_enr = df_307.loc[zero_phys, "crdc_total_enrollment"].sum()
    assert total_enr == 225889
    assert zero_enr == 40707

    student_pct = zero_enr / total_enr * 100
    assert pytest.approx(student_pct, 0.01) == 18.02

    wedge = school_pct - student_pct
    assert pytest.approx(wedge, 0.01) == 14.88
