import os
import pandas as pd
import numpy as np

# Load processed Kansas City panels
kc_school_path = r"2026/2026-09-23-kc-education-capacity/data/processed/kc_school_capacity_2024_2025.csv"
kc_lea_path = r"2026/2026-09-23-kc-education-capacity/data/processed/kc_lea_capacity_2024_2025.csv"
kc_long_path = r"2026/2026-09-23-kc-education-capacity/data/processed/kc_school_capacity_long_2014_15_2024_25.csv"

sch_df = pd.read_csv(kc_school_path)
lea_df = pd.read_csv(kc_lea_path)
long_df = pd.read_csv(kc_long_path)

print("="*75)
print("EMPIRICAL INVESTIGATION: EDU-002 STUDENT ENROLLMENT (KANSAS CITY & NATIONAL)")
print("="*75)

# 1. Total Enrollment Counts & Pre-K Inclusion
print("\n--- 1. TOTAL HEADCOUNT VS K-12 HEADCOUNT (KC METRO SY 2024-25) ---")
total_member = sch_df['enrollment_total'].sum()
total_k12 = sch_df['enrollment_k12'].sum()
pk_count = sch_df['enrollment_pk'].fillna(0).sum()

print(f"Total Raw Campus Enrollment (enrollment_total): {total_member:,.0f}")
print(f"Total Pre-K Enrollment (enrollment_pk):         {pk_count:,.0f} ({pk_count/total_member*100:.2f}%)")
print(f"Total K-12 Campus Enrollment (enrollment_k12):   {total_k12:,.0f}")

# Compare to LEA direct MEMBER
lea_total_member = lea_df['enrollment_total'].sum()
lea_total_k12 = lea_df['enrollment_k12'].sum()
print(f"\nTotal Direct LEA Enrollment Sum: {lea_total_member:,.0f}")
print(f"Total Direct LEA K-12 Sum:       {lea_total_k12:,.0f}")
lea_sch_diff = lea_total_member - total_member
print(f"Difference (LEA Sum - Campus Sum): {lea_sch_diff:+,.0f} ({lea_sch_diff/lea_total_member*100:+.2f}%)")

# 2. Campus vs LEA Enrollment Reconciliation
print("\n--- 2. LEA VS SUM OF CAMPUS ENROLLMENTS (TOP DISCREPANCIES) ---")
sch_by_lea = sch_df.groupby('nces_lea_id')['enrollment_total'].sum().reset_index(name='campus_sum_enrollment')
merged_lea = pd.merge(lea_df[['nces_lea_id', 'district_name', 'state', 'enrollment_total']], sch_by_lea, on='nces_lea_id', how='left')
merged_lea['campus_sum_enrollment'] = merged_lea['campus_sum_enrollment'].fillna(0)
merged_lea['diff'] = merged_lea['enrollment_total'] - merged_lea['campus_sum_enrollment']
merged_lea['pct_diff'] = (merged_lea['diff'] / merged_lea['enrollment_total'] * 100)

discrepant = merged_lea[merged_lea['diff'].abs() > 5].sort_values(by='diff', ascending=False)
print(f"Number of LEAs where Campus Sum != LEA Total by >5 students: {len(discrepant)} of {len(merged_lea)}")
print(discrepant[['district_name', 'state', 'enrollment_total', 'campus_sum_enrollment', 'diff', 'pct_diff']].head(10).to_string(index=False))

# 3. School Size Distribution in KC Metro
print("\n--- 3. SCHOOL SIZE DISTRIBUTION BY SCHOOL LEVEL (KC METRO 2024-25) ---")
levels = sch_df['school_level'].unique()
for lvl in sorted([str(x) for x in levels if pd.notna(x)]):
    sub = sch_df[sch_df['school_level'] == lvl]['enrollment_total']
    print(f"Level: {lvl:<15} N={len(sub):<4} Min={sub.min():<5.0f} Q25={sub.quantile(0.25):<5.0f} Med={sub.median():<5.0f} Mean={sub.mean():<6.1f} Q75={sub.quantile(0.75):<5.0f} Max={sub.max():<6.0f}")

# 4. Outliers & Non-Standard Entities
print("\n--- 4. EXTREME CAMPUS ENROLLMENT OUTLIERS ---")
print("Top 5 Smallest Operating Regular Schools (enrollment > 0):")
print(sch_df[sch_df['enrollment_total'] > 0][['school_name', 'district_name', 'school_level', 'enrollment_total', 'is_regular', 'is_virtual', 'is_special_ed']].sort_values('enrollment_total').head(5).to_string(index=False))

print("\nSchools with enrollment_total == 0:")
zero_enr = sch_df[sch_df['enrollment_total'] == 0][['school_name', 'district_name', 'school_level', 'enrollment_total', 'operational_status_desc', 'is_vocational']]
print(f"Count of 0-enrollment schools: {len(zero_enr)}")
if len(zero_enr) > 0:
    print(zero_enr.head(6).to_string(index=False))

print("\nTop 5 Largest Schools in KC Metro:")
print(sch_df[['school_name', 'district_name', 'school_level', 'enrollment_total', 'is_virtual']].sort_values('enrollment_total', ascending=False).head(5).to_string(index=False))

# 5. Pre-K Dedicated Centers vs Integrated
print("\n--- 5. PRE-K CONCENTRATION PATTERNS ---")
sch_df['pk_pct'] = sch_df['enrollment_pk'].fillna(0) / sch_df['enrollment_total'].replace(0, np.nan) * 100
pk_schools = sch_df[sch_df['enrollment_pk'] > 0]
print(f"Schools with Pre-K enrollment: {len(pk_schools)} of {len(sch_df)} ({len(pk_schools)/len(sch_df)*100:.1f}%)")
pure_pk = sch_df[sch_df['is_standalone_pk'] == True]
print(f"Dedicated Early Childhood Centers (is_standalone_pk): {len(pure_pk)}")
print(pure_pk[['school_name', 'district_name', 'enrollment_total', 'enrollment_pk', 'pk_pct']].head(6).to_string(index=False))

# 6. Longitudinal Enrollment Dynamics (11 Years: 2014-15 to 2024-25)
print("\n--- 6. LONGITUDINAL ENROLLMENT DYNAMICS (11-YEAR LEA PANEL) ---")
lea_long_path = r"2026/2026-09-23-kc-education-capacity/data/processed/kc_lea_capacity_long_2014_15_2024_25.csv"
lea_long = pd.read_csv(lea_long_path)
yearly_enr = lea_long.groupby('school_year')['enrollment_k12'].sum().reset_index()
print(yearly_enr.to_string(index=False))

print("\nExploration completed successfully!")
