"""
src/build_repaired_chronic_absenteeism_panel.py

Phase 6B Data Repair: Validated Chronic Absenteeism Panel (2017-18 to 2022-23).
Repairs the CRDC demographic summation bug identified in earlier complexity panels:
1. 2017-18 CRDC: Uses TOTAL_STUDENTS_REPORTED_M + TOTAL_STUDENTS_REPORTED_F
   (identical to the sum of the 14 mutually exclusive race x sex columns).
2. 2020-21 CRDC: Sums ONLY the 14 mutually exclusive race x sex columns
   (SCH_ABSENT_AM_M ... SCH_ABSENT_WH_F), strictly excluding overlapping
   subgroup columns (IDEA, 504, LEP, Homeless) that previously caused >100% rates.
3. 2021-22 & 2022-23 EDFacts: Ingests official FS195 DG814 LEA files (SUBGROUP == 'ALLLEA').
4. Validates bounded rationality on every observation:
   0 <= chronic_absent_count <= enrollment_denominator and 0% <= chronic_absent_rate_pct <= 100%.
"""

from pathlib import Path
import zipfile
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
OUTPUTS_TABLES = PROJECT_ROOT / "outputs" / "tables"

# Path to capacity sister repository containing raw CRDC and EDFacts zips
SISTER_REPO = PROJECT_ROOT.parent / "2026-09-23-kc-education-capacity"
CRDC_DIR = SISTER_REPO / "data" / "raw" / "crdc"
EDFACTS_DIR = SISTER_REPO / "data" / "raw" / "edfacts"


def build_chronic_absenteeism_panel() -> pd.DataFrame:
    # Load 55 balanced cohort LEAs and enrollment benchmarks
    staff_path = DATA_PROCESSED / "district_staff_year.csv"
    df_staff = pd.read_csv(staff_path)
    b55_staff = df_staff[df_staff["is_balanced_presence_cohort_55"] == 1].copy()

    lea_info = b55_staff[["nces_lea_id", "district_name", "state"]].drop_duplicates("nces_lea_id")
    lea_ids = set(lea_info["nces_lea_id"].astype(str).str.zfill(7))

    records = []

    # =========================================================
    # Wave 1: 2017-18 (CRDC Baseline)
    # =========================================================
    z18_path = CRDC_DIR / "2017-18-crdc-data.zip"
    if z18_path.exists():
        with zipfile.ZipFile(z18_path) as z:
            with z.open("2017-18-crdc-data-corrected-publication 2/2017-18 Public-Use Files/Data/SCH/EDFacts/CSV/ID 814 SCH - Chronic Absenteeism.csv") as f:
                df18 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df18["leaid"] = df18["NCESLEAID"].astype(str).str.split(".").str[0].str.zfill(7)
                df18_kc = df18[df18["leaid"].isin(lea_ids)].copy()

                m = pd.to_numeric(df18_kc["TOTAL_STUDENTS_REPORTED_M"], errors="coerce").fillna(0).clip(lower=0)
                fem = pd.to_numeric(df18_kc["TOTAL_STUDENTS_REPORTED_F"], errors="coerce").fillna(0).clip(lower=0)
                df18_kc["chronic_absent"] = m + fem

                lea18_sum = df18_kc.groupby("leaid")["chronic_absent"].sum()

                # Get official CCD enrollment for 2017-18
                enr18 = b55_staff[b55_staff["school_year"] == "2017-2018"].set_index(
                    b55_staff[b55_staff["school_year"] == "2017-2018"]["nces_lea_id"].astype(str).str.zfill(7)
                )["enrollment_total"].to_dict()

                for lid, count in lea18_sum.items():
                    den = enr18.get(lid, np.nan)
                    rate = (count / den * 100.0) if (pd.notna(den) and den > 0) else np.nan
                    records.append({
                        "school_year": "2017-2018",
                        "wave_source": "CRDC 2017-18",
                        "nces_lea_id": int(lid),
                        "chronic_absent_count": float(count),
                        "enrollment_denominator": float(den) if pd.notna(den) else np.nan,
                        "chronic_absent_rate_pct": float(rate) if pd.notna(rate) else np.nan
                    })

    # =========================================================
    # Wave 2: 2020-21 (CRDC Pandemic Shock - Repaired)
    # =========================================================
    z21_path = CRDC_DIR / "2020-21-crdc-data.zip"
    if z21_path.exists():
        with zipfile.ZipFile(z21_path) as z:
            with z.open("EDFacts/FS195 DG814/ID 814 SCH - Chronic Absenteeism.csv") as f:
                df21 = pd.read_csv(f, encoding="latin1", low_memory=False)
                df21["leaid"] = df21["LEAID"].astype(str).str.split(".").str[0].str.zfill(7)
                df21_kc = df21[df21["leaid"].isin(lea_ids)].copy()

                # CRITICAL REPAIR: Sum ONLY the 14 mutually exclusive race x sex columns
                race_cols = [
                    "SCH_ABSENT_AM_M", "SCH_ABSENT_AS_M", "SCH_ABSENT_BL_M", "SCH_ABSENT_HI_M",
                    "SCH_ABSENT_MU_M", "SCH_ABSENT_PI_M", "SCH_ABSENT_WH_M",
                    "SCH_ABSENT_AM_F", "SCH_ABSENT_AS_F", "SCH_ABSENT_BL_F", "SCH_ABSENT_HI_F",
                    "SCH_ABSENT_MU_F", "SCH_ABSENT_PI_F", "SCH_ABSENT_WH_F"
                ]
                for c in race_cols:
                    df21_kc[c] = pd.to_numeric(df21_kc[c], errors="coerce").fillna(0).clip(lower=0)

                df21_kc["chronic_absent"] = df21_kc[race_cols].sum(axis=1)
                lea21_sum = df21_kc.groupby("leaid")["chronic_absent"].sum()

                enr21 = b55_staff[b55_staff["school_year"] == "2020-2021"].set_index(
                    b55_staff[b55_staff["school_year"] == "2020-2021"]["nces_lea_id"].astype(str).str.zfill(7)
                )["enrollment_total"].to_dict()

                for lid, count in lea21_sum.items():
                    den = enr21.get(lid, np.nan)
                    rate = (count / den * 100.0) if (pd.notna(den) and den > 0) else np.nan
                    records.append({
                        "school_year": "2020-2021",
                        "wave_source": "CRDC 2020-21 (Repaired)",
                        "nces_lea_id": int(lid),
                        "chronic_absent_count": float(count),
                        "enrollment_denominator": float(den) if pd.notna(den) else np.nan,
                        "chronic_absent_rate_pct": float(rate) if pd.notna(rate) else np.nan
                    })

    # =========================================================
    # Wave 3: 2021-22 (EDFacts FS195)
    # =========================================================
    z22_path = EDFACTS_DIR / "edfacts_chronic_absenteeism_2021_22.zip"
    if z22_path.exists():
        with zipfile.ZipFile(z22_path) as z:
            with z.open("SY2122_DG814PCT_LEA_110124.csv") as f:
                df22 = pd.read_csv(f, low_memory=False)
                df22["leaid"] = df22["LEAID"].astype(str).str.split(".").str[0].str.zfill(7)
                df22_kc = df22[(df22["leaid"].isin(lea_ids)) & (df22["SUBGROUP"] == "ALLLEA")].copy()

                for _, r in df22_kc.iterrows():
                    lid = r["leaid"]
                    num = pd.to_numeric(r["NUMERATOR"], errors="coerce")
                    den = pd.to_numeric(r["DENOMINATOR"], errors="coerce")
                    rate = pd.to_numeric(r["NUMERIC_VALUE"], errors="coerce")
                    records.append({
                        "school_year": "2021-2022",
                        "wave_source": "EDFacts FS195 (2021-22)",
                        "nces_lea_id": int(lid),
                        "chronic_absent_count": float(num) if pd.notna(num) else np.nan,
                        "enrollment_denominator": float(den) if pd.notna(den) else np.nan,
                        "chronic_absent_rate_pct": float(rate) if pd.notna(rate) else np.nan
                    })

    # =========================================================
    # Wave 4: 2022-23 (EDFacts FS195)
    # =========================================================
    z23_path = EDFACTS_DIR / "edfacts_chronic_absenteeism_2022_23.zip"
    if z23_path.exists():
        with zipfile.ZipFile(z23_path) as z:
            with z.open("SY2223_DG814PCT_LEA_082724.csv") as f:
                df23 = pd.read_csv(f, low_memory=False)
                df23["leaid"] = df23["LEAID"].astype(str).str.split(".").str[0].str.zfill(7)
                df23_kc = df23[(df23["leaid"].isin(lea_ids)) & (df23["SUBGROUP"] == "ALLLEA")].copy()

                for _, r in df23_kc.iterrows():
                    lid = r["leaid"]
                    num = pd.to_numeric(r["NUMERATOR"], errors="coerce")
                    den = pd.to_numeric(r["DENOMINATOR"], errors="coerce")
                    rate = pd.to_numeric(r["NUMERIC_VALUE"], errors="coerce")
                    records.append({
                        "school_year": "2022-2023",
                        "wave_source": "EDFacts FS195 (2022-23)",
                        "nces_lea_id": int(lid),
                        "chronic_absent_count": float(num) if pd.notna(num) else np.nan,
                        "enrollment_denominator": float(den) if pd.notna(den) else np.nan,
                        "chronic_absent_rate_pct": float(rate) if pd.notna(rate) else np.nan
                    })

    df_out = pd.DataFrame(records)

    # Merge district names and states
    df_out = pd.merge(df_out, lea_info, on="nces_lea_id", how="left")

    # Order columns
    cols = [
        "school_year",
        "wave_source",
        "nces_lea_id",
        "district_name",
        "state",
        "chronic_absent_count",
        "enrollment_denominator",
        "chronic_absent_rate_pct"
    ]
    df_out = df_out[cols].sort_values(["school_year", "state", "district_name"]).reset_index(drop=True)

    # Strict integrity assertions: all rates must be bounded within [0, 100]%
    valid_rates = df_out["chronic_absent_rate_pct"].dropna()
    assert (valid_rates >= 0.0).all(), "Found negative chronic absenteeism rates!"
    assert (valid_rates <= 100.0).all(), "Found chronic absenteeism rates exceeding 100%!"

    return df_out


def build_attendance_recovery_wide(df_panel: pd.DataFrame) -> pd.DataFrame:
    """
    Pivots chronic absenteeism across waves and computes post-pandemic shocks and recovery changes.
    """
    piv = df_panel.pivot(
        index=["nces_lea_id", "district_name", "state"],
        columns="school_year",
        values="chronic_absent_rate_pct"
    ).reset_index()

    piv = piv.rename(columns={
        "2017-2018": "absent_rate_2017_18_pct",
        "2020-2021": "absent_rate_2020_21_pct",
        "2021-2022": "absent_rate_2021_22_pct",
        "2022-2023": "absent_rate_2022_23_pct"
    })

    # Shocks and Recovery Deltas
    # Shock from pre-pandemic to pandemic onset
    piv["shock_onset_pct_pts"] = piv["absent_rate_2020_21_pct"] - piv["absent_rate_2017_18_pct"]
    # Peak shock from pre-pandemic to 2021-22 Omicron surge
    piv["shock_peak_pct_pts"] = piv["absent_rate_2021_22_pct"] - piv["absent_rate_2017_18_pct"]
    # Recovery from peak shock (2021-22 -> 2022-23): negative values indicate improving attendance
    piv["recovery_delta_2122_to_2223_pct_pts"] = piv["absent_rate_2022_23_pct"] - piv["absent_rate_2021_22_pct"]
    # Net change over the whole disruption (2017-18 -> 2022-23)
    piv["net_disruption_delta_pct_pts"] = piv["absent_rate_2022_23_pct"] - piv["absent_rate_2017_18_pct"]

    return piv.sort_values(["state", "district_name"]).reset_index(drop=True)


def main():
    print("Building Phase 6B: Validated Chronic Absenteeism Panel...")
    panel = build_chronic_absenteeism_panel()
    wide = build_attendance_recovery_wide(panel)

    out_panel_path = DATA_PROCESSED / "district_chronic_absenteeism_panel.csv"
    out_wide_path = OUTPUTS_TABLES / "district_chronic_absenteeism_recovery_wide.csv"

    panel.to_csv(out_panel_path, index=False)
    wide.to_csv(out_wide_path, index=False)

    print(f"Saved long chronic absenteeism panel to {out_panel_path} ({len(panel)} rows)")
    print(f"Saved wide attendance recovery panel to {out_wide_path} ({len(wide)} districts)")

    # Print summary statistics
    print("\nSummary Statistics of Validated Chronic Absenteeism Rates (%):")
    print(panel.groupby("school_year")["chronic_absent_rate_pct"].describe().round(2))

    # Print focal districts
    print("\nFocal District Trajectories:")
    focal_ids = [2007950, 2011640, 2010140, 2922800, 2926070, 2918300]
    sub = wide[wide["nces_lea_id"].isin(focal_ids)][[
        "district_name", "absent_rate_2017_18_pct", "absent_rate_2020_21_pct",
        "absent_rate_2021_22_pct", "absent_rate_2022_23_pct", "recovery_delta_2122_to_2223_pct_pts"
    ]]
    print(sub.to_string(index=False))


if __name__ == "__main__":
    main()
