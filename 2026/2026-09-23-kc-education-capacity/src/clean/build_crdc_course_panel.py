"""
Construct the Kansas City Metropolitan CRDC Course Capacity Panel (2013-14 through 2023-24).
Harmonizes course classes and student enrollment across 6 CRDC collection waves:
2013-14, 2015-16, 2017-18, 2020-21, 2021-22, and 2023-24.

Computes:
- Mean section size per course: students / classes
- Course Allocation Wedge: mean section size - school pupil/teacher ratio (CCD PTR)
- Course categorization: Foundation Core vs. Advanced / Specialized
"""

import sys
import csv
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_CRDC_DIR = PROJECT_ROOT / "data" / "raw" / "crdc"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "tables"
LONG_PANEL_PATH = PROCESSED_DIR / "kc_school_capacity_long_2014_15_2024_25.csv"

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
    """Parse numeric CRDC values, converting negative exception/reserve codes to NaN."""
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
    """Load school universe and metadata from CCD longitudinal panel."""
    df = pd.read_csv(LONG_PANEL_PATH, low_memory=False)
    # Master dictionary of school attributes by nces_school_id
    latest_meta = df.sort_values("school_year").groupby("nces_school_id").last().reset_index()
    latest_meta["ncessch_str"] = latest_meta["nces_school_id"].astype(str).str.zfill(12)
    meta_dict = latest_meta.set_index("ncessch_str").to_dict(orient="index")
    
    # Also index CCD PTR by (ncessch_str, school_year)
    df["ncessch_str"] = df["nces_school_id"].astype(str).str.zfill(12)
    ptr_dict = df.set_index(["ncessch_str", "school_year"])["students_per_classroom_teacher_fte_allgrades"].to_dict()
    fte_dict = df.set_index(["ncessch_str", "school_year"])["classroom_teacher_fte"].to_dict()
    enr_dict = df.set_index(["ncessch_str", "school_year"])["enrollment_k12"].to_dict()
    
    return meta_dict, ptr_dict, fte_dict, enr_dict

def process_wave_2013_14(meta_dict, ptr_dict, fte_dict, enr_dict):
    """Process 2013-14 CRDC Excel files."""
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
    
    # Filter to KC schools
    kc_schools = set(meta_dict.keys())
    matched_ids = kc_schools.intersection(set(alg1_df["ncessch"]))
    
    alg1_map = alg1_df.set_index("ncessch").to_dict(orient="index")
    geom_map = geom_df.set_index("ncessch").to_dict(orient="index")
    other_m_map = other_m_df.set_index("ncessch").to_dict(orient="index")
    bio_map = bio_df.set_index("ncessch").to_dict(orient="index")
    chem_map = chem_df.set_index("ncessch").to_dict(orient="index")
    phys_map = phys_df.set_index("ncessch").to_dict(orient="index")
    
    for sid in matched_ids:
        meta = meta_dict[sid]
        # In 2013-14, match PTR from 2014-15 baseline if 2013-14 CCD is not in panel
        ptr = ptr_dict.get((sid, "2013-2014"), ptr_dict.get((sid, "2014-2015"), np.nan))
        fte = fte_dict.get((sid, "2013-2014"), fte_dict.get((sid, "2014-2015"), np.nan))
        enr = enr_dict.get((sid, "2013-2014"), enr_dict.get((sid, "2014-2015"), np.nan))
        
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
        
        records.append(assemble_school_record(sy, wave, sid, meta, ptr, fte, enr, c_data))
        
    return records


def process_wave_2015_16(meta_dict, ptr_dict, fte_dict, enr_dict):
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
            if sid not in meta_dict:
                continue
            
            meta = meta_dict[sid]
            ptr = ptr_dict.get((sid, sy), np.nan)
            fte = fte_dict.get((sid, sy), np.nan)
            enr = enr_dict.get((sid, sy), np.nan)
            
            c_data = {
                "alg1": (clean_crdc_val(row.get("SCH_MATHCLASSES_ALG")),
                         sum_clean_parts(row.get("TOT_ALGENR_GS0910_M"), row.get("TOT_ALGENR_GS0910_F"),
                                         row.get("TOT_ALGENR_GS1112_M"), row.get("TOT_ALGENR_GS1112_F")),
                         clean_crdc_val(row.get("SCH_MATHCERT_ALG"))),
                "geom": (clean_crdc_val(row.get("SCH_MATHCLASSES_GEOM")),
                         sum_clean_parts(row.get("TOT_GEOM_M"), row.get("TOT_GEOM_F")),
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
            records.append(assemble_school_record(sy, wave, sid, meta, ptr, fte, enr, c_data))
            
    return records


def process_modular_csv_wave(sy, wave, meta_dict, ptr_dict, fte_dict, enr_dict, has_nonbinary=False):
    """Process modular CSV wave (2017-18, 2020-21, 2021-22, 2023-24)."""
    p = RAW_CRDC_DIR / sy
    records = []
    
    # Load course files into dicts by sid
    course_files = {
        "alg1": "Algebra I.csv",
        "geom": "Geometry.csv",
        "alg2": "Algebra II.csv",
        "advm": "Advanced Mathematics.csv",
        "calc": "Calculus.csv",
        "bio": "Biology.csv",
        "chem": "Chemistry.csv",
        "phys": "Physics.csv"
    }
    
    maps = {}
    for ccode, fname in course_files.items():
        fpath = p / fname
        if not fpath.exists():
            continue
        try:
            df = pd.read_csv(fpath, low_memory=False, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(fpath, low_memory=False, encoding="latin1")
        # Parse school ID
        if "COMBOKEY" in df.columns:
            df["ncessch"] = df["COMBOKEY"].astype(str).str.replace(".0", "", regex=False).str.zfill(12)
        elif "LEAID" in df.columns and "SCHID" in df.columns:
            df["ncessch"] = df["LEAID"].astype(str).str.zfill(7) + df["SCHID"].astype(str).str.zfill(5)
        # Filter to KC schools
        df_kc = df[df["ncessch"].isin(meta_dict.keys())]
        maps[ccode] = df_kc.set_index("ncessch").to_dict(orient="index")
        
    kc_sids = set(meta_dict.keys())
    for sid in kc_sids:
        # Check if school appears in any map
        if not any(sid in maps[c] for c in maps):
            continue
        
        meta = meta_dict[sid]
        ptr = ptr_dict.get((sid, sy), np.nan)
        fte = fte_dict.get((sid, sy), np.nan)
        enr = enr_dict.get((sid, sy), np.nan)
        
        row_alg1 = maps.get("alg1", {}).get(sid, {})
        row_geom = maps.get("geom", {}).get(sid, {})
        row_alg2 = maps.get("alg2", {}).get(sid, {})
        row_advm = maps.get("advm", {}).get(sid, {})
        row_calc = maps.get("calc", {}).get(sid, {})
        row_bio = maps.get("bio", {}).get(sid, {})
        row_chem = maps.get("chem", {}).get(sid, {})
        row_phys = maps.get("phys", {}).get(sid, {})
        
        if has_nonbinary:
            # 2023-24 includes _X (nonbinary)
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
        records.append(assemble_school_record(sy, wave, sid, meta, ptr, fte, enr, c_data))
        
    return records


def assemble_school_record(sy, wave, sid, meta, ptr, fte, enr, c_data):
    """Assemble standard flat record for a school-year with all courses."""
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
        "is_charter": meta.get("is_charter"),
        "enrollment_k12": enr,
        "classroom_teacher_fte": fte,
        "school_ptr": ptr,
    }
    
    for cinfo in COURSES:
        code = cinfo["code"]
        cls, enrolled, cert = c_data.get(code, (np.nan, np.nan, np.nan))
        
        # Mean class size: enrollment / classes
        mean_size = enrolled / cls if (pd.notnull(cls) and cls > 0 and pd.notnull(enrolled)) else np.nan
        # Certified share: certified / classes
        cert_share = cert / cls if (pd.notnull(cls) and cls > 0 and pd.notnull(cert)) else np.nan
        # Allocation wedge: mean_size - school_ptr
        wedge = mean_size - ptr if (pd.notnull(mean_size) and pd.notnull(ptr)) else np.nan
        
        rec[f"classes_{code}"] = cls
        rec[f"enrollment_{code}"] = enrolled
        rec[f"certified_{code}"] = cert
        rec[f"mean_class_size_{code}"] = mean_size
        rec[f"certified_share_{code}"] = cert_share
        rec[f"allocation_wedge_{code}"] = wedge
        
    return rec


def main():
    print("=" * 70)
    print("BUILDING KANSAS CITY METRO CRDC COURSE CAPACITY PANEL")
    print("=" * 70)
    
    meta_dict, ptr_dict, fte_dict, enr_dict = load_school_universe_metadata()
    print(f"Loaded metadata for {len(meta_dict)} KC public schools.")
    
    all_records = []
    
    # Wave 2013-14
    print("\nProcessing CRDC 2013-14...")
    r1314 = process_wave_2013_14(meta_dict, ptr_dict, fte_dict, enr_dict)
    print(f"  2013-14: {len(r1314)} schools matched.")
    all_records.extend(r1314)
    
    # Wave 2015-16
    print("\nProcessing CRDC 2015-16...")
    r1516 = process_wave_2015_16(meta_dict, ptr_dict, fte_dict, enr_dict)
    print(f"  2015-16: {len(r1516)} schools matched.")
    all_records.extend(r1516)
    
    # Wave 2017-18
    print("\nProcessing CRDC 2017-18...")
    r1718 = process_modular_csv_wave("2017-2018", "2017-18", meta_dict, ptr_dict, fte_dict, enr_dict, has_nonbinary=False)
    print(f"  2017-18: {len(r1718)} schools matched.")
    all_records.extend(r1718)
    
    # Wave 2020-21
    print("\nProcessing CRDC 2020-21...")
    r2021 = process_modular_csv_wave("2020-2021", "2020-21", meta_dict, ptr_dict, fte_dict, enr_dict, has_nonbinary=False)
    print(f"  2020-21: {len(r2021)} schools matched.")
    all_records.extend(r2021)
    
    # Wave 2021-22
    print("\nProcessing CRDC 2021-22...")
    r2122 = process_modular_csv_wave("2021-2022", "2021-22", meta_dict, ptr_dict, fte_dict, enr_dict, has_nonbinary=False)
    print(f"  2021-22: {len(r2122)} schools matched.")
    all_records.extend(r2122)
    
    # Wave 2023-24
    print("\nProcessing CRDC 2023-24...")
    r2324 = process_modular_csv_wave("2023-2024", "2023-24", meta_dict, ptr_dict, fte_dict, enr_dict, has_nonbinary=True)
    print(f"  2023-24: {len(r2324)} schools matched.")
    all_records.extend(r2324)
    
    wide_df = pd.DataFrame(all_records)
    print(f"\nTotal School-Year observations across all 6 waves: {len(wide_df)}")
    
    # Export wide panel
    wide_out = PROCESSED_DIR / "kc_crdc_school_course_capacity_2013_14_2023_24.csv"
    wide_df.to_csv(wide_out, index=False)
    print(f"Exported Wide Panel to {wide_out.name}")
    
    # Construct Long Panel (one row per school-year-course)
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
            "is_charter": row["is_charter"],
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
            
            # Record course instance
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
    long_out = PROCESSED_DIR / "kc_crdc_course_sections_long_2013_14_2023_24.csv"
    long_df.to_csv(long_out, index=False)
    print(f"Exported Long Panel to {long_out.name} ({len(long_df)} course-school-year rows)")
    
    # Audit anomalies (e.g. mean class size > 60 or classes > 0 but enrollment == 0)
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
