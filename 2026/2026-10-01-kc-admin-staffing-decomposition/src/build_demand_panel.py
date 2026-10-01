"""
Build Canonical District Demand & Finance Panel (Phase 2A).

Ingests and harmonizes:
1. Census SAIPE School District Child Poverty (2014–2024).
2. EDFacts / CRDC Special Populations:
   - IDEA School-Age (IEP) counts and shares
   - English Learner (LEP/EL) counts and shares
   - Section 504 accommodation counts and shares
3. Census / NCES F-33 Annual Survey of School System Finances (2014–2023):
   - Categorical revenues: Title I, IDEA, Bilingual Ed
   - Total revenues: Federal, State, Local, Total
   - Functional expenditures: Current Operational, Instruction, General Admin, School Admin, Staff Support
4. Merges 1-to-1 with canonical district_staff_year on (nces_lea_id, school_year).

Produces:
- data/processed/district_demand_year.csv
- data/processed/district_demand_year.parquet
- Updates data/manifest.csv
"""

import sys
import os
import io
import time
import zipfile
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
INTERIM_DEMAND_DIR = DATA_DIR / "interim" / "demand"
PROCESSED_DIR = DATA_DIR / "processed"


def sanitize_num(val):
    """Convert negative exception codes and invalid numbers to NaN."""
    if pd.isna(val):
        return np.nan
    try:
        f = float(val)
        return np.nan if f < 0 else f
    except (ValueError, TypeError):
        return np.nan


def fetch_saipe_data(target_leas: set) -> pd.DataFrame:
    """
    Fetch Census SAIPE child poverty data from Urban Institute API for KS & MO.
    Caches intermediate files to data/interim/demand/saipe_raw.parquet.
    """
    cache_path = INTERIM_DEMAND_DIR / "saipe_raw.parquet"
    if cache_path.exists():
        print(f"Loading cached SAIPE data from {cache_path}")
        df_saipe = pd.read_parquet(cache_path)
        sub = df_saipe[df_saipe["nces_lea_id"].isin(target_leas)].drop_duplicates(subset=["nces_lea_id", "school_year"]).copy()
        return sub

    print("Fetching SAIPE data from Urban Institute API (2014–2024)...")
    records = []
    # Calendar years corresponding to school years 2014-15 (2014) to 2024-25 (2024)
    for year in range(2014, 2025):
        sy = f"{year}-{year+1}"
        for fips in [20, 29]:
            url = f"https://educationdata.urban.org/api/v1/school-districts/saipe/{year}/"
            try:
                resp = requests.get(url, params={"fips": fips, "limit": 1000}, timeout=20)
                if resp.status_code == 200:
                    data = resp.json().get("results", [])
                    for row in data:
                        leaid = str(row.get("leaid", "")).zfill(7)
                        if leaid in target_leas:
                            records.append({
                                "school_year": sy,
                                "saipe_year": year,
                                "nces_lea_id": leaid,
                                "saipe_est_population_total": sanitize_num(row.get("est_population_total")),
                                "saipe_est_population_5_17": sanitize_num(row.get("est_population_5_17")),
                                "saipe_est_population_5_17_poverty": sanitize_num(row.get("est_population_5_17_poverty")),
                                "saipe_poverty_pct": sanitize_num(row.get("est_population_5_17_poverty_pct")),
                            })
                else:
                    print(f"Warning: SAIPE status {resp.status_code} for {year} fips {fips}")
            except Exception as e:
                print(f"Error fetching SAIPE {year} fips {fips}: {e}")

    df_saipe = pd.DataFrame(records).drop_duplicates(subset=["nces_lea_id", "school_year"])
    INTERIM_DEMAND_DIR.mkdir(parents=True, exist_ok=True)
    df_saipe.to_parquet(cache_path, index=False)
    print(f"Cached {len(df_saipe)} SAIPE records to {cache_path}")
    return df_saipe


def fetch_finance_data(target_leas: set) -> pd.DataFrame:
    """
    Fetch Census / NCES F-33 school finance data.
    - FY 2015–2020 (SY 2014-15 to 2019-20): Urban Institute CCD Finance API
    - FY 2021 (SY 2020-21): NCES sdf21_1a.zip
    - FY 2022 (SY 2021-22): NCES sdf22_1a.zip
    - FY 2023 (SY 2022-23): NCES 2025306_2.zip (sdf23_1a.txt)
    """
    cache_path = INTERIM_DEMAND_DIR / "f33_finance_raw.parquet"
    if cache_path.exists():
        print(f"Loading cached F-33 finance data from {cache_path}")
        df_fin = pd.read_parquet(cache_path)
        sub = df_fin[df_fin["nces_lea_id"].isin(target_leas)].drop_duplicates(subset=["nces_lea_id", "school_year"]).copy()
        return sub

    print("Extracting F-33 finance data (2014–2023)...")
    records = []

    # 1. FY 2015–2020 via Urban Institute API (SY 2014-15 through 2019-20)
    for year in range(2015, 2021):
        sy = f"{year-1}-{year}"
        print(f"  Fetching Urban Institute Finance for FY {year} ({sy})...")
        for fips in [20, 29]:
            url = f"https://educationdata.urban.org/api/v1/school-districts/ccd/finance/{year}/"
            try:
                resp = requests.get(url, params={"fips": fips, "limit": 1000}, timeout=30)
                if resp.status_code == 200:
                    data = resp.json().get("results", [])
                    for r in data:
                        leaid = str(r.get("leaid", "")).zfill(7)
                        if leaid in target_leas:
                            records.append({
                                "school_year": sy,
                                "fiscal_year": year,
                                "nces_lea_id": leaid,
                                # Categorical Revenues
                                "rev_fed_state_title_i": sanitize_num(r.get("rev_fed_state_title_i")),
                                "rev_fed_state_idea": sanitize_num(r.get("rev_fed_state_idea")),
                                "rev_fed_state_bilingual_ed": sanitize_num(r.get("rev_fed_state_bilingual_ed")),
                                # Broad Revenues
                                "rev_fed_total": sanitize_num(r.get("rev_fed_total")),
                                "rev_state_total": sanitize_num(r.get("rev_state_total")),
                                "rev_local_total": sanitize_num(r.get("rev_local_total")),
                                "rev_total": sanitize_num(r.get("rev_total")),
                                # Expenditures
                                "exp_total": sanitize_num(r.get("exp_total")),
                                "exp_current_elsec_total": sanitize_num(r.get("exp_current_elsec_total")),
                                "exp_current_instruction_total": sanitize_num(r.get("exp_current_instruction_total")),
                                "exp_current_general_admin": sanitize_num(r.get("exp_current_general_admin")),
                                "exp_current_sch_admin": sanitize_num(r.get("exp_current_sch_admin")),
                                "exp_current_instruc_staff": sanitize_num(r.get("exp_current_instruc_staff")),
                            })
                else:
                    print(f"Warning: Finance API status {resp.status_code} for {year} fips {fips}")
            except Exception as e:
                print(f"Error fetching Finance {year} fips {fips}: {e}")

    # 2. FY 2021 via NCES sdf21_1a.zip (SY 2020-2021)
    print("  Fetching NCES F-33 FY 2021 (2020-2021)...")
    url21 = "https://nces.ed.gov/ccd/Data/zip/sdf21_1a.zip"
    r21 = requests.get(url21, timeout=60)
    with zipfile.ZipFile(io.BytesIO(r21.content)) as z:
        with z.open("sdf21_1a.txt") as f:
            df21 = pd.read_csv(f, sep="\t", dtype=str, encoding="latin1")
            df21["LEAID"] = df21["LEAID"].str.zfill(7)
            df21_kc = df21[df21["LEAID"].isin(target_leas)]
            for _, r in df21_kc.iterrows():
                records.append({
                    "school_year": "2020-2021",
                    "fiscal_year": 2021,
                    "nces_lea_id": r["LEAID"],
                    "rev_fed_state_title_i": sanitize_num(r.get("C14")),
                    "rev_fed_state_idea": sanitize_num(r.get("C15")),
                    "rev_fed_state_bilingual_ed": sanitize_num(r.get("B11")),
                    "rev_fed_total": sanitize_num(r.get("TFEDREV")),
                    "rev_state_total": sanitize_num(r.get("TSTREV")),
                    "rev_local_total": sanitize_num(r.get("TLOCREV")),
                    "rev_total": sanitize_num(r.get("TOTALREV")),
                    "exp_total": sanitize_num(r.get("TOTALEXP")),
                    "exp_current_elsec_total": sanitize_num(r.get("TCURELSC")),
                    "exp_current_instruction_total": sanitize_num(r.get("TCURINST")),
                    "exp_current_general_admin": sanitize_num(r.get("V21")),
                    "exp_current_sch_admin": sanitize_num(r.get("V15")),
                    "exp_current_instruc_staff": sanitize_num(r.get("V13")),
                })

    # 3. FY 2022 via NCES sdf22_1a.zip (SY 2021-2022)
    print("  Fetching NCES F-33 FY 2022 (2021-2022)...")
    url22 = "https://nces.ed.gov/ccd/Data/zip/sdf22_1a.zip"
    r22 = requests.get(url22, timeout=60)
    with zipfile.ZipFile(io.BytesIO(r22.content)) as z:
        with z.open("sdf22_1a.txt") as f:
            df22 = pd.read_csv(f, sep="\t", dtype=str, encoding="latin1")
            df22["LEAID"] = df22["LEAID"].str.zfill(7)
            df22_kc = df22[df22["LEAID"].isin(target_leas)]
            for _, r in df22_kc.iterrows():
                records.append({
                    "school_year": "2021-2022",
                    "fiscal_year": 2022,
                    "nces_lea_id": r["LEAID"],
                    "rev_fed_state_title_i": sanitize_num(r.get("C14")),
                    "rev_fed_state_idea": sanitize_num(r.get("C15")),
                    "rev_fed_state_bilingual_ed": sanitize_num(r.get("B11")),
                    "rev_fed_total": sanitize_num(r.get("TFEDREV")),
                    "rev_state_total": sanitize_num(r.get("TSTREV")),
                    "rev_local_total": sanitize_num(r.get("TLOCREV")),
                    "rev_total": sanitize_num(r.get("TOTALREV")),
                    "exp_total": sanitize_num(r.get("TOTALEXP")),
                    "exp_current_elsec_total": sanitize_num(r.get("TCURELSC")),
                    "exp_current_instruction_total": sanitize_num(r.get("TCURINST")),
                    "exp_current_general_admin": sanitize_num(r.get("V21")),
                    "exp_current_sch_admin": sanitize_num(r.get("V15")),
                    "exp_current_instruc_staff": sanitize_num(r.get("V13")),
                })

    # 4. FY 2023 via NCES 2025306_2.zip (SY 2022-2023)
    print("  Fetching NCES F-33 FY 2023 (2022-2023)...")
    url23 = "https://nces.ed.gov/sites/default/files/data-asset/ccd-common-core-data/2025/09/documentation-nces-common-core-data-school-district-finance-survey-f-33-school-year-2022-23-fiscal/2025306_2.zip"
    r23 = requests.get(url23, timeout=60)
    with zipfile.ZipFile(io.BytesIO(r23.content)) as z:
        with z.open("sdf23_1a.txt") as f:
            df23 = pd.read_csv(f, sep="\t", dtype=str, encoding="latin1")
            df23["LEAID"] = df23["LEAID"].str.zfill(7)
            df23_kc = df23[df23["LEAID"].isin(target_leas)]
            for _, r in df23_kc.iterrows():
                records.append({
                    "school_year": "2022-2023",
                    "fiscal_year": 2023,
                    "nces_lea_id": r["LEAID"],
                    "rev_fed_state_title_i": sanitize_num(r.get("C14")),
                    "rev_fed_state_idea": sanitize_num(r.get("C15")),
                    "rev_fed_state_bilingual_ed": sanitize_num(r.get("B11")),
                    "rev_fed_total": sanitize_num(r.get("TFEDREV")),
                    "rev_state_total": sanitize_num(r.get("TSTREV")),
                    "rev_local_total": sanitize_num(r.get("TLOCREV")),
                    "rev_total": sanitize_num(r.get("TOTALREV")),
                    "exp_total": sanitize_num(r.get("TOTALEXP")),
                    "exp_current_elsec_total": sanitize_num(r.get("TCURELSC")),
                    "exp_current_instruction_total": sanitize_num(r.get("TCURINST")),
                    "exp_current_general_admin": sanitize_num(r.get("V21")),
                    "exp_current_sch_admin": sanitize_num(r.get("V15")),
                    "exp_current_instruc_staff": sanitize_num(r.get("V13")),
                })

    df_fin = pd.DataFrame(records).drop_duplicates(subset=["nces_lea_id", "school_year"])
    INTERIM_DEMAND_DIR.mkdir(parents=True, exist_ok=True)
    df_fin.to_parquet(cache_path, index=False)
    print(f"Cached {len(df_fin)} F-33 finance records to {cache_path}")
    return df_fin


def load_special_populations(target_leas: set, df_staff_base: pd.DataFrame) -> pd.DataFrame:
    """
    Load IDEA, LEP, and Section 504 accommodation counts from the verified
    kc_school_complexity_panel_2015_2024.csv, aggregate to district level,
    and interpolate intermediate non-survey years with explicit flags.
    """
    comp_path = PROJECT_ROOT.parent / "2026-09-23-kc-education-capacity" / "data" / "processed" / "kc_school_complexity_panel_2015_2024.csv"
    if not comp_path.exists():
        comp_path = PROJECT_ROOT.parents[1] / "kc_education_capacity" / "data" / "processed" / "kc_school_complexity_panel_2015_2024.csv"

    print(f"Loading school complexity panel from {comp_path}...")
    df_comp = pd.read_csv(comp_path, dtype=str)
    df_comp["nces_lea_id"] = df_comp["nces_school_id"].str.zfill(12).str[:7]
    df_comp = df_comp[df_comp["nces_lea_id"].isin(target_leas)].copy()

    # Convert numeric metrics
    for col in ["idea_count", "lep_count", "section_504_count", "enrollment_crdc", "enrollment_total"]:
        df_comp[col] = df_comp[col].apply(sanitize_num)

    # Aggregate to district-year level for observed survey waves
    agg = df_comp.groupby(["school_year", "nces_lea_id"])[["idea_count", "lep_count", "section_504_count"]].sum(min_count=1).reset_index()
    agg["has_observed_special_pops"] = True

    # Build master grid of all (nces_lea_id, school_year) from df_staff_base for modern era
    modern_grid = df_staff_base[df_staff_base["school_year"] >= "2014-2015"][["nces_lea_id", "school_year", "enrollment_total"]].drop_duplicates(subset=["nces_lea_id", "school_year"]).copy()
    merged = pd.merge(modern_grid, agg, on=["nces_lea_id", "school_year"], how="left")
    merged["has_observed_special_pops"] = merged["has_observed_special_pops"].fillna(False)

    # Compute observed rates where enrollment > 0
    enr = merged["enrollment_total"]
    merged["idea_share"] = np.where((enr > 0) & merged["idea_count"].notna(), merged["idea_count"] / enr, np.nan)
    merged["lep_share"] = np.where((enr > 0) & merged["lep_count"].notna(), merged["lep_count"] / enr, np.nan)
    merged["section_504_share"] = np.where((enr > 0) & merged["section_504_count"].notna(), merged["section_504_count"] / enr, np.nan)

    # Sort canonically for interpolation
    merged = merged.sort_values(["nces_lea_id", "school_year"]).reset_index(drop=True)

    # Groupby district and linearly interpolate rates across time (with forward/backward fill for boundary endpoints)
    print("Interpolating demographic rates for non-survey years across balanced district horizons...")
    for share_col in ["idea_share", "lep_share", "section_504_share"]:
        merged[share_col] = merged.groupby("nces_lea_id")[share_col].transform(lambda s: s.interpolate(method="linear").bfill().ffill())

    # Reconstruct imputed counts = interpolated_share * enrollment_total
    merged["idea_count_harmonized"] = np.where(merged["has_observed_special_pops"], merged["idea_count"], merged["idea_share"] * merged["enrollment_total"])
    merged["lep_count_harmonized"] = np.where(merged["has_observed_special_pops"], merged["lep_count"], merged["lep_share"] * merged["enrollment_total"])
    merged["section_504_count_harmonized"] = np.where(merged["has_observed_special_pops"], merged["section_504_count"], merged["section_504_share"] * merged["enrollment_total"])

    merged["flag_interpolated_special_pops"] = ~merged["has_observed_special_pops"]

    out_cols = [
        "nces_lea_id", "school_year",
        "idea_count_harmonized", "idea_share",
        "lep_count_harmonized", "lep_share",
        "section_504_count_harmonized", "section_504_share",
        "flag_interpolated_special_pops"
    ]
    return merged[out_cols].drop_duplicates(subset=["nces_lea_id", "school_year"])


def main():
    print("=" * 75)
    print("BUILDING CANONICAL DISTRICT DEMAND & FINANCE PANEL (PHASE 2A)")
    print("=" * 75)

    staff_path = PROCESSED_DIR / "district_staff_year.csv"
    assert staff_path.exists(), f"Missing canonical staff panel at {staff_path}"
    df_staff = pd.read_csv(staff_path, dtype={"nces_lea_id": str})
    df_staff["nces_lea_id"] = df_staff["nces_lea_id"].str.zfill(7)
    target_leas = set(df_staff["nces_lea_id"].unique())
    print(f"Loaded canonical staff panel with {len(df_staff)} rows across {len(target_leas)} LEAs.")

    # 1. SAIPE Child Poverty
    df_saipe = fetch_saipe_data(target_leas)

    # 2. F-33 Finance Data
    df_fin = fetch_finance_data(target_leas)

    # 3. Special Populations (IDEA, LEP, 504)
    df_spec = load_special_populations(target_leas, df_staff)

    # Assert uniqueness of merge keys
    assert not df_saipe.duplicated(subset=["nces_lea_id", "school_year"]).any(), "Duplicate keys in SAIPE!"
    assert not df_fin.duplicated(subset=["nces_lea_id", "school_year"]).any(), "Duplicate keys in F-33 Finance!"
    assert not df_spec.duplicated(subset=["nces_lea_id", "school_year"]).any(), "Duplicate keys in Special Populations!"

    # 4. Merge All Demand Dimensions 1-to-1 onto df_staff
    print("\nMerging demand and finance dimensions onto canonical panel...")
    df_demand = pd.merge(df_staff, df_saipe.drop(columns=["saipe_year"], errors="ignore"), on=["nces_lea_id", "school_year"], how="left")
    df_demand = pd.merge(df_demand, df_fin.drop(columns=["fiscal_year"], errors="ignore"), on=["nces_lea_id", "school_year"], how="left")
    df_demand = pd.merge(df_demand, df_spec, on=["nces_lea_id", "school_year"], how="left")

    assert len(df_demand) == len(df_staff), f"Row count mismatch! Expected {len(df_staff)}, got {len(df_demand)}"

    # 5. Compute derived demand ratios & financial controls
    print("Computing derived categorical intensity metrics...")
    enr = df_demand["enrollment_total"]
    tch = df_demand["teachers_k12_fte"]
    valid_enr = (enr > 0) & enr.notna()

    # SAIPE poverty child count per 1,000 pupils
    df_demand["saipe_poverty_per_1000_students"] = np.where(
        valid_enr & df_demand["saipe_est_population_5_17_poverty"].notna(),
        (df_demand["saipe_est_population_5_17_poverty"] / enr) * 1000.0,
        np.nan
    )

    # Categorical revenues per pupil
    for rev_col in ["rev_fed_state_title_i", "rev_fed_state_idea", "rev_fed_state_bilingual_ed", "rev_fed_total", "rev_total", "exp_total", "exp_current_elsec_total"]:
        df_demand[f"{rev_col}_per_pupil"] = np.where(
            valid_enr & df_demand[rev_col].notna(),
            df_demand[rev_col] / enr,
            np.nan
        )

    # Special needs load per teacher
    valid_tch = (tch > 0) & tch.notna()
    df_demand["idea_per_teacher"] = np.where(valid_tch & df_demand["idea_count_harmonized"].notna(), df_demand["idea_count_harmonized"] / tch, np.nan)
    df_demand["lep_per_teacher"] = np.where(valid_tch & df_demand["lep_count_harmonized"].notna(), df_demand["lep_count_harmonized"] / tch, np.nan)

    # Sort canonically
    df_demand = df_demand.sort_values(["school_year", "state", "district_name"]).reset_index(drop=True)

    # 6. Save outputs
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    csv_out = PROCESSED_DIR / "district_demand_year.csv"
    parquet_out = PROCESSED_DIR / "district_demand_year.parquet"

    df_demand.to_csv(csv_out, index=False)
    df_demand.to_parquet(parquet_out, index=False)
    print(f"\nSaved canonical Demand CSV: {csv_out} ({len(df_demand)} rows, {len(df_demand.columns)} cols)")
    print(f"Saved canonical Demand Parquet: {parquet_out}")

    # 7. Update data manifest
    sha256 = hashlib.sha256(csv_out.read_bytes()).hexdigest()
    manifest_path = DATA_DIR / "manifest.csv"
    manifest_df = pd.read_csv(manifest_path) if manifest_path.exists() else pd.DataFrame()

    new_row = {
        "dataset_name": "district_demand_year",
        "format": "csv / parquet",
        "rows_count": len(df_demand),
        "columns_count": len(df_demand.columns),
        "years_covered": f"{df_demand['school_year'].min()} to {df_demand['school_year'].max()}",
        "district_count": df_demand["nces_lea_id"].nunique(),
        "balanced_presence_cohort_55": len(df_demand[df_demand["is_balanced_presence_cohort_55"]]["nces_lea_id"].unique()),
        "complete_outcome_cohort_53": len(df_demand[df_demand["is_complete_outcome_cohort_53"]]["nces_lea_id"].unique()),
        "sha256": sha256,
        "calibration_phase": "Phase 2A Demand & Finance Ingestion",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    # Append or replace
    manifest_df = manifest_df[manifest_df["dataset_name"] != "district_demand_year"]
    manifest_df = pd.concat([manifest_df, pd.DataFrame([new_row])], ignore_index=True)
    manifest_df.to_csv(manifest_path, index=False)
    print(f"Updated manifest at {manifest_path}")

    # Quick diagnostic coverage report on balanced 55 cohort
    b55_modern = df_demand[(df_demand["school_year"] >= "2014-2015") & df_demand["is_balanced_presence_cohort_55"]]
    print("\nBalanced 55 Cohort Modern Era (2014–2024) Coverage:")
    print(f"  Total District-Years: {len(b55_modern)} (55 * 11 = 605 expected)")
    print(f"  Valid SAIPE Poverty: {b55_modern['saipe_poverty_pct'].notna().sum()} / {len(b55_modern)} ({b55_modern['saipe_poverty_pct'].notna().mean()*100:.1f}%)")
    print(f"  Valid IDEA Count: {b55_modern['idea_count_harmonized'].notna().sum()} / {len(b55_modern)} ({b55_modern['idea_count_harmonized'].notna().mean()*100:.1f}%)")
    print(f"  Valid LEP Count: {b55_modern['lep_count_harmonized'].notna().sum()} / {len(b55_modern)} ({b55_modern['lep_count_harmonized'].notna().mean()*100:.1f}%)")
    fin_years = b55_modern[b55_modern["school_year"] <= "2022-2023"]
    print(f"  Valid F-33 Finance (2014-2023): {fin_years['rev_total'].notna().sum()} / {len(fin_years)} ({fin_years['rev_total'].notna().mean()*100:.1f}%)")


if __name__ == "__main__":
    main()
