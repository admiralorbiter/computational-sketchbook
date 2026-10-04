"""
src/classify_schools.py

Provides standardized logic for:
1. School level classification (Elementary, Middle, High, Mixed).
2. Analytic sample assignment:
   - Sample A: All Public Schools
   - Sample B: Conventional Accountability Schools
   - Sample C: Stable Balanced Longitudinal Panel (2022-2025)
3. Exclusion tracking and auditing.
"""

import re
import numpy as np
import pandas as pd


def parse_grade(g):
    """Normalizes grade code to numeric integer equivalent for span checking."""
    if pd.isna(g):
        return np.nan
    s = str(g).strip().upper()
    if s in ["PK", "P"]:
        return -1
    if s in ["K", "KG"]:
        return 0
    try:
        return int(float(s))
    except ValueError:
        return np.nan


def classify_school_level(beg_grade, end_grade):
    """
    Classifies building into ELEMENTARY, MIDDLE, HIGH, or MIXED based on grade span.
    """
    b = parse_grade(beg_grade)
    e = parse_grade(end_grade)

    if pd.isna(b) or pd.isna(e):
        return "UNKNOWN"

    # Pure high schools (9-12, 10-12, 8-12)
    if e == 12:
        if b >= 9:
            return "HIGH"
        elif b in [7, 8]:
            return "HIGH"  # 7-12 Jr/Sr High band
        else:
            return "MIXED"  # K-12, PK-12

    # Middle schools (5-8, 6-8, 7-8, 6-9)
    if e in [7, 8, 9] and b >= 5:
        return "MIDDLE"

    # Elementary schools (PK-5, K-5, PK-6, K-6, K-4, etc.)
    if e <= 6 and b <= 5:
        return "ELEMENTARY"

    # Broad spans (e.g., K-8, PK-8)
    if b <= 4 and e in [7, 8]:
        return "MIXED"

    return "MIXED"


def identify_specialized_facility(school_name, district_name):
    """
    Detects correctional, residential treatment, juvenile justice, or specialized non-standard schools.
    """
    s = f"{str(school_name).upper()} {str(district_name).upper()}"
    facility_patterns = [
        r"\bTREATMENT\b",
        r"\bDETENTION\b",
        r"\bCORRECTIONAL\b",
        r"\bJUVENILE\b",
        r"\bGROUP HOME\b",
        r"\bACADEMY OF VOCATIONAL\b",
        r"\bCAREER TECH\b",
        r"\bTECH(NICAL)? CTR\b",
        r"\bCAREER CENTER\b",
        r"\bVOCATIONAL\b",
        r"\bSEVERELY DISABLED\b",
        r"\bSEV(ERELY)? HANDICAP\b",
        r"\bSTATE SCHOOLS?\b",
        r"\bSPECL?\b",
        r"\bSPECIAL SCH\b",
        r"\bEXTERNAL SITES\b",
        r"\bDAY TREATMENT\b",
        r"\bSHELTER\b",
    ]
    for pattern in facility_patterns:
        if re.search(pattern, s):
            return True
    return False


def assign_sample_flags(df):
    """
    Assigns sample_a_all, sample_b_conventional, and exclusion reasons.
    """
    df = df.copy()

    # Sample A: Everything present
    df["sample_a_all"] = 1

    # Criteria for Sample B (Conventional Accountability Schools):
    # 1. Not a specialized facility (correctional, treatment, tech center)
    df["is_facility"] = df.apply(lambda r: identify_specialized_facility(r.get("SCHOOL_NAME", ""), r.get("DISTRICT_NAME", "")), axis=1)

    # 2. Serves tested grades (end grade >= 3, not pure early childhood)
    df["end_grade_num"] = df["END_GRADE"].apply(parse_grade)
    df["beg_grade_num"] = df["BEG_GRADE"].apply(parse_grade)
    df["serves_tested_grades"] = df["end_grade_num"] >= 3

    # 3. Has valid APR points possible (> 0) and not entirely suppressed/missing
    df["has_valid_apr"] = (df["apr_points_possible"] > 0) & (~df["apr_pct"].isna())

    # Exclusion reason string
    conditions = [
        df["is_facility"],
        ~df["serves_tested_grades"],
        ~df["has_valid_apr"],
    ]
    reasons = [
        "SPECIALIZED_FACILITY_OR_CTC",
        "NO_TESTED_GRADES_PK_2",
        "NO_VALID_APR_OUTCOME",
    ]
    df["exclusion_reason"] = np.select(conditions, reasons, default="INCLUDED")

    # Sample B flag
    df["sample_b_conventional"] = (df["exclusion_reason"] == "INCLUDED").astype(int)

    return df
