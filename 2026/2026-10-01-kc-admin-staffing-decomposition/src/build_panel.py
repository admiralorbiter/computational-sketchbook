"""
Build Canonical Longitudinal District-Staff-Year Panel (2004–2024).

Integrates official NCES CCD LEA releases (2014-15 through 2024-25)
with harmonized historical CCD files (2004-05 through 2013-14)
across all public school districts in the 9-county Kansas City MARC region.
Computes multi-denominator staffing intensity metrics and enforces zero-negative assertions.
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import requests

# Local imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from taxonomy import sanitize_negative_codes, compute_derived_metrics

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Target MARC 9 Counties
TARGET_COUNTIES = {
    "29095": "Jackson County",
    "29047": "Clay County",
    "29165": "Platte County",
    "29037": "Cass County",
    "29177": "Ray County",
    "20091": "Johnson County",
    "20209": "Wyandotte County",
    "20103": "Leavenworth County",
    "20121": "Miami County",
}

# Typology Mapping
def classify_district_typology(leaid_str: str, name: str, state: str) -> tuple[str, str]:
    """Returns (agency_type_group, typology)."""
    name_upper = str(name).upper()
    leaid_str = str(leaid_str).zfill(7)

    # Specialized State Agencies
    if any(k in name_upper for k in ["BLIND", "DEAF", "PENITENTIARY", "YOUTH SERVICE", "SEV DISABLED", "SEVERELY DISABLED"]):
        return "Specialized State Agency", "Specialized State Agency"

    # Charters (primarily Missouri Jackson County LEAs starting with 29000xx, 29005xx, 29006xx or containing ACADEMY/CHARTER)
    if state == "MO" and (leaid_str.startswith("2900") or any(k in name_upper for k in ["CHARTER", "ACADEMY", "PREPARATORY", "ALLEN VILLAGE", "SCUOLA", "KIP"])):
        return "Charter LEA", "Charter LEA"

    # Urban Core Unified
    if any(k in name_upper for k in ["KANSAS CITY 33", "CENTER 58"]) or (state == "KS" and "KANSAS CITY" in name_upper and "PIPER" not in name_upper and "TURNER" not in name_upper):
        return "Regular Public District", "Urban Core Unified"

    # Major Suburban Unified
    major_subs = [
        "SHAWNEE MISSION", "BLUE VALLEY", "OLATHE", "NORTH KANSAS CITY",
        "LEE'S SUMMIT", "LEE`S SUMMIT", "BLUE SPRINGS", "LIBERTY 53", "PARK HILL",
        "INDEPENDENCE 30", "RAYTOWN", "RAYMORE-PECULIAR"
    ]
    if any(k in name_upper for k in major_subs):
        return "Regular Public District", "Major Suburban Unified"

    # Independent Town / Exurban
    exurban = [
        "LANSING", "LEAVENWORTH", "BASEHOR-LINWOOD", "GARDNER EDGERTON", "DE SOTO",
        "SPRING HILL", "TURNER", "PIPER", "BONNER SPRINGS", "BELTON", "KEARNEY",
        "SMITHVILLE", "EXCELSIOR SPRINGS", "HARRISONVILLE", "PLEASANT HILL",
        "FORT OSAGE", "GRAIN VALLEY", "GRANDVIEW", "PLATTE CO", "PAOLA", "LOUISBURG", "OSAWATOMIE", "TONGANOXIE"
    ]
    if any(k in name_upper for k in exurban):
        return "Regular Public District", "Independent Town / Exurban"

    # All other regular districts are Rural / Peripheral
    return "Regular Public District", "Rural / Peripheral"


def fetch_historical_slice(target_leas: set) -> pd.DataFrame:
    """
    Fetch and harmonize CCD LEA historical data (2004–2013)
    from Urban Institute Education Data API, caching locally.
    """
    cache_path = INTERIM_DIR / "ccd_lea_historical_2004_2013.parquet"
    if cache_path.exists():
        print(f"Loading cached historical data from {cache_path}")
        return pd.read_parquet(cache_path)

    print("Fetching historical 2004-2013 data from Urban Institute API...")
    records = []
    years = range(2004, 2014)

    for y in years:
        sy = f"{y}-{y+1}"
        for fips in [20, 29]:
            url = f"https://educationdata.urban.org/api/v1/school-districts/ccd/directory/{y}/?fips={fips}"
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200:
                    data = resp.json().get("results", [])
                    for row in data:
                        lid = str(row.get("leaid")).zfill(7)
                        if lid in target_leas:
                            records.append({
                                "school_year": sy,
                                "nces_lea_id": lid,
                                "district_name": row.get("lea_name", "").strip(),
                                "lea_name": row.get("lea_name", "").strip(),
                                "state": "KS" if str(row.get("fips")) == "20" else "MO",
                                "county_code": str(row.get("county_code", "")).zfill(5),
                                "county_primary": TARGET_COUNTIES.get(str(row.get("county_code", "")).zfill(5), "Unknown"),
                                "operating_schools_count": sanitize_negative_codes(row.get("number_of_schools")),
                                "regular_schools_count": sanitize_negative_codes(row.get("number_of_schools")),
                                "enrollment_total": sanitize_negative_codes(row.get("enrollment")),
                                "enrollment_pk": sanitize_negative_codes(row.get("enrollment_pk")),
                                "enrollment_k12": sanitize_negative_codes(row.get("enrollment")),
                                "enrollment_kg": sanitize_negative_codes(row.get("enrollment_kg")),
                                "teachers_prek_fte": sanitize_negative_codes(row.get("teachers_prek_fte")),
                                "teachers_kindergarten_fte": sanitize_negative_codes(row.get("teachers_kindergarten_fte")),
                                "teachers_elementary_fte": sanitize_negative_codes(row.get("teachers_elementary_fte")),
                                "teachers_secondary_fte": sanitize_negative_codes(row.get("teachers_secondary_fte")),
                                "teachers_ungraded_fte": sanitize_negative_codes(row.get("teachers_ungraded_fte")),
                                "teachers_total_reported_fte": sanitize_negative_codes(row.get("teachers_total_fte")),
                                "teachers_k12_fte": sanitize_negative_codes(row.get("teachers_total_fte")),
                                "paraprofessionals_fte": sanitize_negative_codes(row.get("instructional_aides_fte")),
                                "instructional_coordinators_fte": sanitize_negative_codes(row.get("coordinators_fte")),
                                "counselors_fte": sanitize_negative_codes(row.get("guidance_counselors_total_fte")),
                                "psychologists_fte": sanitize_negative_codes(row.get("school_psychologists_fte")),
                                "student_support_staff_fte": sanitize_negative_codes(row.get("support_staff_students_fte")),
                                "librarians_fte": sanitize_negative_codes(row.get("librarian_specialists_fte")),
                                "school_administrators_fte": sanitize_negative_codes(row.get("school_administrators_fte")),
                                "school_admin_support_fte": sanitize_negative_codes(row.get("school_admin_support_staff_fte")),
                                "lea_administrators_fte": sanitize_negative_codes(row.get("lea_administrators_fte")),
                                "lea_admin_support_fte": sanitize_negative_codes(row.get("lea_admin_support_staff_fte")),
                                "other_support_staff_fte": sanitize_negative_codes(row.get("support_staff_other_fte")),
                                "total_staff_fte": sanitize_negative_codes(row.get("staff_total_fte")),
                                "data_source_layer": "Urban_Institute_CCD_Historical_API",
                            })
                else:
                    print(f"Warning: Failed to fetch {sy} fips {fips}: status {resp.status_code}")
            except Exception as e:
                print(f"Error fetching {sy} fips {fips}: {e}")

    df_hist = pd.DataFrame(records)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    df_hist.to_parquet(cache_path, index=False)
    print(f"Cached {len(df_hist)} historical records to {cache_path}")
    return df_hist


def main():
    print("=" * 70)
    print("BUILDING CANONICAL DISTRICT-STAFF-YEAR PANEL (2004–2024)")
    print("=" * 70)

    # 1. Load verified 2014-15 through 2024-25 baseline LEA panel
    baseline_path = PROJECT_ROOT.parent / "2026-09-23-kc-education-capacity" / "data" / "processed" / "kc_lea_capacity_long_2014_15_2024_25.csv"
    if not baseline_path.exists():
        # Fallback to root junction
        baseline_path = PROJECT_ROOT.parents[1] / "kc_education_capacity" / "data" / "processed" / "kc_lea_capacity_long_2014_15_2024_25.csv"
    
    print(f"Loading baseline modern panel from: {baseline_path}")
    df_modern = pd.read_csv(baseline_path)
    df_modern["nces_lea_id"] = df_modern["nces_lea_id"].astype(str).str.zfill(7)
    df_modern["data_source_layer"] = "NCES_CCD_LEA_Official_Releases"

    # Identify master list of 9-county target LEAs
    target_leas = set(df_modern["nces_lea_id"].unique())
    print(f"Target LEAs across 9-county MARC region: {len(target_leas)}")

    # 2. Fetch and harmonize historical 2004-05 through 2013-14 panel
    df_hist = fetch_historical_slice(target_leas)

    # Reconcile columns
    common_cols = [
        "school_year", "nces_lea_id", "district_name", "lea_name", "state", "county_primary",
        "operating_schools_count", "regular_schools_count", "enrollment_total", "enrollment_pk",
        "enrollment_k12", "enrollment_kg", "teachers_prek_fte", "teachers_kindergarten_fte",
        "teachers_elementary_fte", "teachers_secondary_fte", "teachers_ungraded_fte",
        "teachers_total_reported_fte", "teachers_k12_fte", "paraprofessionals_fte",
        "instructional_coordinators_fte", "counselors_fte", "psychologists_fte",
        "student_support_staff_fte", "librarians_fte", "school_administrators_fte",
        "school_admin_support_fte", "lea_administrators_fte", "lea_admin_support_fte",
        "other_support_staff_fte", "total_staff_fte", "data_source_layer"
    ]

    for c in common_cols:
        if c not in df_modern.columns:
            df_modern[c] = np.nan
        if c not in df_hist.columns:
            df_hist[c] = np.nan

    df_combined = pd.concat([df_hist[common_cols], df_modern[common_cols]], ignore_index=True)
    df_combined["nces_lea_id"] = df_combined["nces_lea_id"].astype(str).str.zfill(7)

    # 3. Clean and sanitize all numerical columns
    num_cols = [
        "operating_schools_count", "regular_schools_count", "enrollment_total", "enrollment_pk",
        "enrollment_k12", "teachers_k12_fte", "paraprofessionals_fte",
        "instructional_coordinators_fte", "counselors_fte", "psychologists_fte",
        "student_support_staff_fte", "librarians_fte", "school_administrators_fte",
        "school_admin_support_fte", "lea_administrators_fte", "lea_admin_support_fte",
        "other_support_staff_fte", "total_staff_fte"
    ]
    for col in num_cols:
        df_combined[col] = df_combined[col].apply(sanitize_negative_codes)

    # If student_support_staff_fte is NaN but counselors_fte is populated, construct composite
    # or preserve counselors_fte
    df_combined["student_support_staff_fte"] = df_combined["student_support_staff_fte"].fillna(df_combined["counselors_fte"])

    # If total_staff_fte is unpopulated (common in early 2000s), construct structural sum
    calc_total_staff = (
        df_combined["teachers_k12_fte"].fillna(0)
        + df_combined["paraprofessionals_fte"].fillna(0)
        + df_combined["school_administrators_fte"].fillna(0)
        + df_combined["lea_administrators_fte"].fillna(0)
        + df_combined["instructional_coordinators_fte"].fillna(0)
        + df_combined["student_support_staff_fte"].fillna(0)
        + df_combined["school_admin_support_fte"].fillna(0)
        + df_combined["lea_admin_support_fte"].fillna(0)
        + df_combined["other_support_staff_fte"].fillna(0)
    )
    calc_series = pd.Series(np.where(calc_total_staff > 0, calc_total_staff, np.nan), index=df_combined.index)
    df_combined["total_staff_fte"] = df_combined["total_staff_fte"].fillna(calc_series)

    # 4. Attach typology and governance categories
    groups = []
    typos = []
    for _, row in df_combined.iterrows():
        grp, typ = classify_district_typology(row["nces_lea_id"], row["district_name"], row["state"])
        groups.append(grp)
        typos.append(typ)
    df_combined["agency_type_group"] = groups
    df_combined["typology"] = typos

    # 5. Compute derived multi-denominator intensity metrics
    print("Computing derived multi-denominator intensity metrics...")
    df_final = compute_derived_metrics(df_combined)

    # Sort canonically
    df_final = df_final.sort_values(["school_year", "state", "district_name"]).reset_index(drop=True)

    # 6. Save processed outputs
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    csv_out = PROCESSED_DIR / "district_staff_year.csv"
    parquet_out = PROCESSED_DIR / "district_staff_year.parquet"
    df_final.to_csv(csv_out, index=False)
    df_final.to_parquet(parquet_out, index=False)
    print(f"Saved canonical CSV to: {csv_out} ({len(df_final)} rows, {len(df_final.columns)} cols)")
    print(f"Saved canonical Parquet to: {parquet_out}")

    # 7. Generate data manifest
    sha256 = hashlib.sha256(csv_out.read_bytes()).hexdigest()
    manifest_row = {
        "dataset_name": "district_staff_year",
        "relative_path": "data/processed/district_staff_year.csv",
        "record_count": len(df_final),
        "columns_count": len(df_final.columns),
        "years_covered": f"{df_final['school_year'].min()} to {df_final['school_year'].max()}",
        "district_count": df_final["nces_lea_id"].nunique(),
        "sha256": sha256,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_df = pd.DataFrame([manifest_row])
    manifest_df.to_csv(DATA_DIR / "manifest.csv", index=False)
    print(f"Updated manifest at {DATA_DIR / 'manifest.csv'}")

    print("\nSummary of records by school year:")
    print(df_final.groupby("school_year")["nces_lea_id"].count())
    print("\nSummary by typology:")
    print(df_final[df_final["school_year"] == "2024-2025"].groupby("typology")["nces_lea_id"].count())


if __name__ == "__main__":
    main()
