"""
Generate Visual Evidence Packet for EDU-003 Reported Classroom Teacher FTE:
- Figure 12: National & Regional Teacher FTE Trajectories (2014-15 to 2024-25, Indexed)
- Figure 13: Fixed-Plant Staffing Stickiness in Declining Districts (28 Balanced LEAs)
- Figure 14: The Secondary Staffing Wedge — Macro School PTR vs. Actual Course Class Sizes (CRDC)
"""

import os
import shutil
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Styling configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, sans-serif'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

# Path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KC_DIR = os.path.join(os.path.dirname(BASE_DIR), "2026-09-23-kc-education-capacity")

output_dir = os.path.join(BASE_DIR, "dashboard")
artifact_dir = r"C:\Users\admir\.gemini\antigravity\brain\341419bd-5669-4622-8d51-d6eecec301ff"
os.makedirs(output_dir, exist_ok=True)

# Data paths
sch_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_capacity_long_2014_15_2024_25.csv"))
lea_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_lea_capacity_long_2014_15_2024_25.csv"))
crdc_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_crdc_school_course_capacity_2013_14_2023_24.csv"))

# Balanced 75 cohort
leas_1415 = set(lea_long[(lea_long['school_year']=='2014-2015') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
leas_2425 = set(lea_long[(lea_long['school_year']=='2024-2025') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
balanced_leas = sorted(list(leas_1415.intersection(leas_2425)))

# -------------------------------------------------------------
# FIGURE 12: NATIONAL & REGIONAL TEACHER FTE TRAJECTORIES
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6), dpi=300)

# Balanced 75 series
bal_df = lea_long[lea_long['nces_lea_id'].isin(balanced_leas)].groupby('school_year')[['teachers_k12_fte', 'enrollment_k12']].sum()
years_full = bal_df.index.values
years_labels = [y.replace("20", "20", 1).replace("-20", "-") for y in years_full]

kc_tch_bal = bal_df['teachers_k12_fte'].values
kc_tch_bal_idx = kc_tch_bal / kc_tch_bal[0] * 100

# Interpolate / adjust 2015-16 for Kansas non-reporting anomaly (Olathe + Gardner Edgerton ~ 2,311 FTE)
kc_tch_adj = kc_tch_bal.copy()
# 2015-16 index is 1
kc_tch_adj[1] = (kc_tch_adj[0] + kc_tch_adj[2]) / 2.0  # Linear interpolation for clean series
kc_tch_adj_idx = kc_tch_adj / kc_tch_adj[0] * 100

# US National Public Teachers in thousands (from NCES Digest Table 208.20)
# 2014 through 2021 are reported CCD; 2022 to 2024 are NCES projections
us_teachers = np.array([
    3132.351, 3151.497, 3169.499, 3169.750, 3169.762,
    3198.170, 3195.800, 3214.242, 3176.361, 3181.310, 3200.052
])
us_tch_idx = us_teachers / us_teachers[0] * 100

# Plot series
ax.plot(years_labels, kc_tch_adj_idx, marker='o', color='#0284c7', linewidth=2.6, markersize=6.5, label='Kansas City Metro (Balanced 75 LEAs, Adjusted for 2015 KS Gap)')
ax.plot(years_labels, kc_tch_bal_idx, marker='x', color='#94a3b8', linewidth=1.5, linestyle=':', markersize=6, label='Kansas City Metro (Unadjusted Raw CCD, Showing 2015-16 KS Reporting Break)')
ax.plot(years_labels[:8], us_tch_idx[:8], marker='s', color='#0f172a', linewidth=2.2, markersize=5.5, label='United States Total Public Teachers (NCES Digest Table 208.20 Reported)')
ax.plot(years_labels[7:], us_tch_idx[7:], marker='^', color='#64748b', linewidth=2.0, linestyle='--', markersize=5.5, label='United States Total Public Teachers (NCES Projection Model)')

# Highlight 2015-16 anomaly
ax.scatter([years_labels[1]], [kc_tch_bal_idx[1]], color='#e11d48', s=90, zorder=6)
ax.annotate("2015-16 KS Reporting Artifact\nOlathe & Gardner Edgerton missing in CCD\n(-2,311 FTE artificial drop)",
            xy=(years_labels[1], kc_tch_bal_idx[1]),
            xytext=(1.2, 85.0),
            arrowprops=dict(arrowstyle="->", color='#e11d48', lw=1.5),
            fontsize=8.5, fontweight='bold', color='#be123c',
            bbox=dict(boxstyle="round,pad=0.4", fc="#fff1f2", ec="#f43f5e", lw=1))

# Highlight Fall 2020 pandemic resilience
ax.scatter([years_labels[6]], [kc_tch_adj_idx[6]], color='#059669', s=80, zorder=6)
ax.annotate("Fall 2020 Pandemic Freeze\nKC staffing held steady (+0.7%)\nEnrollment dropped -2.4% -> PTR fell",
            xy=(years_labels[6], kc_tch_adj_idx[6]),
            xytext=(4.5, 110.5),
            arrowprops=dict(arrowstyle="->", color='#059669', lw=1.5),
            fontsize=8.5, fontweight='bold', color='#047857',
            bbox=dict(boxstyle="round,pad=0.4", fc="#ecfdf5", ec="#10b981", lw=1))

# Final endpoints annotation
ax.annotate(f"KC Metro 10-Yr Adjusted: +8.88% (+1,917 FTE)\nUS National 10-Yr: +2.16%",
            xy=(years_labels[-1], kc_tch_adj_idx[-1]),
            xytext=(7.2, 103.5),
            fontsize=8.5, fontweight='bold', color='#0369a1',
            bbox=dict(boxstyle="round,pad=0.4", fc="#f0f9ff", ec="#0284c7", lw=1))

ax.set_title("Longitudinal Classroom Teacher FTE Trajectory: Kansas City vs. United States (2014–15 to 2024–25)", fontsize=13, fontweight='bold', pad=15)
ax.set_ylabel("Teacher FTE Index (2014–15 = 100)", fontsize=10, fontweight='bold')
ax.set_xlabel("School Year of Reference", fontsize=10, fontweight='bold')
ax.set_ylim(80, 115)
ax.axhline(100, color='#64748b', linestyle='--', linewidth=0.8, alpha=0.7)
ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)

# Provenance footer
prov_text = (
    "Observatory Visual Provenance:\n"
    "• Measure IDs: EDU-003 (Reported Classroom Teacher FTE), EDU-001 (PTR)\n"
    "• Sources: NCES Common Core of Data (CCD) LEA Non-Fiscal Surveys (SY 2014-15 to 2024-25); NCES Digest Table 208.20 (2022)\n"
    "• Target Population: Balanced 75 Fully Regional Kansas City LEAs vs. US Public Elementary/Secondary Total\n"
    "• Figure Classification: CROSS-SOURCE BENCHMARK COMPARISON & DATA INTEGRITY AUDIT\n"
    "• Pipeline: analysis/cross-measure/generate_edu003_visuals.py | Observatory Standard: Source != Field != Operationalization != Claim"
)
fig.text(0.08, -0.10, prov_text, fontsize=7.2, color='#475569', family='monospace', bbox=dict(boxstyle='square,pad=0.5', fc='#f8fafc', ec='#cbd5e1', lw=0.6))

plt.tight_layout()
fig12_path = os.path.join(output_dir, "fig12_kc_vs_us_teacher_trajectory.png")
fig.savefig(fig12_path, bbox_inches='tight', dpi=300)
shutil.copy(fig12_path, os.path.join(artifact_dir, "fig12_kc_vs_us_teacher_trajectory.png"))
plt.close(fig)
print(f"Saved: {fig12_path}")

# -------------------------------------------------------------
# FIGURE 13: FIXED-PLANT STAFFING STICKINESS IN DECLINING DISTRICTS
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300, gridspec_kw={'width_ratios': [1.2, 1]})

# Data for 28 declining districts with unchanged plant
categories = ['K-12\nEnrollment', 'Classroom\nTeachers', 'School & District\nAdministrators', 'Total Non-Teaching\nSupport Staff']
aggregate_pcts = [-8.33, -3.63, -9.78, +9.41]
bar_colors = ['#ef4444', '#f59e0b', '#dc2626', '#3b82f6']

bars = ax1.bar(categories, aggregate_pcts, color=bar_colors, width=0.55, edgecolor='#334155', linewidth=1)
ax1.axhline(0, color='#334155', linewidth=1.2)
ax1.set_ylim(-15, 15)
ax1.set_ylabel("10-Year Percent Change (2014–15 to 2024–25)", fontsize=9.5, fontweight='bold')
ax1.set_title("A. Aggregate Staffing Elasticity (N = 28 Declining LEAs)", fontsize=11, fontweight='bold', pad=12)

for bar, val in zip(bars, aggregate_pcts):
    yval = bar.get_height()
    va = 'bottom' if yval >= 0 else 'top'
    offset = 0.5 if yval >= 0 else -0.5
    sign = "+" if val > 0 else ""
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + offset, f"{sign}{val:.1f}%", ha='center', va=va, fontsize=9.5, fontweight='bold')

ax1.text(0.5, 0.05, "Fixed physical plants create staffing stickiness:\nClassroom teachers contract at < half the rate of enrollment (-3.6% vs -8.3%).\nNon-teaching support staff expands aggressively (+9.4%).",
         transform=ax1.transAxes, ha='center', fontsize=8.5, style='italic',
         bbox=dict(boxstyle="round,pad=0.4", fc="#f8fafc", ec="#cbd5e1", lw=0.8))

# Panel B: Big 8 Decliners (>200 loss) with unchanged school counts
big_decliners = [
    ("Fort Leavenworth", -21.7, +0.2),
    ("Hogan Prep", -21.7, +6.2),
    ("Grandview C-4", -16.5, -9.4),
    ("Harrisonville", -14.9, -12.7),
    ("Paola", -11.4, -20.1),
    ("Center 58", -8.8, -6.1),
    ("Bonner Springs", -8.1, +0.7),
    ("Kansas City KS", -4.5, -2.8)
]

districts = [d[0] for d in big_decliners]
enr_vals = [d[1] for d in big_decliners]
tch_vals = [d[2] for d in big_decliners]

y_pos = np.arange(len(districts))
h = 0.35

ax2.barh(y_pos + h/2, enr_vals, height=h, color='#ef4444', label='K-12 Enrollment % Change', edgecolor='#334155', linewidth=0.8)
ax2.barh(y_pos - h/2, tch_vals, height=h, color='#0284c7', label='Teacher FTE % Change', edgecolor='#334155', linewidth=0.8)
ax2.axvline(0, color='#334155', linewidth=1.0)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(districts, fontsize=9, fontweight='bold')
ax2.invert_yaxis()
ax2.set_xlabel("Percent Change (2014–15 to 2024–25)", fontsize=9.5, fontweight='bold')
ax2.set_title("B. Staffing Contraction vs. Stickiness (Decliners > 200)", fontsize=11, fontweight='bold', pad=12)
ax2.legend(loc='lower left', fontsize=8.5, frameon=True, facecolor='white', framealpha=0.9)

fig.suptitle("The Fixed-Plant Staffing Penalty: Downward Stickiness & Overhead Expansion in Declining Districts", fontsize=13, fontweight='bold', y=0.98)

# Provenance footer
prov_text = (
    "Observatory Visual Provenance:\n"
    "• Measure IDs: EDU-003 (Reported Classroom Teacher FTE), EDU-002 (Headcount Enrollment), EDU-005 (Paraprofessional FTE)\n"
    "• Sources: NCES Common Core of Data (CCD) School and LEA Universe Panels (SY 2014-15 to 2024-25)\n"
    "• Target Population: Balanced 75 Cohort LEAs experiencing negative enrollment change with zero net change in operating school count (N=28)\n"
    "• Figure Classification: EMPIRICAL ORGANIZATIONAL DYNAMICS & HYPOTHESIS TESTING\n"
    "• Pipeline: analysis/cross-measure/generate_edu003_visuals.py | Key Finding: Overhead does not cut instructional staffing; teachers remain sticky downward."
)
fig.text(0.06, -0.12, prov_text, fontsize=7.2, color='#475569', family='monospace', bbox=dict(boxstyle='square,pad=0.5', fc='#f8fafc', ec='#cbd5e1', lw=0.6))

plt.tight_layout()
fig13_path = os.path.join(output_dir, "fig13_fixed_plant_staffing_stickiness.png")
fig.savefig(fig13_path, bbox_inches='tight', dpi=300)
shutil.copy(fig13_path, os.path.join(artifact_dir, "fig13_fixed_plant_staffing_stickiness.png"))
plt.close(fig)
print(f"Saved: {fig13_path}")

# -------------------------------------------------------------
# FIGURE 14: THE SECONDARY STAFFING WEDGE (MACRO PTR VS CLASS SIZES)
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300, gridspec_kw={'width_ratios': [1.1, 1]})

# Panel A: Subject-by-Subject Class Size vs Macro PTR in CRDC 2023-24
subjects_data = [
    ('Algebra I', 19.28, +4.53),
    ('Geometry', 18.94, +4.06),
    ('Algebra II', 18.92, +3.79),
    ('Biology', 18.81, +3.96),
    ('Chemistry', 18.87, +3.46),
    ('Physics', 17.31, +1.92),
    ('Calculus', 14.97, -0.53)
]

subj_names = [s[0] for s in subjects_data]
class_sizes = [s[1] for s in subjects_data]
wedges = [s[2] for s in subjects_data]
macro_ptr_mean = 14.74

x = np.arange(len(subj_names))
bars1 = ax1.bar(x, class_sizes, color='#3b82f6', width=0.55, edgecolor='#1e293b', linewidth=0.8, label='Actual Derived Course Class Size (EDU-012)')
ax1.axhline(macro_ptr_mean, color='#e11d48', linestyle='--', linewidth=1.8, label=f'Macro School PTR Baseline = {macro_ptr_mean:.2f} (EDU-001)')

ax1.set_xticks(x)
ax1.set_xticklabels(subj_names, rotation=30, ha='right', fontsize=9, fontweight='bold')
ax1.set_ylabel("Students per Class / Ratio", fontsize=9.5, fontweight='bold')
ax1.set_title("A. Secondary Course Class Sizes vs. School PTR (CRDC 2023–24, N=109)", fontsize=11, fontweight='bold', pad=12)
ax1.set_ylim(0, 24)
ax1.legend(loc='lower left', fontsize=8.5, frameon=True, facecolor='white', framealpha=0.9)

for bar, w in zip(bars1, wedges):
    h_val = bar.get_height()
    sign = "+" if w > 0 else ""
    color = "#15803d" if w > 0 else "#be123c"
    ax1.text(bar.get_x() + bar.get_width()/2.0, h_val + 0.4, f"{h_val:.1f}\n({sign}{w:.1f})", ha='center', va='bottom', fontsize=8, fontweight='bold', color=color)

# Panel B: Longitudinal Wedge Stability across CRDC Waves (2013-14 to 2023-24)
waves = ['2013-14', '2015-16', '2017-18', '2020-21', '2021-22', '2023-24']
ptrs = [15.90, 15.49, 15.18, 15.19, 14.88, 14.74]
alg1_cs = [18.82, 20.64, 18.21, 17.67, 18.64, 19.28]

ax2.plot(waves, alg1_cs, marker='o', color='#2563eb', linewidth=2.4, markersize=6, label='Algebra I Mean Class Size (EDU-012)')
ax2.plot(waves, ptrs, marker='s', color='#e11d48', linewidth=2.0, linestyle='--', markersize=5.5, label='Macro School PTR (EDU-001 = EDU-002 / EDU-003)')
ax2.fill_between(waves, ptrs, alg1_cs, color='#bfdbfe', alpha=0.4, label='The Structural Staffing Wedge (Δ ≈ +2.4 to +5.2)')

for i, txt in enumerate([f"+{c - p:.2f}" for c, p in zip(alg1_cs, ptrs)]):
    ax2.annotate(txt, (waves[i], (alg1_cs[i] + ptrs[i])/2), textcoords="offset points", xytext=(0, 5), ha='center', fontsize=8, fontweight='bold', color='#1d4ed8')

ax2.set_ylabel("Students per Classroom / Ratio", fontsize=9.5, fontweight='bold')
ax2.set_xlabel("CRDC Wave", fontsize=9.5, fontweight='bold')
ax2.set_title("B. 10-Year Longitudinal Persistence of the Staffing Wedge", fontsize=11, fontweight='bold', pad=12)
ax2.set_ylim(10, 24)
ax2.legend(loc='lower right', fontsize=8.5, frameon=True, facecolor='white', framealpha=0.9)

fig.suptitle("The Secondary Staffing Wedge: Why Macro Pupil/Teacher Ratios Mechanically Understate Course Class Sizes", fontsize=13, fontweight='bold', y=0.98)

# Provenance footer
prov_text = (
    "Observatory Visual Provenance:\n"
    "• Measure IDs: EDU-003 (Reported Classroom Teacher FTE), EDU-001 (PTR), EDU-006 (Course Enrollment), EDU-011 (Class Count), EDU-012 (Derived Class Size)\n"
    "• Sources: Civil Rights Data Collection (CRDC) 2013-14 through 2023-24 matched to NCES CCD School Universe\n"
    "• Target Population: Kansas City Regional Regular Operating High Schools (N=109 in 2023-24)\n"
    "• Figure Classification: CROSS-SOURCE CONTRAST & STRUCTURAL DECOMPOSITION\n"
    "• Pipeline: analysis/cross-measure/generate_edu003_visuals.py | Key Finding: Core foundational classes exceed PTR by 3.5 to 4.5 students."
)
fig.text(0.06, -0.12, prov_text, fontsize=7.2, color='#475569', family='monospace', bbox=dict(boxstyle='square,pad=0.5', fc='#f8fafc', ec='#cbd5e1', lw=0.6))

plt.tight_layout()
fig14_path = os.path.join(output_dir, "fig14_secondary_staffing_wedge.png")
fig.savefig(fig14_path, bbox_inches='tight', dpi=300)
shutil.copy(fig14_path, os.path.join(artifact_dir, "fig14_secondary_staffing_wedge.png"))
plt.close(fig)
print(f"Saved: {fig14_path}")

print("\nALL THREE EDU-003 FIGURES GENERATED SUCCESSFULLY.")
