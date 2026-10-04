"""
Generate 4 publication quality figures by school for Kansas City secondary classroom capacity:
1. fig_kc01_school_course_profiles.png: Multi-school course profile cards (14 schools)
2. fig_kc02_parent_reality_check_wedge.png: Advertised PTR vs. Actual Core Class Size (Parent perspective)
3. fig_kc03_curriculum_hierarchy_by_school.png: Gateway Core vs. Advanced STEM internal tracking
4. fig_kc04_upper_tail_crowding_by_school.png: Percentage of classes with >=25 and >=30 students
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_DIR = Path(r"C:\Users\admir\Github\computational-sketchbook\2026\2026-10-04-classroom-capacity")
ARTIFACTS_DIR = PROJECT_DIR / "artifacts" / "figures"
BRAIN_DIR = Path(r"C:\Users\admir\.gemini\antigravity\brain\e2a39054-593a-4978-894c-4e35b96a61cb")
CSV_PATH = PROJECT_DIR / "data" / "processed" / "crdc_kc_metro_panel.csv"

ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
BRAIN_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV_PATH, low_memory=False)
df_clean = df[(df["mean_class_size"] > 0) & (df["mean_class_size"] <= 60)].copy()

# Filter to 2023-24 wave
df23 = df_clean[df_clean["crdc_wave"] == "2023-24"].copy()

# Select 14 iconic focal high schools across sectors
focal_schools = [
    ("Urban Core KCPS", "LINCOLN COLLEGE PREPARATORY ACADEMY", "Lincoln College Prep"),
    ("Urban Core KCPS", "CENTRAL HIGH SCHOOL", "Central High"),
    ("Urban Core KCPS", "EAST HIGH SCHOOL", "East High"),
    ("Urban Core KCPS", "NORTHEAST HIGH", "Northeast High"),
    ("Urban Charters", "UNIVERSITY ACADEMY-UPPER", "University Academy"),
    ("Urban Charters", "EWING MARION KAUFFMAN HIGH", "Kauffman School"),
    ("Urban KCKPS", "SUMNER ACADEMY OF ARTS & SCIENCE", "Sumner Academy"),
    ("Urban KCKPS", "WYANDOTTE HIGH", "Wyandotte High"),
    ("Suburban Johnson Co.", "SHAWNEE MISSION EAST HIGH", "SM East High"),
    ("Suburban Johnson Co.", "BLUE VALLEY NORTHWEST HIGH", "BV Northwest High"),
    ("Suburban Northland", "OAK PARK HIGH", "Oak Park High"),
    ("Suburban Northland", "STALEY HIGH", "Staley High"),
    ("Suburban Eastern Jackson", "BLUE SPRINGS HIGH", "Blue Springs High"),
    ("Suburban Eastern Jackson", "LEE'S SUMMIT WEST HIGH", "Lee's Summit West")
]

focal_names = [f[1] for f in focal_schools]
focal_labels = {f[1]: f[2] for f in focal_schools}
focal_sectors = {f[1]: f[0] for f in focal_schools}

df_focal = df23[df23["school_name"].isin(focal_names)].copy()
df_focal["short_label"] = df_focal["school_name"].map(focal_labels)
df_focal["sector_label"] = df_focal["school_name"].map(focal_sectors)

print(f"Matched {len(df_focal)} records across {df_focal['school_name'].nunique()} schools.")

# -------------------------------------------------------------
# FIGURE 1: School-by-School Multi-Course Profiles
# -------------------------------------------------------------
courses_core = ["Algebra I", "Geometry", "Algebra II", "Biology", "Chemistry", "Physics", "Calculus"]
palette_courses = sns.color_palette("tab10", len(courses_core))
course_colors = dict(zip(courses_core, palette_courses))

fig, axes = plt.subplots(4, 4, figsize=(18, 14), sharey=True, sharex=True, dpi=200)
axes = axes.flatten()

all_unique_focal = [f[2] for f in focal_schools]
for i, sname in enumerate(all_unique_focal):
    ax = axes[i]
    sub = df_focal[df_focal["short_label"] == sname].set_index("course_name")
    school_ptr = sub["school_ptr"].dropna().iloc[0] if "school_ptr" in sub.columns and len(sub["school_ptr"].dropna()) > 0 else np.nan
    sec_label = sub["sector_label"].iloc[0] if len(sub) > 0 else ""
    
    vals = [sub.loc[c, "mean_class_size"] if c in sub.index else 0 for c in courses_core]
    bars = ax.barh(courses_core, vals, color=[course_colors[c] for c in courses_core], alpha=0.85, edgecolor="black", height=0.6)
    
    # Add PTR line
    if pd.notna(school_ptr):
        ax.axvline(school_ptr, color="crimson", linestyle="--", linewidth=1.5, label=f"PTR: {school_ptr:.1f}:1")
    
    ax.axvline(25, color="darkorange", linestyle=":", linewidth=1.2, label="25 Crowding")
    ax.set_title(f"{sname}\n({sec_label})", fontsize=11, fontweight="bold")
    ax.set_xlim(0, 36)
    
    # Value labels on bars
    for bar, val in zip(bars, vals):
        if val > 0:
            ax.text(val + 0.6, bar.get_y() + bar.get_height()/2, f"{val:.1f}", va="center", ha="left", fontsize=9, fontweight="semibold")

# Hide extra axes
for j in range(len(all_unique_focal), len(axes)):
    fig.delaxes(axes[j])

axes[0].legend(loc="lower right", fontsize=8)
fig.suptitle("School-by-School Secondary Course Class Size Profiles (Kansas City Metro, SY 2023–24)\n[Bars = Mean Section Size | Red Dashed Line = School Pupil/Teacher Ratio]", fontsize=16, fontweight="bold", y=0.99)
plt.tight_layout()

p1 = ARTIFACTS_DIR / "fig_kc01_school_course_profiles.png"
p1_brain = BRAIN_DIR / "fig_kc01_school_course_profiles.png"
plt.savefig(p1, bbox_inches="tight")
plt.savefig(p1_brain, bbox_inches="tight")
plt.close()
print("Saved Fig 1:", p1)

# -------------------------------------------------------------
# FIGURE 2: Parent Reality Check: Advertised PTR vs Core Class Size
# -------------------------------------------------------------
plt.figure(figsize=(12, 8), dpi=200)

core_mask = df_focal["course_name"].isin(["Algebra I", "Geometry", "Algebra II", "Biology", "Chemistry"])
school_comp = df_focal[core_mask].groupby(["short_label", "sector_label"]).agg(
    core_mean=("mean_class_size", "mean"),
    school_ptr=("school_ptr", "first")
).reset_index().dropna()

school_comp["wedge"] = school_comp["core_mean"] - school_comp["school_ptr"]
school_comp = school_comp.sort_values("core_mean", ascending=True)

y_pos = np.arange(len(school_comp))

# Dumbbell plot
plt.hlines(y=y_pos, xmin=school_comp["school_ptr"], xmax=school_comp["core_mean"], color="gray", alpha=0.6, linewidth=2.5)
plt.scatter(school_comp["school_ptr"], y_pos, color="#2980B9", s=110, label="Advertised School PTR (Staffing Ratio)", zorder=3, edgecolor="black")
plt.scatter(school_comp["core_mean"], y_pos, color="#C0392B", s=130, label="Actual Core Class Size (Encountered by Student)", zorder=3, edgecolor="black")

for i, row in school_comp.reset_index(drop=True).iterrows():
    plt.text(row["core_mean"] + 0.6, i, f"{row['core_mean']:.1f} (+{row['wedge']:.1f})", va="center", ha="left", fontsize=9.5, fontweight="bold", color="#900C3F")
    plt.text(row["school_ptr"] - 0.6, i, f"{row['school_ptr']:.1f}:1", va="center", ha="right", fontsize=9, color="#1B4F72")

plt.yticks(y_pos, school_comp["short_label"] + "  [" + school_comp["sector_label"] + "]", fontsize=10.5)
plt.xlabel("Students per Teacher / Section Size", fontsize=12, fontweight="semibold")
plt.title("The Parent's Reality Check: Advertised School PTR vs. Actual Core Classroom Size\nKansas City High Schools (SY 2023–24)", fontsize=14, fontweight="bold", pad=15)
plt.axvline(20, color="gray", linestyle=":", alpha=0.5)
plt.axvline(25, color="red", linestyle="--", alpha=0.7, label="Crowding Threshold (25+ Students)")
plt.xlim(8, 36)
plt.legend(loc="lower right", frameon=True, fontsize=10)
plt.tight_layout()

p2 = ARTIFACTS_DIR / "fig_kc02_parent_reality_check_wedge.png"
p2_brain = BRAIN_DIR / "fig_kc02_parent_reality_check_wedge.png"
plt.savefig(p2, bbox_inches="tight")
plt.savefig(p2_brain, bbox_inches="tight")
plt.close()
print("Saved Fig 2:", p2)

# -------------------------------------------------------------
# FIGURE 3: Curriculum Hierarchy Within Schools (Core vs Advanced)
# -------------------------------------------------------------
plt.figure(figsize=(12, 7), dpi=200)

tracking_data = []
for sname in school_comp["short_label"]:
    sub = df_focal[df_focal["short_label"] == sname]
    core_avg = sub[sub["course_name"].isin(["Algebra I", "Geometry", "Biology"])]["mean_class_size"].mean()
    adv_avg = sub[sub["course_name"].isin(["Calculus", "Physics", "Advanced Mathematics"])]["mean_class_size"].mean()
    if pd.notna(core_avg) and pd.notna(adv_avg):
        tracking_data.append({
            "school": sname,
            "core": core_avg,
            "adv": adv_avg,
            "drop": core_avg - adv_avg
        })

df_track = pd.DataFrame(tracking_data).sort_values("drop", ascending=True)

y = np.arange(len(df_track))
plt.hlines(y=y, xmin=df_track["adv"], xmax=df_track["core"], color="purple", alpha=0.5, linewidth=2.5)
plt.scatter(df_track["core"], y, color="#D35400", s=110, label="9th/10th Grade Gateway Core (Algebra I, Geometry, Biology)", edgecolor="black", zorder=3)
plt.scatter(df_track["adv"], y, color="#27AE60", s=110, label="11th/12th Grade Advanced STEM (Calculus, Physics, Adv Math)", edgecolor="black", zorder=3)

for i, row in df_track.reset_index(drop=True).iterrows():
    plt.text(row["core"] + 0.5, i, f"{row['core']:.1f}", va="center", ha="left", fontsize=9, fontweight="bold", color="#D35400")
    plt.text(row["adv"] - 0.5, i, f"{row['adv']:.1f}", va="center", ha="right", fontsize=9, fontweight="bold", color="#27AE60")
    plt.text((row["core"] + row["adv"])/2, i + 0.22, f"Δ = -{row['drop']:.1f}", va="bottom", ha="center", fontsize=8.5, fontstyle="italic", color="purple")

plt.yticks(y, df_track["school"], fontsize=10.5)
plt.xlabel("Average Section Size (Students / Class)", fontsize=12, fontweight="semibold")
plt.title("Curriculum Tracking & Resource Allocation Within the Same High School Building\nGateway Core vs. Advanced STEM Offerings (SY 2023–24)", fontsize=13, fontweight="bold", pad=15)
plt.axvline(20, color="gray", linestyle=":", alpha=0.5)
plt.axvline(25, color="red", linestyle="--", alpha=0.7)
plt.xlim(2, 35)
plt.legend(loc="lower right", frameon=True, fontsize=10)
plt.tight_layout()

p3 = ARTIFACTS_DIR / "fig_kc03_curriculum_hierarchy_by_school.png"
p3_brain = BRAIN_DIR / "fig_kc03_curriculum_hierarchy_by_school.png"
plt.savefig(p3, bbox_inches="tight")
plt.savefig(p3_brain, bbox_inches="tight")
plt.close()
print("Saved Fig 3:", p3)

# -------------------------------------------------------------
# FIGURE 4: Upper-Tail Crowding Exposure Risk by School
# -------------------------------------------------------------
plt.figure(figsize=(12, 7), dpi=200)

crowd_records = []
for sname in focal_labels.values():
    sub = df_focal[df_focal["short_label"] == sname]
    tot_offerings = len(sub)
    tot_seats = sub["num_enrolled"].sum()
    if tot_seats > 0:
        pct_seats_25 = 100 * sub.loc[sub["mean_class_size"] >= 25, "num_enrolled"].sum() / tot_seats
        pct_seats_30 = 100 * sub.loc[sub["mean_class_size"] >= 30, "num_enrolled"].sum() / tot_seats
        sec = sub["sector_label"].iloc[0]
        crowd_records.append({
            "school": sname,
            "sector": sec,
            "pct_25": pct_seats_25,
            "pct_30": pct_seats_30
        })

df_crowd = pd.DataFrame(crowd_records).sort_values("pct_25", ascending=True)

y = np.arange(len(df_crowd))
plt.barh(y, df_crowd["pct_25"], height=0.55, color="#F39C12", edgecolor="black", label="Enrolled in Classes Averaging ≥ 25 Students", alpha=0.85)
plt.barh(y, df_crowd["pct_30"], height=0.55, color="#C0392B", edgecolor="black", label="Enrolled in Severe Crowding (≥ 30 Students)", alpha=0.9)

for i, r in df_crowd.reset_index(drop=True).iterrows():
    if r["pct_25"] > 0:
        plt.text(r["pct_25"] + 1.2, i, f"{r['pct_25']:.0f}%", va="center", ha="left", fontsize=9, fontweight="bold")

plt.yticks(y, df_crowd["school"] + "  [" + df_crowd["sector"] + "]", fontsize=10)
plt.xlabel("Percentage of Enrolled Course Seats (%)", fontsize=12, fontweight="semibold")
plt.title("Crowding Exposure Risk by School: Share of Students in Classes ≥25 and ≥30\nKansas City Metropolitan High Schools (SY 2023–24)", fontsize=13, fontweight="bold", pad=15)
plt.xlim(0, 105)
plt.legend(loc="lower right", frameon=True, fontsize=10)
plt.tight_layout()

p4 = ARTIFACTS_DIR / "fig_kc04_upper_tail_crowding_by_school.png"
p4_brain = BRAIN_DIR / "fig_kc04_upper_tail_crowding_by_school.png"
plt.savefig(p4, bbox_inches="tight")
plt.savefig(p4_brain, bbox_inches="tight")
plt.close()
print("Saved Fig 4:", p4)

print("ALL 4 FIGURES GENERATED AND SAVED IN BOTH DIRECTORIES!")
