"""
src/harmonize_apr.py

Constructs the comprehensive variable crosswalk (docs/variable_crosswalk.csv)
and harmonizes building APR Summary and Supporting datasets across 2022, 2023, 2024, 2025.
"""

from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_APR_DIR = BASE_DIR / "data" / "raw" / "apr"
INTERMEDIATE_DIR = BASE_DIR / "data" / "intermediate"
DOCS_DIR = BASE_DIR / "docs"
INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

CROSSWALK_ENTRIES = [
    # Canonical: district_code
    {"canonical_variable": "district_code", "year": "2022-2025", "raw_file": "APR Summary / Supporting", "raw_column": "COUNTY_DISTRICT_CODE", "definition": "6-digit state county-district code", "unit": "code", "denominator": "N/A", "suppression_rule": "None", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Zero-padded to 6 characters."},
    # Canonical: building_code
    {"canonical_variable": "building_code", "year": "2022-2025", "raw_file": "APR Summary / Supporting", "raw_column": "SCHOOL_CODE", "definition": "4-digit state school building code", "unit": "code", "denominator": "N/A", "suppression_rule": "None", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Zero-padded to 4 characters."},
    # Canonical: apr_pct
    {"canonical_variable": "apr_pct", "year": "2023-2025", "raw_file": "APR Summary", "raw_column": "TOTAL_POINTS_EARNED_PCT", "definition": "Overall Annual Performance Report percentage score", "unit": "percent", "denominator": "TOTAL_POINTS_POSSIBLE", "suppression_rule": "None", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Standard MSIP 6 APR composite percentage."},
    {"canonical_variable": "apr_pct", "year": "2022", "raw_file": "APR Summary", "raw_column": "PERCENT_POINTS_EARNED", "definition": "Overall Annual Performance Report percentage score (introductory year)", "unit": "percent", "denominator": "TOTAL_POINTS_POSSIBLE", "suppression_rule": "None", "comparability_status": "COMPARABLE_WITH_CAVEAT", "notes": "2022 was introductory pilot year without official classification stakes."},
    # Canonical: apr_points_earned
    {"canonical_variable": "apr_points_earned", "year": "2022-2025", "raw_file": "APR Summary", "raw_column": "TOTAL_POINTS_EARNED", "definition": "Total APR points earned", "unit": "points", "denominator": "TOTAL_POINTS_POSSIBLE", "suppression_rule": "None", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Sum of Performance and Continuous Improvement points earned."},
    # Canonical: apr_points_possible
    {"canonical_variable": "apr_points_possible", "year": "2022-2025", "raw_file": "APR Summary", "raw_column": "TOTAL_POINTS_POSSIBLE", "definition": "Total APR points possible", "unit": "points", "denominator": "N/A", "suppression_rule": "None", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Denominators differ by grade span (e.g. 108-116 for high schools vs 84-92 for K-8)."},
    # Canonical: ela_status_mpi
    {"canonical_variable": "ela_status_mpi", "year": "2023-2025", "raw_file": "APR Supporting", "raw_column": "ELA_ALL_STATUS_MPI", "definition": "English Language Arts MAP Performance Index (All Students)", "unit": "index (100-500)", "denominator": "Accountable students", "suppression_rule": "Suppressed '*' for cell size < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Standardized scale where 300=Basic, 400=Proficient, 500=Advanced."},
    {"canonical_variable": "ela_status_mpi", "year": "2022", "raw_file": "APR Supporting", "raw_column": "ALL_ELA_CURR_MPI", "definition": "English Language Arts MAP Performance Index (All Students)", "unit": "index (100-500)", "denominator": "Accountable students", "suppression_rule": "Suppressed '*' for cell size < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Directly comparable index formula."},
    # Canonical: math_status_mpi
    {"canonical_variable": "math_status_mpi", "year": "2023-2025", "raw_file": "APR Supporting", "raw_column": "MATH_ALL_STATUS_MPI", "definition": "Mathematics MAP Performance Index (All Students)", "unit": "index (100-500)", "denominator": "Accountable students", "suppression_rule": "Suppressed '*' for cell size < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Standardized scale."},
    {"canonical_variable": "math_status_mpi", "year": "2022", "raw_file": "APR Supporting", "raw_column": "ALL_MATH_CURR_MPI", "definition": "Mathematics MAP Performance Index (All Students)", "unit": "index (100-500)", "denominator": "Accountable students", "suppression_rule": "Suppressed '*' for cell size < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Directly comparable index formula."},
    # Canonical: science_status_mpi
    {"canonical_variable": "science_status_mpi", "year": "2023-2025", "raw_file": "APR Supporting", "raw_column": "SCIENCE_ALL_STATUS_MPI", "definition": "Science MAP Performance Index (All Students)", "unit": "index (100-500)", "denominator": "Accountable students", "suppression_rule": "Suppressed '*' for cell size < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Administered in grades 5, 8, and Biology EOC."},
    {"canonical_variable": "science_status_mpi", "year": "2022", "raw_file": "APR Supporting", "raw_column": "ALL_SCIENCE_CURR_MPI", "definition": "Science MAP Performance Index (All Students)", "unit": "index (100-500)", "denominator": "Accountable students", "suppression_rule": "Suppressed '*' for cell size < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Administered in grades 5, 8, and Biology."},
    # Canonical: ela_growth_pts_pct
    {"canonical_variable": "ela_growth_pts_pct", "year": "2023-2025", "raw_file": "APR Supporting", "raw_column": "ELA_ALL_GROWTH_POINTS_EARNED_PCT", "definition": "ELA Growth Points Earned Percentage", "unit": "percent", "denominator": "ELA_ALL_GROWTH_POINTS_POSSIBLE", "suppression_rule": "NULL if unassigned / cell size", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Discrete APR points derived from growth model residuals: 100% (Target), 75% (On-Track), 50% (Approaching), 25% (Emerging), 0% (Floor)."},
    # Canonical: math_growth_pts_pct
    {"canonical_variable": "math_growth_pts_pct", "year": "2023-2025", "raw_file": "APR Supporting", "raw_column": "MATH_ALL_GROWTH_POINTS_EARNED_PCT", "definition": "Math Growth Points Earned Percentage", "unit": "percent", "denominator": "MATH_ALL_GROWTH_POINTS_POSSIBLE", "suppression_rule": "NULL if unassigned / cell size", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Discrete APR points derived from growth model residuals."},
    # Canonical: science_growth_pts_pct
    {"canonical_variable": "science_growth_pts_pct", "year": "2024-2025", "raw_file": "APR Supporting", "raw_column": "SCIENCE_ALL_GROWTH_POINTS_EARNED_PCT", "definition": "Science Growth Points Earned Percentage", "unit": "percent", "denominator": "SCIENCE_ALL_GROWTH_POINTS_POSSIBLE", "suppression_rule": "NULL if unassigned / cell size", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Science growth introduced officially in 2024."},
    # Canonical: 2022 growth zscores
    {"canonical_variable": "ela_growth_zscore", "year": "2022", "raw_file": "APR Supporting", "raw_column": "ALL_ELA_CURR_GROWTH_ZSCORE", "definition": "Continuous standardized growth score in ELA", "unit": "z-score", "denominator": "Standardized", "suppression_rule": "Suppressed '*' / NULL", "comparability_status": "NOT_COMPARABLE", "notes": "Continuous growth score reported in 2022; later years report points and percentage categories."},
    {"canonical_variable": "math_growth_zscore", "year": "2022", "raw_file": "APR Supporting", "raw_column": "ALL_MATH_CURR_GROWTH_ZSCORE", "definition": "Continuous standardized growth score in Math", "unit": "z-score", "denominator": "Standardized", "suppression_rule": "Suppressed '*' / NULL", "comparability_status": "NOT_COMPARABLE", "notes": "Continuous growth score reported in 2022."},
    # Canonical: frpl_pct
    {"canonical_variable": "frpl_pct", "year": "2022-2025", "raw_file": "Demographics / FRPL File", "raw_column": "LUNCH_COUNT_FREE_REDUCED_PCT / F&RL Percentage", "definition": "Percentage of students eligible for free/reduced-price lunch", "unit": "percent", "denominator": "January Membership / Enrollment", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "COMPARABLE_WITH_CAVEAT", "notes": "CEP schools report 100% claiming rate without individual applications. Must be evaluated with cep_flag."},
    # Canonical: cep_flag
    {"canonical_variable": "cep_flag", "year": "2022-2025", "raw_file": "FRPL File", "raw_column": "Community Eligiblity Provision (CEP) Participating Building", "definition": "Indicator if building participates in Community Eligibility Provision", "unit": "indicator (0/1)", "denominator": "N/A", "suppression_rule": "None", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Identifies universal meal claiming schools where FRPL reaches 100% ceiling."},
    # Canonical: enrollment
    {"canonical_variable": "enrollment", "year": "2022-2025", "raw_file": "Demographics / Enrollment File", "raw_column": "ENROLLMENT_GRADES_K_12", "definition": "Total K-12 building enrollment", "unit": "count", "denominator": "N/A", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Official fall K-12 building head count."},
    # Canonical: iep_pct
    {"canonical_variable": "iep_pct", "year": "2022-2025", "raw_file": "Demographics", "raw_column": "IEP_INCIDENCE_RATE", "definition": "Special Education / IEP incidence rate", "unit": "percent", "denominator": "Enrollment", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Building special education percentage."},
    # Canonical: ell_pct
    {"canonical_variable": "ell_pct", "year": "2022-2025", "raw_file": "Demographics", "raw_column": "ELL_LEP_STUDENTS_ENROLLED_K_12_PCT", "definition": "English Language Learner / Limited English Proficient rate", "unit": "percent", "denominator": "Enrollment", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Percentage of K-12 students receiving EL services."},
    # Canonical: attendance_pct
    {"canonical_variable": "attendance_pct", "year": "2022-2025", "raw_file": "Attendance File", "raw_column": "PROPORTIONAL_ATTENDANCE_TOTAL_PCT", "definition": "Proportional Attendance Rate (percentage of students attending >= 90% of time)", "unit": "percent", "denominator": "Total students", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Missouri standard 90/90 attendance measure."},
    # Canonical: mobility_pct
    {"canonical_variable": "mobility_pct", "year": "2022-2025", "raw_file": "Mobility File", "raw_column": "mobilityRate", "definition": "Student mobility rate percentage", "unit": "percent", "denominator": "Enrollment", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "Inbound and outbound student mobility rate."},
    # Canonical: race demographics
    {"canonical_variable": "race_white_pct", "year": "2022-2025", "raw_file": "Demographics", "raw_column": "ENROLLMENT_WHITE_PCT", "definition": "Percentage of enrolled students identifying as White", "unit": "percent", "denominator": "Enrollment", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "DESE race/ethnicity reporting."},
    {"canonical_variable": "race_black_pct", "year": "2022-2025", "raw_file": "Demographics", "raw_column": "ENROLLMENT_BLACK_PCT", "definition": "Percentage of enrolled students identifying as Black/African American", "unit": "percent", "denominator": "Enrollment", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "DESE race/ethnicity reporting."},
    {"canonical_variable": "race_hispanic_pct", "year": "2022-2025", "raw_file": "Demographics", "raw_column": "ENROLLMENT_HISPANIC_PCT", "definition": "Percentage of enrolled students identifying as Hispanic", "unit": "percent", "denominator": "Enrollment", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "DESE race/ethnicity reporting."},
    {"canonical_variable": "race_asian_pct", "year": "2022-2025", "raw_file": "Demographics", "raw_column": "ENROLLMENT_ASIAN_PCT", "definition": "Percentage of enrolled students identifying as Asian", "unit": "percent", "denominator": "Enrollment", "suppression_rule": "Suppressed '*' if < 10", "comparability_status": "DIRECTLY_COMPARABLE", "notes": "DESE race/ethnicity reporting."},
]


def build_variable_crosswalk():
    """Writes the comprehensive variable crosswalk to docs/variable_crosswalk.csv."""
    df_cw = pd.DataFrame(CROSSWALK_ENTRIES)
    cw_path = DOCS_DIR / "variable_crosswalk.csv"
    df_cw.to_csv(cw_path, index=False)
    print(f"[*] Generated variable crosswalk at {cw_path} ({len(df_cw)} entries).")


def parse_clean_numeric(val):
    """Converts raw values to float, handling suppression symbols ('*', 'NULL', blank)."""
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s in ["*", "NULL", "None", "", "N/A", "na"]:
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


def parse_clean_mpi(val):
    """Converts raw MPI to float; scores below 100 (e.g. 0.0 placeholders in non-tested grades) are set to NaN."""
    num = parse_clean_numeric(val)
    if pd.isna(num) or num < 100.0:
        return np.nan
    return num


def harmonize_apr():
    """Harmonizes APR Summary and Supporting datasets for 2022-2025."""
    build_variable_crosswalk()

    years = [2022, 2023, 2024, 2025]
    for yr in years:
        sum_file = RAW_APR_DIR / f"mo_apr_summary_{yr}_building.xlsx"
        sup_file = RAW_APR_DIR / f"mo_apr_supporting_{yr}_building.xlsx"

        print(f"\n[*] Processing APR datasets for year {yr}...")
        df_sum = pd.read_excel(sum_file)
        df_sup = pd.read_excel(sup_file)

        # Standardize join keys
        # County district code: 6 chars string
        df_sum["district_code"] = df_sum["COUNTY_DISTRICT_CODE"].astype(str).str.strip().str.zfill(6)
        df_sup["district_code"] = df_sup["COUNTY_DISTRICT_CODE"].astype(str).str.strip().str.zfill(6)

        # Building code: 4 chars string
        df_sum["building_code"] = df_sum["SCHOOL_CODE"].astype(str).str.strip().str.zfill(4)
        df_sup["building_code"] = df_sup["SCHOOL_CODE"].astype(str).str.strip().str.zfill(4)

        df_sum["school_year"] = yr
        df_sup["school_year"] = yr

        # Clean grade strings
        df_sum["BEG_GRADE"] = df_sum["BEG_GRADE"].astype(str).str.strip()
        df_sum["END_GRADE"] = df_sum["END_GRADE"].astype(str).str.strip()

        # Canonicalize summary fields
        if yr in [2023, 2024, 2025]:
            df_sum["apr_points_possible"] = df_sum["TOTAL_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sum["apr_points_earned"] = df_sum["TOTAL_POINTS_EARNED"].apply(parse_clean_numeric)
            df_sum["apr_pct"] = df_sum["TOTAL_POINTS_EARNED_PCT"].apply(parse_clean_numeric)
            df_sum["performance_points_possible"] = df_sum["PERFORMANCE_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sum["performance_points_earned"] = df_sum["PERFORMANCE_POINTS_EARNED"].apply(parse_clean_numeric)
            df_sum["performance_points_pct"] = df_sum["PERFORMANCE_POINTS_EARNED_PCT"].apply(parse_clean_numeric)
            df_sum["ci_points_possible"] = df_sum["CONTINUOUS_IMPROVEMENT_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sum["ci_points_earned"] = df_sum["CONTINUOUS_IMPROVEMENT_POINTS_EARNED"].apply(parse_clean_numeric)
            df_sum["ci_points_pct"] = df_sum["CONTINUOUS_IMPROVEMENT_POINTS_EARNED_PCT"].apply(parse_clean_numeric)
        else:  # 2022
            df_sum["apr_points_possible"] = df_sum["TOTAL_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sum["apr_points_earned"] = df_sum["TOTAL_POINTS_EARNED"].apply(parse_clean_numeric)
            # In 2022, PERCENT_POINTS_EARNED is a proportion (0-1), scale to 0-100 to match 2023-2025
            df_sum["apr_pct"] = df_sum["PERCENT_POINTS_EARNED"].apply(parse_clean_numeric) * 100.0
            df_sum["performance_points_possible"] = np.nan
            df_sum["performance_points_earned"] = np.nan
            df_sum["performance_points_pct"] = np.nan
            df_sum["ci_points_possible"] = np.nan
            df_sum["ci_points_earned"] = np.nan
            df_sum["ci_points_pct"] = np.nan

        # Canonicalize supporting fields
        if yr in [2023, 2024, 2025]:
            df_sup["ela_status_mpi"] = df_sup["ELA_ALL_STATUS_MPI"].apply(parse_clean_mpi)
            df_sup["math_status_mpi"] = df_sup["MATH_ALL_STATUS_MPI"].apply(parse_clean_mpi)
            df_sup["science_status_mpi"] = df_sup["SCIENCE_ALL_STATUS_MPI"].apply(parse_clean_mpi)
            df_sup["soc_stud_status_mpi"] = df_sup["SOC_STUD_ALL_STATUS_MPI"].apply(parse_clean_mpi)

            df_sup["ela_status_pts_earned"] = df_sup["ELA_ALL_STATUS_POINTS_EARNED"].apply(parse_clean_numeric)
            df_sup["ela_status_pts_possible"] = df_sup["ELA_ALL_STATUS_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sup["ela_status_pts_pct"] = df_sup["ELA_ALL_STATUS_POINTS_EARNED_PCT"].apply(parse_clean_numeric)

            df_sup["math_status_pts_earned"] = df_sup["MATH_ALL_STATUS_POINTS_EARNED"].apply(parse_clean_numeric)
            df_sup["math_status_pts_possible"] = df_sup["MATH_ALL_STATUS_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sup["math_status_pts_pct"] = df_sup["MATH_ALL_STATUS_POINTS_EARNED_PCT"].apply(parse_clean_numeric)

            df_sup["science_status_pts_earned"] = df_sup["SCIENCE_ALL_STATUS_POINTS_EARNED"].apply(parse_clean_numeric)
            df_sup["science_status_pts_possible"] = df_sup["SCIENCE_ALL_STATUS_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sup["science_status_pts_pct"] = df_sup["SCIENCE_ALL_STATUS_POINTS_EARNED_PCT"].apply(parse_clean_numeric)

            # Growth fields
            df_sup["ela_growth_pts_earned"] = df_sup["ELA_ALL_GROWTH_POINTS_EARNED"].apply(parse_clean_numeric)
            df_sup["ela_growth_pts_possible"] = df_sup["ELA_ALL_GROWTH_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sup["ela_growth_pts_pct"] = df_sup["ELA_ALL_GROWTH_POINTS_EARNED_PCT"].apply(parse_clean_numeric)
            df_sup["ela_growth_designation"] = df_sup["ELA_ALL_GROWTH_PERFORMANCE_DESIGNATION"].astype(str).str.strip()

            df_sup["math_growth_pts_earned"] = df_sup["MATH_ALL_GROWTH_POINTS_EARNED"].apply(parse_clean_numeric)
            df_sup["math_growth_pts_possible"] = df_sup["MATH_ALL_GROWTH_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sup["math_growth_pts_pct"] = df_sup["MATH_ALL_GROWTH_POINTS_EARNED_PCT"].apply(parse_clean_numeric)
            df_sup["math_growth_designation"] = df_sup["MATH_ALL_GROWTH_PERFORMANCE_DESIGNATION"].astype(str).str.strip()

            df_sup["science_growth_pts_earned"] = df_sup["SCIENCE_ALL_GROWTH_POINTS_EARNED"].apply(parse_clean_numeric)
            df_sup["science_growth_pts_possible"] = df_sup["SCIENCE_ALL_GROWTH_POINTS_POSSIBLE"].apply(parse_clean_numeric)
            df_sup["science_growth_pts_pct"] = df_sup["SCIENCE_ALL_GROWTH_POINTS_EARNED_PCT"].apply(parse_clean_numeric)
            df_sup["science_growth_designation"] = df_sup["SCIENCE_ALL_GROWTH_PERFORMANCE_DESIGNATION"].astype(str).str.strip()

            # Accountable and participant counts
            df_sup["ela_accountable_n"] = df_sup["ELA_ALL_STATUS_ACCOUNTABLE"].apply(parse_clean_numeric)
            df_sup["ela_tested_n"] = df_sup["ELA_ALL_STATUS_PARTICIPANTS"].apply(parse_clean_numeric)
            df_sup["math_accountable_n"] = df_sup["MATH_ALL_STATUS_ACCOUNTABLE"].apply(parse_clean_numeric)
            df_sup["math_tested_n"] = df_sup["MATH_ALL_STATUS_PARTICIPANTS"].apply(parse_clean_numeric)
            df_sup["science_accountable_n"] = df_sup["SCIENCE_ALL_STATUS_ACCOUNTABLE"].apply(parse_clean_numeric)
            df_sup["science_tested_n"] = df_sup["SCIENCE_ALL_STATUS_PARTICIPANTS"].apply(parse_clean_numeric)

            df_sup["ela_growth_zscore"] = np.nan
            df_sup["math_growth_zscore"] = np.nan
        else:  # 2022
            df_sup["ela_status_mpi"] = df_sup["ALL_ELA_CURR_MPI"].apply(parse_clean_mpi)
            df_sup["math_status_mpi"] = df_sup["ALL_MATH_CURR_MPI"].apply(parse_clean_mpi)
            df_sup["science_status_mpi"] = df_sup["ALL_SCIENCE_CURR_MPI"].apply(parse_clean_mpi)
            df_sup["soc_stud_status_mpi"] = df_sup["ALL_SOC_STUD_CURR_MPI"].apply(parse_clean_mpi)

            df_sup["ela_status_pts_earned"] = np.nan
            df_sup["ela_status_pts_possible"] = np.nan
            df_sup["ela_status_pts_pct"] = np.nan

            df_sup["math_status_pts_earned"] = np.nan
            df_sup["math_status_pts_possible"] = np.nan
            df_sup["math_status_pts_pct"] = np.nan

            df_sup["science_status_pts_earned"] = np.nan
            df_sup["science_status_pts_possible"] = np.nan
            df_sup["science_status_pts_pct"] = np.nan

            df_sup["ela_growth_pts_earned"] = np.nan
            df_sup["ela_growth_pts_possible"] = np.nan
            df_sup["ela_growth_pts_pct"] = np.nan
            df_sup["ela_growth_designation"] = np.nan

            df_sup["math_growth_pts_earned"] = np.nan
            df_sup["math_growth_pts_possible"] = np.nan
            df_sup["math_growth_pts_pct"] = np.nan
            df_sup["math_growth_designation"] = np.nan

            df_sup["science_growth_pts_earned"] = np.nan
            df_sup["science_growth_pts_possible"] = np.nan
            df_sup["science_growth_pts_pct"] = np.nan
            df_sup["science_growth_designation"] = np.nan

            df_sup["ela_growth_zscore"] = df_sup["ALL_ELA_CURR_GROWTH_ZSCORE"].apply(parse_clean_numeric)
            df_sup["math_growth_zscore"] = df_sup["ALL_MATH_CURR_GROWTH_ZSCORE"].apply(parse_clean_numeric)

            df_sup["ela_accountable_n"] = np.nan
            df_sup["ela_tested_n"] = np.nan
            df_sup["math_accountable_n"] = np.nan
            df_sup["math_tested_n"] = np.nan
            df_sup["science_accountable_n"] = np.nan
            df_sup["science_tested_n"] = np.nan

        # Merge summary and supporting by building key
        sum_cols_to_keep = [
            "school_year", "district_code", "building_code", "DISTRICT_NAME", "SCHOOL_NAME",
            "BEG_GRADE", "END_GRADE", "apr_points_possible", "apr_points_earned", "apr_pct",
            "performance_points_possible", "performance_points_earned", "performance_points_pct",
            "ci_points_possible", "ci_points_earned", "ci_points_pct"
        ]
        sup_cols_to_keep = [
            "school_year", "district_code", "building_code",
            "ela_status_mpi", "math_status_mpi", "science_status_mpi", "soc_stud_status_mpi",
            "ela_status_pts_earned", "ela_status_pts_possible", "ela_status_pts_pct",
            "math_status_pts_earned", "math_status_pts_possible", "math_status_pts_pct",
            "science_status_pts_earned", "science_status_pts_possible", "science_status_pts_pct",
            "ela_growth_pts_earned", "ela_growth_pts_possible", "ela_growth_pts_pct", "ela_growth_designation",
            "math_growth_pts_earned", "math_growth_pts_possible", "math_growth_pts_pct", "math_growth_designation",
            "science_growth_pts_earned", "science_growth_pts_possible", "science_growth_pts_pct", "science_growth_designation",
            "ela_growth_zscore", "math_growth_zscore",
            "ela_accountable_n", "ela_tested_n", "math_accountable_n", "math_tested_n", "science_accountable_n", "science_tested_n"
        ]

        df_sum_clean = df_sum[sum_cols_to_keep].copy()
        df_sup_clean = df_sup[sup_cols_to_keep].copy()

        df_merged = pd.merge(
            df_sum_clean,
            df_sup_clean,
            on=["school_year", "district_code", "building_code"],
            how="outer",
            validate="1:1"
        )

        # Ensure string types
        str_cols = ["district_code", "building_code", "DISTRICT_NAME", "SCHOOL_NAME", "BEG_GRADE", "END_GRADE",
                    "ela_growth_designation", "math_growth_designation", "science_growth_designation"]
        for c in str_cols:
            if c in df_merged.columns:
                df_merged[c] = df_merged[c].astype("string")

        out_intermediate = INTERMEDIATE_DIR / f"apr_harmonized_{yr}.parquet"
        df_merged.to_parquet(out_intermediate, index=False)
        print(f"    Saved harmonized {yr} APR intermediate table: {len(df_merged):,} schools -> {out_intermediate}")

    print("\n[SUCCESS] Phase 2: Variable crosswalk created and APR datasets harmonized across 2022-2025.")


if __name__ == "__main__":
    harmonize_apr()
