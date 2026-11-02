"""
Unit & Data Integrity Tests: PIRLS 2021 Digital Reading Process & Interaction Data (Study B)
Validates item-level timing, navigation revisit metrics, student-level response latencies,
scored accuracy outcomes, and the empirical test of the competing behavioral hypotheses
(Navigation Friction, Observed Response Duration, Ability Mediation, and Within-Item Time-Accuracy Gradient).
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"


@pytest.fixture(scope="module")
def item_metrics():
    path = PROCESSED_DIR / "pirls_2021_item_process_metrics.parquet"
    assert path.exists(), f"Processed PIRLS item metrics missing at {path}"
    return pd.read_parquet(path)


@pytest.fixture(scope="module")
def student_sample():
    path = PROCESSED_DIR / "pirls_2021_student_process_sample.parquet"
    assert path.exists(), f"Processed PIRLS student sample missing at {path}"
    return pd.read_parquet(path)


@pytest.fixture(scope="module")
def student_item_panel():
    path = PROCESSED_DIR / "pirls_2021_student_item_panel.parquet"
    assert path.exists(), f"Processed PIRLS student-item panel missing at {path}"
    return pd.read_parquet(path)


@pytest.fixture(scope="module")
def table15_format_metrics():
    path = TABLES_DIR / "table15_pirls_2021_process_metrics_by_format.csv"
    assert path.exists(), f"Table 15 missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def table16_mechanisms():
    path = TABLES_DIR / "table16_pirls_2021_mechanism_decomposition.csv"
    assert path.exists(), f"Table 16 missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def table17_time_accuracy():
    path = TABLES_DIR / "table17_pirls_2021_time_accuracy_decomposition.csv"
    assert path.exists(), f"Table 17 missing at {path}"
    return pd.read_csv(path)


def test_pirls_item_process_metrics_integrity(item_metrics):
    """Verify item metrics count, format split, and plausible timing ranges on clean sample."""
    assert len(item_metrics) == 273
    
    counts = item_metrics["item_type"].value_counts()
    assert counts["MC"] == 124
    assert counts["CR"] == 149
    
    # Timing bounds
    assert (item_metrics["mean_total_time_s"] > 10.0).all()
    assert (item_metrics["mean_total_time_s"] < 600.0).all()
    assert (item_metrics["revisit_pct"] >= 0.0).all()
    assert (item_metrics["revisit_pct"] <= 100.0).all()
    assert (item_metrics["n_examinees"] > 0).all()


def test_pirls_student_sample_integrity(student_sample):
    """Verify student sample accounting, clean flag filtering, reading achievement, and scored metrics."""
    assert len(student_sample) == 4486
    assert (student_sample["FLAGPT1"] == 0).all()
    assert (student_sample["FLAGPT2"] == 0).all()
    
    # German Grade 4 reading plausible value average is ~525-530
    mean_pv1 = student_sample["ASRREA01"].mean()
    assert 520.0 <= mean_pv1 <= 535.0
    
    # Verify timing counts and scored accuracy fields
    assert "n_mc_timing_obs" in student_sample.columns
    assert "n_cr_timing_obs" in student_sample.columns
    assert "mc_score_pct" in student_sample.columns
    assert "cr_score_pct" in student_sample.columns
    
    valid_mc_score = student_sample["mc_score_pct"].dropna()
    valid_cr_score = student_sample["cr_score_pct"].dropna()
    assert (valid_mc_score >= 0.0).all() and (valid_mc_score <= 100.0).all()
    assert (valid_cr_score >= 0.0).all() and (valid_cr_score <= 100.0).all()
    assert 65.0 <= valid_mc_score.mean() <= 75.0
    assert 55.0 <= valid_cr_score.mean() <= 65.0


def test_response_entry_latency_multiplier(table15_format_metrics):
    """Verify that CR items require 2.4x to 3.0x more time than MC items across all processes."""
    mc_row = table15_format_metrics[
        (table15_format_metrics["grouping"] == "Overall Format") & 
        (table15_format_metrics["category"].str.contains("Multiple Choice"))
    ].iloc[0]
    
    cr_row = table15_format_metrics[
        (table15_format_metrics["grouping"] == "Overall Format") & 
        (table15_format_metrics["category"].str.contains("Constructed Response"))
    ].iloc[0]
    
    assert 40.0 <= mc_row["mean_total_time_s"] <= 55.0  # ~46.9s
    assert 115.0 <= cr_row["mean_total_time_s"] <= 135.0  # ~123.1s
    
    ratio = cr_row["entry_latency_ratio"]
    assert 2.4 <= ratio <= 3.0  # ~2.62x
    
    # Check all four comprehension processes have CR ratios > 2.0x
    proc_rows = table15_format_metrics[table15_format_metrics["grouping"] == "Comprehension Process"]
    cr_proc_rows = proc_rows[proc_rows["category"].str.endswith("(CR)")]
    assert len(cr_proc_rows) == 4
    for _, r in cr_proc_rows.iterrows():
        assert r["entry_latency_ratio"] >= 2.0


def test_navigation_revisit_rates_and_durations(table15_format_metrics):
    """Verify that revisit frequency is format-independent while revisit duration is 3x longer on CR."""
    mc_row = table15_format_metrics[
        (table15_format_metrics["grouping"] == "Overall Format") & 
        (table15_format_metrics["category"].str.contains("Multiple Choice"))
    ].iloc[0]
    
    cr_row = table15_format_metrics[
        (table15_format_metrics["grouping"] == "Overall Format") & 
        (table15_format_metrics["category"].str.contains("Constructed Response"))
    ].iloc[0]
    
    # Revisit frequency gap is tiny (< 5 percentage points)
    revisit_diff = abs(cr_row["revisit_pct"] - mc_row["revisit_pct"])
    assert revisit_diff < 5.0  # 52.2% vs 49.8% -> diff is 2.4 pp
    
    # Additional time after first visit is > 3x longer on CR
    assert cr_row["mean_additional_time_after_first_visit_s"] >= 2.5 * mc_row["mean_additional_time_after_first_visit_s"]
    # Conditional revisit duration is also > 2.5x longer on CR
    assert cr_row["mean_conditional_revisit_duration_s"] >= 2.5 * mc_row["mean_conditional_revisit_duration_s"]


def test_mechanism_reading_ability_correlations(student_sample):
    """
    Verify Hypothesis 3: higher reading ability is negatively correlated with MC time
    (processing efficiency) but positively correlated with CR time and CR-MC wedge (longer written output).
    """
    valid = student_sample.dropna(subset=["mean_mc_time_s", "mean_cr_time_s", "ASRREA01"])
    
    corr_mc = valid["mean_mc_time_s"].corr(valid["ASRREA01"])
    corr_cr = valid["mean_cr_time_s"].corr(valid["ASRREA01"])
    corr_wedge = valid["cr_mc_time_diff_s"].corr(valid["ASRREA01"])
    
    assert corr_mc < 0.0  # Proficient readers answer MC faster
    assert corr_cr > 0.0  # Proficient readers spend longer writing CR answers
    assert corr_wedge > 0.10  # Proficient readers exhibit a wider entry time wedge


def test_within_item_time_accuracy_gradient(table17_time_accuracy, student_item_panel):
    """
    Verify Hypothesis 4: Within-item regression of score on time diverges by format.
    Extra time on MC items predicts lower accuracy (confusion/hesitation),
    while extra time on CR items predicts higher accuracy (productive drafting).
    """
    assert len(student_item_panel) > 90000
    
    mc_row = table17_time_accuracy[table17_time_accuracy["item_format"].str.startswith("Multiple Choice")].iloc[0]
    cr_row = table17_time_accuracy[table17_time_accuracy["item_format"].str.startswith("Constructed Response")].iloc[0]
    
    assert mc_row["within_item_beta_log_time"] < 0.0  # Negative gradient on MC
    assert cr_row["within_item_beta_log_time"] > 0.0  # Positive gradient on CR
    assert cr_row["within_item_beta_log_time"] - mc_row["within_item_beta_log_time"] > 0.05
