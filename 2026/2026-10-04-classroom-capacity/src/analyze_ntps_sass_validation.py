"""
src/analyze_ntps_sass_validation.py
Phase 5: SASS / NTPS Series Validation & Comparative Methodology Audit

Performs empirical cross-validation between:
  1. Administrative Census Data (CRDC derived school-course averages & CCD staffing ratios)
  2. Teacher-Reported Survey Data (NCES SASS & NTPS probability sample surveys)

Key Analysis Streams:
  - Long-Run Longitudinal Trajectory (1999-2000 through 2020-21)
  - Methodological Estimand Crosswalk: Macro PTR vs. CRDC Unweighted vs. CRDC Student-Weighted vs. NTPS Teacher-Reported
  - National 50-State Distribution (2020-21 NTPS) and State Case Study (US vs. MO vs. KS)
  - Secondary Schedule Waterfall & Jenkins Remedial Ceiling Benchmark (<= 125 students/day)
  - Teacher-Level Individual Instructional Load Exposure (IEP, Section 504, and EL counts)

Outputs:
  - artifacts/tables/table_c01_sass_ntps_longitudinal_series.csv
  - artifacts/tables/table_c02_crdc_vs_ntps_crosswalk.csv
  - artifacts/tables/table_c03_ntps_2020_21_state_distribution.csv
  - artifacts/tables/table_c04_teacher_schedule_roster_loads.csv
  - artifacts/tables/table_c05_teacher_iep_el_exposure.csv
  - artifacts/figures/fig_c01_sass_ntps_longitudinal_trajectory.png
  - artifacts/figures/fig_c02_crdc_vs_ntps_comparison.png
  - artifacts/figures/fig_c03_ntps_state_distribution.png
  - artifacts/figures/fig_c04_schedule_regime_roster_load.png
  (And copies figures to Brain artifact directory for user-facing viewing)
"""

import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "artifacts")
TABLES_DIR = os.path.join(ARTIFACTS_DIR, "tables")
FIGURES_DIR = os.path.join(ARTIFACTS_DIR, "figures")
BRAIN_DIR = r"C:\Users\admir\.gemini\antigravity\brain\873b7f0f-08cb-453c-b3e0-5a0024dac318"

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


def copy_to_brain(filename):
    """Copy an artifact file to the Brain directory if available."""
    src = os.path.join(FIGURES_DIR, filename)
    if os.path.exists(src) and os.path.exists(BRAIN_DIR):
        dst = os.path.join(BRAIN_DIR, filename)
        shutil.copy2(src, dst)
        print(f"Copied {filename} to Brain artifact directory.")


def run_sass_ntps_analysis():
    print("=== Running Phase 5: SASS / NTPS Series Validation ===")
    
    # -------------------------------------------------------------
    # 1. Load Processed Datasets
    # -------------------------------------------------------------
    canonical_series_path = os.path.join(PROCESSED_DIR, "ntps_sass_class_size_series.csv")
    ntps_state_path = os.path.join(PROCESSED_DIR, "ntps_2020_21_state_class_size.csv")
    sass_panel_path = os.path.join(PROCESSED_DIR, "sass_state_historical_panel.csv")
    crdc_summary_path = os.path.join(PROCESSED_DIR, "crdc_national_summary.csv")
    
    df_series = pd.read_csv(canonical_series_path)
    df_ntps_state = pd.read_csv(ntps_state_path)
    df_sass_panel = pd.read_csv(sass_panel_path)
    df_crdc = pd.read_csv(crdc_summary_path)
    
    print(f"Loaded canonical series ({len(df_series)} records)")
    print(f"Loaded NTPS state panel ({len(df_ntps_state)} jurisdictions)")
    print(f"Loaded SASS historical panel ({len(df_sass_panel)} records)")
    print(f"Loaded CRDC national summary ({len(df_crdc)} records)")

    # -------------------------------------------------------------
    # 2. Table C01: SASS/NTPS Longitudinal Series
    # -------------------------------------------------------------
    # Filter to primary measured survey statistics for US, MO, KS
    c01_records = []
    
    # SASS Waves: 1999-2000, 2003-04, 2007-08, 2011-12
    for year_label in ["1999-2000", "2003-04", "2007-08", "2011-12"]:
        sub_sass = df_sass_panel[df_sass_panel["school_year"] == year_label]
        for geo in ["United States", "Missouri", "Kansas"]:
            row = sub_sass[sub_sass["state"] == geo].iloc[0]
            # Elementary Self-Contained
            c01_records.append({
                "survey_cycle": f"{year_label} (SASS)",
                "school_year": year_label,
                "geography": geo,
                "school_level": "Elementary School",
                "instructional_type": "Self-Contained",
                "class_size_mean": round(row["elem_mean"], 1),
                "class_size_se": round(row["elem_se"], 2) if pd.notna(row["elem_se"]) else np.nan,
                "reporting_flag": row["elem_flag"] if pd.notna(row["elem_flag"]) else "",
                "estimand_scope": "Grades K-5/6 Self-Contained",
                "source_reference": row["source_table"]
            })
            # Secondary Departmentalized (Grades 7-12)
            c01_records.append({
                "survey_cycle": f"{year_label} (SASS)",
                "school_year": year_label,
                "geography": geo,
                "school_level": "Secondary / Grades 7-12",
                "instructional_type": "Departmentalized",
                "class_size_mean": round(row["sec_mean"], 1),
                "class_size_se": round(row["sec_se"], 2) if pd.notna(row["sec_se"]) else np.nan,
                "reporting_flag": row["sec_flag"] if pd.notna(row["sec_flag"]) else "",
                "estimand_scope": "Grades 7-12 Departmentalized Instruction",
                "source_reference": row["source_table"]
            })

    # High School 9-12 Departmentalized Series: 2011-12, 2015-16, 2017-18, 2020-21
    hs_dept_published = [
        {"survey_cycle": "2011-12 (SASS)", "school_year": "2011-12", "geography": "United States", "mean": 24.2, "se": np.nan, "flag": "", "source": "NCES SASS 2011-12 First Look Table 7"},
        {"survey_cycle": "2011-12 (SASS)", "school_year": "2011-12", "geography": "Missouri", "mean": 21.8, "se": np.nan, "flag": "", "source": "NCES SASS 2011-12 First Look Table 7"},
        {"survey_cycle": "2011-12 (SASS)", "school_year": "2011-12", "geography": "Kansas", "mean": 19.7, "se": np.nan, "flag": "", "source": "NCES SASS 2011-12 First Look Table 7"},
        {"survey_cycle": "2015-16 (NTPS)", "school_year": "2015-16", "geography": "United States", "mean": 26.0, "se": np.nan, "flag": "", "source": "NCES NTPS 2015-16 First Look Table 8"},
        {"survey_cycle": "2017-18 (NTPS)", "school_year": "2017-18", "geography": "United States", "mean": 23.3, "se": np.nan, "flag": "", "source": "NCES NTPS 2017-18 Table A-7a"},
        {"survey_cycle": "2017-18 (NTPS)", "school_year": "2017-18", "geography": "Missouri", "mean": 22.5, "se": np.nan, "flag": "", "source": "NCES NTPS 2017-18 Table A-7a"},
        {"survey_cycle": "2017-18 (NTPS)", "school_year": "2017-18", "geography": "Kansas", "mean": 19.8, "se": np.nan, "flag": "", "source": "NCES NTPS 2017-18 Table A-7a"},
        {"survey_cycle": "2020-21 (NTPS)", "school_year": "2020-21", "geography": "United States", "mean": 21.0, "se": np.nan, "flag": "", "source": "NCES NTPS 2020-21 Table 7"},
        {"survey_cycle": "2020-21 (NTPS)", "school_year": "2020-21", "geography": "Missouri", "mean": 19.2, "se": np.nan, "flag": "", "source": "NCES NTPS 2020-21 Table 7"},
        {"survey_cycle": "2020-21 (NTPS)", "school_year": "2020-21", "geography": "Kansas", "mean": 17.4, "se": np.nan, "flag": "", "source": "NCES NTPS 2020-21 Table 7"},
    ]
    for r in hs_dept_published:
        c01_records.append({
            "survey_cycle": r["survey_cycle"],
            "school_year": r["school_year"],
            "geography": r["geography"],
            "school_level": "High School",
            "instructional_type": "Departmentalized",
            "class_size_mean": r["mean"],
            "class_size_se": r["se"],
            "reporting_flag": r["flag"],
            "estimand_scope": "Grades 9-12 Departmentalized Instruction",
            "source_reference": r["source"]
        })
        
    # NTPS 2020-21 Middle and Elementary
    for geo in ["United States", "Missouri", "Kansas"]:
        sub_21 = df_ntps_state[df_ntps_state["state"] == geo].iloc[0]
        # Middle School Departmentalized
        c01_records.append({
            "survey_cycle": "2020-21 (NTPS)",
            "school_year": "2020-21",
            "geography": geo,
            "school_level": "Middle School",
            "instructional_type": "Departmentalized",
            "class_size_mean": round(sub_21["middle_departmentalized"], 1),
            "class_size_se": np.nan,
            "reporting_flag": sub_21["middle_departmentalized_flag"] if pd.notna(sub_21["middle_departmentalized_flag"]) else "",
            "estimand_scope": "Grades 5/6-8 Departmentalized Instruction",
            "source_reference": "NCES NTPS 2020-21 Table 7"
        })
        # Elementary School Self-Contained
        c01_records.append({
            "survey_cycle": "2020-21 (NTPS)",
            "school_year": "2020-21",
            "geography": geo,
            "school_level": "Elementary School",
            "instructional_type": "Self-Contained",
            "class_size_mean": round(sub_21["elem_self_contained"], 1),
            "class_size_se": np.nan,
            "reporting_flag": sub_21["elem_self_contained_flag"] if pd.notna(sub_21["elem_self_contained_flag"]) else "",
            "estimand_scope": "Grades K-5/6 Self-Contained",
            "source_reference": "NCES NTPS 2020-21 Table 7"
        })

    df_c01 = pd.DataFrame(c01_records)
    c01_path = os.path.join(TABLES_DIR, "table_c01_sass_ntps_longitudinal_series.csv")
    df_c01.to_csv(c01_path, index=False)
    print(f"Saved Table C01 -> {c01_path} ({len(df_c01)} rows)")

    # -------------------------------------------------------------
    # 3. Table C02: CRDC vs. NTPS Methodological Estimand Crosswalk
    # -------------------------------------------------------------
    # Restores frozen Study A estimand nomenclature:
    #   - Estimand A: CRDC Unweighted School-Course Cell Mean (secondary core courses)
    #   - Estimand B: CRDC Section-Weighted Mean (secondary core courses)
    #   - Estimand C: CRDC Enrollment-Weighted Lower-Bound Proxy (secondary core courses)
    #   - CCD Macro PTR: Universal Staffing Ratio (Digest Table 208.20)
    #   - NTPS Teacher Survey: Departmentalized High School Class Size (and Elem Self-Contained)
    
    crdc_waves = ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"]
    crosswalk_rows = []
    
    ccd_macro_ptrs = {
        "2013-14": 16.1,
        "2015-16": 16.1,
        "2017-18": 16.0,
        "2020-21": 15.4,
        "2021-22": 15.4,
        "2023-24": 15.3
    }
    
    ntps_hs_published = {
        "2013-14": np.nan, # No NTPS collection
        "2015-16": 26.0,
        "2017-18": 23.3,
        "2020-21": 21.0,
        "2021-22": np.nan,
        "2023-24": np.nan
    }
    
    ntps_elem_published = {
        "2013-14": np.nan,
        "2015-16": np.nan,
        "2017-18": np.nan,
        "2020-21": 19.1,
        "2021-22": np.nan,
        "2023-24": np.nan
    }

    for w in crdc_waves:
        # Core high school courses (excluding middle-school-spanning Algebra 1/Geometry)
        sub_core = df_crdc[(df_crdc["wave"] == w) & (df_crdc["course_code"].isin(["alg2", "bio", "chem"]))]
        tot_students = sub_core["students_enrolled"].sum()
        tot_classes = sub_core["classes_total"].sum()
        
        # Estimand A: Unweighted average of cell means across the 3 core courses
        a_cell_mean = sub_core["course_cell_mean"].mean()
        # Estimand B: Section-weighted mean
        b_sec_mean = (sub_core["section_weighted_mean"] * sub_core["classes_total"]).sum() / tot_classes
        # Estimand C: Student/seat-weighted lower-bound proxy
        c_seat_mean = (sub_core["seat_weighted_mean"] * sub_core["students_enrolled"]).sum() / tot_students
        
        ptr = ccd_macro_ptrs.get(w, np.nan)
        d_ntps_hs = ntps_hs_published.get(w, np.nan)
        e_ntps_elem = ntps_elem_published.get(w, np.nan)
        
        c_minus_a = c_seat_mean - a_cell_mean
        c_minus_b = c_seat_mean - b_sec_mean
        c_minus_ptr = c_seat_mean - ptr if pd.notna(ptr) else np.nan
        ntps_minus_c = d_ntps_hs - c_seat_mean if pd.notna(d_ntps_hs) else np.nan
        ntps_minus_ptr = d_ntps_hs - ptr if (pd.notna(d_ntps_hs) and pd.notna(ptr)) else np.nan
        
        crosswalk_rows.append({
            "school_year": w,
            "crdc_wave": w,
            "ccd_macro_ptr": ptr,
            "crdc_unweighted_cell_mean": round(a_cell_mean, 2),
            "crdc_section_weighted_mean": round(b_sec_mean, 2),
            "crdc_student_weighted_mean": round(c_seat_mean, 2),
            "ntps_teacher_hs_dept": d_ntps_hs,
            "ntps_teacher_elem_self": e_ntps_elem,
            "gap_c_minus_a": round(c_minus_a, 2),
            "weighting_gap_c_minus_b": round(c_minus_b, 2),
            "ptr_wedge_c_minus_ptr": round(c_minus_ptr, 2) if pd.notna(c_minus_ptr) else np.nan,
            "survey_crdc_gap_ntps_minus_c": round(ntps_minus_c, 2) if pd.notna(ntps_minus_c) else np.nan,
            "survey_ptr_gap_ntps_minus_ptr": round(ntps_minus_ptr, 2) if pd.notna(ntps_minus_ptr) else np.nan,
        })
        
    df_c02 = pd.DataFrame(crosswalk_rows)
    c02_path = os.path.join(TABLES_DIR, "table_c02_crdc_vs_ntps_crosswalk.csv")
    df_c02.to_csv(c02_path, index=False)
    print(f"Saved Table C02 -> {c02_path} ({len(df_c02)} rows)")

    # -------------------------------------------------------------
    # 4. Table C03: NTPS 2020-21 State Distribution Summary
    # -------------------------------------------------------------
    df_states_only = df_ntps_state[df_ntps_state["state"] != "United States"].copy()
    
    sec_series = df_states_only["sec_high_departmentalized"].dropna()
    mid_series = df_states_only["middle_departmentalized"].dropna()
    elem_series = df_states_only["elem_self_contained"].dropna()
    
    mo_row = df_ntps_state[df_ntps_state["state"] == "Missouri"].iloc[0]
    ks_row = df_ntps_state[df_ntps_state["state"] == "Kansas"].iloc[0]
    us_row = df_ntps_state[df_ntps_state["state"] == "United States"].iloc[0]
    
    # Calculate state rank (1 = highest class size, 51 = lowest class size)
    df_states_only["sec_rank"] = df_states_only["sec_high_departmentalized"].rank(ascending=False, method="min")
    mo_rank = int(df_states_only[df_states_only["state"] == "Missouri"]["sec_rank"].values[0])
    ks_rank = int(df_states_only[df_states_only["state"] == "Kansas"]["sec_rank"].values[0])
    
    c03_stats = [
        {
            "metric": "National Benchmark (Verbatim NCES)",
            "sec_high_departmentalized": us_row["sec_high_departmentalized"],
            "middle_departmentalized": us_row["middle_departmentalized"],
            "elem_self_contained": us_row["elem_self_contained"],
            "notes": "Published national population statistic"
        },
        {
            "metric": "50-State + DC Mean",
            "sec_high_departmentalized": round(sec_series.mean(), 2),
            "middle_departmentalized": round(mid_series.mean(), 2),
            "elem_self_contained": round(elem_series.mean(), 2),
            "notes": "Unweighted mean across state entities"
        },
        {
            "metric": "50-State + DC Median",
            "sec_high_departmentalized": round(sec_series.median(), 2),
            "middle_departmentalized": round(mid_series.median(), 2),
            "elem_self_contained": round(elem_series.median(), 2),
            "notes": "50th percentile among states"
        },
        {
            "metric": "25th Percentile (P25)",
            "sec_high_departmentalized": round(sec_series.quantile(0.25), 2),
            "middle_departmentalized": round(mid_series.quantile(0.25), 2),
            "elem_self_contained": round(elem_series.quantile(0.25), 2),
            "notes": "Lower quartile threshold"
        },
        {
            "metric": "75th Percentile (P75)",
            "sec_high_departmentalized": round(sec_series.quantile(0.75), 2),
            "middle_departmentalized": round(mid_series.quantile(0.75), 2),
            "elem_self_contained": round(elem_series.quantile(0.75), 2),
            "notes": "Upper quartile threshold"
        },
        {
            "metric": "Minimum State",
            "sec_high_departmentalized": round(sec_series.min(), 2),
            "middle_departmentalized": round(mid_series.min(), 2),
            "elem_self_contained": round(elem_series.min(), 2),
            "notes": f"Lowest state: {df_states_only.loc[sec_series.idxmin(), 'state']} ({sec_series.min()})"
        },
        {
            "metric": "Maximum State",
            "sec_high_departmentalized": round(sec_series.max(), 2),
            "middle_departmentalized": round(mid_series.max(), 2),
            "elem_self_contained": round(elem_series.max(), 2),
            "notes": f"Highest state: {df_states_only.loc[sec_series.idxmax(), 'state']} ({sec_series.max()})"
        },
        {
            "metric": "Missouri State Average",
            "sec_high_departmentalized": mo_row["sec_high_departmentalized"],
            "middle_departmentalized": mo_row["middle_departmentalized"],
            "elem_self_contained": mo_row["elem_self_contained"],
            "notes": f"State rank: {mo_rank} of 51 (Lower-middle distribution, below state median of {sec_series.median():.2f})"
        },
        {
            "metric": "Kansas State Average",
            "sec_high_departmentalized": ks_row["sec_high_departmentalized"],
            "middle_departmentalized": ks_row["middle_departmentalized"],
            "elem_self_contained": ks_row["elem_self_contained"],
            "notes": f"State rank: {ks_rank} of 51 (Lower quartile, below P25 threshold of {sec_series.quantile(0.25):.2f})"
        },
    ]
    df_c03 = pd.DataFrame(c03_stats)
    c03_path = os.path.join(TABLES_DIR, "table_c03_ntps_2020_21_state_distribution.csv")
    df_c03.to_csv(c03_path, index=False)
    print(f"Saved Table C03 -> {c03_path} ({len(df_c03)} rows)")

    # -------------------------------------------------------------
    # 5. Table C04: Teacher Schedule Roster Loads & Jenkins Benchmark
    # -------------------------------------------------------------
    # Secondary bell schedules dictate teacher volume:
    # Contact load = section_mean * daily_sections
    # Active roster = section_mean * cycle_sections
    # Jenkins historical benchmark: <= 125 students per teacher per day (Jenkins v. Missouri, 1985 remedial goal for KCMSD)
    schedule_environments = [
        {"geo": "Kansas NTPS Mean", "mean": 17.4, "notes": "Statewide departmentalized high school average (pools all locales)"},
        {"geo": "Missouri NTPS Mean", "mean": 19.2, "notes": "Statewide departmentalized high school average (pools all locales)"},
        {"geo": "US National Benchmark", "mean": 21.0, "notes": "Official NCES NTPS national departmentalized high school benchmark"},
        {"geo": "KC Suburban Comprehensive HS", "mean": 22.3, "notes": "Large campus secondary average (SMSD / Olathe / NKC / Lee's Summit)"},
        {"geo": "KC Suburban Core Academic (Math/Sci)", "mean": 24.5, "notes": "CRDC measured core graduation sections at comprehensive high schools"},
    ]
    
    schedule_regimes = [
        {
            "regime": "Contractual 5-of-7",
            "daily_sections": 5,
            "cycle_sections": 5,
            "teaching_fraction": 5/7,
            "multiplier_phi": 1.40,
            "description": "5 teaching periods + 2 duty/prep periods (SMSD / KCPS contractual model)"
        },
        {
            "regime": "Traditional 6-of-7",
            "daily_sections": 6,
            "cycle_sections": 6,
            "teaching_fraction": 6/7,
            "multiplier_phi": 1.17,
            "description": "6 teaching periods + 1 prep period (Traditional secondary schedule)"
        },
        {
            "regime": "Alternating 8-Block",
            "daily_sections": 3,
            "cycle_sections": 6,
            "teaching_fraction": 6/8,
            "multiplier_phi": 1.33,
            "description": "6 active courses across A/B days, 3 teaching blocks daily (NKC / Olathe / Lee's Summit)"
        },
    ]

    c04_records = []
    for env in schedule_environments:
        m = env["mean"]
        for reg in schedule_regimes:
            daily_contact = round(m * reg["daily_sections"], 1)
            active_roster = round(m * reg["cycle_sections"], 1)
            delta_jenkins = round(active_roster - 125.0, 1)
            comparison = (
                f"Below historical KCMSD benchmark ({delta_jenkins:+.1f})"
                if active_roster <= 125.0
                else f"Above historical KCMSD benchmark ({delta_jenkins:+.1f})"
            )
            
            c04_records.append({
                "environment": env["geo"],
                "section_mean": m,
                "schedule_regime": reg["regime"],
                "daily_teaching_sections": reg["daily_sections"],
                "cycle_active_sections": reg["cycle_sections"],
                "daily_contact_students": daily_contact,
                "active_grading_roster": active_roster,
                "jenkins_historical_benchmark": 125.0,
                "delta_vs_jenkins_historical_benchmark": delta_jenkins,
                "benchmark_comparison": comparison,
                "evidence_class": "Class 3: Derived Schedule Benchmark",
                "notes": f"{reg['description']}. {env['notes']}. Compared against historical KCMSD 125 remedial benchmark."
            })
            
    df_c04 = pd.DataFrame(c04_records)
    c04_path = os.path.join(TABLES_DIR, "table_c04_teacher_schedule_roster_loads.csv")
    df_c04.to_csv(c04_path, index=False)
    print(f"Saved Table C04 -> {c04_path} ({len(df_c04)} rows)")

    # -------------------------------------------------------------
    # 6. Table C05: Illustrative Scenario of Proportional Accommodation Exposure
    # -------------------------------------------------------------
    # IMPORTANT METHODOLOGICAL BOUNDARY:
    # Individual teacher rosters and student assignment across sections are unobserved in public data.
    # The figures below represent illustrative model scenarios under the assumption of uniform proportional
    # mixing within a school, using certified Study B rates for secondary schools.
    # Chronic absenteeism is intentionally excluded because school-level DG814/snapshot rates cannot be
    # naively multiplied by roster sizes as student-level probabilities.
    
    # Study B Benchmarks (Secondary High School Universe, 2023-24 CRDC):
    idea_rate = 0.1355       # IDEA IEP rate: ~13.55%
    sec504_rate = 0.0545     # Section 504 rate: ~5.45%
    combined_acc_rate = 0.1900 # Combined Legal Accommodations: ~19.00%
    el_rate = 0.0949         # English Learners (EL): ~9.49%

    secondary_archetypes = [
        {
            "archetype": "Secondary Teacher: Contractual 5-of-7 (US NTPS Benchmark)",
            "school_level": "High School / Secondary",
            "schedule": "5 sections @ 21.0 students",
            "headcount": 105.0,
            "description": "5 teaching periods @ 21.0 national mean (2 prep/duty periods)"
        },
        {
            "archetype": "Secondary Teacher: Traditional 6-of-7 (US NTPS Benchmark)",
            "school_level": "High School / Secondary",
            "schedule": "6 sections @ 21.0 students",
            "headcount": 126.0,
            "description": "6 teaching periods @ 21.0 national mean (1 prep period)"
        },
        {
            "archetype": "Secondary Teacher: Alternating 8-Block (US NTPS Benchmark)",
            "school_level": "High School / Secondary",
            "schedule": "6 sections @ 21.0 students (3 daily)",
            "headcount": 126.0,
            "description": "6 active sections on A/B rotation; daily contact = 63.0 students"
        },
        {
            "archetype": "Suburban Comprehensive HS Teacher (Contractual 5-of-7)",
            "school_level": "High School / Secondary",
            "schedule": "5 sections @ 24.5 core students",
            "headcount": 122.5,
            "description": "CRDC measured secondary core average (24.5) under contractual 5-of-7 schedule"
        },
        {
            "archetype": "Suburban Comprehensive HS Teacher (Traditional 6-of-7)",
            "school_level": "High School / Secondary",
            "schedule": "6 sections @ 24.5 core students",
            "headcount": 147.0,
            "description": "CRDC measured secondary core average (24.5) under traditional 6-period load"
        },
        {
            "archetype": "Suburban Comprehensive HS Teacher (Alternating 8-Block)",
            "school_level": "High School / Secondary",
            "schedule": "6 sections @ 24.5 core students (3 daily)",
            "headcount": 147.0,
            "description": "CRDC measured secondary core average (24.5) on A/B block rotation"
        },
    ]

    c05_records = []
    for arch in secondary_archetypes:
        n = arch["headcount"]
        iep_n = round(n * idea_rate, 1)
        sec504_n = round(n * sec504_rate, 1)
        comb_n = round(n * combined_acc_rate, 1)
        el_n = round(n * el_rate, 1)
        
        c05_records.append({
            "scenario_archetype": arch["archetype"],
            "school_level": arch["school_level"],
            "schedule_model": arch["schedule"],
            "active_roster_headcount": n,
            "proportional_idea_iep": iep_n,
            "proportional_section_504": sec504_n,
            "proportional_combined_accommodations": comb_n,
            "proportional_english_learners": el_n,
            "model_classification": "Class 3: Illustrative Proportional Mixing Scenario",
            "model_notes": f"Illustrative model assuming proportional mixing from secondary rates. {arch['description']}. Actual rosters unobserved."
        })
        
    df_c05 = pd.DataFrame(c05_records)
    c05_path = os.path.join(TABLES_DIR, "table_c05_teacher_iep_el_exposure.csv")
    df_c05.to_csv(c05_path, index=False)
    print(f"Saved Table C05 -> {c05_path} ({len(df_c05)} rows)")

    # -------------------------------------------------------------
    # 7. Generate Figures
    # -------------------------------------------------------------
    c_us = "#1f77b4" # Navy blue
    c_mo = "#2ca02c" # Green
    c_ks = "#ff7f0e" # Amber orange
    c_crdc = "#d62728" # Red
    c_ptr = "#7f7f7f" # Gray

    # --- Figure C01: SASS/NTPS Historical Benchmark Points & Definition Breaks ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    
    # Left Panel: High School Departmentalized (Grades 9-12) vs Grades 7-12
    hs_years_us = [2012, 2016, 2018, 2021]
    hs_vals_us = [24.2, 26.0, 23.3, 21.0]
    hs_years_mo = [2012, 2018, 2021]
    hs_vals_mo = [21.8, 22.5, 19.2]
    hs_years_ks = [2012, 2018, 2021]
    hs_vals_ks = [19.7, 19.8, 17.4]
    
    axes[0].plot(hs_years_us, hs_vals_us, marker="o", linewidth=2.0, markersize=8, color=c_us, label="United States (National Benchmark)")
    axes[0].plot(hs_years_mo, hs_vals_mo, marker="s", linewidth=1.8, markersize=7, color=c_mo, linestyle="--", label="Missouri State Average")
    axes[0].plot(hs_years_ks, hs_vals_ks, marker="^", linewidth=1.8, markersize=7, color=c_ks, linestyle=":", label="Kansas State Average")
    
    for y, v in zip(hs_years_us, hs_vals_us):
        axes[0].annotate(f"{v:.1f}", (y, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, fontweight="bold", color=c_us)
    axes[0].annotate(f"{hs_vals_mo[-1]:.1f}", (hs_years_mo[-1], hs_vals_mo[-1]), textcoords="offset points", xytext=(-10, -14), ha="center", fontsize=9, color=c_mo)
    axes[0].annotate(f"{hs_vals_ks[-1]:.1f}", (hs_years_ks[-1], hs_vals_ks[-1]), textcoords="offset points", xytext=(10, -14), ha="center", fontsize=9, color=c_ks)
    
    # Annotate definition caution and pandemic context
    axes[0].axvline(2019.5, color="#888888", linestyle="--", alpha=0.7)
    axes[0].text(2019.4, 15.0, "Pandemic Survey Conditions\n& Definition Shift (2020–21)", ha="right", fontsize=8, color="#555555", style="italic")
    
    axes[0].set_title("Panel A: Secondary / High School Departmentalized (Grades 9–12)", fontsize=11, fontweight="bold", pad=10)
    axes[0].set_xlabel("Survey Administration Wave", fontsize=10)
    axes[0].set_ylabel("Teacher-Reported Average Class Size", fontsize=10)
    axes[0].set_xticks([2012, 2016, 2018, 2021])
    axes[0].set_xticklabels(["2011–12\n(SASS)", "2015–16\n(NTPS)", "2017–18\n(NTPS)", "2020–21\n(NTPS)"])
    axes[0].grid(True, linestyle="--", alpha=0.5)
    axes[0].legend(loc="upper right", frameon=True, fontsize=8.5)
    axes[0].set_ylim(14, 28)
    
    # Right Panel: Elementary Self-Contained (Grades K-5/6)
    el_years = [2000, 2004, 2008, 2012, 2021]
    el_us = [21.1, 20.4, 20.0, 21.2, 19.1]
    el_mo = [20.7, 19.1, 19.4, 20.2, 18.2]
    el_ks = [18.3, 19.2, 19.5, 20.4, 17.9]
    
    axes[1].plot(el_years, el_us, marker="o", linewidth=2.0, markersize=8, color=c_us, label="United States (National Benchmark)")
    axes[1].plot(el_years, el_mo, marker="s", linewidth=1.8, markersize=7, color=c_mo, linestyle="--", label="Missouri State Average")
    axes[1].plot(el_years, el_ks, marker="^", linewidth=1.8, markersize=7, color=c_ks, linestyle=":", label="Kansas State Average")
    
    for y, v in zip(el_years, el_us):
        axes[1].annotate(f"{v:.1f}", (y, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, fontweight="bold", color=c_us)
        
    axes[1].set_title("Panel B: Elementary School Self-Contained (Grades K–5/6)", fontsize=11, fontweight="bold", pad=10)
    axes[1].set_xlabel("Survey Administration Wave", fontsize=10)
    axes[1].set_xticks([2000, 2004, 2008, 2012, 2021])
    axes[1].set_xticklabels(["1999–00\n(SASS)", "2003–04\n(SASS)", "2007–08\n(SASS)", "2011–12\n(SASS)", "2020–21\n(NTPS)"])
    axes[1].grid(True, linestyle="--", alpha=0.5)
    axes[1].legend(loc="upper right", frameon=True, fontsize=8.5)
    
    fig.suptitle("Historical SASS/NTPS Class Size Benchmarks Across Two Decades (Historical Series with Definition Breaks)", fontsize=12, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    
    fig_c01_path = os.path.join(FIGURES_DIR, "fig_c01_sass_ntps_longitudinal_trajectory.png")
    fig.savefig(fig_c01_path, dpi=300)
    plt.close(fig)
    print(f"Saved Figure C01 -> {fig_c01_path}")
    copy_to_brain("fig_c01_sass_ntps_longitudinal_trajectory.png")

    # --- Figure C02: CRDC vs. NTPS Methodological Comparison ---
    # Generated DIRECTLY from Table C02 to eliminate any hardcoded discrepancy
    sub_c02 = df_c02[df_c02["school_year"].isin(["2015-16", "2017-18", "2020-21"])].copy()
    
    comp_years = [2016, 2018, 2021]
    comp_labels = ["2015–16", "2017–18", "2020–21"]
    
    ptrs = sub_c02["ccd_macro_ptr"].tolist()
    crdc_a = sub_c02["crdc_unweighted_cell_mean"].tolist()
    crdc_b = sub_c02["crdc_section_weighted_mean"].tolist()
    crdc_c = sub_c02["crdc_student_weighted_mean"].tolist()
    ntps_d = sub_c02["ntps_teacher_hs_dept"].tolist()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(comp_years, ptrs, marker="v", linewidth=2.0, markersize=8, color=c_ptr, linestyle="-.", label="CCD Macro Pupil-Teacher Ratio (~15–16)")
    ax.plot(comp_years, crdc_a, marker="s", linewidth=2.0, markersize=8, color="#9467bd", linestyle="--", label="Estimand A: CRDC Unweighted Cell Mean (~15–18)")
    ax.plot(comp_years, crdc_b, marker="^", linewidth=2.0, markersize=8, color="#e377c2", linestyle=":", label="Estimand B: CRDC Section-Weighted Mean (~15–18)")
    ax.plot(comp_years, crdc_c, marker="D", linewidth=2.5, markersize=9, color=c_crdc, label="Estimand C: CRDC Enrollment-Weighted Lower-Bound Proxy (~20–23)")
    ax.plot(comp_years, ntps_d, marker="o", linewidth=2.5, markersize=9, color=c_us, label="NTPS Teacher-Reported High School Class Size (~21–26)")
    
    # Annotate points directly from sub_c02 data
    for y, v in zip(comp_years, ptrs):
        ax.annotate(f"{v:.1f}", (y, v), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9, color=c_ptr, fontweight="bold")
    for y, v in zip(comp_years, crdc_a):
        ax.annotate(f"{v:.1f}", (y, v), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9, color="#9467bd", fontweight="bold")
    for y, v in zip(comp_years, crdc_c):
        ax.annotate(f"{v:.1f}", (y, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=c_crdc, fontweight="bold")
    for y, v in zip(comp_years, ntps_d):
        ax.annotate(f"{v:.1f}", (y, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=c_us, fontweight="bold")

    # Shaded band between CRDC Estimand C and NTPS Teacher-Reported
    ax.fill_between(comp_years, crdc_c, ntps_d, color=c_us, alpha=0.10, label="Numerical Proximity Zone (NTPS Survey vs. CRDC Estimand C)")

    ax.set_title("Reconciling Class Size Estimands: Administrative Census vs. Teacher Survey", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("School Year", fontsize=11)
    ax.set_ylabel("Class Size / Ratio Headcount", fontsize=11)
    ax.set_xticks(comp_years)
    ax.set_xticklabels(comp_labels, fontsize=10)
    ax.set_ylim(13, 28)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", frameon=True, fontsize=8.5)
    fig.tight_layout()
    
    fig_c02_path = os.path.join(FIGURES_DIR, "fig_c02_crdc_vs_ntps_comparison.png")
    fig.savefig(fig_c02_path, dpi=300)
    plt.close(fig)
    print(f"Saved Figure C02 -> {fig_c02_path}")
    copy_to_brain("fig_c02_crdc_vs_ntps_comparison.png")

    # --- Figure C03: NTPS 2020-21 State Distribution ---
    df_sorted = df_states_only.dropna(subset=["sec_high_departmentalized"]).sort_values("sec_high_departmentalized", ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 12))
    colors = []
    for s in df_sorted["state"]:
        if s == "Missouri":
            colors.append(c_mo)
        elif s == "Kansas":
            colors.append(c_ks)
        else:
            colors.append("#aec7e8")
            
    bars = ax.barh(df_sorted["state"], df_sorted["sec_high_departmentalized"], color=colors, height=0.75)
    
    # Add vertical reference lines for US Benchmark, P25, Median, P75
    ax.axvline(21.0, color=c_us, linestyle="-", linewidth=2.0, label="US Benchmark: 21.0")
    ax.axvline(sec_series.median(), color="#333333", linestyle="--", linewidth=1.5, label=f"State Median: {sec_series.median():.1f}")
    ax.axvline(sec_series.quantile(0.25), color="#666666", linestyle=":", linewidth=1.2, label=f"P25: {sec_series.quantile(0.25):.1f}")
    ax.axvline(sec_series.quantile(0.75), color="#666666", linestyle=":", linewidth=1.2, label=f"P75: {sec_series.quantile(0.75):.1f}")
    
    for bar, st, val in zip(bars, df_sorted["state"], df_sorted["sec_high_departmentalized"]):
        if st in ["Missouri", "Kansas"]:
            ax.text(val + 0.3, bar.get_y() + bar.get_height()/2, f"{st}: {val:.1f}", va="center", ha="left", fontsize=9, fontweight="bold", color="black")
            
    ax.set_title("Distribution of Teacher-Reported High School Class Sizes Across States: 2020–21 NTPS", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Average Class Size for Teachers in Departmentalized Instruction (Grades 9–12)", fontsize=11)
    ax.set_xlim(10, 30)
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)
    ax.legend(loc="lower right", frameon=True, fontsize=9)
    fig.tight_layout()
    
    fig_c03_path = os.path.join(FIGURES_DIR, "fig_c03_ntps_state_distribution.png")
    fig.savefig(fig_c03_path, dpi=300)
    plt.close(fig)
    print(f"Saved Figure C03 -> {fig_c03_path}")
    copy_to_brain("fig_c03_ntps_state_distribution.png")

    # --- Figure C04: Schedule Regime Roster Load vs Jenkins Ceiling ---
    fig, ax = plt.subplots(figsize=(11, 6))
    
    labels = [
        "Kansas Mean\n(17.4)",
        "Missouri Mean\n(19.2)",
        "US Benchmark\n(21.0)",
        "KC Suburban Comp\n(22.3)",
        "KC Suburban Core\n(24.5)"
    ]
    x = np.arange(len(labels))
    width = 0.25
    
    load_5of7 = [17.4 * 5, 19.2 * 5, 21.0 * 5, 22.3 * 5, 24.5 * 5]
    load_6of7 = [17.4 * 6, 19.2 * 6, 21.0 * 6, 22.3 * 6, 24.5 * 6]
    daily_8block = [17.4 * 3, 19.2 * 3, 21.0 * 3, 22.3 * 3, 24.5 * 3]
    
    rects1 = ax.bar(x - width, load_5of7, width, label="Contractual 5-of-7 (Active Roster = Daily Contact: 5 sections)", color="#4575b4")
    rects2 = ax.bar(x, load_6of7, width, label="Traditional 6-of-7 (Active Roster = Daily Contact: 6 sections)", color="#d73027")
    rects3 = ax.bar(x + width, daily_8block, width, label="Alternating 8-Block (Daily Contact: 3 blocks; Active Roster = 6 sections)", color="#fdae61")
    
    # Add Jenkins Historical Benchmark Line
    ax.axhline(125.0, color="black", linestyle="--", linewidth=2.0, label="Historical KCMSD Desegregation Benchmark (≤ 125 students/day)")
    ax.text(3.8, 127.0, "KCMSD Benchmark: 125", fontsize=9, fontweight="bold", color="black")
    
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}", (rect.get_x() + rect.get_width()/2, h), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8)
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}", (rect.get_x() + rect.get_width()/2, h), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8, fontweight="bold" if h > 125 else "normal")
    for rect in rects3:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}", (rect.get_x() + rect.get_width()/2, h), textcoords="offset points", xytext=(0, 3), ha="center", fontsize=8)

    ax.set_title("Secondary Teacher Student Loads Under Standard Schedules vs. Historical KCMSD Jenkins Benchmark", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylabel("Number of Assigned Students", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, 175)
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    ax.legend(loc="upper left", frameon=True, fontsize=8.5)
    fig.tight_layout()
    
    fig_c04_path = os.path.join(FIGURES_DIR, "fig_c04_schedule_regime_roster_load.png")
    fig.savefig(fig_c04_path, dpi=300)
    plt.close(fig)
    print(f"Saved Figure C04 -> {fig_c04_path}")
    copy_to_brain("fig_c04_schedule_regime_roster_load.png")

    print("=== Phase 5 Analysis Complete ===")



if __name__ == "__main__":
    run_sass_ntps_analysis()
