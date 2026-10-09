"""
tests/test_data_integrity.py

Automated pytest verification suite for the Keyboarding & Digital Assessment
Mode Effects Observatory.

Verifies:
1. Primary data source integrity (NCES HSTS Table 1, EdWeek 2024, ICILS 2023, NCES Pulse).
2. Published empirical mode effect estimates (Backes & Cowan 2019, NAEP 2017 DBA).
3. Mathematical correctness of contrasts, format wedges, and simulation parameters.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"


def test_hsts_keyboarding_integrity():
    """Verify NCES HSTS Table 1 keyboarding credit trends."""
    df_hsts = pd.read_csv(RAW_DIR / "nces_hsts_2019_table1.csv")
    
    # Keyboarding values
    kb_2000 = df_hsts[(df_hsts["course_title"] == "Keyboarding") & (df_hsts["year"] == 2000)]["pct_graduates"].values[0]
    kb_2019 = df_hsts[(df_hsts["course_title"] == "Keyboarding") & (df_hsts["year"] == 2019)]["pct_graduates"].values[0]

    assert kb_2000 == 44.1, f"Expected 44.1% in 2000, got {kb_2000}"
    assert kb_2019 == 2.5, f"Expected 2.5% in 2019, got {kb_2019}"
    assert kb_2019 < kb_2000, "2019 keyboarding rate must be lower than 2000"

    # Word processing values
    wp_2000 = df_hsts[(df_hsts["course_title"] == "Word Processing") & (df_hsts["year"] == 2000)]["pct_graduates"].values[0]
    wp_2019 = df_hsts[(df_hsts["course_title"] == "Word Processing") & (df_hsts["year"] == 2019)]["pct_graduates"].values[0]
    assert wp_2000 == 12.8
    assert wp_2019 == 1.2


def test_device_pulse_integrity():
    """Verify NCES School Pulse Panel 1:1 device penetration."""
    df_pulse = pd.read_csv(RAW_DIR / "nces_pulse_device_access.csv")
    val_2024 = df_pulse[df_pulse["year"] == 2024]["pct_1to1_devices"].values[0]
    assert val_2024 == 88.0, f"Expected 88.0% 1:1 adoption in 2024-25, got {val_2024}"


def test_edweek_survey_integrity():
    """Verify EdWeek 2024 survey percentages and poverty gradients."""
    df_deliv = pd.read_csv(RAW_DIR / "edweek_keyboarding_survey_2024.csv")
    pct_map = dict(zip(df_deliv["mode"], df_deliv["pct"]))
    
    assert pct_map["Standalone Keyboard Class Only"] == 8.0
    assert pct_map["Both Standalone & Integrated"] == 11.0
    assert pct_map["Integrated within Regular Classroom Only"] == 50.0
    assert pct_map["No Formal Keyboarding Instruction"] == 31.0

    # Total must sum to 100%
    assert sum(df_deliv["pct"]) == 100.0

    df_equity = pd.read_csv(RAW_DIR / "edweek_equity_breakdown_2024.csv")
    k2_low = df_equity[(df_equity["grade_span"] == "Grades K-2") & (df_equity["poverty_tier"] == "Lower-Poverty Systems")]["pct_reporting_instruction"].values[0]
    k2_high = df_equity[(df_equity["grade_span"] == "Grades K-2") & (df_equity["poverty_tier"] == "Higher-Poverty Systems")]["pct_reporting_instruction"].values[0]

    assert k2_low == 36.0
    assert k2_high == 18.0
    assert k2_low == 2.0 * k2_high, "K-2 equity ratio must be exactly 2.0x"


def test_icils_scores():
    """Verify IEA ICILS digital literacy scores and 37-point decline."""
    df_icils = pd.read_csv(RAW_DIR / "icils_cil_trends_2018_2023.csv")
    score_2018 = df_icils[(df_icils["metric"] == "U.S. 8th Grade CIL Score") & (df_icils["year"] == 2018)]["score"].values[0]
    score_2023 = df_icils[(df_icils["metric"] == "U.S. 8th Grade CIL Score") & (df_icils["year"] == 2023)]["score"].values[0]

    assert score_2018 == 519.0
    assert score_2023 == 482.0
    assert score_2018 - score_2023 == 37.0


def test_mode_effects_meta():
    """Verify empirical mode effect benchmark estimates."""
    df_meta = pd.read_csv(DATA_DIR / "master_mode_effects_benchmark.csv")

    # Backes & Cowan 2019
    ma_ela_y1 = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_ELA_Y1"]["effect_size_sd"].values[0]
    ma_mat_y1 = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_Math_Y1"]["effect_size_sd"].values[0]
    assert ma_ela_y1 == -0.25
    assert ma_mat_y1 == -0.10

    # NAEP 2017 Format Contrast
    g4_mc = df_meta[df_meta["study_id"] == "NAEP_2017_DBA_G4_Reading_MC"]["effect_size_sd"].values[0]
    g4_cr = df_meta[df_meta["study_id"] == "NAEP_2017_DBA_G4_Reading_CR"]["effect_size_sd"].values[0]
    assert g4_mc == pytest.approx(-0.01)
    assert g4_cr == pytest.approx(-0.18)
    assert (g4_cr - g4_mc) == pytest.approx(-0.17)


def test_civ_simulation_properties():
    """Verify simulation dataset properties and directional effects."""
    df_sim = pd.read_parquet(DATA_DIR / "construct_irrelevant_variance_simulation.parquet")
    assert len(df_sim) == 2000

    # Grade 4 students should experience a larger CR mode penalty than Grade 8 students
    g4_cr_penalty = df_sim[df_sim["grade"] == 4]["delta_cr_mode"].mean()
    g8_cr_penalty = df_sim[df_sim["grade"] == 8]["delta_cr_mode"].mean()

    assert g4_cr_penalty < g8_cr_penalty, "Grade 4 should have larger negative penalty than Grade 8"
    assert g4_cr_penalty < -0.15, "Grade 4 mean CR penalty should be substantial"

    # Multiple choice mode effect should be close to zero across grades
    mc_penalty = df_sim["delta_mc_mode"].mean()
    assert abs(mc_penalty) < 0.05, f"MC mode penalty should be near 0, got {mc_penalty}"
