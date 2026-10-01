import sys
from pathlib import Path
import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from comparability import assert_outcome_eligible, filter_eligible_observations

# Load canonical demand panel
df = pd.read_parquet(PROJECT_ROOT / "data" / "processed" / "district_demand_year.parquet")
df["nces_lea_id"] = df["nces_lea_id"].astype(str).str.zfill(7)
df["year_int"] = df["school_year"].str[:4].astype(int)

# Balanced 55 regular districts
b55 = df[df["is_balanced_presence_cohort_55"]].copy()
b55["state_year"] = b55["state"] + "_" + b55["school_year"]

print(f"Loaded {len(b55)} balanced cohort district-year records.")

# -------------------------------------------------------------
# 1. SCHADM MODEL (2014-15 to 2023-24, pre-KS-break)
# -------------------------------------------------------------
ok, msg = assert_outcome_eligible("school_administrators_fte", "2014-2015", "2023-2024")
print(f"SCHADM gate: {ok} | {msg}")

sch_df = b55[(b55["school_year"] >= "2014-2015") & (b55["school_year"] <= "2023-2024")].copy()
sch_df = sch_df.dropna(subset=["school_administrators_fte", "enrollment_total", "operating_schools_count"])
sch_df["enrollment_1k"] = sch_df["enrollment_total"] / 1000.0

sch_p = sch_df.set_index(["nces_lea_id", "year_int"])
mod_sch = PanelOLS(sch_p["school_administrators_fte"], sch_p[["enrollment_1k", "operating_schools_count"]], entity_effects=True, other_effects=sch_p["state_year"])
res_sch = mod_sch.fit(cov_type="clustered", cluster_entity=True)
print("\n=== MODEL 1: SCHADM Within-District FE ===")
print(res_sch.summary)

# -------------------------------------------------------------
# 2. LEAADM MODEL (2014-15 to 2023-24, pre-KS-break)
# -------------------------------------------------------------
ok, msg = assert_outcome_eligible("lea_administrators_fte", "2014-2015", "2023-2024")
print(f"\nLEAADM gate: {ok} | {msg}")

lea_df = sch_df.dropna(subset=["lea_administrators_fte"]).copy()
lea_p = lea_df.set_index(["nces_lea_id", "year_int"])
mod_lea = PanelOLS(lea_p["lea_administrators_fte"], lea_p[["enrollment_1k", "operating_schools_count"]], entity_effects=True, other_effects=lea_p["state_year"])
res_lea = mod_lea.fit(cov_type="clustered", cluster_entity=True)
print("\n=== MODEL 2: LEAADM Within-District FE ===")
print(res_lea.summary)

# -------------------------------------------------------------
# 3. CORSUP MODEL (2014-15 to 2022-23 with F-33 Finance)
# -------------------------------------------------------------
ok, msg = assert_outcome_eligible("instructional_coordinators_fte", "2014-2015", "2023-2024")
print(f"\nCORSUP gate: {ok} | {msg}")

cor_df = b55[(b55["school_year"] >= "2014-2015") & (b55["school_year"] <= "2022-2023")].copy()
cor_df["teachers_100"] = cor_df["teachers_k12_fte"] / 100.0
cor_df["idea_100"] = cor_df["idea_count_harmonized"] / 100.0
cor_df["lep_100"] = cor_df["lep_count_harmonized"] / 100.0
cor_df["poverty_100"] = cor_df["saipe_est_population_5_17_poverty"] / 100.0
cor_df["title_i_mil"] = cor_df["rev_fed_state_title_i"] / 1e6
cor_df["idea_rev_mil"] = cor_df["rev_fed_state_idea"] / 1e6

cor_vars = ["teachers_100", "idea_100", "lep_100", "poverty_100", "title_i_mil", "idea_rev_mil"]
cor_df = cor_df.dropna(subset=["instructional_coordinators_fte"] + cor_vars)

cor_p = cor_df.set_index(["nces_lea_id", "year_int"])
mod_cor = PanelOLS(cor_p["instructional_coordinators_fte"], cor_p[cor_vars], entity_effects=True, other_effects=cor_p["state_year"])
res_cor = mod_cor.fit(cov_type="clustered", cluster_entity=True)
print("\n=== MODEL 3: CORSUP Within-District FE ===")
print(res_cor.summary)
