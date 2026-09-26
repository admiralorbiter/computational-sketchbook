"""
Task 004C Reconciliation Script:
Reproducing every EDU-003 claim from raw canonical data panels,
identifying the origins of discrepancies, and preparing machine-readable claim entries.
"""

from pathlib import Path
import pandas as pd
import numpy as np

OBS_DIR = Path(__file__).resolve().parents[2]
KC_DIR = OBS_DIR.parent / "2026-09-23-kc-education-capacity"

lea_long = pd.read_csv(KC_DIR / "data" / "processed" / "kc_lea_capacity_long_2014_15_2024_25.csv")
sch_long = pd.read_csv(KC_DIR / "data" / "processed" / "kc_school_capacity_long_2014_15_2024_25.csv")
crdc_df = pd.read_csv(KC_DIR / "data" / "processed" / "kc_crdc_school_course_capacity_2013_14_2023_24.csv")

print("=" * 80)
print("TASK 004C: NUMERICAL RECONCILIATION & REPRODUCIBILITY AUDIT")
print("=" * 80)

# ------------------------------------------------------------------------------
# 1. REGIONAL TEACHER TRAJECTORIES
# ------------------------------------------------------------------------------
print("\n" + "=" * 80)
print("1. REGIONAL TEACHER TRAJECTORIES ACROSS CANDIDATE UNIVERSES")
print("=" * 80)

# Balanced 75 LEAs
leas_1415 = set(lea_long[(lea_long['school_year'] == '2014-2015') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
leas_2425 = set(lea_long[(lea_long['school_year'] == '2024-2025') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
b75 = sorted(list(leas_1415.intersection(leas_2425)))
print(f"Balanced 75 LEA Count: N = {len(b75)}")

lea_b75 = lea_long[lea_long['nces_lea_id'].isin(b75)].copy()
b75_14_k12 = lea_b75[lea_b75['school_year'] == '2014-2015']['teachers_k12_fte'].sum()
b75_24_k12 = lea_b75[lea_b75['school_year'] == '2024-2025']['teachers_k12_fte'].sum()
b75_chg_k12 = b75_24_k12 - b75_14_k12
b75_pct_k12 = b75_chg_k12 / b75_14_k12 * 100

b75_14_tot = lea_b75[lea_b75['school_year'] == '2014-2015']['teachers_total_reported_fte'].sum()
b75_24_tot = lea_b75[lea_b75['school_year'] == '2024-2025']['teachers_total_reported_fte'].sum()
b75_chg_tot = b75_24_tot - b75_14_tot
b75_pct_tot = b75_chg_tot / b75_14_tot * 100

print(f"Balanced 75 LEA K-12 Teachers:       {b75_14_k12:,.2f} -> {b75_24_k12:,.2f} ({b75_chg_k12:+,.2f}, {b75_pct_k12:+.2f}%)")
print(f"Balanced 75 LEA Total Teachers:      {b75_14_tot:,.2f} -> {b75_24_tot:,.2f} ({b75_chg_tot:+,.2f}, {b75_pct_tot:+.2f}%)")

# Campus sums in Balanced 75 LEAs
sch_b75 = sch_long[sch_long['nces_lea_id'].isin(b75)].copy()
sch_b75_14 = sch_b75[sch_b75['school_year'] == '2014-2015']['classroom_teacher_fte'].sum()
sch_b75_24 = sch_b75[sch_b75['school_year'] == '2024-2025']['classroom_teacher_fte'].sum()
print(f"Campus Sum in Balanced 75 LEAs:      {sch_b75_14:,.2f} -> {sch_b75_24:,.2f} ({sch_b75_24 - sch_b75_14:+,.2f}, {(sch_b75_24 - sch_b75_14)/sch_b75_14*100:+.2f}%)")

# Dynamic fully regional LEAs
lea_dyn_14 = lea_long[(lea_long['school_year'] == '2014-2015') & (lea_long['lea_fully_within_region'] == True)]
lea_dyn_24 = lea_long[(lea_long['school_year'] == '2024-2025') & (lea_long['lea_fully_within_region'] == True)]
dyn_14_k12 = lea_dyn_14['teachers_k12_fte'].sum()
dyn_24_k12 = lea_dyn_24['teachers_k12_fte'].sum()
dyn_14_tot = lea_dyn_14['teachers_total_reported_fte'].sum()
dyn_24_tot = lea_dyn_24['teachers_total_reported_fte'].sum()
print(f"\nDynamic Fully Regional (N={len(lea_dyn_14)} -> N={len(lea_dyn_24)}):")
print(f"  LEA K-12 Teachers:                 {dyn_14_k12:,.2f} -> {dyn_24_k12:,.2f} ({dyn_24_k12 - dyn_14_k12:+,.2f}, {(dyn_24_k12 - dyn_14_k12)/dyn_14_k12*100:+.2f}%)")
print(f"  LEA Total Teachers:                {dyn_14_tot:,.2f} -> {dyn_24_tot:,.2f} ({dyn_24_tot - dyn_14_tot:+,.2f}, {(dyn_24_tot - dyn_14_tot)/dyn_14_tot*100:+.2f}%)")

sch_dyn_14 = sch_long[(sch_long['school_year'] == '2014-2015') & (sch_long['nces_lea_id'].isin(lea_dyn_14['nces_lea_id']))]['classroom_teacher_fte'].sum()
sch_dyn_24 = sch_long[(sch_long['school_year'] == '2024-2025') & (sch_long['nces_lea_id'].isin(lea_dyn_24['nces_lea_id']))]['classroom_teacher_fte'].sum()
print(f"  Campus Classroom Teachers:         {sch_dyn_14:,.2f} -> {sch_dyn_24:,.2f} ({sch_dyn_24 - sch_dyn_14:+,.2f}, {(sch_dyn_24 - sch_dyn_14)/sch_dyn_14*100:+.2f}%)")

# What about all schools in the regional school panel?
sch_all_14 = sch_long[sch_long['school_year'] == '2014-2015']['classroom_teacher_fte'].sum()
sch_all_24 = sch_long[sch_long['school_year'] == '2024-2025']['classroom_teacher_fte'].sum()
print(f"\nAll Schools in Regional School Panel (N={len(sch_long[sch_long['school_year'] == '2014-2015'])} -> N={len(sch_long[sch_long['school_year'] == '2024-2025'])}):")
print(f"  Campus Classroom Teachers:         {sch_all_14:,.2f} -> {sch_all_24:,.2f} ({sch_all_24 - sch_all_14:+,.2f}, {(sch_all_24 - sch_all_14)/sch_all_14*100:+.2f}%)")

# What about 77 current fully regional LEAs evaluated in 2014-15 and 2024-25?
lea_curr77 = lea_long[lea_long['nces_lea_id'].isin(leas_2425)]
c77_14_k12 = lea_curr77[lea_curr77['school_year'] == '2014-2015']['teachers_k12_fte'].sum()
c77_24_k12 = lea_curr77[lea_curr77['school_year'] == '2024-2025']['teachers_k12_fte'].sum()
c77_14_tot = lea_curr77[lea_curr77['school_year'] == '2014-2015']['teachers_total_reported_fte'].sum()
c77_24_tot = lea_curr77[lea_curr77['school_year'] == '2024-2025']['teachers_total_reported_fte'].sum()
print(f"\nCurrent 77 LEAs tracked backward to 2014-15:")
print(f"  LEA K-12 Teachers:                 {c77_14_k12:,.2f} -> {c77_24_k12:,.2f} ({c77_24_k12 - c77_14_k12:+,.2f}, {(c77_24_k12 - c77_14_k12)/c77_14_k12*100:+.2f}%)")
print(f"  LEA Total Teachers:                {c77_14_tot:,.2f} -> {c77_24_tot:,.2f} ({c77_24_tot - c77_14_tot:+,.2f}, {(c77_24_tot - c77_14_tot)/c77_14_tot*100:+.2f}%)")

# Did 22,860.8 -> 24,028.9 come from anything in the data?
# Let's search all possible sums across years/groups
print(f"\nChecking origin of 22,860.8 -> 24,028.9 (+5.11%):")
print(f"  Notice 24,028.9 is close to lea_dyn_24 teachers_total_reported_fte ({dyn_24_tot:,.2f}) or teachers_k12_fte ({dyn_24_k12:,.2f})?")
print(f"  dyn_24_tot = {dyn_24_tot:.2f}, dyn_24_k12 = {dyn_24_k12:.2f}, b75_24_tot = {b75_24_tot:.2f}")

# ------------------------------------------------------------------------------
# 2. DECLINING LEA COHORTS
# ------------------------------------------------------------------------------
print("\n" + "=" * 80)
print("2. DECLINING DISTRICT STAFFING COHORTS")
print("=" * 80)

sch_bal = sch_long[sch_long['nces_lea_id'].isin(b75)].copy()
sch_cnt_14 = sch_bal[(sch_bal['school_year'] == '2014-2015') & (sch_bal['is_operating'] == True)].groupby('nces_lea_id').size()
sch_cnt_24 = sch_bal[(sch_bal['school_year'] == '2024-2025') & (sch_bal['is_operating'] == True)].groupby('nces_lea_id').size()

lea_14_b = lea_b75[lea_b75['school_year'] == '2014-2015'].set_index('nces_lea_id')
lea_24_b = lea_b75[lea_b75['school_year'] == '2024-2025'].set_index('nces_lea_id')

df_bal = pd.DataFrame(index=b75)
df_bal['district_name'] = lea_24_b['district_name']
df_bal['state'] = lea_24_b['state']
df_bal['enr_14'] = lea_14_b['enrollment_k12']
df_bal['enr_24'] = lea_24_b['enrollment_k12']
df_bal['enr_chg'] = df_bal['enr_24'] - df_bal['enr_14']
df_bal['tch_14'] = lea_14_b['teachers_k12_fte']
df_bal['tch_24'] = lea_24_b['teachers_k12_fte']
df_bal['tch_chg'] = df_bal['tch_24'] - df_bal['tch_14']
df_bal['sch_cnt_14'] = sch_cnt_14.reindex(b75).fillna(0)
df_bal['sch_cnt_24'] = sch_cnt_24.reindex(b75).fillna(0)
df_bal['sch_cnt_chg'] = df_bal['sch_cnt_24'] - df_bal['sch_cnt_14']

decliners_28 = df_bal[(df_bal['enr_chg'] < 0) & (df_bal['sch_cnt_chg'] == 0)].copy()
e14_28 = decliners_28['enr_14'].sum()
e24_28 = decliners_28['enr_24'].sum()
t14_28 = decliners_28['tch_14'].sum()
t24_28 = decliners_28['tch_24'].sum()
print(f"28 Declining LEAs (Unchanged School Count):")
print(f"  Enrollment: {e14_28:,.0f} -> {e24_28:,.0f} ({e24_28 - e14_28:+,.0f}, {(e24_28 - e14_28)/e14_28*100:+.2f}%)")
print(f"  Teachers:   {t14_28:,.2f} -> {t24_28:,.2f} ({t24_28 - t14_28:+,.2f}, {(t24_28 - t14_28)/t14_28*100:+.2f}%)")

# Check where -9.58% and +0.73% (-7,844 enr, +42.4 tch, 160 schools) could have come from!
# Could it be school-level sum for schools in declining districts?
sch_decl_28 = sch_bal[sch_bal['nces_lea_id'].isin(decliners_28.index)]
sch_decl_14 = sch_decl_28[sch_decl_28['school_year'] == '2014-2015']
sch_decl_24 = sch_decl_28[sch_decl_28['school_year'] == '2024-2025']
print(f"  School count in 28 LEAs: 2014-15 = {len(sch_decl_14[sch_decl_14['is_operating']==True])}, 2024-25 = {len(sch_decl_24[sch_decl_24['is_operating']==True])}")
sch_enr_14 = sch_decl_14['enrollment_k12'].sum()
sch_enr_24 = sch_decl_24['enrollment_k12'].sum()
sch_tch_14 = sch_decl_14['classroom_teacher_fte'].sum()
sch_tch_24 = sch_decl_24['classroom_teacher_fte'].sum()
print(f"  Campus Sums in 28 LEAs:")
print(f"    Enrollment: {sch_enr_14:,.0f} -> {sch_enr_24:,.0f} ({sch_enr_24 - sch_enr_14:+,.0f}, {(sch_enr_24 - sch_enr_14)/sch_enr_14*100:+.2f}%)")
print(f"    Teachers:   {sch_tch_14:,.2f} -> {sch_tch_24:,.2f} ({sch_tch_24 - sch_tch_14:+,.2f}, {(sch_tch_24 - sch_tch_14)/sch_tch_14*100:+.2f}%)")

# What about total declining LEAs (all LEAs with enr_chg < 0 regardless of school count)?
all_decl = df_bal[df_bal['enr_chg'] < 0]
print(f"\nAll Declining LEAs in B75 (N={len(all_decl)}):")
print(f"  Enrollment: {all_decl['enr_14'].sum():,.0f} -> {all_decl['enr_24'].sum():,.0f} ({all_decl['enr_24'].sum() - all_decl['enr_14'].sum():+,.0f}, {(all_decl['enr_24'].sum() - all_decl['enr_14'].sum())/all_decl['enr_14'].sum()*100:+.2f}%)")
print(f"  Teachers:   {all_decl['tch_14'].sum():,.2f} -> {all_decl['tch_24'].sum():,.2f} ({all_decl['tch_24'].sum() - all_decl['tch_14'].sum():+,.2f}, {(all_decl['tch_24'].sum() - all_decl['tch_14'].sum())/all_decl['tch_14'].sum()*100:+.2f}%)")

# ------------------------------------------------------------------------------
# 3. KANSAS & MISSOURI CAMPUS VS LEA RECONCILIATION
# ------------------------------------------------------------------------------
print("\n" + "=" * 80)
print("3. KANSAS & MISSOURI CAMPUS VS LEA RECONCILIATION (SY 2024-25)")
print("=" * 80)

# Current 77 fully regional LEAs
lea_77 = lea_long[(lea_long['school_year'] == '2024-2025') & (lea_long['lea_fully_within_region'] == True)].copy()
sch_77 = sch_long[(sch_long['school_year'] == '2024-2025') & (sch_long['nces_lea_id'].isin(lea_77['nces_lea_id']))].copy()

# Reconcile by state using teachers_k12_fte vs teachers_total_reported_fte
for st in ['KS', 'MO']:
    st_leas = lea_77[lea_77['state'] == st]
    st_schs = sch_77[sch_77['state'] == st]
    
    sch_sum = st_schs['classroom_teacher_fte'].sum()
    lea_k12_sum = st_leas['teachers_k12_fte'].sum()
    lea_tot_sum = st_leas['teachers_total_reported_fte'].sum()
    
    print(f"\nState {st} across 77 Regional LEAs (N={len(st_leas)} LEAs, {len(st_schs)} schools):")
    print(f"  Campus Sum (classroom_teacher_fte): {sch_sum:,.2f}")
    print(f"  LEA K-12 Sum (teachers_k12_fte):     {lea_k12_sum:,.2f} | Gap = {lea_k12_sum - sch_sum:+,.2f} ({(lea_k12_sum - sch_sum)/lea_k12_sum*100:+.2f}%)")
    print(f"  LEA Total Sum (teachers_total):      {lea_tot_sum:,.2f} | Gap = {lea_tot_sum - sch_sum:+,.2f} ({(lea_tot_sum - sch_sum)/lea_tot_sum*100:+.2f}%)")

# What about the entire Kansas/Missouri state or broader panel?
# Where did 10,076.92 and 10,532.18 come from?
print("\nInvestigating 10,076.92 -> 10,532.18:")
# Let's check subsets: e.g. regular schools only?
for st in ['KS', 'MO']:
    st_schs_reg = sch_77[(sch_77['state'] == st) & (sch_77['school_type'] == 1)]
    print(f"  {st} Regular Schools Campus Sum: {st_schs_reg['classroom_teacher_fte'].sum():,.2f}")
    # What about excluding Pre-K or kindergarten?
    # What about in 2023-24?
    for yr in ['2023-2024', '2024-2025']:
        sub_s = sch_long[(sch_long['school_year'] == yr) & (sch_long['state'] == st) & (sch_long['nces_lea_id'].isin(lea_77['nces_lea_id']))]
        sub_l = lea_long[(lea_long['school_year'] == yr) & (lea_long['state'] == st) & (lea_long['nces_lea_id'].isin(lea_77['nces_lea_id']))]
        print(f"  {st} {yr}: sch_sum = {sub_s['classroom_teacher_fte'].sum():,.2f}, lea_k12 = {sub_l['teachers_k12_fte'].sum():,.2f}, lea_tot = {sub_l['teachers_total_reported_fte'].sum():,.2f}")

# ------------------------------------------------------------------------------
# 4. SECONDARY STAFFING WEDGE
# ------------------------------------------------------------------------------
print("\n" + "=" * 80)
print("4. SECONDARY STAFFING WEDGE (CRDC 2023-24)")
print("=" * 80)

crdc_hs = crdc_df[(crdc_df['crdc_wave'] == '2023-24') & 
                  (crdc_df['school_level'] == 'High') & 
                  (crdc_df['school_type'] == 'Regular School') & 
                  (crdc_df['is_operating'] == True)].copy()

crdc_hs['macro_ptr'] = crdc_hs['enrollment_k12'] / crdc_hs['classroom_teacher_fte']
print(f"Regular High Schools in CRDC 2023-24 (N = {len(crdc_hs)}):")
print(f"  Macro School PTR: Mean = {crdc_hs['macro_ptr'].mean():.2f}, Median = {crdc_hs['macro_ptr'].median():.2f}")

# Check course class sizes
subjects = ['alg1', 'geom', 'alg2', 'bio', 'chem', 'phys', 'calc']
all_cs = []
for s in subjects:
    sub = crdc_hs[crdc_hs[f'mean_class_size_{s}'].notna() & crdc_hs['macro_ptr'].notna()]
    cs = sub[f'mean_class_size_{s}']
    ptr = sub['macro_ptr']
    w = cs - ptr
    print(f"  {s.upper():<5}: N={len(sub):<2} | Mean Class Size = {cs.mean():.2f} | Mean PTR = {ptr.mean():.2f} | Mean Wedge = {w.mean():+.2f}")
    all_cs.extend(cs.tolist())

print(f"\nOverall unweighted average across all {len(all_cs)} school-course class size observations: {np.mean(all_cs):.2f}")
# What about student-weighted mean class size across all courses?
# Total course enrollment / total course classes
tot_course_enr = 0
tot_course_sec = 0
for s in subjects:
    tot_course_enr += crdc_hs[f'enr_{s}'].sum()
    tot_course_sec += crdc_hs[f'classes_{s}'].sum()
print(f"Aggregate Derived Class Size across 7 subjects: {tot_course_enr / tot_course_sec:.2f} ({tot_course_enr:,.0f} students / {tot_course_sec:,.0f} classes)")
print(f"Aggregate High School PTR (Sum Enr / Sum Teachers): {crdc_hs['enrollment_k12'].sum() / crdc_hs['classroom_teacher_fte'].sum():.2f}")
print(f"Aggregate Secondary Wedge: {(tot_course_enr / tot_course_sec) - (crdc_hs['enrollment_k12'].sum() / crdc_hs['classroom_teacher_fte'].sum()):+.2f}")

# Where did 21.5 vs 17.1 = +4.4 come from?
# Could 21.5 and 17.1 be the numbers from Figure 1 or Figure 14?
print("\nCheck Figure 1 and Figure 14 parameters:")
