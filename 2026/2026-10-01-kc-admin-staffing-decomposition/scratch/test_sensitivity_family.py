"""
Test script for the sensitivity family of Long-Difference CORSUP Growth models.
Tests:
1. Current absolute count model with HC3 robust SEs and Leave-One-District-Out (LODO).
2. Demographic share/rate changes (poverty rate, IDEA rate, LEP rate) + teacher scale.
3. Adding 2014 baseline CORSUP capacity (corsup_fte_2014 and corsup_per_100_teachers_2014).
4. Observed CRDC endpoints: 2015-16 -> 2023-24 (53 complete districts) and 2017-18 -> 2023-24 (55 districts).
5. Bootstrapped Shapley confidence intervals.
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
b55 = df[df["is_balanced_presence_cohort_55"] == 1].copy()

def get_diff_df(start_year, end_year, cohort_filter="is_balanced_presence_cohort_55"):
    sub = df[df[cohort_filter] == 1].copy()
    d_start = sub[sub["school_year"] == start_year].set_index("nces_lea_id")
    d_end = sub[sub["school_year"] == end_year].set_index("nces_lea_id")
    common = d_start.index.intersection(d_end.index)
    d_start = d_start.loc[common]
    d_end = d_end.loc[common]

    diff = pd.DataFrame(index=common)
    diff["state"] = d_start["state"]
    diff["district_name"] = d_start["lea_name"]
    diff["is_ks"] = (diff["state"] == "KS").astype(float)
    
    # Dependent variable
    diff["d_corsup"] = d_end["instructional_coordinators_fte"] - d_start["instructional_coordinators_fte"]
    
    # Scale changes
    diff["d_teachers_100"] = (d_end["teachers_k12_fte"] - d_start["teachers_k12_fte"]) / 100.0
    
    # Absolute counts (/ 100)
    diff["d_poverty_100"] = (d_end["saipe_est_population_5_17_poverty"] - d_start["saipe_est_population_5_17_poverty"]) / 100.0
    diff["d_idea_100"] = (d_end["idea_count_harmonized"] - d_start["idea_count_harmonized"]) / 100.0
    diff["d_lep_100"] = (d_end["lep_count_harmonized"] - d_start["lep_count_harmonized"]) / 100.0
    
    # Baseline 2014 capacity
    diff["base_corsup_fte"] = d_start["instructional_coordinators_fte"]
    diff["base_corsup_per_100t"] = (d_start["instructional_coordinators_fte"] / d_start["teachers_k12_fte"]) * 100.0
    
    # Demographic shares / rates (in percentage points: 0 to 100)
    diff["d_poverty_rate_pct"] = (d_end["saipe_poverty_pct"] - d_start["saipe_poverty_pct"]) * 100.0
    diff["d_idea_rate_pct"] = (d_end["idea_share"] - d_start["idea_share"]) * 100.0
    diff["d_lep_rate_pct"] = (d_end["lep_share"] - d_start["lep_share"]) * 100.0
    
    return diff.dropna()

print("Testing Model 1: Baseline Count Model with HC3:")
diff1423 = get_diff_df("2014-2015", "2023-2024")
X_count = sm.add_constant(diff1423[["d_teachers_100", "d_poverty_100", "d_idea_100", "d_lep_100", "is_ks"]])
res_count = sm.OLS(diff1423["d_corsup"], X_count).fit()
res_count_hc3 = sm.OLS(diff1423["d_corsup"], X_count).fit(cov_type="HC3")
print("Non-robust SEs vs HC3 SEs:")
for var in res_count.params.index:
    print(f"  {var:15s}: coef={res_count.params[var]:8.3f}, classic_se={res_count.bse[var]:7.3f} (p={res_count.pvalues[var]:.4f}), hc3_se={res_count_hc3.bse[var]:7.3f} (p={res_count_hc3.pvalues[var]:.4f})")
print(f"R2 = {res_count.rsquared:.4f}, N = {len(diff1423)}")

print("\nTesting Model 2: Adding Baseline 2014 Capacity (base_corsup_fte):")
X_base = sm.add_constant(diff1423[["d_teachers_100", "d_poverty_100", "d_idea_100", "d_lep_100", "is_ks", "base_corsup_fte"]])
res_base_hc3 = sm.OLS(diff1423["d_corsup"], X_base).fit(cov_type="HC3")
for var in res_base_hc3.params.index:
    print(f"  {var:20s}: coef={res_base_hc3.params[var]:8.3f}, hc3_se={res_base_hc3.bse[var]:7.3f} (p={res_base_hc3.pvalues[var]:.4f})")
print(f"R2 = {res_base_hc3.rsquared:.4f}")

print("\nTesting Model 3: Demographic Rate/Share Changes (% points) + Baseline Capacity:")
X_rate = sm.add_constant(diff1423[["d_teachers_100", "d_poverty_rate_pct", "d_idea_rate_pct", "d_lep_rate_pct", "is_ks", "base_corsup_fte"]])
res_rate_hc3 = sm.OLS(diff1423["d_corsup"], X_rate).fit(cov_type="HC3")
for var in res_rate_hc3.params.index:
    print(f"  {var:20s}: coef={res_rate_hc3.params[var]:8.3f}, hc3_se={res_rate_hc3.bse[var]:7.3f} (p={res_rate_hc3.pvalues[var]:.4f})")
print(f"R2 = {res_rate_hc3.rsquared:.4f}")

print("\nTesting Model 4: Observed CRDC Endpoints 2015-16 -> 2023-24 (53 Complete Cohort):")
diff1523 = get_diff_df("2015-2016", "2023-2024", "is_complete_outcome_cohort_53")
X_1523 = sm.add_constant(diff1523[["d_teachers_100", "d_poverty_100", "d_idea_100", "d_lep_100", "is_ks", "base_corsup_fte"]])
res_1523_hc3 = sm.OLS(diff1523["d_corsup"], X_1523).fit(cov_type="HC3")
for var in res_1523_hc3.params.index:
    print(f"  {var:20s}: coef={res_1523_hc3.params[var]:8.3f}, hc3_se={res_1523_hc3.bse[var]:7.3f} (p={res_1523_hc3.pvalues[var]:.4f})")
print(f"R2 = {res_1523_hc3.rsquared:.4f}, N = {len(diff1523)}")

print("\nTesting Model 5: 2017-18 -> 2023-24 (55 Balanced Cohort):")
diff1723 = get_diff_df("2017-2018", "2023-2024", "is_balanced_presence_cohort_55")
X_1723 = sm.add_constant(diff1723[["d_teachers_100", "d_poverty_100", "d_idea_100", "d_lep_100", "is_ks", "base_corsup_fte"]])
res_1723_hc3 = sm.OLS(diff1723["d_corsup"], X_1723).fit(cov_type="HC3")
for var in res_1723_hc3.params.index:
    print(f"  {var:20s}: coef={res_1723_hc3.params[var]:8.3f}, hc3_se={res_1723_hc3.bse[var]:7.3f} (p={res_1723_hc3.pvalues[var]:.4f})")
print(f"R2 = {res_1723_hc3.rsquared:.4f}, N = {len(diff1723)}")

print("\nLeave-One-Out (LODO) Influence Diagnostics on Baseline Count Model (d_teachers_100 coef):")
lodo_results = []
for idx in diff1423.index:
    sub = diff1423.drop(index=idx)
    sub_X = sm.add_constant(sub[["d_teachers_100", "d_poverty_100", "d_idea_100", "d_lep_100", "is_ks"]])
    sub_res = sm.OLS(sub["d_corsup"], sub_X).fit()
    lodo_results.append({
        "excluded_lea_id": idx,
        "excluded_name": diff1423.loc[idx, "district_name"],
        "d_teachers_coef": sub_res.params["d_teachers_100"],
        "d_poverty_coef": sub_res.params["d_poverty_100"],
        "r2": sub_res.rsquared
    })
df_lodo = pd.DataFrame(lodo_results)
df_lodo["coef_diff"] = df_lodo["d_teachers_coef"] - res_count.params["d_teachers_100"]
top_influence = df_lodo.reindex(df_lodo["coef_diff"].abs().sort_values(ascending=False).index).head(5)
print(top_influence[["excluded_name", "d_teachers_coef", "coef_diff", "r2"]])
