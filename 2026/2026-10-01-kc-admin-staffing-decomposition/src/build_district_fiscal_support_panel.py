"""
build_district_fiscal_support_panel.py

Constructs the canonical longitudinal District Fiscal Support Panel (Gate 6C.0)
using raw Census / NCES F-33 Annual Survey of School System Finances files (FY 2015 to FY 2023).

Exact F-33 function mappings:
- Instructional Staff Support (Function 2200): Total = E07, Salaries = V13, Benefits = V14
  -> Non-Personnel Instructional Support: E07 - V13 - V14
- Pupil Support (Function 2100): Total = E17, Salaries = V11, Benefits = V12
  -> Non-Personnel Pupil Support: E17 - V11 - V12
- General Administration (Function 2300): Total = E08, Salaries = V15, Benefits = V16
  -> Non-Personnel General Admin: E08 - V15 - V16
- School Administration (Function 2400): Total = E09, Salaries = V17, Benefits = V18
  -> Non-Personnel School Admin: E09 - V17 - V18

Author: Assistant Pair Programmer
Calibration Phase: Phase 6C.0 Finance Accounting Calibration
"""

import zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw" / "nces_f33"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS_TABLES = ROOT / "outputs" / "tables"

# CPI-U Annual Averages (BLS series CUUR0000SA0) benchmarked to 2023 = 1.0
CPI_U_ANNUAL = {
    2015: 237.017,
    2016: 240.007,
    2017: 245.120,
    2018: 251.107,
    2019: 255.657,
    2020: 258.811,
    2021: 270.970,
    2022: 292.655,
    2023: 304.702,
}
DEFLATOR_TO_2023 = {yr: round(CPI_U_ANNUAL[2023] / val, 4) for yr, val in CPI_U_ANNUAL.items()}

# F-33 Annual Source Archive Mapping
F33_FILES = [
    (2015, "2014-2015", "sdf15_1a.zip", "NCES CCD School District Finance Survey FY 2015 (sdf15_1a.txt)"),
    (2016, "2015-2016", "sdf16_1a.zip", "NCES CCD School District Finance Survey FY 2016 (Sdf16_1a.txt)"),
    (2017, "2016-2017", "sdf17_1a.zip", "NCES CCD School District Finance Survey FY 2017 (sdf17_1a.txt)"),
    (2018, "2017-2018", "sdf18_1a.zip", "NCES CCD School District Finance Survey FY 2018 (sdf18_1a.txt)"),
    (2019, "2018-2019", "sdf19_1a.zip", "NCES CCD School District Finance Survey FY 2019 (sdf19_1a.txt)"),
    (2020, "2019-2020", "sdf20_1a.zip", "NCES CCD School District Finance Survey FY 2020 (sdf20_1a.txt)"),
    (2021, "2020-2021", "sdf21_1a.zip", "NCES CCD School District Finance Survey FY 2021 (sdf21_1a.txt)"),
    (2022, "2021-2022", "sdf22_1a.zip", "NCES CCD School District Finance Survey FY 2022 (sdf22_1a.txt)"),
    (2023, "2022-2023", "sdf23_2025306_2.zip", "NCES CCD School District Finance Survey FY 2023 (sdf23_1a.txt)"),
]


def build_district_fiscal_support_panel() -> pd.DataFrame:
    print("Building Canonical District Fiscal Support Panel (Gate 6C.0)...")

    # 1. Load balanced cohort and architecture panel
    arch_path = DATA_PROCESSED / "district_architecture_panel.csv"
    assert arch_path.exists(), f"Missing {arch_path}"
    df_arch = pd.read_csv(arch_path)

    # Filter architecture panel to the 9 F-33 years (2014-15 to 2022-23)
    target_years = [sy for _, sy, _, _ in F33_FILES]
    df_arch_sub = df_arch[df_arch["school_year"].isin(target_years)].copy()
    bal55_ids = set(df_arch["nces_lea_id"].unique())
    assert len(bal55_ids) == 55

    # 2. Extract raw records from annual F-33 zip archives
    extracted_rows = []
    for fy, sy, zname, src_label in F33_FILES:
        zpath = DATA_RAW / zname
        assert zpath.exists(), f"Missing raw archive: {zpath}"

        with zipfile.ZipFile(zpath) as z:
            data_fn = [f for f in z.namelist() if f.lower().endswith(".txt") or (f.lower().endswith(".csv") and "sdf" in f.lower())][0]
            sep = "\t" if data_fn.lower().endswith(".txt") else ","
            with z.open(data_fn) as f:
                raw_df = pd.read_csv(f, sep=sep, dtype=str, encoding="latin1")

        raw_df["LEAID"] = raw_df["LEAID"].str.zfill(7)
        raw_df["nces_lea_id"] = pd.to_numeric(raw_df["LEAID"], errors="coerce")
        match = raw_df[raw_df["nces_lea_id"].isin(bal55_ids)].copy()
        assert len(match) == 55, f"Expected 55 districts in FY {fy}, found {len(match)}"

        for _, r in match.iterrows():
            def get_num(col: str) -> float:
                val = r.get(col)
                if val is None or pd.isna(val):
                    return 0.0
                try:
                    num = float(val)
                    return num
                except ValueError:
                    return 0.0

            # Raw F-33 codes
            e07 = get_num("E07")
            v13 = get_num("V13")
            v14 = get_num("V14")

            e17 = get_num("E17")
            v11 = get_num("V11")
            v12 = get_num("V12")

            e08 = get_num("E08")
            v15 = get_num("V15")
            v16 = get_num("V16")

            e09 = get_num("E09")
            v17 = get_num("V17")
            v18 = get_num("V18")

            v33 = get_num("V33")
            totalexp = get_num("TOTALEXP")
            tcurelsc = get_num("TCURELSC")
            tcurinst = get_num("TCURINST")

            extracted_rows.append({
                "nces_lea_id": int(r["nces_lea_id"]),
                "school_year": sy,
                "fiscal_year": fy,
                "f33_source_file": data_fn,
                "f33_source_dataset": src_label,
                "cpi_u_annual": CPI_U_ANNUAL[fy],
                "cpi_u_deflator_to_2023": DEFLATOR_TO_2023[fy],
                "enrollment_f33_v33": v33,
                "exp_total_f33": totalexp,
                "exp_current_elsec_f33": tcurelsc,
                "exp_current_instruction_f33": tcurinst,
                # Function 2200: Instructional Staff Support
                "instr_support_total_e07": e07,
                "instr_support_salary_v13": v13,
                "instr_support_benefits_v14": v14,
                "instr_support_nonpersonnel": e07 - v13 - v14,
                # Function 2100: Pupil Support
                "pupil_support_total_e17": e17,
                "pupil_support_salary_v11": v11,
                "pupil_support_benefits_v12": v12,
                "pupil_support_nonpersonnel": e17 - v11 - v12,
                # Function 2300: General Administration
                "general_admin_total_e08": e08,
                "general_admin_salary_v15": v15,
                "general_admin_benefits_v16": v16,
                "general_admin_nonpersonnel": e08 - v15 - v16,
                # Function 2400: School Administration
                "school_admin_total_e09": e09,
                "school_admin_salary_v17": v17,
                "school_admin_benefits_v18": v18,
                "school_admin_nonpersonnel": e09 - v17 - v18,
            })

    df_f33 = pd.DataFrame(extracted_rows)
    assert len(df_f33) == 495, f"Expected 495 rows, found {len(df_f33)}"

    # 3. Merge with staffing architecture continuous panel
    arch_cols = [
        "nces_lea_id", "school_year", "district_name", "state",
        "enrollment_total", "operating_schools_count", "teachers_k12_fte",
        "instructional_coordinators_fte", "corsup_per_100_teachers",
        "corsup_resid_rate", "schadm_per_school", "schadm_resid_rate",
        "leaadm_per_1000_pupils", "supervisory_per_100_teachers",
        "architecture_quadrant"
    ]
    df_merged = pd.merge(df_arch_sub[arch_cols], df_f33, on=["nces_lea_id", "school_year"])
    assert len(df_merged) == 495

    # 4. Compute Real 2023 Dollar Amounts
    defl = df_merged["cpi_u_deflator_to_2023"]
    df_merged["real_instr_support_total_e07"] = df_merged["instr_support_total_e07"] * defl
    df_merged["real_instr_support_salary_v13"] = df_merged["instr_support_salary_v13"] * defl
    df_merged["real_instr_support_benefits_v14"] = df_merged["instr_support_benefits_v14"] * defl
    df_merged["real_instr_support_nonpersonnel"] = df_merged["instr_support_nonpersonnel"] * defl

    # Real Total & Real Current Instruction
    df_merged["real_exp_current_elsec_f33"] = df_merged["exp_current_elsec_f33"] * defl
    df_merged["real_exp_current_instruction_f33"] = df_merged["exp_current_instruction_f33"] * defl

    # 5. Per-Pupil and Per-Teacher Metrics (using canonical enrollment_total & teachers_k12_fte)
    pupils = df_merged["enrollment_total"].replace(0, np.nan)
    teachers = df_merged["teachers_k12_fte"].replace(0, np.nan)

    df_merged["real_instr_support_total_per_pupil"] = df_merged["real_instr_support_total_e07"] / pupils
    df_merged["real_instr_support_salary_per_pupil"] = df_merged["real_instr_support_salary_v13"] / pupils
    df_merged["real_instr_support_benefits_per_pupil"] = df_merged["real_instr_support_benefits_v14"] / pupils
    df_merged["real_instr_support_nonpersonnel_per_pupil"] = df_merged["real_instr_support_nonpersonnel"] / pupils

    df_merged["real_instr_support_total_per_teacher"] = df_merged["real_instr_support_total_e07"] / teachers
    df_merged["real_instr_support_nonpersonnel_per_teacher"] = df_merged["real_instr_support_nonpersonnel"] / teachers

    # Budget shares within Function 2200 (for diagnostic reference)
    total_e07_safe = df_merged["instr_support_total_e07"].replace(0, np.nan)
    df_merged["instr_support_nonpersonnel_share_pct"] = (df_merged["instr_support_nonpersonnel"] / total_e07_safe) * 100
    df_merged["instr_support_salary_share_pct"] = (df_merged["instr_support_salary_v13"] / total_e07_safe) * 100
    df_merged["instr_support_benefits_share_pct"] = (df_merged["instr_support_benefits_v14"] / total_e07_safe) * 100

    # 6. Strict Validation Assertions
    # A. Zero negative residuals in Function 2200 nonpersonnel
    assert (df_merged["instr_support_nonpersonnel"] >= 0).all(), (
        f"Found negative instr_support_nonpersonnel: {df_merged[df_merged['instr_support_nonpersonnel'] < 0]}"
    )
    # B. General admin nonpersonnel non-negative
    assert (df_merged["general_admin_nonpersonnel"] >= 0).all()
    # C. School admin nonpersonnel non-negative
    assert (df_merged["school_admin_nonpersonnel"] >= 0).all()
    # D. Single documented anomaly in pupil support (-$1,000 in Midway R-I FY 2017)
    neg_pupil = df_merged[df_merged["pupil_support_nonpersonnel"] < 0]
    assert len(neg_pupil) == 1, f"Expected 1 pupil support negative residual, found {len(neg_pupil)}"
    assert neg_pupil.iloc[0]["nces_lea_id"] == 2921060
    assert neg_pupil.iloc[0]["fiscal_year"] == 2017
    assert neg_pupil.iloc[0]["pupil_support_nonpersonnel"] == -1000.0

    # 7. Write to canonical processed panel
    out_csv = DATA_PROCESSED / "district_fiscal_support_panel.csv"
    df_merged.to_csv(out_csv, index=False)
    print(f"Successfully generated {out_csv} ({len(df_merged)} rows, {len(df_merged.columns)} columns)")

    # 8. Produce Archetype Diagnostic Snapshot Table
    focal_ids = [2007950, 2011640, 2010140, 2922800, 2926070, 2918300]
    snap_focal = df_merged[
        (df_merged["nces_lea_id"].isin(focal_ids)) &
        (df_merged["school_year"].isin(["2014-2015", "2018-2019", "2022-2023"]))
    ][[
        "school_year", "fiscal_year", "district_name", "state", "architecture_quadrant",
        "instructional_coordinators_fte", "corsup_per_100_teachers", "corsup_resid_rate",
        "enrollment_total", "instr_support_total_e07", "instr_support_salary_v13",
        "instr_support_benefits_v14", "instr_support_nonpersonnel",
        "real_instr_support_total_per_pupil", "real_instr_support_salary_per_pupil",
        "real_instr_support_nonpersonnel_per_pupil", "instr_support_nonpersonnel_share_pct"
    ]].sort_values(["district_name", "school_year"])

    snap_out = OUTPUTS_TABLES / "district_fiscal_support_focal_snapshots.csv"
    snap_focal.to_csv(snap_out, index=False)
    print(f"Saved focal archetype snapshot table to {snap_out}")

    return df_merged


if __name__ == "__main__":
    build_district_fiscal_support_panel()
