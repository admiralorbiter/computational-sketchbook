"""
Pipeline: Build Missouri High School CRDC Measurement Panel (2021–22).

Extracts and standardizes records from:
1. NCES CCD Public Elementary/Secondary School Universe Directory SY 2021-22
2. OCR Civil Rights Data Collection (CRDC) SY 2021-22:
   - School Characteristics
   - Advanced Placement (AP)
   - Dual Enrollment
   - Computer Science
   - Physics
   - Enrollment

Rigorous Population Funnel:
- 318 regular, open public schools classified as serving exactly grades 9–12 in CCD
- 317 matched to CRDC records
- 307 with consistent grades 9–12 reporting across both sources
- 10 with conflicting grade-span reporting retained for sensitivity analysis
"""

import os
import sys
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

# Paths
MODULE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = MODULE_DIR.parent
SKETCHBOOK_ROOT = PROJECT_DIR.parent.parent

RAW_CCD_ZIP = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "raw" / "nces" / "2021_2022" / "ccd_sch_029_2122_w_1a_071722.zip"
RAW_CRDC_DIR = SKETCHBOOK_ROOT / "2026" / "2026-09-23-kc-education-capacity" / "data" / "raw" / "crdc" / "2021-2022"

DATA_RAW = PROJECT_DIR / "data" / "raw"
DATA_PROCESSED = PROJECT_DIR / "data" / "processed"

DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)


def clean_num(val):
    """Clean negative CRDC exception codes (-9, -5, -3, etc.) to NaN or 0 where appropriate."""
    if pd.isna(val):
        return np.nan
    try:
        f = float(val)
        return np.nan if f < 0 else f
    except (ValueError, TypeError):
        return np.nan


def main():
    print("=" * 70)
    print("BUILDING MISSOURI CRDC OPPORTUNITY MEASUREMENT PANEL (2021-22)")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. NCES CCD Directory (2021-22)
    # -------------------------------------------------------------
    print("1. Loading NCES CCD Directory SY 2021-22...")
    with zipfile.ZipFile(RAW_CCD_ZIP) as zf:
        with zf.open("ccd_sch_029_2122_w_1a_071722.csv") as f:
            df_ccd_all = pd.read_csv(f, low_memory=False)

    df_ccd_mo = df_ccd_all[df_ccd_all["ST"] == "MO"].copy()
    print(f"   Total Missouri schools in CCD directory: {len(df_ccd_mo):,}")

    # Standardize IDs
    df_ccd_mo["ncessch"] = df_ccd_mo["NCESSCH"].astype(str).str.zfill(12)
    df_ccd_mo["leaid"] = df_ccd_mo["LEAID"].astype(str).str.zfill(7)

    # Apply initial selection criteria: Regular School, Grades 9-12, Open Status
    is_regular = df_ccd_mo["SCH_TYPE_TEXT"] == "Regular School"
    is_g9_12 = (df_ccd_mo["GSLO"] == "09") & (df_ccd_mo["GSHI"] == "12")
    is_open = df_ccd_mo["SY_STATUS_TEXT"] == "Open"

    initial_318 = df_ccd_mo[is_regular & is_g9_12 & is_open].copy()
    print(f"   Schools meeting initial criteria (Regular, Open, Grades 9-12): {len(initial_318)}")
    assert len(initial_318) == 318, f"Expected 318 initial schools, got {len(initial_318)}"

    # Save raw extract
    ccd_cols = [
        "SCHOOL_YEAR", "FIPST", "ST", "ncessch", "leaid", "SCH_NAME", "LEA_NAME",
        "SCH_TYPE_TEXT", "SY_STATUS_TEXT", "GSLO", "GSHI", "LEVEL",
        "MCITY", "MZIP", "PHONE"
    ]
    initial_318[ccd_cols].to_csv(DATA_RAW / "mo_ccd_directory_2021_22.csv", index=False)

    # -------------------------------------------------------------
    # 2. CRDC School Characteristics (2021-22)
    # -------------------------------------------------------------
    print("2. Loading CRDC School Characteristics SY 2021-22...")
    df_char = pd.read_csv(RAW_CRDC_DIR / "School Characteristics.csv", low_memory=False, encoding="latin1")
    df_char_mo = df_char[df_char["LEA_STATE"] == "MO"].copy()
    df_char_mo["ncessch"] = df_char_mo["COMBOKEY"].astype(str).str.zfill(12)
    print(f"   Total Missouri schools in CRDC characteristics: {len(df_char_mo):,}")
    df_char_mo.to_csv(DATA_RAW / "mo_crdc_school_char_2021_22.csv", index=False)

    # -------------------------------------------------------------
    # 3. Match CCD to CRDC Characteristics
    # -------------------------------------------------------------
    print("3. Matching CCD initial sample to CRDC records...")
    m = initial_318.merge(df_char_mo, on="ncessch", how="left", suffixes=("_ccd", "_crdc"))
    m["flag_matched_crdc"] = m["COMBOKEY"].notna()
    matched_317 = m[m["flag_matched_crdc"]].copy()
    print(f"   Schools matched to CRDC records: {len(matched_317)}")
    assert len(matched_317) == 317, f"Expected 317 matched schools, got {len(matched_317)}"

    unmatched_1 = m[~m["flag_matched_crdc"]].iloc[0]
    print(f"   Unmatched school (CCD only): {unmatched_1['ncessch']} - {unmatched_1['SCH_NAME_ccd']}")

    # -------------------------------------------------------------
    # 4. Grade-Span Consistency Classification
    # -------------------------------------------------------------
    print("4. Evaluating Grade-Span consistency...")
    all_grade_cols = [
        "SCH_GRADE_PS", "SCH_GRADE_KG", "SCH_GRADE_G01", "SCH_GRADE_G02",
        "SCH_GRADE_G03", "SCH_GRADE_G04", "SCH_GRADE_G05", "SCH_GRADE_G06",
        "SCH_GRADE_G07", "SCH_GRADE_G08", "SCH_GRADE_G09", "SCH_GRADE_G10",
        "SCH_GRADE_G11", "SCH_GRADE_G12", "SCH_GRADE_UG"
    ]
    high_grades = ["SCH_GRADE_G09", "SCH_GRADE_G10", "SCH_GRADE_G11", "SCH_GRADE_G12"]
    other_grades = [c for c in all_grade_cols if c not in high_grades]

    has_all_high = (m[high_grades] == "Yes").all(axis=1)
    has_no_others = (m[other_grades] == "No").all(axis=1)

    m["flag_consistent_9_12"] = m["flag_matched_crdc"] & has_all_high & has_no_others
    m["flag_conflicting_span"] = m["flag_matched_crdc"] & (~m["flag_consistent_9_12"])

    def get_reported_grades(row):
        if not row["flag_matched_crdc"]:
            return "UNMATCHED_IN_CRDC"
        yes_grades = [c.replace("SCH_GRADE_", "") for c in all_grade_cols if row.get(c) == "Yes"]
        return ", ".join(yes_grades)

    m["crdc_reported_grades"] = m.apply(get_reported_grades, axis=1)

    consistent_307 = m[m["flag_consistent_9_12"]].copy()
    conflicting_10 = m[m["flag_conflicting_span"]].copy()

    print(f"   Consistent grades 9–12 reporting in both sources: {len(consistent_307)}")
    print(f"   Conflicting grade-span records (sensitivity group): {len(conflicting_10)}")
    assert len(consistent_307) == 307, f"Expected 307 consistent schools, got {len(consistent_307)}"
    assert len(conflicting_10) == 10, f"Expected 10 conflicting schools, got {len(conflicting_10)}"

    # -------------------------------------------------------------
    # 5. Extract CRDC Courses & Opportunity Tables
    # -------------------------------------------------------------
    print("5. Loading and merging CRDC opportunity tables...")

    # AP
    df_ap = pd.read_csv(RAW_CRDC_DIR / "Advanced Placement.csv", low_memory=False, encoding="latin1")
    df_ap_mo = df_ap[df_ap["LEA_STATE"] == "MO"].copy()
    df_ap_mo["ncessch"] = df_ap_mo["COMBOKEY"].astype(str).str.zfill(12)
    df_ap_mo.to_csv(DATA_RAW / "mo_crdc_ap_2021_22.csv", index=False)

    # Dual Enrollment
    df_dual = pd.read_csv(RAW_CRDC_DIR / "Dual Enrollment.csv", low_memory=False, encoding="latin1")
    df_dual_mo = df_dual[df_dual["LEA_STATE"] == "MO"].copy()
    df_dual_mo["ncessch"] = df_dual_mo["COMBOKEY"].astype(str).str.zfill(12)
    df_dual_mo.to_csv(DATA_RAW / "mo_crdc_dual_2021_22.csv", index=False)

    # Physics
    df_phys = pd.read_csv(RAW_CRDC_DIR / "Physics.csv", low_memory=False, encoding="latin1")
    df_phys_mo = df_phys[df_phys["LEA_STATE"] == "MO"].copy()
    df_phys_mo["ncessch"] = df_phys_mo["COMBOKEY"].astype(str).str.zfill(12)
    df_phys_mo.to_csv(DATA_RAW / "mo_crdc_physics_2021_22.csv", index=False)

    # Computer Science
    df_cs = pd.read_csv(RAW_CRDC_DIR / "Computer Science.csv", low_memory=False, encoding="latin1")
    df_cs_mo = df_cs[df_cs["LEA_STATE"] == "MO"].copy()
    df_cs_mo["ncessch"] = df_cs_mo["COMBOKEY"].astype(str).str.zfill(12)
    df_cs_mo.to_csv(DATA_RAW / "mo_crdc_computer_science_2021_22.csv", index=False)

    # Enrollment
    df_enr = pd.read_csv(RAW_CRDC_DIR / "Enrollment.csv", low_memory=False, encoding="latin1")
    df_enr_mo = df_enr[df_enr["LEA_STATE"] == "MO"].copy()
    df_enr_mo["ncessch"] = df_enr_mo["COMBOKEY"].astype(str).str.zfill(12)
    enr_m = pd.to_numeric(df_enr_mo["TOT_ENR_M"], errors="coerce").fillna(0)
    enr_f = pd.to_numeric(df_enr_mo["TOT_ENR_F"], errors="coerce").fillna(0)
    enr_x = pd.to_numeric(df_enr_mo["TOT_ENR_X"], errors="coerce").fillna(0) if "TOT_ENR_X" in df_enr_mo.columns else 0
    df_enr_mo["crdc_total_enrollment"] = enr_m + enr_f + enr_x
    df_enr_mo.to_csv(DATA_RAW / "mo_crdc_enrollment_2021_22.csv", index=False)

    # -------------------------------------------------------------
    # 6. Merge Opportunity Fields onto Master Panel
    # -------------------------------------------------------------
    print("6. Standardizing indicators and creating analytical columns...")
    panel = m.merge(
        df_ap_mo[["ncessch", "SCH_APENR_IND", "SCH_APCOMPENR_IND", "SCH_APCOURSES"]],
        on="ncessch", how="left"
    )
    panel = panel.merge(
        df_dual_mo[["ncessch", "SCH_DUAL_IND"]],
        on="ncessch", how="left"
    )
    panel = panel.merge(
        df_phys_mo[["ncessch", "SCH_SCICLASSES_PHYS"]],
        on="ncessch", how="left"
    )
    panel = panel.merge(
        df_cs_mo[["ncessch", "SCH_COMPCLASSES_CSCI"]],
        on="ncessch", how="left"
    )
    panel = panel.merge(
        df_enr_mo[["ncessch", "crdc_total_enrollment"]],
        on="ncessch", how="left"
    )

    # Clean variables
    panel["ap_participating"] = panel["SCH_APENR_IND"].str.strip() == "Yes"
    panel["ap_indicator_raw"] = panel["SCH_APENR_IND"].str.strip()
    panel["ap_courses_count"] = panel["SCH_APCOURSES"].apply(clean_num)

    panel["dual_participating"] = panel["SCH_DUAL_IND"].str.strip() == "Yes"
    panel["dual_indicator_raw"] = panel["SCH_DUAL_IND"].str.strip()

    panel["ap_cs_participating"] = panel["SCH_APCOMPENR_IND"].str.strip() == "Yes"
    panel["ap_cs_indicator_raw"] = panel["SCH_APCOMPENR_IND"].str.strip()

    panel["physics_classes"] = panel["SCH_SCICLASSES_PHYS"].apply(clean_num).fillna(0)
    panel["has_physics_classes"] = panel["physics_classes"] > 0

    panel["general_cs_classes"] = panel["SCH_COMPCLASSES_CSCI"].apply(clean_num).fillna(0)
    panel["has_general_cs_classes"] = panel["general_cs_classes"] > 0

    # Categorize 4-cell pathway: AP x Dual
    def categorize_pathway(row):
        ap = row["ap_participating"]
        dual = row["dual_participating"]
        if not ap and not dual:
            return "Neither"
        elif not ap and dual:
            return "Dual_Only"
        elif ap and not dual:
            return "AP_Only"
        else:
            return "Both"

    panel["pathway_cell"] = panel.apply(categorize_pathway, axis=1)

    # Keep tidy column subset
    output_cols = [
        "ncessch", "leaid", "SCH_NAME_ccd", "LEA_NAME_ccd", "MCITY", "MZIP",
        "flag_matched_crdc", "flag_consistent_9_12", "flag_conflicting_span",
        "crdc_reported_grades", "crdc_total_enrollment",
        "ap_participating", "ap_indicator_raw", "ap_courses_count",
        "dual_participating", "dual_indicator_raw", "pathway_cell",
        "ap_cs_participating", "ap_cs_indicator_raw",
        "general_cs_classes", "has_general_cs_classes",
        "physics_classes", "has_physics_classes"
    ]
    tidy_panel = panel[output_cols].rename(columns={
        "SCH_NAME_ccd": "school_name",
        "LEA_NAME_ccd": "district_name",
        "MCITY": "city",
        "MZIP": "zip_code"
    })

    # Save panel outputs
    tidy_panel.to_csv(DATA_PROCESSED / "mo_high_school_crdc_measurement_panel_2021_22.csv", index=False)
    tidy_panel.to_parquet(DATA_PROCESSED / "mo_high_school_crdc_measurement_panel_2021_22.parquet", index=False)

    # Save population exclusion funnel
    funnel = pd.DataFrame([
        {"stage": "1. Missouri Regular Public Schools (CCD)", "count": len(df_ccd_mo[df_ccd_mo["SCH_TYPE_TEXT"] == "Regular School"]), "excluded": 0, "pct_retained": 100.0, "reason": "State universe of regular schools"},
        {"stage": "2. Classified Exactly Grades 9-12 & Open (CCD)", "count": 318, "excluded": len(df_ccd_mo[df_ccd_mo["SCH_TYPE_TEXT"] == "Regular School"]) - 318, "pct_retained": 318 / 318 * 100.0, "reason": "Excludes elementary, middle, combined 7-12, and inactive/future schools"},
        {"stage": "3. Matched to CRDC Records", "count": 317, "excluded": 1, "pct_retained": 317 / 318 * 100.0, "reason": "1 school (Academia Del Pueblo / Kansas City) missing in CRDC collection"},
        {"stage": "4. Consistent Grades 9-12 Reporting in CRDC", "count": 307, "excluded": 10, "pct_retained": 307 / 318 * 100.0, "reason": "10 schools report PS, KG, UG, or G10-12 in CRDC; quarantined for sensitivity analysis"},
    ])
    funnel.to_csv(DATA_PROCESSED / "population_exclusion_funnel.csv", index=False)

    print("\nPanel build complete!")
    print(f"Master panel saved to: {DATA_PROCESSED / 'mo_high_school_crdc_measurement_panel_2021_22.parquet'}")
    print(f"Total rows: {len(tidy_panel)}")


if __name__ == "__main__":
    main()
