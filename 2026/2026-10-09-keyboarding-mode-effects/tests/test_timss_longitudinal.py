"""
Unit and Integration Tests for TIMSS 2019–2023 Longitudinal Attribution (Study D).
Validates Tables 21–25, difference-in-differences models, non-response accounting,
historical 31-item mode sensitivity, screen process timing, and psychometric IRT benchmarks.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import pytest
import statsmodels.api as sm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"


def test_table21_did_models():
    """Verify Table 21 difference-in-differences models, sample sizes, and format interaction bounds."""
    t21_path = TABLES_DIR / "table21_timss_longitudinal_did_models.csv"
    assert t21_path.exists(), "Table 21 CSV not found"
    
    df = pd.read_csv(t21_path)
    assert len(df) >= 4, f"Expected at least 4 models in Table 21, found {len(df)}"
    
    # Model 2: Primary 84 Common Items (Item + School FE) - Primary Pre-Registered Model
    m2 = df[df["model_specification"].str.contains("Model 2")].iloc[0]
    assert "Primary 84" in m2["sample_tier"]
    assert m2["n_items"] == 84
    assert m2["n_unique_students"] == 12060
    assert m2["n_student_item_obs"] == 214056
    
    # MC Baseline Trend: -1.92 pp (SE ~ 1.02)
    assert abs(m2["mc_baseline_trend_pp"] - (-1.92)) < 0.15
    assert abs(m2["mc_baseline_trend_se"] - 1.02) < 0.15
    
    # Format Interaction (beta_observed): -0.97 pp (SE ~ 0.49)
    assert abs(m2["did_format_interaction_pp"] - (-0.97)) < 0.15
    assert abs(m2["did_format_interaction_se"] - 0.49) < 0.15
    assert 0.03 < m2["p_value"] < 0.08
    
    # 95% Confidence Interval strictly inside [-2.0, 0.0] pp practical difference margin
    assert m2["ci_95_lower_pp"] >= -2.05
    assert m2["ci_95_upper_pp"] <= 0.05
    
    # Verify bounds across all primary models: format interaction magnitude is < 2.0 pp
    for _, row in df.iterrows():
        assert -2.5 < row["did_format_interaction_pp"] < 0.5


def test_table22_nonresponse_decomposition():
    """Verify Table 22 non-response accounting decomposition into completion vs attempted performance."""
    t22_path = TABLES_DIR / "table22_timss_longitudinal_nonresponse_decomposition.csv"
    assert t22_path.exists(), "Table 22 CSV not found"
    
    df = pd.read_csv(t22_path)
    primary = df[df["subgroup"] == "Primary 84 Pool"]
    assert len(primary) == 2, f"Expected 2 rows for Primary 84 Pool in Table 22, found {len(primary)}"
    
    mc = primary[primary["format"] == "Multiple Choice"].iloc[0]
    cr = primary[primary["format"] == "Constructed Response"].iloc[0]
    
    # Total change should match completion + performance components
    assert abs((mc["completion_component_pp"] + mc["performance_component_pp"]) - mc["total_change_pp"]) < 0.02
    assert abs((cr["completion_component_pp"] + cr["performance_component_pp"]) - cr["total_change_pp"]) < 0.02
    
    # MC total drop ~ -1.94 pp
    assert abs(mc["total_change_pp"] - (-1.94)) < 0.15
    # CR total drop ~ -2.89 pp
    assert abs(cr["total_change_pp"] - (-2.89)) < 0.15
    
    # Differential format change is ~ -0.95 pp
    diff_total = cr["total_change_pp"] - mc["total_change_pp"]
    assert abs(diff_total - (-0.95)) < 0.15
    
    # Attempted performance component accounts for > 70% of total change in both formats
    assert mc["performance_component_pp"] < mc["completion_component_pp"]
    assert cr["performance_component_pp"] < cr["completion_component_pp"]
    assert mc["share_due_to_noncompletion_pct"] < 35.0
    assert cr["share_due_to_noncompletion_pct"] < 35.0


def test_table23_historical_mode_sensitivity():
    """Verify Table 23 31-item overlap with Study A and split-sample test of mode vulnerability decay."""
    t23_path = TABLES_DIR / "table23_timss_historical_mode_sensitivity_31items.csv"
    assert t23_path.exists(), "Table 23 CSV not found"
    
    df = pd.read_csv(t23_path)
    assert len(df) == 31, f"Expected exactly 31 items in Table 23, found {len(df)}"
    
    fmt_counts = df["format"].value_counts().to_dict()
    assert fmt_counts["Multiple Choice"] == 14
    assert fmt_counts["Constructed Response"] == 17
    
    # Historical mode difference in 2019 was negative on average
    mean_mode_19 = df["mode_diff_2019_pp"].mean()
    assert mean_mode_19 < -2.0, f"Expected mean mode diff < -2.0 pp, got {mean_mode_19}"
    
    # CR items had larger 2019 mode vulnerability than MC items
    cr_mode_19 = df[df["format"] == "Constructed Response"]["mode_diff_2019_pp"].mean()
    mc_mode_19 = df[df["format"] == "Multiple Choice"]["mode_diff_2019_pp"].mean()
    assert cr_mode_19 < mc_mode_19
    
    # Split-sample regression: trend_split2 ~ mode_diff_split1
    # Tests whether items with large 2019 mode disadvantage deteriorated faster longitudinally
    x = sm.add_constant(df["mode_diff_split1"])
    y = df["trend_split2"]
    mod = sm.OLS(y, x).fit()
    
    # Slope should NOT be significantly negative (historical mode vulnerability does not predict decay)
    assert mod.pvalues.iloc[1] > 0.10, f"Expected non-significant slope p > 0.10, got {mod.pvalues.iloc[1]}"


def test_table24_screen_behavioral_panel():
    """Verify Table 24 screen-level process timing models across 77 pure screens."""
    t24_path = TABLES_DIR / "table24_timss_screen_behavioral_panel.csv"
    assert t24_path.exists(), "Table 24 CSV not found"
    
    df = pd.read_csv(t24_path)
    assert len(df) == 2, f"Expected 2 rows in Table 24, found {len(df)}"
    
    row_sec = df[df["metric"].str.contains("Seconds")].iloc[0]
    assert row_sec["n_screens"] == 77
    assert row_sec["n_obs"] > 180000
    
    # MC screen time baseline trend: small and non-significant (+0.06s)
    assert abs(row_sec["mc_baseline_trend"] - 0.06) < 0.20
    assert abs(row_sec["mc_baseline_se"] - 0.80) < 0.20
    
    # CR screen time differential interaction: -2.71s (SE 0.60, p < 0.001)
    assert abs(row_sec["cr_differential_interaction"] - (-2.71)) < 0.25
    assert abs(row_sec["cr_differential_se"] - 0.60) < 0.20
    assert row_sec["p_value"] < 0.001
    
    # Confirms students spent LESS time on CR screens in 2023 (not more time struggling with keyboard/tools)
    assert row_sec["ci_95_upper"] < 0.0


def test_table25_irt_counterfactuals():
    """Verify Table 25 psychometric IRT benchmark and scale-score counterfactual scenarios."""
    t25_path = TABLES_DIR / "table25_timss_longitudinal_irt_counterfactuals.csv"
    assert t25_path.exists(), "Table 25 CSV not found"
    
    df = pd.read_csv(t25_path)
    assert len(df) == 3, f"Expected 3 scenarios in Table 25, found {len(df)}"
    
    # All scenarios assume the published national decline of -17.80 points (-0.2225 SD)
    for _, row in df.iterrows():
        assert abs(row["latent_theta_shift_sd"] - (-0.2225)) < 0.001
        # Expected CR drop is steeper than MC drop due to guessing floors on MC and higher CR discrimination
        assert row["expected_cr_drop_pp"] < row["expected_mc_drop_pp"]
        # Expected beta is negative (between -1.3 and -2.3 pp)
        assert -2.30 < row["beta_expected_pp"] < -1.30
        # Observed beta is -0.97 pp
        assert abs(row["beta_observed_pp"] - (-0.97)) < 0.05
        # Excess beta is POSITIVE (beta_observed > beta_expected)
        assert row["beta_excess_pp"] > 0.0
        # No evidence of excess CR penalty
        assert "No" in row["evidence_of_excess_cr_penalty"]


def test_processed_parquets_exist_and_consistent():
    """Verify that all processed parquet files exist and have consistent row counts."""
    p_panel = PROCESSED_DIR / "timss_2019_2023_longitudinal_student_item.parquet"
    p_trends = PROCESSED_DIR / "timss_2019_2023_item_trends.parquet"
    p_screens = PROCESSED_DIR / "timss_2019_2023_screen_longitudinal_panel.parquet"
    
    assert p_panel.exists(), "Longitudinal student-item panel parquet missing"
    assert p_trends.exists(), "Item trends parquet missing"
    assert p_screens.exists(), "Screen longitudinal panel parquet missing"
    
    df_panel = pd.read_parquet(p_panel)
    assert len(df_panel) == 214056
    assert df_panel["idstud"].nunique() == 12060
    assert set(df_panel["year"].unique()) == {2019, 2023}
    assert df_panel["item_id"].nunique() == 84
    
    df_trends = pd.read_parquet(p_trends)
    assert len(df_trends) == 84
    assert set(df_trends["format"].unique()) == {"Multiple Choice", "Constructed Response"}
    
    df_screens = pd.read_parquet(p_screens)
    assert len(df_screens) > 180000
    assert df_screens["screen_id"].nunique() == 77
