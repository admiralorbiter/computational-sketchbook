"""
Task 004 Investigation Script:
Empirical Investigation for EDU-003 Reported Classroom Teacher FTE
- Part 1: Source Fields, Inventory, Missingness, and Data Types (School vs. LEA)
- Part 2: School-Sum vs. LEA-Reported Teacher FTE Reconciliation (77 Regional LEAs)
- Part 3: Job 1 — Fixed-Plant Staffing Penalty in Declining Districts
- Part 4: Job 2 — Curricular Breadth Staffing Cost in High Schools (<800 enrollment)
- Part 5: Job 3 — Kindergarten Allocation & Early Childhood Staffing Dynamics
- Part 6: Job 4 — Charter Staffing Elasticity in KC Urban Footprint (KCPS + Jackson Co Charters)
- Part 7: Job 5 — Macro PTR (EDU-001 = EDU-002 / EDU-003) vs. Course Class Sizes (EDU-012)
"""

# [HISTORICAL / EXPLORATORY SCRIPT — TASK 004]
# Note: For canonical Task 004A audited calculations, see task004a_empirical_audit.py and generate_edu003_visuals.py.

import os
from pathlib import Path
import pandas as pd
import numpy as np

script_dir = Path(__file__).resolve().parent
repo_dir = script_dir.parent.parent
KC_DIR = repo_dir.parent / "2026-09-23-kc-education-capacity"

sch_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_capacity_long_2014_15_2024_25.csv"))
lea_long = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_lea_capacity_long_2014_15_2024_25.csv"))
crdc_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_crdc_school_course_capacity_2013_14_2023_24.csv"))
comp_df = pd.read_csv(os.path.join(KC_DIR, "data", "processed", "kc_school_complexity_panel_2015_2024.csv"))

# Balanced 75 LEA cohort definition
leas_1415 = set(lea_long[(lea_long['school_year']=='2014-2015') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
leas_2425 = set(lea_long[(lea_long['school_year']=='2024-2025') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
balanced_leas = sorted(list(leas_1415.intersection(leas_2425)))

print("="*80)
print(f"LOADED DATASETS. Balanced LEAs N = {len(balanced_leas)}")
print("="*80)

# ==============================================================================
# PART 1: FIELD INVENTORY, DISTRIBUTIONS & MISSINGNESS
# ==============================================================================
print("\n" + "="*80)
print("PART 1: FIELD INVENTORY, DISTRIBUTIONS & MISSINGNESS (SY 2024-25 & LONGITUDINAL)")
print("="*80)

sch_2425 = sch_long[sch_long['school_year'] == '2024-2025'].copy()
lea_2425 = lea_long[lea_long['school_year'] == '2024-2025'].copy()

print(f"SY 2024-25 Total Schools in Panel: N = {len(sch_2425)}")
print(f"  Valid classroom_teacher_fte: {sch_2425['classroom_teacher_fte'].notna().sum()}")
print(f"  Missing classroom_teacher_fte: {sch_2425['classroom_teacher_fte'].isna().sum()}")
print(f"  Zero classroom_teacher_fte: {(sch_2425['classroom_teacher_fte'] == 0).sum()}")
print(f"  Positive classroom_teacher_fte: {(sch_2425['classroom_teacher_fte'] > 0).sum()}")

# Zero teacher schools
zero_teach_schs = sch_2425[sch_2425['classroom_teacher_fte'] == 0]
print(f"\nZero-Teacher Schools in 2024-25 (N={len(zero_teach_schs)}):")
print(zero_teach_schs[['school_name', 'district_name', 'school_level', 'enrollment_total', 'classroom_teacher_fte', 'school_type', 'is_virtual']].to_string(index=False))

# Missing teacher schools
na_teach_schs = sch_2425[sch_2425['classroom_teacher_fte'].isna()]
print(f"\nMissing-Teacher Schools in 2024-25 (N={len(na_teach_schs)}):")
print(na_teach_schs[['school_name', 'district_name', 'school_level', 'enrollment_total', 'school_type', 'is_virtual']].to_string(index=False))

# Distribution of school teacher FTE by level for regular schools
reg_2425 = sch_2425[(sch_2425['school_type'] == 1) & (sch_2425['classroom_teacher_fte'] > 0)]
print("\nRegular School Teacher FTE Summary by School Level (SY 2024-25):")
for lvl in sorted(reg_2425['school_level'].dropna().unique()):
    sub = reg_2425[reg_2425['school_level'] == lvl]['classroom_teacher_fte']
    print(f"  {lvl:<15} N={len(sub):<3} Min={sub.min():<5.1f} Q25={sub.quantile(0.25):<5.1f} Med={sub.median():<5.1f} Mean={sub.mean():<5.1f} Q75={sub.quantile(0.75):<5.1f} Max={sub.max():<6.1f} Sum={sub.sum():<7.1f}")

# Total regional teacher FTE sums
print("\nRegional Teacher FTE Aggregates (SY 2024-25, 77 Fully Regional LEAs):")
lea_reg_2425 = lea_2425[lea_2425['lea_fully_within_region'] == True]
sch_reg_2425 = sch_2425[sch_2425['nces_lea_id'].isin(lea_reg_2425['nces_lea_id'])]

sum_sch_teachers = sch_reg_2425['classroom_teacher_fte'].sum()
sum_lea_k12_teachers = lea_reg_2425['teachers_k12_fte'].sum()
sum_lea_total_teachers = lea_reg_2425['teachers_total_reported_fte'].sum()
sum_lea_prek_teachers = lea_reg_2425['teachers_prek_fte'].fillna(0).sum()
sum_lea_kg_teachers = lea_reg_2425['teachers_kindergarten_fte'].fillna(0).sum()
sum_lea_elem_teachers = lea_reg_2425['teachers_elementary_fte'].fillna(0).sum()
sum_lea_sec_teachers = lea_reg_2425['teachers_secondary_fte'].fillna(0).sum()
sum_lea_ungraded_teachers = lea_reg_2425['teachers_ungraded_fte'].fillna(0).sum()

print(f"  Sum of Campus Classroom Teacher FTE:        {sum_sch_teachers:,.2f}")
print(f"  Sum of LEA K-12 Teacher FTE (reported):     {sum_lea_k12_teachers:,.2f}")
print(f"  Sum of LEA Total Teacher FTE (incl Pre-K):  {sum_lea_total_teachers:,.2f}")
print(f"  Reconciliation Gap (LEA K12 - School Sum):   {sum_lea_k12_teachers - sum_sch_teachers:+,.2f} ({(sum_lea_k12_teachers - sum_sch_teachers)/sum_lea_k12_teachers*100:+.2f}%)")
print(f"  Reconciliation Gap (LEA Total - School Sum): {sum_lea_total_teachers - sum_sch_teachers:+,.2f} ({(sum_lea_total_teachers - sum_sch_teachers)/sum_lea_total_teachers*100:+.2f}%)")

print("\nLEA Teacher Grade Breakdown:")
print(f"  Pre-K Teachers:     {sum_lea_prek_teachers:,.2f}")
print(f"  Kindergarten:       {sum_lea_kg_teachers:,.2f}")
print(f"  Elementary:         {sum_lea_elem_teachers:,.2f}")
print(f"  Secondary:          {sum_lea_sec_teachers:,.2f}")
print(f"  Ungraded:           {sum_lea_ungraded_teachers:,.2f}")

# Other LEA staff breakdown
print("\nLEA Non-Classroom Staff Aggregates (SY 2024-25, 77 Fully Regional LEAs):")
staff_cols = [
    'paraprofessionals_fte', 'instructional_coordinators_fte', 'counselors_fte',
    'psychologists_fte', 'student_support_staff_fte', 'librarians_fte',
    'school_administrators_fte', 'school_admin_support_fte', 'lea_administrators_fte',
    'lea_admin_support_fte', 'other_support_staff_fte', 'total_staff_fte'
]
for sc in staff_cols:
    val = lea_reg_2425[sc].fillna(0).sum()
    print(f"  {sc:<30}: {val:,.2f}")

# ==============================================================================
# PART 2: LEA VS SCHOOL-SUM RECONCILIATION
# ==============================================================================
print("\n" + "="*80)
print("PART 2: LEA VS SCHOOL-SUM RECONCILIATION ACROSS 77 REGIONAL LEAs")
print("="*80)

sch_sum_by_lea = sch_reg_2425.groupby('nces_lea_id')['classroom_teacher_fte'].sum().reset_index(name='sch_teacher_sum')
recon_df = pd.merge(lea_reg_2425[['nces_lea_id', 'district_name', 'state', 'teachers_k12_fte', 'teachers_total_reported_fte']], sch_sum_by_lea, on='nces_lea_id', how='left')
recon_df['sch_teacher_sum'] = recon_df['sch_teacher_sum'].fillna(0)
recon_df['diff_k12'] = recon_df['teachers_k12_fte'] - recon_df['sch_teacher_sum']
recon_df['diff_total'] = recon_df['teachers_total_reported_fte'] - recon_df['sch_teacher_sum']

exact_k12 = recon_df[recon_df['diff_k12'].abs() < 0.1]
pos_k12 = recon_df[recon_df['diff_k12'] >= 0.1]
neg_k12 = recon_df[recon_df['diff_k12'] <= -0.1]

print(f"Exact reconciliation (|diff| < 0.1): {len(exact_k12)} LEAs")
print(f"Positive gap (LEA > School Sum):    {len(pos_k12)} LEAs (Sum of excess = {pos_k12['diff_k12'].sum():+,.2f})")
print(f"Negative gap (LEA < School Sum):    {len(neg_k12)} LEAs (Sum of deficit = {neg_k12['diff_k12'].sum():+,.2f})")

# Check by state
for st in ['MO', 'KS']:
    sub_st = recon_df[recon_df['state'] == st]
    print(f"\nState {st} (N={len(sub_st)} LEAs):")
    print(f"  LEA K12 Teachers Sum:   {sub_st['teachers_k12_fte'].sum():,.2f}")
    print(f"  Campus Teachers Sum:    {sub_st['sch_teacher_sum'].sum():,.2f}")
    print(f"  Net Gap:                {sub_st['diff_k12'].sum():+,.2f}")
    print(f"  Exact count:            {(sub_st['diff_k12'].abs() < 0.1).sum()}")
    print(f"  Positive gap count:     {(sub_st['diff_k12'] >= 0.1).sum()}")
    print(f"  Negative gap count:     {(sub_st['diff_k12'] <= -0.1).sum()}")

# ==============================================================================
# PART 3: JOB 1 — FIXED-PLANT STAFFING PENALTY
# ==============================================================================
print("\n" + "="*80)
print("PART 3: JOB 1 — FIXED-PLANT STAFFING PENALTY (28 DECLINING LEAS WITH UNCHANGED SCHOOL COUNTS)")
print("="*80)

lea_bal = lea_long[lea_long['nces_lea_id'].isin(balanced_leas)].copy()
lea_1415 = lea_bal[lea_bal['school_year'] == '2014-2015'].set_index('nces_lea_id')
lea_2425_b = lea_bal[lea_bal['school_year'] == '2024-2025'].set_index('nces_lea_id')

sch_bal = sch_long[sch_long['nces_lea_id'].isin(balanced_leas)].copy()
sch_cnt_1415 = sch_bal[(sch_bal['school_year'] == '2014-2015') & (sch_bal['is_operating'] == True)].groupby('nces_lea_id').size()
sch_cnt_2425 = sch_bal[(sch_bal['school_year'] == '2024-2025') & (sch_bal['is_operating'] == True)].groupby('nces_lea_id').size()

comp_df_bal = pd.DataFrame(index=balanced_leas)
comp_df_bal['district_name'] = lea_2425_b['district_name']
comp_df_bal['state'] = lea_2425_b['state']
comp_df_bal['enr_1415'] = lea_1415['enrollment_k12']
comp_df_bal['enr_2425'] = lea_2425_b['enrollment_k12']
comp_df_bal['enr_chg'] = comp_df_bal['enr_2425'] - comp_df_bal['enr_1415']
comp_df_bal['enr_pct'] = comp_df_bal['enr_chg'] / comp_df_bal['enr_1415'] * 100

comp_df_bal['tch_1415'] = lea_1415['teachers_k12_fte']
comp_df_bal['tch_2425'] = lea_2425_b['teachers_k12_fte']
comp_df_bal['tch_chg'] = comp_df_bal['tch_2425'] - comp_df_bal['tch_1415']
comp_df_bal['tch_pct'] = comp_df_bal['tch_chg'] / comp_df_bal['tch_1415'] * 100

comp_df_bal['ptr_1415'] = comp_df_bal['enr_1415'] / comp_df_bal['tch_1415']
comp_df_bal['ptr_2425'] = comp_df_bal['enr_2425'] / comp_df_bal['tch_2425']
comp_df_bal['ptr_chg'] = comp_df_bal['ptr_2425'] - comp_df_bal['ptr_1415']

comp_df_bal['total_staff_1415'] = lea_1415['total_staff_fte']
comp_df_bal['total_staff_2425'] = lea_2425_b['total_staff_fte']
comp_df_bal['admin_1415'] = lea_1415['school_administrators_fte'].fillna(0) + lea_1415['lea_administrators_fte'].fillna(0)
comp_df_bal['admin_2425'] = lea_2425_b['school_administrators_fte'].fillna(0) + lea_2425_b['lea_administrators_fte'].fillna(0)

comp_df_bal['sch_cnt_1415'] = sch_cnt_1415.reindex(balanced_leas).fillna(0)
comp_df_bal['sch_cnt_2425'] = sch_cnt_2425.reindex(balanced_leas).fillna(0)
comp_df_bal['sch_cnt_chg'] = comp_df_bal['sch_cnt_2425'] - comp_df_bal['sch_cnt_1415']

# Declining LEAs with unchanged school count
declining_unchanged = comp_df_bal[(comp_df_bal['enr_chg'] < 0) & (comp_df_bal['sch_cnt_chg'] == 0)]
print(f"Declining LEAs with Unchanged School Count: N = {len(declining_unchanged)}")

# Aggregates for declining unchanged
tot_enr_14 = declining_unchanged['enr_1415'].sum()
tot_enr_24 = declining_unchanged['enr_2425'].sum()
tot_tch_14 = declining_unchanged['tch_1415'].sum()
tot_tch_24 = declining_unchanged['tch_2425'].sum()
tot_admin_14 = declining_unchanged['admin_1415'].sum()
tot_admin_24 = declining_unchanged['admin_2425'].sum()
tot_staff_14 = declining_unchanged['total_staff_1415'].sum()
tot_staff_24 = declining_unchanged['total_staff_2425'].sum()

print("\nAggregate Changes in Declining LEAs with Unchanged School Count (N=28):")
print(f"  K-12 Enrollment:  {tot_enr_14:,.0f} -> {tot_enr_24:,.0f} ({tot_enr_24 - tot_enr_14:+,.0f}, {(tot_enr_24 - tot_enr_14)/tot_enr_14*100:+.2f}%)")
print(f"  Teacher K-12 FTE: {tot_tch_14:,.1f} -> {tot_tch_24:,.1f} ({tot_tch_24 - tot_tch_14:+,.1f}, {(tot_tch_24 - tot_tch_14)/tot_tch_14*100:+.2f}%)")
print(f"  Macro PTR:        {tot_enr_14/tot_tch_14:.2f} -> {tot_enr_24/tot_tch_24:.2f} ({(tot_enr_24/tot_tch_24) - (tot_enr_14/tot_tch_14):+.2f})")
print(f"  Administrators:   {tot_admin_14:,.1f} -> {tot_admin_24:,.1f} ({tot_admin_24 - tot_admin_14:+,.1f}, {(tot_admin_24 - tot_admin_14)/tot_admin_14*100:+.2f}%)")
print(f"  Total Staff FTE:  {tot_staff_14:,.1f} -> {tot_staff_24:,.1f} ({tot_staff_24 - tot_staff_14:+,.1f}, {(tot_staff_24 - tot_staff_14)/tot_staff_14*100:+.2f}%)")

# ==============================================================================
# PART 4: JOB 2 — CURRICULAR BREADTH STAFFING COST (HIGH SCHOOLS)
# ==============================================================================
print("\n" + "="*80)
print("PART 4: JOB 2 — CURRICULAR BREADTH STAFFING COST IN HIGH SCHOOLS (<800 ENROLLMENT)")
print("="*80)

crdc_hs = crdc_df[(crdc_df['crdc_wave'] == '2023-24') & (crdc_df['school_level'] == 'High') & (crdc_df['school_type'] == 'Regular School') & (crdc_df['is_operating'] == True)].copy()
print(f"Regular Operating High Schools in CRDC 2023-24: N = {len(crdc_hs)}")

crdc_hs['offers_calc'] = crdc_hs['classes_calc'] > 0
crdc_hs['offers_phys'] = crdc_hs['classes_phys'] > 0

bins = [0, 400, 800, 1200, 1600, 9999]
labels = ['<400', '400-799', '800-1199', '1200-1599', '>=1600']
crdc_hs['scale_bin'] = pd.cut(crdc_hs['enrollment_k12'], bins=bins, labels=labels, right=False)

for b in labels:
    sub = crdc_hs[crdc_hs['scale_bin'] == b]
    n = len(sub)
    if n == 0: continue
    calc_cnt = sub['offers_calc'].sum()
    phys_cnt = sub['offers_phys'].sum()
    mean_tch = sub['classroom_teacher_fte'].mean()
    med_tch = sub['classroom_teacher_fte'].median()
    mean_enr = sub['enrollment_k12'].mean()
    mean_ptr = sub['school_ptr'].mean()
    print(f"  Bin {b:<10} N={n:<2} MeanEnr={mean_enr:<6.0f} MeanTchFTE={mean_tch:<5.1f} MedTchFTE={med_tch:<5.1f} CalcOffered={calc_cnt}/{n} ({calc_cnt/n*100:4.1f}%) PhysOffered={phys_cnt}/{n} ({phys_cnt/n*100:4.1f}%) MeanPTR={mean_ptr:4.1f}")

# Subsample of high schools under 800 students
hs_under800 = crdc_hs[crdc_hs['enrollment_k12'] < 800].copy()
print(f"\nHigh Schools < 800 Enrollment in 2023-24: N = {len(hs_under800)}")
calc_yes = hs_under800[hs_under800['offers_calc'] == True]
calc_no = hs_under800[hs_under800['offers_calc'] == False]
print(f"  Offers Calculus (N={len(calc_yes)}): Mean Enrollment = {calc_yes['enrollment_k12'].mean():.1f}, Mean Teacher FTE = {calc_yes['classroom_teacher_fte'].mean():.1f}, Median Teacher FTE = {calc_yes['classroom_teacher_fte'].median():.1f}, Mean PTR = {calc_yes['school_ptr'].mean():.1f}")
print(f"  No Calculus     (N={len(calc_no)}): Mean Enrollment = {calc_no['enrollment_k12'].mean():.1f}, Mean Teacher FTE = {calc_no['classroom_teacher_fte'].mean():.1f}, Median Teacher FTE = {calc_no['classroom_teacher_fte'].median():.1f}, Mean PTR = {calc_no['school_ptr'].mean():.1f}")

phys_yes = hs_under800[hs_under800['offers_phys'] == True]
phys_no = hs_under800[hs_under800['offers_phys'] == False]
print(f"  Offers Physics  (N={len(phys_yes)}): Mean Enrollment = {phys_yes['enrollment_k12'].mean():.1f}, Mean Teacher FTE = {phys_yes['classroom_teacher_fte'].mean():.1f}, Median Teacher FTE = {phys_yes['classroom_teacher_fte'].median():.1f}, Mean PTR = {phys_yes['school_ptr'].mean():.1f}")
print(f"  No Physics      (N={len(phys_no)}): Mean Enrollment = {phys_no['enrollment_k12'].mean():.1f}, Mean Teacher FTE = {phys_no['classroom_teacher_fte'].mean():.1f}, Median Teacher FTE = {phys_no['classroom_teacher_fte'].median():.1f}, Mean PTR = {phys_no['school_ptr'].mean():.1f}")

# Multi-wave analysis for <800 regular high schools across CRDC waves
print("\nMulti-Wave Curricular Offerings for Regular High Schools < 800 (CRDC 2013-14 through 2023-24):")
crdc_hs_all = crdc_df[(crdc_df['school_level'] == 'High') & (crdc_df['school_type'] == 'Regular School') & (crdc_df['enrollment_k12'] < 800) & (crdc_df['is_operating'] == True)].copy()
crdc_hs_all['offers_calc'] = crdc_hs_all['classes_calc'] > 0
crdc_hs_all['offers_phys'] = crdc_hs_all['classes_phys'] > 0
for wave in sorted(crdc_hs_all['crdc_wave'].unique()):
    sub_w = crdc_hs_all[crdc_hs_all['crdc_wave'] == wave]
    n_w = len(sub_w)
    calc_w = sub_w['offers_calc'].sum()
    phys_w = sub_w['offers_phys'].sum()
    print(f"  Wave {wave}: N={n_w:<2} | Calculus: {calc_w}/{n_w} ({calc_w/n_w*100:.1f}%) | Physics: {phys_w}/{n_w} ({phys_w/n_w*100:.1f}%) | Mean Tch FTE: {sub_w['classroom_teacher_fte'].mean():.1f} | Mean Enr: {sub_w['enrollment_k12'].mean():.1f}")

# ==============================================================================
# PART 7: JOB 5 — MACRO PTR VS COURSE CLASS SIZE
# ==============================================================================
print("\n" + "="*80)
print("PART 7: JOB 5 — MACRO PTR (EDU-001) VS ACTUAL COURSE CLASS SIZES (EDU-012)")
print("="*80)

# Compare campus PTR with CRDC derived class sizes
# For regular high schools in CRDC 2023-24
crdc_hs['macro_ptr'] = crdc_hs['enrollment_k12'] / crdc_hs['classroom_teacher_fte']

print(f"Regular High Schools Comparison (CRDC 2023-24, N={len(crdc_hs)}):")
print(f"  Macro School PTR:           Mean = {crdc_hs['macro_ptr'].mean():.2f}, Median = {crdc_hs['macro_ptr'].median():.2f}, IQR = [{crdc_hs['macro_ptr'].quantile(0.25):.2f}, {crdc_hs['macro_ptr'].quantile(0.75):.2f}]")

# Check class size columns for core subjects
subjects = ['alg1', 'geom', 'alg2', 'bio', 'chem', 'phys', 'calc']
for s in subjects:
    sub_valid = crdc_hs[crdc_hs[f'mean_class_size_{s}'].notna() & crdc_hs['macro_ptr'].notna()]
    mean_cs = sub_valid[f'mean_class_size_{s}']
    wedge = sub_valid[f'mean_class_size_{s}'] - sub_valid['macro_ptr']
    print(f"  Subject {s.upper():<5}: Valid N={len(sub_valid):<2} | Mean Class Size = {mean_cs.mean():5.2f} | Median = {mean_cs.median():5.2f} | Mean Staffing Wedge = {wedge.mean():+5.2f} | Median Wedge = {wedge.median():+5.2f}")

# Multi-wave class size comparison (across all 6 CRDC waves)
print("\nMulti-Wave Class Size vs. Macro PTR (Regular High Schools, 2013-14 through 2023-24):")
crdc_hs_reg_all = crdc_df[(crdc_df['school_level'] == 'High') & (crdc_df['school_type'] == 'Regular School') & (crdc_df['is_operating'] == True)].copy()
crdc_hs_reg_all['macro_ptr'] = crdc_hs_reg_all['enrollment_k12'] / crdc_hs_reg_all['classroom_teacher_fte']

for wave in sorted(crdc_hs_reg_all['crdc_wave'].unique()):
    sub_w = crdc_hs_reg_all[crdc_hs_reg_all['crdc_wave'] == wave]
    sub_valid_alg1 = sub_w[sub_w['mean_class_size_alg1'].notna() & sub_w['macro_ptr'].notna()]
    wedge_alg1 = sub_valid_alg1['mean_class_size_alg1'] - sub_valid_alg1['macro_ptr']
    print(f"  Wave {wave}: N={len(sub_w):<3} | Mean PTR = {sub_w['macro_ptr'].mean():.2f} | Alg1 Mean CS = {sub_valid_alg1['mean_class_size_alg1'].mean():.2f} | Alg1 Wedge = {wedge_alg1.mean():+5.2f}")

print("\n" + "="*80)
print("INVESTIGATION COMPLETE.")
print("="*80)
