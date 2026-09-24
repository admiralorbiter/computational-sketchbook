import pandas as pd
import numpy as np

# Load CRDC long course aggregates
df = pd.read_csv("data/processed/kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv")
hs_df = df[df["school_level"] == "High"].copy()

core_math = ["alg1", "geom", "alg2"]
adv_math = ["advm", "calc"]
core_sci = ["bio", "chem"]

records = []
for (yr, nces_id, sch_name, dist_name, state), g in hs_df.groupby(
    ["school_year", "nces_school_id", "school_name", "district_name", "state"]
):
    enr = g["enrollment_k12"].iloc[0]
    ptr = g["school_ptr"].iloc[0]
    
    # Core Math
    cm = g[g["course_code"].isin(core_math)]
    cm_classes = cm["num_classes"].sum()
    cm_enrolled = cm["num_enrolled"].sum()
    cm_size = cm_enrolled / cm_classes if cm_classes > 0 else np.nan
    
    # Adv Math
    am = g[g["course_code"].isin(adv_math)]
    am_classes = am["num_classes"].sum()
    am_enrolled = am["num_enrolled"].sum()
    am_size = am_enrolled / am_classes if am_classes > 0 else np.nan
    
    # Core Science
    cs = g[g["course_code"].isin(core_sci)]
    cs_classes = cs["num_classes"].sum()
    cs_enrolled = cs["num_enrolled"].sum()
    cs_size = cs_enrolled / cs_classes if cs_classes > 0 else np.nan
    
    naive_roster = 5 * ptr if pd.notnull(ptr) else np.nan
    core_roster = 5 * cm_size if pd.notnull(cm_size) else np.nan
    wedge = core_roster - naive_roster if pd.notnull(core_roster) and pd.notnull(naive_roster) else np.nan
    
    records.append({
        "school_year": yr,
        "nces_school_id": nces_id,
        "school_name": sch_name,
        "district_name": dist_name,
        "state": state,
        "enrollment": enr,
        "building_ptr": ptr,
        "core_math_size": cm_size,
        "adv_math_size": am_size,
        "core_sci_size": cs_size,
        "core_math_roster": core_roster,
        "naive_roster": naive_roster,
        "roster_wedge": wedge
    })

hist_df = pd.DataFrame(records)

# Filter for key urban schools
urban_schools = [
    "LINCOLN COLLEGE PREP.",
    "GRANDVIEW SR. HIGH",
    "RUSKIN HIGH SCHOOL",
    "CENTER SR. HIGH",
    "EAST HIGH SCHOOL",
    "NORTHEAST HIGH",
    "Wyandotte High"
]

sub = hist_df[hist_df["school_name"].isin(urban_schools)].sort_values(["school_name", "school_year"])
print("=== HISTORICAL TRENDS IN CORE MATH CLASS SIZE & ROSTER WEDGE ===")
for sch, g in sub.groupby("school_name"):
    print(f"\n--- {sch} ({g['district_name'].iloc[0]}) ---")
    for _, r in g.iterrows():
        print(f"  {r['school_year']} | PTR: {r['building_ptr']:4.1f} | Core Math Size: {r['core_math_size']:4.1f} | Adv Math: {r['adv_math_size']:4.1f} | Core Roster (5p): {r['core_math_roster']:5.1f} | Naive: {r['naive_roster']:4.1f} | Wedge: {r['roster_wedge']:+5.1f}")

hist_df.to_csv("outputs/tables/task006_urban_historical_course_trends.csv", index=False)
print("\nSaved historical trends to outputs/tables/task006_urban_historical_course_trends.csv")
