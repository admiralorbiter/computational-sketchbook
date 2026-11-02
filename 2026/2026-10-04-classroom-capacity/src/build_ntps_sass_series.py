"""
src/build_ntps_sass_series.py
Phase 5: SASS / NTPS Series Construction & Historical Harmonization

Constructs the canonical longitudinal dataset of teacher-reported class size and instructional
environments from the National Center for Education Statistics (NCES) Schools and Staffing
Survey (SASS) and National Teacher and Principal Survey (NTPS).

Data Sources Ingested:
  1. 1999-2000 SASS (Digest of Education Statistics 2004, Table 68: tabn068.xls)
  2. 2003-04 SASS (Digest of Education Statistics 2006, Table 64: tabn064.xls)
  3. 2007-08 SASS (Digest of Education Statistics 2010, Table 71: tabn071.xls & First Look Table 8)
  4. 2011-12 SASS (Digest of Education Statistics 2019, Table 209.30: tabn209_30.xls & First Look Table 7)
  5. 2015-16 NTPS (NTPS First Look Table 8: National departmentalized secondary benchmark)
  6. 2017-18 NTPS (NTPS Table A-7a: National & state departmentalized secondary benchmark)
  7. 2020-21 NTPS (NTPS Table 7: ntps2021_sflt07_t1s.xlsx: 50 states + DC + US by level & class type)

Outputs:
  - data/processed/ntps_sass_class_size_series.csv
  - data/processed/ntps_2020_21_state_class_size.csv
  - data/processed/sass_state_historical_panel.csv
"""

import os
import re
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SASS_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "sass")
NTPS_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "ntps")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

# Standard 50 States + DC Lookup
STATE_FIPS_MAP = {
    "United States": "US", "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
    "California": "06", "Colorado": "08", "Connecticut": "09", "Delaware": "10", "District of Columbia": "11",
    "Florida": "12", "Georgia": "13", "Hawaii": "15", "Idaho": "16", "Illinois": "17",
    "Indiana": "18", "Iowa": "19", "Kansas": "20", "Kentucky": "21", "Louisiana": "22",
    "Maine": "23", "Maryland": "24", "Massachusetts": "25", "Michigan": "26", "Minnesota": "27",
    "Mississippi": "28", "Missouri": "29", "Montana": "30", "Nebraska": "31", "Nevada": "32",
    "New Hampshire": "33", "New Jersey": "34", "New Mexico": "35", "New York": "36",
    "North Carolina": "37", "North Dakota": "38", "Ohio": "39", "Oklahoma": "40", "Oregon": "41",
    "Pennsylvania": "42", "Rhode Island": "44", "South Carolina": "45", "South Dakota": "46",
    "Tennessee": "47", "Texas": "48", "Utah": "49", "Vermont": "50", "Virginia": "51",
    "Washington": "53", "West Virginia": "54", "Wisconsin": "55", "Wyoming": "56"
}


def clean_state_name(val):
    """Normalize state names by stripping trailing leader dots, backslashes, and whitespace."""
    if pd.isna(val):
        return None
    s = str(val).strip()
    s = re.sub(r"[\.\s\\_]+$", "", s).strip()
    return s


def parse_numeric(val):
    """Parse numeric values from Excel cells, converting suppression codes and symbols to NaN."""
    if pd.isna(val):
        return np.nan, ""
    if isinstance(val, (int, float, np.integer, np.floating)):
        return abs(float(val)), ""
    s = str(val).strip()
    flag = ""
    if "!" in s:
        flag = "!"
        s = s.replace("!", "").strip()
    if "\ufffd" in s or "‡" in s or s in ["-", "—", "†", "N/A", "nan"]:
        return np.nan, "‡"
    try:
        num = float(s)
        # SASS SEs are sometimes formatted as negative numbers in older Digest tables
        return abs(num), flag
    except ValueError:
        return np.nan, flag


def parse_sass_1999_2000():
    """Parse Digest 2004 Table 68 (1999-2000 SASS)."""
    filepath = os.path.join(SASS_RAW_DIR, "tabn068.xls")
    df = pd.read_excel(filepath, header=None)
    records = []
    
    for r in range(12, len(df)):
        raw_name = df.iloc[r, 0]
        state = clean_state_name(raw_name)
        if not state or state not in STATE_FIPS_MAP:
            continue
            
        elem_val, elem_flag = parse_numeric(df.iloc[r, 29])
        elem_se, _ = parse_numeric(df.iloc[r, 30])
        sec_val, sec_flag = parse_numeric(df.iloc[r, 32])
        sec_se, _ = parse_numeric(df.iloc[r, 33])
        
        records.append({
            "survey_cycle": "1999-2000 (SASS)",
            "school_year": "1999-2000",
            "year": 2000,
            "state": state,
            "state_fips": STATE_FIPS_MAP[state],
            "elem_mean": elem_val,
            "elem_se": elem_se,
            "elem_flag": elem_flag,
            "sec_mean": sec_val,
            "sec_se": sec_se,
            "sec_flag": sec_flag,
            "source_table": "NCES Digest 2004 Table 68",
        })
    return pd.DataFrame(records)


def parse_sass_2003_04():
    """Parse Digest 2006 Table 64 (2003-04 SASS)."""
    filepath = os.path.join(SASS_RAW_DIR, "tabn064.xls")
    df = pd.read_excel(filepath, header=None)
    records = []
    
    for r in range(8, len(df)):
        raw_name = df.iloc[r, 0]
        state = clean_state_name(raw_name)
        if not state or state not in STATE_FIPS_MAP:
            continue
            
        elem_val, elem_flag = parse_numeric(df.iloc[r, 19])
        elem_se, _ = parse_numeric(df.iloc[r, 20])
        sec_val, sec_flag = parse_numeric(df.iloc[r, 21])
        sec_se, _ = parse_numeric(df.iloc[r, 22])
        
        records.append({
            "survey_cycle": "2003-04 (SASS)",
            "school_year": "2003-04",
            "year": 2004,
            "state": state,
            "state_fips": STATE_FIPS_MAP[state],
            "elem_mean": elem_val,
            "elem_se": elem_se,
            "elem_flag": elem_flag,
            "sec_mean": sec_val,
            "sec_se": sec_se,
            "sec_flag": sec_flag,
            "source_table": "NCES Digest 2006 Table 64",
        })
    return pd.DataFrame(records)


def parse_sass_2007_08():
    """Parse Digest 2010 Table 71 (2007-08 SASS)."""
    filepath = os.path.join(SASS_RAW_DIR, "tabn071.xls")
    df = pd.read_excel(filepath, header=None)
    records = []
    
    for r in range(4, len(df)):
        raw_name = df.iloc[r, 0]
        state = clean_state_name(raw_name)
        if not state or state not in STATE_FIPS_MAP:
            continue
            
        elem_val, elem_flag = parse_numeric(df.iloc[r, 19])
        elem_se, _ = parse_numeric(df.iloc[r, 20])
        sec_val, sec_flag = parse_numeric(df.iloc[r, 21])
        sec_se, _ = parse_numeric(df.iloc[r, 22])
        
        records.append({
            "survey_cycle": "2007-08 (SASS)",
            "school_year": "2007-08",
            "year": 2008,
            "state": state,
            "state_fips": STATE_FIPS_MAP[state],
            "elem_mean": elem_val,
            "elem_se": elem_se,
            "elem_flag": elem_flag,
            "sec_mean": sec_val,
            "sec_se": sec_se,
            "sec_flag": sec_flag,
            "source_table": "NCES Digest 2010 Table 71",
        })
    return pd.DataFrame(records)


def parse_sass_2011_12():
    """Parse Digest 2019 Table 209.30 (2011-12 SASS)."""
    filepath = os.path.join(SASS_RAW_DIR, "tabn209_30.xls")
    df = pd.read_excel(filepath, header=None)
    records = []
    
    for r in range(5, len(df)):
        raw_name = df.iloc[r, 0]
        state = clean_state_name(raw_name)
        if not state or state not in STATE_FIPS_MAP:
            continue
            
        elem_val, elem_flag = parse_numeric(df.iloc[r, 27])
        elem_se, _ = parse_numeric(df.iloc[r, 29])
        sec_val, sec_flag = parse_numeric(df.iloc[r, 30])
        sec_se, _ = parse_numeric(df.iloc[r, 32])
        
        records.append({
            "survey_cycle": "2011-12 (SASS)",
            "school_year": "2011-12",
            "year": 2012,
            "state": state,
            "state_fips": STATE_FIPS_MAP[state],
            "elem_mean": elem_val,
            "elem_se": elem_se,
            "elem_flag": elem_flag,
            "sec_mean": sec_val,
            "sec_se": sec_se,
            "sec_flag": sec_flag,
            "source_table": "NCES Digest 2019 Table 209.30",
        })
    return pd.DataFrame(records)


def parse_ntps_2020_21():
    """Parse official 2020-21 NTPS Table 7 (ntps2021_sflt07_t1s.xlsx)."""
    filepath = os.path.join(NTPS_RAW_DIR, "ntps2021_sflt07_t1s.xlsx")
    df = pd.read_excel(filepath, sheet_name="EST", header=None)
    
    records = []
    for r in range(3, len(df)):
        raw_name = df.iloc[r, 0]
        state = clean_state_name(raw_name)
        if not state or state not in STATE_FIPS_MAP:
            continue
            
        e_sc, e_sc_f = parse_numeric(df.iloc[r, 1])
        e_dp, e_dp_f = parse_numeric(df.iloc[r, 3])
        m_sc, m_sc_f = parse_numeric(df.iloc[r, 5])
        m_dp, m_dp_f = parse_numeric(df.iloc[r, 7])
        s_sc, s_sc_f = parse_numeric(df.iloc[r, 9])
        s_dp, s_dp_f = parse_numeric(df.iloc[r, 11])
        c_sc, c_sc_f = parse_numeric(df.iloc[r, 13])
        c_dp, c_dp_f = parse_numeric(df.iloc[r, 15])
        
        records.append({
            "state": state,
            "state_fips": STATE_FIPS_MAP[state],
            "elem_self_contained": e_sc,
            "elem_self_contained_flag": e_sc_f,
            "elem_departmentalized": e_dp,
            "elem_departmentalized_flag": e_dp_f,
            "middle_self_contained": m_sc,
            "middle_self_contained_flag": m_sc_f,
            "middle_departmentalized": m_dp,
            "middle_departmentalized_flag": m_dp_f,
            "sec_high_self_contained": s_sc,
            "sec_high_self_contained_flag": s_sc_f,
            "sec_high_departmentalized": s_dp,
            "sec_high_departmentalized_flag": s_dp_f,
            "comb_self_contained": c_sc,
            "comb_self_contained_flag": c_sc_f,
            "comb_departmentalized": c_dp,
            "comb_departmentalized_flag": c_dp_f,
        })
    return pd.DataFrame(records)


def build_canonical_series():
    """Build canonical multi-wave class size series and save all processed outputs."""
    print("=== Building SASS / NTPS Harmonized Series ===")
    
    # 1. Parse historical SASS tables
    df_s99 = parse_sass_1999_2000()
    df_s03 = parse_sass_2003_04()
    df_s07 = parse_sass_2007_08()
    df_s11 = parse_sass_2011_12()
    
    print(f"Parsed SASS 1999-2000: {len(df_s99)} jurisdictions.")
    print(f"Parsed SASS 2003-04:   {len(df_s03)} jurisdictions.")
    print(f"Parsed SASS 2007-08:   {len(df_s07)} jurisdictions.")
    print(f"Parsed SASS 2011-12:   {len(df_s11)} jurisdictions.")
    
    # Combine SASS historical panel
    df_sass_panel = pd.concat([df_s99, df_s03, df_s07, df_s11], ignore_index=True)
    sass_panel_path = os.path.join(PROCESSED_DIR, "sass_state_historical_panel.csv")
    df_sass_panel.to_csv(sass_panel_path, index=False)
    print(f"Saved SASS state historical panel -> {sass_panel_path}")
    
    # 2. Parse 2020-21 NTPS Table 7
    df_ntps2021 = parse_ntps_2020_21()
    ntps_state_path = os.path.join(PROCESSED_DIR, "ntps_2020_21_state_class_size.csv")
    df_ntps2021.to_csv(ntps_state_path, index=False)
    print(f"Saved NTPS 2020-21 clean state panel -> {ntps_state_path} ({len(df_ntps2021)} jurisdictions)")
    
    # 3. Construct Canonical Harmonized Series
    # Rows include:
    #   - Genuinely published survey estimates (Class 1) across all waves
    #   - Dual estimands for 2011-12 (Grades 7-12 vs High School 9-12)
    #   - Subject-specific benchmarks for secondary departmentalized instruction
    #   - Schedule-derived load models
    
    canonical_rows = []
    
    # --- A. SASS 1999-2000 ---
    for st in ["United States", "Missouri", "Kansas"]:
        sub = df_s99[df_s99["state"] == st].iloc[0]
        # Elementary Self-Contained
        canonical_rows.append({
            "survey_cycle": "1999-2000 (SASS)", "survey_program": "SASS", "school_year": "1999-2000", "year": 2000,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Elementary School",
            "instructional_type": "Self-Contained", "subject": "All / General",
            "class_size_mean": sub["elem_mean"], "class_size_se": sub["elem_se"], "reporting_flag": sub["elem_flag"],
            "estimand_definition": "Teacher-reported self-contained class size (K-5/6)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": sub["source_table"], "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })
        # Secondary Departmentalized (Grades 7-12)
        canonical_rows.append({
            "survey_cycle": "1999-2000 (SASS)", "survey_program": "SASS", "school_year": "1999-2000", "year": 2000,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Secondary / Grades 7-12",
            "instructional_type": "Departmentalized", "subject": "All / General",
            "class_size_mean": sub["sec_mean"], "class_size_se": sub["sec_se"], "reporting_flag": sub["sec_flag"],
            "estimand_definition": "Grade-span level of instruction (grades 7-12 departmentalized)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": sub["source_table"], "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })
        
    # --- B. SASS 2003-04 ---
    for st in ["United States", "Missouri", "Kansas"]:
        sub = df_s03[df_s03["state"] == st].iloc[0]
        canonical_rows.append({
            "survey_cycle": "2003-04 (SASS)", "survey_program": "SASS", "school_year": "2003-04", "year": 2004,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Elementary School",
            "instructional_type": "Self-Contained", "subject": "All / General",
            "class_size_mean": sub["elem_mean"], "class_size_se": sub["elem_se"], "reporting_flag": sub["elem_flag"],
            "estimand_definition": "Teacher-reported self-contained class size (K-5/6)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": sub["source_table"], "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })
        canonical_rows.append({
            "survey_cycle": "2003-04 (SASS)", "survey_program": "SASS", "school_year": "2003-04", "year": 2004,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Secondary / Grades 7-12",
            "instructional_type": "Departmentalized", "subject": "All / General",
            "class_size_mean": sub["sec_mean"], "class_size_se": sub["sec_se"], "reporting_flag": sub["sec_flag"],
            "estimand_definition": "Grade-span level of instruction (grades 7-12 departmentalized)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": sub["source_table"], "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })

    # --- C. SASS 2007-08 ---
    for st in ["United States", "Missouri", "Kansas"]:
        sub = df_s07[df_s07["state"] == st].iloc[0]
        canonical_rows.append({
            "survey_cycle": "2007-08 (SASS)", "survey_program": "SASS", "school_year": "2007-08", "year": 2008,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Elementary School",
            "instructional_type": "Self-Contained", "subject": "All / General",
            "class_size_mean": sub["elem_mean"], "class_size_se": sub["elem_se"], "reporting_flag": sub["elem_flag"],
            "estimand_definition": "Teacher-reported self-contained class size (K-5/6)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": sub["source_table"], "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })
        canonical_rows.append({
            "survey_cycle": "2007-08 (SASS)", "survey_program": "SASS", "school_year": "2007-08", "year": 2008,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Secondary / Grades 7-12",
            "instructional_type": "Departmentalized", "subject": "All / General",
            "class_size_mean": sub["sec_mean"], "class_size_se": sub["sec_se"], "reporting_flag": sub["sec_flag"],
            "estimand_definition": "Grade-span level of instruction (grades 7-12 departmentalized)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": sub["source_table"], "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })

    # --- D. SASS 2011-12 ---
    # First: Digest Table 209.30 (Grades 7-12 Departmentalized)
    for st in ["United States", "Missouri", "Kansas"]:
        sub = df_s11[df_s11["state"] == st].iloc[0]
        canonical_rows.append({
            "survey_cycle": "2011-12 (SASS)", "survey_program": "SASS", "school_year": "2011-12", "year": 2012,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Elementary School",
            "instructional_type": "Self-Contained", "subject": "All / General",
            "class_size_mean": sub["elem_mean"], "class_size_se": sub["elem_se"], "reporting_flag": sub["elem_flag"],
            "estimand_definition": "Teacher-reported self-contained class size (K-5/6)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": "NCES Digest 2019 Table 209.30", "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })
        canonical_rows.append({
            "survey_cycle": "2011-12 (SASS)", "survey_program": "SASS", "school_year": "2011-12", "year": 2012,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Secondary / Grades 7-12",
            "instructional_type": "Departmentalized", "subject": "All / General",
            "class_size_mean": sub["sec_mean"], "class_size_se": sub["sec_se"], "reporting_flag": sub["sec_flag"],
            "estimand_definition": "Grade-span level of instruction (grades 7-12 departmentalized)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": "NCES Digest 2019 Table 209.30", "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })
        
    # Second: First Look Table 7 (High School 9-12 Departmentalized)
    # NCES 2013-314 Table 7: US 24.2, MO 21.8, KS 19.7 (and Table 69: US 24.2, MO 23.1, KS 20.5)
    hs_11_benchmarks = [
        {"geography": "United States", "state_fips": "US", "mean": 24.2, "source": "NCES SASS 2011-12 First Look Table 7"},
        {"geography": "Missouri", "state_fips": "29", "mean": 21.8, "source": "NCES SASS 2011-12 First Look Table 7"},
        {"geography": "Kansas", "state_fips": "20", "mean": 19.7, "source": "NCES SASS 2011-12 First Look Table 7"},
    ]
    for b in hs_11_benchmarks:
        canonical_rows.append({
            "survey_cycle": "2011-12 (SASS)", "survey_program": "SASS", "school_year": "2011-12", "year": 2012,
            "geography": b["geography"], "state_fips": b["state_fips"], "school_level": "High School",
            "instructional_type": "Departmentalized", "subject": "All / General",
            "class_size_mean": b["mean"], "class_size_se": np.nan, "reporting_flag": "",
            "estimand_definition": "School-level departmentalized (grades 9-12 schools)",
            "sample_representation": "National Population" if b["geography"] == "United States" else "State Population",
            "source_table": b["source"], "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })

    # --- E. NTPS 2015-16 ---
    # National High School Departmentalized only (not state-representative)
    canonical_rows.append({
        "survey_cycle": "2015-16 (NTPS)", "survey_program": "NTPS", "school_year": "2015-16", "year": 2016,
        "geography": "United States", "state_fips": "US", "school_level": "High School",
        "instructional_type": "Departmentalized", "subject": "All / General",
        "class_size_mean": 26.0, "class_size_se": np.nan, "reporting_flag": "",
        "estimand_definition": "School-level departmentalized (grades 9-12 schools)",
        "sample_representation": "National Population (National Only; Not State-Representative)",
        "source_table": "NCES NTPS 2015-16 First Look Table 8", "evidence_class": "Class 1: Measured / Published Survey Statistic"
    })

    # --- F. NTPS 2017-18 ---
    ntps_17_benchmarks = [
        {"geography": "United States", "state_fips": "US", "mean": 23.3, "source": "NCES NTPS 2017-18 Table A-7a"},
        {"geography": "Missouri", "state_fips": "29", "mean": 22.5, "source": "NCES NTPS 2017-18 State Library / Table A-7a"},
        {"geography": "Kansas", "state_fips": "20", "mean": 19.8, "source": "NCES NTPS 2017-18 State Library / Table A-7a"},
    ]
    for b in ntps_17_benchmarks:
        canonical_rows.append({
            "survey_cycle": "2017-18 (NTPS)", "survey_program": "NTPS", "school_year": "2017-18", "year": 2018,
            "geography": b["geography"], "state_fips": b["state_fips"], "school_level": "High School",
            "instructional_type": "Departmentalized", "subject": "All / General",
            "class_size_mean": b["mean"], "class_size_se": np.nan, "reporting_flag": "",
            "estimand_definition": "School-level departmentalized (grades 9-12 schools)",
            "sample_representation": "National Population" if b["geography"] == "United States" else "State Population",
            "source_table": b["source"], "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })

    # --- G. NTPS 2020-21 (All Levels & Types for US, MO, KS) ---
    for st in ["United States", "Missouri", "Kansas"]:
        sub = df_ntps2021[df_ntps2021["state"] == st].iloc[0]
        # Elementary Self-Contained
        canonical_rows.append({
            "survey_cycle": "2020-21 (NTPS)", "survey_program": "NTPS", "school_year": "2020-21", "year": 2021,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Elementary School",
            "instructional_type": "Self-Contained", "subject": "All / General",
            "class_size_mean": sub["elem_self_contained"], "class_size_se": np.nan, "reporting_flag": sub["elem_self_contained_flag"],
            "estimand_definition": "Teacher-reported self-contained class size (grades K-5/6)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": "NCES NTPS 2020-21 Table 7", "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })
        # Middle School Departmentalized
        canonical_rows.append({
            "survey_cycle": "2020-21 (NTPS)", "survey_program": "NTPS", "school_year": "2020-21", "year": 2021,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "Middle School",
            "instructional_type": "Departmentalized", "subject": "All / General",
            "class_size_mean": sub["middle_departmentalized"], "class_size_se": np.nan, "reporting_flag": sub["middle_departmentalized_flag"],
            "estimand_definition": "School-level departmentalized (grades 5/6-8 schools)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": "NCES NTPS 2020-21 Table 7", "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })
        # Secondary / High School Departmentalized
        canonical_rows.append({
            "survey_cycle": "2020-21 (NTPS)", "survey_program": "NTPS", "school_year": "2020-21", "year": 2021,
            "geography": st, "state_fips": sub["state_fips"], "school_level": "High School",
            "instructional_type": "Departmentalized", "subject": "All / General",
            "class_size_mean": sub["sec_high_departmentalized"], "class_size_se": np.nan, "reporting_flag": sub["sec_high_departmentalized_flag"],
            "estimand_definition": "School-level departmentalized (grades 9-12 schools)",
            "sample_representation": "National Population" if st == "United States" else "State Population",
            "source_table": "NCES NTPS 2020-21 Table 7", "evidence_class": "Class 1: Measured / Published Survey Statistic"
        })

    # Save Canonical Harmonized Series (Authentic Published Statistics Only)
    df_canonical = pd.DataFrame(canonical_rows)
    canonical_path = os.path.join(PROCESSED_DIR, "ntps_sass_class_size_series.csv")
    df_canonical.to_csv(canonical_path, index=False)
    print(f"Saved canonical SASS/NTPS class size series -> {canonical_path} ({len(df_canonical)} authentic published records)")

    # Optional: Save Analyst Subject Scenarios in a clearly distinguished separate file
    subject_weights = [
        {"subject": "Mathematics", "multiplier": 1.10, "notes": "Core graduation requirement; balanced tracks"},
        {"subject": "Science", "multiplier": 1.12, "notes": "Lab safety caps typically 24-28"},
        {"subject": "Social Studies", "multiplier": 1.18, "notes": "Typically largest academic core sections"},
        {"subject": "English / Language Arts", "multiplier": 1.07, "notes": "Writing-intensive grading burden"},
        {"subject": "Foreign Languages", "multiplier": 1.00, "notes": "Standard elective academic tracks"},
        {"subject": "Fine Arts / Music", "multiplier": 1.26, "notes": "Includes large performance ensembles"},
        {"subject": "Career & Tech Ed (CTE)", "multiplier": 0.83, "notes": "Shop, culinary, lab safety caps"},
        {"subject": "Special Education (Resource)", "multiplier": 0.45, "notes": "Pull-out departmentalized sections"}
    ]
    geo_bases = [
        {"geography": "United States", "state_fips": "US", "base_mean": 21.0},
        {"geography": "Missouri", "state_fips": "29", "base_mean": 19.2},
        {"geography": "Kansas", "state_fips": "20", "base_mean": 17.4},
    ]
    scenario_rows = []
    for g in geo_bases:
        for sw in subject_weights:
            subj_mean = round(g["base_mean"] * sw["multiplier"], 1)
            scenario_rows.append({
                "scenario_type": "Analyst Subject Ratio Projection",
                "survey_base_cycle": "2020-21 (NTPS)",
                "geography": g["geography"], "state_fips": g["state_fips"],
                "subject": sw["subject"], "multiplier": sw["multiplier"],
                "projected_class_size_mean": subj_mean,
                "notes": sw["notes"],
                "evidence_class": "Class 3: Analyst Scenario Projection (Not Published NCES Data)"
            })
    df_scenarios = pd.DataFrame(scenario_rows)
    scenario_path = os.path.join(PROCESSED_DIR, "analyst_subject_scenarios.csv")
    df_scenarios.to_csv(scenario_path, index=False)
    print(f"Saved analyst subject scenarios -> {scenario_path} ({len(df_scenarios)} records)")
    
    return df_canonical


if __name__ == "__main__":
    build_canonical_series()

