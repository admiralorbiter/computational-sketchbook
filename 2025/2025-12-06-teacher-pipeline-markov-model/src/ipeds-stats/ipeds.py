import pandas as pd
import numpy as np
from pathlib import Path

# -------------------------
# Helper functions (needed for configuration)
# -------------------------

def find_file_case_insensitive(directory: Path, filename: str) -> Path:
    """
    Find a file in the directory, case-insensitively.
    Returns the Path if found, otherwise returns directory / filename (original case).
    """
    if not directory.exists():
        return directory / filename
    
    # Try exact match first (fast path)
    exact_path = directory / filename
    if exact_path.exists():
        return exact_path
    
    # Search case-insensitively
    filename_lower = filename.lower()
    for file in directory.iterdir():
        if file.is_file() and file.name.lower() == filename_lower:
            return file
    
    # Not found, return original path (will fail later with clearer error)
    return exact_path


# -------------------------
# Configuration
# -------------------------

# Folder where you put your IPEDS CSV files
DATA_DIR = Path(".")  # change to your folder if needed

# File names from the IPEDS program generator / Data Center export
# Use case-insensitive lookup to handle Windows filesystem
C2024_A_FILE = find_file_case_insensitive(DATA_DIR, "C2024_A.csv")   # program-level completions (with CIPCODE)
C2024_C_FILE = find_file_case_insensitive(DATA_DIR, "C2024_C.csv")   # OPTIONAL: institution-level totals (your file)
HD2024_FILE = find_file_case_insensitive(DATA_DIR, "HD2024.csv")    # Institution directory (names, location, etc.)

OUTPUT_DIR = DATA_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# CIP series we care about:
# Series 13 = Education, including teacher ed and related programs (CIP 2020). 
# We filter by codes starting with "13".
CIP_SERIES_PREFIX = "13"

# Optional: if you want ONLY teacher-prep-ish 4-digit series, you could use:
# TEACHER_ED_4DIGIT = {"13.12", "13.13", "13.14", "13.15"}

# Human-readable labels for AWLEVEL codes (per IPEDS documentation for completions).
# AWLEVEL is technically alphanumeric (1a, 1b, 2–8, 17–19), but in CSV exports it is
# usually numeric; we handle both by treating it as text.
AWLEVEL_LABELS = {
    "1":  "Postsecondary award <1 year (short)",
    "2":  "Postsecondary cert 1–<2 years",
    "3":  "Associate’s degree",
    "4":  "Postsecondary cert 2–<4 years",
    "5":  "Bachelor’s degree",
    "6":  "Postbaccalaureate certificate",
    "7":  "Master’s degree",
    "8":  "Post-master’s certificate",
    "17": "Doctor’s degree – research/scholarship",
    "18": "Doctor’s degree – professional practice",
    "19": "Doctor’s degree – other",
    # If your file actually uses '1a' / '1b', you can add:
    "1A": "Postsecondary award <300 clock hrs / <9 credits",
    "1B": "Postsecondary award 300–899 clock hrs / 9–29 credits",
}


# Race/ethnicity total columns in C2024_A (not the imputation "X" fields)
RACE_TOTAL_COLS = [
    "CAIANT",   # American Indian or Alaska Native total
    "CASIAT",   # Asian total
    "CBKAAT",   # Black or African American total
    "CHISPT",   # Hispanic or Latino total
    "CNHPIT",   # Native Hawaiian or Other Pacific Islander total
    "CWHITT",   # White total
    "C2MORT",   # Two or more races total
    "CUNKNT",   # Race/ethnicity unknown total
    "CNRALT",   # U.S. Nonresident total
]

# -------------------------
# Helper functions
# -------------------------

def load_c2024_a(path: Path) -> pd.DataFrame:
    """
    Load the IPEDS C2024_A program-level completions CSV and normalize column names.
    """
    df = pd.read_csv(path, dtype=str)  # read everything as string first
    df.columns = df.columns.str.upper()

    # Convert numeric columns from strings where appropriate
    numeric_cols = [
        "CTOTALT", "CTOTALM", "CTOTALW",
        "CAIANT", "CAIANM", "CAIANW",
        "CASIAT", "CASIAM", "CASIAW",
        "CBKAAT", "CBKAAM", "CBKAAW",
        "CHISPT", "CHISPM", "CHISPW",
        "CNHPIT", "CNHPIM", "CNHPIW",
        "CWHITT", "CWHITM", "CWHITW",
        "C2MORT", "C2MORM", "C2MORW",
        "CUNKNT", "CUNKNM", "CUNKNW",
        "CNRALT", "CNRALM", "CNRALW",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Convert UNITID to numeric for proper merging with other datasets
    if "UNITID" in df.columns:
        df["UNITID"] = pd.to_numeric(df["UNITID"], errors="coerce")

    # AWLEVEL as string (so we can handle 1a/1b if present)
    if "AWLEVEL" in df.columns:
        df["AWLEVEL"] = df["AWLEVEL"].astype(str).str.strip().str.upper()

    return df


def load_hd2024(path: Path) -> pd.DataFrame:
    """
    Load the IPEDS HD2024 institution directory CSV and normalize column names.
    Returns a dataframe with UNITID, INSTNM, LATITUDE, LONGITUD, and other institution info.
    """
    df = pd.read_csv(path, dtype=str)  # read everything as string first
    df.columns = df.columns.str.upper()
    
    # Convert UNITID to numeric for proper merging
    if "UNITID" in df.columns:
        df["UNITID"] = pd.to_numeric(df["UNITID"], errors="coerce")
    
    # Convert latitude and longitude to numeric
    for col in ["LATITUDE", "LONGITUD"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df


def filter_cip_series(df: pd.DataFrame, prefix: str = CIP_SERIES_PREFIX) -> pd.DataFrame:
    """
    Keep only rows where CIPCODE belongs to the desired series (e.g., '13' for Education).
    CIPCODE in IPEDS CSV is usually 'xx.xxxx' with leading zeros preserved.
    """
    if "CIPCODE" not in df.columns:
        raise KeyError("CIPCODE column not found in C2024_A file.")
    df = df.copy()
    df["CIPCODE"] = df["CIPCODE"].astype(str).str.strip()
    return df[df["CIPCODE"].str.startswith(prefix)]


def add_awlevel_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attach human-readable labels for award level.
    """
    df = df.copy()
    if "AWLEVEL" in df.columns:
        df["AWLEVEL_CODE"] = df["AWLEVEL"]
        df["AWLEVEL_LABEL"] = df["AWLEVEL"].map(AWLEVEL_LABELS).fillna(df["AWLEVEL"])
    return df


# -------------------------
# Core analyses
# -------------------------

def summarize_by_award_level(df_ed: pd.DataFrame) -> pd.DataFrame:
    """
    Total teacher-education (CIP series 13) completions by award level.
    """
    grouped = (
        df_ed
        .groupby("AWLEVEL", dropna=False)[["CTOTALT", "CTOTALM", "CTOTALW"]]
        .sum()
        .reset_index()
    )
    grouped = add_awlevel_labels(grouped)
    return grouped.sort_values("AWLEVEL")


def summarize_by_race_overall(df_ed: pd.DataFrame) -> pd.DataFrame:
    """
    Overall teacher-education completions by race/ethnicity (all institutions and award levels).
    """
    totals = {}
    grand_total = df_ed["CTOTALT"].sum()

    totals["RACE_CATEGORY"] = []
    totals["COMPLETIONS"] = []
    totals["PCT_OF_TEACHER_ED"] = []

    race_labels = {
        "CAIANT": "American Indian or Alaska Native",
        "CASIAT": "Asian",
        "CBKAAT": "Black or African American",
        "CHISPT": "Hispanic or Latino",
        "CNHPIT": "Native Hawaiian or Other Pacific Islander",
        "CWHITT": "White",
        "C2MORT": "Two or more races",
        "CUNKNT": "Race/ethnicity unknown",
        "CNRALT": "U.S. Nonresident",
    }

    for col in RACE_TOTAL_COLS:
        if col in df_ed.columns:
            count = df_ed[col].sum()
            label = race_labels.get(col, col)
            totals["RACE_CATEGORY"].append(label)
            totals["COMPLETIONS"].append(count)
            pct = (count / grand_total * 100) if grand_total > 0 else 0
            totals["PCT_OF_TEACHER_ED"].append(round(pct, 2))

    return pd.DataFrame(totals).sort_values("COMPLETIONS", ascending=False)


def summarize_award_by_race(df_ed: pd.DataFrame) -> pd.DataFrame:
    """
    Teacher-education completions by award level and race/ethnicity.
    """
    keep_cols = ["AWLEVEL"] + [c for c in RACE_TOTAL_COLS if c in df_ed.columns]
    sub = df_ed[keep_cols].copy()

    grouped = sub.groupby("AWLEVEL", dropna=False).sum().reset_index()
    grouped = add_awlevel_labels(grouped)
    return grouped.sort_values("AWLEVEL")


def summarize_award_by_gender(df_ed: pd.DataFrame) -> pd.DataFrame:
    """
    Teacher-education completions by award level and gender.
    """
    grouped = (
        df_ed
        .groupby("AWLEVEL", dropna=False)[["CTOTALM", "CTOTALW", "CTOTALT"]]
        .sum()
        .reset_index()
    )
    grouped = add_awlevel_labels(grouped)

    # Percent women/men within award level
    grouped["PCT_WOMEN"] = (grouped["CTOTALW"] / grouped["CTOTALT"] * 100).round(2)
    grouped["PCT_MEN"] = (grouped["CTOTALM"] / grouped["CTOTALT"] * 100).round(2)

    return grouped.sort_values("AWLEVEL")


def compute_institution_program_completions(df_ed: pd.DataFrame,
                                           hd2024_path: Path = None) -> pd.DataFrame:
    """
    Create a view of teacher-education completions by institution, specific program (CIP code), and award level.
    Shows total completions for each education program (e.g., Elementary Education, Secondary Education) by institution and award level.
    Does not include race breakdowns.
    
    - df_ed: Education (CIP 13) completions data
    - hd2024_path: Optional institution directory file
    """
    # Aggregate completions by institution, CIP code, and award level (no race breakdown)
    inst_program = (
        df_ed
        .groupby(["UNITID", "CIPCODE", "AWLEVEL"], dropna=False)
        .agg({
            "CTOTALT": "sum",
        })
        .reset_index()
    )
    
    # Ensure UNITID is numeric
    inst_program["UNITID"] = pd.to_numeric(inst_program["UNITID"], errors="coerce")
    
    # Ensure CIPCODE is string and clean
    inst_program["CIPCODE"] = inst_program["CIPCODE"].astype(str).str.strip()
    
    # Add CIP code description (4-digit level) - first 5 characters (e.g., "13.12")
    inst_program["CIPCODE_4DIGIT"] = inst_program["CIPCODE"].str.slice(0, 5)
    
    # Common CIP code labels for education programs (CIP 2020)
    cip_labels = {
        "13.01": "Education, General",
        "13.02": "Bilingual, Multilingual, and Multicultural Education",
        "13.03": "Curriculum and Instruction",
        "13.04": "Educational Administration and Supervision",
        "13.05": "Educational/Instructional Media Design",
        "13.06": "Educational Assessment, Evaluation, and Research",
        "13.07": "International and Comparative Education",
        "13.08": "Educational Statistics and Research Methods",
        "13.09": "Social and Philosophical Foundations of Education",
        "13.10": "Special Education and Teaching, General",
        "13.11": "Student Counseling and Personnel Services",
        "13.12": "Teacher Education and Professional Development, Specific Levels and Methods",
        "13.13": "Teacher Education and Professional Development, Specific Subject Areas",
        "13.14": "Teaching English or French as a Second or Foreign Language",
        "13.15": "Teaching Assistants/Aides",
        "13.16": "Adult and Continuing Education and Teaching",
        "13.17": "Education, Other",
    }
    
    inst_program["CIPCODE_LABEL"] = inst_program["CIPCODE_4DIGIT"].map(cip_labels).fillna("Other Education")
    
    # Add award level labels
    inst_program = add_awlevel_labels(inst_program)
    
    # Merge in institution directory data (HD2024) if available
    if hd2024_path and hd2024_path.exists():
        df_hd = load_hd2024(hd2024_path)
        # Include more institution details
        hd_cols = ["UNITID", "INSTNM", "CITY", "STABBR", "LATITUDE", "LONGITUD", "CONTROL", "SECTOR"]
        hd_cols = [col for col in hd_cols if col in df_hd.columns]
        
        inst_program = inst_program.merge(
            df_hd[hd_cols],
            on="UNITID",
            how="left",
            validate="m:1",
        )
        
        # Add control type labels
        control_labels = {
            "1": "Public",
            "2": "Private nonprofit",
            "3": "Private for-profit"
        }
        if "CONTROL" in inst_program.columns:
            inst_program["CONTROL_LABEL"] = inst_program["CONTROL"].astype(str).map(control_labels).fillna(inst_program["CONTROL"])
    
    # Reorder columns for better readability
    if "INSTNM" in inst_program.columns:
        base_cols = ["UNITID", "INSTNM", "CITY", "STABBR", "LATITUDE", "LONGITUD"]
        if "CONTROL_LABEL" in inst_program.columns:
            base_cols.append("CONTROL_LABEL")
        base_cols.extend(["CIPCODE", "CIPCODE_4DIGIT", "CIPCODE_LABEL", "AWLEVEL", "AWLEVEL_CODE", "AWLEVEL_LABEL", "CTOTALT"])
        
        # Add any remaining columns
        remaining_cols = [col for col in inst_program.columns if col not in base_cols]
        col_order = base_cols + remaining_cols
        inst_program = inst_program[[col for col in col_order if col in inst_program.columns]]
    
    return inst_program.sort_values(["INSTNM" if "INSTNM" in inst_program.columns else "UNITID", "CIPCODE", "AWLEVEL"])


def compute_institution_degree_completions(df_ed: pd.DataFrame,
                                          hd2024_path: Path = None) -> pd.DataFrame:
    """
    Create a detailed view of teacher-education completions by institution and degree type.
    Includes institution info, award level, completions by gender and race/ethnicity.
    
    - df_ed: Education (CIP 13) completions data
    - hd2024_path: Optional institution directory file
    """
    # Aggregate completions by institution and award level with all demographics
    inst_degree = (
        df_ed
        .groupby(["UNITID", "AWLEVEL"], dropna=False)
        .agg({
            "CTOTALT": "sum",
            "CTOTALM": "sum",
            "CTOTALW": "sum",
            **{col: "sum" for col in RACE_TOTAL_COLS if col in df_ed.columns}
        })
        .reset_index()
    )
    
    # Ensure UNITID is numeric
    inst_degree["UNITID"] = pd.to_numeric(inst_degree["UNITID"], errors="coerce")
    
    # Add award level labels
    inst_degree = add_awlevel_labels(inst_degree)
    
    # Merge in institution directory data (HD2024) if available
    if hd2024_path and hd2024_path.exists():
        df_hd = load_hd2024(hd2024_path)
        # Include more institution details
        hd_cols = ["UNITID", "INSTNM", "CITY", "STABBR", "LATITUDE", "LONGITUD", "CONTROL", "SECTOR"]
        hd_cols = [col for col in hd_cols if col in df_hd.columns]
        
        inst_degree = inst_degree.merge(
            df_hd[hd_cols],
            on="UNITID",
            how="left",
            validate="m:1",
        )
        
        # Add control type labels
        control_labels = {
            "1": "Public",
            "2": "Private nonprofit",
            "3": "Private for-profit"
        }
        if "CONTROL" in inst_degree.columns:
            inst_degree["CONTROL_LABEL"] = inst_degree["CONTROL"].astype(str).map(control_labels).fillna(inst_degree["CONTROL"])
    
    # Calculate percentages (handle division by zero)
    inst_degree["PCT_WOMEN"] = np.where(
        inst_degree["CTOTALT"] > 0,
        (inst_degree["CTOTALW"] / inst_degree["CTOTALT"] * 100).round(2),
        np.nan
    )
    inst_degree["PCT_MEN"] = np.where(
        inst_degree["CTOTALT"] > 0,
        (inst_degree["CTOTALM"] / inst_degree["CTOTALT"] * 100).round(2),
        np.nan
    )
    
    # Calculate race/ethnicity percentages
    for col in RACE_TOTAL_COLS:
        if col in inst_degree.columns:
            pct_col = col.replace("T", "_PCT")
            inst_degree[pct_col] = np.where(
                inst_degree["CTOTALT"] > 0,
                (inst_degree[col] / inst_degree["CTOTALT"] * 100).round(2),
                np.nan
            )
    
    # Reorder columns for better readability
    if "INSTNM" in inst_degree.columns:
        base_cols = ["UNITID", "INSTNM", "CITY", "STABBR", "LATITUDE", "LONGITUD"]
        if "CONTROL_LABEL" in inst_degree.columns:
            base_cols.append("CONTROL_LABEL")
        base_cols.extend(["AWLEVEL", "AWLEVEL_CODE", "AWLEVEL_LABEL"])
        base_cols.extend(["CTOTALT", "CTOTALM", "CTOTALW", "PCT_WOMEN", "PCT_MEN"])
        
        # Add race columns
        race_cols = []
        for col in RACE_TOTAL_COLS:
            if col in inst_degree.columns:
                race_cols.append(col)
                pct_col = col.replace("T", "_PCT")
                if pct_col in inst_degree.columns:
                    race_cols.append(pct_col)
        
        # Add any remaining columns
        remaining_cols = [col for col in inst_degree.columns if col not in base_cols + race_cols]
        col_order = base_cols + race_cols + remaining_cols
        inst_degree = inst_degree[[col for col in col_order if col in inst_degree.columns]]
    
    return inst_degree.sort_values(["INSTNM" if "INSTNM" in inst_degree.columns else "UNITID", "AWLEVEL"])


def compute_teacher_ed_share_by_institution_award(df_ed: pd.DataFrame,
                                                  c2024_c_path: Path,
                                                  hd2024_path: Path = None) -> pd.DataFrame:
    """
    OPTIONAL: Use C2024_C to compute, for each institution & consolidated award level,
    the share of completions that are in CIP series 13.

    - C2024_A: program-level completions (teacher-ed subset already in df_ed)
    - C2024_C: institution-level totals by consolidated award level (AWLEVELC)
    - HD2024: institution directory with names and location data (optional)
    """
    # Aggregate teacher-ed totals at institution x award level (using AWLEVEL)
    teacher_inst_aw = (
        df_ed
        .groupby(["UNITID", "AWLEVEL"], dropna=False)[["CTOTALT"]]
        .sum()
        .reset_index()
        .rename(columns={"CTOTALT": "TEACHER_ED_COMPLETIONS"})
    )
    
    # Ensure UNITID is numeric for proper merging
    teacher_inst_aw["UNITID"] = pd.to_numeric(teacher_inst_aw["UNITID"], errors="coerce")

    # Load C2024_C
    df_c = pd.read_csv(c2024_c_path, dtype=str)
    df_c.columns = df_c.columns.str.upper()
    # Convert UNITID to numeric for proper merging
    if "UNITID" in df_c.columns:
        df_c["UNITID"] = pd.to_numeric(df_c["UNITID"], errors="coerce")
    # Convert numeric fields
    for col in ["CSTOTLT"]:
        if col in df_c.columns:
            df_c[col] = pd.to_numeric(df_c[col], errors="coerce").fillna(0).astype(int)

    # AWLEVELC is consolidated; for a rough merge we will just treat AWLEVEL as AWLEVELC
    # if codes line up in your analysis (3=Associate, 5=Bachelor, 7=Master, etc.).
    # You can improve this by applying the full AWLEVEL→AWLEVELC crosswalk if needed.
    if "AWLEVELC" not in df_c.columns:
        raise KeyError("AWLEVELC not found in C2024_C file.")

    df_c["AWLEVELC"] = df_c["AWLEVELC"].astype(str).str.strip().str.upper()

    # For a simple comparison, assume AWLEVEL (from A) and AWLEVELC (from C) can be aligned
    teacher_inst_aw["AWLEVELC"] = teacher_inst_aw["AWLEVEL"]  # simple mapping

    merged = teacher_inst_aw.merge(
        df_c[["UNITID", "AWLEVELC", "CSTOTLT"]],
        on=["UNITID", "AWLEVELC"],
        how="left",
        validate="m:1",
    )

    # Merge in institution directory data (HD2024) if available
    if hd2024_path and hd2024_path.exists():
        df_hd = load_hd2024(hd2024_path)
        # Select only the columns we want to include
        hd_cols = ["UNITID", "INSTNM", "LATITUDE", "LONGITUD"]
        hd_cols = [col for col in hd_cols if col in df_hd.columns]
        
        merged = merged.merge(
            df_hd[hd_cols],
            on="UNITID",
            how="left",
            validate="m:1",
        )

    merged = add_awlevel_labels(merged)

    # Ensure numeric types
    merged["TOTAL_COMPLETIONS_ALL_CIPS"] = pd.to_numeric(merged["CSTOTLT"], errors="coerce").fillna(0).astype(int)
    merged["TEACHER_ED_COMPLETIONS"] = pd.to_numeric(merged["TEACHER_ED_COMPLETIONS"], errors="coerce").fillna(0).astype(int)
    
    # Calculate share percentage, handling division by zero
    # Use numpy where to avoid division by zero
    merged["TEACHER_ED_SHARE_PCT"] = np.where(
        merged["TOTAL_COMPLETIONS_ALL_CIPS"] > 0,
        (merged["TEACHER_ED_COMPLETIONS"].astype(float) / merged["TOTAL_COMPLETIONS_ALL_CIPS"].astype(float) * 100).round(2),
        np.nan
    )
    # Convert to float type
    merged["TEACHER_ED_SHARE_PCT"] = merged["TEACHER_ED_SHARE_PCT"].astype(float)

    # Reorder columns to put institution info first (if available)
    if "INSTNM" in merged.columns:
        col_order = ["UNITID", "INSTNM", "LATITUDE", "LONGITUD", "AWLEVEL", "AWLEVEL_CODE", "AWLEVEL_LABEL",
                     "TEACHER_ED_COMPLETIONS", "TOTAL_COMPLETIONS_ALL_CIPS", "TEACHER_ED_SHARE_PCT"]
        # Add any remaining columns
        remaining_cols = [col for col in merged.columns if col not in col_order]
        col_order.extend(remaining_cols)
        merged = merged[[col for col in col_order if col in merged.columns]]

    return merged.sort_values(["UNITID", "AWLEVELC"])


# -------------------------
# Main entry point
# -------------------------

def main():
    print("Loading C2024_A (program-level completions)...")
    df_a = load_c2024_a(C2024_A_FILE)

    print(f"Rows in C2024_A: {len(df_a):,}")

    print(f"Filtering to CIP series {CIP_SERIES_PREFIX} (Education)...")
    df_ed = filter_cip_series(df_a, prefix=CIP_SERIES_PREFIX)
    print(f"Rows in Education (CIP starting with {CIP_SERIES_PREFIX}): {len(df_ed):,}")

    # If you want to narrow to teacher-ed 4-digit series only, uncomment:
    # df_ed = df_ed[df_ed["CIPCODE"].str.slice(0, 5).isin(TEACHER_ED_4DIGIT)]

    # --- Summaries ---

    print("Summarizing by award level...")
    by_aw = summarize_by_award_level(df_ed)
    by_aw.to_csv(OUTPUT_DIR / "teacher_ed_by_award_level.csv", index=False)

    print("Summarizing overall by race/ethnicity...")
    by_race = summarize_by_race_overall(df_ed)
    by_race.to_csv(OUTPUT_DIR / "teacher_ed_by_race_total.csv", index=False)

    print("Summarizing award level x race/ethnicity...")
    by_aw_race = summarize_award_by_race(df_ed)
    by_aw_race.to_csv(OUTPUT_DIR / "teacher_ed_by_award_and_race.csv", index=False)

    print("Summarizing award level x gender...")
    by_aw_gender = summarize_award_by_gender(df_ed)
    by_aw_gender.to_csv(OUTPUT_DIR / "teacher_ed_by_award_and_gender.csv", index=False)

    # Create institution-level view by degree type (aggregated across all programs)
    print("Creating institution-level completions by degree type...")
    inst_degree = compute_institution_degree_completions(df_ed, HD2024_FILE)
    inst_degree.to_csv(OUTPUT_DIR / "teacher_ed_institution_by_degree.csv", index=False)
    print(f"  Created detailed view with {len(inst_degree):,} institution-degree combinations")
    
    # Create institution-level view by specific program (CIP code) and degree type
    print("Creating institution-level completions by specific program and degree type...")
    inst_program = compute_institution_program_completions(df_ed, HD2024_FILE)
    inst_program.to_csv(OUTPUT_DIR / "teacher_ed_institution_by_program.csv", index=False)
    print(f"  Created detailed view with {len(inst_program):,} institution-program-degree combinations")

    # OPTIONAL: use your C2024_C file (the one you uploaded) to compute shares
    if C2024_C_FILE.exists():
        print(f"Found C2024_C file: {C2024_C_FILE}")
        if HD2024_FILE.exists():
            print(f"Found HD2024 file: {HD2024_FILE}")
            print("Computing teacher-ed share of all completions using C2024_C with institution names and locations...")
        else:
            print("Computing teacher-ed share of all completions using C2024_C...")
        shares = compute_teacher_ed_share_by_institution_award(df_ed, C2024_C_FILE, HD2024_FILE)
        shares.to_csv(OUTPUT_DIR / "teacher_ed_share_by_institution_award.csv", index=False)
    else:
        print(f"C2024_C.csv not found (checked: {C2024_C_FILE.name}); skipping share-of-total calculation.")
        print("  Note: C2024_C.csv is optional - it's for institution-level totals, different from C2024_A.csv")

    print(f"Done. CSV outputs are in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
