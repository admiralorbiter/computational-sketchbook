"""
Prototype of upgraded models.py functions.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import itertools
import math

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "district_demand_year.parquet"
df = pd.read_parquet(DATA_PATH)

def run_prototype():
    # Test diff construction
    b55 = df[df["is_balanced_presence_cohort_55"] == 1].copy()
    d14 = b55[b55["school_year"] == "2014-2015"].set_index("nces_lea_id")
    d23 = b55[b55["school_year"] == "2023-2024"].set_index("nces_lea_id")
    
    diff = pd.DataFrame(index=d14.index)
    diff["state"] = d14["state"]
    diff["district_name"] = d14["lea_name"]
    diff["is_ks"] = (diff["state"] == "KS").astype(float)
    diff["d_corsup"] = d23["instructional_coordinators_fte"] - d14["instructional_coordinators_fte"]
    diff["d_teachers_100"] = (d23["teachers_k12_fte"] - d14["teachers_k12_fte"]) / 100.0
    diff["d_poverty_100"] = (d23["saipe_est_population_5_17_poverty"] - d14["saipe_est_population_5_17_poverty"]) / 100.0
    diff["d_idea_100"] = (d23["idea_count_harmonized"] - d14["idea_count_harmonized"]) / 100.0
    diff["d_lep_100"] = (d23["lep_count_harmonized"] - d14["lep_count_harmonized"]) / 100.0
    diff["base_corsup_fte"] = d14["instructional_coordinators_fte"]
    diff["d_poverty_rate_pct"] = (d23["saipe_poverty_pct"] - d14["saipe_poverty_pct"]) * 100.0
    diff["d_idea_rate_pct"] = (d23["idea_share"] - d14["idea_share"]) * 100.0
    diff["d_lep_rate_pct"] = (d23["lep_share"] - d14["lep_share"]) * 100.0
    diff = diff.dropna().copy()
    
    print(f"Diff built successfully. N = {len(diff)}")

run_prototype()
