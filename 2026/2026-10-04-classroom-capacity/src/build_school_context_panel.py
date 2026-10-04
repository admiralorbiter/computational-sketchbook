"""
Pipeline: Build Longitudinal School-Level Context & Instructional-Load Panel (Phase 4).
Outputs:
- data/processed/school_context_panel.parquet
- data/processed/school_context_secondary_panel.csv
- data/processed/school_context_national_summary.csv

Methodological Guardrails:
1. Keeps dimensions strictly distinct: class size, IDEA/IEP, 504, EL, chronic absenteeism, staffing.
   Does NOT collapse into a composite "instructional complexity index".
2. Maintains explicit epistemic distinction: School-level IEP/EL/absence percentages describe the
   surrounding school context, NOT the composition of any particular classroom section.
3. Strict missingness enforcement (require_complete=True) across all demographic and enrollment sums.
"""

import sys
import os
import zipfile
import time
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parents[1]
SKETCHBOOK_ROOT = PROJECT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.harmonize_crdc import (
    clean_series, sum_clean_series, sum_enrollment_with_nonbinary, clean_combokey, KC_COUNTY_FIPS
)

RAW_CRDC_DIR = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "raw" / "crdc"
RAW_EDFACTS_DIR = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "raw" / "edfacts"
KC_LONG_PATH = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "processed" / "kc_school_capacity_long_2014_15_2024_25.csv"
KC_2013_PATH = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "processed" / "kc_ccd_school_capacity_2013_14.csv"

DATA_INTERMEDIATE = PROJECT_DIR / "data" / "intermediate"
DATA_PROCESSED = PROJECT_DIR / "data" / "processed"

DATA_INTERMEDIATE.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)


def load_kc_metadata():
    """Load Kansas City metropolitan school metadata and canonical PTR from Phase 3 CCD files."""
    df_kc_long = pd.read_csv(KC_LONG_PATH, low_memory=False)
    df_kc_2013 = pd.read_csv(KC_2013_PATH, low_memory=False)
    
    df_kc_2013["sid"] = df_kc_2013["nces_school_id"].astype(str).str.zfill(12)
    df_kc_long["sid"] = df_kc_long["nces_school_id"].astype(str).str.zfill(12)
    
    kc_meta = {}
    kc_sids = set(df_kc_long["sid"]).union(set(df_kc_2013["sid"]))
    
    for _, r in df_kc_2013.iterrows():
        ptr = r.get("school_ptr")
        kc_meta[(r["sid"], "2013-2014")] = {
            "county_fips": str(r.get("county_fips", "")).zfill(5),
            "county_name": str(r.get("county_name", "")),
            "locale_group": str(r.get("locale_group", "Unknown")),
            "school_level": str(r.get("school_level", "Other")),
            "school_ptr": float(ptr) if pd.notna(ptr) and float(ptr) > 0 and float(ptr) <= 50 else np.nan,
        }
    for _, r in df_kc_long.iterrows():
        ptr = r.get("students_per_classroom_teacher_fte_allgrades")
        kc_meta[(r["sid"], str(r["school_year"]))] = {
            "county_fips": str(r.get("county_fips", "")).zfill(5),
            "county_name": str(r.get("county_name", "")),
            "locale_group": str(r.get("locale_group_year", r.get("locale_group", "Unknown"))),
            "school_level": str(r.get("school_level", "Other")),
            "school_ptr": float(ptr) if pd.notna(ptr) and float(ptr) > 0 and float(ptr) <= 50 else np.nan,
        }
    return kc_sids, kc_meta


def extract_wave_2013_14():
    """Extract 2013-14 school context metrics with intermediate disk caching."""
    cache_path = DATA_INTERMEDIATE / "school_context_2013_14.parquet"
    if cache_path.exists():
        print(f"--> [Cache Hit] Loading 2013-14 context from {cache_path}")
        return pd.read_parquet(cache_path)

    print("--> Extracting 2013-14 CRDC context from raw Excel files...")
    t0 = time.time()
    raw_dir = RAW_CRDC_DIR / "2013-2014"
    
    # 1. Enrollment and Demographics
    f_enr = raw_dir / "03 Enrollment.xlsx"
    usecols_enr = [
        "COMBOKEY", "LEAID", "SCHID", "LEA_STATE", "SCH_NAME", "LEA_NAME",
        "TOT_ENR_M", "TOT_ENR_F",
        "SCH_ENR_IDEA_M", "SCH_ENR_IDEA_F",
        "SCH_ENR_504_M", "SCH_ENR_504_F",
        "SCH_ENR_LEP_M", "SCH_ENR_LEP_F",
    ]
    df_enr = pd.read_excel(f_enr, usecols=usecols_enr)
    sids = clean_combokey(df_enr["COMBOKEY"])
    
    tot_enr = sum_clean_series(df_enr["TOT_ENR_M"], df_enr["TOT_ENR_F"], require_complete=True)
    idea_cnt = sum_clean_series(df_enr["SCH_ENR_IDEA_M"], df_enr["SCH_ENR_IDEA_F"], require_complete=True)
    s504_cnt = sum_clean_series(df_enr["SCH_ENR_504_M"], df_enr["SCH_ENR_504_F"], require_complete=True)
    el_cnt = sum_clean_series(df_enr["SCH_ENR_LEP_M"], df_enr["SCH_ENR_LEP_F"], require_complete=True)

    df_base = pd.DataFrame({
        "nces_school_id": sids,
        "nces_lea_id": df_enr["LEAID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(7),
        "school_year": "2013-2014",
        "crdc_wave": "2013-14",
        "state": df_enr["LEA_STATE"].astype(str).str.strip(),
        "school_name": df_enr["SCH_NAME"].astype(str).str.strip(),
        "district_name": df_enr["LEA_NAME"].astype(str).str.strip(),
        "school_enrollment": tot_enr,
        "idea_count": idea_cnt,
        "sec504_count": s504_cnt,
        "el_count": el_cnt,
    })

    # 2. Chronic Absenteeism (CRDC 15+ Days Regime)
    f_abs = raw_dir / "09-1 Chronic Absenteeism.xlsx"
    df_abs = pd.read_excel(f_abs, usecols=["COMBOKEY", "TOT_ABSENT_M", "TOT_ABSENT_F"])
    sids_abs = clean_combokey(df_abs["COMBOKEY"])
    tot_abs = sum_clean_series(df_abs["TOT_ABSENT_M"], df_abs["TOT_ABSENT_F"], require_complete=True)
    map_abs = dict(zip(sids_abs, tot_abs))
    df_base["crdc_absent_15d_count"] = df_base["nces_school_id"].map(map_abs)
    df_base["edfacts_absent_10pct_count"] = np.nan
    df_base["chronic_absent_count"] = df_base["crdc_absent_15d_count"]
    df_base["chronic_absent_regime"] = "crdc_15d"

    # 3. Staffing & Teachers
    f_supp = raw_dir / "08-1 School Support and Security Staff (required elements).xlsx"
    df_supp = pd.read_excel(f_supp, usecols=["COMBOKEY", "SCH_FTETEACH_TOT", "SCH_FTECOUNSELORS", "SCH_FTETEACH_ABSENT"])
    sids_supp = clean_combokey(df_supp["COMBOKEY"])
    map_fte = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_TOT"])))
    map_couns = dict(zip(sids_supp, clean_series(df_supp["SCH_FTECOUNSELORS"])))
    map_tch_abs = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_ABSENT"])))
    
    df_base["school_teachers_fte"] = df_base["nces_school_id"].map(map_fte)
    df_base["counselors_fte"] = df_base["nces_school_id"].map(map_couns)
    df_base["teachers_absent_count"] = df_base["nces_school_id"].map(map_tch_abs)

    # 4. School Characteristics (Grades offered)
    f_char = raw_dir / "01 School Characteristics.xlsx"
    usecols_char = ["COMBOKEY", "SCH_GRADE_G09", "SCH_GRADE_G10", "SCH_GRADE_G11", "SCH_GRADE_G12", "SCH_STATUS_CHARTER", "SCH_STATUS_MAGNET"]
    df_char = pd.read_excel(f_char, usecols=usecols_char)
    sids_char = clean_combokey(df_char["COMBOKEY"])
    is_hs = (
        (df_char["SCH_GRADE_G09"].astype(str).str.upper() == "YES") |
        (df_char["SCH_GRADE_G10"].astype(str).str.upper() == "YES") |
        (df_char["SCH_GRADE_G11"].astype(str).str.upper() == "YES") |
        (df_char["SCH_GRADE_G12"].astype(str).str.upper() == "YES")
    )
    is_charter = df_char["SCH_STATUS_CHARTER"].astype(str).str.upper() == "YES"
    map_hs = dict(zip(sids_char, is_hs))
    map_charter = dict(zip(sids_char, is_charter))
    df_base["is_high_school"] = df_base["nces_school_id"].map(map_hs).fillna(False)
    df_base["is_charter"] = df_base["nces_school_id"].map(map_charter).fillna(False)

    df_base.to_parquet(cache_path, index=False)
    print(f"--> Saved cached 2013-14 context to {cache_path} ({len(df_base)} rows, {time.time()-t0:.1f}s)")
    return df_base


def extract_wave_2015_16():
    """Extract 2015-16 school context metrics with intermediate disk caching."""
    cache_path = DATA_INTERMEDIATE / "school_context_2015_16.parquet"
    if cache_path.exists():
        print(f"--> [Cache Hit] Loading 2015-16 context from {cache_path}")
        return pd.read_parquet(cache_path)

    print("--> Extracting 2015-16 CRDC context from raw monolithic CSV...")
    t0 = time.time()
    fpath = RAW_CRDC_DIR / "2015-2016" / "CRDC 2015-16 School Data.csv"
    
    abs_cols = [
        "SCH_ABSENT_HI_M", "SCH_ABSENT_HI_F", "SCH_ABSENT_AM_M", "SCH_ABSENT_AM_F",
        "SCH_ABSENT_AS_M", "SCH_ABSENT_AS_F", "SCH_ABSENT_HP_M", "SCH_ABSENT_HP_F",
        "SCH_ABSENT_BL_M", "SCH_ABSENT_BL_F", "SCH_ABSENT_WH_M", "SCH_ABSENT_WH_F",
        "SCH_ABSENT_TR_M", "SCH_ABSENT_TR_F"
    ]
    usecols = [
        "COMBOKEY", "LEAID", "SCHID", "LEA_STATE", "SCH_NAME", "LEA_NAME",
        "TOT_ENR_M", "TOT_ENR_F",
        "SCH_ENR_IDEA_M", "SCH_ENR_IDEA_F",
        "SCH_ENR_504_M", "SCH_ENR_504_F",
        "SCH_ENR_LEP_M", "SCH_ENR_LEP_F",
        "SCH_FTETEACH_TOT", "SCH_FTECOUNSELORS", "SCH_FTETEACH_ABSENT",
        "SCH_GRADE_G09", "SCH_GRADE_G10", "SCH_GRADE_G11", "SCH_GRADE_G12",
        "SCH_STATUS_CHARTER"
    ] + abs_cols
    
    df = pd.read_csv(fpath, usecols=usecols, encoding="latin1", low_memory=False)
    sids = clean_combokey(df["COMBOKEY"], df["LEAID"], df["SCHID"])
    
    tot_enr = sum_clean_series(df["TOT_ENR_M"], df["TOT_ENR_F"], require_complete=True)
    idea_cnt = sum_clean_series(df["SCH_ENR_IDEA_M"], df["SCH_ENR_IDEA_F"], require_complete=True)
    s504_cnt = sum_clean_series(df["SCH_ENR_504_M"], df["SCH_ENR_504_F"], require_complete=True)
    el_cnt = sum_clean_series(df["SCH_ENR_LEP_M"], df["SCH_ENR_LEP_F"], require_complete=True)
    tot_abs = sum_clean_series(*[df[c] for c in abs_cols], require_complete=True)

    is_hs = (
        (df["SCH_GRADE_G09"].astype(str).str.upper() == "YES") |
        (df["SCH_GRADE_G10"].astype(str).str.upper() == "YES") |
        (df["SCH_GRADE_G11"].astype(str).str.upper() == "YES") |
        (df["SCH_GRADE_G12"].astype(str).str.upper() == "YES")
    )
    is_charter = df["SCH_STATUS_CHARTER"].astype(str).str.upper() == "YES"

    df_out = pd.DataFrame({
        "nces_school_id": sids,
        "nces_lea_id": df["LEAID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(7),
        "school_year": "2015-2016",
        "crdc_wave": "2015-16",
        "state": df["LEA_STATE"].astype(str).str.strip(),
        "school_name": df["SCH_NAME"].astype(str).str.strip(),
        "district_name": df["LEA_NAME"].astype(str).str.strip(),
        "school_enrollment": tot_enr,
        "idea_count": idea_cnt,
        "sec504_count": s504_cnt,
        "el_count": el_cnt,
        "crdc_absent_15d_count": tot_abs,
        "edfacts_absent_10pct_count": np.nan,
        "chronic_absent_count": tot_abs,
        "chronic_absent_regime": "crdc_15d",
        "school_teachers_fte": clean_series(df["SCH_FTETEACH_TOT"]),
        "counselors_fte": clean_series(df["SCH_FTECOUNSELORS"]),
        "teachers_absent_count": clean_series(df["SCH_FTETEACH_ABSENT"]),
        "is_high_school": is_hs,
        "is_charter": is_charter,
    })

    df_out.to_parquet(cache_path, index=False)
    print(f"--> Saved cached 2015-16 context to {cache_path} ({len(df_out)} rows, {time.time()-t0:.1f}s)")
    return df_out


def extract_wave_2017_18():
    """Extract 2017-18 school context metrics with intermediate disk caching."""
    cache_path = DATA_INTERMEDIATE / "school_context_2017_18.parquet"
    if cache_path.exists():
        print(f"--> [Cache Hit] Loading 2017-18 context from {cache_path}")
        return pd.read_parquet(cache_path)

    print("--> Extracting 2017-18 CRDC context from raw zip...")
    t0 = time.time()
    zp = RAW_CRDC_DIR / "2017-18-crdc-data.zip"
    
    with zipfile.ZipFile(zp) as z:
        # Enrollment
        enr_name = [n for n in z.namelist() if "Enrollment.csv" in n and "Dual" not in n][0]
        usecols_enr = [
            "COMBOKEY", "LEAID", "SCHID", "LEA_STATE", "SCH_NAME", "LEA_NAME",
            "TOT_ENR_M", "TOT_ENR_F",
            "SCH_ENR_IDEA_M", "SCH_ENR_IDEA_F",
            "SCH_ENR_504_M", "SCH_ENR_504_F",
            "SCH_ENR_LEP_M", "SCH_ENR_LEP_F",
        ]
        df_enr = pd.read_csv(z.open(enr_name), usecols=usecols_enr, encoding="latin1", low_memory=False)
        sids = clean_combokey(df_enr["COMBOKEY"])

        tot_enr = sum_clean_series(df_enr["TOT_ENR_M"], df_enr["TOT_ENR_F"], require_complete=True)
        idea_cnt = sum_clean_series(df_enr["SCH_ENR_IDEA_M"], df_enr["SCH_ENR_IDEA_F"], require_complete=True)
        s504_cnt = sum_clean_series(df_enr["SCH_ENR_504_M"], df_enr["SCH_ENR_504_F"], require_complete=True)
        el_cnt = sum_clean_series(df_enr["SCH_ENR_LEP_M"], df_enr["SCH_ENR_LEP_F"], require_complete=True)

        df_out = pd.DataFrame({
            "nces_school_id": sids,
            "nces_lea_id": df_enr["LEAID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(7),
            "school_year": "2017-2018",
            "crdc_wave": "2017-18",
            "state": df_enr["LEA_STATE"].astype(str).str.strip(),
            "school_name": df_enr["SCH_NAME"].astype(str).str.strip(),
            "district_name": df_enr["LEA_NAME"].astype(str).str.strip(),
            "school_enrollment": tot_enr,
            "idea_count": idea_cnt,
            "sec504_count": s504_cnt,
            "el_count": el_cnt,
        })

        # Chronic Absenteeism (EDFacts DG814: >=10% of enrolled days)
        abs_name = [n for n in z.namelist() if "814" in n and n.endswith(".csv")][0]
        df_abs = pd.read_csv(z.open(abs_name), usecols=["NCESSCH", "TOTAL_STUDENTS_REPORTED_M", "TOTAL_STUDENTS_REPORTED_F"], encoding="latin1", low_memory=False)
        sids_abs = clean_combokey(df_abs["NCESSCH"])
        tot_abs = sum_clean_series(df_abs["TOTAL_STUDENTS_REPORTED_M"], df_abs["TOTAL_STUDENTS_REPORTED_F"], require_complete=True)
        map_abs = dict(zip(sids_abs, tot_abs))
        df_out["crdc_absent_15d_count"] = np.nan
        df_out["edfacts_absent_10pct_count"] = df_out["nces_school_id"].map(map_abs)
        df_out["chronic_absent_count"] = df_out["edfacts_absent_10pct_count"]
        df_out["chronic_absent_regime"] = "edfacts_10pct"

        # Staffing
        supp_name = [n for n in z.namelist() if "School Support.csv" in n][0]
        df_supp = pd.read_csv(z.open(supp_name), usecols=["COMBOKEY", "SCH_FTETEACH_TOT", "SCH_FTECOUNSELORS", "SCH_FTETEACH_ABSENT"], encoding="latin1", low_memory=False)
        sids_supp = clean_combokey(df_supp["COMBOKEY"])
        map_fte = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_TOT"])))
        map_couns = dict(zip(sids_supp, clean_series(df_supp["FTECOUNSELORS"] if "FTECOUNSELORS" in df_supp.columns else df_supp["SCH_FTECOUNSELORS"])))
        map_tch_abs = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_ABSENT"])))
        
        df_out["school_teachers_fte"] = df_out["nces_school_id"].map(map_fte)
        df_out["counselors_fte"] = df_out["nces_school_id"].map(map_couns)
        df_out["teachers_absent_count"] = df_out["nces_school_id"].map(map_tch_abs)

        # Characteristics
        char_name = [n for n in z.namelist() if "School Characteristics.csv" in n][0]
        df_char = pd.read_csv(z.open(char_name), usecols=["COMBOKEY", "SCH_GRADE_G09", "SCH_GRADE_G10", "SCH_GRADE_G11", "SCH_GRADE_G12", "SCH_STATUS_CHARTER"], encoding="latin1", low_memory=False)
        sids_char = clean_combokey(df_char["COMBOKEY"])
        is_hs = (
            (df_char["SCH_GRADE_G09"].astype(str).str.upper() == "YES") |
            (df_char["SCH_GRADE_G10"].astype(str).str.upper() == "YES") |
            (df_char["SCH_GRADE_G11"].astype(str).str.upper() == "YES") |
            (df_char["SCH_GRADE_G12"].astype(str).str.upper() == "YES")
        )
        is_charter = df_char["SCH_STATUS_CHARTER"].astype(str).str.upper() == "YES"
        df_out["is_high_school"] = df_out["nces_school_id"].map(dict(zip(sids_char, is_hs))).fillna(False)
        df_out["is_charter"] = df_out["nces_school_id"].map(dict(zip(sids_char, is_charter))).fillna(False)

    df_out.to_parquet(cache_path, index=False)
    print(f"--> Saved cached 2017-18 context to {cache_path} ({len(df_out)} rows, {time.time()-t0:.1f}s)")
    return df_out


def extract_wave_2020_21():
    """Extract 2020-21 school context metrics with intermediate disk caching."""
    cache_path = DATA_INTERMEDIATE / "school_context_2020_21.parquet"
    if cache_path.exists():
        print(f"--> [Cache Hit] Loading 2020-21 context from {cache_path}")
        return pd.read_parquet(cache_path)

    print("--> Extracting 2020-21 CRDC context from raw zip...")
    t0 = time.time()
    zp = RAW_CRDC_DIR / "2020-21-crdc-data.zip"
    
    with zipfile.ZipFile(zp) as z:
        # Enrollment
        enr_name = [n for n in z.namelist() if "Enrollment.csv" in n and "Dual" not in n][0]
        usecols_enr = [
            "COMBOKEY", "LEAID", "SCHID", "LEA_STATE", "SCH_NAME", "LEA_NAME",
            "TOT_ENR_M", "TOT_ENR_F",
            "SCH_ENR_IDEA_M", "SCH_ENR_IDEA_F",
            "SCH_ENR_504_M", "SCH_ENR_504_F",
            "SCH_ENR_LEP_M", "SCH_ENR_LEP_F",
        ]
        df_enr = pd.read_csv(z.open(enr_name), usecols=usecols_enr, encoding="latin1", low_memory=False)
        sids = clean_combokey(df_enr["COMBOKEY"])

        tot_enr = sum_clean_series(df_enr["TOT_ENR_M"], df_enr["TOT_ENR_F"], require_complete=True)
        idea_cnt = sum_clean_series(df_enr["SCH_ENR_IDEA_M"], df_enr["SCH_ENR_IDEA_F"], require_complete=True)
        s504_cnt = sum_clean_series(df_enr["SCH_ENR_504_M"], df_enr["SCH_ENR_504_F"], require_complete=True)
        el_cnt = sum_clean_series(df_enr["SCH_ENR_LEP_M"], df_enr["SCH_ENR_LEP_F"], require_complete=True)

        df_out = pd.DataFrame({
            "nces_school_id": sids,
            "nces_lea_id": df_enr["LEAID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(7),
            "school_year": "2020-2021",
            "crdc_wave": "2020-21",
            "state": df_enr["LEA_STATE"].astype(str).str.strip(),
            "school_name": df_enr["SCH_NAME"].astype(str).str.strip(),
            "district_name": df_enr["LEA_NAME"].astype(str).str.strip(),
            "school_enrollment": tot_enr,
            "idea_count": idea_cnt,
            "sec504_count": s504_cnt,
            "el_count": el_cnt,
        })

        # Chronic Absenteeism (EDFacts DG814: >=10% of enrolled days; Note: ~6% reporting due to federal COVID waivers)
        abs_name = [n for n in z.namelist() if "814" in n and n.endswith(".csv")][0]
        df_abs = pd.read_csv(z.open(abs_name), encoding="latin1", low_memory=False)
        sids_abs = clean_combokey(df_abs["NCESSCH"])
        abs_cols = [c for c in df_abs.columns if c.startswith("SCH_ABSENT_") and (c.endswith("_M") or c.endswith("_F")) and not any(k in c for k in ["IDEA", "504", "LEP", "HMENRL"])]
        tot_abs = sum_clean_series(*[df_abs[c] for c in abs_cols], require_complete=True)
        map_abs = dict(zip(sids_abs, tot_abs))
        df_out["crdc_absent_15d_count"] = np.nan
        df_out["edfacts_absent_10pct_count"] = df_out["nces_school_id"].map(map_abs)
        df_out["chronic_absent_count"] = df_out["edfacts_absent_10pct_count"]
        df_out["chronic_absent_regime"] = "edfacts_10pct"

        # Staffing
        supp_name = [n for n in z.namelist() if "School Support.csv" in n][0]
        df_supp = pd.read_csv(z.open(supp_name), encoding="latin1", low_memory=False)
        sids_supp = clean_combokey(df_supp["COMBOKEY"])
        map_fte = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_TOT"]))) if "SCH_FTETEACH_TOT" in df_supp.columns else {}
        map_couns = dict(zip(sids_supp, clean_series(df_supp["SCH_FTECOUNSELORS"]))) if "SCH_FTECOUNSELORS" in df_supp.columns else {}
        map_tch_abs = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_ABSENT"]))) if "SCH_FTETEACH_ABSENT" in df_supp.columns else {}
        
        df_out["school_teachers_fte"] = df_out["nces_school_id"].map(map_fte)
        df_out["counselors_fte"] = df_out["nces_school_id"].map(map_couns)
        df_out["teachers_absent_count"] = df_out["nces_school_id"].map(map_tch_abs)

        # Characteristics
        char_name = [n for n in z.namelist() if "School Characteristics.csv" in n][0]
        df_char = pd.read_csv(z.open(char_name), usecols=["COMBOKEY", "SCH_GRADE_G09", "SCH_GRADE_G10", "SCH_GRADE_G11", "SCH_GRADE_G12", "SCH_STATUS_CHARTER"], encoding="latin1", low_memory=False)
        sids_char = clean_combokey(df_char["COMBOKEY"])
        is_hs = (
            (df_char["SCH_GRADE_G09"].astype(str).str.upper() == "YES") |
            (df_char["SCH_GRADE_G10"].astype(str).str.upper() == "YES") |
            (df_char["SCH_GRADE_G11"].astype(str).str.upper() == "YES") |
            (df_char["SCH_GRADE_G12"].astype(str).str.upper() == "YES")
        )
        is_charter = df_char["SCH_STATUS_CHARTER"].astype(str).str.upper() == "YES"
        df_out["is_high_school"] = df_out["nces_school_id"].map(dict(zip(sids_char, is_hs))).fillna(False)
        df_out["is_charter"] = df_out["nces_school_id"].map(dict(zip(sids_char, is_charter))).fillna(False)

    df_out.to_parquet(cache_path, index=False)
    print(f"--> Saved cached 2020-21 context to {cache_path} ({len(df_out)} rows, {time.time()-t0:.1f}s)")
    return df_out


def extract_wave_2021_22():
    """Extract 2021-22 school context metrics with intermediate disk caching."""
    cache_path = DATA_INTERMEDIATE / "school_context_2021_22.parquet"
    if cache_path.exists():
        print(f"--> [Cache Hit] Loading 2021-22 context from {cache_path}")
        return pd.read_parquet(cache_path)

    print("--> Extracting 2021-22 CRDC context and EDFacts absenteeism...")
    t0 = time.time()
    wave_dir = RAW_CRDC_DIR / "2021-2022"
    
    # 1. Enrollment & Demographics
    f_enr = wave_dir / "Enrollment.csv"
    usecols_enr = [
        "COMBOKEY", "LEAID", "SCHID", "LEA_STATE", "SCH_NAME", "LEA_NAME",
        "TOT_ENR_M", "TOT_ENR_F", "TOT_ENR_X",
        "SCH_ENR_IDEA_M", "SCH_ENR_IDEA_F", "SCH_ENR_IDEA_X",
        "SCH_ENR_504_M", "SCH_ENR_504_F", "SCH_ENR_504_X",
        "SCH_ENR_EL_M", "SCH_ENR_EL_F", "SCH_ENR_EL_X",
    ]
    df_enr = pd.read_csv(f_enr, usecols=usecols_enr, encoding="latin1", low_memory=False)
    sids = clean_combokey(df_enr["COMBOKEY"])

    tot_enr = sum_enrollment_with_nonbinary(df_enr["TOT_ENR_M"], df_enr["TOT_ENR_F"], df_enr.get("TOT_ENR_X"), require_complete=True)
    idea_cnt = sum_enrollment_with_nonbinary(df_enr["SCH_ENR_IDEA_M"], df_enr["SCH_ENR_IDEA_F"], df_enr.get("SCH_ENR_IDEA_X"), require_complete=True)
    s504_cnt = sum_enrollment_with_nonbinary(df_enr["SCH_ENR_504_M"], df_enr["SCH_ENR_504_F"], df_enr.get("SCH_ENR_504_X"), require_complete=True)
    el_cnt = sum_enrollment_with_nonbinary(df_enr["SCH_ENR_EL_M"], df_enr["SCH_ENR_EL_F"], df_enr.get("SCH_ENR_EL_X"), require_complete=True)

    df_out = pd.DataFrame({
        "nces_school_id": sids,
        "nces_lea_id": df_enr["LEAID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(7),
        "school_year": "2021-2022",
        "crdc_wave": "2021-22",
        "state": df_enr["LEA_STATE"].astype(str).str.strip(),
        "school_name": df_enr["SCH_NAME"].astype(str).str.strip(),
        "district_name": df_enr["LEA_NAME"].astype(str).str.strip(),
        "school_enrollment": tot_enr,
        "idea_count": idea_cnt,
        "sec504_count": s504_cnt,
        "el_count": el_cnt,
    })

    # 2. Chronic Absenteeism from EDFacts DG814 (>=10% of enrolled days)
    z_edf = RAW_EDFACTS_DIR / "edfacts_chronic_absenteeism_2021_22.zip"
    if z_edf.exists():
        with zipfile.ZipFile(z_edf) as z:
            df_edf = pd.read_csv(z.open("SY2122_FS195_DG814_SCH_110124.csv"), encoding="latin1", low_memory=False)
            df_sub = df_edf[df_edf["SUBGROUP"] == "ALLSCH"].copy()
            sids_edf = clean_combokey(df_sub["NCES_SCH"])
            map_abs = dict(zip(sids_edf, clean_series(df_sub["NUMERIC_VALUE"])))
            df_out["edfacts_absent_10pct_count"] = df_out["nces_school_id"].map(map_abs)
    else:
        df_out["edfacts_absent_10pct_count"] = np.nan

    df_out["crdc_absent_15d_count"] = np.nan
    df_out["chronic_absent_count"] = df_out["edfacts_absent_10pct_count"]
    df_out["chronic_absent_regime"] = "edfacts_10pct"

    # 3. Staffing
    f_supp = wave_dir / "School Support.csv"
    df_supp = pd.read_csv(f_supp, encoding="latin1", low_memory=False)
    sids_supp = clean_combokey(df_supp["COMBOKEY"])
    map_fte = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_TOT"]))) if "SCH_FTETEACH_TOT" in df_supp.columns else {}
    map_couns = dict(zip(sids_supp, clean_series(df_supp["SCH_FTECOUNSELORS"]))) if "SCH_FTECOUNSELORS" in df_supp.columns else {}
    map_tch_abs = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_ABSENT"]))) if "SCH_FTETEACH_ABSENT" in df_supp.columns else {}
    
    df_out["school_teachers_fte"] = df_out["nces_school_id"].map(map_fte)
    df_out["counselors_fte"] = df_out["nces_school_id"].map(map_couns)
    df_out["teachers_absent_count"] = df_out["nces_school_id"].map(map_tch_abs)

    # 4. Characteristics
    f_char = wave_dir / "School Characteristics.csv"
    df_char = pd.read_csv(f_char, usecols=["COMBOKEY", "SCH_GRADE_G09", "SCH_GRADE_G10", "SCH_GRADE_G11", "SCH_GRADE_G12", "SCH_STATUS_CHARTER"], encoding="latin1", low_memory=False)
    sids_char = clean_combokey(df_char["COMBOKEY"])
    is_hs = (
        (df_char["SCH_GRADE_G09"].astype(str).str.upper() == "YES") |
        (df_char["SCH_GRADE_G10"].astype(str).str.upper() == "YES") |
        (df_char["SCH_GRADE_G11"].astype(str).str.upper() == "YES") |
        (df_char["SCH_GRADE_G12"].astype(str).str.upper() == "YES")
    )
    is_charter = df_char["SCH_STATUS_CHARTER"].astype(str).str.upper() == "YES"
    df_out["is_high_school"] = df_out["nces_school_id"].map(dict(zip(sids_char, is_hs))).fillna(False)
    df_out["is_charter"] = df_out["nces_school_id"].map(dict(zip(sids_char, is_charter))).fillna(False)

    df_out.to_parquet(cache_path, index=False)
    print(f"--> Saved cached 2021-22 context to {cache_path} ({len(df_out)} rows, {time.time()-t0:.1f}s)")
    return df_out


def extract_wave_2023_24():
    """Extract 2023-24 school context metrics with intermediate disk caching."""
    cache_path = DATA_INTERMEDIATE / "school_context_2023_24.parquet"
    if cache_path.exists():
        print(f"--> [Cache Hit] Loading 2023-24 context from {cache_path}")
        return pd.read_parquet(cache_path)

    print("--> Extracting 2023-24 CRDC context from raw zip...")
    t0 = time.time()
    zp = RAW_CRDC_DIR / "2023-24-crdc-data.zip"
    
    with zipfile.ZipFile(zp) as z:
        # Enrollment
        enr_name = [n for n in z.namelist() if "Enrollment.csv" in n and "Dual" not in n][0]
        usecols_enr = [
            "COMBOKEY", "LEAID", "SCHID", "LEA_STATE", "SCH_NAME", "LEA_NAME",
            "TOT_ENR_M", "TOT_ENR_F", "TOT_ENR_X",
            "SCH_ENR_IDEA_M", "SCH_ENR_IDEA_F", "SCH_ENR_IDEA_X",
            "SCH_ENR_504_M", "SCH_ENR_504_F", "SCH_ENR_504_X",
            "SCH_ENR_EL_M", "SCH_ENR_EL_F", "SCH_ENR_EL_X",
        ]
        df_enr = pd.read_csv(z.open(enr_name), usecols=usecols_enr, encoding="latin1", low_memory=False)
        sids = clean_combokey(df_enr["COMBOKEY"])

        tot_enr = sum_enrollment_with_nonbinary(df_enr["TOT_ENR_M"], df_enr["TOT_ENR_F"], df_enr.get("TOT_ENR_X"), require_complete=True)
        idea_cnt = sum_enrollment_with_nonbinary(df_enr["SCH_ENR_IDEA_M"], df_enr["SCH_ENR_IDEA_F"], df_enr.get("SCH_ENR_IDEA_X"), require_complete=True)
        s504_cnt = sum_enrollment_with_nonbinary(df_enr["SCH_ENR_504_M"], df_enr["SCH_ENR_504_F"], df_enr.get("SCH_ENR_504_X"), require_complete=True)
        el_cnt = sum_enrollment_with_nonbinary(df_enr["SCH_ENR_EL_M"], df_enr["SCH_ENR_EL_F"], df_enr.get("SCH_ENR_EL_X"), require_complete=True)

        df_out = pd.DataFrame({
            "nces_school_id": sids,
            "nces_lea_id": df_enr["LEAID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(7),
            "school_year": "2023-2024",
            "crdc_wave": "2023-24",
            "state": df_enr["LEA_STATE"].astype(str).str.strip(),
            "school_name": df_enr["SCH_NAME"].astype(str).str.strip(),
            "district_name": df_enr["LEA_NAME"].astype(str).str.strip(),
            "school_enrollment": tot_enr,
            "idea_count": idea_cnt,
            "sec504_count": s504_cnt,
            "el_count": el_cnt,
            "crdc_absent_15d_count": np.nan,
            "edfacts_absent_10pct_count": np.nan,
            "chronic_absent_count": np.nan,  # Not published in public 2023-24 CRDC files
            "chronic_absent_regime": None,
        })

        # Staffing
        supp_name = [n for n in z.namelist() if "School Support.csv" in n][0]
        df_supp = pd.read_csv(z.open(supp_name), usecols=["COMBOKEY", "SCH_FTETEACH_TOT", "SCH_FTECOUNSELORS", "SCH_FTETEACH_ABSENT"], encoding="latin1", low_memory=False)
        sids_supp = clean_combokey(df_supp["COMBOKEY"])
        map_fte = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_TOT"])))
        map_couns = dict(zip(sids_supp, clean_series(df_supp["SCH_FTECOUNSELORS"])))
        map_tch_abs = dict(zip(sids_supp, clean_series(df_supp["SCH_FTETEACH_ABSENT"])))
        
        df_out["school_teachers_fte"] = df_out["nces_school_id"].map(map_fte)
        df_out["counselors_fte"] = df_out["nces_school_id"].map(map_couns)
        df_out["teachers_absent_count"] = df_out["nces_school_id"].map(map_tch_abs)

        # Characteristics
        char_name = [n for n in z.namelist() if "School Characteristics.csv" in n][0]
        df_char = pd.read_csv(z.open(char_name), usecols=["COMBOKEY", "SCH_GRADE_G09", "SCH_GRADE_G10", "SCH_GRADE_G11", "SCH_GRADE_G12", "SCH_STATUS_CHARTER"], encoding="latin1", low_memory=False)
        sids_char = clean_combokey(df_char["COMBOKEY"])
        is_hs = (
            (df_char["SCH_GRADE_G09"].astype(str).str.upper() == "YES") |
            (df_char["SCH_GRADE_G10"].astype(str).str.upper() == "YES") |
            (df_char["SCH_GRADE_G11"].astype(str).str.upper() == "YES") |
            (df_char["SCH_GRADE_G12"].astype(str).str.upper() == "YES")
        )
        is_charter = df_char["SCH_STATUS_CHARTER"].astype(str).str.upper() == "YES"
        df_out["is_high_school"] = df_out["nces_school_id"].map(dict(zip(sids_char, is_hs))).fillna(False)
        df_out["is_charter"] = df_out["nces_school_id"].map(dict(zip(sids_char, is_charter))).fillna(False)

    df_out.to_parquet(cache_path, index=False)
    print(f"--> Saved cached 2023-24 context to {cache_path} ({len(df_out)} rows, {time.time()-t0:.1f}s)")
    return df_out


def build_school_context_panel():
    """Main execution function to construct school_context_panel.parquet."""
    print("=" * 70)
    print("CONSTRUCTING LONGITUDINAL SCHOOL CONTEXT & INSTRUCTIONAL LOAD PANEL (STUDY B)")
    print("=" * 70)
    t_start = time.time()
    
    # 1. Extract and harmonize all 6 waves
    df13 = extract_wave_2013_14()
    df15 = extract_wave_2015_16()
    df17 = extract_wave_2017_18()
    df20 = extract_wave_2020_21()
    df21 = extract_wave_2021_22()
    df23 = extract_wave_2023_24()
    
    print("\n--> Concatenating all 6 waves...")
    panel = pd.concat([df13, df15, df17, df20, df21, df23], ignore_index=True)
    print(f"Total school-wave records: {len(panel):,}")
    
    # 2. Derive percentage shares and operational ratios
    # Rates must strictly divide by valid positive school enrollment
    valid_enr_mask = panel["school_enrollment"].notna() & (panel["school_enrollment"] > 0)
    
    panel["pct_idea"] = np.where(valid_enr_mask & panel["idea_count"].notna(), (panel["idea_count"] / panel["school_enrollment"]) * 100.0, np.nan)
    panel["pct_sec504"] = np.where(valid_enr_mask & panel["sec504_count"].notna(), (panel["sec504_count"] / panel["school_enrollment"]) * 100.0, np.nan)
    
    # Combined IDEA or Section 504-only
    both_valid = panel["idea_count"].notna() & panel["sec504_count"].notna()
    panel["idea_or_504_count"] = np.where(both_valid, panel["idea_count"] + panel["sec504_count"], np.nan)
    panel["pct_idea_or_504"] = np.where(valid_enr_mask & both_valid, (panel["idea_or_504_count"] / panel["school_enrollment"]) * 100.0, np.nan)

    panel["pct_el"] = np.where(valid_enr_mask & panel["el_count"].notna(), (panel["el_count"] / panel["school_enrollment"]) * 100.0, np.nan)
    
    # Distinct Chronic Absenteeism Regimes
    panel["pct_crdc_absent_15d"] = np.where(valid_enr_mask & panel["crdc_absent_15d_count"].notna(), (panel["crdc_absent_15d_count"] / panel["school_enrollment"]) * 100.0, np.nan)
    panel["pct_edfacts_absent_10pct"] = np.where(valid_enr_mask & panel["edfacts_absent_10pct_count"].notna(), (panel["edfacts_absent_10pct_count"] / panel["school_enrollment"]) * 100.0, np.nan)
    
    # Flags: Denominator discordance (cumulative 12-month count > October snapshot enrollment)
    panel["flag_absent_gt_enrollment"] = np.where(
        panel["chronic_absent_count"].notna() & valid_enr_mask,
        panel["chronic_absent_count"] > panel["school_enrollment"],
        False
    )
    # Waiver flag for 2020-21 COVID wave (~6% reporting)
    panel["is_absent_waiver_year"] = panel["crdc_wave"] == "2020-21"
    
    # Unclipped rate and clean rate
    panel["pct_chronic_absent"] = np.where(valid_enr_mask & panel["chronic_absent_count"].notna(), (panel["chronic_absent_count"] / panel["school_enrollment"]) * 100.0, np.nan)
    panel["pct_chronic_absent_clean"] = np.where(panel["flag_absent_gt_enrollment"], np.nan, panel["pct_chronic_absent"])

    # Staffing PTR and Counselor ratios
    valid_fte_mask = panel["school_teachers_fte"].notna() & (panel["school_teachers_fte"] > 0)
    raw_ptr = np.where(valid_enr_mask & valid_fte_mask, panel["school_enrollment"] / panel["school_teachers_fte"], np.nan)
    panel["school_ptr"] = np.where((raw_ptr > 0) & (raw_ptr <= 50), raw_ptr, np.nan)
    
    valid_couns_mask = panel["counselors_fte"].notna() & (panel["counselors_fte"] > 0)
    panel["student_counselor_ratio"] = np.where(valid_enr_mask & valid_couns_mask, panel["school_enrollment"] / panel["counselors_fte"], np.nan)
    
    panel["pct_teachers_absent"] = np.where(valid_fte_mask & panel["teachers_absent_count"].notna(), np.minimum((panel["teachers_absent_count"] / panel["school_teachers_fte"]) * 100.0, 100.0), np.nan)

    # 3. Add Kansas City Metropolitan Area flags and metadata (including canonical PTR)
    kc_sids, kc_meta = load_kc_metadata()
    panel["is_kc_metro"] = panel["nces_school_id"].isin(kc_sids)
    
    panel["county_fips"] = None
    panel["county_name"] = None
    panel["locale_group"] = None
    panel["school_level"] = None
    
    for idx in panel[panel["is_kc_metro"]].index:
        sid = panel.loc[idx, "nces_school_id"]
        sy = panel.loc[idx, "school_year"]
        meta = kc_meta.get((sid, sy))
        if meta:
            panel.loc[idx, "county_fips"] = meta["county_fips"]
            panel.loc[idx, "county_name"] = meta["county_name"]
            panel.loc[idx, "locale_group"] = meta["locale_group"]
            panel.loc[idx, "school_level"] = meta["school_level"]
            # Carry forward certified canonical PTR from Phase 3 CCD metadata
            if pd.notna(meta.get("school_ptr")):
                panel.loc[idx, "school_ptr"] = meta["school_ptr"]

    # 4. Link with Aggregated School-Level Class Size Metrics
    course_panel_path = DATA_PROCESSED / "crdc_course_panel.parquet"
    if course_panel_path.exists():
        print("--> Linking with canonical CRDC course panel at school-wave level...")
        df_cp = pd.read_parquet(course_panel_path)
        
        # Group by nces_school_id and crdc_wave
        df_cp["enr_times_cs"] = df_cp["num_enrolled"] * df_cp["mean_class_size"]
        grp = df_cp.groupby(["nces_school_id", "crdc_wave"])
        
        cs_agg = grp.agg(
            stem_courses_count=("course_code", "nunique"),
            stem_sections_tot=("num_classes", "sum"),
            stem_enrolled_tot=("num_enrolled", "sum"),
            mean_class_size_cell=("mean_class_size", "mean"),
            enr_times_cs_sum=("enr_times_cs", "sum")
        ).reset_index()
        
        cs_agg["enr_weighted_class_size"] = cs_agg["enr_times_cs_sum"] / cs_agg["stem_enrolled_tot"]
        cs_agg["sec_weighted_class_size"] = cs_agg["stem_enrolled_tot"] / cs_agg["stem_sections_tot"]
        cs_agg["in_class_size_panel"] = True
        
        # Merge onto school context panel
        panel = panel.merge(
            cs_agg[["nces_school_id", "crdc_wave", "stem_courses_count", "stem_sections_tot", "stem_enrolled_tot", "mean_class_size_cell", "sec_weighted_class_size", "enr_weighted_class_size", "in_class_size_panel"]],
            on=["nces_school_id", "crdc_wave"],
            how="left"
        )
        panel["in_class_size_panel"] = panel["in_class_size_panel"].fillna(False)
    else:
        print("Warning: crdc_course_panel.parquet not found for linkage.")
        panel["in_class_size_panel"] = False

    # 5. Define Class Size Bins for Secondary Offerings
    bins = [0, 20, 25, 30, 100]
    labels = ["<20", "20-24", "25-29", "30+"]
    panel["class_size_bin"] = pd.cut(panel["enr_weighted_class_size"], bins=bins, labels=labels, right=False)

    # 6. Save Processed Datasets
    out_parquet = DATA_PROCESSED / "school_context_panel.parquet"
    panel.to_parquet(out_parquet, index=False)
    print(f"\n--> Successfully saved {out_parquet} ({len(panel):,} rows, {out_parquet.stat().st_size / (1024*1024):.2f} MB)")

    # Secondary schools subset (in_class_size_panel or is_high_school)
    sec_mask = panel["in_class_size_panel"] | panel["is_high_school"]
    df_sec = panel[sec_mask].copy()
    out_sec_csv = DATA_PROCESSED / "school_context_secondary_panel.csv"
    df_sec.to_csv(out_sec_csv, index=False)
    print(f"--> Saved secondary school context subset to {out_sec_csv} ({len(df_sec):,} rows)")

    # 7. Generate National Summary by Wave
    print("\n--> Generating National Context Summary by Wave...")
    summary_rows = []
    for w in sorted(panel["crdc_wave"].unique()):
        sub_all = panel[panel["crdc_wave"] == w]
        sub_sec = df_sec[df_sec["crdc_wave"] == w]
        
        sec_enr_tot = sub_sec["school_enrollment"].sum()
        stem_enr_tot = sub_sec["stem_enrolled_tot"].sum()
        
        summary_rows.append({
            "crdc_wave": w,
            "school_year": sub_all["school_year"].iloc[0],
            "total_schools": len(sub_all),
            "secondary_schools": len(sub_sec),
            "schools_in_class_size_panel": sub_all["in_class_size_panel"].sum(),
            "mean_enrollment_secondary": sub_sec["school_enrollment"].mean(),
            "mean_ptr_secondary": sub_sec["school_ptr"].mean(),
            "student_weighted_class_size": (sub_sec["stem_enrolled_tot"] * sub_sec["enr_weighted_class_size"]).sum() / stem_enr_tot if stem_enr_tot > 0 else np.nan,
            "mean_class_size_secondary": sub_sec["enr_weighted_class_size"].mean(),
            "school_mean_pct_idea": sub_sec["pct_idea"].mean(),
            "pooled_pct_idea": sub_sec["idea_count"].sum() / sec_enr_tot * 100.0 if sec_enr_tot > 0 else np.nan,
            "school_mean_pct_504": sub_sec["pct_sec504"].mean(),
            "pooled_pct_504": sub_sec["sec504_count"].sum() / sec_enr_tot * 100.0 if sec_enr_tot > 0 else np.nan,
            "school_mean_pct_idea_or_504": sub_sec["pct_idea_or_504"].mean(),
            "pooled_pct_idea_or_504": sub_sec["idea_or_504_count"].sum() / sec_enr_tot * 100.0 if sec_enr_tot > 0 else np.nan,
            "school_mean_pct_el": sub_sec["pct_el"].mean(),
            "pooled_pct_el": sub_sec["el_count"].sum() / sec_enr_tot * 100.0 if sec_enr_tot > 0 else np.nan,
            "crdc_15d_median": sub_sec["pct_crdc_absent_15d"].median(),
            "crdc_15d_pooled": sub_sec["crdc_absent_15d_count"].sum() / sec_enr_tot * 100.0 if sub_sec["crdc_absent_15d_count"].notna().sum() > 0 else np.nan,
            "crdc_15d_n": sub_sec["pct_crdc_absent_15d"].notna().sum(),
            "edfacts_10pct_median": sub_sec["pct_edfacts_absent_10pct"].median(),
            "edfacts_10pct_clean_median": sub_sec["pct_chronic_absent_clean"].median() if w in ["2017-18", "2020-21", "2021-22"] else np.nan,
            "edfacts_10pct_pooled": sub_sec["edfacts_absent_10pct_count"].sum() / sec_enr_tot * 100.0 if sub_sec["edfacts_absent_10pct_count"].notna().sum() > 0 else np.nan,
            "edfacts_10pct_n": sub_sec["pct_edfacts_absent_10pct"].notna().sum(),
            "absent_gt_enr_n": sub_sec["flag_absent_gt_enrollment"].sum(),
        })
        
    df_summary = pd.DataFrame(summary_rows)
    out_summary = DATA_PROCESSED / "school_context_national_summary.csv"
    df_summary.to_csv(out_summary, index=False)
    print(f"--> Saved National Summary to {out_summary}")
    print(df_summary.to_string(index=False))
    
    print("\n" + "=" * 70)
    print(f"PHASE 4 PANEL CONSTRUCTION COMPLETE IN {time.time()-t_start:.1f}s")
    print("=" * 70)
    return panel

if __name__ == "__main__":
    build_school_context_panel()
