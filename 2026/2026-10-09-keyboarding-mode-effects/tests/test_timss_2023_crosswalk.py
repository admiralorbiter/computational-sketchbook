"""
Unit and Integration Tests for TIMSS 2023 U.S. Grade 4 Admission and Item Crosswalk.
Validates 5-PV sample accounting, three-way item reconciliation, primary 84 standard scaling sample,
secondary 100 PSI robustness sample, complete denominators, screen-level process timing (Table 20),
and raw microdata integrity.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "timss_2023"
RAW_19_DIR = PROJECT_ROOT / "data" / "raw" / "timss_2019"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"


def test_sample_accounting_table_18():
    """Verify Table 18 matches published IEA national benchmarks and 5-PV sample properties."""
    t18_path = TABLES_DIR / "table18_timss_2023_sample_accounting.csv"
    assert t18_path.exists(), "Table 18 CSV not found"
    
    df = pd.read_csv(t18_path)
    assert len(df) == 3, f"Expected 3 rows in Table 18, found {len(df)}"
    
    # Row 0: TIMSS 2019 (Official eTIMSS)
    row_19_off = df[df["assessment_cycle"].str.contains("Official eTIMSS")].iloc[0]
    assert row_19_off["total_assessed_students"] == 8776
    assert row_19_off["total_schools"] == 287
    assert row_19_off["total_classes"] == 507
    assert row_19_off["total_booklets"] == 14
    assert abs(row_19_off["population_weighted_5pv_mean"] - 534.73) < 0.05
    assert row_19_off["official_published_math_scale_score"] == 535.0
    assert abs(row_19_off["reconciliation_delta"] - (-0.27)) < 0.05
    
    # Row 1: TIMSS 2019 (eTIMSS + PSI)
    row_19_psi = df[df["assessment_cycle"].str.contains("eTIMSS \\+ PSI")].iloc[0]
    assert row_19_psi["total_assessed_students"] == 10029
    assert row_19_psi["total_schools"] == 287
    assert row_19_psi["total_classes"] == 507
    assert row_19_psi["total_booklets"] == 16
    assert abs(row_19_psi["population_weighted_5pv_mean"] - 533.53) < 0.05
    assert row_19_psi["official_published_math_scale_score"] == 535.0
    
    # Row 2: TIMSS 2023 (Official Digital)
    row_23 = df[df["assessment_cycle"].str.contains("TIMSS 2023")].iloc[0]
    assert row_23["total_assessed_students"] == 9090
    assert row_23["total_schools"] == 242
    assert row_23["total_classes"] == 479
    assert row_23["total_booklets"] == 14
    assert abs(row_23["population_weighted_5pv_mean"] - 516.93) < 0.05
    assert row_23["official_published_math_scale_score"] == 517.0
    assert abs(row_23["reconciliation_delta"] - (-0.07)) < 0.05
    
    # National drop reconciliation: 534.73 - 516.93 = 17.80 points (official published drop = 18.0)
    drop = row_19_off["population_weighted_5pv_mean"] - row_23["population_weighted_5pv_mean"]
    assert abs(drop - 17.80) < 0.10


def test_item_crosswalk_sample_tiers():
    """Verify Table 19 and crosswalk parquet reconcile primary, secondary, and subpart tiers."""
    t19_path = TABLES_DIR / "table19_timss_2019_2023_item_crosswalk.csv"
    parquet_path = PROCESSED_DIR / "timss_2019_2023_item_crosswalk.parquet"
    
    assert t19_path.exists(), "Table 19 CSV not found"
    assert parquet_path.exists(), "Crosswalk parquet not found"
    
    df_csv = pd.read_csv(t19_path)
    df_pq = pd.read_parquet(parquet_path)
    
    assert len(df_csv) == 157
    assert len(df_pq) == 157
    
    # 1. Proposed 107-Item NCES Trend Match: 104 scaling + 3 standalone unscaled
    assert df_pq["is_proposed_107_reconciliation"].sum() == 107
    scaling_in_trend = (df_pq["is_proposed_107_reconciliation"] & (df_pq["scaling_status"] == "Yes")).sum()
    unscaled_in_trend = (df_pq["is_proposed_107_reconciliation"] & (df_pq["scaling_status"] == "No")).sum()
    assert scaling_in_trend == 104
    assert unscaled_in_trend == 3
    standalone_ids = set(df_pq[df_pq["is_proposed_107_reconciliation"] & (df_pq["scaling_status"] == "No")]["item_id_2023"])
    assert standalone_ids == {"ME61021", "MQ71A01", "MQ71A03A"}
    
    # 2. Primary Analytical Sample: Exactly 84 standard scaling items dual-administered (non-PSI)
    assert df_pq["in_primary_scaling_sample"].sum() == 84
    primary = df_pq[df_pq["in_primary_scaling_sample"]]
    assert (primary["item_type"] == "MC").sum() == 32
    assert (primary["item_type"] == "CR").sum() == 52
    assert (primary["block"] != "A_MD4").all()
    
    # 3. Secondary Robustness Sample: Exactly 100 scaling items dual-administered (including PSI)
    assert df_pq["in_psi_robustness_sample"].sum() == 100
    sec = df_pq[df_pq["in_psi_robustness_sample"]]
    assert (sec["item_type"] == "MC").sum() == 33
    assert (sec["item_type"] == "CR").sum() == 67
    
    # 4. Standard eTIMSS Sample: Exactly 128 items dual-administered (7 non-PSI blocks)
    assert df_pq["in_standard_etimss_sample"].sum() == 128
    standard = df_pq[df_pq["in_standard_etimss_sample"]]
    assert (standard["item_type"] == "MC").sum() == 61
    assert (standard["item_type"] == "CR").sum() == 67
    assert (standard["scaling_status"] == "Yes").sum() == 84
    assert (standard["scaling_status"] == "No").sum() == 44
    
    # 5. Full Trend Pool: Exactly 151 items dual-administered across all 8 blocks
    assert df_pq["in_full_trend_sample"].sum() == 151
    full = df_pq[df_pq["in_full_trend_sample"]]
    assert (full["item_type"] == "MC").sum() == 62
    assert (full["item_type"] == "CR").sum() == 89
    
    # 6. Single-cycle unadministered items: Exactly 6 items
    single = df_pq[~df_pq["in_full_trend_sample"]]
    assert len(single) == 6
    single_ids = set(single["item_id_2023"])
    assert "ME71005" in single_ids  # 2023 only MC
    assert "ME71135A" in single_ids # 2023 only MC
    assert "ME71199" in single_ids  # 2023 only MC
    assert "ME61021" in single_ids  # 2019 only CR
    assert "ME61081" in single_ids  # 2023 parent code only
    assert "MQ71A01" in single_ids  # 2019 PSI intro only


def test_complete_denominators_and_process_timing():
    """Verify complete administered denominators (user_missing=True) and screen timing integrity."""
    parquet_path = PROCESSED_DIR / "timss_2019_2023_item_crosswalk.parquet"
    df = pd.read_parquet(parquet_path)
    
    # Standard eTIMSS blocks in 2019: within each block, all administered items share an identical denominator
    standard = df[df["in_standard_etimss_sample"]]
    assert (standard.groupby("block")["n_admin_2019"].nunique() == 1).all()
    assert (standard["n_admin_2019"] >= 1240).all() and (standard["n_admin_2019"] <= 1280).all()
    
    # In 2023, examinees per block are consistent and balanced
    assert (standard["n_admin_2023"] >= 1250).all()
    assert (standard["n_admin_2023"] <= 1350).all()
    
    # Accounting identity holds: Administered = Answered + Omitted + Not Reached
    for _, row in df.iterrows():
        if row["n_admin_2019"] > 0:
            assert row["n_admin_2019"] == (row["n_answered_2019"] + row["n_omitted_2019"] + row["n_not_reached_2019"])
        if row["n_admin_2023"] > 0:
            assert row["n_admin_2023"] == (row["n_answered_2023"] + row["n_omitted_2023"] + row["n_not_reached_2023"])
            
    # Process timing variables are documented and populated
    timing_items = df[df["has_timing_2019"] & df["has_timing_2023"]]
    assert len(timing_items) >= 150
    assert (timing_items["timing_var_2019"] != "").all()
    assert (timing_items["timing_var_2023"] != "").all()
    assert (timing_items["mean_screen_time_2019"] > 5).all()
    assert (timing_items["mean_screen_time_2019"] < 300).all()
    assert (timing_items["mean_screen_time_2023"] > 5).all()
    assert (timing_items["mean_screen_time_2023"] < 300).all()


def test_screen_level_timing_table_20():
    """Verify Table 20 deduplicates screen-level process timing across the 92 unique screens."""
    t20_path = TABLES_DIR / "table20_timss_2019_2023_screen_timing.csv"
    pq_path = PROCESSED_DIR / "timss_2019_2023_screen_timing.parquet"
    assert t20_path.exists(), "Table 20 CSV not found"
    assert pq_path.exists(), "Screen timing parquet not found"
    
    df_scr = pd.read_csv(t20_path)
    assert len(df_scr) == 92, f"Expected 92 unique screens, found {len(df_scr)}"
    
    # Screen presence in primary and secondary samples
    assert df_scr["in_primary_84_sample"].sum() == 78
    assert df_scr["in_secondary_100_sample"].sum() == 87
    
    # Both screen format classifications exist
    assert "screen_format_all_items" in df_scr.columns
    assert "screen_format_primary_items" in df_scr.columns
    
    # Primary screens breakdown under both classifications
    p_scr = df_scr[df_scr["in_primary_84_sample"]]
    assert p_scr["screen_format_all_items"].value_counts().to_dict() == {
        "Constructed Response": 36, "Multiple Choice": 31, "Mixed (MC + CR)": 11
    }
    assert p_scr["screen_format_primary_items"].value_counts().to_dict() == {
        "Constructed Response": 46, "Multiple Choice": 31, "Mixed (MC + CR)": 1
    }
    assert p_scr[p_scr["screen_format_primary_items"] == "Mixed (MC + CR)"]["screen_id"].iloc[0] == "ME61211"
    
    # All screens have auditable timing variable names
    assert (df_scr["timing_var_2019"].str.len() > 0).all()
    assert (df_scr["timing_var_2023"].str.len() > 0).all()
    
    # Valid screen durations: exactly 88 dual-administered screens and 4 single-cycle screens
    valid_dual = df_scr[df_scr["mean_screen_time_2019"].notna() & df_scr["mean_screen_time_2023"].notna()]
    assert len(valid_dual) == 88
    assert len(df_scr[df_scr["mean_screen_time_2019"].isna() | df_scr["mean_screen_time_2023"].isna()]) == 4
    assert (valid_dual["mean_screen_time_2019"] > 5).all()
    assert (valid_dual["mean_screen_time_2019"] < 300).all()
    assert (valid_dual["mean_screen_time_2023"] > 5).all()
    assert (valid_dual["mean_screen_time_2023"] < 300).all()
    
    # Verify recovered timing for screens ME71135 and ME61081
    me71135 = df_scr[df_scr["screen_id"] == "ME71135"].iloc[0]
    assert me71135["mean_screen_time_2019"] == 70.5
    assert me71135["mean_screen_time_2023"] == 68.7
    
    me61081 = df_scr[df_scr["screen_id"] == "ME61081"].iloc[0]
    assert me61081["mean_screen_time_2019"] == 82.4
    assert me61081["mean_screen_time_2023"] == 82.9


def test_microdata_and_process_data_files():
    """Verify raw SPSS microdata files and process data columns."""
    required_files_23 = [
        "asausam8.sav",
        "asrusam8.sav",
        "asgusam8.sav",
        "ashusam8.sav",
        "acgusam8.sav",
        "aspusam8.sav",
        "astusam8.sav",
        "atgusam8.sav"
    ]
    for rf in required_files_23:
        p = RAW_DIR / rf
        assert p.exists(), f"Missing required 2023 microdata file: {rf}"
        assert p.stat().st_size > 50_000, f"File appears too small or corrupt: {rf}"
        
    required_files_19 = [
        "asausam7.sav",
        "asausaz7.sav"
    ]
    for rf in required_files_19:
        p = RAW_19_DIR / rf
        assert p.exists(), f"Missing required 2019 microdata file: {rf}"
        assert p.stat().st_size > 50_000, f"File appears too small or corrupt: {rf}"
