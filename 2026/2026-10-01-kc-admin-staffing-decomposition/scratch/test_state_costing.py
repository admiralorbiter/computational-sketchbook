"""
Test exact state-specific costing for CF1 coordinator rollback.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "district_demand_year.parquet"
df = pd.read_parquet(DATA_PATH)

b55 = df[df["is_balanced_presence_cohort_55"] == 1].copy()
d14 = b55[b55["school_year"] == "2014-2015"]
base_ratio = d14["instructional_coordinators_fte"].sum() / d14["teachers_k12_fte"].sum()
print(f"2014 Regional Baseline Ratio: {base_ratio:.6f} coordinators per teacher ({base_ratio*100:.2f} per 100t)")

# 2023-24
d23 = b55[b55["school_year"] == "2023-2024"].copy()
d23_ks = d23[d23["state"] == "KS"]
d23_mo = d23[d23["state"] == "MO"]

ks_teachers = d23_ks["teachers_k12_fte"].sum()
mo_teachers = d23_mo["teachers_k12_fte"].sum()
tot_teachers = ks_teachers + mo_teachers

ks_actual_c = d23_ks["instructional_coordinators_fte"].sum()
mo_actual_c = d23_mo["instructional_coordinators_fte"].sum()
tot_actual_c = ks_actual_c + mo_actual_c

ks_target_c = ks_teachers * base_ratio
mo_target_c = mo_teachers * base_ratio
tot_target_c = tot_teachers * base_ratio

ks_surplus_c = ks_actual_c - ks_target_c
mo_surplus_c = mo_actual_c - mo_target_c
tot_surplus_c = tot_actual_c - tot_target_c

cost_ks = ks_surplus_c * 99450.0
cost_mo = mo_surplus_c * 93600.0
tot_exact_cost = cost_ks + cost_mo

print(f"KS Surplus: {ks_surplus_c:.2f} FTE -> Cost: ${cost_ks:,.2f}")
print(f"MO Surplus: {mo_surplus_c:.2f} FTE -> Cost: ${cost_mo:,.2f}")
print(f"Total Exact Cost: ${tot_exact_cost:,.2f} across {tot_surplus_c:.2f} FTE")
