"""
Pytest Suite: Auditable Replication & Source Code Accounting Tests
for Missouri CRDC Opportunity Measurement Studies (2021-22).

Validates:
1. Exact population funnel counts (318 -> 317 -> 307 + 10 sensitivity schools).
2. Proper treatment of CRDC source codes (-9 skipped, -12 suppressed) to prevent subtraction artifacts.
3. Study 1: Dual enrollment rate among non-AP schools (92.9%) vs miss rate among either route (35.1%).
4. Study 2: Reported AP Computer Science participation concealment (65.5% no AP CS among AP schools).
5. Study 3: Recomputed provisional released enrollment (228,637 total; 41,616 zero-physics; 18.20% student; 14.70 pp divergence).
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PROCESSED = PROJECT_DIR / "data" / "processed"
DATA_RAW = PROJECT_DIR / "data" / "raw"


@pytest.fixture(scope="module")
def panel():
    parquet_path = DATA_PROCESSED / "mo_high_school_crdc_measurement_panel_2021_22.parquet"
    assert parquet_path.exists(), f"Missing panel: {parquet_path}"
    return pd.read_parquet(parquet_path)


@pytest.fixture(scope="module")
def raw_enr():
    enr_path = DATA_RAW / "mo_crdc_enrollment_2021_22.csv"
    assert enr_path.exists(), f"Missing raw enrollment extract: {enr_path}"
    df = pd.read_csv(enr_path, low_memory=False)
    df["ncessch"] = df["ncessch"].astype(str).str.zfill(12)
    return df


def test_population_funnel_counts(panel):
    """Verify the exact filtering funnel: 318 -> 317 -> 307 + 10 sensitivity schools."""
    # 1. Total rows in panel = initial 318
    assert len(panel) == 318

    # 2. Matched to CRDC = 317
    matched = panel[panel["flag_matched_crdc"]]
    assert len(matched) == 317

    # 3. Exactly 1 unmatched school (Hawthorn High School in KCPS boundaries)
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


def test_source_code_handling_and_suppression(panel, raw_enr):
    """
    Validate that negative CRDC source codes are audited rather than subtracted:
    - -9 indicates Not Applicable / Skipped (nonbinary not collected/reported).
    - -12 indicates Data Suppressed for Privacy Protection.
    - Released enrollment must sum only nonnegative released components.
    """
    df_307 = panel[panel["flag_consistent_9_12"]].copy()
    m_enr = df_307.merge(raw_enr, on="ncessch", how="inner")

    # Check nonbinary raw field distribution
    tot_x_raw = pd.to_numeric(m_enr["TOT_ENR_X"], errors="coerce")
    n_skipped = (tot_x_raw == -9).sum()
    n_suppressed = (tot_x_raw == -12).sum()

    assert n_skipped == 304, f"Expected 304 schools with -9 in TOT_ENR_X, got {n_skipped}"
    assert n_suppressed == 1, f"Expected exactly 1 school with -12 in TOT_ENR_X, got {n_suppressed}"

    # Verify which school has suppression
    suppressed_school = m_enr[tot_x_raw == -12].iloc[0]
    assert "CENTRAL HIGH" in suppressed_school["school_name"]

    # Assert flag in master panel
    assert df_307["flag_enr_suppressed"].sum() == 1
    assert df_307["flag_enr_x_skipped"].sum() == 304

    # Ensure no negative values exist in released enrollment
    assert (df_307["crdc_released_enrollment"] < 0).sum() == 0
    assert df_307["crdc_released_enrollment"].min() > 0


def test_study_1_ap_dual_contingency_and_miss_rate(panel):
    """
    Study 1 Replication:
    - 307 schools: 113 No AP, 194 Yes AP
    - Metric A (among No AP, N=113): 105 Yes Dual -> 105/113 = 92.920% (~92.9%)
    - Metric B (miss rate among either route, N=299): 105 / 299 = 35.117% (~35.1%)
    - Neither route: 8 schools (2.61%)
    """
    df_307 = panel[panel["flag_consistent_9_12"]]
    no_ap_307 = df_307[df_307["ap_indicator_raw"] == "No"]
    assert len(no_ap_307) == 113

    dual_in_no_ap_307 = (no_ap_307["dual_indicator_raw"] == "Yes").sum()
    neither_307 = (no_ap_307["dual_indicator_raw"] == "No").sum()
    assert dual_in_no_ap_307 == 105
    assert neither_307 == 8

    # Metric A
    rate_a = dual_in_no_ap_307 / len(no_ap_307) * 100
    assert pytest.approx(rate_a, 0.001) == 92.920

    # Metric B (Miss rate among either route)
    either_route_307 = df_307[(df_307["ap_participating"]) | (df_307["dual_participating"])]
    assert len(either_route_307) == 299
    rate_b = dual_in_no_ap_307 / len(either_route_307) * 100
    assert pytest.approx(rate_b, 0.001) == 35.117

    # Sensitivity (317 schools)
    df_317 = panel[panel["flag_matched_crdc"]]
    no_ap_317 = df_317[df_317["ap_indicator_raw"] == "No"]
    assert len(no_ap_317) == 116
    dual_in_no_ap_317 = (no_ap_317["dual_indicator_raw"] == "Yes").sum()
    assert dual_in_no_ap_317 == 108

    rate_a_317 = dual_in_no_ap_317 / len(no_ap_317) * 100
    assert pytest.approx(rate_a_317, 0.001) == 93.103

    either_route_317 = df_317[(df_317["ap_participating"]) | (df_317["dual_participating"])]
    assert len(either_route_317) == 309
    rate_b_317 = dual_in_no_ap_317 / len(either_route_317) * 100
    assert pytest.approx(rate_b_317, 0.001) == 34.951


def test_study_2_ap_cs_reported_participation(panel):
    """
    Study 2 Replication:
    - 307 sample: 194 AP-participating schools
    - No AP CS reported participation: 127 (65.46%)
    - Yes AP CS reported participation: 67 (34.54%)
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


def test_study_3_physics_recomputed_released_enrollment(panel):
    """
    Study 3 Replication with Recomputed Released Enrollment:
    - 307 sample: 101 schools report 0 physics classes (32.90%)
    - Total released enrollment across 307 schools = 228,637 (provisional, holding 1 suppressed unresolved)
    - Released enrollment at zero-physics schools = 41,616
    - Student-weighted percentage = 41,616 / 228,637 = 18.2018% (~18.20%)
    - Denominator divergence = 32.8990% - 18.2018% = 14.6972 pp (~14.70 pp)
    """
    df_307 = panel[panel["flag_consistent_9_12"]]
    zero_phys = df_307["physics_classes"] == 0
    n_zero_schools = zero_phys.sum()
    assert n_zero_schools == 101

    school_pct = n_zero_schools / len(df_307) * 100
    assert pytest.approx(school_pct, 0.01) == 32.90

    rel_enr_total = df_307["crdc_released_enrollment"].sum()
    rel_enr_zero = df_307.loc[zero_phys, "crdc_released_enrollment"].sum()

    assert rel_enr_total == 228637.0, f"Expected 228,637, got {rel_enr_total}"
    assert rel_enr_zero == 41616.0, f"Expected 41,616, got {rel_enr_zero}"

    student_pct = rel_enr_zero / rel_enr_total * 100
    assert pytest.approx(student_pct, 0.001) == 18.202

    wedge = school_pct - student_pct
    assert pytest.approx(wedge, 0.001) == 14.697

    # Broad sensitivity (317 schools)
    df_317 = panel[panel["flag_matched_crdc"]]
    zero_phys_317 = df_317["physics_classes"] == 0
    assert zero_phys_317.sum() == 105

    school_pct_317 = zero_phys_317.mean() * 100
    assert pytest.approx(school_pct_317, 0.01) == 33.12

    rel_enr_total_317 = df_317["crdc_released_enrollment"].sum()
    rel_enr_zero_317 = df_317.loc[zero_phys_317, "crdc_released_enrollment"].sum()

    assert rel_enr_total_317 == 237945.0
    assert rel_enr_zero_317 == 42481.0

    student_pct_317 = rel_enr_zero_317 / rel_enr_total_317 * 100
    assert pytest.approx(student_pct_317, 0.001) == 17.853

    wedge_317 = school_pct_317 - student_pct_317
    assert pytest.approx(wedge_317, 0.001) == 15.270


def test_course_counts_preserve_unknowns_and_assert_valid_cohort(panel):
    """
    Validate that missing/administrative course counts are preserved as NaN:
    - Never silently fillna(0) unknowns into apparent absence of courses.
    - Assert that all schools in the analyzed cohorts (307 and 317) have verified, non-null, nonnegative counts.
    - Assert that unmatched schools (Hawthorn) have NaN rather than 0 for course counts.
    """
    df_307 = panel[panel["flag_consistent_9_12"]]
    df_317 = panel[panel["flag_matched_crdc"]]
    unmatched = panel[~panel["flag_matched_crdc"]]

    # 1. Analyzed cohorts must have strictly non-null, valid nonnegative counts
    assert df_307["physics_classes"].notna().all(), "Strict cohort contains missing physics counts!"
    assert (df_307["physics_classes"] >= 0).all(), "Strict cohort contains negative physics counts!"
    assert df_307["general_cs_classes"].notna().all(), "Strict cohort contains missing CS counts!"
    assert (df_307["general_cs_classes"] >= 0).all(), "Strict cohort contains negative CS counts!"

    assert df_317["physics_classes"].notna().all(), "Sensitivity cohort contains missing physics counts!"
    assert (df_317["physics_classes"] >= 0).all(), "Sensitivity cohort contains negative physics counts!"
    assert df_317["general_cs_classes"].notna().all(), "Sensitivity cohort contains missing CS counts!"
    assert (df_317["general_cs_classes"] >= 0).all(), "Sensitivity cohort contains negative CS counts!"

    # 2. Unmatched school must have NaN, NOT 0.0 or False
    assert len(unmatched) == 1
    assert pd.isna(unmatched.iloc[0]["physics_classes"]), "Unmatched school physics count was converted to 0 instead of NaN!"
    assert pd.isna(unmatched.iloc[0]["general_cs_classes"]), "Unmatched school general CS count was converted to 0 instead of NaN!"
    assert pd.isna(unmatched.iloc[0]["has_physics_classes"]), "Unmatched school has_physics_classes was converted to False instead of NA/NaN!"

