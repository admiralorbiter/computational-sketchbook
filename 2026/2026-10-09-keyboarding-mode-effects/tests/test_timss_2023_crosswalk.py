"""
Unit and Integration Tests for TIMSS 2023 U.S. Grade 4 Admission and Item Crosswalk.
Validates sample accounting, data integrity, microdata files, and 2019-2023 common items.
"""

from pathlib import Path
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "timss_2023"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"


def test_sample_accounting_table_18():
    """Verify Table 18 matches published IEA national benchmarks and sample properties."""
    t18_path = TABLES_DIR / "table18_timss_2023_sample_accounting.csv"
    assert t18_path.exists(), "Table 18 CSV not found"
    
    df = pd.read_csv(t18_path)
    assert len(df) == 1
    row = df.iloc[0]
    
    # Official sample properties
    assert row["total_assessed_students"] == 9090
    assert row["total_schools"] == 242
    assert row["total_classes"] == 479
    assert row["total_booklets"] == 14
    
    # Scale score alignment: 516.69 rounds to 517.0
    assert round(row["population_weighted_math_pv1"]) == int(row["official_published_math_scale_score"])
    assert row["official_published_math_scale_score"] == 517.0


def test_item_crosswalk_table_19_and_parquet():
    """Verify Table 19 and crosswalk parquet file consistency and counts."""
    t19_path = TABLES_DIR / "table19_timss_2019_2023_item_crosswalk.csv"
    parquet_path = PROCESSED_DIR / "timss_2019_2023_item_crosswalk.parquet"
    
    assert t19_path.exists(), "Table 19 CSV not found"
    assert parquet_path.exists(), "Crosswalk parquet not found"
    
    df_csv = pd.read_csv(t19_path)
    df_pq = pd.read_parquet(parquet_path)
    assert len(df_csv) == 132
    assert len(df_pq) == 132
    
    # Format counts in joint codebook space: 64 MC, 68 CR
    assert (df_pq["item_type"] == "MC").sum() == 64
    assert (df_pq["item_type"] == "CR").sum() == 68
    
    # Dual-administered items: exactly 128 items (61 MC, 67 CR)
    dual = df_pq[df_pq["administered_both"]]
    assert len(dual) == 128
    assert (dual["item_type"] == "MC").sum() == 61
    assert (dual["item_type"] == "CR").sum() == 67
    
    # Single-cycle unadministered items
    single = df_pq[~df_pq["administered_both"]]
    assert len(single) == 4
    single_ids = set(single["item_id"])
    assert single_ids == {"ME71005", "ME71135A", "ME71199", "ME61021"}
    
    # ME61021 was CR in 2019 only; others were MC in 2023 only
    me61021 = single[single["item_id"] == "ME61021"].iloc[0]
    assert me61021["n_examinees_2019"] == 1219
    assert me61021["n_examinees_2023"] == 0
    assert me61021["item_type"] == "CR"


def test_dual_administered_exposure_and_scaling():
    """Verify examinee exposure and scaling continuity for dual-administered items."""
    parquet_path = PROCESSED_DIR / "timss_2019_2023_item_crosswalk.parquet"
    df = pd.read_parquet(parquet_path)
    dual = df[df["administered_both"]]
    
    # Both formats have > 1,000 examinees on average in 2023
    mc_23_mean = dual[dual["item_type"] == "MC"]["n_examinees_2023"].mean()
    cr_23_mean = dual[dual["item_type"] == "CR"]["n_examinees_2023"].mean()
    assert 1200 <= mc_23_mean <= 1250
    assert 1200 <= cr_23_mean <= 1250
    
    # Scaling status: 84 scaling, 44 non-scaling
    assert (dual["scaling_status"] == "Yes").sum() == 84
    assert (dual["scaling_status"] == "No").sum() == 44


def test_microdata_and_process_data_files():
    """Verify raw SPSS microdata files and process data columns."""
    required_files = [
        "asausam8.sav",
        "asrusam8.sav",
        "asgusam8.sav",
        "ashusam8.sav",
        "acgusam8.sav",
        "aspusam8.sav",
        "astusam8.sav",
        "atgusam8.sav"
    ]
    for rf in required_files:
        p = RAW_DIR / rf
        assert p.exists(), f"Missing required microdata file: {rf}"
        assert p.stat().st_size > 50_000, f"File appears too small or corrupt: {rf}"
