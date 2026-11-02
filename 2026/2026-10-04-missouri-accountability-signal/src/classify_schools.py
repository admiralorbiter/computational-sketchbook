"""
src/classify_schools.py

Provides standardized logic for:
1. School level classification (Elementary, Middle, High, Mixed).
2. Explicit facility and institution type flags using both NCES CCD classifications and state administrative records:
   - flag_regular_school
   - flag_alternative_school
   - flag_special_education
   - flag_cte_vocational
   - flag_virtual_school
   - flag_juvenile_correctional
   - flag_no_tested_grades
   - flag_invalid_apr
3. Analytic sample assignment:
   - Sample A: All Public Schools (Universe)
   - Sample B: Conventional Accountability Schools
   - Sample C: Stable Balanced Longitudinal Panel (2022-2025)
4. Audit-grade exclusion categorization.
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

    # Pure high schools (9-12, 10-12, 8-12, 7-12 Jr/Sr high)
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


def regex_matches(text, patterns):
    s = str(text).upper()
    for p in patterns:
        if re.search(p, s):
            return True
    return False


def assign_sample_flags(df):
    """
    Assigns institutional type flags, sample_a_all, sample_b_conventional,
    and detailed exclusion reasons.
    """
    df = df.copy()

    # Universe flag
    df["sample_a_all"] = 1

    school_and_dist = (df["SCHOOL_NAME"].fillna("") + " " + df["DISTRICT_NAME"].fillna("")).str.upper()

    # 1. Juvenile Detention / Correctional / Residential Treatment
    detention_patterns = [
        r"\bTREATMENT\b",
        r"\bDETENTION\b",
        r"\bCORRECTIONAL\b",
        r"\bJUVENILE\b",
        r"\bGROUP HOME\b",
        r"\bDAY TREATMENT\b",
        r"\bSHELTER\b",
        r"\bCRISIS NURSERY\b",
    ]
    df["flag_juvenile_correctional"] = school_and_dist.apply(lambda s: 1 if regex_matches(s, detention_patterns) else 0)

    # 2. Career & Technical / Vocational (NCES school_type == 3 or name regex)
    cte_patterns = [
        r"\bCAREER TECH\b",
        r"\bTECH(NICAL)? CTR\b",
        r"\bCAREER CENTER\b",
        r"\bVOCATIONAL\b",
        r"\bACADEMY OF VOCATIONAL\b",
    ]
    df["flag_cte_vocational"] = np.where(
        (df.get("nces_school_type") == "3") | school_and_dist.apply(lambda s: regex_matches(s, cte_patterns)),
        1, 0
    )

    # 3. Special Education School (NCES school_type == 2 or special district/severe handicap)
    sped_patterns = [
        r"\bSEVERELY DISABLED\b",
        r"\bSEV(ERELY)? HANDICAP\b",
        r"\bSTATE SCHOOLS?\b",
        r"\bSPECL?\b",
        r"\bSPECIAL SCH\b",
        r"\bEXTERNAL SITES\b",
    ]
    df["flag_special_education"] = np.where(
        (df.get("nces_school_type") == "2") | school_and_dist.apply(lambda s: regex_matches(s, sped_patterns)),
        1, 0
    )

    # 4. Alternative School (NCES school_type == 4 or name regex)
    alt_patterns = [
        r"\bALTERNATIVE\b",
        r"\bALTRN\b",
        r"\bACADEMY FOR SUCCESS\b",
        r"\bTRANSITION(AL)? CTR\b",
        r"\bSECOND CHANCE\b",
    ]
    df["flag_alternative_school"] = np.where(
        (df.get("nces_school_type") == "4") | school_and_dist.apply(lambda s: regex_matches(s, alt_patterns)),
        1, 0
    )

    # 5. Virtual School (NCES virtual == '1.0' or name regex)
    virtual_patterns = [
        r"\bVIRTUAL\b",
        r"\bONLINE ACADEMY\b",
        r"\bCYBER\b",
    ]
    df["flag_virtual_school"] = np.where(
        (df.get("nces_virtual").isin(["1.0", "1", 1])) | school_and_dist.apply(lambda s: regex_matches(s, virtual_patterns)),
        1, 0
    )

    # 6. Regular School indicator
    df["flag_regular_school"] = np.where(
        (df["flag_juvenile_correctional"] == 0) &
        (df["flag_cte_vocational"] == 0) &
        (df["flag_special_education"] == 0) &
        (df["flag_alternative_school"] == 0) &
        (df["flag_virtual_school"] == 0),
        1, 0
    )

    # 7. Tested Grades: end_grade >= 3
    df["end_grade_num"] = df["END_GRADE"].apply(parse_grade)
    df["beg_grade_num"] = df["BEG_GRADE"].apply(parse_grade)
    df["flag_no_tested_grades"] = np.where(df["end_grade_num"] < 3, 1, 0)

    # 8. Valid APR Outcome: apr_points_possible > 0 and not apr_pct is NaN
    df["flag_invalid_apr"] = np.where(
        (df["apr_points_possible"].fillna(0) <= 0) | df["apr_pct"].isna(),
        1, 0
    )

    # Detailed Mutually Exclusive Exclusion Reason (hierarchical):
    conditions = [
        df["flag_juvenile_correctional"] == 1,
        df["flag_special_education"] == 1,
        df["flag_cte_vocational"] == 1,
        df["flag_alternative_school"] == 1,
        df["flag_virtual_school"] == 1,
        df["flag_no_tested_grades"] == 1,
        df["flag_invalid_apr"] == 1,
    ]
    reasons = [
        "JUVENILE_DETENTION_OR_TREATMENT",
        "SPECIAL_EDUCATION_SCHOOL",
        "CAREER_TECHNICAL_CENTER",
        "ALTERNATIVE_SCHOOL",
        "VIRTUAL_SCHOOL",
        "NO_TESTED_GRADES_PK_2",
        "NO_VALID_APR_OUTCOME",
    ]
    df["exclusion_reason"] = np.select(conditions, reasons, default="INCLUDED")

    # Sample B Conventional School flag
    df["sample_b_conventional"] = (df["exclusion_reason"] == "INCLUDED").astype(int)

    return df
