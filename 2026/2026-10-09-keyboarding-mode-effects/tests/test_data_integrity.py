"""
tests/test_data_integrity.py

Automated pytest verification suite for the Keyboarding & Digital Assessment
Mode Effects Observatory (Audited Source Fidelity Edition).

Verifies:
1. Primary data source fidelity against published values (NCES HSTS Table 1, EdWeek 2024, ICILS 2023, NAEP Table 4.1c).
2. Proper measurement units (percentage points vs. standard deviations).
3. Bibliographic and empirical attribution accuracy (Backes & Cowan 2019 EER, Gordanier et al. 2023 EFP, Parker 2018 JRBE).
4. Mathematical properties of parameter sensitivity grids.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"


def test_hsts_audited_table1():
    """Verify NCES HSTS Table 1 audited coursework values."""
    df_hsts = pd.read_csv(RAW_DIR / "nces_hsts_2019_table1.csv")

    # Keyboarding
    kb = dict(zip(df_hsts[df_hsts["course_title"] == "Keyboarding"]["year"],
                  df_hsts[df_hsts["course_title"] == "Keyboarding"]["pct_graduates"]))
    assert kb[2000] == 44.1
    assert kb[2005] == 26.6
    assert kb[2009] == 15.0
    assert kb[2019] == 2.5

    # Computer Applications (audited against HSTS Table 1)
    ca = dict(zip(df_hsts[df_hsts["course_title"] == "Computer Applications"]["year"],
                  df_hsts[df_hsts["course_title"] == "Computer Applications"]["pct_graduates"]))
    assert ca[2000] == 3.1
    assert ca[2005] == 26.8
    assert ca[2009] == 31.4
    assert ca[2019] == 10.4

    # Word Processing
    wp = dict(zip(df_hsts[df_hsts["course_title"] == "Word Processing"]["year"],
                  df_hsts[df_hsts["course_title"] == "Word Processing"]["pct_graduates"]))
    assert wp[2000] == 12.8
    assert wp[2005] == 5.0
    assert wp[2009] == 3.8
    assert wp[2019] == 1.2


def test_edweek_audited_survey():
    """Verify Education Week 2024 audited numbers and poverty gradient."""
    df_deliv = pd.read_csv(RAW_DIR / "edweek_keyboarding_survey_2024.csv")
    pct_map = dict(zip(df_deliv["mode"], df_deliv["pct"]))
    assert pct_map["Standalone Keyboard Class Only"] == 8.0
    assert pct_map["Both Standalone & Integrated"] == 11.0
    assert pct_map["Integrated within Regular Classroom Only"] == 50.0
    assert pct_map["No Formal Keyboarding Instruction"] == 31.0
    assert sum(df_deliv["pct"]) == 100.0

    # Poverty gradient in K-2: 74% vs 51% (1.45x disparity)
    df_equity = pd.read_csv(RAW_DIR / "edweek_equity_breakdown_2024.csv")
    k2_low = df_equity[(df_equity["grade_span"] == "Grades K-2") & (df_equity["poverty_tier"] == "Lower-Poverty Systems")]["pct_reporting_instruction"].values[0]
    k2_high = df_equity[(df_equity["grade_span"] == "Grades K-2") & (df_equity["poverty_tier"] == "Higher-Poverty Systems")]["pct_reporting_instruction"].values[0]
    assert k2_low == 74.0
    assert k2_high == 51.0
    assert (k2_low / k2_high) == pytest.approx(1.451, abs=0.01)


def test_naep_2017_mode_table41c():
    """Verify official NCES Table 4.1c reading item differences in percentage points."""
    df_41c = pd.read_csv(RAW_DIR / "naep_2017_mode_table41c.csv")

    # Grade 4
    g4_sr = df_41c[(df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Selected"))]["difference_pp"].values[0]
    g4_cr = df_41c[(df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Constructed"))]["difference_pp"].values[0]
    assert g4_sr == pytest.approx(-3.8)
    assert g4_cr == pytest.approx(-6.8)
    assert (g4_cr - g4_sr) == pytest.approx(-3.0)

    # Grade 8
    g8_sr = df_41c[(df_41c["grade"] == 8) & (df_41c["item_type"].str.contains("Selected"))]["difference_pp"].values[0]
    g8_cr = df_41c[(df_41c["grade"] == 8) & (df_41c["item_type"].str.contains("Constructed"))]["difference_pp"].values[0]
    assert g8_sr == pytest.approx(-1.6)
    assert g8_cr == pytest.approx(-2.0)
    assert (g8_cr - g8_sr) == pytest.approx(-0.4)


def test_icils_scores():
    """Verify IEA ICILS digital literacy scores and 37-point decline."""
    df_icils = pd.read_csv(RAW_DIR / "icils_cil_trends_2018_2023.csv")
    score_2018 = df_icils[(df_icils["metric"] == "U.S. 8th Grade CIL Score") & (df_icils["year"] == 2018)]["score"].values[0]
    score_2023 = df_icils[(df_icils["metric"] == "U.S. 8th Grade CIL Score") & (df_icils["year"] == 2023)]["score"].values[0]

    assert score_2018 == 519.0
    assert score_2023 == 482.0
    assert score_2018 - score_2023 == 37.0


def test_literature_bibliographic_fidelity():
    """Verify that citations match correct peer-reviewed journals and authors."""
    df_meta = pd.read_csv(RAW_DIR / "mode_effects_literature_meta.csv")

    # Backes & Cowan 2019
    bc = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_ELA_Y1"].iloc[0]
    assert "Economics of Education Review" in bc["publication"]
    assert bc["reported_effect"] == "-0.25 SD"

    # Gordanier et al. 2023
    sc = df_meta[df_meta["study_id"] == "Gordanier_Ozturk_Zhan_2023_SC"].iloc[0]
    assert "Education Finance and Policy" in sc["publication"]
    assert "Gordanier" in sc["authors"]

    # Carol Parker 2018 (reconciled as non-significant chi-square, no fabricated SD)
    parker = df_meta[df_meta["study_id"] == "Parker_2018_TN_Keyboarding"].iloc[0]
    assert "Carol Parker" in parker["authors"]
    assert "Chi-square" in parker["reported_effect"] or "Non-significant" in parker["reported_effect"]


def test_sensitivity_analysis_grid_properties():
    """Verify mathematical properties of the parameter sensitivity analysis."""
    df_grid = pd.read_parquet(DATA_DIR / "typing_threshold_sensitivity_grid.parquet")
    assert len(df_grid) == 12

    # Higher threshold WPM should monotonically increase % below threshold
    t15 = df_grid[df_grid["threshold_wpm"] == 15]["g4_pct_below_threshold"].iloc[0]
    t25 = df_grid[df_grid["threshold_wpm"] == 25]["g4_pct_below_threshold"].iloc[0]
    assert t25 > t15

    # Steeper penalty slope should increase magnitude of simulated penalty
    s10 = abs(df_grid[(df_grid["threshold_wpm"] == 25) & (df_grid["penalty_slope_sd_per_wpm"] == -0.010)]["g4_mean_simulated_penalty_sd"].iloc[0])
    s25 = abs(df_grid[(df_grid["threshold_wpm"] == 25) & (df_grid["penalty_slope_sd_per_wpm"] == -0.025)]["g4_mean_simulated_penalty_sd"].iloc[0])
    assert s25 > s10
