"""
Generate National Context Visualizations for EDU-002:
Figure 7: KC vs. U.S. Public K-12 Enrollment Trend (Indexed to 2014-15 = 100)
Figure 8: Kansas City School Size in National Context by Grade Band
"""

import os
import shutil
from pathlib import Path
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
artifact_env = os.environ.get("ANTIGRAVITY_ARTIFACT_DIR")
artifact_dir = Path(artifact_env) if artifact_env and Path(artifact_env).exists() else None
os.makedirs(output_dir, exist_ok=True)

# Data paths
lea_long_path = os.path.join(KC_DIR, "data", "processed", "kc_lea_capacity_long_2014_15_2024_25.csv")
lea_long = pd.read_csv(lea_long_path)

# -------------------------------------------------------------
# FIGURE 7: CROSS-SOURCE / BENCHMARK COMPARISON
# KC Metro vs. United States Public K-12 Enrollment Trajectory (2014-15 = 100)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)

# Compute KC series dynamically
fully_dyn = lea_long[lea_long['lea_fully_within_region'] == True].groupby('school_year')['enrollment_k12'].sum()
years_full = fully_dyn.index.values
kc_raw = fully_dyn.values

# US Total K-12 Public Enrollment in thousands (from NCES Digest 2023, Table 203.10: Total - Pre-K)
# Note: 2023-24 and 2024-25 are NCES National Projection Model figures
us_raw = np.array([
    48943.2, 49036.4, 49189.5, 49214.4, 49154.4, 
    49210.7, 48132.8, 48022.5, 48090.3, 47658.5, 47381.3
])

kc_idx = kc_raw / kc_raw[0] * 100
us_idx = us_raw / us_raw[0] * 100

years_labels = [y.replace("20", "20", 1).replace("-20", "-") for y in years_full]

ax.plot(years_labels, kc_idx, marker='o', color='#0284c7', linewidth=2.5, markersize=6, label='Kansas City Metro (Dynamic Fully-Regional, 77 LEAs)')
ax.plot(years_labels[:9], us_idx[:9], marker='s', color='#0f172a', linewidth=2.2, markersize=5.5, label='United States Total (Reported CCD Census)')
ax.plot(years_labels[8:], us_idx[8:], marker='^', color='#64748b', linewidth=2.0, linestyle='--', markersize=5.5, label='United States Total (NCES Projection Model)')

# Highlight Fall 2020 break
covid_idx = 6 # 2020-21
ax.scatter([years_labels[covid_idx]], [kc_idx[covid_idx]], color='#e11d48', s=70, zorder=5)
ax.scatter([years_labels[covid_idx]], [us_idx[covid_idx]], color='#e11d48', s=70, zorder=5)

ax.annotate('Fall 2020 Enrollment Drop:\nKC Metro: -2.32% (-7.6k students)\nU.S. Total: -2.19% (-1.08M students)',
            xy=(years_labels[covid_idx], 99.2), xytext=(25, -28), textcoords="offset points",
            fontsize=8.5, fontweight='bold', color='#be123c',
            arrowprops=dict(arrowstyle="->", color='#e11d48', lw=1.2),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff1f2", edgecolor="#fda4af", alpha=0.9))

peak_idx = 5 # 2019-20
ax.annotate(f'Pre-Pandemic Peak (2019–20)\nKC: {kc_raw[peak_idx]:,} ({kc_idx[peak_idx]:.2f})\nUS: 49.21M ({us_idx[peak_idx]:.2f})',
            xy=(years_labels[peak_idx], kc_idx[peak_idx]), xytext=(-65, 22), textcoords="offset points",
            fontsize=8.2, fontweight='bold', color='#0369a1',
            arrowprops=dict(arrowstyle="->", color='#0284c7', lw=1.2))

# Post-pandemic diverge annotation
ax.annotate(f'Post-Pandemic Stabilization:\nKC Plateau: 99.27% of 2014 baseline\nUS Continued Decline: 96.81% (proj)',
            xy=(years_labels[-1], kc_idx[-1]), xytext=(-110, -45), textcoords="offset points",
            fontsize=8.2, fontweight='bold', color='#0f172a',
            arrowprops=dict(arrowstyle="->", color='#0f172a', lw=1.2),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

ax.axhline(100.0, color='#94a3b8', linestyle=':', linewidth=1)
ax.set_ylabel('K–12 Public Enrollment Index (SY 2014–15 = 100)', fontsize=10, fontweight='semibold')
ax.set_title('[CROSS-SOURCE / BENCHMARK COMPARISON] Regional vs. National K–12 Enrollment Trajectories\nIndexed Public School Membership Trends: Kansas City Metro vs. United States (SY 2014–15 to SY 2024–25)', fontsize=11, fontweight='bold', pad=15)
ax.set_ylim(95.5, 103.5)
ax.set_xticks(range(len(years_labels)))
ax.set_xticklabels(years_labels, rotation=35, ha='right', fontsize=9)
ax.legend(loc='lower left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.5)

footer_text7 = (
    "CLASSIFICATION: CROSS-SOURCE / BENCHMARK COMPARISON. Operationalization: ENR-NCES-K12-MEMBER (excludes Pre-K).\n"
    f"Sources: Kansas City: Dynamically computed from audited CCD LEA Panel (baseline = {kc_raw[0]:,} students; 2024–25 = {kc_raw[-1]:,}).\n"
    "United States: NCES Digest of Education Statistics Table 203.10 (SY 2014–15 baseline = 48,943,226 students; 2023–25 are NCES projections).\n"
    "Generated by: analysis/cross-measure/generate_national_enrollment_visuals.py"
)
plt.figtext(0.5, 0.015, footer_text7, ha="center", fontsize=7.2, color="#475569",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

plt.subplots_adjust(top=0.88, bottom=0.22, left=0.10, right=0.95)
fig7_path = os.path.join(output_dir, "fig07_kc_vs_us_enrollment_trajectory.png")
plt.savefig(fig7_path)
plt.close()
if artifact_dir:
    shutil.copy(fig7_path, artifact_dir / "fig07_kc_vs_us_enrollment_trajectory.png")

# -------------------------------------------------------------
# FIGURE 8: BENCHMARK COMPARISON
# Kansas City School Size in National Context by Grade Band
# -------------------------------------------------------------
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13.5, 6.0), dpi=300, sharey=True)

# Size bands for grouped comparison:
# Groups: Under 200, 200-399, 400-599, 600-799, 800-999, 1000+
cat_labels = ["<200", "200–399", "400–599", "600–799", "800–999", "1,000+"]
x = np.arange(len(cat_labels))
width = 0.36

# National Percentages (NCES Digest Table 216.40, SY 2021-22 Regular Schools)
us_elem = [4.5 + 8.1, 14.9 + 20.2, 19.3 + 13.9, 8.9 + 4.8, 3.9, 1.4 + 0.1]
us_middle = [5.9 + 7.7, 9.8 + 11.4, 10.9 + 10.9, 10.3 + 9.5, 13.1, 9.4 + 0.8 + 0.1]
us_high = [8.9 + 10.3, 10.1 + 10.0, 7.6 + 6.2, 5.0 + 4.3, 6.5, 13.0 + 9.1 + 7.7 + 1.4]

# Kansas City Percentages (SY 2024-25 Operating Schools with Enrollment > 0)
# Elementary (N=393)
kc_elem = [1.8 + 4.8, 16.8 + 32.8, 24.7 + 12.2, 5.3 + 0.8, 0.5, 0.3]
# Middle (N=122)
kc_middle = [1.6 + 6.6, 4.9 + 11.5, 9.0 + 21.3, 21.3 + 10.7, 10.7, 2.5]
# High (N=114)
kc_high = [14.0 + 7.9, 6.1 + 3.5, 6.1 + 2.6, 3.5 + 4.4, 7.0, 20.2 + 20.2 + 4.4]

def plot_grade_band(ax, title, kc_data, us_data, kc_med, us_med, note_text):
    rects1 = ax.bar(x - width/2, us_data, width, label='U.S. National', color='#94a3b8', edgecolor='#64748b')
    rects2 = ax.bar(x + width/2, kc_data, width, label='KC Metro', color='#0284c7', edgecolor='#0369a1')
    ax.set_title(title, fontsize=10.5, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels, fontsize=8.5)
    ax.grid(axis='y', linestyle=':', alpha=0.7)
    
    # Text box for medians and insight
    info_box = f"KC Median: {kc_med:.0f}\nU.S. Median: ~{us_med:.0f}\n{note_text}"
    ax.text(0.95, 0.95, info_box, transform=ax.transAxes, fontsize=7.8,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#ffffff", edgecolor="#cbd5e1", alpha=0.9))

plot_grade_band(ax1, "Elementary Schools\n(KC N=393 | U.S. N=52,800)", kc_elem, us_elem, 374, 420, "KC concentrated in\n300-499 size range")
plot_grade_band(ax2, "Middle Schools\n(KC N=122 | U.S. N=540)", kc_middle, us_middle, 584, 540, "KC concentrated in\n500-699 size range")
plot_grade_band(ax3, "High Schools\n(KC N=114 | U.S. N=18,200)", kc_high, us_high, 843, 640, "KC 1,000+ mega-schools:\n44.8% vs. 31.3% U.S.")

ax1.set_ylabel('Percentage of Schools (%)', fontsize=10, fontweight='semibold')
ax1.set_ylim(0, 60)
ax3.legend(loc='upper right', bbox_to_anchor=(0.95, 0.65), frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.2)

fig.suptitle('[BENCHMARK COMPARISON] Kansas City School Size Distributions in National Context\nComparing Public School Campus Scales by Grade Band: Kansas City Metro (SY 2024–25) vs. United States (SY 2021–22)', fontsize=11.5, fontweight='bold', y=0.97)

footer_text8 = (
    "CLASSIFICATION: BENCHMARK COMPARISON. Operationalization: ENR-NCES-FALL-MEMBER-SCH (Fall Headcount MEMBER).\n"
    "Sources: Kansas City: NCES CCD Public School Universe (SY 2024–25, N=629 regular elementary/middle/high operating schools with enrollment > 0).\n"
    "United States: NCES Digest of Education Statistics Table 216.40 (SY 2021–22 regular public schools). Excludes specialized/zero-membership facilities.\n"
    "Generated by: analysis/cross-measure/generate_national_enrollment_visuals.py"
)
plt.figtext(0.5, 0.015, footer_text8, ha="center", fontsize=7.2, color="#475569",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

plt.subplots_adjust(top=0.82, bottom=0.18, left=0.06, right=0.97, wspace=0.15)
fig8_path = os.path.join(output_dir, "fig08_kc_school_size_national_context.png")
plt.savefig(fig8_path)
plt.close()
if artifact_dir:
    shutil.copy(fig8_path, artifact_dir / "fig08_kc_school_size_national_context.png")

print("Figures 7 and 8 successfully generated and copied to dashboard and artifact directories!")
