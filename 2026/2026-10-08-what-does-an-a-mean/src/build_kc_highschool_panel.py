"""
src/build_kc_highschool_panel.py

Constructs the comprehensive Missouri High School Accountability & Graduation Panel (2022-2025),
with a specialized focal subset on the Kansas City Metropolitan Area.
Integrates:
- Building-level MAP Performance Index (MPI) for Mathematics / Algebra I
- Continuous 4-year graduation rates from official DESE 2022 supporting data
- MSIP 6 Graduation points percentage (2023-2025)
- College and Career Readiness (CCR) graduate percentages
- School poverty (FRPL % and Direct Certification %)
- Attendance, chronic absenteeism, enrollment, and racial demographics
- Kansas City geographic typology (Urban Core KCPS, Public Charter, Inner-Ring Suburban, Outer Suburban)
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent.parent
RAW_APR_DIR = REPO_ROOT / "2026" / "2026-10-04-missouri-accountability-signal" / "data" / "raw" / "apr"
PROCESSED_PANEL_PATH = REPO_ROOT / "2026" / "2026-10-04-missouri-accountability-signal" / "data" / "processed" / "mo_school_accountability_panel.parquet"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "artifacts" / "tables"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

KC_DISTRICTS = {
    # Urban Core
    "KANSAS CITY 33": "Urban Core (KCPS)",
    
    # Public Charters (Kansas City)
    "UNIVERSITY ACADEMY": "Public Charter (KC)",
    "GUADALUPE CENTERS SCHOOLS": "Public Charter (KC)",
    "HOGAN PREPARATORY ACADEMY": "Public Charter (KC)",
    "EWING MARION KAUFFMAN SCHOOL": "Public Charter (KC)",
    "CROSSROADS CHARTER SCHOOLS": "Public Charter (KC)",
    "FRONTIER SCHOOLS": "Public Charter (KC)",
    "DELASALLE CHARTER SCHOOL": "Public Charter (KC)",
    "BROOKSIDE CHARTER SCHOOL": "Public Charter (KC)",
    "KANSAS CITY GIRLS PREP ACADEMY": "Public Charter (KC)",
    "GENESIS SCHOOL INC.": "Public Charter (KC)",
    "HOPE LEADERSHIP ACADEMY": "Public Charter (KC)",
    "LEE A. TOLBERT COMM. ACADEMY": "Public Charter (KC)",
    "ACADÉMIE LAFAYETTE": "Public Charter (KC)",
    "GORDON PARKS ELEM.": "Public Charter (KC)",
    "KANSAS CITY INTERNATIONAL ACAD": "Public Charter (KC)",
    
    # Inner-Ring Suburban
    "INDEPENDENCE 30": "Inner-Ring Suburban",
    "RAYTOWN C-2": "Inner-Ring Suburban",
    "GRANDVIEW C-4": "Inner-Ring Suburban",
    "HICKMAN MILLS C-1": "Inner-Ring Suburban",
    "CENTER 58": "Inner-Ring Suburban",
    
    # Outer Suburban (Jackson, Clay, Platte, Cass)
    "NORTH KANSAS CITY 74": "Outer Suburban",
    "LEE'S SUMMIT R-VII": "Outer Suburban",
    "BLUE SPRINGS R-IV": "Outer Suburban",
    "LIBERTY 53": "Outer Suburban",
    "PARK HILL": "Outer Suburban",
    "FORT OSAGE R-I": "Outer Suburban",
    "GRAIN VALLEY R-V": "Outer Suburban",
    "OAK GROVE R-VI": "Outer Suburban",
    "BELTON 124": "Outer Suburban",
    "RAYMORE-PECULIAR R-II": "Outer Suburban",
    "PLATTE COUNTY R-III": "Outer Suburban",
    "SMITHVILLE R-II": "Outer Suburban",
    "EXCELSIOR SPRINGS 40": "Outer Suburban",
    "KEARNEY R-I": "Outer Suburban",
    "PLEASANT HILL R-III": "Outer Suburban",
    "HARRISONVILLE R-IX": "Outer Suburban",
}

def extract_supporting_grad_data():
    """Extracts building-level graduation and CCR metrics across 2022-2025."""
    records = []
    
    # 2022: Contains continuous 4-year graduation rate
    f22 = RAW_APR_DIR / "mo_apr_supporting_2022_building.xlsx"
    if f22.exists():
        df22 = pd.read_excel(f22)
        df22 = df22[df22["END_GRADE"].astype(str).str.strip() == "12"].copy()
        df22["district_code"] = df22["COUNTY_DISTRICT_CODE"].astype(str).str.zfill(6)
        df22["building_code"] = df22["SCHOOL_CODE"].astype(str).str.zfill(4)
        df22["school_year"] = 2022
        df22["grad_rate_4yr"] = pd.to_numeric(df22["GRAD_CURR_4YR_GRAD_RATE"], errors="coerce")
        df22["grad_rate_5yr"] = pd.to_numeric(df22["GRAD_CURR_5YR_GRAD_RATE"], errors="coerce")
        df22["ccr_grad_pct"] = pd.to_numeric(df22["CCR_CURR_PERCENT_OF_GRADUATES"], errors="coerce")
        df22["adv_cred_pct"] = pd.to_numeric(df22["ADV_CRED_CURR_PERCENT_OF_GRADUATES"], errors="coerce")
        df22["grad_pts_pct"] = 100.0  # Informational year
        df22["grad_cohort_highest"] = "4-Year"
        records.append(df22[["district_code", "building_code", "school_year", "grad_rate_4yr", "grad_rate_5yr", "ccr_grad_pct", "adv_cred_pct", "grad_pts_pct", "grad_cohort_highest"]])
        print(f"[*] Loaded 2022 graduation records: {len(df22)}")

    # 2023-2025: MSIP 6 Supporting reports
    for yr in [2023, 2024, 2025]:
        fpath = RAW_APR_DIR / f"mo_apr_supporting_{yr}_building.xlsx"
        if not fpath.exists():
            continue
        df = pd.read_excel(fpath)
        df = df[df["END_GRADE"].astype(str).str.strip() == "12"].copy()
        df["district_code"] = df["COUNTY_DISTRICT_CODE"].astype(str).str.zfill(6)
        df["building_code"] = df["SCHOOL_CODE"].astype(str).str.zfill(4)
        df["school_year"] = yr
        df["grad_rate_4yr"] = np.nan
        df["grad_rate_5yr"] = np.nan
        df["grad_pts_pct"] = pd.to_numeric(df["GRADUATION_POINTS_EARNED_PCT"], errors="coerce")
        df["grad_cohort_highest"] = df["GRADUATION_COHORT_RATE_HIGHEST"].astype(str)
        df["ccr_grad_pct"] = pd.to_numeric(df["CCR_ASSESSMENTS_GRADUATES_POINTS_EARNED_PCT"], errors="coerce")
        df["adv_cred_pct"] = pd.to_numeric(df["ADV_CRED_GRADUATES_POINTS_EARNED_PCT"], errors="coerce")
        records.append(df[["district_code", "building_code", "school_year", "grad_rate_4yr", "grad_rate_5yr", "ccr_grad_pct", "adv_cred_pct", "grad_pts_pct", "grad_cohort_highest"]])
        print(f"[*] Loaded {yr} graduation records: {len(df)}")

    df_grad = pd.concat(records, ignore_index=True)
    return df_grad

def build_panels():
    # 1. Load master panel
    print(f"[*] Loading master panel from {PROCESSED_PANEL_PATH}")
    df_panel = pd.read_parquet(PROCESSED_PANEL_PATH)
    hs_panel = df_panel[df_panel["school_level"] == "HIGH"].copy()
    print(f"[*] High school rows in panel: {len(hs_panel)}")

    # 2. Extract graduation records
    df_grad = extract_supporting_grad_data()

    # 3. Merge
    hs_merged = pd.merge(
        hs_panel,
        df_grad,
        on=["district_code", "building_code", "school_year"],
        how="left"
    )

    # Propagate 2022 continuous grad rate as baseline attribute for each building
    grad_2022_map = df_grad[df_grad["school_year"] == 2022].set_index(["district_code", "building_code"])["grad_rate_4yr"].to_dict()
    hs_merged["baseline_grad_rate_2022"] = hs_merged.set_index(["district_code", "building_code"]).index.map(grad_2022_map)

    # 4. Classify KC Metro
    def classify_kc(row):
        dname = str(row["DISTRICT_NAME"]).strip().upper()
        sname = str(row["SCHOOL_NAME"]).strip().upper()
        for dkey, category in KC_DISTRICTS.items():
            if dkey in dname or dkey in sname:
                return category
        # Check specific charter school names
        if any(w in sname for w in ["UNIVERSITY ACADEMY", "HOGAN PREP", "KAUFFMAN", "CROSSROADS", "GUADALUPE"]):
            return "Public Charter (KC)"
        return "Rest of Missouri"

    hs_merged["geographic_typology"] = hs_merged.apply(classify_kc, axis=1)
    hs_merged["is_kc_metro"] = hs_merged["geographic_typology"] != "Rest of Missouri"

    # Save statewide high school panel
    out_statewide = PROCESSED_DIR / "mo_high_school_panel.parquet"
    hs_merged.to_parquet(out_statewide, index=False)
    print(f"[*] Saved full high school panel to {out_statewide} ({len(hs_merged)} rows)")

    # Save KC High School panel CSV
    kc_panel = hs_merged[hs_merged["is_kc_metro"]].copy()
    out_kc = PROCESSED_DIR / "kc_high_school_panel.csv"
    kc_panel.to_csv(out_kc, index=False)
    print(f"[*] Saved KC high school panel to {out_kc} ({len(kc_panel)} rows)")

    # 5. Export summary Table 2: 2022 KC High School Benchmark Table
    kc_2022 = kc_panel[kc_panel["school_year"] == 2022].copy()
    t2_cols = [
        "DISTRICT_NAME", "SCHOOL_NAME", "geographic_typology",
        "baseline_grad_rate_2022", "math_status_mpi", "ccr_grad_pct",
        "frpl_pct", "proportional_attendance_pct", "enrollment"
    ]
    t2 = kc_2022[t2_cols].dropna(subset=["baseline_grad_rate_2022", "math_status_mpi"]).sort_values(
        by="math_status_mpi", ascending=False
    )
    t2.columns = [
        "District", "High School", "Typology",
        "Graduation Rate (%)", "Math Status MPI (Alg I)", "CCR Graduate (%)",
        "FRPL Poverty (%)", "Attendance 90/90 (%)", "Enrollment"
    ]
    t2_path = TABLES_DIR / "table2_kc_high_schools_2022_2025.csv"
    t2.to_csv(t2_path, index=False)
    print(f"[*] Saved Table 2 to {t2_path} ({len(t2)} KC High Schools)")
    return hs_merged, kc_panel

if __name__ == "__main__":
    build_panels()
