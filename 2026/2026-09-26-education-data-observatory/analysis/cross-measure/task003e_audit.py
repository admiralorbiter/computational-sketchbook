"""
Task 003E Verification Script:
1. Great-circle displacement of enrollment-weighted centroid vs. mean distance change.
2. School continuity re-audit across ALL operating schools (including enrollment_total == 0) and address/coordinate check.
3. CRDC wave-by-wave advanced course offering rates (small vs large).
4. Complexity table exact N audit and locale breakdown.
"""

import os
import pandas as pd
import numpy as np
import math

BASE_DIR = r"c:\Users\admir\Github\computational-sketchbook"
KC_DIR = os.path.join(BASE_DIR, "2026", "2026-09-23-kc-education-capacity")

lea_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_lea_capacity_long_2014_15_2024_25.csv"))
sch_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_capacity_long_2014_15_2024_25.csv"))
crdc_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_crdc_school_course_capacity_2013_14_2023_24.csv"))
comp_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_complexity_panel_2015_2024.csv"))

# 1. SPATIAL STATISTICS
print("="*75)
print("1. SPATIAL STATISTICS: CENTROID DISPLACEMENT VS MEAN DISTANCE")
print("="*75)

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8 # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# Centroids from task003d:
# 2014-15: 39.023576, -94.586733
# 2024-25: 39.026558, -94.591280
lat14, lon14 = 39.023576, -94.586733
lat24, lon24 = 39.026558, -94.591280

disp_miles = haversine(lat14, lon14, lat24, lon24)
disp_feet = disp_miles * 5280

print(f"2014-15 Weighted Centroid: Lat {lat14:.6f}, Lon {lon14:.6f}")
print(f"2024-25 Weighted Centroid: Lat {lat24:.6f}, Lon {lon24:.6f}")
print(f"Great-Circle Centroid Displacement: {disp_miles:.4f} miles ({disp_feet:.1f} feet)")
print(f"Enrollment-Weighted Mean Distance from Downtown: 15.0088 -> 14.9314 miles (change = -0.0774 miles)")

# 2. SCHOOL CONTINUITY RE-AUDIT
print("\n" + "="*75)
print("2. SCHOOL CONTINUITY RE-AUDIT (ALL OPERATING SCHOOLS REGARDLESS OF ENROLLMENT)")
print("="*75)

leas_1415 = set(lea_long[(lea_long['school_year']=='2014-2015') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
leas_2425 = set(lea_long[(lea_long['school_year']=='2024-2025') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
balanced_leas = sorted(list(leas_1415.intersection(leas_2425)))

# Slice A: All Operating Schools (including zero enrollment)
op_14 = sch_long[(sch_long['school_year']=='2014-2015') & (sch_long['nces_lea_id'].isin(balanced_leas)) & (sch_long['is_operating']==True)]
op_24 = sch_long[(sch_long['school_year']=='2024-2025') & (sch_long['nces_lea_id'].isin(balanced_leas)) & (sch_long['is_operating']==True)]

set_op14 = set(op_14['nces_school_id'])
set_op24 = set(op_24['nces_school_id'])

cont_op = set_op14.intersection(set_op24)
cl_op = set_op14 - set_op24
open_op = set_op24 - set_op14

print(f"All Operating Schools in Balanced 75: 2014={len(set_op14)}, 2024={len(set_op24)}")
print(f"Continuing Operating IDs: {len(cont_op)} ({len(cont_op)/len(set_op14)*100:.1f}%)")
print(f"Operating IDs Closed: {len(cl_op)} | Operating IDs Opened: {len(open_op)}")

# Address/coordinate matching for "closed" and "opened" schools to detect facility reconfigurations
cl_df = op_14[op_14['nces_school_id'].isin(cl_op)][['nces_school_id', 'school_name', 'nces_lea_id', 'latitude', 'longitude']].drop_duplicates()
op_new_df = op_24[op_24['nces_school_id'].isin(open_op)][['nces_school_id', 'school_name', 'nces_lea_id', 'latitude', 'longitude']].drop_duplicates()

same_building_reconfig = []
for _, r_cl in cl_df.iterrows():
    matches = op_new_df[op_new_df['nces_lea_id'] == r_cl['nces_lea_id']]
    for _, r_op in matches.iterrows():
        dist = haversine(r_cl['latitude'], r_cl['longitude'], r_op['latitude'], r_op['longitude'])
        if dist < 0.1: # within 500 feet
            same_building_reconfig.append({
                'lea_id': r_cl['nces_lea_id'],
                'old_id': r_cl['nces_school_id'],
                'old_name': r_cl['school_name'],
                'new_id': r_op['nces_school_id'],
                'new_name': r_op['school_name'],
                'dist_miles': dist
            })

print(f"\nDetected Administrative Reconfigurations in Same Physical Facility: N = {len(same_building_reconfig)}")
for m in same_building_reconfig:
    print(f"  LEA {m['lea_id']}: '{m['old_name']}' -> '{m['new_name']}' (dist = {m['dist_miles']:.3f} mi)")

# Examine 28 declining districts with unchanged count
pivot_enr = lea_long[lea_long['nces_lea_id'].isin(balanced_leas)].pivot(index='nces_lea_id', columns='school_year', values='enrollment_k12')
lea_names = lea_long.groupby('nces_lea_id').first()[['district_name', 'state']]

decl_districts = []
for lid in balanced_leas:
    s14 = set(op_14[op_14['nces_lea_id']==lid]['nces_school_id'])
    s24 = set(op_24[op_24['nces_lea_id']==lid]['nces_school_id'])
    e14 = pivot_enr.loc[lid, '2014-2015']
    e24 = pivot_enr.loc[lid, '2024-2025']
    e_diff = e24 - e14
    c_diff = len(s24) - len(s14)
    cl = s14 - s24
    op = s24 - s14
    if e_diff < 0 and c_diff == 0:
        decl_districts.append({
            'lea_id': lid, 'district_name': lea_names.loc[lid, 'district_name'],
            'state': lea_names.loc[lid, 'state'],
            'count_14': len(s14), 'count_24': len(s24),
            'continuing': len(s14.intersection(s24)),
            'closed': len(cl), 'opened': len(op),
            'e_diff': e_diff, 'is_identical': (len(cl)==0 and len(op)==0)
        })

decl_df = pd.DataFrame(decl_districts)
print(f"\nAll Declining Districts with Unchanged Operating School Count: N = {len(decl_df)}")
print(f"Identical Operating School IDs kept: {decl_df['is_identical'].sum()} of {len(decl_df)} ({decl_df['is_identical'].mean()*100:.1f}%)")

decl_severe = decl_df[decl_df['e_diff'] < -200]
print(f"Districts losing > 200 students with unchanged operating count: N = {len(decl_severe)}")
print(f"Identical Operating School IDs kept (>200 loss): {decl_severe['is_identical'].sum()} of {len(decl_severe)} ({decl_severe['is_identical'].mean()*100:.1f}%)")
print(decl_severe[['district_name', 'state', 'count_14', 'continuing', 'closed', 'opened', 'e_diff', 'is_identical']].to_string())

# 3. CRDC ADVANCED COURSE OFFERINGS WAVE-BY-WAVE
print("\n" + "="*75)
print("3. CRDC ADVANCED COURSE OFFERINGS: WAVE-BY-WAVE SMALL (<400) VS LARGE (1600+)")
print("="*75)

crdc_reg_hs = crdc_df[(crdc_df['is_operating']==True) & (crdc_df['school_type']=='Regular School') & (crdc_df['school_level']=='High') & (crdc_df['enrollment_k12']>0)].copy()
crdc_reg_hs['has_calc'] = (crdc_reg_hs['classes_calc'] > 0) | (crdc_reg_hs['enrollment_calc'] > 0)
crdc_reg_hs['has_phys'] = (crdc_reg_hs['classes_phys'] > 0) | (crdc_reg_hs['enrollment_phys'] > 0)

for w in sorted(crdc_reg_hs['crdc_wave'].unique()):
    sub = crdc_reg_hs[crdc_reg_hs['crdc_wave']==w]
    sm = sub[sub['enrollment_k12'] < 400]
    lg = sub[sub['enrollment_k12'] >= 1600]
    sm_calc = sm['has_calc'].mean()*100 if len(sm)>0 else np.nan
    lg_calc = lg['has_calc'].mean()*100 if len(lg)>0 else np.nan
    sm_phys = sm['has_phys'].mean()*100 if len(sm)>0 else np.nan
    lg_phys = lg['has_phys'].mean()*100 if len(lg)>0 else np.nan
    print(f"Wave {w:<7} | Small N={len(sm):>2}, Large N={len(lg):>2} | Calc: Small={sm_calc:>5.1f}% vs Large={lg_calc:>5.1f}% | Phys: Small={sm_phys:>5.1f}% vs Large={lg_phys:>5.1f}%")

# 4. COMPLEXITY TABLE EXACT N RECOUNT (SY 2023-24)
print("\n" + "="*75)
print("4. COMPLEXITY TABLE EXACT N RECOUNT (SY 2023-24)")
print("="*75)

comp_24 = comp_df[comp_df['school_year']=='2023-2024'].copy()
print(f"Total Records in 2023-24: N = {len(comp_24)}")
print(f"Total Operating: N = {len(comp_24[comp_24['is_operating']==True])}")

comp_reg_op = comp_24[(comp_24['is_operating']==True) & (comp_24['school_type']=='Regular School')]
print(f"Regular Operating Schools in 2023-24: N = {len(comp_reg_op)}")
print(f"  Valid IDEA records: N = {comp_reg_op['idea_share'].notna().sum()}")
print(f"  Valid FRL records:  N = {comp_reg_op['frl_rate'].notna().sum()}")
print(f"  Valid EL records:   N = {comp_reg_op['lep_share'].notna().sum()}")
print(f"  Valid 504 records:  N = {comp_reg_op['section_504_share'].notna().sum()}")

# Regular High Schools by Locale in 2023-24
hs_reg_op = comp_reg_op[comp_reg_op['school_level']=='High']
print(f"\nRegular Operating High Schools: N = {len(hs_reg_op)}")
for loc, grp in hs_reg_op.groupby('locale_group'):
    r_frl = grp[['enrollment_k12', 'frl_rate']].dropna().corr().iloc[0,1]
    r_idea = grp[['enrollment_k12', 'idea_share']].dropna().corr().iloc[0,1]
    r_el = grp[['enrollment_k12', 'lep_share']].dropna().corr().iloc[0,1]
    print(f"  {loc:<8} (N={len(grp):>2}) | FRL r = {r_frl:>+6.3f} | IDEA r = {r_idea:>+6.3f} | EL r = {r_el:>+6.3f}")

print("\nAudit check script complete.")
