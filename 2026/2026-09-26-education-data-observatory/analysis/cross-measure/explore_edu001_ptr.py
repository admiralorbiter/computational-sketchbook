"""
Audit and compute exact quantities for EDU-001 (Pupil/Teacher Ratio)
Using frozen EDU-002 (Enrollment) and EDU-003 (Teacher FTE) upstream panels.
"""

from pathlib import Path
import pandas as pd
import numpy as np

OBS_DIR = Path(__file__).resolve().parents[2]
KC_DIR = OBS_DIR.parent / "2026-09-23-kc-education-capacity"

sch_long = pd.read_csv(KC_DIR / "data" / "processed" / "kc_school_capacity_long_2014_15_2024_25.csv")
lea_long = pd.read_csv(KC_DIR / "data" / "processed" / "kc_lea_capacity_long_2014_15_2024_25.csv")
crdc_df = pd.read_csv(KC_DIR / "data" / "processed" / "kc_crdc_school_course_capacity_2013_14_2023_24.csv")

print("=" * 70)
print("1. KC_BALANCED_LEA_75 (10-Year Longitudinal Balanced Cohort)")
print("=" * 70)
leas_1415 = set(lea_long[(lea_long['school_year'] == '2014-2015') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
leas_2425 = set(lea_long[(lea_long['school_year'] == '2024-2025') & (lea_long['lea_fully_within_region'] == True)]['nces_lea_id'])
b75 = sorted(list(leas_1415.intersection(leas_2425)))

lea_b75 = lea_long[lea_long['nces_lea_id'].isin(b75)].copy()
lea_14_b = lea_b75[lea_b75['school_year'] == '2014-2015'].set_index('nces_lea_id')
lea_24_b = lea_b75[lea_b75['school_year'] == '2024-2025'].set_index('nces_lea_id')

enr14_b75 = lea_14_b['enrollment_k12'].sum()
enr24_b75 = lea_24_b['enrollment_k12'].sum()
tch14_b75 = lea_14_b['teachers_k12_fte'].sum()
tch24_b75 = lea_24_b['teachers_k12_fte'].sum()

ptr14_b75 = enr14_b75 / tch14_b75
ptr24_b75 = enr24_b75 / tch24_b75
ptr_chg_b75 = ptr24_b75 - ptr14_b75
ptr_pct_b75 = ptr_chg_b75 / ptr14_b75 * 100

print(f"Balanced 75 K-12 Enrollment: {enr14_b75:.2f} -> {enr24_b75:.2f} ({enr24_b75 - enr14_b75:+.2f}, {(enr24_b75 - enr14_b75)/enr14_b75*100:+.2f}%)")
print(f"Balanced 75 K-12 Teacher FTE: {tch14_b75:.2f} -> {tch24_b75:.2f} ({tch24_b75 - tch14_b75:+.2f}, {(tch24_b75 - tch14_b75)/tch14_b75*100:+.2f}%)")
print(f"Balanced 75 Pooled K-12 PTR:  {ptr14_b75:.4f} -> {ptr24_b75:.4f} ({ptr_chg_b75:+.4f}, {ptr_pct_b75:+.2f}%)")

# Unweighted mean and median LEA PTR across b75
lea_14_b['ptr_k12'] = lea_14_b['enrollment_k12'] / lea_14_b['teachers_k12_fte']
lea_24_b['ptr_k12'] = lea_24_b['enrollment_k12'] / lea_24_b['teachers_k12_fte']
print(f"Balanced 75 Unweighted Mean LEA PTR: {lea_14_b['ptr_k12'].mean():.2f} -> {lea_24_b['ptr_k12'].mean():.2f}")
print(f"Balanced 75 Median LEA PTR:          {lea_14_b['ptr_k12'].median():.2f} -> {lea_24_b['ptr_k12'].median():.2f}")

print("\n" + "=" * 70)
print("2. KC_DYNAMIC_REGIONAL_LEA (Annual Contemporary Panel)")
print("=" * 70)
lea_dyn_14 = lea_long[(lea_long['school_year'] == '2014-2015') & (lea_long['lea_fully_within_region'] == True)]
lea_dyn_24 = lea_long[(lea_long['school_year'] == '2024-2025') & (lea_long['lea_fully_within_region'] == True)]

d_enr14 = lea_dyn_14['enrollment_k12'].sum()
d_enr24 = lea_dyn_24['enrollment_k12'].sum()
d_tch14 = lea_dyn_14['teachers_k12_fte'].sum()
d_tch24 = lea_dyn_24['teachers_k12_fte'].sum()

d_ptr14 = d_enr14 / d_tch14
d_ptr24 = d_enr24 / d_tch24
d_chg = d_ptr24 - d_ptr14
d_pct = d_chg / d_ptr14 * 100

print(f"Dynamic Regional K-12 Enrollment: {d_enr14:.2f} -> {d_enr24:.2f} ({d_enr24 - d_enr14:+.2f}, {(d_enr24 - d_enr14)/d_enr14*100:+.2f}%)")
print(f"Dynamic Regional K-12 Teacher FTE: {d_tch14:.2f} -> {d_tch24:.2f} ({d_tch24 - d_tch14:+.2f}, {(d_tch24 - d_tch14)/d_tch14*100:+.2f}%)")
print(f"Dynamic Regional Pooled K-12 PTR:  {d_ptr14:.4f} -> {d_ptr24:.4f} ({d_chg:+.4f}, {d_pct:+.2f}%)")

print("\n" + "=" * 70)
print("3. KC_DECLINING_UNCHANGED_COUNT_28 (Declining LEAs Staffing Stickiness)")
print("=" * 70)
sch_bal = sch_long[sch_long['nces_lea_id'].isin(b75)].copy()
sch_cnt_14 = sch_bal[(sch_bal['school_year'] == '2014-2015') & (sch_bal['operational_status'] == 1)].groupby('nces_lea_id').size()
sch_cnt_24 = sch_bal[(sch_bal['school_year'] == '2024-2025') & (sch_bal['operational_status'] == 1)].groupby('nces_lea_id').size()

df_bal = pd.DataFrame(index=b75)
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
dec_enr14 = decliners_28['enr_14'].sum()
dec_enr24 = decliners_28['enr_24'].sum()
dec_tch14 = decliners_28['tch_14'].sum()
dec_tch24 = decliners_28['tch_24'].sum()

dec_ptr14 = dec_enr14 / dec_tch14
dec_ptr24 = dec_enr24 / dec_tch24
dec_ptr_chg = dec_ptr24 - dec_ptr14
dec_ptr_pct = dec_ptr_chg / dec_ptr14 * 100

print(f"Decliners 28 K-12 Enrollment: {dec_enr14:.2f} -> {dec_enr24:.2f} ({dec_enr24 - dec_enr14:+.2f}, {(dec_enr24 - dec_enr14)/dec_enr14*100:+.2f}%)")
print(f"Decliners 28 K-12 Teacher FTE: {dec_tch14:.2f} -> {dec_tch24:.2f} ({dec_tch24 - dec_tch14:+.2f}, {(dec_tch24 - dec_tch14)/dec_tch14*100:+.2f}%)")
print(f"Decliners 28 Pooled K-12 PTR:  {dec_ptr14:.4f} -> {dec_ptr24:.4f} ({dec_ptr_chg:+.4f}, {dec_ptr_pct:+.2f}%)")

print("\n" + "=" * 70)
print("4. KC_FULLY_REGIONAL_CURRENT_77 (Cross-Sectional Campus vs LEA PTR Wedge)")
print("=" * 70)
lea_77 = lea_long[(lea_long['school_year'] == '2024-2025') & (lea_long['lea_fully_within_region'] == True)].copy()
sch_77 = sch_long[(sch_long['school_year'] == '2024-2025') & (sch_long['nces_lea_id'].isin(lea_77['nces_lea_id']))].copy()

# Total Headcount Campus vs LEA PTR
sch_enr_tot = sch_77['enrollment_total'].sum()
sch_tch_tot = sch_77['classroom_teacher_fte'].sum()
lea_enr_tot = lea_77['enrollment_total'].sum()
lea_tch_tot = lea_77['teachers_total_reported_fte'].sum()

sch_ptr_tot = sch_enr_tot / sch_tch_tot
lea_ptr_tot = lea_enr_tot / lea_tch_tot
gap_ptr_tot = sch_ptr_tot - lea_ptr_tot

print(f"School Universe Sums:  {sch_enr_tot:.0f} students / {sch_tch_tot:.2f} teachers = PTR {sch_ptr_tot:.4f}")
print(f"LEA Universe Sums:     {lea_enr_tot:.0f} students / {lea_tch_tot:.2f} teachers = PTR {lea_ptr_tot:.4f}")
print(f"Campus vs LEA PTR Gap: {gap_ptr_tot:+.4f} students/teacher ({gap_ptr_tot/lea_ptr_tot*100:+.2f}%)")

# Campus regular school distributions
sch_reg = sch_77[(sch_77['operational_status'] == 1) & (sch_77['school_type'] == 'Regular School') & (sch_77['enrollment_k12'] > 0) & (sch_77['classroom_teacher_fte'] > 0)].copy()
sch_reg['ptr'] = sch_reg['enrollment_k12'] / sch_reg['classroom_teacher_fte']
print(f"\nRegular School Campus K-12 PTR Distribution (N={len(sch_reg)}):")
print(f"  Pooled: {sch_reg['enrollment_k12'].sum() / sch_reg['classroom_teacher_fte'].sum():.2f}")
print(f"  Mean:   {sch_reg['ptr'].mean():.2f}")
print(f"  Std:    {sch_reg['ptr'].std():.2f}")
print(f"  Min:    {sch_reg['ptr'].min():.2f}")
print(f"  Q25:    {sch_reg['ptr'].quantile(0.25):.2f}")
print(f"  Median: {sch_reg['ptr'].median():.2f}")
print(f"  Q75:    {sch_reg['ptr'].quantile(0.75):.2f}")
print(f"  Max:    {sch_reg['ptr'].max():.2f}")

# By grade band
for level in ['Primary', 'Middle', 'High']:
    sub = sch_reg[sch_reg['school_level'] == level]
    print(f"  {level:<10} (N={len(sub):3d}): Pooled = {sub['enrollment_k12'].sum()/sub['classroom_teacher_fte'].sum():.2f}, Mean = {sub['ptr'].mean():.2f}, Median = {sub['ptr'].median():.2f}")

print("\n" + "=" * 70)
print("5. CRDC SECONDARY CONTRAST (High School Macro PTR vs Course Class Size)")
print("=" * 70)
crdc_hs_23 = crdc_df[(crdc_df['crdc_wave'] == '2023-24') & 
                     (crdc_df['school_level'] == 'High') & 
                     (crdc_df['school_type'] == 'Regular School') & 
                     (crdc_df['is_operating'] == True)].copy()
crdc_hs_23['macro_ptr'] = crdc_hs_23['enrollment_k12'] / crdc_hs_23['classroom_teacher_fte']
sub_alg = crdc_hs_23[crdc_hs_23['mean_class_size_alg1'].notna() & crdc_hs_23['macro_ptr'].notna()]
print(f"Matched High Schools with Valid Algebra I & Macro PTR (N={len(sub_alg)}):")
print(f"  Mean Macro PTR:        {sub_alg['macro_ptr'].mean():.2f}")
print(f"  Mean Algebra I Size:   {sub_alg['mean_class_size_alg1'].mean():.2f}")
print(f"  Mean Wedge:            {sub_alg['mean_class_size_alg1'].mean() - sub_alg['macro_ptr'].mean():+.2f}")
