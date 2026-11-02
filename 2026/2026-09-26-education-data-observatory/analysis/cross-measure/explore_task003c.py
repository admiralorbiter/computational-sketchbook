"""
# [HISTORICAL / EXPLORATORY SCRIPT — TASK 003C]
# Note: For canonical audited Task 003E findings, see measures/EDU-002-student-enrollment/README.md.

Comprehensive exploration script for Task 003C:
1. LEA-School Membership Reconciliation Gap audit (77 fully regional LEAs vs 2 statewide agencies)
2. Longitudinal enrollment universes (dynamic fully-regional vs balanced 75-LEA vs unfiltered)
3. Exploratory Analyses:
   A. Regional Redistribution (growing vs shrinking, gross vs net, county, locale, distance from downtown)
   B. System Concentration (Top 5, 10, 20 LEAs over time, HHI, charter vs traditional)
   C. School Scale & Exposure (grade band, locale, student-weighted vs median, exposure brackets)
   D. District Portfolio Response (enrollment change vs operating school count change, campus density)
   E. Pre-K Structure (standalone vs integrated, Pre-K share)
   F. Existing Cross-Measure Connections (enrollment vs CRDC class size by subject, student complexity)
"""

import os
import pandas as pd
import numpy as np

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KC_DIR = os.path.join(os.path.dirname(BASE_DIR), "2026-09-23-kc-education-capacity")

# Load processed datasets
lea_2425 = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_lea_capacity_2024_2025.csv"))
sch_2425 = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_capacity_2024_2025.csv"))
lea_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_lea_capacity_long_2014_15_2024_25.csv"))
sch_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_capacity_long_2014_15_2024_25.csv"))
sch_uni = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_universe_2024_2025.csv"))

crdc_course_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_crdc_school_course_capacity_2013_14_2023_24.csv"))
complexity_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_complexity_panel_2015_2024.csv"))

print("="*75)
print("1. RECONCILIATION GAP AUDIT (SY 2024-25)")
print("="*75)
sch_by_lea = sch_2425.groupby('nces_lea_id')['enrollment_total'].sum().reset_index(name='campus_sum_enrollment')
merged = pd.merge(lea_2425, sch_by_lea, on='nces_lea_id', how='left')
merged['campus_sum_enrollment'] = merged['campus_sum_enrollment'].fillna(0)
merged['diff'] = merged['enrollment_total'] - merged['campus_sum_enrollment']

fully = merged[merged['lea_fully_within_region'] == True].copy()
non_fully = merged[merged['lea_fully_within_region'] == False].copy()

tot_lea = fully['enrollment_total'].sum()
tot_sch = fully['campus_sum_enrollment'].sum()
tot_diff = fully['diff'].sum()
exact_zero = (fully['diff'] == 0).sum()
pos_diff = (fully['diff'] > 0).sum()
neg_diff = (fully['diff'] < 0).sum()

print(f"Total Fully Regional LEAs: {len(fully)}")
print(f"Total LEA Enrollment: {tot_lea:,}")
print(f"Total Campus Sum Enrollment: {tot_sch:,}")
print(f"Total Regional Gap: +{tot_diff:,} ({tot_diff/tot_lea*100:.3f}% of LEA membership)")
print(f"Exact Reconciliations (diff == 0): {exact_zero} of {len(fully)} districts ({exact_zero/len(fully)*100:.1f}%)")
print(f"Positive Gaps (diff > 0): {pos_diff} districts")
print(f"Negative Gaps (diff < 0): {neg_diff} districts")

print("\n--- ALL POSITIVE GAPS IN FULLY REGIONAL LEAS ---")
top_pos = fully[fully['diff'] > 0].sort_values(by='diff', ascending=False)
for _, r in top_pos.iterrows():
    pct = r['diff'] / r['enrollment_total'] * 100
    print(f"  {r['district_name']:<30} ({r['state']}): LEA={r['enrollment_total']:>6,}, CampusSum={r['campus_sum_enrollment']:>6,}, Gap=+{r['diff']:>4,} ({pct:>5.1f}%)")

print("\n--- NON-FULLY REGIONAL LEAS (STATEWIDE AGENCIES) ---")
for _, r in non_fully.iterrows():
    pct = r['diff'] / r['enrollment_total'] * 100
    print(f"  {r['district_name']:<30} ({r['state']}): LEA={r['enrollment_total']:>6,}, In-Region CampusSum={r['campus_sum_enrollment']:>6,}, Gap=+{r['diff']:>4,} ({pct:>5.1f}%)")

print("\n" + "="*75)
print("2. LONGITUDINAL UNIVERSES & TRAJECTORIES")
print("="*75)
unfilt = lea_long.groupby('school_year')['enrollment_k12'].sum()
fully_dyn = lea_long[lea_long['lea_fully_within_region'] == True].groupby('school_year')['enrollment_k12'].sum()

leas_1415 = set(lea_long[(lea_long['school_year']=='2014-2015') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
leas_2425 = set(lea_long[(lea_long['school_year']=='2024-2025') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
balanced_leas = leas_1415.intersection(leas_2425)
bal_dyn = lea_long[lea_long['nces_lea_id'].isin(balanced_leas)].groupby('school_year')['enrollment_k12'].sum()

print("Year        Unfiltered     Dynamic Fully-Regional     Balanced 75-LEA")
print("-" * 70)
for yr in unfilt.index:
    print(f"{yr}   {unfilt[yr]:>10,}     {fully_dyn[yr]:>14,} ({fully_dyn[yr]/fully_dyn.iloc[0]*100:>6.2f})   {bal_dyn[yr]:>12,} ({bal_dyn[yr]/bal_dyn.iloc[0]*100:>6.2f})")

p14_dyn = fully_dyn['2014-2015']
p24_dyn = fully_dyn['2024-2025']
peak_dyn = fully_dyn.max()
peak_yr_dyn = fully_dyn.idxmax()
print(f"\nDynamic Fully Regional Change: {p14_dyn:,} -> {p24_dyn:,} ({p24_dyn - p14_dyn:+,} students, {(p24_dyn - p14_dyn)/p14_dyn*100:+.2f}%)")
print(f"Dynamic Peak: {peak_dyn:,} in {peak_yr_dyn}")

p14_bal = bal_dyn['2014-2015']
p24_bal = bal_dyn['2024-2025']
peak_bal = bal_dyn.max()
peak_yr_bal = bal_dyn.idxmax()
print(f"Balanced 75 Cohort Change:    {p14_bal:,} -> {p24_bal:,} ({p24_bal - p14_bal:+,} students, {(p24_bal - p14_bal)/p14_bal*100:+.2f}%)")
print(f"Balanced Peak: {peak_bal:,} in {peak_yr_bal}")

print("\n" + "="*75)
print("3. EXPLORATORY ANALYSIS A: REGIONAL REDISTRIBUTION")
print("="*75)
p14 = lea_long[(lea_long['school_year']=='2014-2015') & (lea_long['nces_lea_id'].isin(balanced_leas))].set_index('nces_lea_id')
p24 = lea_long[(lea_long['school_year']=='2024-2025') & (lea_long['nces_lea_id'].isin(balanced_leas))].set_index('nces_lea_id')

redist = pd.DataFrame({
    'district_name': p24['district_name'],
    'state': p24['state'],
    'county': p24['county_primary'],
    'k12_1415': p14['enrollment_k12'],
    'k12_2425': p24['enrollment_k12'],
})
redist['change_abs'] = redist['k12_2425'] - redist['k12_1415']
redist['change_pct'] = redist['change_abs'] / redist['k12_1415'] * 100

growing = redist[redist['change_abs'] > 0]
shrinking = redist[redist['change_abs'] < 0]
flat = redist[redist['change_abs'] == 0]

print(f"Total Balanced Districts: {len(redist)}")
print(f"Growing Districts:   {len(growing)} | Total Gross Gain: +{growing['change_abs'].sum():,}")
print(f"Shrinking Districts: {len(shrinking)} | Total Gross Loss: {shrinking['change_abs'].sum():,}")
print(f"Net Change across Balanced 75: {redist['change_abs'].sum():,}")

print("\nTop 8 Growing Districts (Absolute):")
print(redist.sort_values(by='change_abs', ascending=False)[['district_name', 'state', 'k12_1415', 'k12_2425', 'change_abs', 'change_pct']].head(8).to_string())

print("\nTop 8 Shrinking Districts (Absolute):")
print(redist.sort_values(by='change_abs', ascending=True)[['district_name', 'state', 'k12_1415', 'k12_2425', 'change_abs', 'change_pct']].head(8).to_string())

# Change by State
by_state = redist.groupby('state').agg({'k12_1415': 'sum', 'k12_2425': 'sum', 'change_abs': 'sum'}).reset_index()
by_state['change_pct'] = by_state['change_abs'] / by_state['k12_1415'] * 100
print("\nGrowth by State (Balanced 75):")
print(by_state.to_string())

# Change by County
by_county = redist.groupby(['state', 'county']).agg({'k12_1415': 'sum', 'k12_2425': 'sum', 'change_abs': 'sum'}).reset_index()
by_county['change_pct'] = by_county['change_abs'] / by_county['k12_1415'] * 100
print("\nGrowth by County (Balanced 75):")
print(by_county.sort_values(by='change_abs', ascending=False).to_string())

# Distance from downtown check using school file directly
sch_2425['dist_band'] = pd.cut(sch_2425['distance_downtown_kc_miles'], bins=[0, 5, 10, 15, 20, 30, 100], labels=['0-5 mi', '5-10 mi', '10-15 mi', '15-20 mi', '20-30 mi', '30+ mi'])
dist_summ = sch_2425.groupby('dist_band', observed=False)['enrollment_total'].agg(['count', 'sum']).reset_index()
dist_summ['pct_enr'] = dist_summ['sum'] / dist_summ['sum'].sum() * 100
print("\nCampus enrollment by distance from downtown KC (SY 2024-25):")
print(dist_summ.to_string())

print("\n" + "="*75)
print("4. EXPLORATORY ANALYSIS B: SYSTEM CONCENTRATION")
print("="*75)
fully_2425_sorted = fully.sort_values(by='enrollment_total', ascending=False)
top5_enr = fully_2425_sorted.iloc[:5]['enrollment_total'].sum()
top10_enr = fully_2425_sorted.iloc[:10]['enrollment_total'].sum()
top20_enr = fully_2425_sorted.iloc[:20]['enrollment_total'].sum()
tot_reg_enr = fully['enrollment_total'].sum()

print(f"Top 5 LEAs Share:  {top5_enr:,} / {tot_reg_enr:,} = {top5_enr/tot_reg_enr*100:.2f}%")
print(f"Top 10 LEAs Share: {top10_enr:,} / {tot_reg_enr:,} = {top10_enr/tot_reg_enr*100:.2f}%")
print(f"Top 20 LEAs Share: {top20_enr:,} / {tot_reg_enr:,} = {top20_enr/tot_reg_enr*100:.2f}%")

# Top 10 districts by name
print("\nTop 10 Districts in KC Metro:")
print(fully_2425_sorted[['district_name', 'state', 'enrollment_total']].head(10).to_string())

# Herfindahl-Hirschman Index (HHI) for LEA enrollment
shares = fully['enrollment_total'] / tot_reg_enr * 100
hhi = (shares ** 2).sum()
print(f"\nRegional LEA Enrollment HHI: {hhi:.1f} (Benchmark: <1,500 = unconcentrated / decentralized)")

# Charter vs traditional in 2024-25
charter_leas = sch_uni[sch_uni['is_charter'] == True]['nces_lea_id'].unique()
fully['is_charter_lea'] = fully['nces_lea_id'].isin(charter_leas)
charter_summ = fully.groupby('is_charter_lea')['enrollment_total'].agg(['count', 'sum']).reset_index()
charter_summ['pct'] = charter_summ['sum'] / charter_summ['sum'].sum() * 100
print("\nCharter vs Traditional LEA summary (SY 2024-25):")
print(charter_summ.to_string())

print("\n" + "="*75)
print("5. EXPLORATORY ANALYSIS C: SCHOOL SCALE & EXPOSURE")
print("="*75)
reg_sch = sch_2425[sch_2425['enrollment_total'] > 0].copy()
reg_sch['size_bracket'] = pd.cut(
    reg_sch['enrollment_total'],
    bins=[0, 250, 500, 1000, 1500, 99999],
    labels=['<250', '250-499', '500-999', '1,000-1,499', '1,500+'],
    right=False
)

size_summ = reg_sch.groupby('size_bracket', observed=False).agg(
    school_count=('nces_school_id', 'count'),
    student_sum=('enrollment_total', 'sum')
).reset_index()
size_summ['pct_schools'] = size_summ['school_count'] / size_summ['school_count'].sum() * 100
size_summ['pct_students'] = size_summ['student_sum'] / size_summ['student_sum'].sum() * 100
print("Overall Campus Scale Exposure (SY 2024-25, N=665 schools with enrollment > 0):")
print(size_summ.to_string())

# High school specific exposure
hs_sch = sch_2425[(sch_2425['school_level'] == 'High') & (sch_2425['enrollment_total'] > 0)].copy()
hs_sch['size_bracket'] = pd.cut(
    hs_sch['enrollment_total'],
    bins=[0, 250, 500, 1000, 1500, 99999],
    labels=['<250', '250-499', '500-999', '1,000-1,499', '1,500+'],
    right=False
)
hs_summ = hs_sch.groupby('size_bracket', observed=False).agg(
    school_count=('nces_school_id', 'count'),
    student_sum=('enrollment_total', 'sum')
).reset_index()
hs_summ['pct_schools'] = hs_summ['school_count'] / hs_summ['school_count'].sum() * 100
hs_summ['pct_students'] = hs_summ['student_sum'] / hs_summ['student_sum'].sum() * 100
print("\nHigh School Specific Exposure (SY 2024-25, N=114 high schools):")
print(hs_summ.to_string())

# Student-weighted mean school size vs unweighted mean/median
for lvl in ['Elementary', 'Middle', 'High']:
    sub = sch_2425[(sch_2425['school_level'] == lvl) & (sch_2425['enrollment_total'] > 0)]
    unw_mean = sub['enrollment_total'].mean()
    med = sub['enrollment_total'].median()
    w_mean = (sub['enrollment_total'] * sub['enrollment_total']).sum() / sub['enrollment_total'].sum()
    print(f"{lvl:<10} | Median: {med:>5.0f} | Unweighted Mean: {unw_mean:>5.1f} | Student-Weighted Mean: {w_mean:>5.1f} | Ratio: {w_mean/med:.2f}x")

print("\n" + "="*75)
print("6. EXPLORATORY ANALYSIS D: DISTRICT PORTFOLIO RESPONSE")
print("="*75)
redist['schools_1415'] = p14['operating_schools_count']
redist['schools_2425'] = p24['operating_schools_count']
redist['schools_diff'] = redist['schools_2425'] - redist['schools_1415']
redist['students_per_sch_1415'] = redist['k12_1415'] / redist['schools_1415']
redist['students_per_sch_2425'] = redist['k12_2425'] / redist['schools_2425']
redist['density_diff'] = redist['students_per_sch_2425'] - redist['students_per_sch_1415']

print("District Portfolio Matrix (Enrollment Direction vs School Count Direction, Balanced 75):")
matrix = pd.crosstab(
    np.sign(redist['change_abs']).map({1: 'Enrollment Grew', -1: 'Enrollment Shrank', 0: 'Flat'}),
    np.sign(redist['schools_diff']).map({1: 'Schools Added', -1: 'Schools Closed', 0: 'Schools Unchanged'})
)
print(matrix)

print("\nDeclining districts that kept SAME number of schools (campus density hollowed out):")
decl_same = redist[(redist['change_abs'] < -200) & (redist['schools_diff'] == 0)].sort_values(by='change_abs')
print(decl_same[['district_name', 'state', 'k12_1415', 'k12_2425', 'change_abs', 'schools_2425', 'students_per_sch_1415', 'students_per_sch_2425', 'density_diff']].head(6).to_string())

print("\nGrowing districts that ADDED schools:")
grow_added = redist[(redist['change_abs'] > 200) & (redist['schools_diff'] > 0)].sort_values(by='change_abs', ascending=False)
print(grow_added[['district_name', 'state', 'k12_1415', 'k12_2425', 'change_abs', 'schools_diff', 'students_per_sch_1415', 'students_per_sch_2425']].head(6).to_string())

print("\n" + "="*75)
print("7. EXPLORATORY ANALYSIS E: PRE-K STRUCTURE")
print("="*75)
pk_tot = sch_2425['enrollment_pk'].fillna(0).sum()
pk_standalone = sch_2425[sch_2425['school_level'] == 'Prekindergarten']['enrollment_pk'].fillna(0).sum()
pk_integrated = pk_tot - pk_standalone
print(f"Total Pre-K in Campus Universe: {pk_tot:,}")
print(f"Standalone Pre-K Centers: {pk_standalone:,} ({pk_standalone/pk_tot*100:.1f}%)")
print(f"Integrated Pre-K in Elementary/Other: {pk_integrated:,} ({pk_integrated/pk_tot*100:.1f}%)")

print("\n" + "="*75)
print("8. EXPLORATORY ANALYSIS F: CROSS-MEASURE ASSOCIATIONS (CRDC & COMPLEXITY)")
print("="*75)
# CRDC Course Class Sizes vs High School Enrollment in 2021-22 wave
crdc_latest = crdc_course_df[crdc_course_df['crdc_wave'] == '2021-22'].copy()
print(f"CRDC 2021-22 High Schools in dataset: {len(crdc_latest)}")

for subj in ['alg1', 'geom', 'alg2', 'bio', 'chem', 'phys']:
    col = f"mean_class_size_{subj}"
    valid = crdc_latest[['enrollment_k12', col]].dropna()
    valid = valid[valid[col] > 0]
    if len(valid) > 10:
        corr = valid['enrollment_k12'].corr(valid[col])
        mean_sz = valid[col].mean()
        med_sz = valid[col].median()
        print(f"  {subj.upper():<5} | N={len(valid):>3} | Mean Size: {mean_sz:>4.1f} | Med: {med_sz:>4.1f} | Corr with School K12 Enrollment: r = {corr:>+5.3f}")

# Complexity associations (SY 2023-24)
comp_24 = complexity_df[complexity_df['school_year'] == '2023-2024'].copy()
print(f"\nComplexity Panel (SY 2023-24, N={len(comp_24)}):")
for metric in ['idea_share', 'lep_share', 'chronic_absent_rate', 'frl_rate']:
    valid = comp_24[['enrollment_k12', metric]].dropna()
    if len(valid) > 20:
        corr = valid['enrollment_k12'].corr(valid[metric])
        print(f"  {metric:<20} | N={len(valid):>3} | Mean: {valid[metric].mean()*100:>5.1f}% | Corr with School Enrollment: r = {corr:>+5.3f}")

print("\nDone.")
