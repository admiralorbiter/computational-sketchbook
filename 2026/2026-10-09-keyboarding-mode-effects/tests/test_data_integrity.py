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
    """Verify official NCES Table 4.1c reading and math item differences, percentages, and SEs in percentage points."""
    df_41c = pd.read_csv(RAW_DIR / "naep_2017_mode_table41c.csv")

    # Grade 4 Reading: DBA 60%, PBA 64%, Diff -3.8 pp (SE 0.22); CR: DBA 35%, PBA 42%, Diff -6.8 pp (SE 0.18)
    g4_rd_sr = df_41c[(df_41c["subject"] == "Reading") & (df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Selected"))].iloc[0]
    g4_rd_cr = df_41c[(df_41c["subject"] == "Reading") & (df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Constructed"))].iloc[0]
    
    assert g4_rd_sr["dba_pct"] == 60.0
    assert g4_rd_sr["pba_pct"] == 64.0
    assert g4_rd_sr["difference_pp"] == pytest.approx(-3.8)
    assert g4_rd_sr["se_pp"] == pytest.approx(0.22)

    assert g4_rd_cr["dba_pct"] == 35.0
    assert g4_rd_cr["pba_pct"] == 42.0
    assert g4_rd_cr["difference_pp"] == pytest.approx(-6.8)
    assert g4_rd_cr["se_pp"] == pytest.approx(0.18)
    assert (g4_rd_cr["difference_pp"] - g4_rd_sr["difference_pp"]) == pytest.approx(-3.0)

    # Grade 4 Mathematics: SR Diff -2.4 pp (SE 0.17); CR Diff -6.9 pp (SE 0.21)
    g4_m_sr = df_41c[(df_41c["subject"] == "Mathematics") & (df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Selected"))].iloc[0]
    g4_m_cr = df_41c[(df_41c["subject"] == "Mathematics") & (df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Constructed"))].iloc[0]

    assert g4_m_sr["difference_pp"] == pytest.approx(-2.4)
    assert g4_m_sr["se_pp"] == pytest.approx(0.17)
    assert g4_m_cr["difference_pp"] == pytest.approx(-6.9)
    assert g4_m_cr["se_pp"] == pytest.approx(0.21)
    # Highlight that CR penalty is nearly identical across Reading (-6.8 pp) and Math (-6.9 pp)
    assert abs(g4_rd_cr["difference_pp"] - g4_m_cr["difference_pp"]) == pytest.approx(0.1, abs=1e-4)

    # Grade 8 Reading: DBA 74%, PBA 76%, Diff -1.6 pp (SE 0.19); CR: DBA 53%, PBA 55%, Diff -2.0 pp (SE 0.24)
    g8_rd_sr = df_41c[(df_41c["subject"] == "Reading") & (df_41c["grade"] == 8) & (df_41c["item_type"].str.contains("Selected"))].iloc[0]
    g8_rd_cr = df_41c[(df_41c["subject"] == "Reading") & (df_41c["grade"] == 8) & (df_41c["item_type"].str.contains("Constructed"))].iloc[0]
    assert g8_rd_sr["dba_pct"] == 74.0
    assert g8_rd_sr["pba_pct"] == 76.0
    assert g8_rd_sr["difference_pp"] == pytest.approx(-1.6)
    assert g8_rd_sr["se_pp"] == pytest.approx(0.19)
    assert g8_rd_cr["dba_pct"] == 53.0
    assert g8_rd_cr["pba_pct"] == 55.0
    assert g8_rd_cr["difference_pp"] == pytest.approx(-2.0)
    assert g8_rd_cr["se_pp"] == pytest.approx(0.24)


def test_icils_scores():
    """Verify IEA ICILS digital literacy scores, 37-pt decline, 51% at/below Level 1, and 102-pt SES gap."""
    df_icils = pd.read_csv(RAW_DIR / "icils_cil_trends_2018_2023.csv")
    score_2018 = df_icils[(df_icils["metric"] == "U.S. 8th Grade CIL Score") & (df_icils["year"] == 2018)]["score"].values[0]
    score_2023 = df_icils[(df_icils["metric"] == "U.S. 8th Grade CIL Score") & (df_icils["year"] == 2023)]["score"].values[0]

    assert score_2018 == 519.0
    assert score_2023 == 482.0
    assert score_2018 - score_2023 == 37.0

    # Proficiency distribution: 25% below Level 1 + 26% Level 1 = 51% combined
    below_l1 = df_icils[df_icils["metric"] == "Below Level 1 (Deficient)"]["score"].values[0]
    l1 = df_icils[df_icils["metric"] == "Level 1 (Basic)"]["score"].values[0]
    comb_l1 = df_icils[df_icils["metric"] == "Combined At or Below Level 1"]["score"].values[0]
    assert below_l1 == 25.0
    assert l1 == 26.0
    assert comb_l1 == 51.0
    assert below_l1 + l1 == comb_l1

    # Socioeconomic gap: 102 scale points between highest and lowest quartiles
    ses_gap = df_icils[df_icils["metric"] == "Socioeconomic Gap (Highest vs Lowest SES Quartile)"]["score"].values[0]
    assert ses_gap == 102.0


def test_literature_bibliographic_fidelity():
    """Verify that citations match correct peer-reviewed journals, DOIs, and empirical estimates."""
    df_meta = pd.read_csv(RAW_DIR / "mode_effects_literature_meta.csv")

    # Backes & Cowan 2019
    bc_ela = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_ELA_Y1"].iloc[0]
    assert "Economics of Education Review" in bc_ela["publication"]
    assert bc_ela["doi"] == "10.1016/j.econedurev.2018.12.003"
    assert bc_ela["reported_effect"] == "-0.25 SD"

    bc_math = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_Math_Y1"].iloc[0]
    assert bc_math["reported_effect"] == "-0.10 SD"

    # Gordanier, Ozturk, & Zhan 2023: EFP Vol 18(2), pp. 232-252, DOI 10.1162/edfp_a_00373
    sc_ela = df_meta[df_meta["study_id"] == "Gordanier_Ozturk_Zhan_2023_SC_ELA"].iloc[0]
    assert "Education Finance and Policy" in sc_ela["publication"]
    assert "18(2)" in sc_ela["publication"]
    assert "232-252" in sc_ela["publication"]
    assert sc_ela["doi"] == "10.1162/edfp_a_00373"
    assert "Gordanier" in sc_ela["authors"]
    assert sc_ela["reported_effect"] == "-0.085 SD"

    sc_math = df_meta[df_meta["study_id"] == "Gordanier_Ozturk_Zhan_2023_SC_Math"].iloc[0]
    assert sc_math["reported_effect"] == "-0.044 SD"

    # Carol Parker 2018 (reconciled as non-significant chi-square, no fabricated SD)
    parker = df_meta[df_meta["study_id"] == "Parker_2018_TN_Keyboarding"].iloc[0]
    assert "Carol Parker" in parker["authors"]
    assert "Chi-square" in parker["reported_effect"] or "Non-significant" in parker["reported_effect"]
    assert "916" in parker["sample_size"] and "906" in parker["sample_size"]

    # NCES 2012 Writing Pilot: 110 computer words vs 159 paper words
    pilot = df_meta[df_meta["study_id"] == "NCES_2012_Writing_Pilot"].iloc[0]
    assert "110 words" in pilot["reported_effect"]
    assert "159 words" in pilot["reported_effect"]
    assert "12 WPM" in pilot["key_finding"]
    assert "30 WPM" in pilot["key_finding"]

    # NAEP 2017 Writing Technical Summary
    supp = df_meta[df_meta["study_id"] == "NAEP_2017_Writing_Technical_Summary"].iloc[0]
    assert "SUPPRESSED" in supp["reported_effect"]


def test_device_access_pulse_data():
    """Verify NCES School Pulse Panel device access statistics."""
    df_pulse = pd.read_csv(RAW_DIR / "nces_pulse_device_access.csv")
    p24 = df_pulse[df_pulse["year"] == 2024]["pct_1to1_devices"].values[0]
    assert p24 == 88.0
    p21 = df_pulse[df_pulse["year"] == 2021]["pct_1to1_devices"].values[0]
    assert p21 == 83.0


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
