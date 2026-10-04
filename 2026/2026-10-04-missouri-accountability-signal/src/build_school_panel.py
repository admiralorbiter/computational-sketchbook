"""
src/build_school_panel.py

Constructs the master school-year accountability panel:
data/processed/mo_school_accountability_panel.parquet

Integrates:
- MSIP 6 Building APR Summary & Supporting files (2022-2025)
- Free and Reduced Price Lunch & CEP Participation (2022-2025)
- Student Demographics (Race/ethnicity, IEP, EL/LEP, Title I)
- Attendance and Chronic Absenteeism (Proportional Attendance 90/90)
- Student Mobility Rates
- Prior year achievement, growth, and APR lags
- Analytic sample flags (Sample A, Sample B, Sample C)
- Data suppression and small school indicators
"""

from pathlib import Path
import numpy as np
import pandas as pd
from classify_schools import classify_school_level, assign_sample_flags

BASE_DIR = Path(__file__).resolve().parent.parent
INTERMEDIATE_DIR = BASE_DIR / "data" / "intermediate"
RAW_CONTEXT_DIR = BASE_DIR / "data" / "raw" / "context"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def parse_clean_numeric(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s in ["*", "NULL", "None", "", "N/A", "na"]:
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


def load_frpl_panel():
    """Loads building-level FRPL and CEP flags across 2022-2025 from longitudinal workbook."""
    frpl_file = RAW_CONTEXT_DIR / "mo_frpl_building_2009_2026.xlsx"
    sheet_year_map = {
        "2024-2025": 2025,
        "2023-2024": 2024,
        "2022-2023": 2023,
        "2021-2022": 2022,
    }
    dfs = []
    for sheet_name, yr in sheet_year_map.items():
        df_raw = pd.read_excel(frpl_file, sheet_name=sheet_name, skiprows=9)
        df_sub = df_raw.dropna(subset=["District Code", "BLDG. NO."]).copy()
        
        df_sub["school_year"] = yr
        df_sub["district_code"] = df_sub["District Code"].astype(int).astype(str).str.strip().str.zfill(6)
        df_sub["building_code"] = df_sub["BLDG. NO."].astype(int).astype(str).str.strip().str.zfill(4)
        
        # Identify F&RL percentage column
        pct_col = [c for c in df_sub.columns if "F&RL Percentage" in str(c) or "Percentage" in str(c)]
        if pct_col:
            # Raw F&RL Percentage is on a 0.0 - 1.0 proportion scale.
            # Scale to percentage [0, 100] and clip ratio overages at 100.0
            raw_pct = df_sub[pct_col[0]].apply(parse_clean_numeric)
            df_sub["frpl_pct_file"] = (raw_pct * 100.0).clip(lower=0.0, upper=100.0)
        else:
            df_sub["frpl_pct_file"] = np.nan

        # Membership / count
        count_col = [c for c in df_sub.columns if "F&RL Count" in str(c)]
        df_sub["frpl_count_file"] = df_sub[count_col[0]].apply(parse_clean_numeric) if count_col else np.nan

        # CEP participating flag
        cep_col = [c for c in df_sub.columns if "Community" in str(c) or "CEP" in str(c)]
        if cep_col:
            df_sub["cep_flag"] = df_sub[cep_col[0]].astype(str).str.strip().str.upper().apply(
                lambda x: 1 if x in ["Y", "YES", "TRUE", "1"] else 0
            )
        else:
            df_sub["cep_flag"] = 0

        dfs.append(df_sub[["school_year", "district_code", "building_code", "frpl_pct_file", "frpl_count_file", "cep_flag"]])

    df_frpl_all = pd.concat(dfs, ignore_index=True)
    return df_frpl_all


def load_demographics_panel():
    """Loads student demographic indicators across 2022-2025."""
    p = RAW_CONTEXT_DIR / "mo_building_demographics_2006_2025.xlsx"
    df = pd.read_excel(p)
    df = df[df["YEAR"].isin([2022, 2023, 2024, 2025])].copy()

    df["school_year"] = df["YEAR"].astype(int)
    df["district_code"] = df["COUNTY_DISTRICT_CODE"].astype(str).str.strip().str.zfill(6)
    df["building_code"] = df["SCHOOL_CODE"].astype(str).str.strip().str.zfill(4)

    df["enrollment"] = df["ENROLLMENT_GRADES_K_12"].apply(parse_clean_numeric)
    df["january_membership"] = df["JANUARY_MEMBERSHIP"].apply(parse_clean_numeric)
    raw_demog_frpl = df["LUNCH_COUNT_FREE_REDUCED_PCT"].apply(parse_clean_numeric)
    df["frpl_pct_demog"] = np.where((raw_demog_frpl >= 0) & (raw_demog_frpl <= 100), raw_demog_frpl, np.nan)

    # Racial percentages
    df["race_white_pct"] = df["ENROLLMENT_WHITE_PCT"].apply(parse_clean_numeric)
    df["race_black_pct"] = df["ENROLLMENT_BLACK_PCT"].apply(parse_clean_numeric)
    df["race_hispanic_pct"] = df["ENROLLMENT_HISPANIC_PCT"].apply(parse_clean_numeric)
    df["race_asian_pct"] = df["ENROLLMENT_ASIAN_PCT"].apply(parse_clean_numeric)
    df["race_indian_pct"] = df["ENROLLMENT_INDIAN_PCT"].apply(parse_clean_numeric)
    df["race_multiracial_pct"] = df["ENROLLMENT_MULTIRACIAL_PCT"].apply(parse_clean_numeric)
    df["race_pacific_islander_pct"] = df["ENROLLMENT_PACIFIC_ISLANDER_PCT"].apply(parse_clean_numeric)

    # Combined underrepresented minority (URM) percentage
    df["race_urm_pct"] = (
        df["race_black_pct"].fillna(0) +
        df["race_hispanic_pct"].fillna(0) +
        df["race_indian_pct"].fillna(0) +
        df["race_multiracial_pct"].fillna(0) +
        df["race_pacific_islander_pct"].fillna(0)
    ).clip(lower=0.0, upper=100.0)

    # EL and IEP
    df["ell_pct"] = df["ELL_LEP_STUDENTS_ENROLLED_K_12_PCT"].apply(parse_clean_numeric).clip(lower=0.0, upper=100.0)
    df["iep_pct"] = df["IEP_INCIDENCE_RATE"].apply(parse_clean_numeric).clip(lower=0.0, upper=100.0)
    df["title1_flag"] = df["TITLE1_FLAG"].astype(str).str.strip().str.upper().apply(
        lambda x: 1 if x in ["Y", "YES", "TRUE", "1"] else 0
    )

    keep_cols = [
        "school_year", "district_code", "building_code", "enrollment", "january_membership",
        "frpl_pct_demog", "race_white_pct", "race_black_pct", "race_hispanic_pct",
        "race_asian_pct", "race_indian_pct", "race_multiracial_pct", "race_urm_pct",
        "ell_pct", "iep_pct", "title1_flag"
    ]
    return df[keep_cols]


def load_attendance_panel():
    """Loads proportional attendance rate across 2022-2025."""
    p = RAW_CONTEXT_DIR / "mo_building_attendance_rates.xlsx"
    df = pd.read_excel(p)
    df = df[df["YEAR"].isin([2022, 2023, 2024, 2025])].copy()

    df["school_year"] = df["YEAR"].astype(int)
    df["district_code"] = df["COUNTY_DISTRICT_CODE"].astype(str).str.strip().str.zfill(6)
    df["building_code"] = df["SCHOOL_CODE"].astype(str).str.strip().str.zfill(4)

    df["proportional_attendance_pct"] = df["PROPORTIONAL_ATTENDANCE_TOTAL_PCT"].apply(parse_clean_numeric)
    df["chronic_absence_pct"] = 100.0 - df["proportional_attendance_pct"]

    return df[["school_year", "district_code", "building_code", "proportional_attendance_pct", "chronic_absence_pct"]]


def load_mobility_panel():
    """Loads student mobility rate across 2022-2025."""
    p = RAW_CONTEXT_DIR / "mo_building_mobility_rates.xlsx"
    df = pd.read_excel(p)
    df = df[df["schoolyear"].isin([2022, 2023, 2024, 2025])].copy()

    df["school_year"] = df["schoolyear"].astype(int)
    df["district_code"] = df["districtcode"].astype(str).str.strip().str.zfill(6)
    df["building_code"] = df["schoolcode"].astype(str).str.strip().str.zfill(4)

    df["mobility_pct"] = df["mobilityRate"].apply(parse_clean_numeric)

    return df[["school_year", "district_code", "building_code", "mobility_pct"]]


def build_panel():
    print("[*] Building master school accountability panel...")

    # 1. Load harmonized APR across 2022-2025
    apr_dfs = []
    for yr in [2022, 2023, 2024, 2025]:
        p = INTERMEDIATE_DIR / f"apr_harmonized_{yr}.parquet"
        df_yr = pd.read_parquet(p)
        apr_dfs.append(df_yr)
    df_apr = pd.concat(apr_dfs, ignore_index=True)
    print(f"[*] Loaded {len(df_apr):,} school-year APR records.")

    # 2. Load context panels
    df_frpl = load_frpl_panel()
    df_demog = load_demographics_panel()
    df_att = load_attendance_panel()
    df_mob = load_mobility_panel()

    # 3. Join context with APR
    print("[*] Merging datasets...")
    df_panel = pd.merge(df_apr, df_demog, on=["school_year", "district_code", "building_code"], how="left")
    df_panel = pd.merge(df_panel, df_frpl, on=["school_year", "district_code", "building_code"], how="left")
    df_panel = pd.merge(df_panel, df_att, on=["school_year", "district_code", "building_code"], how="left")
    df_panel = pd.merge(df_panel, df_mob, on=["school_year", "district_code", "building_code"], how="left")

    # Reconcile primary poverty variable:
    # Prefer explicit frpl_pct_file from FRPL table; if missing, fall back to demographics FRPL
    df_panel["frpl_pct"] = df_panel["frpl_pct_file"].combine_first(df_panel["frpl_pct_demog"])
    df_panel["cep_flag"] = df_panel["cep_flag"].fillna(0).astype(int)

    # 4. Classify School Level and Grade Spans
    df_panel["school_level"] = df_panel.apply(
        lambda r: classify_school_level(r["BEG_GRADE"], r["END_GRADE"]), axis=1
    )
    df_panel["grade_low"] = df_panel["BEG_GRADE"]
    df_panel["grade_high"] = df_panel["END_GRADE"]

    # 5. Composite Outcome Measures
    # Status: Mean of ELA and Math MPI
    df_panel["achievement_measure"] = df_panel[["ela_status_mpi", "math_status_mpi"]].mean(axis=1)

    # Growth:
    # 2023-2025: composite growth points percentage
    df_panel["composite_growth_pts_pct"] = df_panel[["ela_growth_pts_pct", "math_growth_pts_pct"]].mean(axis=1)
    # 2022: standardized zscore composite
    df_panel["growth_zscore_composite"] = df_panel[["ela_growth_zscore", "math_growth_zscore"]].mean(axis=1)
    # Generic growth measure: composite points pct for 2023-2025
    df_panel["growth_measure"] = df_panel["composite_growth_pts_pct"]

    # 6. Assign Sample Flags and Exclusions
    df_panel = assign_sample_flags(df_panel)

    # 7. Longitudinal Lags (prior year achievement, growth, APR)
    print("[*] Computing longitudinal lags...")
    df_panel = df_panel.sort_values(["district_code", "building_code", "school_year"]).reset_index(drop=True)

    # Verify building continuity for lags
    df_panel["prior_school_year"] = df_panel.groupby(["district_code", "building_code"])["school_year"].shift(1)
    df_panel["is_consecutive_year"] = (df_panel["school_year"] - df_panel["prior_school_year"]) == 1

    df_panel["prior_year_achievement"] = np.where(
        df_panel["is_consecutive_year"],
        df_panel.groupby(["district_code", "building_code"])["achievement_measure"].shift(1),
        np.nan
    )
    df_panel["prior_year_growth"] = np.where(
        df_panel["is_consecutive_year"],
        df_panel.groupby(["district_code", "building_code"])["growth_measure"].shift(1),
        np.nan
    )
    df_panel["prior_year_apr"] = np.where(
        df_panel["is_consecutive_year"],
        df_panel.groupby(["district_code", "building_code"])["apr_pct"].shift(1),
        np.nan
    )

    # 8. Sample C: Stable Balanced Panel (present in Sample B across all 4 years 2022-2025)
    stable_counts = (
        df_panel[df_panel["sample_b_conventional"] == 1]
        .groupby(["district_code", "building_code"])["school_year"]
        .nunique()
    )
    stable_schools = set(stable_counts[stable_counts == 4].index)
    df_panel["sample_c_stable_panel"] = df_panel.apply(
        lambda r: 1 if (r["district_code"], r["building_code"]) in stable_schools and r["sample_b_conventional"] == 1 else 0,
        axis=1
    )

    # 9. Suppression and Small School Flags
    df_panel["small_school_flag"] = (df_panel["enrollment"] < 100).astype(int)
    df_panel["suppression_flag_achievement"] = (
        df_panel["ela_status_mpi"].isna() | df_panel["math_status_mpi"].isna()
    ).astype(int)
    df_panel["suppression_flag_growth"] = (
        df_panel["growth_measure"].isna() & df_panel["growth_zscore_composite"].isna()
    ).astype(int)

    # Clean string dtypes for Parquet compatibility
    str_cols = [
        "district_code", "building_code", "DISTRICT_NAME", "SCHOOL_NAME",
        "BEG_GRADE", "END_GRADE", "school_level", "grade_low", "grade_high",
        "exclusion_reason", "ela_growth_designation", "math_growth_designation", "science_growth_designation"
    ]
    for c in str_cols:
        if c in df_panel.columns:
            df_panel[c] = df_panel[c].astype("string")

    out_panel = PROCESSED_DIR / "mo_school_accountability_panel.parquet"
    df_panel.to_parquet(out_panel, index=False)
    print(f"\n[SUCCESS] Saved master panel: {len(df_panel):,} rows x {len(df_panel.columns)} columns -> {out_panel}")

    # Summary table by year and sample
    summary = df_panel.groupby("school_year").agg(
        total_schools=("district_code", "count"),
        sample_b_conventional=("sample_b_conventional", "sum"),
        sample_c_stable=("sample_c_stable_panel", "sum"),
        mean_enrollment=("enrollment", "mean"),
        mean_frpl_pct=("frpl_pct", "mean"),
        mean_apr_pct=("apr_pct", "mean"),
        mean_achievement_mpi=("achievement_measure", "mean"),
        mean_growth_pct=("composite_growth_pts_pct", "mean"),
    ).reset_index()
    print("\nMaster Panel Summary by Year:")
    print(summary.to_string(index=False))

    return df_panel


if __name__ == "__main__":
    build_panel()
