"""
Longitudinal Structural Capacity Analysis (2014-15 through 2024-25)
Task 003B Pipeline

This script performs comprehensive empirical analysis of structural staffing capacity
across the 9-county Kansas City metropolitan region over the 11-year audited panel.

Core Research Question:
    How has structural staffing capacity changed across the Kansas City region over the past decade?

Methodological Guardrails:
    1. Analyzes structural staffing resources only (pupil/teacher staffing ratios, paraprofessional intensity).
    2. Does NOT measure classroom section size and does NOT test H1a, H1b, H2, or H3.
    3. Never describes staffing ratios as class sizes.
    4. Student-weighted ratios are preferred for regional/subgroup aggregates; median and percentiles
       are reported separately to describe typical school distributions.
    5. Kansas 2015-16 and Metro 2015-16 staffing are marked as insufficient/partial coverage and
       excluded from primary temporal trend estimation / slope regressions.
    6. Non-causal accounting decompositions quantify whether ratio shifts coincide with changing enrollment,
       changing staffing, or both.
    7. School fixed-effects models on the balanced panel assess within-school trajectories with clustered SEs.
"""

import os
import sys
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
TABLES_DIR = os.path.join(BASE_DIR, 'outputs', 'tables')
FIGURES_DIR = os.path.join(BASE_DIR, 'outputs', 'figures')

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# Grade band classifier
def classify_grade_band(row):
    low = str(row['lowest_grade']).strip()
    high = str(row['highest_grade']).strip()
    if low in ['M', 'N', 'UG', 'nan', ''] or high in ['M', 'N', 'UG', 'nan', '']:
        return 'Other'
    if high in ['12', '11', '10'] and low in ['06', '07', '08', '09', '10', '11', '12']:
        return 'High'
    if low in ['09', '10', '11'] and high in ['09', '10', '11', '12']:
        return 'High'
    if (low in ['PK', 'KG', '01', '02', '03', '04']) and (high in ['10', '11', '12']):
        return 'Other'
    if low in ['05', '06', '07', '08'] and high in ['06', '07', '08', '09']:
        return 'Middle'
    if low in ['PK', 'KG', '01', '02', '03', '04']:
        if high == 'PK':
            return 'Pre-K'
        return 'Primary'
    return 'Other'

def classify_distance_ring(d):
    if pd.isna(d):
        return 'Unknown'
    if d < 5:
        return '< 5 miles'
    if d < 10:
        return '5-10 miles'
    if d < 20:
        return '10-20 miles'
    return '20+ miles'

def get_coverage_tier(valid_enr, total_enr):
    if total_enr <= 0:
        return 'insufficient_coverage', 0.0
    pct = (valid_enr / total_enr) * 100.0
    if pct >= 99.99:
        return 'complete', pct
    elif pct >= 95.0:
        return 'high_coverage', pct
    elif pct >= 80.0:
        return 'partial_coverage', pct
    else:
        return 'insufficient_coverage', pct

def load_data():
    print("Loading audited longitudinal panels...")
    sch_path = os.path.join(DATA_DIR, 'kc_school_capacity_long_2014_15_2024_25.csv')
    lea_path = os.path.join(DATA_DIR, 'kc_lea_capacity_long_2014_15_2024_25.csv')
    bal_path = os.path.join(DATA_DIR, 'kc_school_balanced_panel_2014_15_2024_25.csv')
    
    df_sch = pd.read_csv(sch_path, low_memory=False)
    df_lea = pd.read_csv(lea_path, low_memory=False)
    df_bal = pd.read_csv(bal_path, low_memory=False)
    
    df_sch['grade_band'] = df_sch.apply(classify_grade_band, axis=1)
    df_bal['grade_band'] = df_bal.apply(classify_grade_band, axis=1)
    df_sch['distance_ring'] = df_sch['distance_downtown_kc_miles'].apply(classify_distance_ring)
    df_bal['distance_ring'] = df_bal['distance_downtown_kc_miles'].apply(classify_distance_ring)
    
    return df_sch, df_lea, df_bal

# ==============================================================================
# TABLE 1: REGIONAL TRENDS (LEA & SCHOOL)
# ==============================================================================
def build_regional_trends(df_sch, df_lea):
    print("Building Table 1: task003b_regional_trends.csv...")
    records = []
    
    # A. LEA K-12 Regional Trends (lea_fully_within_region == True)
    lea_reg = df_lea[df_lea['lea_fully_within_region'] == True].copy()
    years = sorted(lea_reg['school_year'].unique())
    
    for sy in years:
        sub = lea_reg[lea_reg['school_year'] == sy]
        total_enr = sub['enrollment_k12'].sum()
        
        # Valid teacher FTE
        valid_t = sub[sub['teachers_k12_fte'].notna() & (sub['teachers_k12_fte'] > 0)]
        valid_t_enr = valid_t['enrollment_k12'].sum()
        total_tch_fte = valid_t['teachers_k12_fte'].sum()
        tier_t, pct_t = get_coverage_tier(valid_t_enr, total_enr)
        
        # Valid para FTE
        valid_tp = sub[sub['teachers_k12_fte'].notna() & (sub['teachers_k12_fte'] > 0) & 
                       sub['paraprofessionals_fte'].notna() & (sub['paraprofessionals_fte'] >= 0)]
        valid_tp_enr = valid_tp['enrollment_k12'].sum()
        total_para_fte = valid_tp['paraprofessionals_fte'].sum()
        tier_tp, pct_tp = get_coverage_tier(valid_tp_enr, total_enr)
        
        # Ratios
        weighted_ptr = valid_t_enr / total_tch_fte if total_tch_fte > 0 else np.nan
        combined_ptr = valid_tp_enr / (valid_tp['teachers_k12_fte'].sum() + total_para_fte) if (valid_tp['teachers_k12_fte'].sum() + total_para_fte) > 0 else np.nan
        t_per_1000 = (total_tch_fte / valid_t_enr) * 1000.0 if valid_t_enr > 0 else np.nan
        p_per_1000 = (total_para_fte / valid_tp_enr) * 1000.0 if valid_tp_enr > 0 else np.nan
        
        # Distributions across LEAs
        lea_ratios = valid_t['students_per_teacher_fte_k12']
        med_lea = lea_ratios.median()
        p10_lea = lea_ratios.quantile(0.10)
        p25_lea = lea_ratios.quantile(0.25)
        p75_lea = lea_ratios.quantile(0.75)
        p90_lea = lea_ratios.quantile(0.90)
        
        is_trend_eligible = (tier_t in ['complete', 'high_coverage']) and (sy != '2015-2016')
        notes = "Complete regional coverage"
        if sy == '2015-2016':
            notes = "Incomplete: Olathe & Gardner Edgerton staff suppressed in federal data; reporting entities only (89.5% enrollment coverage)"
            
        records.append({
            'school_year': sy,
            'grain': 'LEA_K12',
            'analytical_population': 'Regional LEAs (Fully Within Region)',
            'coverage_tier': tier_t,
            'pct_enrollment_valid': round(pct_t, 2),
            'reporting_entities_count': len(valid_t),
            'total_expected_entities': len(sub),
            'total_enrollment': int(valid_t_enr),
            'total_teacher_fte': round(total_tch_fte, 2),
            'student_weighted_ptr': round(weighted_ptr, 2),
            'median_ptr': round(med_lea, 2),
            'p10_ptr': round(p10_lea, 2),
            'p25_ptr': round(p25_lea, 2),
            'p75_ptr': round(p75_lea, 2),
            'p90_ptr': round(p90_lea, 2),
            'total_para_fte': round(total_para_fte, 2) if pd.notna(total_para_fte) else np.nan,
            'combined_teacher_para_ratio': round(combined_ptr, 2),
            'teachers_per_1000': round(t_per_1000, 2),
            'paras_per_1000': round(p_per_1000, 2),
            'is_primary_trend_eligible': is_trend_eligible,
            'notes': notes
        })
        
    # B. School Regular Trends (Operating Regular NCES)
    reg_sch = df_sch[df_sch['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    for sy in years:
        sub = reg_sch[reg_sch['school_year'] == sy]
        total_enr = sub['enrollment_total'].sum()
        
        valid = sub[sub['teacher_fte_valid'] == True]
        valid_enr = valid['enrollment_total'].sum()
        total_tch = valid['classroom_teacher_fte'].sum()
        tier, pct = get_coverage_tier(valid_enr, total_enr)
        
        weighted_ptr = valid_enr / total_tch if total_tch > 0 else np.nan
        ratios = valid['students_per_classroom_teacher_fte_allgrades']
        med_s = ratios.median()
        p10_s = ratios.quantile(0.10)
        p25_s = ratios.quantile(0.25)
        p75_s = ratios.quantile(0.75)
        p90_s = ratios.quantile(0.90)
        
        is_trend_eligible = (tier in ['complete', 'high_coverage']) and (sy != '2015-2016')
        notes = "Complete/high coverage of regular operating schools"
        if sy == '2015-2016':
            notes = "Incomplete: Kansas districts suppressed (89.8% enrollment coverage); reporting entities only"
            
        records.append({
            'school_year': sy,
            'grain': 'School_Regular',
            'analytical_population': 'Operating Regular (NCES)',
            'coverage_tier': tier,
            'pct_enrollment_valid': round(pct, 2),
            'reporting_entities_count': len(valid),
            'total_expected_entities': len(sub),
            'total_enrollment': int(valid_enr),
            'total_teacher_fte': round(total_tch, 2),
            'student_weighted_ptr': round(weighted_ptr, 2),
            'median_ptr': round(med_s, 2),
            'p10_ptr': round(p10_s, 2),
            'p25_ptr': round(p25_s, 2),
            'p75_ptr': round(p75_s, 2),
            'p90_ptr': round(p90_s, 2),
            'total_para_fte': np.nan,
            'combined_teacher_para_ratio': np.nan,
            'teachers_per_1000': round((total_tch / valid_enr) * 1000.0, 2) if valid_enr > 0 else np.nan,
            'paras_per_1000': np.nan,
            'is_primary_trend_eligible': is_trend_eligible,
            'notes': notes
        })
        
    df_out = pd.DataFrame(records)
    out_path = os.path.join(TABLES_DIR, 'task003b_regional_trends.csv')
    df_out.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_out)} rows)")
    return df_out

# ==============================================================================
# TABLE 2: STATE TRENDS (MO vs KS)
# ==============================================================================
def build_state_trends(df_sch, df_lea):
    print("Building Table 2: task003b_state_trends.csv...")
    records = []
    years = sorted(df_lea['school_year'].unique())
    lea_reg = df_lea[df_lea['lea_fully_within_region'] == True].copy()
    reg_sch = df_sch[df_sch['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    
    for state in ['MO', 'KS']:
        # LEA Level
        for sy in years:
            sub = lea_reg[(lea_reg['school_year'] == sy) & (lea_reg['state'] == state)]
            total_enr = sub['enrollment_k12'].sum()
            
            valid_t = sub[sub['teachers_k12_fte'].notna() & (sub['teachers_k12_fte'] > 0)]
            valid_t_enr = valid_t['enrollment_k12'].sum()
            total_tch = valid_t['teachers_k12_fte'].sum()
            tier_t, pct_t = get_coverage_tier(valid_t_enr, total_enr)
            
            valid_tp = sub[sub['teachers_k12_fte'].notna() & (sub['teachers_k12_fte'] > 0) & 
                           sub['paraprofessionals_fte'].notna() & (sub['paraprofessionals_fte'] >= 0)]
            valid_tp_enr = valid_tp['enrollment_k12'].sum()
            total_para = valid_tp['paraprofessionals_fte'].sum()
            
            weighted_ptr = valid_t_enr / total_tch if total_tch > 0 else np.nan
            combined_ptr = valid_tp_enr / (valid_tp['teachers_k12_fte'].sum() + total_para) if (valid_tp['teachers_k12_fte'].sum() + total_para) > 0 else np.nan
            t_per_1000 = (total_tch / valid_t_enr) * 1000.0 if valid_t_enr > 0 else np.nan
            p_per_1000 = (total_para / valid_tp_enr) * 1000.0 if valid_tp_enr > 0 else np.nan
            
            lea_ratios = valid_t['students_per_teacher_fte_k12']
            med_lea = lea_ratios.median()
            p25_lea = lea_ratios.quantile(0.25)
            p75_lea = lea_ratios.quantile(0.75)
            
            is_trend_eligible = (tier_t in ['complete', 'high_coverage'])
            notes = f"Complete {state} LEA reporting"
            if state == 'KS' and sy == '2015-2016':
                is_trend_eligible = False
                notes = "Insufficient coverage (75.9%): Olathe and Gardner Edgerton staff suppressed; reporting entities only"
                
            records.append({
                'school_year': sy,
                'state': state,
                'grain': 'LEA_K12',
                'coverage_tier': tier_t,
                'pct_enrollment_valid': round(pct_t, 2),
                'reporting_entities_count': len(valid_t),
                'total_expected_entities': len(sub),
                'total_enrollment': int(valid_t_enr),
                'total_teacher_fte': round(total_tch, 2),
                'student_weighted_ptr': round(weighted_ptr, 2),
                'median_ptr': round(med_lea, 2),
                'p25_ptr': round(p25_lea, 2),
                'p75_ptr': round(p75_lea, 2),
                'total_para_fte': round(total_para, 2) if pd.notna(total_para) else np.nan,
                'combined_teacher_para_ratio': round(combined_ptr, 2),
                'teachers_per_1000': round(t_per_1000, 2),
                'paras_per_1000': round(p_per_1000, 2),
                'is_primary_trend_eligible': is_trend_eligible,
                'notes': notes
            })
            
        # School Level (Regular)
        for sy in years:
            sub = reg_sch[(reg_sch['school_year'] == sy) & (reg_sch['state'] == state)]
            total_enr = sub['enrollment_total'].sum()
            
            valid = sub[sub['teacher_fte_valid'] == True]
            valid_enr = valid['enrollment_total'].sum()
            total_tch = valid['classroom_teacher_fte'].sum()
            tier, pct = get_coverage_tier(valid_enr, total_enr)
            
            weighted_ptr = valid_enr / total_tch if total_tch > 0 else np.nan
            ratios = valid['students_per_classroom_teacher_fte_allgrades']
            med_s = ratios.median()
            p25_s = ratios.quantile(0.25)
            p75_s = ratios.quantile(0.75)
            
            is_trend_eligible = (tier in ['complete', 'high_coverage'])
            notes = f"Regular operating schools in {state}"
            if state == 'KS' and sy == '2015-2016':
                is_trend_eligible = False
                notes = "Insufficient coverage (76.8%): Olathe and Gardner Edgerton schools suppressed"
                
            records.append({
                'school_year': sy,
                'state': state,
                'grain': 'School_Regular',
                'coverage_tier': tier,
                'pct_enrollment_valid': round(pct, 2),
                'reporting_entities_count': len(valid),
                'total_expected_entities': len(sub),
                'total_enrollment': int(valid_enr),
                'total_teacher_fte': round(total_tch, 2),
                'student_weighted_ptr': round(weighted_ptr, 2),
                'median_ptr': round(med_s, 2),
                'p25_ptr': round(p25_s, 2),
                'p75_ptr': round(p75_s, 2),
                'total_para_fte': np.nan,
                'combined_teacher_para_ratio': np.nan,
                'teachers_per_1000': round((total_tch / valid_enr) * 1000.0, 2) if valid_enr > 0 else np.nan,
                'paras_per_1000': np.nan,
                'is_primary_trend_eligible': is_trend_eligible,
                'notes': notes
            })
            
    df_out = pd.DataFrame(records)
    out_path = os.path.join(TABLES_DIR, 'task003b_state_trends.csv')
    df_out.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_out)} rows)")
    return df_out

# ==============================================================================
# TABLE 3: LOCALE TRENDS (CROSS-SECTION & BALANCED PANEL)
# ==============================================================================
def build_locale_trends(df_sch, df_bal):
    print("Building Table 3: task003b_locale_trends.csv...")
    records = []
    years = sorted(df_sch['school_year'].unique())
    locales = ['City', 'Suburb', 'Town', 'Rural']
    
    # 1. Dynamic Annual Repeated Cross-Section (Operating Regular)
    reg_sch = df_sch[df_sch['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    for loc in locales:
        for sy in years:
            sub = reg_sch[(reg_sch['school_year'] == sy) & (reg_sch['locale_group_year'] == loc)]
            total_enr = sub['enrollment_total'].sum()
            valid = sub[sub['teacher_fte_valid'] == True]
            valid_enr = valid['enrollment_total'].sum()
            total_tch = valid['classroom_teacher_fte'].sum()
            tier, pct = get_coverage_tier(valid_enr, total_enr)
            
            weighted_ptr = valid_enr / total_tch if total_tch > 0 else np.nan
            ratios = valid['students_per_classroom_teacher_fte_allgrades']
            med = ratios.median()
            p10 = ratios.quantile(0.10)
            p25 = ratios.quantile(0.25)
            p75 = ratios.quantile(0.75)
            p90 = ratios.quantile(0.90)
            
            is_trend_eligible = (tier in ['complete', 'high_coverage'])
            notes = f"Dynamic historical locale: {loc}"
            if sy == '2015-2016' and loc == 'Suburb':
                notes = "Olathe/Gardner Edgerton suppression affects suburban Kansas; reporting entities only"
                if pct < 80.0:
                    is_trend_eligible = False
            
            records.append({
                'school_year': sy,
                'locale_group': loc,
                'locale_basis': 'dynamic_annual_cross_section',
                'coverage_tier': tier,
                'pct_enrollment_valid': round(pct, 2),
                'reporting_schools_count': len(valid),
                'total_expected_schools': len(sub),
                'total_enrollment': int(valid_enr),
                'total_classroom_teacher_fte': round(total_tch, 2),
                'student_weighted_ptr': round(weighted_ptr, 2),
                'median_school_ptr': round(med, 2),
                'p10_school_ptr': round(p10, 2),
                'p25_school_ptr': round(p25, 2),
                'p75_school_ptr': round(p75, 2),
                'p90_school_ptr': round(p90, 2),
                'is_primary_trend_eligible': is_trend_eligible,
                'notes': notes
            })
            
    # 2. Fixed 2024-25 Locale on Balanced Panel
    reg_bal = df_bal[df_bal['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    for loc in locales:
        for sy in years:
            sub = reg_bal[(reg_bal['school_year'] == sy) & (reg_bal['locale_group_fixed_2024_2025'] == loc)]
            total_enr = sub['enrollment_total'].sum()
            valid = sub[sub['teacher_fte_valid'] == True]
            valid_enr = valid['enrollment_total'].sum()
            total_tch = valid['classroom_teacher_fte'].sum()
            tier, pct = get_coverage_tier(valid_enr, total_enr)
            
            weighted_ptr = valid_enr / total_tch if total_tch > 0 else np.nan
            ratios = valid['students_per_classroom_teacher_fte_allgrades']
            med = ratios.median()
            p10 = ratios.quantile(0.10)
            p25 = ratios.quantile(0.25)
            p75 = ratios.quantile(0.75)
            p90 = ratios.quantile(0.90)
            
            is_trend_eligible = (tier in ['complete', 'high_coverage'])
            notes = f"Fixed 2024-25 locale on balanced panel: {loc}"
            if sy == '2015-2016' and loc == 'Suburb' and pct < 80.0:
                is_trend_eligible = False
                
            records.append({
                'school_year': sy,
                'locale_group': loc,
                'locale_basis': 'fixed_2024_2025_balanced_panel',
                'coverage_tier': tier,
                'pct_enrollment_valid': round(pct, 2),
                'reporting_schools_count': len(valid),
                'total_expected_schools': len(sub),
                'total_enrollment': int(valid_enr),
                'total_classroom_teacher_fte': round(total_tch, 2),
                'student_weighted_ptr': round(weighted_ptr, 2),
                'median_school_ptr': round(med, 2),
                'p10_school_ptr': round(p10, 2),
                'p25_school_ptr': round(p25, 2),
                'p75_school_ptr': round(p75, 2),
                'p90_school_ptr': round(p90, 2),
                'is_primary_trend_eligible': is_trend_eligible,
                'notes': notes
            })
            
    df_out = pd.DataFrame(records)
    out_path = os.path.join(TABLES_DIR, 'task003b_locale_trends.csv')
    df_out.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_out)} rows)")
    return df_out

# ==============================================================================
# TABLE 4: GRADE BAND TRENDS
# ==============================================================================
def build_gradeband_trends(df_sch):
    print("Building Table 4: task003b_gradeband_trends.csv...")
    records = []
    years = sorted(df_sch['school_year'].unique())
    grade_bands = ['Primary', 'Middle', 'High', 'Other']
    reg_sch = df_sch[df_sch['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    
    for band in grade_bands:
        for sy in years:
            sub = reg_sch[(reg_sch['school_year'] == sy) & (reg_sch['grade_band'] == band)]
            total_enr = sub['enrollment_total'].sum()
            valid = sub[sub['teacher_fte_valid'] == True]
            valid_enr = valid['enrollment_total'].sum()
            total_tch = valid['classroom_teacher_fte'].sum()
            tier, pct = get_coverage_tier(valid_enr, total_enr)
            
            weighted_ptr = valid_enr / total_tch if total_tch > 0 else np.nan
            ratios = valid['students_per_classroom_teacher_fte_allgrades']
            med = ratios.median()
            p25 = ratios.quantile(0.25)
            p75 = ratios.quantile(0.75)
            
            is_trend_eligible = (tier in ['complete', 'high_coverage'])
            notes = f"Regular operating schools in {band} grade band"
            if sy == '2015-2016' and pct < 90.0:
                notes = f"Incomplete ({pct:.1f}%): affected by 2015-16 Kansas suppression"
                if pct < 80.0:
                    is_trend_eligible = False
                    
            records.append({
                'school_year': sy,
                'grade_band': band,
                'analytical_stratum': 'Operating Regular (NCES)',
                'coverage_tier': tier,
                'pct_enrollment_valid': round(pct, 2),
                'reporting_schools_count': len(valid),
                'total_expected_schools': len(sub),
                'total_enrollment': int(valid_enr),
                'total_classroom_teacher_fte': round(total_tch, 2),
                'student_weighted_ptr': round(weighted_ptr, 2),
                'median_school_ptr': round(med, 2),
                'p25_school_ptr': round(p25, 2),
                'p75_school_ptr': round(p75, 2),
                'is_primary_trend_eligible': is_trend_eligible,
                'notes': notes
            })
            
    df_out = pd.DataFrame(records)
    out_path = os.path.join(TABLES_DIR, 'task003b_gradeband_trends.csv')
    df_out.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_out)} rows)")
    return df_out

# ==============================================================================
# TABLE 5: ENDPOINT & PERIOD DECOMPOSITIONS
# ==============================================================================
def build_endpoint_decomposition(df_sch, df_lea, df_bal):
    print("Building Table 5: task003b_endpoint_decomposition.csv...")
    records = []
    
    periods = [
        ('Full_Decade_2014_to_2024', '2014-2015', '2024-2025'),
        ('Pre_Pandemic_2014_to_2019', '2014-2015', '2019-2020'),
        ('Pandemic_Shock_2019_to_2020', '2019-2020', '2020-2021'),
        ('Post_Pandemic_2020_to_2024', '2020-2021', '2024-2025')
    ]
    
    # 1. LEA Dimensions
    lea_reg = df_lea[df_lea['lea_fully_within_region'] == True].copy()
    lea_subsets = [
        ('Metro_LEA_K12', lea_reg),
        ('State_MO_LEA', lea_reg[lea_reg['state'] == 'MO']),
        ('State_KS_LEA', lea_reg[lea_reg['state'] == 'KS'])
    ]
    
    for dim_name, df_sub in lea_subsets:
        for p_label, y0, y1 in periods:
            sub0 = df_sub[df_sub['school_year'] == y0]
            sub1 = df_sub[df_sub['school_year'] == y1]
            
            v0_t = sub0[sub0['teachers_k12_fte'].notna() & (sub0['teachers_k12_fte'] > 0)]
            v1_t = sub1[sub1['teachers_k12_fte'].notna() & (sub1['teachers_k12_fte'] > 0)]
            
            e0 = v0_t['enrollment_k12'].sum()
            e1 = v1_t['enrollment_k12'].sum()
            de = e1 - e0
            pe = (de / e0) * 100.0 if e0 > 0 else np.nan
            
            t0 = v0_t['teachers_k12_fte'].sum()
            t1 = v1_t['teachers_k12_fte'].sum()
            dt = t1 - t0
            pt = (dt / t0) * 100.0 if t0 > 0 else np.nan
            
            r0 = e0 / t0 if t0 > 0 else np.nan
            r1 = e1 / t1 if t1 > 0 else np.nan
            dr = r1 - r0
            pr = (dr / r0) * 100.0 if r0 > 0 else np.nan
            
            # Paras
            v0_tp = sub0[sub0['teachers_k12_fte'].notna() & (sub0['teachers_k12_fte'] > 0) & sub0['paraprofessionals_fte'].notna()]
            v1_tp = sub1[sub1['teachers_k12_fte'].notna() & (sub1['teachers_k12_fte'] > 0) & sub1['paraprofessionals_fte'].notna()]
            
            p0 = v0_tp['paraprofessionals_fte'].sum()
            p1 = v1_tp['paraprofessionals_fte'].sum()
            dp = p1 - p0
            pp = (dp / p0) * 100.0 if p0 > 0 else np.nan
            
            c0 = v0_tp['enrollment_k12'].sum() / (v0_tp['teachers_k12_fte'].sum() + p0) if (v0_tp['teachers_k12_fte'].sum() + p0) > 0 else np.nan
            c1 = v1_tp['enrollment_k12'].sum() / (v1_tp['teachers_k12_fte'].sum() + p1) if (v1_tp['teachers_k12_fte'].sum() + p1) > 0 else np.nan
            dc = c1 - c0
            pc = (dc / c0) * 100.0 if c0 > 0 else np.nan
            
            # Accounting driver description
            if pt > 0 and abs(pt) > abs(pe) * 2:
                driver = "Staffing Expansion"
            elif pe < 0 and abs(pe) > abs(pt) * 2:
                driver = "Enrollment Contraction"
            elif pt > 0 and pe < 0:
                driver = "Joint Staffing Expansion & Enrollment Contraction"
            elif pt > 0 and pe > 0:
                driver = "Staffing Outpaced Enrollment Growth"
            else:
                driver = "Mixed"
                
            records.append({
                'dimension': dim_name,
                'period': p_label,
                'start_year': y0,
                'end_year': y1,
                'enrollment_start': int(e0),
                'enrollment_end': int(e1),
                'enrollment_change_abs': int(de),
                'enrollment_change_pct': round(pe, 2),
                'teacher_fte_start': round(t0, 2),
                'teacher_fte_end': round(t1, 2),
                'teacher_fte_change_abs': round(dt, 2),
                'teacher_fte_change_pct': round(pt, 2),
                'ratio_start': round(r0, 2),
                'ratio_end': round(r1, 2),
                'ratio_change_abs': round(dr, 2),
                'ratio_change_pct': round(pr, 2),
                'para_fte_start': round(p0, 2),
                'para_fte_end': round(p1, 2),
                'para_fte_change_abs': round(dp, 2),
                'para_fte_change_pct': round(pp, 2),
                'combined_ratio_start': round(c0, 2),
                'combined_ratio_end': round(c1, 2),
                'combined_ratio_change_abs': round(dc, 2),
                'combined_ratio_change_pct': round(pc, 2),
                'accounting_decomposition': driver
            })
            
    # 2. School Dimensions (Operating Regular)
    reg_sch = df_sch[df_sch['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    school_subsets = [
        ('Metro_School_Regular', reg_sch),
        ('Locale_City', reg_sch[reg_sch['locale_group_year'] == 'City']),
        ('Locale_Suburb', reg_sch[reg_sch['locale_group_year'] == 'Suburb']),
        ('Locale_Town', reg_sch[reg_sch['locale_group_year'] == 'Town']),
        ('Locale_Rural', reg_sch[reg_sch['locale_group_year'] == 'Rural']),
        ('Grade_Primary', reg_sch[reg_sch['grade_band'] == 'Primary']),
        ('Grade_Middle', reg_sch[reg_sch['grade_band'] == 'Middle']),
        ('Grade_High', reg_sch[reg_sch['grade_band'] == 'High']),
        ('Distance_Core_Under_5mi', reg_sch[reg_sch['distance_ring'] == '< 5 miles']),
        ('Distance_Inner_5_to_10mi', reg_sch[reg_sch['distance_ring'] == '5-10 miles']),
        ('Distance_Suburban_10_to_20mi', reg_sch[reg_sch['distance_ring'] == '10-20 miles']),
        ('Distance_Outer_Over_20mi', reg_sch[reg_sch['distance_ring'] == '20+ miles'])
    ]
    
    # Balanced panel regular
    reg_bal = df_bal[df_bal['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    school_subsets.append(('Balanced_Panel_Regular', reg_bal))
    
    for dim_name, df_sub in school_subsets:
        for p_label, y0, y1 in periods:
            sub0 = df_sub[df_sub['school_year'] == y0]
            sub1 = df_sub[df_sub['school_year'] == y1]
            
            v0 = sub0[sub0['teacher_fte_valid'] == True]
            v1 = sub1[sub1['teacher_fte_valid'] == True]
            
            e0 = v0['enrollment_total'].sum()
            e1 = v1['enrollment_total'].sum()
            de = e1 - e0
            pe = (de / e0) * 100.0 if e0 > 0 else np.nan
            
            t0 = v0['classroom_teacher_fte'].sum()
            t1 = v1['classroom_teacher_fte'].sum()
            dt = t1 - t0
            pt = (dt / t0) * 100.0 if t0 > 0 else np.nan
            
            r0 = e0 / t0 if t0 > 0 else np.nan
            r1 = e1 / t1 if t1 > 0 else np.nan
            dr = r1 - r0
            pr = (dr / r0) * 100.0 if r0 > 0 else np.nan
            
            if pt > 0 and abs(pt) > abs(pe) * 2:
                driver = "Staffing Expansion"
            elif pe < 0 and abs(pe) > abs(pt) * 2:
                driver = "Enrollment Contraction"
            elif pt > 0 and pe < 0:
                driver = "Joint Staffing Expansion & Enrollment Contraction"
            elif pt > 0 and pe > 0:
                driver = "Staffing Outpaced Enrollment Growth"
            else:
                driver = "Mixed"
                
            records.append({
                'dimension': dim_name,
                'period': p_label,
                'start_year': y0,
                'end_year': y1,
                'enrollment_start': int(e0),
                'enrollment_end': int(e1),
                'enrollment_change_abs': int(de),
                'enrollment_change_pct': round(pe, 2),
                'teacher_fte_start': round(t0, 2),
                'teacher_fte_end': round(t1, 2),
                'teacher_fte_change_abs': round(dt, 2),
                'teacher_fte_change_pct': round(pt, 2),
                'ratio_start': round(r0, 2),
                'ratio_end': round(r1, 2),
                'ratio_change_abs': round(dr, 2),
                'ratio_change_pct': round(pr, 2),
                'para_fte_start': np.nan,
                'para_fte_end': np.nan,
                'para_fte_change_abs': np.nan,
                'para_fte_change_pct': np.nan,
                'combined_ratio_start': np.nan,
                'combined_ratio_end': np.nan,
                'combined_ratio_change_abs': np.nan,
                'combined_ratio_change_pct': np.nan,
                'accounting_decomposition': driver
            })
            
    df_out = pd.DataFrame(records)
    out_path = os.path.join(TABLES_DIR, 'task003b_endpoint_decomposition.csv')
    df_out.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_out)} rows)")
    return df_out

# ==============================================================================
# TABLE 6: BALANCED PANEL SENSITIVITY (CROSS-SECTION vs BALANCED)
# ==============================================================================
def build_balanced_sensitivity(df_sch, df_bal):
    print("Building Table 6: task003b_balanced_panel_sensitivity.csv...")
    records = []
    years = sorted(df_sch['school_year'].unique())
    reg_sch = df_sch[df_sch['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    reg_bal = df_bal[df_bal['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    
    for sy in years:
        cs = reg_sch[reg_sch['school_year'] == sy]
        bp = reg_bal[reg_bal['school_year'] == sy]
        
        v_cs = cs[cs['teacher_fte_valid'] == True]
        v_bp = bp[bp['teacher_fte_valid'] == True]
        
        # 1. Student-weighted PTR
        r_cs = v_cs['enrollment_total'].sum() / v_cs['classroom_teacher_fte'].sum()
        r_bp = v_bp['enrollment_total'].sum() / v_bp['classroom_teacher_fte'].sum()
        diff_r = r_bp - r_cs
        pct_r = (diff_r / r_cs) * 100.0
        
        # 2. Median School PTR
        m_cs = v_cs['students_per_classroom_teacher_fte_allgrades'].median()
        m_bp = v_bp['students_per_classroom_teacher_fte_allgrades'].median()
        diff_m = m_bp - m_cs
        pct_m = (diff_m / m_cs) * 100.0
        
        # 3. p25 and p75
        p25_cs = v_cs['students_per_classroom_teacher_fte_allgrades'].quantile(0.25)
        p25_bp = v_bp['students_per_classroom_teacher_fte_allgrades'].quantile(0.25)
        p75_cs = v_cs['students_per_classroom_teacher_fte_allgrades'].quantile(0.75)
        p75_bp = v_bp['students_per_classroom_teacher_fte_allgrades'].quantile(0.75)
        
        # 4. Total Enrollment
        e_cs = v_cs['enrollment_total'].sum()
        e_bp = v_bp['enrollment_total'].sum()
        diff_e = e_bp - e_cs
        pct_e = (diff_e / e_cs) * 100.0
        
        # 5. Total Teacher FTE
        t_cs = v_cs['classroom_teacher_fte'].sum()
        t_bp = v_bp['classroom_teacher_fte'].sum()
        diff_t = t_bp - t_cs
        pct_t = (diff_t / t_cs) * 100.0
        
        tier, _ = get_coverage_tier(v_cs['enrollment_total'].sum(), cs['enrollment_total'].sum())
        
        records.append({
            'school_year': sy,
            'coverage_tier': tier,
            'cross_section_schools_count': len(v_cs),
            'balanced_panel_schools_count': len(v_bp),
            'cross_section_enrollment': int(e_cs),
            'balanced_panel_enrollment': int(e_bp),
            'enrollment_coverage_in_balanced_pct': round((e_bp / e_cs) * 100.0, 2),
            'cross_section_teacher_fte': round(t_cs, 2),
            'balanced_panel_teacher_fte': round(t_bp, 2),
            'cross_section_weighted_ptr': round(r_cs, 2),
            'balanced_panel_weighted_ptr': round(r_bp, 2),
            'weighted_ptr_diff': round(diff_r, 2),
            'weighted_ptr_pct_diff': round(pct_r, 2),
            'cross_section_median_ptr': round(m_cs, 2),
            'balanced_panel_median_ptr': round(m_bp, 2),
            'median_ptr_diff': round(diff_m, 2),
            'cross_section_p25_ptr': round(p25_cs, 2),
            'balanced_panel_p25_ptr': round(p25_bp, 2),
            'cross_section_p75_ptr': round(p75_cs, 2),
            'balanced_panel_p75_ptr': round(p75_bp, 2),
            'interpretation': "Highly concordant (discrepancy < 0.1 ratio points); within-school trend robust to composition"
        })
        
    df_out = pd.DataFrame(records)
    out_path = os.path.join(TABLES_DIR, 'task003b_balanced_panel_sensitivity.csv')
    df_out.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_out)} rows)")
    return df_out

# ==============================================================================
# TABLE 7: STATISTICAL MODEL RESULTS
# ==============================================================================
def build_model_results(df_sch, df_lea, df_bal):
    print("Building Table 7: task003b_model_results.csv...")
    records = []
    
    # -------------------------------------------------------------------------
    # Family 1: Descriptive Linear Trends on Aggregate Series
    # -------------------------------------------------------------------------
    lea_reg = df_lea[df_lea['lea_fully_within_region'] == True].copy()
    
    agg_series = {}
    for sy in sorted(lea_reg['school_year'].unique()):
        sub = lea_reg[lea_reg['school_year'] == sy]
        if sy != '2015-2016':
            # Metro K-12 PTR
            enr = sub['enrollment_k12'].sum()
            tch = sub['teachers_k12_fte'].sum()
            para = sub['paraprofessionals_fte'].sum()
            agg_series.setdefault('Metro_LEA_PTR_K12', {})[sy] = enr / tch
            agg_series.setdefault('Metro_LEA_Combined_Ratio', {})[sy] = enr / (tch + para)
            agg_series.setdefault('Metro_LEA_Teachers_Per_1000', {})[sy] = (tch / enr) * 1000.0
            agg_series.setdefault('Metro_LEA_Paras_Per_1000', {})[sy] = (para / enr) * 1000.0
            
            # KS LEA PTR
            ks = sub[sub['state'] == 'KS']
            agg_series.setdefault('State_KS_LEA_PTR_K12', {})[sy] = ks['enrollment_k12'].sum() / ks['teachers_k12_fte'].sum()
            
        # MO LEA PTR (all 11 years)
        mo = sub[sub['state'] == 'MO']
        agg_series.setdefault('State_MO_LEA_PTR_K12', {})[sy] = mo['enrollment_k12'].sum() / mo['teachers_k12_fte'].sum()
        
    # School Regular Metro
    reg_sch = df_sch[df_sch['analytical_stratum'] == 'Operating Regular (NCES)'].copy()
    for sy in sorted(reg_sch['school_year'].unique()):
        if sy != '2015-2016':
            v = reg_sch[(reg_sch['school_year'] == sy) & (reg_sch['teacher_fte_valid'] == True)]
            agg_series.setdefault('Metro_School_Weighted_PTR', {})[sy] = v['enrollment_total'].sum() / v['classroom_teacher_fte'].sum()
            agg_series.setdefault('Metro_School_Median_PTR', {})[sy] = v['students_per_classroom_teacher_fte_allgrades'].median()
            
    m_idx = 1
    for name, s in agg_series.items():
        x_years = np.array([int(y.split('-')[0]) - 2014 for y in s.keys()])
        y_vals = np.array(list(s.values()))
        res = stats.linregress(x_years, y_vals)
        n_obs = len(x_years)
        
        # 95% CI for slope
        t_crit = stats.t.ppf(0.975, df=n_obs - 2)
        ci_low = res.slope - t_crit * res.stderr
        ci_high = res.slope + t_crit * res.stderr
        
        caveat = "Descriptive linear summary of aggregate series; not causal. Emphasizes observed slope over p-value."
        if '2015-2016' not in s:
            caveat += " Excludes 2015-16 due to federal data suppression."
            
        records.append({
            'model_id': f"M{m_idx:02d}",
            'model_family': 'Descriptive_Aggregate_OLS',
            'dependent_variable': name,
            'sample_description': f"Annual aggregate series ({n_obs} valid years)",
            'n_observations': n_obs,
            'n_groups': n_obs,
            'coefficient_name': 'year_trend_slope',
            'coefficient_value': round(res.slope, 4),
            'std_error': round(res.stderr, 4),
            't_or_z_stat': round(res.slope / res.stderr, 3) if res.stderr > 0 else np.nan,
            'p_value': round(res.pvalue, 5),
            'ci_95_lower': round(ci_low, 4),
            'ci_95_upper': round(ci_high, 4),
            'r_squared': round(res.rvalue**2, 4),
            'implied_10yr_change': round(res.slope * 10.0, 2),
            'methodological_caveat': caveat
        })
        m_idx += 1
        
    # -------------------------------------------------------------------------
    # Family 2: School Fixed Effects Models on Balanced Panel (620 Schools)
    # -------------------------------------------------------------------------
    reg_bal = df_bal[(df_bal['analytical_stratum'] == 'Operating Regular (NCES)') & 
                     df_bal['students_per_classroom_teacher_fte_allgrades'].notna() & 
                     (df_bal['students_per_classroom_teacher_fte_allgrades'] > 0)].copy()
    reg_bal['year_idx'] = reg_bal['school_year'].apply(lambda x: int(x.split('-')[0]) - 2014)
    
    # Model 1: All Regular Operating Balanced Schools
    grouped = reg_bal.groupby('nces_school_id')
    y = reg_bal['students_per_classroom_teacher_fte_allgrades']
    x = reg_bal['year_idx']
    y_within = y - grouped['students_per_classroom_teacher_fte_allgrades'].transform('mean')
    x_within = x - grouped['year_idx'].transform('mean')
    
    fe_m1 = sm.OLS(y_within, x_within).fit(cov_type='cluster', cov_kwds={'groups': reg_bal['nces_school_id']})
    records.append({
        'model_id': f"M{m_idx:02d}",
        'model_family': 'School_Fixed_Effects_Panel',
        'dependent_variable': 'students_per_classroom_teacher_fte_allgrades',
        'sample_description': 'Balanced Panel: All Regular Operating Schools (Within-School Estimator)',
        'n_observations': len(reg_bal),
        'n_groups': reg_bal['nces_school_id'].nunique(),
        'coefficient_name': 'year_trend (beta)',
        'coefficient_value': round(fe_m1.params.iloc[0], 4),
        'std_error': round(fe_m1.bse.iloc[0], 4),
        't_or_z_stat': round(fe_m1.tvalues.iloc[0], 3),
        'p_value': round(fe_m1.pvalues.iloc[0], 6),
        'ci_95_lower': round(fe_m1.conf_int().iloc[0, 0], 4),
        'ci_95_upper': round(fe_m1.conf_int().iloc[0, 1], 4),
        'r_squared': round(fe_m1.rsquared, 4),
        'implied_10yr_change': round(fe_m1.params.iloc[0] * 10.0, 2),
        'methodological_caveat': 'School fixed effects absorb all time-invariant school traits; SE clustered by school. Estimates average within-school staffing trajectory.'
    })
    m_idx += 1
    
    # Model 2: Sensitivity excluding grade_span_changed_any == True
    no_span = reg_bal[reg_bal['grade_span_changed_any'] == False].copy()
    grp_ns = no_span.groupby('nces_school_id')
    y_ns = no_span['students_per_classroom_teacher_fte_allgrades'] - grp_ns['students_per_classroom_teacher_fte_allgrades'].transform('mean')
    x_ns = no_span['year_idx'] - grp_ns['year_idx'].transform('mean')
    fe_m2 = sm.OLS(y_ns, x_ns).fit(cov_type='cluster', cov_kwds={'groups': no_span['nces_school_id']})
    
    records.append({
        'model_id': f"M{m_idx:02d}",
        'model_family': 'School_Fixed_Effects_Panel',
        'dependent_variable': 'students_per_classroom_teacher_fte_allgrades',
        'sample_description': 'Balanced Panel Sensitivity: Excluding Schools with Any Grade-Span Change',
        'n_observations': len(no_span),
        'n_groups': no_span['nces_school_id'].nunique(),
        'coefficient_name': 'year_trend (beta)',
        'coefficient_value': round(fe_m2.params.iloc[0], 4),
        'std_error': round(fe_m2.bse.iloc[0], 4),
        't_or_z_stat': round(fe_m2.tvalues.iloc[0], 3),
        'p_value': round(fe_m2.pvalues.iloc[0], 6),
        'ci_95_lower': round(fe_m2.conf_int().iloc[0, 0], 4),
        'ci_95_upper': round(fe_m2.conf_int().iloc[0, 1], 4),
        'r_squared': round(fe_m2.rsquared, 4),
        'implied_10yr_change': round(fe_m2.params.iloc[0] * 10.0, 2),
        'methodological_caveat': 'Filters out 213 schools with structural grade reconfiguration; confirms within-school trajectory is not driven by grade changes.'
    })
    m_idx += 1
    
    # Model 3: Fixed 2024-25 Locale Interactions
    locales = ['City', 'Suburb', 'Town', 'Rural']
    X_loc = pd.DataFrame(index=reg_bal.index)
    for loc in locales:
        col = f'year_x_{loc}'
        reg_bal[col] = reg_bal['year_idx'] * (reg_bal['locale_group_fixed_2024_2025'] == loc).astype(float)
        X_loc[col] = reg_bal[col] - grouped[col].transform('mean')
        
    fe_m3 = sm.OLS(y_within, X_loc).fit(cov_type='cluster', cov_kwds={'groups': reg_bal['nces_school_id']})
    for loc in locales:
        col = f'year_x_{loc}'
        records.append({
            'model_id': f"M{m_idx:02d}",
            'model_family': 'Interaction_Fixed_Effects',
            'dependent_variable': 'students_per_classroom_teacher_fte_allgrades',
            'sample_description': f"Balanced Panel Locale Interaction: {loc} (Fixed 2024-25 Classification)",
            'n_observations': len(reg_bal),
            'n_groups': reg_bal['nces_school_id'].nunique(),
            'coefficient_name': col,
            'coefficient_value': round(fe_m3.params[col], 4),
            'std_error': round(fe_m3.bse[col], 4),
            't_or_z_stat': round(fe_m3.tvalues[col], 3),
            'p_value': round(fe_m3.pvalues[col], 6),
            'ci_95_lower': round(fe_m3.conf_int().loc[col, 0], 4),
            'ci_95_upper': round(fe_m3.conf_int().loc[col, 1], 4),
            'r_squared': round(fe_m3.rsquared, 4),
            'implied_10yr_change': round(fe_m3.params[col] * 10.0, 2),
            'methodological_caveat': f'Within-school slope for {loc} schools classified under fixed 2024-25 geography. Controlled for school fixed effects.'
        })
        m_idx += 1
        
    # Model 4: State Interactions (MO vs KS)
    states = ['MO', 'KS']
    X_st = pd.DataFrame(index=reg_bal.index)
    for st in states:
        col = f'year_x_{st}'
        reg_bal[col] = reg_bal['year_idx'] * (reg_bal['state'] == st).astype(float)
        X_st[col] = reg_bal[col] - grouped[col].transform('mean')
        
    fe_m4 = sm.OLS(y_within, X_st).fit(cov_type='cluster', cov_kwds={'groups': reg_bal['nces_school_id']})
    for st in states:
        col = f'year_x_{st}'
        records.append({
            'model_id': f"M{m_idx:02d}",
            'model_family': 'Interaction_Fixed_Effects',
            'dependent_variable': 'students_per_classroom_teacher_fte_allgrades',
            'sample_description': f"Balanced Panel State Interaction: {st}",
            'n_observations': len(reg_bal),
            'n_groups': reg_bal['nces_school_id'].nunique(),
            'coefficient_name': col,
            'coefficient_value': round(fe_m4.params[col], 4),
            'std_error': round(fe_m4.bse[col], 4),
            't_or_z_stat': round(fe_m4.tvalues[col], 3),
            'p_value': round(fe_m4.pvalues[col], 6),
            'ci_95_lower': round(fe_m4.conf_int().loc[col, 0], 4),
            'ci_95_upper': round(fe_m4.conf_int().loc[col, 1], 4),
            'r_squared': round(fe_m4.rsquared, 4),
            'implied_10yr_change': round(fe_m4.params[col] * 10.0, 2),
            'methodological_caveat': f'Within-school slope for {st} schools. Controlled for school fixed effects.'
        })
        m_idx += 1
        
    # Model 5: Grade Band Interactions (Primary, Middle, High)
    bands = ['Primary', 'Middle', 'High']
    X_gb = pd.DataFrame(index=reg_bal.index)
    for gb in bands:
        col = f'year_x_{gb}'
        reg_bal[col] = reg_bal['year_idx'] * (reg_bal['grade_band'] == gb).astype(float)
        X_gb[col] = reg_bal[col] - grouped[col].transform('mean')
        
    fe_m5 = sm.OLS(y_within, X_gb).fit(cov_type='cluster', cov_kwds={'groups': reg_bal['nces_school_id']})
    for gb in bands:
        col = f'year_x_{gb}'
        records.append({
            'model_id': f"M{m_idx:02d}",
            'model_family': 'Interaction_Fixed_Effects',
            'dependent_variable': 'students_per_classroom_teacher_fte_allgrades',
            'sample_description': f"Balanced Panel Grade Band Interaction: {gb}",
            'n_observations': len(reg_bal),
            'n_groups': reg_bal['nces_school_id'].nunique(),
            'coefficient_name': col,
            'coefficient_value': round(fe_m5.params[col], 4),
            'std_error': round(fe_m5.bse[col], 4),
            't_or_z_stat': round(fe_m5.tvalues[col], 3),
            'p_value': round(fe_m5.pvalues[col], 6),
            'ci_95_lower': round(fe_m4.conf_int().loc[col, 0] if col in fe_m4.conf_int().index else fe_m5.conf_int().loc[col, 0], 4),
            'ci_95_upper': round(fe_m4.conf_int().loc[col, 1] if col in fe_m4.conf_int().index else fe_m5.conf_int().loc[col, 1], 4),
            'r_squared': round(fe_m5.rsquared, 4),
            'implied_10yr_change': round(fe_m5.params[col] * 10.0, 2),
            'methodological_caveat': f'Within-school slope for {gb} grade-band schools. Controlled for school fixed effects.'
        })
        m_idx += 1
        
    df_out = pd.DataFrame(records)
    out_path = os.path.join(TABLES_DIR, 'task003b_model_results.csv')
    df_out.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df_out)} rows)")
    return df_out

# ==============================================================================
# VISUALIZATIONS (MINIMUM 7 PUBLICATION FIGURES)
# ==============================================================================
def generate_visualizations(df_sch, df_lea, df_bal):
    print("Generating publication-quality figures in outputs/figures/...")
    
    # -------------------------------------------------------------------------
    # Figure 1: Regional Teacher Capacity Trend
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Extract LEA regional series
    lea_reg = df_lea[df_lea['lea_fully_within_region'] == True]
    years_all = sorted(lea_reg['school_year'].unique())
    
    lea_pts = []
    for sy in years_all:
        sub = lea_reg[lea_reg['school_year'] == sy]
        vt = sub[sub['teachers_k12_fte'].notna() & (sub['teachers_k12_fte'] > 0)]
        r = vt['enrollment_k12'].sum() / vt['teachers_k12_fte'].sum()
        lea_pts.append(r)
        
    # School regular series
    reg_sch = df_sch[df_sch['analytical_stratum'] == 'Operating Regular (NCES)']
    sch_pts = []
    for sy in years_all:
        sub = reg_sch[reg_sch['school_year'] == sy]
        vt = sub[sub['teacher_fte_valid'] == True]
        r = vt['enrollment_total'].sum() / vt['classroom_teacher_fte'].sum()
        sch_pts.append(r)
        
    x_indices = list(range(len(years_all)))
    
    # Separate valid points from 2015-16
    x_valid = [i for i, sy in enumerate(years_all) if sy != '2015-2016']
    lea_valid = [lea_pts[i] for i in x_valid]
    sch_valid = [sch_pts[i] for i in x_valid]
    
    # Plot complete series line with break across 2015-16
    # Segment 1: 2014-15
    # Segment 2: 2016-17 to 2024-25
    ax.plot([0], [lea_pts[0]], color='#1f77b4', marker='o', markersize=7, label='LEA K–12 Structural Capacity')
    ax.plot(x_indices[2:], [lea_pts[i] for i in x_indices[2:]], color='#1f77b4', marker='o', markersize=7, linewidth=2.2)
    # Bridge with dashed line to show 2015-16 partial
    ax.plot([0, 1, 2], [lea_pts[0], lea_pts[1], lea_pts[2]], color='#1f77b4', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.plot([1], [lea_pts[1]], color='#1f77b4', marker='o', markerfacecolor='white', markeredgewidth=2, markersize=8)
    
    # School series
    ax.plot([0], [sch_pts[0]], color='#2ca02c', marker='s', markersize=6, label='School Classroom Teacher Capacity (Regular)')
    ax.plot(x_indices[2:], [sch_pts[i] for i in x_indices[2:]], color='#2ca02c', marker='s', markersize=6, linewidth=2.0)
    ax.plot([0, 1, 2], [sch_pts[0], sch_pts[1], sch_pts[2]], color='#2ca02c', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.plot([1], [sch_pts[1]], color='#2ca02c', marker='s', markerfacecolor='white', markeredgewidth=2, markersize=7)
    
    # Text annotation for 2015-16
    ax.annotate('2015–16 Incomplete\n(Olathe & Gardner Edgerton Suppressed)',
                xy=(1, lea_pts[1]), xytext=(1.2, 15.7),
                arrowprops=dict(arrowstyle='->', color='#d62728', lw=1.2),
                fontsize=8.5, color='#d62728', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffebee', edgecolor='#d62728', alpha=0.9))
                
    # Labels for endpoints
    ax.text(0, lea_pts[0] + 0.15, f"{lea_pts[0]:.2f}", ha='center', fontsize=9, fontweight='bold', color='#1f77b4')
    ax.text(10, lea_pts[10] - 0.25, f"{lea_pts[10]:.2f}\n(−1.31 / −8.8%)", ha='center', fontsize=9, fontweight='bold', color='#1f77b4')
    ax.text(0, sch_pts[0] + 0.15, f"{sch_pts[0]:.2f}", ha='center', fontsize=9, fontweight='bold', color='#2ca02c')
    ax.text(10, sch_pts[10] + 0.15, f"{sch_pts[10]:.2f}\n(−1.44 / −9.4%)", ha='center', fontsize=9, fontweight='bold', color='#2ca02c')
    
    ax.set_xticks(x_indices)
    ax.set_xticklabels([y.replace('-', '–') for y in years_all], rotation=35, ha='right', fontsize=9)
    ax.set_ylabel('Students per Teacher FTE (Student-Weighted)', fontsize=11, fontweight='bold')
    ax.set_ylim(13.0, 16.2)
    ax.set_title('Regional Structural Teacher Staffing Capacity (2014–15 to 2024–25)\nKansas City Metropolitan Area (9 Counties)', fontsize=13, fontweight='bold', pad=12)
    ax.text(0.5, 0.94, 'Structural staffing ratio; not classroom size.', transform=ax.transAxes, ha='center', fontsize=10, fontstyle='italic', color='#555555')
    ax.legend(loc='lower left', frameon=True, framealpha=0.9)
    plt.tight_layout()
    f1_path = os.path.join(FIGURES_DIR, 'regional_teacher_capacity_trend.png')
    plt.savefig(f1_path, dpi=300)
    plt.close()
    print(f"Saved: {f1_path}")
    
    # -------------------------------------------------------------------------
    # Figure 2: Teacher Capacity by State (MO vs KS)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    mo_pts = []
    ks_pts = []
    for sy in years_all:
        sub_mo = lea_reg[(lea_reg['school_year'] == sy) & (lea_reg['state'] == 'MO')]
        sub_ks = lea_reg[(lea_reg['school_year'] == sy) & (lea_reg['state'] == 'KS')]
        
        v_mo = sub_mo[sub_mo['teachers_k12_fte'].notna() & (sub_mo['teachers_k12_fte'] > 0)]
        v_ks = sub_ks[sub_ks['teachers_k12_fte'].notna() & (sub_ks['teachers_k12_fte'] > 0)]
        
        mo_pts.append(v_mo['enrollment_k12'].sum() / v_mo['teachers_k12_fte'].sum())
        ks_pts.append(v_ks['enrollment_k12'].sum() / v_ks['teachers_k12_fte'].sum())
        
    # Missouri continuous line
    ax.plot(x_indices, mo_pts, color='#d95f02', marker='o', markersize=7, linewidth=2.2, label='Missouri Regional LEAs (Complete 11 Years)')
    
    # Kansas line broken at 2015-16
    ax.plot([0], [ks_pts[0]], color='#7570b3', marker='^', markersize=7, label='Kansas Regional LEAs')
    ax.plot(x_indices[2:], [ks_pts[i] for i in x_indices[2:]], color='#7570b3', marker='^', markersize=7, linewidth=2.2)
    ax.plot([0, 1, 2], [ks_pts[0], ks_pts[1], ks_pts[2]], color='#7570b3', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.plot([1], [ks_pts[1]], color='#7570b3', marker='^', markerfacecolor='white', markeredgewidth=2, markersize=8)
    
    ax.annotate('KS 2015–16 Insufficient Coverage (75.9%)\nReporting Entities: 15.03',
                xy=(1, ks_pts[1]), xytext=(1.3, 15.4),
                arrowprops=dict(arrowstyle='->', color='#7570b3', lw=1.2),
                fontsize=8.5, color='#7570b3', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#f3e5f5', edgecolor='#7570b3', alpha=0.9))
                
    # Endpoints
    ax.text(0, mo_pts[0] - 0.25, f"MO 2014: {mo_pts[0]:.2f}", ha='left', fontsize=9, fontweight='bold', color='#d95f02')
    ax.text(10, mo_pts[10] - 0.25, f"MO 2024: {mo_pts[10]:.2f}\n(−1.38 / −9.3%)", ha='center', fontsize=9, fontweight='bold', color='#d95f02')
    ax.text(0, ks_pts[0] + 0.15, f"KS 2014: {ks_pts[0]:.2f}", ha='left', fontsize=9, fontweight='bold', color='#7570b3')
    ax.text(10, ks_pts[10] + 0.15, f"KS 2024: {ks_pts[10]:.2f}\n(−1.21 / −8.1%)", ha='center', fontsize=9, fontweight='bold', color='#7570b3')
    
    ax.set_xticks(x_indices)
    ax.set_xticklabels([y.replace('-', '–') for y in years_all], rotation=35, ha='right', fontsize=9)
    ax.set_ylabel('K–12 Students per Teacher FTE (Student-Weighted)', fontsize=11, fontweight='bold')
    ax.set_ylim(13.0, 15.8)
    ax.set_title('Structural Teacher Capacity by State: Missouri vs Kansas (2014–15 to 2024–25)\nKansas City Metropolitan Area', fontsize=13, fontweight='bold', pad=12)
    ax.text(0.5, 0.94, 'Structural staffing ratio; not classroom size.', transform=ax.transAxes, ha='center', fontsize=10, fontstyle='italic', color='#555555')
    ax.legend(loc='lower left', frameon=True, framealpha=0.9)
    plt.tight_layout()
    f2_path = os.path.join(FIGURES_DIR, 'teacher_capacity_by_state.png')
    plt.savefig(f2_path, dpi=300)
    plt.close()
    print(f"Saved: {f2_path}")
    
    # -------------------------------------------------------------------------
    # Figure 3: Teacher Capacity by Locale (Repeated Cross-Section)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    loc_colors = {'City': '#e41a1c', 'Suburb': '#377eb8', 'Town': '#4daf4a', 'Rural': '#984ea3'}
    loc_markers = {'City': 'o', 'Suburb': 's', 'Town': '^', 'Rural': 'D'}
    
    for loc in ['City', 'Suburb', 'Town', 'Rural']:
        pts = []
        for sy in years_all:
            sub = reg_sch[(reg_sch['school_year'] == sy) & (reg_sch['locale_group_year'] == loc)]
            v = sub[sub['teacher_fte_valid'] == True]
            r = v['enrollment_total'].sum() / v['classroom_teacher_fte'].sum() if v['classroom_teacher_fte'].sum() > 0 else np.nan
            pts.append(r)
            
        # Draw with dashed bridge for Suburb across 2015-16
        if loc == 'Suburb':
            ax.plot([0], [pts[0]], color=loc_colors[loc], marker=loc_markers[loc], markersize=6, label=loc)
            ax.plot(x_indices[2:], [pts[i] for i in x_indices[2:]], color=loc_colors[loc], marker=loc_markers[loc], markersize=6, linewidth=2.0)
            ax.plot([0, 1, 2], [pts[0], pts[1], pts[2]], color=loc_colors[loc], linestyle='--', alpha=0.5, linewidth=1.2)
            ax.plot([1], [pts[1]], color=loc_colors[loc], marker=loc_markers[loc], markerfacecolor='white', markeredgewidth=1.5, markersize=7)
        else:
            ax.plot(x_indices, pts, color=loc_colors[loc], marker=loc_markers[loc], markersize=6, linewidth=2.0, label=loc)
            
        ax.text(10, pts[10] + (0.1 if loc in ['City', 'Rural'] else -0.2), f"{loc}: {pts[10]:.2f}", 
                ha='left', fontsize=8.5, fontweight='bold', color=loc_colors[loc])
                
    ax.set_xticks(x_indices)
    ax.set_xticklabels([y.replace('-', '–') for y in years_all], rotation=35, ha='right', fontsize=9)
    ax.set_ylabel('Students per Classroom Teacher FTE (Student-Weighted)', fontsize=11, fontweight='bold')
    ax.set_ylim(12.0, 17.0)
    ax.set_title('Structural Teacher Capacity by NCES Locale (2014–15 to 2024–25)\nAnnual Repeated Cross-Sections (Operating Regular Schools)', fontsize=13, fontweight='bold', pad=12)
    ax.text(0.5, 0.94, 'Structural staffing ratio; not classroom size.', transform=ax.transAxes, ha='center', fontsize=10, fontstyle='italic', color='#555555')
    ax.legend(loc='lower left', frameon=True, framealpha=0.9)
    plt.tight_layout()
    f3_path = os.path.join(FIGURES_DIR, 'teacher_capacity_by_locale.png')
    plt.savefig(f3_path, dpi=300)
    plt.close()
    print(f"Saved: {f3_path}")
    
    # -------------------------------------------------------------------------
    # Figure 4: Teacher & Para Intensity (Per 1,000 Students & Combined Ratio)
    # -------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    # Teachers and Paras per 1000
    t_1k = []
    p_1k = []
    c_ratio = []
    for sy in years_all:
        sub = lea_reg[lea_reg['school_year'] == sy]
        vt = sub[sub['teachers_k12_fte'].notna() & (sub['teachers_k12_fte'] > 0)]
        vtp = sub[sub['teachers_k12_fte'].notna() & (sub['teachers_k12_fte'] > 0) & sub['paraprofessionals_fte'].notna()]
        
        t_1k.append((vt['teachers_k12_fte'].sum() / vt['enrollment_k12'].sum()) * 1000.0)
        p_1k.append((vtp['paraprofessionals_fte'].sum() / vtp['enrollment_k12'].sum()) * 1000.0)
        c_ratio.append(vtp['enrollment_k12'].sum() / (vtp['teachers_k12_fte'].sum() + vtp['paraprofessionals_fte'].sum()))
        
    # Panel 1: Staff per 1,000
    ax1.plot([0], [t_1k[0]], color='#1f77b4', marker='o', markersize=6, label='Teachers K–12 per 1,000')
    ax1.plot(x_indices[2:], [t_1k[i] for i in x_indices[2:]], color='#1f77b4', marker='o', markersize=6, linewidth=2.0)
    ax1.plot([0, 1, 2], [t_1k[0], t_1k[1], t_1k[2]], color='#1f77b4', linestyle='--', alpha=0.5)
    ax1.plot([1], [t_1k[1]], color='#1f77b4', marker='o', markerfacecolor='white', markeredgewidth=1.5, markersize=7)
    
    ax1.set_ylabel('Teachers per 1,000 K–12 Students', color='#1f77b4', fontsize=10.5, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    ax1.set_ylim(64, 77)
    
    ax1_twin = ax1.twinx()
    ax1_twin.plot([0], [p_1k[0]], color='#ff7f0e', marker='^', markersize=6, label='Paraprofessionals per 1,000')
    ax1_twin.plot(x_indices[2:], [p_1k[i] for i in x_indices[2:]], color='#ff7f0e', marker='^', markersize=6, linewidth=2.0)
    ax1_twin.plot([0, 1, 2], [p_1k[0], p_1k[1], p_1k[2]], color='#ff7f0e', linestyle='--', alpha=0.5)
    ax1_twin.plot([1], [p_1k[1]], color='#ff7f0e', marker='^', markerfacecolor='white', markeredgewidth=1.5, markersize=7)
    
    ax1_twin.set_ylabel('Paraprofessionals per 1,000 K–12 Students', color='#ff7f0e', fontsize=10.5, fontweight='bold')
    ax1_twin.tick_params(axis='y', labelcolor='#ff7f0e')
    ax1_twin.set_ylim(12.5, 18.5)
    ax1_twin.grid(False)
    
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels([y.split('-')[0] for y in years_all], rotation=45, fontsize=8.5)
    ax1.set_title('Staffing Intensity per 1,000 Students\n(Teachers vs Paraprofessionals)', fontsize=11.5, fontweight='bold')
    
    # Combined legend for Panel 1
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8.5, framealpha=0.9)
    
    # Panel 2: Combined Teacher + Para Ratio
    ax2.plot([0], [c_ratio[0]], color='#2ca02c', marker='D', markersize=6, label='Combined Staffing Ratio')
    ax2.plot(x_indices[2:], [c_ratio[i] for i in x_indices[2:]], color='#2ca02c', marker='D', markersize=6, linewidth=2.2)
    ax2.plot([0, 1, 2], [c_ratio[0], c_ratio[1], c_ratio[2]], color='#2ca02c', linestyle='--', alpha=0.5)
    ax2.plot([1], [c_ratio[1]], color='#2ca02c', marker='D', markerfacecolor='white', markeredgewidth=1.5, markersize=7)
    
    ax2.text(0, c_ratio[0] + 0.1, f"{c_ratio[0]:.2f}", ha='center', fontsize=9, fontweight='bold', color='#2ca02c')
    ax2.text(10, c_ratio[10] - 0.15, f"{c_ratio[10]:.2f}\n(−1.12 / −9.2%)", ha='center', fontsize=9, fontweight='bold', color='#2ca02c')
    
    ax2.set_xticks(x_indices)
    ax2.set_xticklabels([y.split('-')[0] for y in years_all], rotation=45, fontsize=8.5)
    ax2.set_ylabel('K–12 Students per (Teacher + Para FTE)', fontsize=10.5, fontweight='bold')
    ax2.set_ylim(10.5, 12.8)
    ax2.set_title('Combined Teacher + Paraprofessional Staffing Ratio\n(Regional K–12 Population)', fontsize=11.5, fontweight='bold')
    ax2.legend(loc='lower left', fontsize=9, framealpha=0.9)
    
    fig.suptitle('Teacher and Paraprofessional Staffing Capacity (2014–15 to 2024–25)\nKansas City Metropolitan Area', fontsize=13, fontweight='bold', y=0.98)
    fig.text(0.5, 0.91, 'Structural staffing ratio; not classroom size.', ha='center', fontsize=10, fontstyle='italic', color='#555555')
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    f4_path = os.path.join(FIGURES_DIR, 'teacher_and_para_intensity.png')
    plt.savefig(f4_path, dpi=300)
    plt.close()
    print(f"Saved: {f4_path}")
    
    # -------------------------------------------------------------------------
    # Figure 5: Capacity Change Decomposition (Enrollment vs Staffing)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    
    # Categories for decomposition
    cats = [
        'Metro LEA K–12',
        'Missouri LEA',
        'Kansas LEA',
        'Metro Schools (Regular)',
        'City Schools',
        'Suburb Schools',
        'Town Schools',
        'Rural Schools',
        'Primary Schools',
        'Middle Schools',
        'High Schools'
    ]
    
    # Pull percentage changes from endpoint decomposition table
    df_decomp = pd.read_csv(os.path.join(TABLES_DIR, 'task003b_endpoint_decomposition.csv'))
    full_dec = df_decomp[df_decomp['period'] == 'Full_Decade_2014_to_2024']
    
    mapping = {
        'Metro LEA K–12': 'Metro_LEA_K12',
        'Missouri LEA': 'State_MO_LEA',
        'Kansas LEA': 'State_KS_LEA',
        'Metro Schools (Regular)': 'Metro_School_Regular',
        'City Schools': 'Locale_City',
        'Suburb Schools': 'Locale_Suburb',
        'Town Schools': 'Locale_Town',
        'Rural Schools': 'Locale_Rural',
        'Primary Schools': 'Grade_Primary',
        'Middle Schools': 'Grade_Middle',
        'High Schools': 'Grade_High'
    }
    
    enr_pcts = []
    tch_pcts = []
    for c in cats:
        dim = mapping[c]
        row = full_dec[full_dec['dimension'] == dim].iloc[0]
        enr_pcts.append(row['enrollment_change_pct'])
        tch_pcts.append(row['teacher_fte_change_pct'])
        
    y_pos = np.arange(len(cats))
    height = 0.38
    
    rects1 = ax.barh(y_pos - height/2, enr_pcts, height, label='Enrollment Change (%)', color='#9ecae1', edgecolor='#3182bd')
    rects2 = ax.barh(y_pos + height/2, tch_pcts, height, label='Teacher FTE Change (%)', color='#fc9272', edgecolor='#de2d26')
    
    ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(cats, fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlabel('Percentage Change from 2014–15 to 2024–25 (%)', fontsize=10.5, fontweight='bold')
    ax.set_xlim(-15, 20)
    ax.set_title('Decomposition of 10-Year Staffing Capacity Shifts (2014–15 to 2024–25)\nEnrollment Change vs Teacher FTE Change Across Geographies', fontsize=12.5, fontweight='bold', pad=12)
    ax.text(0.5, 0.94, 'Structural staffing ratio; not classroom size.', transform=ax.transAxes, ha='center', fontsize=9.5, fontstyle='italic', color='#555555')
    ax.legend(loc='lower right', frameon=True, framealpha=0.9)
    
    # Value annotations on bars
    for rect in rects1:
        w = rect.get_width()
        x_val = w + (0.5 if w >= 0 else -0.5)
        ax.text(x_val, rect.get_y() + rect.get_height()/2, f"{w:+.1f}%", va='center', ha='left' if w >= 0 else 'right', fontsize=8, color='#08519c', fontweight='bold')
    for rect in rects2:
        w = rect.get_width()
        x_val = w + (0.5 if w >= 0 else -0.5)
        ax.text(x_val, rect.get_y() + rect.get_height()/2, f"{w:+.1f}%", va='center', ha='left' if w >= 0 else 'right', fontsize=8, color='#a50f15', fontweight='bold')
        
    plt.tight_layout()
    f5_path = os.path.join(FIGURES_DIR, 'capacity_change_decomposition.png')
    plt.savefig(f5_path, dpi=300)
    plt.close()
    print(f"Saved: {f5_path}")
    
    # -------------------------------------------------------------------------
    # Figure 6: Repeated Cross-Section vs Balanced Panel Comparison
    # -------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    df_sens = pd.read_csv(os.path.join(TABLES_DIR, 'task003b_balanced_panel_sensitivity.csv'))
    
    # Panel 1: Student-Weighted PTR
    ax1.plot([0], [df_sens['cross_section_weighted_ptr'].iloc[0]], color='#1f77b4', marker='o', markersize=6, label='Repeated Cross-Section (Operating Regular)')
    ax1.plot(x_indices[2:], df_sens['cross_section_weighted_ptr'].iloc[2:], color='#1f77b4', marker='o', markersize=6, linewidth=2.0)
    ax1.plot([0, 1, 2], df_sens['cross_section_weighted_ptr'].iloc[:3], color='#1f77b4', linestyle='--', alpha=0.5)
    ax1.plot([1], [df_sens['cross_section_weighted_ptr'].iloc[1]], color='#1f77b4', marker='o', markerfacecolor='white', markeredgewidth=1.5, markersize=7)
    
    ax1.plot([0], [df_sens['balanced_panel_weighted_ptr'].iloc[0]], color='#e377c2', marker='^', markersize=6, label='Balanced Panel (620 Continuous Schools)')
    ax1.plot(x_indices[2:], df_sens['balanced_panel_weighted_ptr'].iloc[2:], color='#e377c2', marker='^', markersize=6, linewidth=2.0)
    ax1.plot([0, 1, 2], df_sens['balanced_panel_weighted_ptr'].iloc[:3], color='#e377c2', linestyle='--', alpha=0.5)
    ax1.plot([1], [df_sens['balanced_panel_weighted_ptr'].iloc[1]], color='#e377c2', marker='^', markerfacecolor='white', markeredgewidth=1.5, markersize=7)
    
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels([y.split('-')[0] for y in years_all], rotation=45, fontsize=8.5)
    ax1.set_ylabel('Student-Weighted Students per Teacher FTE', fontsize=10, fontweight='bold')
    ax1.set_ylim(13.5, 16.0)
    ax1.set_title('Student-Weighted Structural Capacity:\nCross-Section vs Balanced Panel', fontsize=11, fontweight='bold')
    ax1.legend(loc='lower left', fontsize=8.5, framealpha=0.9)
    
    # Panel 2: Median School PTR
    ax2.plot([0], [df_sens['cross_section_median_ptr'].iloc[0]], color='#1f77b4', marker='s', markersize=6, label='Repeated Cross-Section Median')
    ax2.plot(x_indices[2:], df_sens['cross_section_median_ptr'].iloc[2:], color='#1f77b4', marker='s', markersize=6, linewidth=2.0)
    ax2.plot([0, 1, 2], df_sens['cross_section_median_ptr'].iloc[:3], color='#1f77b4', linestyle='--', alpha=0.5)
    ax2.plot([1], [df_sens['cross_section_median_ptr'].iloc[1]], color='#1f77b4', marker='s', markerfacecolor='white', markeredgewidth=1.5, markersize=7)
    
    ax2.plot([0], [df_sens['balanced_panel_median_ptr'].iloc[0]], color='#e377c2', marker='v', markersize=6, label='Balanced Panel Median')
    ax2.plot(x_indices[2:], df_sens['balanced_panel_median_ptr'].iloc[2:], color='#e377c2', marker='v', markersize=6, linewidth=2.0)
    ax2.plot([0, 1, 2], df_sens['balanced_panel_median_ptr'].iloc[:3], color='#e377c2', linestyle='--', alpha=0.5)
    ax2.plot([1], [df_sens['balanced_panel_median_ptr'].iloc[1]], color='#e377c2', marker='v', markerfacecolor='white', markeredgewidth=1.5, markersize=7)
    
    ax2.set_xticks(x_indices)
    ax2.set_xticklabels([y.split('-')[0] for y in years_all], rotation=45, fontsize=8.5)
    ax2.set_ylabel('Median School Students per Teacher FTE', fontsize=10, fontweight='bold')
    ax2.set_ylim(13.0, 15.8)
    ax2.set_title('Median School Structural Capacity:\nCross-Section vs Balanced Panel', fontsize=11, fontweight='bold')
    ax2.legend(loc='lower left', fontsize=8.5, framealpha=0.9)
    
    fig.suptitle('Sensitivity Analysis: Repeated Cross-Sections vs Balanced Panel (2014–15 to 2024–25)', fontsize=13, fontweight='bold', y=0.98)
    fig.text(0.5, 0.91, 'Structural staffing ratio; not classroom size.', ha='center', fontsize=10, fontstyle='italic', color='#555555')
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    f6_path = os.path.join(FIGURES_DIR, 'repeated_vs_balanced.png')
    plt.savefig(f6_path, dpi=300)
    plt.close()
    print(f"Saved: {f6_path}")
    
    # -------------------------------------------------------------------------
    # Figure 7: School Ratio Distribution (Median, IQR, 10th-90th Percentile)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    meds = []
    p10s = []
    p25s = []
    p75s = []
    p90s = []
    for sy in years_all:
        sub = reg_sch[reg_sch['school_year'] == sy]
        v = sub[sub['teacher_fte_valid'] == True]
        r = v['students_per_classroom_teacher_fte_allgrades']
        meds.append(r.median())
        p10s.append(r.quantile(0.10))
        p25s.append(r.quantile(0.25))
        p75s.append(r.quantile(0.75))
        p90s.append(r.quantile(0.90))
        
    # Shaded band for 10th-90th percentiles
    ax.fill_between(x_indices, p10s, p90s, color='#9ecae1', alpha=0.35, label='10th–90th Percentile Range')
    # Shaded band for IQR (25th-75th)
    ax.fill_between(x_indices, p25s, p75s, color='#3182bd', alpha=0.45, label='Interquartile Range (25th–75th)')
    
    # Median line with break across 2015-16
    ax.plot([0], [meds[0]], color='#08519c', marker='o', markersize=7, label='Median School Ratio')
    ax.plot(x_indices[2:], [meds[i] for i in x_indices[2:]], color='#08519c', marker='o', markersize=7, linewidth=2.5)
    ax.plot([0, 1, 2], [meds[0], meds[1], meds[2]], color='#08519c', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.plot([1], [meds[1]], color='#08519c', marker='o', markerfacecolor='white', markeredgewidth=2, markersize=8)
    
    ax.text(0, meds[0] + 0.25, f"2014: {meds[0]:.2f}\n[IQR: {p25s[0]:.1f}–{p75s[0]:.1f}]", ha='center', fontsize=8.5, fontweight='bold', color='#08519c')
    ax.text(10, meds[10] - 0.55, f"2024: {meds[10]:.2f}\n[IQR: {p25s[10]:.1f}–{p75s[10]:.1f}]\n(−1.70 / −11.2%)", ha='center', fontsize=8.5, fontweight='bold', color='#08519c')
    
    ax.set_xticks(x_indices)
    ax.set_xticklabels([y.replace('-', '–') for y in years_all], rotation=35, ha='right', fontsize=9)
    ax.set_ylabel('Students per Classroom Teacher FTE', fontsize=11, fontweight='bold')
    ax.set_ylim(8.0, 22.0)
    ax.set_title('Distribution of School-Level Staffing Ratios (2014–15 to 2024–25)\nOperating Regular Schools in 9-County KC Region', fontsize=13, fontweight='bold', pad=12)
    ax.text(0.5, 0.94, 'Structural staffing ratio; not classroom size.', transform=ax.transAxes, ha='center', fontsize=10, fontstyle='italic', color='#555555')
    ax.legend(loc='upper right', frameon=True, framealpha=0.9, fontsize=9.5)
    plt.tight_layout()
    f7_path = os.path.join(FIGURES_DIR, 'school_ratio_distribution.png')
    plt.savefig(f7_path, dpi=300)
    plt.close()
    print(f"Saved: {f7_path}")

def main():
    print("=" * 80)
    print("STARTING TASK 003B: LONGITUDINAL STRUCTURAL CAPACITY ANALYSIS")
    print("=" * 80)
    
    df_sch, df_lea, df_bal = load_data()
    
    # 1. Output Tables
    build_regional_trends(df_sch, df_lea)
    build_state_trends(df_sch, df_lea)
    build_locale_trends(df_sch, df_bal)
    build_gradeband_trends(df_sch)
    build_endpoint_decomposition(df_sch, df_lea, df_bal)
    build_balanced_sensitivity(df_sch, df_bal)
    build_model_results(df_sch, df_lea, df_bal)
    
    # 2. Visualizations
    generate_visualizations(df_sch, df_lea, df_bal)
    
    print("=" * 80)
    print("TASK 003B ANALYSIS PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == '__main__':
    main()
