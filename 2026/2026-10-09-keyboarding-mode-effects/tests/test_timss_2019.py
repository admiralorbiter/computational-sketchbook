"""
Unit & Data Integrity Tests: TIMSS 2019 Grade 4 U.S. Mode Effects Empirical Study
Validates sample accounting, two-digit diagnostic scoring fidelity, omission recovery,
input modality classifications, within-school randomized comparisons, and econometric estimation.
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"


@pytest.fixture(scope="module")
def item_contrasts():
    path = PROCESSED_DIR / "timss_2019_g4_item_contrasts.parquet"
    assert path.exists(), f"Processed item contrasts missing at {path}"
    return pd.read_parquet(path)


@pytest.fixture(scope="module")
def student_pvs():
    path = PROCESSED_DIR / "timss_2019_g4_student_pvs.parquet"
    assert path.exists(), f"Processed student records missing at {path}"
    return pd.read_parquet(path)


@pytest.fixture(scope="module")
def student_item_stacked():
    path = PROCESSED_DIR / "timss_2019_g4_student_item_stacked.parquet"
    assert path.exists(), f"Processed stacked panel missing at {path}"
    return pd.read_parquet(path)


@pytest.fixture(scope="module")
def sample_accounting():
    path = TABLES_DIR / "table5_timss_2019_sample_accounting.csv"
    assert path.exists(), f"Table 5 missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def econometric_models():
    path = TABLES_DIR / "table10_timss_2019_econometric_models.csv"
    assert path.exists(), f"Table 10 missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def survey_inference_jk2():
    path = TABLES_DIR / "table11_timss_2019_survey_inference_jk2.csv"
    assert path.exists(), f"Table 11 missing at {path}"
    return pd.read_csv(path)


def test_timss_sample_accounting(student_pvs, sample_accounting):
    """Verify exact student, school, classroom, and study mode sample counts."""
    # 1. Total students
    assert len(student_pvs) == 10428
    
    # 2. Mode counts
    counts = student_pvs["study_mode"].value_counts()
    assert counts["Bridge_Paper"] == 1652
    assert counts["eTIMSS_Digital"] == 8776
    
    # 3. School counts
    sch_br = set(student_pvs[student_pvs["study_mode"] == "Bridge_Paper"]["IDSCHOOL"].unique())
    sch_e = set(student_pvs[student_pvs["study_mode"] == "eTIMSS_Digital"]["IDSCHOOL"].unique())
    assert len(sch_br) == 79
    assert len(sch_e) == 287
    assert student_pvs["IDSCHOOL"].nunique() == 294
    
    # 4. Overlapping 72 schools with randomized classrooms
    overlap = sch_br.intersection(sch_e)
    assert len(overlap) == 72
    
    sub_ov = student_pvs[student_pvs["IDSCHOOL"].isin(overlap)]
    assert len(sub_ov[sub_ov["study_mode"] == "Bridge_Paper"]) == 1456
    assert len(sub_ov[sub_ov["study_mode"] == "eTIMSS_Digital"]) == 1272


def test_stacked_student_item_panel_integrity(student_item_stacked):
    """Verify stacked student-by-item response panel dimensions and anchor coverage."""
    assert len(student_item_stacked) == 164653
    assert (student_item_stacked["is_digital"] == 0).sum() == 40759
    assert (student_item_stacked["is_digital"] == 1).sum() == 123894
    assert student_item_stacked["item_id"].nunique() == 99
    assert student_item_stacked["IDSCHOOL"].nunique() == 294


def test_two_digit_diagnostic_scoring_fidelity():
    """Verify that scoring correctly credits two-digit diagnostic codes (11-19, 20-29)."""
    from src.acquire_timss_2019 import score_response_series
    
    # 1-point CR item: codes 10-19 should all receive 1.0 point
    s_cr1 = pd.Series([10.0, 11.0, 12.0, 70.0, 79.0, 96.0, 99.0, np.nan])
    sc, adm, om, nr, val = score_response_series(s_cr1, "CR", 1, "None")
    np.testing.assert_array_equal(sc[:3], [1.0, 1.0, 1.0])
    np.testing.assert_array_equal(sc[3:7], [0.0, 0.0, 0.0, 0.0])
    assert adm[7] == False
    assert om[6] == True   # 99.0 is omit
    assert nr[5] == True   # 96.0 is not reached
    
    # 2-point CR item: codes 20-29 receive 1.0 (2/2), codes 10-19 receive 0.5 (1/2)
    s_cr2 = pd.Series([20.0, 21.0, 10.0, 11.0, 79.0, 99.0])
    sc2, _, _, _, _ = score_response_series(s_cr2, "CR", 2, "None")
    np.testing.assert_array_equal(sc2, [1.0, 1.0, 0.5, 0.5, 0.0, 0.0])


def test_iea_published_item_benchmarks(item_contrasts):
    """Validate that pipeline percent-correct matches official published IEA item tables."""
    # 1. 1-point CR item MP51043 matches published IEA table exactly
    row_51043 = item_contrasts[item_contrasts["item_id"] == "MP51043"].iloc[0]
    assert pytest.approx(49.93, abs=0.01) == row_51043["pct_paper"]
    assert pytest.approx(44.27, abs=0.01) == row_51043["pct_digital"]
    assert pytest.approx(-5.66, abs=0.01) == row_51043["diff_pp"]

    # 2. 1-point MC item MP51040 matches published IEA table
    row_51040 = item_contrasts[item_contrasts["item_id"] == "MP51040"].iloc[0]
    assert pytest.approx(88.53, abs=0.01) == row_51040["pct_paper"]
    assert pytest.approx(90.37, abs=0.01) == row_51040["pct_digital"]
    assert pytest.approx(1.84, abs=0.01) == row_51040["diff_pp"]

    # 3. 2-point CR item MP61228: verify partial credit calculation
    row_61228 = item_contrasts[item_contrasts["item_id"] == "MP61228"].iloc[0]
    # Published full credit is 29.63%; our partial-credit weighted score is 40.16%
    assert pytest.approx(40.16, abs=0.05) == row_61228["pct_paper"]
    assert pytest.approx(26.45, abs=0.05) == row_61228["pct_digital"]


def test_anchor_item_properties_and_omission_recovery(item_contrasts):
    """Verify that all 99 common items are present with non-zero recovered omissions."""
    assert len(item_contrasts) == 99
    
    type_counts = item_contrasts["item_type"].value_counts()
    assert type_counts["MC"] == 49
    assert type_counts["CR"] == 50
    
    # Check that omission rates are non-zero across the assessment
    mean_omit_paper = item_contrasts["omit_paper_pct"].mean()
    mean_omit_digital = item_contrasts["omit_digital_pct"].mean()
    assert mean_omit_paper > 2.0  # Paper average ~3.0%
    assert mean_omit_digital > 1.0 # Digital average ~1.3%
    
    # Check that input modalities are assigned
    mod_counts = item_contrasts["modality"].value_counts()
    assert mod_counts["Multiple Choice"] == 49
    assert mod_counts["CR: Drawing / Graphing"] == 10
    assert mod_counts["CR: Interactive / Table"] == 8
    assert mod_counts["CR: Number-pad / Numeric"] == 27
    assert mod_counts["CR: Text / Explanation"] == 5


def test_format_gap_and_econometric_estimation(item_contrasts, econometric_models):
    """Verify item format contrasts and 5 design-based econometric models."""
    mc_diffs = item_contrasts[item_contrasts["item_type"] == "MC"]["diff_pp"]
    cr_diffs = item_contrasts[item_contrasts["item_type"] == "CR"]["diff_pp"]
    
    mean_mc = mc_diffs.mean()
    mean_cr = cr_diffs.mean()
    format_gap = mean_cr - mean_mc
    
    # Audited numbers: MC ~ -0.47 pp, CR ~ -3.90 pp, format gap ~ -3.42 pp
    assert pytest.approx(-0.47, abs=0.1) == mean_mc
    assert pytest.approx(-3.90, abs=0.1) == mean_cr
    assert pytest.approx(-3.42, abs=0.1) == format_gap
    
    # Check Model 1: Survey-weighted Student DiD clustered by school
    m1 = econometric_models[econometric_models["model_specification"].str.contains("Model 1")].iloc[0]
    assert pytest.approx(-3.102, abs=0.05) == m1["coefficient_beta"]
    assert m1["p_value"] < 0.001
    
    # Check Model 2: National Item Fixed-Effects Panel WLS
    m2 = econometric_models[econometric_models["model_specification"].str.contains("Model 2")].iloc[0]
    assert pytest.approx(-3.422, abs=0.05) == m2["coefficient_beta"]
    assert m2["p_value"] < 0.0001
    
    # Check Model 3: Within-School Student DiD on 72 Overlapping Schools
    m3 = econometric_models[econometric_models["model_specification"].str.contains("Model 3")].iloc[0]
    assert pytest.approx(-2.364, abs=0.05) == m3["coefficient_beta"]
    assert m3["p_value"] < 0.01  # p = 0.0065
    
    # Check Model 4: Within-School Item FE + School FE Panel
    m4 = econometric_models[econometric_models["model_specification"].str.contains("Model 4")].iloc[0]
    assert pytest.approx(-2.734, abs=0.05) == m4["coefficient_beta"]
    assert m4["p_value"] < 0.01  # p = 0.00335
    
    # Check Model 5: SES Interaction Term
    m5 = econometric_models[econometric_models["model_specification"].str.contains("Model 5")].iloc[0]
    assert pytest.approx(-0.096, abs=0.05) == m5["coefficient_beta"]
    assert m5["p_value"] > 0.50  # p = 0.934 confirms null interaction
    assert pytest.approx(-2.35, abs=0.1) == m5["ci_95_lower"]
    assert pytest.approx(2.16, abs=0.1) == m5["ci_95_upper"]


def test_survey_jackknife_repeated_replication(survey_inference_jk2):
    """Verify design-based standard errors from TIMSS Jackknife Repeated Replication (JK2)."""
    did_row = survey_inference_jk2[survey_inference_jk2["parameter"].str.contains("Student Format Gap")].iloc[0]
    assert pytest.approx(-3.102, abs=0.05) == did_row["mode_difference"]
    assert pytest.approx(0.668, abs=0.05) == did_row["jk2_standard_error"]
    assert did_row["p_value"] < 0.001


def test_cognitive_reasoning_wedge(item_contrasts):
    """Verify that Reasoning MC is positive while Reasoning CR is severely negative."""
    reasoning_mc = item_contrasts[(item_contrasts["cognitive_domain"] == "Reasoning") & (item_contrasts["item_type"] == "MC")]["diff_pp"]
    reasoning_cr = item_contrasts[(item_contrasts["cognitive_domain"] == "Reasoning") & (item_contrasts["item_type"] == "CR")]["diff_pp"]
    
    assert len(reasoning_mc) == 8
    assert len(reasoning_cr) == 10
    
    # Reasoning MC is positive (digital is not harder when selecting answers)
    assert reasoning_mc.mean() > 0
    assert pytest.approx(2.61, abs=0.2) == reasoning_mc.mean()
    
    # Reasoning CR is large negative (digital is much harder when constructing answers)
    assert reasoning_cr.mean() < -7.0
    assert pytest.approx(-7.54, abs=0.2) == reasoning_cr.mean()
    
    # Reasoning format gap exceeds -10 percentage points
    reasoning_gap = reasoning_cr.mean() - reasoning_mc.mean()
    assert pytest.approx(-10.14, abs=0.2) == reasoning_gap


def test_student_level_subgroup_invariance(student_pvs, econometric_models):
    """Verify that student format gap mode difference is invariant across home SES with calibrated bounds."""
    # Compute format penalty dynamically for Low SES vs High SES
    low_ses_br = student_pvs[(student_pvs["study_mode"] == "Bridge_Paper") & (student_pvs["ASBG04"].isin([1.0, 2.0]))].dropna(subset=["format_gap", "TOTWGT"])
    low_ses_e = student_pvs[(student_pvs["study_mode"] == "eTIMSS_Digital") & (student_pvs["ASBG04"].isin([1.0, 2.0]))].dropna(subset=["format_gap", "TOTWGT"])
    
    gap_low_br = np.average(low_ses_br["format_gap"], weights=low_ses_br["TOTWGT"])
    gap_low_e = np.average(low_ses_e["format_gap"], weights=low_ses_e["TOTWGT"])
    penalty_low = gap_low_e - gap_low_br
    
    high_ses_br = student_pvs[(student_pvs["study_mode"] == "Bridge_Paper") & (student_pvs["ASBG04"].isin([3.0, 4.0, 5.0]))].dropna(subset=["format_gap", "TOTWGT"])
    high_ses_e = student_pvs[(student_pvs["study_mode"] == "eTIMSS_Digital") & (student_pvs["ASBG04"].isin([3.0, 4.0, 5.0]))].dropna(subset=["format_gap", "TOTWGT"])
    
    gap_high_br = np.average(high_ses_br["format_gap"], weights=high_ses_br["TOTWGT"])
    gap_high_e = np.average(high_ses_e["format_gap"], weights=high_ses_e["TOTWGT"])
    penalty_high = gap_high_e - gap_high_br
    
    # Both are approx -3.1 pp
    assert pytest.approx(-3.17, abs=0.2) == penalty_low
    assert pytest.approx(-3.07, abs=0.2) == penalty_high
    
    # Check Model 5 regression interaction p-value is non-significant
    m5 = econometric_models[econometric_models["model_specification"].str.contains("Model 5")].iloc[0]
    assert m5["p_value"] > 0.50  # p = 0.934 confirms null interaction
    # Confirm interpretation acknowledges precision bounds rather than asserting strict equivalence
    assert "not prove statistical equivalence" in m5["interpretation"] or "does not rule out" in m5["interpretation"]

