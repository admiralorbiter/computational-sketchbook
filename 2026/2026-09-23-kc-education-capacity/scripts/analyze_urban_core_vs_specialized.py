import pandas as pd
import numpy as np

# Load CRDC long course aggregates
df = pd.read_csv("data/processed/kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv")

# Filter for High schools in the most recent wave (2023-24)
latest_year = df["school_year"].max()
hs_latest = df[(df["school_year"] == latest_year) & (df["school_level"] == "High")].copy()

# Categorize courses into Core vs Advanced
core_math = ["alg1", "geom", "alg2"]
adv_math = ["advm", "calc"]
core_sci = ["bio", "chem"]
adv_sci = ["phys"]

# Aggregate by school and course category
records = []
for (nces_id, sch_name, dist_name, state, locale), g in hs_latest.groupby(
    ["nces_school_id", "school_name", "district_name", "state", "locale_group"]
):
    enr = g["enrollment_k12"].iloc[0]
    fte = g["classroom_teacher_fte"].iloc[0]
    ptr = g["school_ptr"].iloc[0]
    
    # Core Math
    cm = g[g["course_code"].isin(core_math)]
    cm_classes = cm["num_classes"].sum()
    cm_enrolled = cm["num_enrolled"].sum()
    cm_size = cm_enrolled / cm_classes if cm_classes > 0 else np.nan
    
    # Advanced Math
    am = g[g["course_code"].isin(adv_math)]
    am_classes = am["num_classes"].sum()
    am_enrolled = am["num_enrolled"].sum()
    am_size = am_enrolled / am_classes if am_classes > 0 else np.nan
    
    # Core Science
    cs = g[g["course_code"].isin(core_sci)]
    cs_classes = cs["num_classes"].sum()
    cs_enrolled = cs["num_enrolled"].sum()
    cs_size = cs_enrolled / cs_classes if cs_classes > 0 else np.nan
    
    # Physics / Adv Science
    ps = g[g["course_code"].isin(adv_sci)]
    ps_classes = ps["num_classes"].sum()
    ps_enrolled = ps["num_enrolled"].sum()
    ps_size = ps_enrolled / ps_classes if ps_classes > 0 else np.nan
    
    # Roster loads under standard 5-period teaching assignment
    naive_roster = 5 * ptr if pd.notnull(ptr) else np.nan
    core_math_roster = 5 * cm_size if pd.notnull(cm_size) else np.nan
    core_sci_roster = 5 * cs_size if pd.notnull(cs_size) else np.nan
    adv_math_roster = 5 * am_size if pd.notnull(am_size) else np.nan
    
    math_wedge = core_math_roster - naive_roster if pd.notnull(core_math_roster) and pd.notnull(naive_roster) else np.nan
    
    records.append({
        "nces_school_id": nces_id,
        "school_name": sch_name,
        "district_name": dist_name,
        "state": state,
        "locale_group": locale,
        "enrollment": enr,
        "teacher_fte": fte,
        "building_ptr": ptr,
        "core_math_classes": cm_classes,
        "core_math_enrolled": cm_enrolled,
        "core_math_size": cm_size,
        "adv_math_classes": am_classes,
        "adv_math_enrolled": am_enrolled,
        "adv_math_size": am_size,
        "core_sci_classes": cs_classes,
        "core_sci_enrolled": cs_enrolled,
        "core_sci_size": cs_size,
        "adv_sci_classes": ps_classes,
        "adv_sci_enrolled": ps_enrolled,
        "adv_sci_size": ps_size,
        "naive_roster_5p": naive_roster,
        "core_math_roster_5p": core_math_roster,
        "core_sci_roster_5p": core_sci_roster,
        "adv_math_roster_5p": adv_math_roster,
        "math_roster_wedge": math_wedge
    })

res_df = pd.DataFrame(records)

# Save intermediate summary
res_df.to_csv("outputs/tables/task006_urban_core_vs_specialized_summary.csv", index=False)
print(f"Generated task006_urban_core_vs_specialized_summary.csv with {len(res_df)} high schools.")

# Filter for urban inner-city schools
urban_districts = ["KANSAS CITY 33", "HICKMAN MILLS C-1", "CENTER 58", "GRANDVIEW C-4", "Kansas City"]
urban_hs = res_df[res_df["district_name"].isin(urban_districts)].sort_values("enrollment", ascending=False)

print("\n=== INNER-CITY KANSAS CITY HIGH SCHOOLS (2023-24) ===")
cols_show = ["school_name", "district_name", "enrollment", "building_ptr", "core_math_size", "adv_math_size", "core_sci_size", "core_math_roster_5p", "naive_roster_5p", "math_roster_wedge"]
print(urban_hs[cols_show].to_string(index=False))

print("\n=== REGIONAL SUMMARY BY LOCALE GROUP ===")
locale_grp = res_df.groupby("locale_group").agg({
    "building_ptr": "mean",
    "core_math_size": "mean",
    "adv_math_size": "mean",
    "core_sci_size": "mean",
    "adv_sci_size": "mean",
    "core_math_roster_5p": "mean",
    "naive_roster_5p": "mean",
    "math_roster_wedge": "mean"
}).round(1)
print(locale_grp.to_string())
