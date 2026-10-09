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

    # Grade 4 Mathematics: DBA 54%, PBA 56%, Diff -2.4 pp (SE 0.24); CR: DBA 46%, PBA 52%, Diff -6.9 pp (SE 0.31)
    g4_m_sr = df_41c[(df_41c["subject"] == "Mathematics") & (df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Selected"))].iloc[0]
    g4_m_cr = df_41c[(df_41c["subject"] == "Mathematics") & (df_41c["grade"] == 4) & (df_41c["item_type"].str.contains("Constructed"))].iloc[0]

    assert g4_m_sr["dba_pct"] == 54.0
    assert g4_m_sr["pba_pct"] == 56.0
    assert g4_m_sr["difference_pp"] == pytest.approx(-2.4)
    assert g4_m_sr["se_pp"] == pytest.approx(0.24)

    assert g4_m_cr["dba_pct"] == 46.0
    assert g4_m_cr["pba_pct"] == 52.0
    assert g4_m_cr["difference_pp"] == pytest.approx(-6.9)
    assert g4_m_cr["se_pp"] == pytest.approx(0.31)
    assert (g4_m_cr["difference_pp"] - g4_m_sr["difference_pp"]) == pytest.approx(-4.5)

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

    # Grade 8 Mathematics: DBA 51%, PBA 53%, Diff -2.5 pp (SE 0.26); CR: Diff -3.5 pp (SE 0.30)
    g8_m_sr = df_41c[(df_41c["subject"] == "Mathematics") & (df_41c["grade"] == 8) & (df_41c["item_type"].str.contains("Selected"))].iloc[0]
    g8_m_cr = df_41c[(df_41c["subject"] == "Mathematics") & (df_41c["grade"] == 8) & (df_41c["item_type"].str.contains("Constructed"))].iloc[0]
    assert g8_m_sr["dba_pct"] == 51.0
    assert g8_m_sr["pba_pct"] == 53.0
    assert g8_m_sr["difference_pp"] == pytest.approx(-2.5)
    assert g8_m_sr["se_pp"] == pytest.approx(0.26)
    assert g8_m_cr["difference_pp"] == pytest.approx(-3.5)
    assert g8_m_cr["se_pp"] == pytest.approx(0.30)


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
    """Verify that citations match correct peer-reviewed journals, DOIs, model fields, and empirical estimates."""
    df_meta = pd.read_csv(RAW_DIR / "mode_effects_literature_meta.csv")

    # Verify structured econometric schema
    required_cols = ["study_id", "authors", "year", "publication", "table_reference", "estimation_model", "coefficient", "standard_error"]
    for col in required_cols:
        assert col in df_meta.columns

    # Backes & Cowan 2019
    bc_ela = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_ELA_Y1"].iloc[0]
    assert "Economics of Education Review" in bc_ela["publication"]
    assert bc_ela["doi"] == "10.1016/j.econedurev.2018.12.003"
    assert bc_ela["coefficient"] == -0.250

    bc_math = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_Math_Y1"].iloc[0]
    assert bc_math["coefficient"] == -0.100

    # Gordanier, Ozturk, & Zhan 2023: EFP Vol 18(2), pp. 232-252, Table 3 OLS estimates
    sc_ela = df_meta[df_meta["study_id"] == "Gordanier_Ozturk_Zhan_2023_SC_ELA"].iloc[0]
    assert "Education Finance and Policy" in sc_ela["publication"]
    assert "18(2)" in sc_ela["publication"]
    assert "232-252" in sc_ela["publication"]
    assert sc_ela["doi"] == "10.1162/edfp_a_00373"
    assert "Table 3" in sc_ela["table_reference"]
    assert sc_ela["coefficient"] == -0.085
    assert sc_ela["standard_error"] == 0.007

    sc_math = df_meta[df_meta["study_id"] == "Gordanier_Ozturk_Zhan_2023_SC_Math"].iloc[0]
    assert "Table 3" in sc_math["table_reference"]
    assert sc_math["coefficient"] == -0.024  # Table 3 OLS estimate (not the -0.044 science interaction)
    assert sc_math["standard_error"] == 0.007

    # Carol Parker 2018 (reconciled as non-significant chi-square, no fabricated SD)
    parker = df_meta[df_meta["study_id"] == "Parker_2018_TN_Keyboarding"].iloc[0]
    assert "Carol Parker" in parker["authors"]
    assert "Chi-square" in parker["reported_effect"] or "Non-significant" in parker["reported_effect"]
    assert "916" in parker["sample_size"] and "906" in parker["sample_size"]

    # NAEP 2017 Writing Technical Summary (cautious official wording)
    supp = df_meta[df_meta["study_id"] == "NAEP_2017_Writing_Technical_Summary"].iloc[0]
    assert "SUPPRESSED" in supp["reported_effect"]
    assert "unresolved comparability concerns" in supp["key_finding"]


def test_writing_pilot_comparison():
    """Verify NCES Writing Pilot 2010 vs 2012 benchmarks, score parity, and distributional shift."""
    df_pilot = pd.read_csv(RAW_DIR / "nces_writing_pilot_comparison.csv")
    
    # Response length: 159 words paper vs 110 words computer (-49 words)
    rlen = df_pilot[df_pilot["metric"].str.contains("Response Length")].iloc[0]
    assert rlen["paper_2010"] == 159.0
    assert rlen["computer_2012"] == 110.0
    assert rlen["difference"] == -49.0

    # Average score: 2.98 paper vs 3.08 computer
    score = df_pilot[df_pilot["metric"].str.contains("Average Score")].iloc[0]
    assert score["paper_2010"] == pytest.approx(2.98)
    assert score["computer_2012"] == pytest.approx(3.08)

    # Usability speeds: 12 WPM (G4), 30 WPM (G8)
    g4_wpm = df_pilot[df_pilot["metric"].str.contains("Grade 4")].iloc[0]["computer_2012"]
    g8_wpm = df_pilot[df_pilot["metric"].str.contains("Grade 8")].iloc[0]["computer_2012"]
    assert g4_wpm == 12.0
    assert g8_wpm == 30.0


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
