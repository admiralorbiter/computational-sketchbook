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
# FIGURE 1: National & State Epistemic Contrast (CCD PTR vs NTPS Class Size)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

jurisdictions = [
    "United States\n(National)",
    "Missouri\n(Statewide)",
    "Kansas\n(Statewide)",
    "Shawnee Mission North\n(KC Suburb)",
    "Lincoln College Prep\n(KCPS Urban Core)"
]

macro_ptr = [15.4, 13.8, 13.6, 14.19, 17.25]
actual_class_size = [23.3, 22.5, 19.8, 25.71, 31.0] # NTPS 2017-18 / CRDC 2021-22 Core
gaps = [c - p for p, c in zip(macro_ptr, actual_class_size)]

x = np.arange(len(jurisdictions))
width = 0.35

rects1 = ax.bar(x - width/2, macro_ptr, width, label='Macro Staffing Ratio (CCD PTR)', color='#3b82f6', alpha=0.9, edgecolor='#1d4ed8')
rects2 = ax.bar(x + width/2, actual_class_size, width, label='Actual Secondary Class Size (NTPS Survey / CRDC Core)', color='#f59e0b', alpha=0.9, edgecolor='#b45309')

# Annotate values and gap
for i in range(len(jurisdictions)):
    ax.annotate(f"{macro_ptr[i]:.1f}:1",
                xy=(x[i] - width/2, macro_ptr[i]), xytext=(0, 3),
                textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1e3a8a')
    ax.annotate(f"{actual_class_size[i]:.1f}",
                xy=(x[i] + width/2, actual_class_size[i]), xytext=(0, 3),
                textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#78350f')
    # Draw gap arrow / bracket
    ax.annotate(f"+{gaps[i]:.1f} gap",
                xy=(x[i], max(macro_ptr[i], actual_class_size[i]) + 1.8),
                ha='center', va='bottom', fontsize=8.5, fontweight='semibold', color='#dc2626')

ax.set_ylabel('Students per Teacher FTE / Students per Class', fontsize=11, fontweight='semibold')
ax.set_title('The Epistemic Contrast: Administrative Staffing Density (CCD) vs. Secondary Classroom Reality\nNational Benchmarks (NTPS) and Kansas City High Schools (CRDC)', fontsize=12, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(jurisdictions, fontsize=9.5)
ax.set_ylim(0, 37)
ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')

plt.tight_layout()
fig1_path = os.path.join(output_dir, "fig01_macro_ptr_vs_actual_class_size.png")
plt.savefig(fig1_path)
plt.close()
shutil.copy(fig1_path, os.path.join(artifact_dir, "fig01_macro_ptr_vs_actual_class_size.png"))

# -------------------------------------------------------------
# FIGURE 2: The KC 10-Year Capacity Paradox (2014-15 to 2024-25)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.8), dpi=300)

categories = [
    "K–12 Student\nEnrollment",
    "Certified Teacher\nFTE",
    "Instructional\nParaprofessionals",
    "Regional Pupil/Teacher\nRatio (PTR)"
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
        # Place label just to the left of 0 inside the white space, or neatly outside
        ax.text(pct - 0.6, bar.get_y() + bar.get_height()/2,
                label_text,
                va='center', ha='right', fontsize=9.5, fontweight='bold', color='#1e293b')
    else:
        ax.text(pct + 0.6, bar.get_y() + bar.get_height()/2,
                label_text,
                va='center', ha='left', fontsize=9.5, fontweight='bold', color='#1e293b')

ax.set_xlabel('10-Year Percentage Change (SY 2014–15 to SY 2024–25)', fontsize=10.5, fontweight='semibold')
ax.set_title('The Kansas City Capacity Paradox: 10-Year Staffing Expansion vs. Flat Enrollment\n77 Regional School Districts (Mid-America Regional Council 9-County Region)', fontsize=11.5, fontweight='bold', pad=15)
ax.set_xlim(-22, 19)
ax.invert_yaxis()

plt.tight_layout()
fig2_path = os.path.join(output_dir, "fig02_kc_10yr_capacity_paradox.png")
plt.savefig(fig2_path)
plt.close()
shutil.copy(fig2_path, os.path.join(artifact_dir, "fig02_kc_10yr_capacity_paradox.png"))

# -------------------------------------------------------------
# FIGURE 3: Multi-Stage Waterfall Decomposition (Shawnee Mission North Case)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=300)

stages = [
    "1. Macro CCD PTR\n(Students / Total Staff)",
    "2. Specialist Wedge (Δ1)\n(Remove Non-Classroom)",
    "3. Schedule Multiplier (Δ2)\n('5 of 7' Planning: φ = 1.40)",
    "4. Core Residual (Δ3)\n(Curriculum Hierarchy)",
    "Observed Algebra I\nAverage Class Size"
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
ax.set_title('Why 14:1 Macro PTR Yields 26-Student Algebra Classes\nMulti-Stage Decomposition of the Structural Wedges (Shawnee Mission North HS)', fontsize=11.5, fontweight='bold', pad=15)
ax.set_ylim(0, 30)

plt.tight_layout()
fig3_path = os.path.join(output_dir, "fig03_schedule_waterfall_decomposition.png")
plt.savefig(fig3_path)
plt.close()
shutil.copy(fig3_path, os.path.join(artifact_dir, "fig03_schedule_waterfall_decomposition.png"))

print("All 3 figures successfully created and copied to artifacts directory!")
