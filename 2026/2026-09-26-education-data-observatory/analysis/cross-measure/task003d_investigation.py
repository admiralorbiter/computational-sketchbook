"""
Task 003D Deep Investigation Script:
Executing Parts 2 through 8 of Task 003D mandate:
- Part 2: Fall-2020 Shock / Recovery Typology
- Part 3: Kindergarten as a Leading Indicator
- Part 4: Longitudinal Geographic Redistribution (Distance bands & weighted centroid)
- Part 5: School Opening/Closure Dynamics using NCESSCH IDs
- Part 6: Charter Substitution Analysis in KCPS urban footprint
- Part 7: High-School Scale & Curricular Breadth (CRDC multi-wave)
- Part 8: Demographic Complexity with Stratification
"""

# [HISTORICAL / EXPLORATORY SCRIPT — TASK 003D]
# Note: For canonical audited Task 003E findings, see measures/EDU-002-student-enrollment/README.md.

import os
from pathlib import Path
import pandas as pd
import numpy as np

# Path resolution
script_dir = Path(__file__).resolve().parent
repo_dir = script_dir.parent.parent
KC_DIR = repo_dir.parent / "2026-09-23-kc-education-capacity"

lea_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_lea_capacity_long_2014_15_2024_25.csv"))
sch_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_capacity_long_2014_15_2024_25.csv"))
crdc_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_crdc_school_course_capacity_2013_14_2023_24.csv"))
comp_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_complexity_panel_2015_2024.csv"))

# Balanced 75 cohort definition
leas_1415 = set(lea_long[(lea_long['school_year']=='2014-2015') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
leas_2425 = set(lea_long[(lea_long['school_year']=='2024-2025') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
balanced_leas = sorted(list(leas_1415.intersection(leas_2425)))
print(f"Balanced LEAs: N = {len(balanced_leas)}")

# ==============================================================================
# PART 2 — FALL-2020 SHOCK / RECOVERY TYPOLOGY
# ==============================================================================
print("\n" + "="*80)
print("PART 2: FALL-2020 SHOCK / RECOVERY TYPOLOGY (BALANCED 75 LEAs)")
print("="*80)

lea_bal = lea_long[lea_long['nces_lea_id'].isin(balanced_leas)].copy()
pivot_enr = lea_bal.pivot(index='nces_lea_id', columns='school_year', values='enrollment_k12')
lea_names = lea_bal.groupby('nces_lea_id').first()[['district_name', 'state', 'county_primary']]

typology = pd.DataFrame(index=pivot_enr.index)
typology['district_name'] = lea_names['district_name']
typology['state'] = lea_names['state']
typology['county'] = lea_names['county_primary']
typology['e_2019'] = pivot_enr['2019-2020']
typology['e_2020'] = pivot_enr['2020-2021']
typology['e_2024'] = pivot_enr['2024-2025']

typology['shock_pct'] = (typology['e_2020'] - typology['e_2019']) / typology['e_2019'] * 100
typology['recov_abs'] = typology['e_2024'] - typology['e_2020']
typology['net_from_peak_pct'] = (typology['e_2024'] - typology['e_2019']) / typology['e_2019'] * 100

def classify_trajectory(r):
    if r['e_2024'] >= r['e_2019']:
        if r['e_2020'] >= r['e_2019']:
            return "Continued Growth (No 2020 Drop)"
        else:
            return "Exceeded Pre-2020 Peak"
    elif r['e_2024'] > r['e_2020']:
        return "Partial Recovery"
    else:
        return "Persistent Decline"

typology['category'] = typology.apply(classify_trajectory, axis=1)

typ_summary = typology.groupby('category').agg(
    district_count=('district_name', 'count'),
    students_2019=('e_2019', 'sum'),
    students_2024=('e_2024', 'sum'),
    net_change=('e_2024', lambda s: (typology.loc[s.index, 'e_2024'] - typology.loc[s.index, 'e_2019']).sum())
).reset_index()
typ_summary['pct_districts'] = typ_summary['district_count'] / typ_summary['district_count'].sum() * 100
typ_summary['pct_students_2024'] = typ_summary['students_2024'] / typ_summary['students_2024'].sum() * 100

print(typ_summary.to_string())

# ==============================================================================
# PART 3 — KINDERGARTEN AS A LEADING INDICATOR
# ==============================================================================
print("\n" + "="*80)
print("PART 3: KINDERGARTEN AS A LEADING INDICATOR")
print("="*80)

kg_bal = lea_bal.groupby('school_year').agg(
    enr_kg=('enrollment_kg', 'sum'),
    enr_k12=('enrollment_k12', 'sum')
).reset_index()
kg_bal['enr_1_12'] = kg_bal['enr_k12'] - kg_bal['enr_kg']
kg_bal['kg_share_pct'] = kg_bal['enr_kg'] / kg_bal['enr_k12'] * 100
kg_bal['kg_index'] = kg_bal['enr_kg'] / kg_bal['enr_kg'].iloc[0] * 100
kg_bal['k12_index'] = kg_bal['enr_k12'] / kg_bal['enr_k12'].iloc[0] * 100
kg_bal['grades1_12_index'] = kg_bal['enr_1_12'] / kg_bal['enr_1_12'].iloc[0] * 100

print("Year        KG Enrollment    KG Share (%)    KG Index    Grades 1-12 Index    Total K-12 Index")
print("-" * 85)
for _, r in kg_bal.iterrows():
    print(f"{r['school_year']:<10}  {r['enr_kg']:>12,.0f}    {r['kg_share_pct']:>11.2f}%   {r['kg_index']:>9.2f}    {r['grades1_12_index']:>16.2f}    {r['k12_index']:>15.2f}")

kg_14 = kg_bal['enr_kg'].iloc[0]
kg_19 = kg_bal[kg_bal['school_year']=='2019-2020']['enr_kg'].values[0]
kg_20 = kg_bal[kg_bal['school_year']=='2020-2021']['enr_kg'].values[0]
kg_24 = kg_bal['enr_kg'].iloc[-1]

print(f"\nKindergarten 10-Yr Change (2014-15 to 2024-25): {kg_14:,.0f} -> {kg_24:,.0f} ({kg_24 - kg_14:+,.0f}, {(kg_24 - kg_14)/kg_14*100:+.2f}%)")
print(f"Grades 1-12 10-Yr Change:   {(kg_bal['enr_1_12'].iloc[-1] - kg_bal['enr_1_12'].iloc[0]):+,.0f} ({(kg_bal['enr_1_12'].iloc[-1] - kg_bal['enr_1_12'].iloc[0])/kg_bal['enr_1_12'].iloc[0]*100:+.2f}%)")
print(f"Kindergarten Fall 2020 Shock (2019 to 2020): {kg_19:,.0f} -> {kg_20:,.0f} ({kg_20 - kg_19:+,.0f}, {(kg_20 - kg_19)/kg_19*100:+.2f}%)")
print(f"Kindergarten Post-2019 Change (2019-20 to 2024-25): {kg_19:,.0f} -> {kg_24:,.0f} ({kg_24 - kg_19:+,.0f}, {(kg_24 - kg_19)/kg_19*100:+.2f}%)")

# ==============================================================================
# PART 4 — LONGITUDINAL GEOGRAPHIC REDISTRIBUTION
# ==============================================================================
print("\n" + "="*80)
print("PART 4: LONGITUDINAL GEOGRAPHIC REDISTRIBUTION (DISTANCE BANDS & CENTROID)")
print("="*80)

sch_valid = sch_long[(sch_long['enrollment_total'] > 0) & (sch_long['distance_downtown_kc_miles'].notna())].copy()
sch_valid['dist_band'] = pd.cut(
    sch_valid['distance_downtown_kc_miles'],
    bins=[0, 5, 10, 15, 20, 30, 150],
    labels=['0-5 mi', '5-10 mi', '10-15 mi', '15-20 mi', '20-30 mi', '30+ mi']
)

dist_by_yr = sch_valid.groupby(['school_year', 'dist_band'], observed=False)['enrollment_total'].sum().unstack()
dist_pct_by_yr = dist_by_yr.div(dist_by_yr.sum(axis=1), axis=0) * 100

print("Distance Band Enrollment Shares Over Time (% of Total Campus Enrollment):")
print(dist_pct_by_yr[['0-5 mi', '5-10 mi', '10-15 mi', '15-20 mi', '20-30 mi', '30+ mi']].to_string())

centroids = []
for yr, grp in sch_valid.groupby('school_year'):
    w = grp['enrollment_total']
    w_lat = np.average(grp['latitude'], weights=w)
    w_lon = np.average(grp['longitude'], weights=w)
    w_dist = np.average(grp['distance_downtown_kc_miles'], weights=w)
    centroids.append({'school_year': yr, 'w_lat': w_lat, 'w_lon': w_lon, 'w_dist_miles': w_dist, 'total_enr': w.sum()})

cent_df = pd.DataFrame(centroids)
print("\nEnrollment-Weighted Geographic Centroid & Mean Distance from Downtown:")
print(cent_df[['school_year', 'w_lat', 'w_lon', 'w_dist_miles', 'total_enr']].to_string())
d_shift = cent_df.iloc[-1]['w_dist_miles'] - cent_df.iloc[0]['w_dist_miles']
print(f"\nNet Shift in Enrollment-Weighted Distance from Downtown KC (2014-15 to 2024-25): {d_shift:+.3f} miles")

# ==============================================================================
# PART 5 — SCHOOL OPENING / CLOSURE DYNAMICS (USING NCESSCH IDs)
# ==============================================================================
print("\n" + "="*80)
print("PART 5: SCHOOL OPENING / CLOSURE DYNAMICS (USING NCESSCH IDs)")
print("="*80)

sch_14 = sch_long[(sch_long['school_year']=='2014-2015') & (sch_long['nces_lea_id'].isin(balanced_leas)) & (sch_long['is_operating']==True) & (sch_long['enrollment_total']>0)]
sch_24 = sch_long[(sch_long['school_year']=='2024-2025') & (sch_long['nces_lea_id'].isin(balanced_leas)) & (sch_long['is_operating']==True) & (sch_long['enrollment_total']>0)]

set_14 = set(sch_14['nces_school_id'])
set_24 = set(sch_24['nces_school_id'])

continuing_ids = set_14.intersection(set_24)
closed_ids = set_14 - set_24
opened_ids = set_24 - set_14

print(f"Total Operating Schools with Enrollment in Balanced 75 (2014-15): {len(set_14)}")
print(f"Total Operating Schools with Enrollment in Balanced 75 (2024-25): {len(set_24)}")
print(f"Continuing Campuses (Both Endpoints): {len(continuing_ids)} ({len(continuing_ids)/len(set_14)*100:.1f}% of 2014 plants)")
print(f"Closed / Shuttered Campuses (in 2014, not 2024): {len(closed_ids)}")
print(f"Newly Opened Campuses (in 2024, not 2014): {len(opened_ids)}")
print(f"Net Campus Change: {len(opened_ids) - len(closed_ids):+d}")

lea_port = []
for lid in balanced_leas:
    s14 = set(sch_14[sch_14['nces_lea_id']==lid]['nces_school_id'])
    s24 = set(sch_24[sch_24['nces_lea_id']==lid]['nces_school_id'])
    cont = s14.intersection(s24)
    op = s24 - s14
    cl = s14 - s24
    name = lea_names.loc[lid, 'district_name']
    st = lea_names.loc[lid, 'state']
    lea_port.append({
        'nces_lea_id': lid, 'district_name': name, 'state': st,
        'count_14': len(s14), 'count_24': len(s24), 'count_diff': len(s24) - len(s14),
        'continuing': len(cont), 'opened': len(op), 'closed': len(cl),
        'net_change_id': len(op) - len(cl)
    })

port_df = pd.DataFrame(lea_port).set_index('nces_lea_id')
port_df['change_abs_10yr'] = typology['e_2024'] - pivot_enr['2014-2015']

decl_same = port_df[(port_df['change_abs_10yr'] < -200) & (port_df['count_diff'] == 0)]
print(f"\nDeclining Districts (loss > 200) with Unchanged School Count (N={len(decl_same)}):")
identical_ids = (decl_same['closed'] == 0) & (decl_same['opened'] == 0)
print(f"  Identical Campuses Kept: {identical_ids.sum()} of {len(decl_same)} districts ({identical_ids.sum()/len(decl_same)*100:.1f}%)")
print(f"  Reconfigured Campuses (closed & opened): {(~identical_ids).sum()} districts")
print(decl_same[['district_name', 'state', 'count_14', 'count_24', 'continuing', 'opened', 'closed', 'change_abs_10yr']].head(10).to_string())

# ==============================================================================
# PART 6 — CHARTER SUBSTITUTION IN KANSAS CITY 33 (KCPS) URBAN FOOTPRINT
# ==============================================================================
print("\n" + "="*80)
print("PART 6: CHARTER SUBSTITUTION IN KANSAS CITY 33 (KCPS) URBAN FOOTPRINT")
print("="*80)

kcps_id = 2916400  # KANSAS CITY 33 (verified NCES LEA ID)

charter_leas_long = set(sch_long[(sch_long['state']=='MO') & (sch_long['county_name']=='Jackson County') & (sch_long['is_charter']==True) & (sch_long['nces_lea_id'] != kcps_id)]['nces_lea_id'])
print(f"Independent Charter LEAs in Jackson County, MO: N = {len(charter_leas_long)}")

urban_panel = []
for yr in sorted(lea_long['school_year'].unique()):
    kcps_row = lea_long[(lea_long['school_year']==yr) & (lea_long['nces_lea_id']==kcps_id)]
    kcps_enr = kcps_row['enrollment_k12'].values[0] if len(kcps_row)>0 else 0
    
    chart_rows = lea_long[(lea_long['school_year']==yr) & (lea_long['nces_lea_id'].isin(charter_leas_long))]
    chart_enr = chart_rows['enrollment_k12'].sum()
    chart_count = len(chart_rows[chart_rows['enrollment_k12']>0])
    
    comb_enr = kcps_enr + chart_enr
    chart_share = chart_enr / comb_enr * 100 if comb_enr > 0 else 0
    
    urban_panel.append({
        'school_year': yr,
        'kcps_k12': kcps_enr,
        'charter_k12': chart_enr,
        'charter_leas_active': chart_count,
        'combined_k12': comb_enr,
        'charter_share_pct': chart_share
    })

urban_df = pd.DataFrame(urban_panel)
print("Urban Public School Enrollment (KCPS vs. Jackson County Charters, K-12 Headcount):")
print(urban_df.to_string(index=False))

# ==============================================================================
# PART 7 — HIGH-SCHOOL SCALE AND CURRICULAR BREADTH (CRDC)
# ==============================================================================
print("\n" + "="*80)
print("PART 7: HIGH-SCHOOL SCALE AND CURRICULAR BREADTH (CRDC MULTI-WAVE)")
print("="*80)

# Restrict strictly to: operating, regular high schools
crdc_reg_hs = crdc_df[(crdc_df['is_operating']==True) & (crdc_df['school_type']=='Regular School') & (crdc_df['school_level']=='High') & (crdc_df['enrollment_k12']>0)].copy()

print(f"Regular Operating High Schools in CRDC Dataset across waves: N = {len(crdc_reg_hs)}")
print("Count by wave:")
print(crdc_reg_hs.groupby('crdc_wave')['nces_school_id'].count())

crdc_reg_hs['has_alg2'] = (crdc_reg_hs['classes_alg2'] > 0) | (crdc_reg_hs['enrollment_alg2'] > 0)
crdc_reg_hs['has_phys'] = (crdc_reg_hs['classes_phys'] > 0) | (crdc_reg_hs['enrollment_phys'] > 0)
crdc_reg_hs['has_calc'] = (crdc_reg_hs['classes_calc'] > 0) | (crdc_reg_hs['enrollment_calc'] > 0)
crdc_reg_hs['has_chem'] = (crdc_reg_hs['classes_chem'] > 0) | (crdc_reg_hs['enrollment_chem'] > 0)
crdc_reg_hs['adv_course_count'] = crdc_reg_hs[['has_alg2', 'has_phys', 'has_calc', 'has_chem']].sum(axis=1)

crdc_reg_hs['size_band'] = pd.cut(
    crdc_reg_hs['enrollment_k12'],
    bins=[0, 400, 800, 1200, 1600, 99999],
    labels=['<400', '400-799', '800-1199', '1200-1599', '1600+'],
    right=False
)

print("\n--- Advanced Course Offering Rates by High School Enrollment Size Band (All Waves Pooled, N={}):".format(len(crdc_reg_hs)))
offer_by_band = crdc_reg_hs.groupby('size_band', observed=False).agg(
    n_schools=('nces_school_id', 'count'),
    mean_enr=('enrollment_k12', 'mean'),
    pct_alg2=('has_alg2', lambda s: s.mean()*100),
    pct_chem=('has_chem', lambda s: s.mean()*100),
    pct_phys=('has_phys', lambda s: s.mean()*100),
    pct_calc=('has_calc', lambda s: s.mean()*100),
    avg_adv_courses=('adv_course_count', 'mean')
).reset_index()
print(offer_by_band.to_string())

print("\n--- 2021-22 Wave Specifically (N={}):".format(len(crdc_reg_hs[crdc_reg_hs['crdc_wave']=='2021-22'])))
offer_2122 = crdc_reg_hs[crdc_reg_hs['crdc_wave']=='2021-22'].groupby('size_band', observed=False).agg(
    n_schools=('nces_school_id', 'count'),
    pct_alg2=('has_alg2', lambda s: s.mean()*100),
    pct_chem=('has_chem', lambda s: s.mean()*100),
    pct_phys=('has_phys', lambda s: s.mean()*100),
    pct_calc=('has_calc', lambda s: s.mean()*100),
    avg_adv_courses=('adv_course_count', 'mean')
).reset_index()
print(offer_2122.to_string())

# Correlations between school enrollment and school-course mean class size by wave
print("\n--- Correlations: School K-12 Enrollment vs School-Course Mean Class Size by Wave (Regular High Schools Only) ---")
waves = ['2015-16', '2017-18', '2020-21', '2021-22']
corrs = []
for w in waves:
    sub = crdc_reg_hs[crdc_reg_hs['crdc_wave']==w]
    row = {'wave': w, 'n_hs': len(sub)}
    for subj in ['alg1', 'geom', 'alg2', 'bio', 'chem', 'phys']:
        col = f"mean_class_size_{subj}"
        valid = sub[['enrollment_k12', col]].dropna()
        valid = valid[valid[col] > 0]
        if len(valid) >= 15:
            r = valid['enrollment_k12'].corr(valid[col])
            row[subj] = r
        else:
            row[subj] = np.nan
    corrs.append(row)

corr_df = pd.DataFrame(corrs).set_index('wave')
print("Correlations (r) across waves:")
print(corr_df[['alg1', 'geom', 'alg2', 'bio', 'chem', 'phys']].to_string())

# ==============================================================================
# PART 8 — COMPLEXITY ASSOCIATIONS WITH STRATIFICATION
# ==============================================================================
print("\n" + "="*80)
print("PART 8: DEMOGRAPHIC COMPLEXITY ASSOCIATIONS WITH STRATIFICATION")
print("="*80)

comp_latest = comp_df[comp_df['school_year']=='2023-2024'].copy()

# Stratification 1: Regular vs Specialized
print("\nPooled vs. Regular vs. Specialized Schools (SY 2023-24):")
for metric in ['idea_share', 'lep_share', 'frl_rate']:
    r_pool = comp_latest[['enrollment_k12', metric]].dropna().corr().iloc[0,1]
    r_reg = comp_latest[comp_latest['school_type']=='Regular School'][['enrollment_k12', metric]].dropna().corr().iloc[0,1]
    r_spec = comp_latest[comp_latest['school_type']!='Regular School'][['enrollment_k12', metric]].dropna().corr().iloc[0,1]
    print(f"  {metric:<15} | Pooled: r = {r_pool:>+6.3f} | Regular Only: r = {r_reg:>+6.3f} | Specialized: r = {r_spec:>+6.3f}")

# Stratification 2: By Grade Band (Regular Schools Only)
print("\nBy Grade Band (Regular Operating Schools Only, SY 2023-24):")
comp_reg = comp_latest[comp_latest['school_type']=='Regular School'].copy()
for lvl in ['Elementary', 'Middle', 'High']:
    sub = comp_reg[comp_reg['school_level']==lvl]
    r_idea = sub[['enrollment_k12', 'idea_share']].dropna().corr().iloc[0,1]
    r_lep = sub[['enrollment_k12', 'lep_share']].dropna().corr().iloc[0,1]
    r_frl = sub[['enrollment_k12', 'frl_rate']].dropna().corr().iloc[0,1]
    print(f"  {lvl:<12} (N={len(sub):>3}) | IDEA: r = {r_idea:>+6.3f} | LEP: r = {r_lep:>+6.3f} | FRL: r = {r_frl:>+6.3f}")

# Stratification 3: High Schools by Locale (Regular High Schools Only)
print("\nRegular High Schools by Locale Group (SY 2023-24):")
comp_reg_hs = comp_reg[comp_reg['school_level']=='High'].copy()
for loc in ['City', 'Suburb', 'Town', 'Rural']:
    sub = comp_reg_hs[comp_reg_hs['locale_group']==loc]
    if len(sub) >= 5:
        r_idea = sub[['enrollment_k12', 'idea_share']].dropna().corr().iloc[0,1]
        r_frl = sub[['enrollment_k12', 'frl_rate']].dropna().corr().iloc[0,1]
        print(f"  {loc:<8} (N={len(sub):>2}) | IDEA: r = {r_idea:>+6.3f} | FRL: r = {r_frl:>+6.3f}")

print("\nDeep investigation run completed successfully.")
