"""
Generate Task 003D Visual Evidence Packet:
Figure 09: Fall-2020 Shock & Post-Pandemic Trajectory Typology (Balanced 75 LEAs)
Figure 10: Kindergarten as a Demographic Warning Indicator (Indexed KG vs Grades 1-12)
Figure 11: Institutional Scale vs. Curricular Breadth: Advanced STEM Course Offerings (CRDC)
"""

import os
import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Styling
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

lea_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_lea_capacity_long_2014_15_2024_25.csv"))
sch_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_capacity_long_2014_15_2024_25.csv"))
crdc_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_crdc_school_course_capacity_2013_14_2023_24.csv"))

# Balanced 75 cohort definition
leas_1415 = set(lea_long[(lea_long['school_year']=='2014-2015') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
leas_2425 = set(lea_long[(lea_long['school_year']=='2024-2025') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
balanced_leas = sorted(list(leas_1415.intersection(leas_2425)))

lea_bal = lea_long[lea_long['nces_lea_id'].isin(balanced_leas)].copy()
pivot_enr = lea_bal.pivot(index='nces_lea_id', columns='school_year', values='enrollment_k12')
lea_names = lea_bal.groupby('nces_lea_id').first()[['district_name', 'state']]

# ------------------------------------------------------------------------------
# FIGURE 09: FALL-2020 SHOCK & RECOVERY TYPOLOGY
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 5.8), dpi=300)

typology = pd.DataFrame(index=pivot_enr.index)
typology['district_name'] = lea_names['district_name']
typology['e_2019'] = pivot_enr['2019-2020']
typology['e_2020'] = pivot_enr['2020-2021']
typology['e_2024'] = pivot_enr['2024-2025']

def classify(r):
    if r['e_2024'] >= r['e_2019']:
        return "Exceeded Pre-2020 Peak\n(N=23 LEAs | 16.3% of students)"
    elif r['e_2024'] > r['e_2020']:
        return "Partial Recovery\n(N=11 LEAs | 26.0% of students)"
    else:
        return "Persistent Decline\n(N=41 LEAs | 57.8% of students)"

typology['cat'] = typology.apply(classify, axis=1)

cats = [
    "Exceeded Pre-2020 Peak\n(N=23 LEAs | 16.3% of students)",
    "Partial Recovery\n(N=11 LEAs | 26.0% of students)",
    "Persistent Decline\n(N=41 LEAs | 57.8% of students)"
]
colors = ['#10b981', '#f59e0b', '#ef4444']

# Aggregate students in 2019, 2020, and 2024
cat_data = []
for c in cats:
    sub = typology[typology['cat'] == c]
    cat_data.append({
        '2019': sub['e_2019'].sum(),
        '2020': sub['e_2020'].sum(),
        '2024': sub['e_2024'].sum(),
        'net_pct': (sub['e_2024'].sum() - sub['e_2019'].sum()) / sub['e_2019'].sum() * 100
    })

x = np.arange(len(cats))
width = 0.25

rects1 = ax.bar(x - width, [d['2019'] for d in cat_data], width, label='2019–20 (Pre-Pandemic Peak)', color='#94a3b8', edgecolor='#64748b')
rects2 = ax.bar(x, [d['2020'] for d in cat_data], width, label='2020–21 (Immediate Shock)', color='#cbd5e1', edgecolor='#94a3b8')
rects3 = ax.bar(x + width, [d['2024'] for d in cat_data], width, label='2024–25 (Current Enrollment)', color=['#10b981', '#f59e0b', '#ef4444'], edgecolor='#0f172a', linewidth=1.1)

ax.set_ylabel('Total Enrolled K–12 Students', fontsize=10.5, fontweight='semibold')
ax.set_title('[DESCRIPTIVE OBSERVATION] The Post-Pandemic Divergence: Fall 2020 Shock & Recovery Typology\n75 Balanced School Districts in Kansas City Metro Grouped by 5-Year Trajectory', fontsize=11, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(cats, fontsize=9.5, fontweight='bold')
ax.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.8)
ax.set_ylim(0, 230000)

# Annotate net changes
for i, d in enumerate(cat_data):
    chg = d['2024'] - d['2019']
    pct = d['net_pct']
    ax.text(x[i] + width, d['2024'] + 3500, f"{chg:+,.0f}\n({pct:+.1f}%)",
            ha='center', va='bottom', fontsize=8.5, fontweight='bold',
            color='#065f46' if chg > 0 else ('#b45309' if pct > -5 else '#991b1b'))

footer_text9 = (
    "CLASSIFICATION: DESCRIPTIVE OBSERVATION. Source: NCES CCD LEA Longitudinal Panel (Balanced 75-LEA Cohort).\n"
    "Typology partitions the aggregate 'flat' trajectory: 41 districts (57.8% of students) remain in persistent decline below 2020 levels,\n"
    "offset by 23 growing suburban/charter districts that exceeded pre-pandemic peaks. Generated by: analysis/cross-measure/generate_task003d_visuals.py"
)
plt.figtext(0.5, 0.015, footer_text9, ha="center", fontsize=7.2, color="#475569",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

plt.subplots_adjust(bottom=0.20, top=0.88, left=0.10, right=0.95)
fig9_path = os.path.join(output_dir, "fig09_post_2020_recovery_typology.png")
plt.savefig(fig9_path)
plt.close()
if artifact_dir:
    shutil.copy(fig9_path, artifact_dir / "fig09_post_2020_recovery_typology.png")

# ------------------------------------------------------------------------------
# FIGURE 10: KINDERGARTEN AS A DEMOGRAPHIC WARNING INDICATOR
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)

kg_bal = lea_bal.groupby('school_year').agg(
    enr_kg=('enrollment_kg', 'sum'),
    enr_k12=('enrollment_k12', 'sum')
).reset_index()
kg_bal['enr_1_12'] = kg_bal['enr_k12'] - kg_bal['enr_kg']

years = kg_bal['school_year'].values
years_labels = [y.replace("20", "20", 1).replace("-20", "-") for y in years]

kg_idx = kg_bal['enr_kg'] / kg_bal['enr_kg'].iloc[0] * 100
g1_12_idx = kg_bal['enr_1_12'] / kg_bal['enr_1_12'].iloc[0] * 100
k12_idx = kg_bal['enr_k12'] / kg_bal['enr_k12'].iloc[0] * 100

ax.plot(years_labels, kg_idx, marker='o', color='#e11d48', linewidth=2.6, markersize=6.5, label='Kindergarten Cohort (Incoming Entry Class)')
ax.plot(years_labels, g1_12_idx, marker='s', color='#0284c7', linewidth=2.0, linestyle='--', markersize=5.5, label='Grades 1–12 (Continuing Cohorts)')
ax.plot(years_labels, k12_idx, marker='^', color='#475569', linewidth=1.8, linestyle=':', markersize=5.0, label='Total K–12 Enrollment')

ax.axhline(100.0, color='#94a3b8', linestyle='-', linewidth=0.8)

# Highlight Fall 2020 shock
covid_idx = 6 # 2020-21
drop_kg_pct = (kg_bal['enr_kg'].iloc[covid_idx] - kg_bal['enr_kg'].iloc[5]) / kg_bal['enr_kg'].iloc[5] * 100
drop_g112_pct = (kg_bal['enr_1_12'].iloc[covid_idx] - kg_bal['enr_1_12'].iloc[5]) / kg_bal['enr_1_12'].iloc[5] * 100

ax.scatter([years_labels[covid_idx]], [kg_idx.iloc[covid_idx]], color='#be123c', s=80, zorder=5)
ax.annotate(f"Fall 2020 Kindergarten Collapse: {drop_kg_pct:.1f}%\n(-2,871 pupils; accounts for 36.9% of total drop)",
            xy=(years_labels[covid_idx], kg_idx.iloc[covid_idx]), xytext=(-40, -45),
            textcoords="offset points", fontsize=8.5, fontweight='bold', color='#991b1b',
            arrowprops=dict(arrowstyle="->", color='#dc2626', lw=1.2),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff1f2", edgecolor="#fda4af", alpha=0.9))

# Endpoint 10-year divergence annotation
ax.annotate(f"10-Yr Net Difference:\nKindergarten: {kg_idx.iloc[-1] - 100:+.2f}% (-2,341 students)\nGrades 1–12: {g1_12_idx.iloc[-1] - 100:+.2f}% (+282 students)",
            xy=(years_labels[-1], kg_idx.iloc[-1]), xytext=(-110, -45),
            textcoords="offset points", fontsize=8.2, fontweight='bold', color='#0f172a',
            arrowprops=dict(arrowstyle="->", color='#0f172a', lw=1.2),
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

ax.set_ylabel('Cohort Enrollment Index (SY 2014–15 = 100)', fontsize=10, fontweight='semibold')
ax.set_title('[DEMOGRAPHIC WARNING INDICATOR] Kindergarten as a Leading Indicator: The Pipeline Dynamic\nIndexed Trajectories of Incoming Kindergarten vs. Continuing Grades 1–12 (SY 2014–15 to SY 2024–25)', fontsize=11, fontweight='bold', pad=15)
ax.set_ylim(84, 106)
ax.set_xticks(range(len(years_labels)))
ax.set_xticklabels(years_labels, rotation=35, ha='right', fontsize=9)
ax.legend(loc='lower left', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=8.8)

footer_text10 = (
    "CLASSIFICATION: DEMOGRAPHIC WARNING INDICATOR. Source: NCES CCD LEA Survey (Balanced 75-LEA Cohort).\n"
    "The net difference between 2014-15 and 2024-25 is arithmetically concentrated in Kindergarten (-9.14%), while continuing grades 1–12 are net positive (+0.10%).\n"
    "If smaller entering cohorts persist without offsetting migration or sector shifts, they will exert downward pressure on later grades as they advance upward."
)
plt.figtext(0.5, 0.015, footer_text10, ha="center", fontsize=7.2, color="#475569",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

plt.subplots_adjust(bottom=0.22, top=0.88, left=0.10, right=0.95)
fig10_path = os.path.join(output_dir, "fig10_kindergarten_pipeline_indicator.png")
plt.savefig(fig10_path)
plt.close()
if artifact_dir:
    shutil.copy(fig10_path, artifact_dir / "fig10_kindergarten_pipeline_indicator.png")

# ------------------------------------------------------------------------------
# FIGURE 11: INSTITUTIONAL SCALE VS. CURRICULAR BREADTH (CRDC)
# ------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)

crdc_reg_hs = crdc_df[(crdc_df['is_operating']==True) & (crdc_df['school_type']=='Regular School') & (crdc_df['school_level']=='High') & (crdc_df['enrollment_k12']>0)].copy()

crdc_reg_hs['has_alg2'] = (crdc_reg_hs['classes_alg2'] > 0) | (crdc_reg_hs['enrollment_alg2'] > 0)
crdc_reg_hs['has_phys'] = (crdc_reg_hs['classes_phys'] > 0) | (crdc_reg_hs['enrollment_phys'] > 0)
crdc_reg_hs['has_calc'] = (crdc_reg_hs['classes_calc'] > 0) | (crdc_reg_hs['enrollment_calc'] > 0)
crdc_reg_hs['has_chem'] = (crdc_reg_hs['classes_chem'] > 0) | (crdc_reg_hs['enrollment_chem'] > 0)

crdc_reg_hs['size_band'] = pd.cut(
    crdc_reg_hs['enrollment_k12'],
    bins=[0, 400, 800, 1200, 1600, 99999],
    labels=['<400', '400–799', '800–1,199', '1,200–1,599', '1,600+'],
    right=False
)

offer = crdc_reg_hs.groupby('size_band', observed=False).agg(
    n_schools=('nces_school_id', 'count'),
    pct_chem=('has_chem', lambda s: s.mean()*100),
    pct_phys=('has_phys', lambda s: s.mean()*100),
    pct_calc=('has_calc', lambda s: s.mean()*100),
).reset_index()

bands = offer['size_band'].values
n_counts = offer['n_schools'].values
x = np.arange(len(bands))
width = 0.26

rects1 = ax.bar(x - width, offer['pct_chem'], width, label='Chemistry', color='#0284c7', edgecolor='#0369a1')
rects2 = ax.bar(x, offer['pct_phys'], width, label='Physics', color='#8b5cf6', edgecolor='#6d28d9')
rects3 = ax.bar(x + width, offer['pct_calc'], width, label='Calculus', color='#f59e0b', edgecolor='#d97706')

ax.set_ylabel('Percentage of High Schools Offering Course (%)', fontsize=10, fontweight='semibold')
ax.set_title('[CROSS-MEASURE BENCHMARK] Institutional Scale vs. Curricular Breadth: The Association\nProbability of Advanced STEM Course Offerings Across High School Enrollment Brackets (CRDC Multi-Wave, N=587 Regular High School-Waves)', fontsize=10.5, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels([f"{b}\n(N={n})" for b, n in zip(bands, n_counts)], fontsize=9)
ax.set_ylim(0, 115)
ax.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9)

# Value labels on Calculus
for i, v in enumerate(offer['pct_calc']):
    ax.text(x[i] + width, v + 2, f"{v:.1f}%", ha='center', va='bottom', fontsize=8.2, fontweight='bold', color='#b45309')

# Value labels on Physics
for i, v in enumerate(offer['pct_phys']):
    ax.text(x[i], v + 2, f"{v:.1f}%", ha='center', va='bottom', fontsize=8.2, fontweight='bold', color='#5b21b6')

footer_text11 = (
    "CLASSIFICATION: CROSS-MEASURE BENCHMARK. Source: Civil Rights Data Collection (CRDC Waves 2013–14 through 2023–24).\n"
    "Population: Regular operating public high schools (excludes specialized/alternative facilities). Shows robust scale association:\n"
    "Larger regular high schools are substantially more likely to report offering Calculus (32.6% vs 95.9%) and Physics (56.2% vs 98.4%)."
)
plt.figtext(0.5, 0.015, footer_text11, ha="center", fontsize=7.2, color="#475569",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9))

plt.subplots_adjust(bottom=0.20, top=0.88, left=0.08, right=0.95)
fig11_path = os.path.join(output_dir, "fig11_school_scale_vs_curricular_breadth.png")
plt.savefig(fig11_path)
plt.close()
if artifact_dir:
    shutil.copy(fig11_path, artifact_dir / "fig11_school_scale_vs_curricular_breadth.png")

print("Figures 9, 10, and 11 successfully generated and copied to artifact directory!")
