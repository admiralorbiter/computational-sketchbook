import pandas as pd
import numpy as np

# Load CRDC long course aggregates
df = pd.read_csv("data/processed/kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv")
latest_year = df["school_year"].max()
latest_hs = df[(df["school_year"] == latest_year) & (df["school_level"] == "High")].copy()

# Focus urban target schools
target_schools = [
    ("LINCOLN COLLEGE PREP.", "KANSAS CITY 33"),
    ("GRANDVIEW SR. HIGH", "GRANDVIEW C-4"),
    ("RUSKIN HIGH SCHOOL", "HICKMAN MILLS C-1"),
    ("CENTER SR. HIGH", "CENTER 58"),
    ("EAST HIGH SCHOOL", "KANSAS CITY 33"),
    ("Wyandotte High", "Kansas City")
]

# Teaching period regimes
# Most secondary schools operate a 7-period day (5 teaching) or 8-period A/B block (5 or 6 teaching)
# We test D = 5 as canonical (7-period day or 5 of 8 block) and D = 6 (6 of 8 block)
regimes = [
    {"name": "7-Period Day (5 Teaching, 2 Plan)", "periods": 7, "duty": 5, "multiplier": 1.40},
    {"name": "8-Period Block (6 Teaching, 2 Plan)", "periods": 8, "duty": 6, "multiplier": 1.333},
]

math_courses = ["alg1", "geom", "alg2", "advm", "calc"]
core_math = ["alg1", "geom", "alg2"]
adv_math = ["advm", "calc"]

reconstruction_rows = []

for sch_name, dist_name in target_schools:
    sch_data = latest_hs[(latest_hs["school_name"] == sch_name) & (latest_hs["district_name"] == dist_name)]
    if len(sch_data) == 0:
        continue
    
    row0 = sch_data.iloc[0]
    enr = row0["enrollment_k12"]
    fte = row0["classroom_teacher_fte"]
    ptr = row0["school_ptr"]
    state = row0["state"]
    
    # Math department courses
    math_data = sch_data[sch_data["course_code"].isin(math_courses)]
    
    # Department totals
    total_math_classes = math_data["num_classes"].sum()
    total_math_enrolled = math_data["num_enrolled"].sum()
    dept_mean_size = total_math_enrolled / total_math_classes if total_math_classes > 0 else np.nan
    
    # Core Math totals
    cm_data = sch_data[sch_data["course_code"].isin(core_math)]
    cm_classes = cm_data["num_classes"].sum()
    cm_enrolled = cm_data["num_enrolled"].sum()
    cm_mean_size = cm_enrolled / cm_classes if cm_classes > 0 else np.nan
    
    # Adv Math totals
    am_data = sch_data[sch_data["course_code"].isin(adv_math)]
    am_classes = am_data["num_classes"].sum()
    am_enrolled = am_data["num_enrolled"].sum()
    am_mean_size = am_enrolled / am_classes if am_classes > 0 else np.nan
    
    for reg in regimes:
        d = reg["duty"]
        p = reg["periods"]
        mu = reg["multiplier"]
        
        # Required math teachers
        req_math_fte = total_math_classes / d if total_math_classes > 0 else np.nan
        req_core_fte = cm_classes / d if cm_classes > 0 else np.nan
        
        # Roster loads
        naive_roster = d * ptr
        schedule_neutral_roster = d * (ptr * mu) # if PTR scaled purely by schedule
        dept_avg_roster = d * dept_mean_size if pd.notnull(dept_mean_size) else np.nan
        core_pure_roster = d * cm_mean_size if pd.notnull(cm_mean_size) else np.nan
        adv_pure_roster = d * am_mean_size if pd.notnull(am_mean_size) else np.nan
        
        # Mixed assignment: (d-1) core + 1 advanced
        mixed_roster = ((d - 1) * cm_mean_size + 1 * am_mean_size) if pd.notnull(cm_mean_size) and pd.notnull(am_mean_size) else core_pure_roster
        
        # Wedges relative to Naive PTR Roster
        # 1. Schedule Wedge: load increase due to teacher planning periods
        # 2. Tracking Wedge: load difference between core and department average
        # 3. Total Wedge: core load minus naive roster
        total_core_wedge = core_pure_roster - naive_roster if pd.notnull(core_pure_roster) else np.nan
        sched_wedge = dept_avg_roster - naive_roster if pd.notnull(dept_avg_roster) else np.nan
        tracking_wedge = core_pure_roster - dept_avg_roster if pd.notnull(core_pure_roster) and pd.notnull(dept_avg_roster) else np.nan
        
        # Percentage wedges
        pct_wedge = (total_core_wedge / naive_roster * 100) if pd.notnull(naive_roster) and naive_roster > 0 else np.nan
        
        # Integer bounds under MSIP cap 33
        # In Missouri MSIP standard, max class size is 33.
        # Minimal plausible section size for core is 15.
        min_feasible_roster = d * max(15.0, np.floor(cm_mean_size - 3))
        max_feasible_roster = d * min(33.0, np.ceil(cm_mean_size + 3))
        
        reconstruction_rows.append({
            "school_name": sch_name,
            "district_name": dist_name,
            "state": state,
            "enrollment": enr,
            "teacher_fte": fte,
            "building_ptr": ptr,
            "regime_name": reg["name"],
            "duty_periods": d,
            "total_periods": p,
            "schedule_multiplier": mu,
            "total_math_classes": total_math_classes,
            "total_math_enrolled": total_math_enrolled,
            "dept_mean_size": dept_mean_size,
            "core_math_classes": cm_classes,
            "core_math_enrolled": cm_enrolled,
            "core_math_size": cm_mean_size,
            "adv_math_classes": am_classes,
            "adv_math_enrolled": am_enrolled,
            "adv_math_size": am_mean_size,
            "req_math_teachers": req_math_fte,
            "naive_roster": naive_roster,
            "dept_avg_roster": dept_avg_roster,
            "core_pure_roster": core_pure_roster,
            "adv_pure_roster": adv_pure_roster,
            "mixed_roster": mixed_roster,
            "total_core_wedge": total_core_wedge,
            "schedule_wedge": sched_wedge,
            "tracking_wedge": tracking_wedge,
            "pct_core_wedge": pct_wedge,
            "min_feasible_roster": min_feasible_roster,
            "max_feasible_roster": max_feasible_roster
        })

recon_df = pd.DataFrame(reconstruction_rows)

recon_df.to_csv("outputs/tables/task006_urban_roster_reconstruction.csv", index=False)
print("Saved outputs/tables/task006_urban_roster_reconstruction.csv")

# Print summary table for canonical 5-period regime
canonical = recon_df[recon_df["duty_periods"] == 5]
cols_to_print = [
    "school_name", "district_name", "building_ptr", "core_math_size", "adv_math_size",
    "naive_roster", "core_pure_roster", "mixed_roster", "total_core_wedge", "pct_core_wedge"
]
print("\n=== RECONSTRUCTED ROSTER LOADS (CANONICAL 5-PERIOD TEACHING REGIME) ===")
print(canonical[cols_to_print].to_string(index=False))
