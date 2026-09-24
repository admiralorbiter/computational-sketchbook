"""
Construct the Kansas City Metropolitan CRDC Course Capacity Panel (2013-14 through 2023-24).
Harmonizes course classes and student enrollment across 6 CRDC collection waves:
2013-14, 2015-16, 2017-18, 2020-21, 2021-22, and 2023-24.

Unit of Analysis:
- Wide panel: one row per school x CRDC survey wave
- Long panel: one row per school x CRDC survey wave x course offering
  (School-Course Aggregates, NOT individual classroom sections)

Estimands:
- School-course average class size: reported students / reported classes
- School-course allocation wedge: school-course average class size - same-school same-year CCD PTR
- Course categorization: Foundation Core vs. Advanced / Specialized

Contemporaneous CCD Alignment:
- 2013-14 matched to same-year 2013-14 CCD school directory & staffing (via Urban Institute)
- 2015-16 through 2023-24 matched to same-year CCD longitudinal panel records
"""

import sys
import os
import csv
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_CRDC_DIR = PROJECT_ROOT / "data" / "raw" / "crdc"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "tables"
LONG_PANEL_PATH = PROCESSED_DIR / "kc_school_capacity_long_2014_15_2024_25.csv"
CCD_2013_PATH = PROCESSED_DIR / "kc_ccd_school_capacity_2013_14.csv"

COURSES = [
    {"code": "alg1", "name": "Algebra I", "subject": "Math", "level": "Foundation Core"},
    {"code": "geom", "name": "Geometry", "subject": "Math", "level": "Foundation Core"},
    {"code": "alg2", "name": "Algebra II", "subject": "Math", "level": "Foundation Core"},
    {"code": "advm", "name": "Advanced Mathematics", "subject": "Math", "level": "Advanced / Specialized"},
    {"code": "calc", "name": "Calculus", "subject": "Math", "level": "Advanced / Specialized"},
    {"code": "bio", "name": "Biology", "subject": "Science", "level": "Foundation Core"},
    {"code": "chem", "name": "Chemistry", "subject": "Science", "level": "Foundation Core"},
    {"code": "phys", "name": "Physics", "subject": "Science", "level": "Advanced / Specialized"},
]

def clean_crdc_val(val):
    """
    Parse numeric CRDC values, converting negative exception/reserve codes to NaN.
    Negative CRDC reserve codes (-1, -2, -3, -5, -9, -11, -12) must never enter arithmetic.
    """
    if pd.isna(val) or val is None or val == "":
        return np.nan
    try:
        f = float(val)
        return f if f >= 0 else np.nan
    except (ValueError, TypeError):
        return np.nan

def sum_clean_parts(*parts):
    """Sum parts if at least one is valid and non-negative; return NaN if all are NaN."""
    clean = [clean_crdc_val(p) for p in parts]
    valid = [p for p in clean if not np.isnan(p)]
    return sum(valid) if valid else np.nan

def load_school_universe_metadata():
    """
    Load school universe and contemporaneous metadata from:
    1. 2013-14 CCD capacity panel (kc_ccd_school_capacity_2013_14.csv)
    2. 2014-15 through 2024-25 longitudinal panel (kc_school_capacity_long_2014_15_2024_25.csv)
    
    Provides exact year-specific metadata and same-year CCD PTR.
    """
    df_long = pd.read_csv(LONG_PANEL_PATH, low_memory=False)
    df_2013 = pd.read_csv(CCD_2013_PATH, low_memory=False)
    
    df_2013["ncessch_str"] = df_2013["nces_school_id"].astype(str).str.zfill(12)
    df_long["ncessch_str"] = df_long["nces_school_id"].astype(str).str.zfill(12)
    
    year_meta_dict = {}
    
    # Ingest 2013-14 CCD
    for _, r in df_2013.iterrows():
        sid = r["ncessch_str"]
        sy = "2013-2014"
        ptr_val = r.get("school_ptr")
        fte_val = r.get("classroom_teacher_fte")
        enr_val = r.get("enrollment_total")
        
        year_meta_dict[(sid, sy)] = {
            "nces_school_id": sid,
            "nces_lea_id": str(r.get("nces_lea_id", "")).zfill(7),
            "school_name": str(r.get("school_name", "")).strip(),
            "district_name": str(r.get("district_name", "")).strip(),
            "lea_name": str(r.get("district_name", "")).strip(),
            "state": str(r.get("state", "")).strip(),
            "county_name": str(r.get("county_name", "")).strip(),
            "county_fips": str(r.get("county_fips", "")).zfill(5),
            "locale_group": str(r.get("locale_group", "Unknown")),
            "school_level": str(r.get("school_level", "Other")),
            "school_type": str(r.get("school_type", "Regular School")),
            "operational_status": r.get("operational_status", 1),
            "is_operating": bool(r.get("is_operating", True)),
            "is_charter": bool(r.get("is_charter", False)),
            "is_virtual": bool(r.get("is_virtual", False)),
            "school_ptr": float(ptr_val) if pd.notna(ptr_val) and float(ptr_val) > 0 else np.nan,
            "enrollment_k12": float(enr_val) if pd.notna(enr_val) and float(enr_val) >= 0 else np.nan,
            "classroom_teacher_fte": float(fte_val) if pd.notna(fte_val) and float(fte_val) > 0 else np.nan,
        }
        
    # Ingest 2014-15 through 2024-25 CCD
    for _, r in df_long.iterrows():
        sid = r["ncessch_str"]
        sy = str(r["school_year"]).strip()
        ptr_val = r.get("students_per_classroom_teacher_fte_allgrades")
        fte_val = r.get("classroom_teacher_fte")
        enr_val = r.get("enrollment_k12")
        
        year_meta_dict[(sid, sy)] = {
            "nces_school_id": sid,
            "nces_lea_id": str(r.get("nces_lea_id", "")).zfill(7),
            "school_name": str(r.get("school_name", "")).strip(),
            "district_name": str(r.get("district_name", r.get("lea_name", ""))).strip(),
            "lea_name": str(r.get("lea_name", "")).strip(),
            "state": str(r.get("state", "")).strip(),
            "county_name": str(r.get("county_name", "")).strip(),
            "county_fips": str(r.get("county_fips", "")).zfill(5),
            "locale_group": str(r.get("locale_group_year", r.get("locale_group", "Unknown"))),
            "school_level": str(r.get("school_level", "Other")),
            "school_type": str(r.get("school_type", "Regular School")),
            "operational_status": r.get("operational_status", 1),
            "is_operating": bool(r.get("is_operating", True)),
            "is_charter": bool(r.get("is_charter", False)),
            "is_virtual": bool(r.get("is_virtual", False)),
            "school_ptr": float(ptr_val) if pd.notna(ptr_val) and float(ptr_val) > 0 else np.nan,
            "enrollment_k12": float(enr_val) if pd.notna(enr_val) and float(enr_val) >= 0 else np.nan,
            "classroom_teacher_fte": float(fte_val) if pd.notna(fte_val) and float(fte_val) > 0 else np.nan,
        }
        
    # Master dictionary of latest known attributes across all years
    combined_df = pd.concat([df_2013, df_long], ignore_index=True)
    latest_meta = combined_df.sort_values("school_year").groupby("ncessch_str").last().reset_index()
    fallback_meta = latest_meta.set_index("ncessch_str").to_dict(orient="index")
    
    return year_meta_dict, fallback_meta

def assemble_school_record(sy, wave, sid, meta, c_data):
    """Assemble standard flat record for a school-year with all courses."""
    ptr = meta.get("school_ptr", np.nan)
    fte = meta.get("classroom_teacher_fte", np.nan)
    enr = meta.get("enrollment_k12", np.nan)
    
    rec = {
        "school_year": sy,
        "crdc_wave": wave,
        "nces_school_id": sid,
        "nces_lea_id": meta.get("nces_lea_id"),
        "school_name": meta.get("school_name"),
        "district_name": meta.get("district_name", meta.get("lea_name")),
        "lea_name": meta.get("lea_name"),
        "state": meta.get("state"),
        "county_name": meta.get("county_name"),
        "county_fips": meta.get("county_fips"),
        "locale_group": meta.get("locale_group"),
        "school_level": meta.get("school_level"),
        "school_type": meta.get("school_type", "Regular School"),
        "operational_status": meta.get("operational_status", 1),
        "is_operating": meta.get("is_operating", True),
        "is_charter": meta.get("is_charter", False),
        "is_virtual": meta.get("is_virtual", False),
        "enrollment_k12": enr,
        "classroom_teacher_fte": fte,
        "school_ptr": ptr,
    }
    
    for cinfo in COURSES:
        code = cinfo["code"]
        cls, enrolled, cert = c_data.get(code, (np.nan, np.nan, np.nan))
        
        # School-course average class size: enrollment / classes
        mean_size = enrolled / cls if (pd.notnull(cls) and cls > 0 and pd.notnull(enrolled)) else np.nan
        # Certified share: certified / classes
        cert_share = cert / cls if (pd.notnull(cls) and cls > 0 and pd.notnull(cert)) else np.nan
        # School-course allocation wedge: mean_size - same-year same-school ptr
        wedge = mean_size - ptr if (pd.notnull(mean_size) and pd.notnull(ptr)) else np.nan
        
        rec[f"classes_{code}"] = cls
        rec[f"enrollment_{code}"] = enrolled
        rec[f"certified_{code}"] = cert
        rec[f"mean_class_size_{code}"] = mean_size
        rec[f"certified_share_{code}"] = cert_share
        rec[f"allocation_wedge_{code}"] = wedge
        
    return rec

def process_wave_2013_14(year_meta_dict, fallback_meta):
    """Process 2013-14 CRDC Excel files with contemporaneous 2013-14 CCD PTR."""
    p = RAW_CRDC_DIR / "2013-2014"
    sy = "2013-2014"
    wave = "2013-14"
    records = []
    
    # 1. Algebra I
    alg1_df = pd.read_excel(p / "05-1 Algebra I Courses and Classes.xlsx")
    alg1_df["ncessch"] = alg1_df["LEAID"].astype(str).str.zfill(7) + alg1_df["SCHID"].astype(str).str.zfill(5)
    
    # 2. Geometry
    geom_df = pd.read_excel(p / "05-2 Geometry Courses and Classes.xlsx")
    geom_df["ncessch"] = geom_df["LEAID"].astype(str).str.zfill(7) + geom_df["SCHID"].astype(str).str.zfill(5)
    
    # 3. Other Math (Alg II, Adv Math, Calc)
    other_m_df = pd.read_excel(p / "05-3 Other Math Courses and Classes.xlsx")
    other_m_df["ncessch"] = other_m_df["LEAID"].astype(str).str.zfill(7) + other_m_df["SCHID"].astype(str).str.zfill(5)
    
    # 4. Biology
    bio_df = pd.read_excel(p / "05-4 Biology Courses and Classes.xlsx")
    bio_df["ncessch"] = bio_df["LEAID"].astype(str).str.zfill(7) + bio_df["SCHID"].astype(str).str.zfill(5)
    
    # 5. Chemistry
    chem_df = pd.read_excel(p / "05-5 Chemistry Courses and Classes.xlsx")
    chem_df["ncessch"] = chem_df["LEAID"].astype(str).str.zfill(7) + chem_df["SCHID"].astype(str).str.zfill(5)
    
    # 6. Physics
    phys_df = pd.read_excel(p / "05-6 Physics Courses and Classes.xlsx")
    phys_df["ncessch"] = phys_df["LEAID"].astype(str).str.zfill(7) + phys_df["SCHID"].astype(str).str.zfill(5)
    
    kc_schools = set(fallback_meta.keys())
    matched_ids = kc_schools.intersection(set(alg1_df["ncessch"]))
    
    alg1_map = alg1_df.set_index("ncessch").to_dict(orient="index")
    geom_map = geom_df.set_index("ncessch").to_dict(orient="index")
    other_m_map = other_m_df.set_index("ncessch").to_dict(orient="index")
    bio_map = bio_df.set_index("ncessch").to_dict(orient="index")
    chem_map = chem_df.set_index("ncessch").to_dict(orient="index")
    phys_map = phys_df.set_index("ncessch").to_dict(orient="index")
    
    for sid in matched_ids:
        meta = year_meta_dict.get((sid, sy), fallback_meta.get(sid, {}))
        
        row_alg1 = alg1_map.get(sid, {})
        row_geom = geom_map.get(sid, {})
        row_other = other_m_map.get(sid, {})
        row_bio = bio_map.get(sid, {})
        row_chem = chem_map.get(sid, {})
        row_phys = phys_map.get(sid, {})
        
        c_data = {
            "alg1": (clean_crdc_val(row_alg1.get("SCH_ALGCLASSES_GS0712")),
                     sum_clean_parts(row_alg1.get("TOT_ALGENR_GS0910_M"), row_alg1.get("TOT_ALGENR_GS0910_F"),
                                     row_alg1.get("TOT_ALGENR_GS1112_M"), row_alg1.get("TOT_ALGENR_GS1112_F")),
                     np.nan),
            "geom": (clean_crdc_val(row_geom.get("SCH_MATHCLASSES_GEOM")),
                     sum_clean_parts(row_geom.get("TOT_GEOMENR_GS0712_M"), row_geom.get("TOT_GEOMENR_GS0712_F")),
                     np.nan),
            "alg2": (clean_crdc_val(row_other.get("SCH_MATHCLASSES_ALG2")),
                     sum_clean_parts(row_other.get("TOT_MATHENR_ALG2_M"), row_other.get("TOT_MATHENR_ALG2_F")),
                     np.nan),
            "advm": (clean_crdc_val(row_other.get("SCH_MATHCLASSES_ADVM")),
                     sum_clean_parts(row_other.get("TOT_MATHENR_ADVM_M"), row_other.get("TOT_MATHENR_ADVM_F")),
                     np.nan),
            "calc": (clean_crdc_val(row_other.get("SCH_MATHCLASSES_CALC")),
                     sum_clean_parts(row_other.get("TOT_MATHENR_CALC_M"), row_other.get("TOT_MATHENR_CALC_F")),
                     np.nan),
            "bio": (clean_crdc_val(row_bio.get("SCH_SCICLASSES_BIOL")),
                    sum_clean_parts(row_bio.get("TOT_SCIENR_BIOL_M"), row_bio.get("TOT_SCIENR_BIOL_F")),
                    np.nan),
            "chem": (clean_crdc_val(row_chem.get("SCH_SCICLASSES_CHEM")),
                     sum_clean_parts(row_chem.get("TOT_SCIENR_CHEM_M"), row_chem.get("TOT_SCIENR_CHEM_F")),
                     np.nan),
            "phys": (clean_crdc_val(row_phys.get("SCH_SCICLASSES_PHYS")),
                     sum_clean_parts(row_phys.get("TOT_SCIENR_PHYS_M"), row_phys.get("TOT_SCIENR_PHYS_F")),
                     np.nan),
        }
        
        records.append(assemble_school_record(sy, wave, sid, meta, c_data))
        
    return records

def process_wave_2015_16(year_meta_dict, fallback_meta):
    """Process 2015-16 CRDC single wide file."""
    fpath = RAW_CRDC_DIR / "2015-2016" / "CRDC 2015-16 School Data.csv"
    sy = "2015-2016"
    wave = "2015-16"
    records = []
    
    with open(fpath, mode="r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            st = row.get("LEA_STATE", "")
            if st not in ["MO", "KS"]:
                continue
            leaid = str(row.get("LEAID", "")).strip().zfill(7)
            schid = str(row.get("SCHID", "")).strip().zfill(5)
            sid = f"{leaid}{schid}"
            if sid not in fallback_meta:
                continue
            
            meta = year_meta_dict.get((sid, sy), fallback_meta.get(sid, {}))
            
            c_data = {
                "alg1": (clean_crdc_val(row.get("SCH_MATHCLASSES_ALG")),
                         sum_clean_parts(row.get("TOT_ALGENR_GS0910_M"), row.get("TOT_ALGENR_GS0910_F"),
                                         row.get("TOT_ALGENR_GS1112_M"), row.get("TOT_ALGENR_GS1112_F")),
                         clean_crdc_val(row.get("SCH_MATHCERT_ALG"))),
                "geom": (clean_crdc_val(row.get("SCH_MATHCLASSES_GEOM")),
                         sum_clean_parts(row.get("TOT_MATHENR_GEOM_M"), row.get("TOT_MATHENR_GEOM_F")),
                         clean_crdc_val(row.get("SCH_MATHCERT_GEOM"))),
                "alg2": (clean_crdc_val(row.get("SCH_MATHCLASSES_ALG2")),
                         sum_clean_parts(row.get("TOT_MATHENR_ALG2_M"), row.get("TOT_MATHENR_ALG2_F")),
                         clean_crdc_val(row.get("SCH_MATHCERT_ALG2"))),
                "advm": (clean_crdc_val(row.get("SCH_MATHCLASSES_ADVM")),
                         sum_clean_parts(row.get("TOT_MATHENR_ADVM_M"), row.get("TOT_MATHENR_ADVM_F")),
                         clean_crdc_val(row.get("SCH_MATHCERT_ADVM"))),
                "calc": (clean_crdc_val(row.get("SCH_MATHCLASSES_CALC")),
                         sum_clean_parts(row.get("TOT_MATHENR_CALC_M"), row.get("TOT_MATHENR_CALC_F")),
                         clean_crdc_val(row.get("SCH_MATHCERT_CALC"))),
                "bio": (clean_crdc_val(row.get("SCH_SCICLASSES_BIOL")),
                        sum_clean_parts(row.get("TOT_SCIENR_BIOL_M"), row.get("TOT_SCIENR_BIOL_F")),
                        clean_crdc_val(row.get("SCH_SCICCERT_BIOL"))),
                "chem": (clean_crdc_val(row.get("SCH_SCICLASSES_CHEM")),
                         sum_clean_parts(row.get("TOT_SCIENR_CHEM_M"), row.get("TOT_SCIENR_CHEM_F")),
                         clean_crdc_val(row.get("SCH_SCICCERT_CHEM"))),
                "phys": (clean_crdc_val(row.get("SCH_SCICLASSES_PHYS")),
                         sum_clean_parts(row.get("TOT_SCIENR_PHYS_M"), row.get("TOT_SCIENR_PHYS_F")),
                         clean_crdc_val(row.get("SCH_SCICCERT_PHYS"))),
            }
            records.append(assemble_school_record(sy, wave, sid, meta, c_data))
            
    return records

def process_modular_csv_wave(sy, wave, year_meta_dict, fallback_meta, has_nonbinary=False):
    """Process waves 2017-18, 2020-21, 2021-22, 2023-24 with modular CSV files."""
    p = RAW_CRDC_DIR / sy
    records = []
    
    file_map = {
        "alg1": "Algebra I.csv",
        "geom": "Geometry.csv",
        "alg2": "Algebra II.csv",
        "advm": "Advanced Mathematics.csv",
        "calc": "Calculus.csv",
        "bio": "Biology.csv",
        "chem": "Chemistry.csv",
        "phys": "Physics.csv",
    }
    
    maps = {}
    for ccode, fname in file_map.items():
        fpath = p / fname
        if not fpath.exists():
            continue
        try:
            df = pd.read_csv(fpath, encoding="utf-8", low_memory=False)
        except UnicodeDecodeError:
            df = pd.read_csv(fpath, encoding="latin1", low_memory=False)
            
        # Reconstruct 12-digit NCES ID
        if "LEAID" in df.columns and "SCHID" in df.columns:
            df["ncessch"] = df["LEAID"].astype(str).str.zfill(7) + df["SCHID"].astype(str).str.zfill(5)
        elif "COMBOKEY" in df.columns:
            df["ncessch"] = df["COMBOKEY"].astype(str).str.replace(".0", "", regex=False).str.zfill(12)
            
        # Filter to KC schools
        df_kc = df[df["ncessch"].isin(fallback_meta.keys())]
        maps[ccode] = df_kc.set_index("ncessch").to_dict(orient="index")
        
    kc_sids = set(fallback_meta.keys())
    for sid in kc_sids:
        if not any(sid in maps[c] for c in maps):
            continue
        
        meta = year_meta_dict.get((sid, sy), fallback_meta.get(sid, {}))
        
        row_alg1 = maps.get("alg1", {}).get(sid, {})
        row_geom = maps.get("geom", {}).get(sid, {})
        row_alg2 = maps.get("alg2", {}).get(sid, {})
        row_advm = maps.get("advm", {}).get(sid, {})
        row_calc = maps.get("calc", {}).get(sid, {})
        row_bio = maps.get("bio", {}).get(sid, {})
        row_chem = maps.get("chem", {}).get(sid, {})
        row_phys = maps.get("phys", {}).get(sid, {})
        
        if has_nonbinary:
            c_data = {
                "alg1": (clean_crdc_val(row_alg1.get("SCH_MATHCLASSES_ALG")),
                         sum_clean_parts(row_alg1.get("TOT_ALGENR_GS0910_M"), row_alg1.get("TOT_ALGENR_GS0910_F"), row_alg1.get("TOT_ALGENR_GS0910_X"),
                                         row_alg1.get("TOT_ALGENR_GS1112_M"), row_alg1.get("TOT_ALGENR_GS1112_F"), row_alg1.get("TOT_ALGENR_GS1112_X")),
                         clean_crdc_val(row_alg1.get("SCH_MATHCERT_ALG"))),
                "geom": (clean_crdc_val(row_geom.get("SCH_MATHCLASSES_GEOM")),
                         sum_clean_parts(row_geom.get("TOT_MATHENR_GEOM_M"), row_geom.get("TOT_MATHENR_GEOM_F"), row_geom.get("TOT_MATHENR_GEOM_X")),
                         clean_crdc_val(row_geom.get("SCH_MATHCERT_GEOM"))),
                "alg2": (clean_crdc_val(row_alg2.get("SCH_MATHCLASSES_ALG2")),
                         sum_clean_parts(row_alg2.get("TOT_MATHENR_ALG2_M"), row_alg2.get("TOT_MATHENR_ALG2_F"), row_alg2.get("TOT_MATHENR_ALG2_X")),
                         clean_crdc_val(row_alg2.get("SCH_MATHCERT_ALG2"))),
                "advm": (clean_crdc_val(row_advm.get("SCH_MATHCLASSES_ADVM")),
                         sum_clean_parts(row_advm.get("TOT_MATHENR_ADVM_M"), row_advm.get("TOT_MATHENR_ADVM_F"), row_advm.get("TOT_MATHENR_ADVM_X")),
                         clean_crdc_val(row_advm.get("SCH_MATHCERT_ADVM"))),
                "calc": (clean_crdc_val(row_calc.get("SCH_MATHCLASSES_CALC")),
                         sum_clean_parts(row_calc.get("TOT_MATHENR_CALC_M"), row_calc.get("TOT_MATHENR_CALC_F"), row_calc.get("TOT_MATHENR_CALC_X")),
                         clean_crdc_val(row_calc.get("SCH_MATHCERT_CALC"))),
                "bio": (clean_crdc_val(row_bio.get("SCH_SCICLASSES_BIOL")),
                        sum_clean_parts(row_bio.get("TOT_SCIENR_BIOL_M"), row_bio.get("TOT_SCIENR_BIOL_F"), row_bio.get("TOT_SCIENR_BIOL_X")),
                        clean_crdc_val(row_bio.get("SCH_SCICCERT_BIOL"))),
                "chem": (clean_crdc_val(row_chem.get("SCH_SCICLASSES_CHEM")),
                         sum_clean_parts(row_chem.get("TOT_SCIENR_CHEM_M"), row_chem.get("TOT_SCIENR_CHEM_F"), row_chem.get("TOT_SCIENR_CHEM_X")),
                         clean_crdc_val(row_chem.get("SCH_SCICCERT_CHEM"))),
                "phys": (clean_crdc_val(row_phys.get("SCH_SCICLASSES_PHYS")),
                         sum_clean_parts(row_phys.get("TOT_SCIENR_PHYS_M"), row_phys.get("TOT_SCIENR_PHYS_F"), row_phys.get("TOT_SCIENR_PHYS_X")),
                         clean_crdc_val(row_phys.get("SCH_SCICCERT_PHYS"))),
            }
        else:
            c_data = {
                "alg1": (clean_crdc_val(row_alg1.get("SCH_MATHCLASSES_ALG")),
                         sum_clean_parts(row_alg1.get("TOT_ALGENR_GS0910_M"), row_alg1.get("TOT_ALGENR_GS0910_F"),
                                         row_alg1.get("TOT_ALGENR_GS1112_M"), row_alg1.get("TOT_ALGENR_GS1112_F")),
                         clean_crdc_val(row_alg1.get("SCH_MATHCERT_ALG"))),
                "geom": (clean_crdc_val(row_geom.get("SCH_MATHCLASSES_GEOM")),
                         sum_clean_parts(row_geom.get("TOT_MATHENR_GEOM_M"), row_geom.get("TOT_MATHENR_GEOM_F")),
                         clean_crdc_val(row_geom.get("SCH_MATHCERT_GEOM"))),
                "alg2": (clean_crdc_val(row_alg2.get("SCH_MATHCLASSES_ALG2")),
                         sum_clean_parts(row_alg2.get("TOT_MATHENR_ALG2_M"), row_alg2.get("TOT_MATHENR_ALG2_F")),
                         clean_crdc_val(row_alg2.get("SCH_MATHCERT_ALG2"))),
                "advm": (clean_crdc_val(row_advm.get("SCH_MATHCLASSES_ADVM")),
                         sum_clean_parts(row_advm.get("TOT_MATHENR_ADVM_M"), row_advm.get("TOT_MATHENR_ADVM_F")),
                         clean_crdc_val(row_advm.get("SCH_MATHCERT_ADVM"))),
                "calc": (clean_crdc_val(row_calc.get("SCH_MATHCLASSES_CALC")),
                         sum_clean_parts(row_calc.get("TOT_MATHENR_CALC_M"), row_calc.get("TOT_MATHENR_CALC_F")),
                         clean_crdc_val(row_calc.get("SCH_MATHCERT_CALC"))),
                "bio": (clean_crdc_val(row_bio.get("SCH_SCICLASSES_BIOL")),
                         sum_clean_parts(row_bio.get("TOT_SCIENR_BIOL_M"), row_bio.get("TOT_SCIENR_BIOL_F")),
                         clean_crdc_val(row_bio.get("SCH_SCICCERT_BIOL"))),
                "chem": (clean_crdc_val(row_chem.get("SCH_SCICLASSES_CHEM")),
                         sum_clean_parts(row_chem.get("TOT_SCIENR_CHEM_M"), row_chem.get("TOT_SCIENR_CHEM_F")),
                         clean_crdc_val(row_chem.get("SCH_SCICCERT_CHEM"))),
                "phys": (clean_crdc_val(row_phys.get("SCH_SCICLASSES_PHYS")),
                         sum_clean_parts(row_phys.get("TOT_SCIENR_PHYS_M"), row_phys.get("TOT_SCIENR_PHYS_F")),
                         clean_crdc_val(row_phys.get("SCH_SCICCERT_PHYS"))),
            }
        records.append(assemble_school_record(sy, wave, sid, meta, c_data))
        
    return records

def main():
    print("=" * 70)
    print("BUILDING KANSAS CITY METRO CRDC COURSE CAPACITY PANEL (AUDITED)")
    print("=" * 70)
    
    year_meta_dict, fallback_meta = load_school_universe_metadata()
    print(f"Loaded metadata for {len(fallback_meta)} distinct KC public schools.")
    print(f"Loaded {len(year_meta_dict)} school-year metadata pairs across 2013-14 to 2024-25.")
    
    all_records = []
    
    # Wave 2013-14
    print("\nProcessing CRDC 2013-14...")
    r1314 = process_wave_2013_14(year_meta_dict, fallback_meta)
    print(f"  2013-14: {len(r1314)} schools matched.")
    all_records.extend(r1314)
    
    # Wave 2015-16
    print("\nProcessing CRDC 2015-16...")
    r1516 = process_wave_2015_16(year_meta_dict, fallback_meta)
    print(f"  2015-16: {len(r1516)} schools matched.")
    all_records.extend(r1516)
    
    # Wave 2017-18
    print("\nProcessing CRDC 2017-18...")
    r1718 = process_modular_csv_wave("2017-2018", "2017-18", year_meta_dict, fallback_meta, has_nonbinary=False)
    print(f"  2017-18: {len(r1718)} schools matched.")
    all_records.extend(r1718)
    
    # Wave 2020-21
    print("\nProcessing CRDC 2020-21...")
    r2021 = process_modular_csv_wave("2020-2021", "2020-21", year_meta_dict, fallback_meta, has_nonbinary=False)
    print(f"  2020-21: {len(r2021)} schools matched.")
    all_records.extend(r2021)
    
    # Wave 2021-22
    print("\nProcessing CRDC 2021-22...")
    r2122 = process_modular_csv_wave("2021-2022", "2021-22", year_meta_dict, fallback_meta, has_nonbinary=False)
    print(f"  2021-22: {len(r2122)} schools matched.")
    all_records.extend(r2122)
    
    # Wave 2023-24
    print("\nProcessing CRDC 2023-24...")
    r2324 = process_modular_csv_wave("2023-2024", "2023-24", year_meta_dict, fallback_meta, has_nonbinary=True)
    print(f"  2023-24: {len(r2324)} schools matched.")
    all_records.extend(r2324)
    
    wide_df = pd.DataFrame(all_records)
    print(f"\nTotal School-Year observations across all 6 waves: {len(wide_df)}")
    
    # Export wide panel
    wide_out = PROCESSED_DIR / "kc_crdc_school_course_capacity_2013_14_2023_24.csv"
    wide_df.to_csv(wide_out, index=False)
    print(f"Exported Wide Panel to {wide_out.name}")
    
    # Construct Long Panel (one row per school-year-course)
    # RENAME to kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv
    long_records = []
    for idx, row in wide_df.iterrows():
        base_info = {
            "school_year": row["school_year"],
            "crdc_wave": row["crdc_wave"],
            "nces_school_id": row["nces_school_id"],
            "nces_lea_id": row["nces_lea_id"],
            "school_name": row["school_name"],
            "district_name": row["district_name"],
            "state": row["state"],
            "county_name": row["county_name"],
            "county_fips": row["county_fips"],
            "locale_group": row["locale_group"],
            "school_level": row["school_level"],
            "school_type": row.get("school_type", "Regular School"),
            "operational_status": row.get("operational_status", 1),
            "is_operating": row.get("is_operating", True),
            "is_charter": row.get("is_charter", False),
            "is_virtual": row.get("is_virtual", False),
            "school_ptr": row["school_ptr"],
            "enrollment_k12": row["enrollment_k12"],
            "classroom_teacher_fte": row["classroom_teacher_fte"]
        }
        for cinfo in COURSES:
            code = cinfo["code"]
            cls = row[f"classes_{code}"]
            enr = row[f"enrollment_{code}"]
            cert = row[f"certified_{code}"]
            size = row[f"mean_class_size_{code}"]
            cert_share = row[f"certified_share_{code}"]
            wedge = row[f"allocation_wedge_{code}"]
            
            c_rec = base_info.copy()
            c_rec.update({
                "course_code": code,
                "course_name": cinfo["name"],
                "subject_area": cinfo["subject"],
                "course_level": cinfo["level"],
                "num_classes": cls,
                "num_enrolled": enr,
                "num_certified": cert,
                "mean_class_size": size,
                "certified_share": cert_share,
                "allocation_wedge": wedge
            })
            long_records.append(c_rec)
            
    long_df = pd.DataFrame(long_records)
    long_out = PROCESSED_DIR / "kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv"
    long_df.to_csv(long_out, index=False)
    print(f"Exported Long Panel to {long_out.name} ({len(long_df)} course-school-year rows)")
    
    # Remove old misnamed file if it exists
    old_file = PROCESSED_DIR / "kc_crdc_course_sections_long_2013_14_2023_24.csv"
    if old_file.exists():
        try:
            os.remove(old_file)
            print(f"Removed old misnamed file: {old_file.name}")
        except Exception as e:
            print(f"Warning: could not remove {old_file.name}: {e}")
            
    # Audit anomalies (mean class size > 50 or < 3)
    anomalies = []
    for idx, r in long_df.dropna(subset=["mean_class_size"]).iterrows():
        if r["mean_class_size"] > 50:
            anomalies.append({
                "school_year": r["school_year"],
                "nces_school_id": r["nces_school_id"],
                "school_name": r["school_name"],
                "course_name": r["course_name"],
                "num_classes": r["num_classes"],
                "num_enrolled": r["num_enrolled"],
                "mean_class_size": r["mean_class_size"],
                "flag": "High Mean Class Size (> 50 students/class)"
            })
        elif r["mean_class_size"] < 3:
            anomalies.append({
                "school_year": r["school_year"],
                "nces_school_id": r["nces_school_id"],
                "school_name": r["school_name"],
                "course_name": r["course_name"],
                "num_classes": r["num_classes"],
                "num_enrolled": r["num_enrolled"],
                "mean_class_size": r["mean_class_size"],
                "flag": "Very Low Mean Class Size (< 3 students/class)"
            })
            
    anom_df = pd.DataFrame(anomalies)
    anom_out = OUTPUTS_DIR / "task004_crdc_anomalies.csv"
    anom_df.to_csv(anom_out, index=False)
    print(f"Audited anomalies exported to {anom_out.name} ({len(anom_df)} flagged items)")

if __name__ == "__main__":
    main()
