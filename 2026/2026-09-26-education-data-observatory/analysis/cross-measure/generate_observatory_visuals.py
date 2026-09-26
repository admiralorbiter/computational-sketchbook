import os
import shutil
import matplotlib.pyplot as plt
import numpy as np

# Set clean styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, sans-serif'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

output_dir = r"c:\Users\admir\Github\computational-sketchbook\2026\2026-09-26-education-data-observatory\dashboard"
artifact_dir = r"C:\Users\admir\.gemini\antigravity\brain\341419bd-5669-4622-8d51-d6eecec301ff"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------
# FIGURE 1: CROSS-SOURCE COMPARISON
# Macro Staffing Density (CCD) vs. Secondary Classroom Reality
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6.2), dpi=300)

jurisdictions = [
    "United States\n(National Benchmark)",
    "Missouri\n(Statewide)",
    "Kansas\n(Statewide)",
    "Shawnee Mission North\n(KC Suburb)",
    "Lincoln College Prep\n(KCPS Urban Core)"
]

# Exact sources and reference periods
macro_ptr = [15.4, 13.8, 13.6, 14.19, 17.25]
macro_sub = ["SY 2020–21 (CCD)", "SY 2020–21 (CCD)", "SY 2020–21 (CCD)", "SY 2021–22 (CCD)", "SY 2021–22 (CCD)"]

actual_class_size = [23.3, 22.5, 19.8, 25.71, 31.0]
actual_sub = ["SY 2017–18 (NTPS)", "SY 2017–18 (NTPS)", "SY 2017–18 (NTPS)", "SY 2021–22 (CRDC)", "SY 2021–22 (CRDC)"]
actual_label_names = ["NTPS Sec. Dept.", "NTPS Sec. Dept.", "NTPS Sec. Dept.", "CRDC Alg I Mean", "CRDC Geom Mean"]

gaps = [c - p for p, c in zip(macro_ptr, actual_class_size)]

x = np.arange(len(jurisdictions))
width = 0.35

rects1 = ax.bar(x - width/2, macro_ptr, width, label='Macro Staffing Ratio (CCD PTR)', color='#3b82f6', alpha=0.9, edgecolor='#1d4ed8')
rects2 = ax.bar(x + width/2, actual_class_size, width, label='Secondary Classroom Measure (NTPS Survey Mean / CRDC Course Mean)', color='#f59e0b', alpha=0.9, edgecolor='#b45309')

# Annotate values and gap
for i in range(len(jurisdictions)):
    # Macro annotation
    ax.annotate(f"{macro_ptr[i]:.1f}:1\n[{macro_sub[i]}]",
                xy=(x[i] - width/2, macro_ptr[i]), xytext=(0, 4),
                textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1e3a8a')
    # Actual annotation
    ax.annotate(f"{actual_class_size[i]:.1f}\n[{actual_sub[i]}]",
                xy=(x[i] + width/2, actual_class_size[i]), xytext=(0, 4),
                textcoords="offset points", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#78350f')
    # Draw gap annotation
    ax.annotate(f"+{gaps[i]:.1f} wedge",
                xy=(x[i], max(macro_ptr[i], actual_class_size[i]) + 4.2),
                ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#dc2626')

ax.set_ylabel('Students per Teacher FTE / Students per Class', fontsize=10.5, fontweight='semibold')
ax.set_title('[CROSS-SOURCE COMPARISON] Macro Staffing Density (CCD) vs. Secondary Classroom Class Size\nIllustrative Juxtaposition Across Multiple Independent Sources, Reference Periods & Estimands', fontsize=11.5, fontweight='bold', pad=18)
ax.set_xticks(x)
ax.set_xticklabels(jurisdictions, fontsize=9.5)
ax.set_ylim(0, 41)
ax.legend(frameon=True, facecolor='white', framealpha=0.95, loc='upper left', fontsize=9)

# Provenance and classification footer box
footer_text = (
    "CLASSIFICATION: CROSS-SOURCE COMPARISON (Not synchronous observations). Note: US National PTR (15.4:1) cited from Digest of Education Statistics 2022 (Table 208.20)\n"
    "because preliminary NCES 2024–25 Table 2 suppresses US total teacher FTE and national PTR. NTPS national benchmark is 23.3 (2017–18) and 21.0 (2020–21).\n"
    "CRDC observations are derived course means (enrollment / class count). Bars illustrate that macro PTR everywhere sits 6 to 14 students below secondary class rosters."
)
plt.figtext(0.5, 0.01, footer_text, ha="center", fontsize=7.5, color="#475569",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

plt.subplots_adjust(bottom=0.15)
fig1_path = os.path.join(output_dir, "fig01_macro_ptr_vs_actual_class_size.png")
plt.savefig(fig1_path)
plt.close()
shutil.copy(fig1_path, os.path.join(artifact_dir, "fig01_macro_ptr_vs_actual_class_size.png"))

# -------------------------------------------------------------
# FIGURE 2: DESCRIPTIVE OBSERVATION
# The KC 10-Year Capacity Paradox (SY 2014–15 to SY 2024–25)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.2), dpi=300)

categories = [
    "K–12 Student\nEnrollment",
    "Certified Teacher\nFTE",
    "Instructional\nParaprofessionals",
    "Regional Pooled\nPupil/Teacher Ratio"
]

pct_changes = [-0.73, +8.88, +11.85, -8.82]
raw_labels = ["-2,345 students", "+1,921.9 FTE", "+565.9 FTE", "14.85:1 -> 13.54:1"]
colors = ['#94a3b8', '#10b981', '#8b5cf6', '#3b82f6']

bars = ax.barh(categories, pct_changes, color=colors, height=0.55, edgecolor='#475569', linewidth=0.8)

ax.axvline(0, color='#64748b', linewidth=1, linestyle='--')

for bar, pct, raw in zip(bars, pct_changes, raw_labels):
    sign = "+" if pct > 0 else ""
    label_text = f"{sign}{pct:.2f}% ({raw})"
    if pct < 0:
        ax.text(pct - 0.6, bar.get_y() + bar.get_height()/2,
                label_text,
                va='center', ha='right', fontsize=9.5, fontweight='bold', color='#1e293b')
    else:
        ax.text(pct + 0.6, bar.get_y() + bar.get_height()/2,
                label_text,
                va='center', ha='left', fontsize=9.5, fontweight='bold', color='#1e293b')

ax.set_xlabel('10-Year Percentage Change (SY 2014–15 to SY 2024–25)', fontsize=10.5, fontweight='semibold')
ax.set_title('[DESCRIPTIVE OBSERVATION] The Kansas City Capacity Paradox: 10-Year Staffing Expansion vs. Flat Enrollment\n77 Regional School Districts (Mid-America Regional Council 9-County Bi-State Metropolitan Universe)', fontsize=11, fontweight='bold', pad=15)
ax.set_xlim(-22, 19)
ax.invert_yaxis()

# Footer note
footer_text2 = (
    "CLASSIFICATION: DESCRIPTIVE OBSERVATION. Source: Audited NCES CCD LEA Longitudinal Panel (SY 2014–15 through SY 2024–25).\n"
    "Universe: 77 public operating regular school districts across 9 MARC counties (MO: Jackson, Clay, Platte, Cass, Ray; KS: Johnson, Wyandotte, Leavenworth, Miami).\n"
    "Generated by: analysis/cross-measure/generate_observatory_visuals.py"
)
plt.figtext(0.5, 0.01, footer_text2, ha="center", fontsize=7.5, color="#475569",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

plt.subplots_adjust(bottom=0.15)
fig2_path = os.path.join(output_dir, "fig02_kc_10yr_capacity_paradox.png")
plt.savefig(fig2_path)
plt.close()
shutil.copy(fig2_path, os.path.join(artifact_dir, "fig02_kc_10yr_capacity_paradox.png"))

# -------------------------------------------------------------
# FIGURE 3: MODEL / CALIBRATED CASE STUDY
# Waterfall Decomposition (Shawnee Mission North HS Case)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

stages = [
    "1. Macro CCD PTR\n(Students / Total Staff)",
    "2. Specialist Wedge (Δ1)\n(Remove Non-Classroom)",
    "3. Schedule Multiplier (Δ2)\n('5 of 7' Regime: φ = 1.40)",
    "4. Core Residual (Δ3)\n(Curriculum Hierarchy)",
    "Observed Algebra I\nMean Class Size"
]

# Waterfall values
start = 14.19
w1 = 2.67
w2 = 5.68
w3 = 3.17
total = 25.71

bottoms = [0, start, start + w1, start + w1 + w2, 0]
heights = [start, w1, w2, w3, total]
colors = ['#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#ef4444']

bars = ax.bar(stages, heights, bottom=bottoms, color=colors, width=0.52, edgecolor='#1e293b', linewidth=0.8)

# Annotations
ax.text(0, start/2, f"{start:.2f}:1", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
ax.text(1, start + w1/2, f"+{w1:.2f}", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
ax.text(2, start + w1 + w2/2, f"+{w2:.2f}", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
ax.text(3, start + w1 + w2 + w3/2, f"+{w3:.2f}", ha='center', va='center', color='white', fontweight='bold', fontsize=10)
ax.text(4, total/2, f"{total:.2f}", ha='center', va='center', color='white', fontweight='bold', fontsize=11)

ax.set_ylabel('Effective Student Count per Teacher / Section', fontsize=10.5, fontweight='semibold')
ax.set_title('[MODEL / CALIBRATED CASE STUDY] Why 14:1 Macro PTR Yields 26-Student Algebra Classes\nMulti-Stage Decomposition of Secondary Structural Wedges (Shawnee Mission North HS, SY 2021–22)', fontsize=11, fontweight='bold', pad=15)
ax.set_ylim(0, 31)

# Footer note
footer_text3 = (
    "CLASSIFICATION: MODEL / CALIBRATED CASE STUDY (Empirical decomposition model, not a raw census observation).\n"
    "Model Formulation: Observed Core Section Size ≈ Macro PTR + Δ1 (Specialist Wedge) + Δ2 (Schedule Multiplier φ = 1.400) + Δ3 (Course Hierarchy).\n"
    "Data Sources: NCES CCD SY 2021–22, KSDE KPTEN 2021–22, OCR CRDC 2021–22. Generated by: analysis/cross-measure/generate_observatory_visuals.py"
)
plt.figtext(0.5, 0.01, footer_text3, ha="center", fontsize=7.5, color="#475569",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

plt.subplots_adjust(bottom=0.15)
fig3_path = os.path.join(output_dir, "fig03_schedule_waterfall_decomposition.png")
plt.savefig(fig3_path)
plt.close()
shutil.copy(fig3_path, os.path.join(artifact_dir, "fig03_schedule_waterfall_decomposition.png"))

print("All 3 figures successfully updated with explicit visual provenance and classification standards!")
