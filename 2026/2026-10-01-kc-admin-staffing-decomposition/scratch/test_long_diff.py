"""
Test script for long-difference model and Shapley growth decomposition.
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
from itertools import combinations
import math

df = pd.read_parquet('data/processed/district_demand_year.parquet')
b55 = df[df['is_balanced_presence_cohort_55'] == 1].copy()

# Clean endpoints 2014-15 and 2023-24
d14 = b55[b55['school_year'] == '2014-2015'].set_index('nces_lea_id')
d23 = b55[b55['school_year'] == '2023-2024'].set_index('nces_lea_id')

diff = pd.DataFrame(index=d14.index)
diff['state'] = d14['state']
diff['district_name'] = d14['lea_name']
diff['d_corsup'] = d23['instructional_coordinators_fte'] - d14['instructional_coordinators_fte']
diff['d_teachers_100'] = (d23['teachers_k12_fte'] - d14['teachers_k12_fte']) / 100.0
diff['d_poverty_100'] = (d23['saipe_est_population_5_17_poverty'] - d14['saipe_est_population_5_17_poverty']) / 100.0
diff['d_idea_100'] = (d23['idea_per_teacher']*d23['teachers_k12_fte'] - d14['idea_per_teacher']*d14['teachers_k12_fte']) / 100.0
diff['d_lep_100'] = (d23['lep_per_teacher']*d23['teachers_k12_fte'] - d14['lep_per_teacher']*d14['teachers_k12_fte']) / 100.0
diff['is_ks'] = (diff['state'] == 'KS').astype(float)

# Fit OLS
X_vars = ['d_teachers_100', 'd_poverty_100', 'd_idea_100', 'd_lep_100', 'is_ks']
X = sm.add_constant(diff[X_vars])
model = sm.OLS(diff['d_corsup'], X).fit()
print("Long-Difference OLS Results:")
print(model.summary())

# Grouped Shapley on Long Difference Growth
groups = {
    "Teacher Scale Growth": ["d_teachers_100"],
    "Student Need Shifts": ["d_poverty_100", "d_idea_100", "d_lep_100"],
    "State Jurisdiction": ["is_ks"]
}

group_names = list(groups.keys())
k = len(group_names)
r2_map = {}

for r in range(k + 1):
    for subset in combinations(group_names, r):
        if r == 0:
            r2_map[()] = 0.0
        else:
            cols = []
            for g in subset:
                cols.extend(groups[g])
            sub_X = sm.add_constant(diff[cols])
            reg = sm.OLS(diff['d_corsup'], sub_X).fit()
            r2_map[tuple(sorted(subset))] = reg.rsquared

tot_r2 = r2_map[tuple(sorted(group_names))]
shapley_vals = {}
for g in group_names:
    others = [x for x in group_names if x != g]
    val = 0.0
    for r in range(len(others) + 1):
        for subset in combinations(others, r):
            w = (math.factorial(len(subset)) * math.factorial(k - len(subset) - 1)) / math.factorial(k)
            marginal = r2_map[tuple(sorted(subset + (g,)))] - r2_map[tuple(sorted(subset))]
            val += w * marginal
    shapley_vals[g] = val

print("\nGrouped Shapley on Growth (Delta CORSUP):")
for g, v in shapley_vals.items():
    pct = (v / tot_r2) * 100.0
    print(f"  {g}: Shapley R2 = {v:.4f} ({pct:.1f}% of explained variance)")
