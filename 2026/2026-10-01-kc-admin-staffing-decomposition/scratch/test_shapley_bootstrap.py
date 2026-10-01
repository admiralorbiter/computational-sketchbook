"""
Bootstrap confidence intervals for Grouped Shapley variance decomposition.
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

d14 = b55[b55["school_year"] == "2014-2015"].set_index("nces_lea_id")
d23 = b55[b55["school_year"] == "2023-2024"].set_index("nces_lea_id")

diff = pd.DataFrame(index=d14.index)
diff["state"] = d14["state"]
diff["district_name"] = d14["lea_name"]
diff["d_corsup"] = d23["instructional_coordinators_fte"] - d14["instructional_coordinators_fte"]
diff["d_teachers_100"] = (d23["teachers_k12_fte"] - d14["teachers_k12_fte"]) / 100.0
diff["d_poverty_100"] = (d23["saipe_est_population_5_17_poverty"] - d14["saipe_est_population_5_17_poverty"]) / 100.0
diff["d_idea_100"] = (d23["idea_count_harmonized"] - d14["idea_count_harmonized"]) / 100.0
diff["d_lep_100"] = (d23["lep_count_harmonized"] - d14["lep_count_harmonized"]) / 100.0
diff["is_ks"] = (diff["state"] == "KS").astype(float)
diff["base_corsup_fte"] = d14["instructional_coordinators_fte"]
diff = diff.dropna().copy()

def compute_shapley(df_data, groups):
    group_names = list(groups.keys())
    k = len(group_names)
    r2_map = {}
    for r in range(k + 1):
        for subset in itertools.combinations(group_names, r):
            if r == 0:
                r2_map[()] = 0.0
            else:
                cols = []
                for g in subset:
                    cols.extend(groups[g])
                sub_X = sm.add_constant(df_data[cols])
                reg_sub = sm.OLS(df_data["d_corsup"], sub_X).fit()
                r2_map[tuple(sorted(subset))] = reg_sub.rsquared

    shapley_vals = {}
    for g in group_names:
        others = [x for x in group_names if x != g]
        val = 0.0
        for r in range(len(others) + 1):
            for subset in itertools.combinations(others, r):
                w = (math.factorial(len(subset)) * math.factorial(k - len(subset) - 1)) / math.factorial(k)
                marginal = r2_map[tuple(sorted(subset + (g,)))] - r2_map[tuple(sorted(subset))]
                val += w * marginal
        shapley_vals[g] = val
    tot = sum(shapley_vals.values())
    pcts = {g: (v / tot * 100.0) if tot > 0 else 0.0 for g, v in shapley_vals.items()}
    return pcts, r2_map[tuple(sorted(group_names))]

# 3-group baseline
groups_base = {
    "Teacher Scale Growth": ["d_teachers_100"],
    "Student Need Shifts": ["d_poverty_100", "d_idea_100", "d_lep_100"],
    "State Jurisdiction": ["is_ks"]
}

point_pcts, total_r2 = compute_shapley(diff, groups_base)
print("Point estimates:", point_pcts, f"R2={total_r2:.4f}")

# Bootstrap
np.random.seed(42)
n_boot = 500
boot_records = []
for i in range(n_boot):
    boot_df = diff.sample(n=len(diff), replace=True)
    try:
        b_pcts, b_r2 = compute_shapley(boot_df, groups_base)
        boot_records.append(b_pcts)
    except Exception:
        pass

df_boot = pd.DataFrame(boot_records)
print("\nBootstrap 95% Confidence Intervals (500 draws):")
for col in df_boot.columns:
    low = np.percentile(df_boot[col], 2.5)
    high = np.percentile(df_boot[col], 97.5)
    median = np.median(df_boot[col])
    print(f"  {col:25s}: point={point_pcts[col]:5.1f}%, median={median:5.1f}%, 95% CI=[{low:5.1f}%, {high:5.1f}%]")

# 4-group specification including Baseline Capacity
groups_with_base = {
    "Teacher Scale Growth": ["d_teachers_100"],
    "Student Need Shifts": ["d_poverty_100", "d_idea_100", "d_lep_100"],
    "Baseline Capacity": ["base_corsup_fte"],
    "State Jurisdiction": ["is_ks"]
}
point_pcts_wb, total_r2_wb = compute_shapley(diff, groups_with_base)
print("\nPoint estimates with Baseline Capacity (4-group):", point_pcts_wb, f"R2={total_r2_wb:.4f}")

boot_records_wb = []
for i in range(n_boot):
    boot_df = diff.sample(n=len(diff), replace=True)
    try:
        b_pcts, b_r2 = compute_shapley(boot_df, groups_with_base)
        boot_records_wb.append(b_pcts)
    except Exception:
        pass
df_boot_wb = pd.DataFrame(boot_records_wb)
print("Bootstrap 95% CI with Baseline Capacity:")
for col in df_boot_wb.columns:
    low = np.percentile(df_boot_wb[col], 2.5)
    high = np.percentile(df_boot_wb[col], 97.5)
    print(f"  {col:25s}: point={point_pcts_wb[col]:5.1f}%, 95% CI=[{low:5.1f}%, {high:5.1f}%]")
