"""
Master Pipeline: Build Harmonized Longitudinal CRDC Course Capacity Panel (Phases 1-2).
Outputs:
- data/processed/crdc_course_panel.parquet
- data/processed/crdc_kc_metro_panel.csv
- data/processed/crdc_national_summary.csv
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
    COURSE_SPECS, KC_COUNTY_FIPS, clean_crdc_val, clean_series,
    sum_clean_series, clean_combokey
)

RAW_CRDC_DIR = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "raw" / "crdc"
RAW_NCES_DIR = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "raw" / "nces"
KC_LONG_PATH = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "processed" / "kc_school_capacity_long_2014_15_2024_25.csv"
KC_2013_PATH = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "processed" / "kc_ccd_school_capacity_2013_14.csv"
KC_CRDC_LONG = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "processed" / "kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv"

DATA_INTERMEDIATE = PROJECT_DIR / "data" / "intermediate"
DATA_PROCESSED = PROJECT_DIR / "data" / "processed"

DATA_INTERMEDIATE.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

def load_kc_metadata():
    """Load Kansas City metropolitan school metadata and contemporaneous PTR."""
    df_kc_long = pd.read_csv(KC_LONG_PATH, low_memory=False)
    df_kc_2013 = pd.read_csv(KC_2013_PATH, low_memory=False)
    
    df_kc_2013["sid"] = df_kc_2013["nces_school_id"].astype(str).str.zfill(12)
    df_kc_long["sid"] = df_kc_long["nces_school_id"].astype(str).str.zfill(12)
    
    kc_meta = {}
    kc_sids = set(df_kc_long["sid"]).union(set(df_kc_2013["sid"]))
    
    for _, r in df_kc_2013.iterrows():
        kc_meta[(r["sid"], "2013-2014")] = {
            "school_ptr": float(r["school_ptr"]) if pd.notna(r.get("school_ptr")) and float(r["school_ptr"]) > 0 else np.nan,
            "school_enrollment": float(r["enrollment_total"]) if pd.notna(r.get("enrollment_total")) else np.nan,
            "school_teachers_fte": float(r["classroom_teacher_fte"]) if pd.notna(r.get("classroom_teacher_fte")) else np.nan,
            "county_fips": str(r.get("county_fips", "")).zfill(5),
            "county_name": str(r.get("county_name", "")),
            "locale_group": str(r.get("locale_group", "Unknown")),
            "school_level": str(r.get("school_level", "Other")),
        }
        
    for _, r in df_kc_long.iterrows():
        sy = str(r["school_year"]).strip()
        ptr = r.get("students_per_classroom_teacher_fte_allgrades")
        kc_meta[(r["sid"], sy)] = {
            "school_ptr": float(ptr) if pd.notna(ptr) and float(ptr) > 0 else np.nan,
            "school_enrollment": float(r["enrollment_k12"]) if pd.notna(r.get("enrollment_k12")) else np.nan,
            "school_teachers_fte": float(r["classroom_teacher_fte"]) if pd.notna(r.get("classroom_teacher_fte")) else np.nan,
            "county_fips": str(r.get("county_fips", "")).zfill(5),
            "county_name": str(r.get("county_name", "")),
            "locale_group": str(r.get("locale_group_year", r.get("locale_group", "Unknown"))),
            "school_level": str(r.get("school_level", "Other")),
        }
        
    return kc_sids, kc_meta

def extract_modular_wave(sy, wave, course_file_map, has_nonbinary=False, zip_name=None):
    """Extract and standardize course records from modular CSV wave."""
    print(f"--> Extracting CRDC wave {wave} ({sy})...")
    wave_dir = RAW_CRDC_DIR / sy
    records = []
    
    # 1. School Support (FTE) and Enrollment for PTR
    school_support = {}
    if zip_name:
        zp = RAW_CRDC_DIR / zip_name
        if zp.exists():
            with zipfile.ZipFile(zp) as z:
                # Find school support
                s_supp_matches = [n for n in z.namelist() if "School Support.csv" in n]
                if s_supp_matches:
                    df_supp = pd.read_csv(z.open(s_supp_matches[0]), encoding="latin1", low_memory=False)
                    sids = clean_combokey(df_supp["COMBOKEY"]) if "COMBOKEY" in df_supp.columns else clean_combokey(None, df_supp["LEAID"], df_supp["SCHID"])
                    ftes = clean_series(df_supp["SCH_FTETEACH_TOT"])
                    school_support["fte"] = dict(zip(sids, ftes))
                    
                s_enr_matches = [n for n in z.namelist() if "Enrollment.csv" in n and "Dual" not in n]
                if s_enr_matches:
                    df_enr = pd.read_csv(z.open(s_enr_matches[0]), encoding="latin1", low_memory=False)
                    sids_enr = clean_combokey(df_enr["COMBOKEY"]) if "COMBOKEY" in df_enr.columns else clean_combokey(None, df_enr["LEAID"], df_enr["SCHID"])
                    if "TOT_ENR_M" in df_enr.columns:
                        if has_nonbinary and "TOT_ENR_X" in df_enr.columns:
                            tot = sum_clean_series(df_enr["TOT_ENR_M"], df_enr["TOT_ENR_F"], df_enr["TOT_ENR_X"], require_complete=True)
                        else:
                            tot = sum_clean_series(df_enr["TOT_ENR_M"], df_enr["TOT_ENR_F"], require_complete=True)
                        school_support["enr"] = dict(zip(sids_enr, tot))

    # 2. Extract each course
    for cspec in COURSE_SPECS:
        ccode = cspec["code"]
        cname = cspec["name"]
        csubj = cspec["subject"]
        clevel = cspec["level"]
        
        fname = course_file_map[ccode]["filename"]
        cls_var = course_file_map[ccode]["classes_var"]
        enr_vars = course_file_map[ccode]["enrollment_vars"]
        
        fpath = wave_dir / fname
        if not fpath.exists():
            continue
            
        try:
            df = pd.read_csv(fpath, encoding="latin1", low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(fpath, encoding="utf-8", low_memory=False)
            
        df.columns = df.columns.str.strip().str.replace('"', '', regex=False).str.strip()
            
        if "COMBOKEY" in df.columns:
            sids = clean_combokey(df["COMBOKEY"])
        else:
            sids = clean_combokey(None, df.get("LEAID"), df.get("SCHID"))
            
        leaids = df["LEAID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(7) if "LEAID" in df.columns else sids.str[:7]
        st = df["LEA_STATE"].astype(str).str.strip() if "LEA_STATE" in df.columns else pd.Series("", index=df.index)
        sname = df["SCH_NAME"].astype(str).str.strip() if "SCH_NAME" in df.columns else pd.Series("", index=df.index)
        leaname = df["LEA_NAME"].astype(str).str.strip() if "LEA_NAME" in df.columns else pd.Series("", index=df.index)
        
        cls_clean = clean_series(df[cls_var]) if cls_var in df.columns else pd.Series(np.nan, index=df.index)
        
        enr_series_list = [df[col] for col in enr_vars if col in df.columns]
        enr_clean = sum_clean_series(*enr_series_list, require_complete=True) if enr_series_list else pd.Series(np.nan, index=df.index)
        
        # Valid active course cells: classes > 0 and enrollment > 0
        active_mask = (cls_clean > 0) & (enr_clean > 0)
        
        sub_df = pd.DataFrame({
            "school_year": sy,
            "crdc_wave": wave,
            "nces_school_id": sids[active_mask],
            "nces_lea_id": leaids[active_mask],
            "school_name": sname[active_mask],
            "district_name": leaname[active_mask],
            "state": st[active_mask],
            "course_code": ccode,
            "course_name": cname,
            "subject": csubj,
            "course_level": clevel,
            "num_classes": cls_clean[active_mask],
            "num_enrolled": enr_clean[active_mask],
        })
        
        # Derive class size
        sub_df["mean_class_size"] = sub_df["num_enrolled"] / sub_df["num_classes"]
        
        # Merge CRDC enrollment and teacher FTE if available
        fte_map = school_support.get("fte", {})
        enr_map = school_support.get("enr", {})
        sub_df["school_enrollment"] = sub_df["nces_school_id"].map(enr_map)
        sub_df["school_teachers_fte"] = sub_df["nces_school_id"].map(fte_map)
        
        # Compute preliminary PTR
        sub_df["school_ptr"] = np.where(
            (sub_df["school_teachers_fte"] > 0) & (sub_df["school_enrollment"] > 0),
            sub_df["school_enrollment"] / sub_df["school_teachers_fte"],
            np.nan
        )
        
        records.append(sub_df)
        
    return pd.concat(records, ignore_index=True) if records else pd.DataFrame()

def extract_2015_16():
    """Extract 2015-16 CRDC wave from single wide CSV."""
    print("--> Extracting CRDC wave 2015-16 (2015-2016)...")
    fpath = RAW_CRDC_DIR / "2015-2016" / "CRDC 2015-16 School Data.csv"
    
    usecols = [
        "COMBOKEY", "LEAID", "SCHID", "LEA_STATE", "SCH_NAME", "LEA_NAME",
        "SCH_MATHCLASSES_ALG", "TOT_ALGENR_GS0910_M", "TOT_ALGENR_GS0910_F", "TOT_ALGENR_GS1112_M", "TOT_ALGENR_GS1112_F",
        "SCH_MATHCLASSES_GEOM", "TOT_GEOM_M", "TOT_GEOM_F",
        "SCH_MATHCLASSES_ALG2", "TOT_MATHENR_ALG2_M", "TOT_MATHENR_ALG2_F",
        "SCH_MATHCLASSES_ADVM", "TOT_MATHENR_ADVM_M", "TOT_MATHENR_ADVM_F",
        "SCH_MATHCLASSES_CALC", "TOT_MATHENR_CALC_M", "TOT_MATHENR_CALC_F",
        "SCH_SCICLASSES_BIOL", "TOT_SCIENR_BIOL_M", "TOT_SCIENR_BIOL_F",
        "SCH_SCICLASSES_CHEM", "TOT_SCIENR_CHEM_M", "TOT_SCIENR_CHEM_F",
        "SCH_SCICLASSES_PHYS", "TOT_SCIENR_PHYS_M", "TOT_SCIENR_PHYS_F",
        "TOT_ENR_M", "TOT_ENR_F", "SCH_FTETEACH_TOT"
    ]
    
    df = pd.read_csv(fpath, encoding="latin1", usecols=usecols, low_memory=False)
    sids = clean_combokey(None, df["LEAID"], df["SCHID"])
    leaids = df["LEAID"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(7)
    st = df["LEA_STATE"].astype(str).str.strip()
    sname = df["SCH_NAME"].astype(str).str.strip()
    leaname = df["LEA_NAME"].astype(str).str.strip()
    
    tot_enr = sum_clean_series(df["TOT_ENR_M"], df["TOT_ENR_F"], require_complete=True)
    tot_fte = clean_series(df["SCH_FTETEACH_TOT"])
    ptr = np.where((tot_fte > 0) & (tot_enr > 0), tot_enr / tot_fte, np.nan)
    
    c_map = {
        "alg1": ("SCH_MATHCLASSES_ALG", ["TOT_ALGENR_GS0910_M", "TOT_ALGENR_GS0910_F", "TOT_ALGENR_GS1112_M", "TOT_ALGENR_GS1112_F"]),
        "geom": ("SCH_MATHCLASSES_GEOM", ["TOT_GEOM_M", "TOT_GEOM_F"]),
        "alg2": ("SCH_MATHCLASSES_ALG2", ["TOT_MATHENR_ALG2_M", "TOT_MATHENR_ALG2_F"]),
        "advm": ("SCH_MATHCLASSES_ADVM", ["TOT_MATHENR_ADVM_M", "TOT_MATHENR_ADVM_F"]),
        "calc": ("SCH_MATHCLASSES_CALC", ["TOT_MATHENR_CALC_M", "TOT_MATHENR_CALC_F"]),
        "bio": ("SCH_SCICLASSES_BIOL", ["TOT_SCIENR_BIOL_M", "TOT_SCIENR_BIOL_F"]),
        "chem": ("SCH_SCICLASSES_CHEM", ["TOT_SCIENR_CHEM_M", "TOT_SCIENR_CHEM_F"]),
        "phys": ("SCH_SCICLASSES_PHYS", ["TOT_SCIENR_PHYS_M", "TOT_SCIENR_PHYS_F"]),
    }
    
    records = []
    for cspec in COURSE_SPECS:
        ccode = cspec["code"]
        cls_var, enr_vars = c_map[ccode]
        
        cls_clean = clean_series(df[cls_var])
        enr_clean = sum_clean_series(*[df[col] for col in enr_vars], require_complete=True)
        
        active_mask = (cls_clean > 0) & (enr_clean > 0)
        
        sub_df = pd.DataFrame({
            "school_year": "2015-2016",
            "crdc_wave": "2015-16",
            "nces_school_id": sids[active_mask],
            "nces_lea_id": leaids[active_mask],
            "school_name": sname[active_mask],
            "district_name": leaname[active_mask],
            "state": st[active_mask],
            "course_code": ccode,
            "course_name": cspec["name"],
            "subject": cspec["subject"],
            "course_level": cspec["level"],
            "num_classes": cls_clean[active_mask],
            "num_enrolled": enr_clean[active_mask],
            "school_enrollment": tot_enr[active_mask],
            "school_teachers_fte": tot_fte[active_mask],
            "school_ptr": ptr[active_mask],
        })
        sub_df["mean_class_size"] = sub_df["num_enrolled"] / sub_df["num_classes"]
        records.append(sub_df)
        
    return pd.concat(records, ignore_index=True)

def extract_2013_14():
    """
    Extract 2013-14 CRDC wave. Uses versioned cached intermediate parquet if present;
    otherwise extracts from 2013-14 Excel files and caches.
    Strict missingness: If any required enrollment component is missing, suppressed (-5),
    or a negative reserve code (-9, -11, etc.), the course enrollment is considered incomplete
    and excluded from active course cells.
    """
    CACHE_VERSION = "v2_strict"
    cache_path = DATA_INTERMEDIATE / f"crdc_2013_14_active_{CACHE_VERSION}.parquet"
    
    # Invalidate and delete unversioned/legacy cache if present
    legacy_cache = DATA_INTERMEDIATE / "crdc_2013_14_active.parquet"
    if legacy_cache.exists():
        try:
            legacy_cache.unlink()
            print(f"--> Invalidated and deleted legacy cache: {legacy_cache}")
        except Exception as e:
            print(f"Warning: could not delete {legacy_cache}: {e}")
            
    if cache_path.exists():
        print(f"--> Loading cached 2013-14 active course records ({CACHE_VERSION}) from intermediate parquet...")
        return pd.read_parquet(cache_path)
        
    print(f"--> Extracting 2013-14 CRDC wave from Excel files with strict missingness ({CACHE_VERSION}, will cache)...")
    import openpyxl
    p = RAW_CRDC_DIR / "2013-2014"
    records = []
    
    # Mapping of courses to Excel files and columns
    files_to_process = [
        ("alg1", p / "05-1 Algebra I Courses and Classes.xlsx", "SCH_ALGCLASSES_GS0712",
         ["TOT_ALGENR_GS0708_M", "TOT_ALGENR_GS0708_F", "TOT_ALGENR_GS0910_M", "TOT_ALGENR_GS0910_F", "TOT_ALGENR_GS1112_M", "TOT_ALGENR_GS1112_F"]),
        ("geom", p / "05-2 Geometry Courses and Classes.xlsx", "SCH_GEOMCLASSES_GS0712",
         ["TOT_GEOMENR_GS0712_M", "TOT_GEOMENR_GS0712_F"]),
        ("alg2", p / "05-3 Other Math Courses and Classes.xlsx", "SCH_MATHCLASSES_ALG2",
         ["TOT_MATHENR_ALG2_M", "TOT_MATHENR_ALG2_F"]),
        ("advm", p / "05-3 Other Math Courses and Classes.xlsx", "SCH_MATHCLASSES_ADVM",
         ["TOT_MATHENR_ADVM_M", "TOT_MATHENR_ADVM_F"]),
        ("calc", p / "05-3 Other Math Courses and Classes.xlsx", "SCH_MATHCLASSES_CALC",
         ["TOT_MATHENR_CALC_M", "TOT_MATHENR_CALC_F"]),
        ("bio", p / "05-4 Biology Courses and Classes.xlsx", "SCH_SCICLASSES_BIOL",
         ["TOT_SCIENR_BIOL_M", "TOT_SCIENR_BIOL_F"]),
        ("chem", p / "05-5 Chemistry Courses and Classes.xlsx", "SCH_SCICLASSES_CHEM",
         ["TOT_SCIENR_CHEM_M", "TOT_SCIENR_CHEM_F"]),
        ("phys", p / "05-6 Physics Courses and Classes.xlsx", "SCH_SCICLASSES_PHYS",
         ["TOT_SCIENR_PHYS_M", "TOT_SCIENR_PHYS_F"]),
    ]
    
    cspec_map = {cs["code"]: cs for cs in COURSE_SPECS}
    
    for ccode, fpath, cls_var, enr_vars in files_to_process:
        cspec = cspec_map[ccode]
        print(f"    Extracting 2013-14 {cspec['name']} with strict missingness...")
        wb = openpyxl.load_workbook(fpath, read_only=True)
        sheet = wb.active
        rows = sheet.iter_rows(values_only=True)
        headers = list(next(rows))
        
        idx_leaid = headers.index("LEAID")
        idx_schid = headers.index("SCHID")
        idx_st = headers.index("LEA_STATE")
        idx_sname = headers.index("SCH_NAME")
        idx_leaname = headers.index("LEA_NAME")
        idx_cls = headers.index(cls_var)
        idx_enr = [headers.index(ev) for ev in enr_vars if ev in headers]
        
        c_recs = []
        for r in rows:
            c_val = r[idx_cls]
            try:
                fc = float(c_val)
                if fc > 0:
                    is_complete = True
                    enr_sum = 0.0
                    for i in idx_enr:
                        val = r[i]
                        if val is None or str(val).strip() == "":
                            is_complete = False
                            break
                        try:
                            fv = float(val)
                            if fv < 0:
                                is_complete = False
                                break
                            enr_sum += fv
                        except (ValueError, TypeError):
                            is_complete = False
                            break
                    if is_complete and enr_sum > 0:
                        sid = str(r[idx_leaid]).zfill(7) + str(r[idx_schid]).zfill(5)
                        lid = str(r[idx_leaid]).zfill(7)
                        c_recs.append({
                            "school_year": "2013-2014",
                            "crdc_wave": "2013-14",
                            "nces_school_id": sid,
                            "nces_lea_id": lid,
                            "school_name": str(r[idx_sname]).strip(),
                            "district_name": str(r[idx_leaname]).strip(),
                            "state": str(r[idx_st]).strip(),
                            "course_code": ccode,
                            "course_name": cspec["name"],
                            "subject": cspec["subject"],
                            "course_level": cspec["level"],
                            "num_classes": fc,
                            "num_enrolled": enr_sum,
                            "mean_class_size": enr_sum / fc,
                            "school_enrollment": np.nan,
                            "school_teachers_fte": np.nan,
                            "school_ptr": np.nan,
                        })
            except (ValueError, TypeError):
                continue
        wb.close()
        records.append(pd.DataFrame(c_recs))
        
    df_1314 = pd.concat(records, ignore_index=True)
    df_1314.to_parquet(cache_path, index=False)
    print(f"--> Saved cached 2013-14 active records to {cache_path} ({len(df_1314)} rows)")
    return df_1314

def main():
    print("=" * 70)
    print("CONSTRUCTING COMPREHENSIVE CRDC LONGITUDINAL COURSE PANEL (2013-14 TO 2023-24)")
    print("=" * 70)
    t0 = time.time()
    
    kc_sids, kc_meta = load_kc_metadata()
    print(f"Loaded {len(kc_sids)} Kansas City school IDs for metro classification.")
    
    # 2023-24
    map_23 = {
        "alg1": {"filename": "Algebra I.csv", "classes_var": "SCH_MATHCLASSES_ALG", "enrollment_vars": ["TOT_ALGENR_GS0910_M", "TOT_ALGENR_GS0910_F", "TOT_ALGENR_GS0910_X", "TOT_ALGENR_GS1112_M", "TOT_ALGENR_GS1112_F", "TOT_ALGENR_GS1112_X"]},
        "geom": {"filename": "Geometry.csv", "classes_var": "SCH_MATHCLASSES_GEOM", "enrollment_vars": ["TOT_MATHENR_GEOM_M", "TOT_MATHENR_GEOM_F", "TOT_MATHENR_GEOM_X"]},
        "alg2": {"filename": "Algebra II.csv", "classes_var": "SCH_MATHCLASSES_ALG2", "enrollment_vars": ["TOT_MATHENR_ALG2_M", "TOT_MATHENR_ALG2_F", "TOT_MATHENR_ALG2_X"]},
        "advm": {"filename": "Advanced Mathematics.csv", "classes_var": "SCH_MATHCLASSES_ADVM", "enrollment_vars": ["TOT_MATHENR_ADVM_M", "TOT_MATHENR_ADVM_F", "TOT_MATHENR_ADVM_X"]},
        "calc": {"filename": "Calculus.csv", "classes_var": "SCH_MATHCLASSES_CALC", "enrollment_vars": ["TOT_MATHENR_CALC_M", "TOT_MATHENR_CALC_F", "TOT_MATHENR_CALC_X"]},
        "bio": {"filename": "Biology.csv", "classes_var": "SCH_SCICLASSES_BIOL", "enrollment_vars": ["TOT_SCIENR_BIOL_M", "TOT_SCIENR_BIOL_F", "TOT_SCIENR_BIOL_X"]},
        "chem": {"filename": "Chemistry.csv", "classes_var": "SCH_SCICLASSES_CHEM", "enrollment_vars": ["TOT_SCIENR_CHEM_M", "TOT_SCIENR_CHEM_F", "TOT_SCIENR_CHEM_X"]},
        "phys": {"filename": "Physics.csv", "classes_var": "SCH_SCICLASSES_PHYS", "enrollment_vars": ["TOT_SCIENR_PHYS_M", "TOT_SCIENR_PHYS_F", "TOT_SCIENR_PHYS_X"]},
    }
    df_23 = extract_modular_wave("2023-2024", "2023-24", map_23, has_nonbinary=True, zip_name="2023-24-crdc-data.zip")
    
    # 2021-22
    map_21 = {
        "alg1": {"filename": "Algebra I.csv", "classes_var": "SCH_MATHCLASSES_ALG", "enrollment_vars": ["TOT_ALGENR_GS0910_M", "TOT_ALGENR_GS0910_F", "TOT_ALGENR_GS1112_M", "TOT_ALGENR_GS1112_F"]},
        "geom": {"filename": "Geometry.csv", "classes_var": "SCH_MATHCLASSES_GEOM", "enrollment_vars": ["TOT_MATHENR_GEOM_M", "TOT_MATHENR_GEOM_F"]},
        "alg2": {"filename": "Algebra II.csv", "classes_var": "SCH_MATHCLASSES_ALG2", "enrollment_vars": ["TOT_MATHENR_ALG2_M", "TOT_MATHENR_ALG2_F"]},
        "advm": {"filename": "Advanced Mathematics.csv", "classes_var": "SCH_MATHCLASSES_ADVM", "enrollment_vars": ["TOT_MATHENR_ADVM_M", "TOT_MATHENR_ADVM_F"]},
        "calc": {"filename": "Calculus.csv", "classes_var": "SCH_MATHCLASSES_CALC", "enrollment_vars": ["TOT_MATHENR_CALC_M", "TOT_MATHENR_CALC_F"]},
        "bio": {"filename": "Biology.csv", "classes_var": "SCH_SCICLASSES_BIOL", "enrollment_vars": ["TOT_SCIENR_BIOL_M", "TOT_SCIENR_BIOL_F"]},
        "chem": {"filename": "Chemistry.csv", "classes_var": "SCH_SCICLASSES_CHEM", "enrollment_vars": ["TOT_SCIENR_CHEM_M", "TOT_SCIENR_CHEM_F"]},
        "phys": {"filename": "Physics.csv", "classes_var": "SCH_SCICLASSES_PHYS", "enrollment_vars": ["TOT_SCIENR_PHYS_M", "TOT_SCIENR_PHYS_F"]},
    }
    df_21 = extract_modular_wave("2021-2022", "2021-22", map_21, has_nonbinary=False, zip_name=None)
    
    # 2020-21
    df_20 = extract_modular_wave("2020-2021", "2020-21", map_21, has_nonbinary=False, zip_name="2020-21-crdc-data.zip")
    
    # 2017-18
    df_17 = extract_modular_wave("2017-2018", "2017-18", map_21, has_nonbinary=False, zip_name="2017-18-crdc-data.zip")
    
    # 2015-16
    df_15 = extract_2015_16()
    
    # 2013-14
    df_13 = extract_2013_14()
    
    print("--> Concatenating all waves...")
    panel = pd.concat([df_13, df_15, df_17, df_20, df_21, df_23], ignore_index=True)
    
    # Flag Kansas City Metropolitan Area
    panel["is_kc_metro"] = panel["nces_school_id"].isin(kc_sids)
    
    # Merge Kansas City contemporaneous CCD metadata and PTR where available
    for idx in panel[panel["is_kc_metro"]].index:
        sid = panel.loc[idx, "nces_school_id"]
        sy = panel.loc[idx, "school_year"]
        meta = kc_meta.get((sid, sy))
        if meta:
            if pd.notna(meta.get("school_ptr")):
                panel.loc[idx, "school_ptr"] = meta["school_ptr"]
            if pd.notna(meta.get("school_enrollment")):
                panel.loc[idx, "school_enrollment"] = meta["school_enrollment"]
            if pd.notna(meta.get("school_teachers_fte")):
                panel.loc[idx, "school_teachers_fte"] = meta["school_teachers_fte"]
            panel.loc[idx, "county_fips"] = meta.get("county_fips")
            panel.loc[idx, "county_name"] = meta.get("county_name")
            panel.loc[idx, "locale_group"] = meta.get("locale_group")
            panel.loc[idx, "school_level"] = meta.get("school_level")
            
    # Calculate Allocation Wedge
    panel["ptr_wedge"] = panel["mean_class_size"] - panel["school_ptr"]
    panel["ptr_wedge_ratio"] = panel["mean_class_size"] / panel["school_ptr"]
    
    # Anomaly flags
    panel["flag_extreme_size"] = panel["mean_class_size"] > 60.0
    panel["flag_singleton_section"] = panel["num_classes"] == 1.0
    
    # Sort
    panel.sort_values(["school_year", "state", "nces_school_id", "course_code"], inplace=True)
    
    # Export Parquet
    parquet_path = DATA_PROCESSED / "crdc_course_panel.parquet"
    panel.to_parquet(parquet_path, index=False)
    print(f"--> Saved harmonized panel to {parquet_path}: {len(panel):,} rows across {panel['crdc_wave'].nunique()} waves.")
    
    # Export Kansas City Metro CSV slice
    kc_slice = panel[panel["is_kc_metro"]].copy()
    kc_path = DATA_PROCESSED / "crdc_kc_metro_panel.csv"
    kc_slice.to_csv(kc_path, index=False)
    print(f"--> Saved KC metro slice to {kc_path}: {len(kc_slice):,} rows.")
    
    # Export National Summary Table
    def get_summary(df_group):
        res = []
        for (w, c), g in df_group.groupby(["crdc_wave", "course_code"]):
            n_schools = g["nces_school_id"].nunique()
            tot_cls = g["num_classes"].sum()
            tot_enr = g["num_enrolled"].sum()
            cs = g["mean_class_size"]
            
            # Weighting schemes
            unwt_mean = cs.mean()
            sec_wt = tot_enr / tot_cls if tot_cls > 0 else np.nan
            seat_wt = (g["num_enrolled"] * cs).sum() / tot_enr if tot_enr > 0 else np.nan
            
            # Distributions
            med = cs.median()
            p25 = cs.quantile(0.25)
            p75 = cs.quantile(0.75)
            p90 = cs.quantile(0.90)
            p95 = cs.quantile(0.95)
            
            # Exposure shares
            sh_under_20 = (cs < 20).mean() * 100
            sh_20_24 = ((cs >= 20) & (cs < 25)).mean() * 100
            sh_25_29 = ((cs >= 25) & (cs < 30)).mean() * 100
            sh_30_34 = ((cs >= 30) & (cs < 35)).mean() * 100
            sh_35_plus = (cs >= 35).mean() * 100
            
            sh_ge_25 = (cs >= 25).mean() * 100
            sh_ge_30 = (cs >= 30).mean() * 100
            sh_ge_35 = (cs >= 35).mean() * 100
            
            # Seat-weighted exposure shares
            seat_ge_25 = (g.loc[cs >= 25, "num_enrolled"].sum() / tot_enr) * 100 if tot_enr > 0 else np.nan
            seat_ge_30 = (g.loc[cs >= 30, "num_enrolled"].sum() / tot_enr) * 100 if tot_enr > 0 else np.nan
            seat_ge_35 = (g.loc[cs >= 35, "num_enrolled"].sum() / tot_enr) * 100 if tot_enr > 0 else np.nan
            
            # Wedge
            g_wedge = g["ptr_wedge"].dropna()
            mean_wedge = g_wedge.mean() if len(g_wedge) > 0 else np.nan
            
            res.append({
                "wave": w,
                "course_code": c,
                "schools_n": n_schools,
                "classes_total": tot_cls,
                "students_enrolled": tot_enr,
                "course_cell_mean": unwt_mean,
                "section_weighted_mean": sec_wt,
                "seat_weighted_mean": seat_wt,
                "median": med,
                "p25": p25,
                "p75": p75,
                "p90": p90,
                "p95": p95,
                "pct_cells_under_20": sh_under_20,
                "pct_cells_20_24": sh_20_24,
                "pct_cells_25_29": sh_25_29,
                "pct_cells_30_34": sh_30_34,
                "pct_cells_35_plus": sh_35_plus,
                "pct_cells_ge_25": sh_ge_25,
                "pct_cells_ge_30": sh_ge_30,
                "pct_cells_ge_35": sh_ge_35,
                "pct_seats_ge_25": seat_ge_25,
                "pct_seats_ge_30": seat_ge_30,
                "pct_seats_ge_35": seat_ge_35,
                "mean_ptr_wedge": mean_wedge,
            })
        return pd.DataFrame(res)

    summary_df = get_summary(panel)
    summary_path = DATA_PROCESSED / "crdc_national_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"--> Saved summary table to {summary_path}: {len(summary_df)} wave-course combinations.")
    
    print(f"PIPELINE COMPLETE in {time.time()-t0:.1f}s.")

if __name__ == "__main__":
    main()
