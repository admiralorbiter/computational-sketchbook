"""
Tests for Phase 9A Gate 0: Florida Measurement & Temporal Alignment Audit.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pytest

from src.audit_florida_gate0_measurement import (
    load_florida_high_school_panel,
    audit_crdc_vs_florida_statutory_rules,
    audit_threshold_section_jumps,
    audit_schedule_noise_and_alternative_facilities,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
TABLES_DIR = PROJECT_DIR / "artifacts" / "tables"

def test_florida_traditional_high_school_sample():
    fl = load_florida_high_school_panel()
    assert len(fl) > 25000, f"Expected >25,000 course cells, got {len(fl)}"
    assert fl["state"].unique() == ["FL"]
    assert not fl["is_charter"].any()
    assert fl["is_high_school"].all()
    assert set(fl["crdc_wave"].unique()) == {"2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"}

def test_gate0_rules_comparison_table():
    df_rules = audit_crdc_vs_florida_statutory_rules()
    assert len(df_rules) >= 5
    assert (TABLES_DIR / "table09_gate0_crdc_vs_florida_rules.csv").exists()

def test_gate0_threshold_jump_is_null_at_25():
    fl = load_florida_high_school_panel()
    df_jumps = audit_threshold_section_jumps(fl)
    assert (TABLES_DIR / "table10_gate0_threshold_jump_tests.csv").exists()
    
    # Check baseline All Traditional High Schools at C=25
    row_25 = df_jumps[(df_jumps["sample"] == "All Traditional High Schools") & (df_jumps["cutoff"] == 25)].iloc[0]
    # The jump should be statistically null (p > 0.05) and tiny (|jump| < 0.05)
    assert row_25["p_value"] > 0.05
    assert abs(row_25["jump_p_ge_k"]) < 0.05
    assert row_25["n_at"] > 100
    assert row_25["n_above"] > 100

def test_gate0_schedule_noise_diagnostics():
    fl = load_florida_high_school_panel()
    df_noise = audit_schedule_noise_and_alternative_facilities(fl)
    assert (TABLES_DIR / "table11_gate0_schedule_noise_audit.csv").exists()
    
    noise = df_noise.iloc[0]
    assert noise["total_cells_e_20_30"] > 1000
    assert noise["pct_cells_k_ge_3"] > 50.0
    assert noise["pct_cells_cs_lt_10"] > 50.0
