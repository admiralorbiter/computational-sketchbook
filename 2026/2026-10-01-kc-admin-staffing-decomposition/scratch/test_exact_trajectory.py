"""
Test 10-year annual trajectory with exact state-by-state pricing.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "processed" / "district_demand_year.parquet"
df = pd.read_parquet(DATA_PATH)

b55 = df[df["is_balanced_presence_cohort_55"] == 1].copy()
d14 = b55[b55["school_year"] == "2014-2015"]
base_ratio = d14["instructional_coordinators_fte"].sum() / d14["teachers_k12_fte"].sum()

sy_list = [
    "2014-2015", "2015-2016", "2016-2017", "2017-2018", "2018-2019",
    "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"
]

records = []
for sy in sy_list:
    sub = b55[b55["school_year"] == sy].copy()
    is_reconstructed = (sy == "2015-2016")
    
    # In 2015-16, replace missing Olathe and Gardner with reconstructed values
    if is_reconstructed:
        sub.loc[sub["nces_lea_id"] == "2010140", "teachers_k12_fte"] = 2018.42
        sub.loc[sub["nces_lea_id"] == "2010140", "instructional_coordinators_fte"] = 34.82
        sub.loc[sub["nces_lea_id"] == "2006420", "teachers_k12_fte"] = 329.00
        sub.loc[sub["nces_lea_id"] == "2006420", "instructional_coordinators_fte"] = 3.90
        
    sub_ks = sub[sub["state"] == "KS"]
    sub_mo = sub[sub["state"] == "MO"]
    
    t_ks = sub_ks["teachers_k12_fte"].sum()
    t_mo = sub_mo["teachers_k12_fte"].sum()
    t_tot = t_ks + t_mo
    
    c_ks = sub_ks["instructional_coordinators_fte"].sum()
    c_mo = sub_mo["instructional_coordinators_fte"].sum()
    c_tot = c_ks + c_mo
    
    target_ks = t_ks * base_ratio
    target_mo = t_mo * base_ratio
    target_tot = t_tot * base_ratio
    
    surplus_ks = c_ks - target_ks
    surplus_mo = c_mo - target_mo
    surplus_tot = c_tot - target_tot
    
    # Pricing: allow surplus to be priced by state, capped at 0 at cohort level
    savings_ks = surplus_ks * 99450.0
    savings_mo = surplus_mo * 93600.0
    savings_tot = max(0.0, savings_ks + savings_mo)
    
    records.append({
        "school_year": sy,
        "teachers_total_fte": round(t_tot, 2),
        "actual_coordinators_fte": round(c_tot, 2),
        "baseline_target_coordinators_fte": round(target_tot, 2),
        "net_surplus_coordinators_fte": round(surplus_tot, 2),
        "ks_surplus_fte": round(surplus_ks, 2),
        "mo_surplus_fte": round(surplus_mo, 2),
        "net_cohort_annual_cost_savings": round(savings_tot, 2),
        "flag_reconstructed_ks_2015_16": is_reconstructed
    })

traj_df = pd.DataFrame(records)
print(traj_df[["school_year", "teachers_total_fte", "actual_coordinators_fte", "net_surplus_coordinators_fte", "net_cohort_annual_cost_savings"]])
cum_fte = traj_df["net_surplus_coordinators_fte"].sum()
cum_cost = traj_df["net_cohort_annual_cost_savings"].sum()
clean_9 = traj_df[traj_df["school_year"] != "2015-2016"]
clean_fte = clean_9["net_surplus_coordinators_fte"].sum()
clean_cost = clean_9["net_cohort_annual_cost_savings"].sum()

print(f"\n10-Year Cumulative: {cum_fte:.2f} FTE-Yrs, ${cum_cost:,.2f}")
print(f"9-Year Clean: {clean_fte:.2f} FTE-Yrs, ${clean_cost:,.2f}")
