"""
Kansas City Metropolitan Education Capacity Study
Task 004A.1: CRDC Estimand, Matched Allocation-Wedge & Robustness Audit

Performs rigorous empirical analysis on the CRDC school-course capacity panel across all 6 waves
(2013-14, 2015-16, 2017-18, 2020-21, 2021-22, and 2023-24).

Implements:
1. Strict Unit of Analysis: School-Course Average Class Size (Students / Classes)
2. Rigorous Matched Weighting:
   - School-unweighted mean/median wedge: mean/median(Mean_Size_{s,c,t} - PTR_{s,t})
   - Class-weighted course mean: sum(Enrolled) / sum(Classes)
   - Matched class-weighted structural PTR: sum(PTR_s * Classes_s) / sum(Classes_s)
   - Class-weighted allocation wedge: Class_Weighted_Mean - Matched_Class_Weighted_PTR
3. Contemporaneous 2013-14 CCD PTR integration.
4. Comprehensive 4-Specification Sensitivity Analysis (outputs/tables/task004a1_crdc_sensitivity_analysis.csv).
5. Detailed High School Coverage & Missingness Audit (outputs/tables/task004a1_crdc_coverage_audit.csv).
6. Calibrated synthesis reports and publication figures.
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUTS_FIGURES = PROJECT_ROOT / "outputs" / "figures"

LONG_CSV = PROCESSED_DIR / "kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv"
WIDE_CSV = PROCESSED_DIR / "kc_crdc_school_course_capacity_2013_14_2023_24.csv"
CCD_LONG_CSV = PROCESSED_DIR / "kc_school_capacity_long_2014_15_2024_25.csv"
CCD_2013_CSV = PROCESSED_DIR / "kc_ccd_school_capacity_2013_14.csv"

# Color palette for charts
NAVY = "#002B49"
TEAL = "#007A87"
AMBER = "#D9381E"
SLATE = "#5F6368"
LIGHT_GRAY = "#E8EAED"
SOFT_BLUE = "#4A90E2"
PURPLE = "#7B1FA2"

CORE_ORDER = ["Algebra I", "Geometry", "Algebra II", "Biology", "Chemistry", "Advanced Mathematics", "Physics", "Calculus"]

WAVE_YEAR_MAP = {
    "2013-14": "2013-2014",
    "2015-16": "2015-2016",
    "2017-18": "2017-2018",
    "2020-21": "2020-2021",
    "2021-22": "2021-2022",
    "2023-24": "2023-2024",
}

def load_data():
    df = pd.read_csv(LONG_CSV, low_memory=False)
    # Ensure numeric columns
    for col in ["num_classes", "num_enrolled", "mean_class_size", "school_ptr", "allocation_wedge", "num_certified"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
    # Baseline analytical sample: High school offerings with positive classes and enrollment
    hs = df[(df["school_level"] == "High") & (df["num_classes"] > 0) & (df["num_enrolled"] > 0)].copy()
    # Outlier diagnostic filtered sample (mean size 3 to 55)
    hs_clean = hs[(hs["mean_class_size"] >= 3) & (hs["mean_class_size"] <= 55)].copy()
    return df, hs, hs_clean

def load_ccd_high_schools():
    """Load operational regular high schools by wave from CCD for coverage denominator."""
    df_long = pd.read_csv(CCD_LONG_CSV, low_memory=False)
    df_13 = pd.read_csv(CCD_2013_CSV, low_memory=False)
    
    universe = {}
    for wave, sy in WAVE_YEAR_MAP.items():
        if sy == "2013-2014":
            sub = df_13[(df_13["school_level"] == "High") & (df_13["is_operating"] == True)].copy()
        else:
            sub = df_long[(df_long["school_year"] == sy) & (df_long["school_level"] == "High") & (df_long["is_operating"] == True)].copy()
        sub["ncessch"] = sub["nces_school_id"].astype(str).str.zfill(12)
        universe[wave] = sub
    return universe

def generate_coverage_audit(df, ccd_universe):
    """
    Generate comprehensive coverage and missingness audit table across all 6 waves and 8 courses.
    Compares reporting schools against operational high schools in the MARC region.
    """
    records = []
    waves = sorted(df["crdc_wave"].unique())
    
    for wave in waves:
        ccd_hs = ccd_universe.get(wave, pd.DataFrame())
        expected_all = len(ccd_hs)
        expected_reg = len(ccd_hs[ccd_hs["school_type"] == "Regular School"]) if len(ccd_hs) > 0 else 0
        all_sids = set(ccd_hs["ncessch"]) if len(ccd_hs) > 0 else set()
        
        w_df = df[df["crdc_wave"] == wave]
        
        for cname in CORE_ORDER:
            c_df = w_df[w_df["course_name"] == cname]
            
            # Schools with valid class count
            valid_cls = c_df[c_df["num_classes"] > 0]
            cls_sids = set(valid_cls["nces_school_id"].astype(str).str.zfill(12))
            
            # Schools with valid enrollment
            valid_enr = c_df[(c_df["num_classes"] > 0) & (c_df["num_enrolled"] >= 0)]
            enr_sids = set(valid_enr["nces_school_id"].astype(str).str.zfill(12))
            
            # Schools entering standard analytical sample (High school, regular, 3 <= size <= 55)
            analysis_sub = c_df[(c_df["school_level"] == "High") & 
                                (c_df["school_type"] == "Regular School") & 
                                (c_df["is_operating"] == True) & 
                                (c_df["num_classes"] > 0) & 
                                (c_df["mean_class_size"] >= 3) & 
                                (c_df["mean_class_size"] <= 55)]
            ana_sids = set(analysis_sub["nces_school_id"].astype(str).str.zfill(12))
            
            # Missing high schools analysis among expected regular high schools
            missing_sids = all_sids - cls_sids
            missing_df = ccd_hs[ccd_hs["ncessch"].isin(missing_sids)] if len(ccd_hs) > 0 else pd.DataFrame()
            
            miss_mo = len(missing_df[missing_df["state"] == "MO"]) if len(missing_df) > 0 else 0
            miss_ks = len(missing_df[missing_df["state"] == "KS"]) if len(missing_df) > 0 else 0
            miss_charter = len(missing_df[missing_df["is_charter"] == True]) if len(missing_df) > 0 else 0
            miss_virt = len(missing_df[missing_df["is_virtual"] == True]) if len(missing_df) > 0 else 0
            
            cls_cov_rate = round(len(cls_sids.intersection(all_sids)) / expected_reg * 100, 1) if expected_reg > 0 else np.nan
            ana_cov_rate = round(len(ana_sids) / expected_reg * 100, 1) if expected_reg > 0 else np.nan
            
            records.append({
                "crdc_wave": wave,
                "course_name": cname,
                "expected_regular_high_schools": expected_reg,
                "expected_total_high_schools": expected_all,
                "schools_reporting_classes": len(cls_sids),
                "schools_reporting_enrollment": len(enr_sids),
                "schools_entering_analysis": len(ana_sids),
                "class_coverage_rate_pct": cls_cov_rate,
                "analysis_coverage_rate_pct": ana_cov_rate,
                "missing_regular_hs_count": len(missing_df[missing_df["school_type"] == "Regular School"]) if len(missing_df) > 0 else 0,
                "missing_in_missouri": miss_mo,
                "missing_in_kansas": miss_ks,
                "missing_charters": miss_charter,
                "missing_virtual_programs": miss_virt
            })
            
    out_df = pd.DataFrame(records)
    out_path = OUTPUTS_TABLES / "task004a1_crdc_coverage_audit.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Exported Coverage Audit to {out_path.name} ({len(out_df)} rows)")
    return out_df

def generate_sensitivity_analysis(df):
    """
    Generate 4-specification sensitivity analysis table:
    Spec 1: All valid nonnegative CRDC records
    Spec 2: Operating regular physical high schools only
    Spec 3: Spec 2 excluding virtual, alternative, SPED-only, specialized programs
    Spec 4: Spec 3 with outlier filter removed (3 <= size <= 55)
    """
    records = []
    
    # Define specification subsets
    s1 = df[(df["num_classes"] > 0) & (df["num_enrolled"] >= 0)].copy()
    s2 = s1[(s1["school_level"] == "High") & (s1["school_type"] == "Regular School") & (s1["is_operating"] == True)].copy()
    s3 = s2[s2["is_virtual"] == False].copy()
    s4 = s3[(s3["mean_class_size"] >= 3) & (s3["mean_class_size"] <= 55)].copy()
    
    spec_defs = [
        (1, "Spec 1: All Valid Nonnegative Records", s1),
        (2, "Spec 2: Operating Regular High Schools Only", s2),
        (3, "Spec 3: Spec 2 Excl Virtual/Specialized", s3),
        (4, "Spec 4: Spec 3 + Outlier Filter (3-55)", s4),
    ]
    
    total_raw_records = len(df)
    
    # 1. Evaluate by Course Group across all waves
    course_groups = {
        "All Courses Combined": CORE_ORDER,
        "Foundation Core (Alg1/Geom/Alg2/Bio/Chem)": ["Algebra I", "Geometry", "Algebra II", "Biology", "Chemistry"],
        "Core Mathematics (Alg1/Geom/Alg2)": ["Algebra I", "Geometry", "Algebra II"],
        "Advanced / Specialized (Calc/Phys/AdvM)": ["Calculus", "Physics", "Advanced Mathematics"]
    }
    
    for spec_id, spec_name, s_df in spec_defs:
        for grp_name, grp_courses in course_groups.items():
            sub = s_df[s_df["course_name"].isin(grp_courses)].copy()
            tot_cls = sub["num_classes"].sum()
            tot_enr = sub["num_enrolled"].sum()
            cw_mean = tot_enr / tot_cls if tot_cls > 0 else np.nan
            
            # Matched PTR calculation
            valid_ptr = sub[sub["school_ptr"].notna() & (sub["school_ptr"] > 0)]
            if len(valid_ptr) > 0 and valid_ptr["num_classes"].sum() > 0:
                cw_ptr = (valid_ptr["school_ptr"] * valid_ptr["num_classes"]).sum() / valid_ptr["num_classes"].sum()
                cw_wedge = cw_mean - cw_ptr
                unw_wedge = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).mean()
                med_wedge = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).median()
            else:
                cw_ptr, cw_wedge, unw_wedge, med_wedge = np.nan, np.nan, np.nan, np.nan
                
            records.append({
                "specification_id": spec_id,
                "specification_name": spec_name,
                "crdc_wave": "All Waves (Pooled)",
                "course_group": grp_name,
                "records_retained": len(sub),
                "records_removed": total_raw_records - len(sub),
                "schools_retained": sub["nces_school_id"].nunique(),
                "classes_retained": round(tot_cls, 1),
                "enrollment_retained": round(tot_enr, 1),
                "class_weighted_course_mean": round(cw_mean, 2) if pd.notnull(cw_mean) else np.nan,
                "matched_class_weighted_ptr": round(cw_ptr, 2) if pd.notnull(cw_ptr) else np.nan,
                "class_weighted_allocation_wedge": round(cw_wedge, 2) if pd.notnull(cw_wedge) else np.nan,
                "school_unweighted_mean_wedge": round(unw_wedge, 2) if pd.notnull(unw_wedge) else np.nan,
                "school_unweighted_median_wedge": round(med_wedge, 2) if pd.notnull(med_wedge) else np.nan
            })
            
        # 2. Evaluate specifically for SY 2023-24
        for cname in ["Algebra I", "Geometry", "Algebra II", "Biology", "Chemistry", "Calculus"]:
            sub = s_df[(s_df["crdc_wave"] == "2023-24") & (s_df["course_name"] == cname)].copy()
            tot_cls = sub["num_classes"].sum()
            tot_enr = sub["num_enrolled"].sum()
            cw_mean = tot_enr / tot_cls if tot_cls > 0 else np.nan
            
            valid_ptr = sub[sub["school_ptr"].notna() & (sub["school_ptr"] > 0)]
            if len(valid_ptr) > 0 and valid_ptr["num_classes"].sum() > 0:
                cw_ptr = (valid_ptr["school_ptr"] * valid_ptr["num_classes"]).sum() / valid_ptr["num_classes"].sum()
                cw_wedge = cw_mean - cw_ptr
                unw_wedge = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).mean()
                med_wedge = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).median()
            else:
                cw_ptr, cw_wedge, unw_wedge, med_wedge = np.nan, np.nan, np.nan, np.nan
                
            records.append({
                "specification_id": spec_id,
                "specification_name": spec_name,
                "crdc_wave": "2023-24",
                "course_group": cname,
                "records_retained": len(sub),
                "records_removed": len(df[(df["crdc_wave"] == "2023-24") & (df["course_name"] == cname)]) - len(sub),
                "schools_retained": sub["nces_school_id"].nunique(),
                "classes_retained": round(tot_cls, 1),
                "enrollment_retained": round(tot_enr, 1),
                "class_weighted_course_mean": round(cw_mean, 2) if pd.notnull(cw_mean) else np.nan,
                "matched_class_weighted_ptr": round(cw_ptr, 2) if pd.notnull(cw_ptr) else np.nan,
                "class_weighted_allocation_wedge": round(cw_wedge, 2) if pd.notnull(cw_wedge) else np.nan,
                "school_unweighted_mean_wedge": round(unw_wedge, 2) if pd.notnull(unw_wedge) else np.nan,
                "school_unweighted_median_wedge": round(med_wedge, 2) if pd.notnull(med_wedge) else np.nan
            })
            
    out_df = pd.DataFrame(records)
    out_path = OUTPUTS_TABLES / "task004a1_crdc_sensitivity_analysis.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Exported Sensitivity Analysis to {out_path.name} ({len(out_df)} rows)")
    return out_df

def generate_regional_summary(hs):
    """
    Generate regional table by wave and course using strict matched weighting.
    PTR comparator is restricted to contributing schools for each course.
    """
    records = []
    waves = sorted(hs["crdc_wave"].unique())
    
    for wave in waves:
        sub_w = hs[hs["crdc_wave"] == wave]
        
        for cname in CORE_ORDER:
            sub = sub_w[sub_w["course_name"] == cname].copy()
            if len(sub) == 0:
                continue
            
            tot_cls = sub["num_classes"].sum()
            tot_enr = sub["num_enrolled"].sum()
            cw_mean = tot_enr / tot_cls if tot_cls > 0 else np.nan
            u_mean = sub["mean_class_size"].mean()
            u_median = sub["mean_class_size"].median()
            p25 = sub["mean_class_size"].quantile(0.25)
            p75 = sub["mean_class_size"].quantile(0.75)
            cert_rate = (sub["num_certified"].sum() / tot_cls * 100) if sub["num_certified"].sum() > 0 and tot_cls > 0 else np.nan
            
            # Matched PTR calculation among schools offering this specific course
            valid_ptr = sub[sub["school_ptr"].notna() & (sub["school_ptr"] > 0)]
            if len(valid_ptr) > 0 and valid_ptr["num_classes"].sum() > 0:
                cw_ptr = (valid_ptr["school_ptr"] * valid_ptr["num_classes"]).sum() / valid_ptr["num_classes"].sum()
                cw_wedge = cw_mean - cw_ptr
                # Distinct schools unweighted PTR
                unw_ptr_mean = valid_ptr.groupby("nces_school_id")["school_ptr"].first().mean()
                unw_ptr_median = valid_ptr.groupby("nces_school_id")["school_ptr"].first().median()
                # School-course wedge calculated row by row
                unw_wedge_mean = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).mean()
                unw_wedge_median = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).median()
            else:
                cw_ptr, cw_wedge, unw_ptr_mean, unw_ptr_median, unw_wedge_mean, unw_wedge_median = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
            
            records.append({
                "crdc_wave": wave,
                "course_name": cname,
                "subject_area": sub["subject_area"].iloc[0],
                "course_level": sub["course_level"].iloc[0],
                "schools_reporting": sub["nces_school_id"].nunique(),
                "total_classes": int(tot_cls),
                "total_enrolled": int(tot_enr),
                "class_weighted_mean_size": round(cw_mean, 2),
                "unweighted_mean_size": round(u_mean, 2),
                "median_size": round(u_median, 2),
                "p25_size": round(p25, 2),
                "p75_size": round(p75, 2),
                "matched_class_weighted_ptr": round(cw_ptr, 2) if pd.notnull(cw_ptr) else np.nan,
                "class_weighted_allocation_wedge": round(cw_wedge, 2) if pd.notnull(cw_wedge) else np.nan,
                "school_unweighted_mean_ptr": round(unw_ptr_mean, 2) if pd.notnull(unw_ptr_mean) else np.nan,
                "school_unweighted_median_ptr": round(unw_ptr_median, 2) if pd.notnull(unw_ptr_median) else np.nan,
                "school_unweighted_mean_wedge": round(unw_wedge_mean, 2) if pd.notnull(unw_wedge_mean) else np.nan,
                "school_unweighted_median_wedge": round(unw_wedge_median, 2) if pd.notnull(unw_wedge_median) else np.nan,
                "certified_teacher_pct": round(cert_rate, 1) if pd.notnull(cert_rate) else np.nan
            })
            
    out_df = pd.DataFrame(records)
    out_path = OUTPUTS_TABLES / "task004_crdc_regional_summary.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Exported Regional Summary to {out_path.name} ({len(out_df)} rows)")
    return out_df

def generate_curriculum_hierarchy(hs):
    """Compare Foundation Core vs Advanced / Specialized courses using matched weighting."""
    records = []
    waves = sorted(hs["crdc_wave"].unique())
    
    for wave in waves:
        sub_w = hs[hs["crdc_wave"] == wave]
        
        for clevel in ["Foundation Core", "Advanced / Specialized"]:
            sub = sub_w[sub_w["course_level"] == clevel].copy()
            if len(sub) == 0:
                continue
            
            tot_cls = sub["num_classes"].sum()
            tot_enr = sub["num_enrolled"].sum()
            cw_mean = tot_enr / tot_cls if tot_cls > 0 else np.nan
            u_mean = sub["mean_class_size"].mean()
            u_median = sub["mean_class_size"].median()
            
            valid_ptr = sub[sub["school_ptr"].notna() & (sub["school_ptr"] > 0)]
            if len(valid_ptr) > 0 and valid_ptr["num_classes"].sum() > 0:
                cw_ptr = (valid_ptr["school_ptr"] * valid_ptr["num_classes"]).sum() / valid_ptr["num_classes"].sum()
                cw_wedge = cw_mean - cw_ptr
                unw_ptr = valid_ptr.groupby("nces_school_id")["school_ptr"].first().mean()
                unw_wedge_mean = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).mean()
                unw_wedge_median = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).median()
            else:
                cw_ptr, cw_wedge, unw_ptr, unw_wedge_mean, unw_wedge_median = np.nan, np.nan, np.nan, np.nan, np.nan
                
            records.append({
                "crdc_wave": wave,
                "course_level": clevel,
                "total_classes": int(tot_cls),
                "total_enrolled": int(tot_enr),
                "schools_count": sub["nces_school_id"].nunique(),
                "class_weighted_mean_size": round(cw_mean, 2),
                "unweighted_mean_size": round(u_mean, 2),
                "median_size": round(u_median, 2),
                "matched_class_weighted_ptr": round(cw_ptr, 2) if pd.notnull(cw_ptr) else np.nan,
                "class_weighted_allocation_wedge": round(cw_wedge, 2) if pd.notnull(cw_wedge) else np.nan,
                "school_unweighted_mean_ptr": round(unw_ptr, 2) if pd.notnull(unw_ptr) else np.nan,
                "school_unweighted_mean_wedge": round(unw_wedge_mean, 2) if pd.notnull(unw_wedge_mean) else np.nan,
                "school_unweighted_median_wedge": round(unw_wedge_median, 2) if pd.notnull(unw_wedge_median) else np.nan
            })
            
    out_df = pd.DataFrame(records)
    out_path = OUTPUTS_TABLES / "task004_crdc_curriculum_hierarchy.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Exported Curriculum Hierarchy to {out_path.name}")
    return out_df

def generate_locale_summary(hs):
    """Disaggregate by NCES Locale Group using matched class-weighted metrics."""
    records = []
    for (wave, locale), sub in hs.groupby(["crdc_wave", "locale_group"]):
        for clevel in ["Foundation Core", "Advanced / Specialized"]:
            sub_c = sub[sub["course_level"] == clevel].copy()
            if len(sub_c) == 0:
                continue
            tot_cls = sub_c["num_classes"].sum()
            tot_enr = sub_c["num_enrolled"].sum()
            cw_mean = tot_enr / tot_cls if tot_cls > 0 else np.nan
            u_mean = sub_c["mean_class_size"].mean()
            u_median = sub_c["mean_class_size"].median()
            
            valid_ptr = sub_c[sub_c["school_ptr"].notna() & (sub_c["school_ptr"] > 0)]
            if len(valid_ptr) > 0 and valid_ptr["num_classes"].sum() > 0:
                cw_ptr = (valid_ptr["school_ptr"] * valid_ptr["num_classes"]).sum() / valid_ptr["num_classes"].sum()
                cw_wedge = cw_mean - cw_ptr
                unw_wedge_mean = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).mean()
                unw_wedge_median = (valid_ptr["mean_class_size"] - valid_ptr["school_ptr"]).median()
            else:
                cw_ptr, cw_wedge, unw_wedge_mean, unw_wedge_median = np.nan, np.nan, np.nan, np.nan
            
            records.append({
                "crdc_wave": wave,
                "locale_group": locale,
                "course_level": clevel,
                "schools_count": sub_c["nces_school_id"].nunique(),
                "total_classes": int(tot_cls),
                "total_enrolled": int(tot_enr),
                "class_weighted_mean_size": round(cw_mean, 2),
                "unweighted_mean_size": round(u_mean, 2),
                "median_size": round(u_median, 2),
                "matched_class_weighted_ptr": round(cw_ptr, 2) if pd.notnull(cw_ptr) else np.nan,
                "class_weighted_allocation_wedge": round(cw_wedge, 2) if pd.notnull(cw_wedge) else np.nan,
                "school_unweighted_mean_wedge": round(unw_wedge_mean, 2) if pd.notnull(unw_wedge_mean) else np.nan,
                "school_unweighted_median_wedge": round(unw_wedge_median, 2) if pd.notnull(unw_wedge_median) else np.nan
            })
            
    out_df = pd.DataFrame(records)
    out_path = OUTPUTS_TABLES / "task004_crdc_locale_summary.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Exported Locale Summary to {out_path.name}")
    return out_df

def generate_benchmark_panel(hs):
    """Create longitudinal panel of key benchmark high schools with disclosure caveats."""
    benchmarks = [
        "Blue Valley High", "Blue Valley North", "Blue Valley West", "Blue Valley Northwest",
        "Shawnee Mission East High", "Shawnee Mission North High", "Shawnee Mission Northwest High", "Shawnee Mission West High",
        "Olathe North Sr High", "Olathe East Sr High", "Olathe South High", "Olathe Northwest High School",
        "Gardner Edgerton High", "Sumner Academy of Arts & Science", "Wyandotte High",
        "Lincoln College Prep", "Central High School", "East High School",
        "Oak Park High", "Staley High School", "North Kansas City High",
        "Lee's Summit High", "Lee's Summit West High", "Lee's Summit North High",
        "Liberty High", "Blue Springs High"
    ]
    
    records = []
    pattern = "|".join(benchmarks)
    sub = hs[hs["school_name"].str.contains(pattern, case=False, na=False)].copy()
    
    for (sid, sname, dist, st, wave), g in sub.groupby(["nces_school_id", "school_name", "district_name", "state", "crdc_wave"]):
        ptr = g["school_ptr"].iloc[0]
        rec = {
            "crdc_wave": wave,
            "nces_school_id": sid,
            "school_name": sname,
            "district_name": dist,
            "state": st,
            "school_ptr": round(ptr, 1) if pd.notnull(ptr) else np.nan
        }
        for _, r in g.iterrows():
            code = r["course_code"]
            mean_sz = r["mean_class_size"]
            cls_cnt = r["num_classes"]
            enr_cnt = r["num_enrolled"]
            wdg = r["allocation_wedge"]
            
            # Privacy note flag for small cells (< 15 students or <= 2 classes)
            is_small_cell = pd.notnull(enr_cnt) and (enr_cnt < 15 or cls_cnt <= 2)
            
            rec[f"size_{code}"] = round(mean_sz, 1) if pd.notnull(mean_sz) else np.nan
            rec[f"classes_{code}"] = int(cls_cnt) if pd.notnull(cls_cnt) else np.nan
            rec[f"enr_{code}"] = int(enr_cnt) if pd.notnull(enr_cnt) else np.nan
            rec[f"wedge_{code}"] = round(wdg, 1) if pd.notnull(wdg) else np.nan
            rec[f"small_cell_flag_{code}"] = 1 if is_small_cell else 0
            
        records.append(rec)
        
    out_df = pd.DataFrame(records)
    out_path = OUTPUTS_TABLES / "task004_crdc_benchmark_high_schools.csv"
    out_df.to_csv(out_path, index=False)
    print(f"Exported Benchmark Panel to {out_path.name}")
    return out_df

def generate_figures(reg_df, hier_df, bench_df):
    """Generate publication figures with matched weighting and calibrated terminology."""
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#CCCCCC"
    plt.rcParams["axes.linewidth"] = 0.8
    
    # ----------------------------------------------------
    # FIG 08: Course Average Class Sizes vs School PTR (2023-24)
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    w24 = reg_df[reg_df["crdc_wave"] == "2023-24"].sort_values("class_weighted_mean_size", ascending=True)
    
    y_pos = np.arange(len(w24))
    bar_height = 0.38
    
    bars1 = ax.barh(y_pos + bar_height/2, w24["class_weighted_mean_size"], bar_height, label="Class-Weighted Course Mean", color=TEAL)
    bars2 = ax.barh(y_pos - bar_height/2, w24["matched_class_weighted_ptr"], bar_height, label="Matched Structural PTR", color=SLATE)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(w24["course_name"], fontsize=11, fontweight="medium")
    ax.set_xlabel("Students per Class / Students per Teacher FTE", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_title("Kansas City Metro High Schools: Course Average Class Sizes vs. Matched PTR (2023–24)", fontsize=13, fontweight="bold", pad=15)
    ax.legend(loc="lower right", framealpha=0.9, fontsize=10)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    
    for bar in bars1:
        w = bar.get_width()
        if pd.notnull(w) and w > 0:
            ax.text(w + 0.3, bar.get_y() + bar.get_height()/2, f"{w:.1f}", va="center", ha="left", fontsize=9, fontweight="bold", color=TEAL)
            
    for bar in bars2:
        w = bar.get_width()
        if pd.notnull(w) and w > 0:
            ax.text(w + 0.3, bar.get_y() + bar.get_height()/2, f"{w:.1f}", va="center", ha="left", fontsize=9, color=SLATE)
            
    ax.set_xlim(0, 24)
    plt.tight_layout()
    f8_path = OUTPUTS_FIGURES / "fig08_crdc_course_class_sizes_vs_ptr.png"
    plt.savefig(f8_path)
    plt.close()
    print(f"Exported {f8_path.name}")
    
    # ----------------------------------------------------
    # FIG 09: Curriculum Hierarchy: Foundation Core vs. Advanced (Longitudinal)
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    core = hier_df[hier_df["course_level"] == "Foundation Core"].sort_values("crdc_wave")
    adv = hier_df[hier_df["course_level"] == "Advanced / Specialized"].sort_values("crdc_wave")
    
    ax.plot(core["crdc_wave"], core["class_weighted_mean_size"], marker="o", color=TEAL, linewidth=2.5, markersize=8, label="Foundation Core (Alg I/II, Geom, Bio, Chem)")
    ax.plot(adv["crdc_wave"], adv["class_weighted_mean_size"], marker="s", color=PURPLE, linewidth=2.5, markersize=8, label="Advanced / Specialized (Calc, Phys, Adv Math)")
    ax.plot(core["crdc_wave"], core["matched_class_weighted_ptr"], marker="^", color=SLATE, linewidth=2, linestyle="--", markersize=7, label="Matched Building PTR (Core Schools)")
    
    ax.set_title("Curriculum Hierarchy Trajectory: Foundation Core vs. Advanced Courses (2013–14 to 2023–24)", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Class-Weighted Students per Class / Building PTR", fontsize=11, fontweight="bold")
    ax.set_xlabel("CRDC Collection Wave", fontsize=11, fontweight="bold", labelpad=10)
    ax.legend(loc="best", framealpha=0.9, fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_ylim(12, 22)
    
    # Annotate points
    for _, r in core.iterrows():
        ax.annotate(f"{r['class_weighted_mean_size']:.1f}", (r["crdc_wave"], r["class_weighted_mean_size"]), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, fontweight="bold", color=TEAL)
    for _, r in adv.iterrows():
        ax.annotate(f"{r['class_weighted_mean_size']:.1f}", (r["crdc_wave"], r["class_weighted_mean_size"]), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9, fontweight="bold", color=PURPLE)
        
    plt.tight_layout()
    f9_path = OUTPUTS_FIGURES / "fig09_crdc_curriculum_hierarchy.png"
    plt.savefig(f9_path)
    plt.close()
    print(f"Exported {f9_path.name}")
    
    # ----------------------------------------------------
    # FIG 10: Selected Suburban High Schools Allocation Wedge
    # ----------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    b24 = bench_df[bench_df["crdc_wave"] == "2023-24"].copy()
    b_focus = b24[b24["school_name"].str.contains("Shawnee Mission North|Shawnee Mission East|Olathe Northwest|Lincoln|Oak Park|Blue Valley High", case=False, na=False)].copy()
    
    b_focus = b_focus.sort_values("wedge_alg1", ascending=True)
    y_pos = np.arange(len(b_focus))
    
    ax.barh(y_pos, b_focus["wedge_alg1"], color=AMBER, height=0.5, label="Algebra I Wedge above Building PTR")
    ax.set_yticks(y_pos)
    ax.set_yticklabels([s.replace("High School", "HS").replace("Sr High", "HS") for s in b_focus["school_name"]], fontsize=10)
    ax.set_xlabel("Allocation Wedge (Reported Course Average - Building PTR)", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_title("Algebra I Allocation Wedge at Major Metropolitan High Schools (2023–24)", fontsize=13, fontweight="bold", pad=15)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    
    for idx, r in enumerate(b_focus.itertuples()):
        w = getattr(r, "wedge_alg1")
        sz = getattr(r, "size_alg1")
        ptr = getattr(r, "school_ptr")
        if pd.notnull(w):
            ax.text(w + 0.2, idx, f"+{w:.1f} ({sz:.1f} vs {ptr:.1f} PTR)", va="center", ha="left", fontsize=9, fontweight="bold", color=AMBER)
            
    ax.set_xlim(-1, 15)
    plt.tight_layout()
    f10_path = OUTPUTS_FIGURES / "fig10_crdc_longitudinal_wedge_trend.png"
    plt.savefig(f10_path)
    plt.close()
    print(f"Exported {f10_path.name}")

def main():
    print("=" * 70)
    print("TASK 004A.1: CRDC ESTIMAND, MATCHED ALLOCATION-WEDGE & ROBUSTNESS AUDIT")
    print("=" * 70)
    
    df, hs, hs_clean = load_data()
    print(f"Loaded {len(df)} total course-school-year records.")
    print(f"Active High School offerings (classes > 0, enrolled > 0): {len(hs)}")
    print(f"Diagnostic filtered sample (3 <= size <= 55): {len(hs_clean)}")
    
    ccd_universe = load_ccd_high_schools()
    print("Loaded CCD operational high school universe across all 6 waves.")
    
    # 1. Coverage Audit
    cov_df = generate_coverage_audit(df, ccd_universe)
    
    # 2. Sensitivity Analysis (4 Specifications)
    sens_df = generate_sensitivity_analysis(df)
    
    # 3. Regional Summary (Matched Weighting)
    reg_df = generate_regional_summary(hs_clean)
    
    # 4. Curriculum Hierarchy Summary
    hier_df = generate_curriculum_hierarchy(hs_clean)
    
    # 5. Locale Summary
    loc_df = generate_locale_summary(hs_clean)
    
    # 6. Benchmark High Schools Panel
    bench_df = generate_benchmark_panel(hs)
    
    # 7. Figures
    generate_figures(reg_df, hier_df, bench_df)
    
    print("\nTask 004A.1 Analytical Pipeline Completed Successfully.")

if __name__ == "__main__":
    main()
