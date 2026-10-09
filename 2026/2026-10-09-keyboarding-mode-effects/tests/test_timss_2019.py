"""
Unit & Data Integrity Tests: TIMSS 2019 Grade 4 U.S. Mode Effects Empirical Study
Validates sample accounting, anchor item matching, format gaps, and psychometric bounds.
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
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
def sample_accounting():
    path = TABLES_DIR / "table5_timss_2019_sample_accounting.csv"
    assert path.exists(), f"Table 5 missing at {path}"
    return pd.read_csv(path)


def test_timss_sample_accounting(student_pvs, sample_accounting):
    """Verify exact student, school, and study mode sample counts."""
    # 1. Total students
    assert len(student_pvs) == 10428
    
    # 2. Mode counts
    counts = student_pvs["study_mode"].value_counts()
    assert counts["Bridge_Paper"] == 1652
    assert counts["eTIMSS_Digital"] == 8776
    
    # 3. School counts
    sch_br = student_pvs[student_pvs["study_mode"] == "Bridge_Paper"]["IDSCHOOL"].nunique()
    sch_e = student_pvs[student_pvs["study_mode"] == "eTIMSS_Digital"]["IDSCHOOL"].nunique()
    assert sch_br == 79
    assert sch_e == 287
    assert student_pvs["IDSCHOOL"].nunique() == 294
    
    # 4. Check Table 5 fidelity
    br_row = sample_accounting[sample_accounting["sample_group"].str.contains("Bridge")].iloc[0]
    assert br_row["students"] == 1652
    assert br_row["schools"] == 79
    e_row = sample_accounting[sample_accounting["sample_group"].str.contains("eTIMSS")].iloc[0]
    assert e_row["students"] == 8776
    assert e_row["schools"] == 287


def test_anchor_item_properties(item_contrasts):
    """Verify that all 99 common items are present with valid scores and classifications."""
    assert len(item_contrasts) == 99
    
    # Check item type counts
    type_counts = item_contrasts["item_type"].value_counts()
    assert type_counts["MC"] == 49
    assert type_counts["CR"] == 50
    
    # Check percentages are within valid [0, 100] bounds
    assert (item_contrasts["pct_paper"] >= 0).all() and (item_contrasts["pct_paper"] <= 100).all()
    assert (item_contrasts["pct_digital"] >= 0).all() and (item_contrasts["pct_digital"] <= 100).all()
    
    # Check difference identity: diff_pp == pct_digital - pct_paper (within rounding 0.02)
    diff_check = (item_contrasts["pct_digital"] - item_contrasts["pct_paper"]).round(2)
    assert np.allclose(item_contrasts["diff_pp"], diff_check, atol=0.03)


def test_format_gap_and_directionality(item_contrasts):
    """Verify that Constructed Response items experience a larger negative mode difference."""
    mc_diffs = item_contrasts[item_contrasts["item_type"] == "MC"]["diff_pp"]
    cr_diffs = item_contrasts[item_contrasts["item_type"] == "CR"]["diff_pp"]
    
    mean_mc = mc_diffs.mean()
    mean_cr = cr_diffs.mean()
    format_gap = mean_cr - mean_mc
    
    # Both are negative
    assert mean_mc < 0
    assert mean_cr < 0
    
    # CR penalty is more negative
    assert mean_cr < mean_mc
    
    # Audited numbers: MC ~ -2.17 pp, CR ~ -4.65 pp, format gap ~ -2.48 pp
    assert pytest.approx(-2.17, abs=0.1) == mean_mc
    assert pytest.approx(-4.65, abs=0.1) == mean_cr
    assert pytest.approx(-2.48, abs=0.1) == format_gap


def test_cognitive_reasoning_wedge(item_contrasts):
    """Verify the striking finding: Reasoning MC is positive while Reasoning CR is severely negative."""
    reasoning_mc = item_contrasts[(item_contrasts["cognitive_domain"] == "Reasoning") & (item_contrasts["item_type"] == "MC")]["diff_pp"]
    reasoning_cr = item_contrasts[(item_contrasts["cognitive_domain"] == "Reasoning") & (item_contrasts["item_type"] == "CR")]["diff_pp"]
    
    assert len(reasoning_mc) == 8
    assert len(reasoning_cr) == 10
    
    # Reasoning MC is positive or zero (digital is not harder when selecting answers)
    assert reasoning_mc.mean() > 0
    assert pytest.approx(1.27, abs=0.2) == reasoning_mc.mean()
    
    # Reasoning CR is large negative (digital is much harder when constructing answers)
    assert reasoning_cr.mean() < -7.0
    assert pytest.approx(-8.17, abs=0.2) == reasoning_cr.mean()
    
    # Reasoning format gap exceeds -9 percentage points
    reasoning_gap = reasoning_cr.mean() - reasoning_mc.mean()
    assert reasoning_gap < -9.0


def test_subgroup_invariance_counterargument(student_pvs):
    """Test the 2018 TIMSS finding: format gap does not compound heavily across student SES."""
    # Low SES (Books 1-2) vs High SES (Books 3-5)
    # Check that both groups have substantial sample sizes in both paper and digital
    low_ses = student_pvs[student_pvs["ASBG04"].isin([1.0, 2.0])]
    high_ses = student_pvs[student_pvs["ASBG04"].isin([3.0, 4.0, 5.0])]
    
    assert len(low_ses[low_ses["study_mode"] == "Bridge_Paper"]) > 500
    assert len(low_ses[low_ses["study_mode"] == "eTIMSS_Digital"]) > 3000
    assert len(high_ses[high_ses["study_mode"] == "Bridge_Paper"]) > 900
    assert len(high_ses[high_ses["study_mode"] == "eTIMSS_Digital"]) > 4000
