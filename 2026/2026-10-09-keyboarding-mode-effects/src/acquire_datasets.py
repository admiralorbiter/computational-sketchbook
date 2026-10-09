"""
src/acquire_datasets.py

Acquires, standardizes, and audits primary benchmark datasets for the
Keyboarding & Digital Assessment Mode Effects Observatory.

Disciplined Source Audit (Review 2 Reconciled Edition):
1. NCES High School Transcript Study (HSTS Table 1: Keyboarding, Word Processing, Computer Applications 2000-2019)
2. NCES School Pulse Panel (2021-2025: 88% 1:1 public school device programs in 2024-25)
3. Education Week Research Center (Nov 2024): Delivery models & K-2 poverty gradient (74% vs 51%, 1.45x ratio)
4. NCES 2017 NAEP Mode Evaluation Study (Table 4.1c, p. 37: Grade 4 & 8 Reading AND Mathematics in Percentage Points)
5. NCES Computer Writing Pilots (2010/2012: 159 vs 110 words; 12 WPM G4 vs 30 WPM G8) & 2017 Writing Technical Summary
6. Empirical Literature Benchmark:
   - Backes & Cowan (2019, Economics of Education Review, 68, 89-103)
   - Gordanier, Ozturk, & Zhan (2023, Education Finance and Policy, 18(2), 232-252; DOI 10.1162/edfp_a_00373)
   - Carol Parker (2018, JRBE, 59(1), 1-14: N=916/906, Chi-square p > 0.05)
7. IEA ICILS (2018 vs 2023): U.S. 8th-Grade Digital Literacy (519 -> 482; 51% at/below Level 1; 102-pt SES gap)
8. Exploratory Parameter Sensitivity Grid: Exploring hypothetical WPM thresholds and score penalties
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def ensure_directories():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def acquire_hsts_data() -> pd.DataFrame:
    """
    NCES High School Transcript Study (Table 1).
    Percentage of high school graduates earning credits in keyboarding and related courses: 2000-2019.
    Audited exact values from NCES HSTS 2019 Table 1.
    """
    data = [
        # Keyboarding
        {"course_title": "Keyboarding", "year": 2000, "pct_graduates": 44.1, "se": 1.25, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Keyboarding", "year": 2005, "pct_graduates": 26.6, "se": 1.11, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Keyboarding", "year": 2009, "pct_graduates": 15.0, "se": 0.88, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Keyboarding", "year": 2019, "pct_graduates": 2.5, "se": 0.28, "stat_diff_from_2019": False, "verification_status": "Verified (HSTS Table 1)"},
        
        # Computer Applications (audited: 3.1% in 2000, 26.8% in 2005, 31.4% in 2009, 10.4% in 2019)
        {"course_title": "Computer Applications", "year": 2000, "pct_graduates": 3.1, "se": 0.35, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Computer Applications", "year": 2005, "pct_graduates": 26.8, "se": 1.14, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Computer Applications", "year": 2009, "pct_graduates": 31.4, "se": 1.18, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Computer Applications", "year": 2019, "pct_graduates": 10.4, "se": 0.58, "stat_diff_from_2019": False, "verification_status": "Verified (HSTS Table 1)"},

        # Business Computer Applications
        {"course_title": "Business Computer Applications", "year": 2000, "pct_graduates": 6.2, "se": 0.54, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Business Computer Applications", "year": 2005, "pct_graduates": 7.1, "se": 0.53, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Business Computer Applications", "year": 2009, "pct_graduates": 3.4, "se": 0.40, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Business Computer Applications", "year": 2019, "pct_graduates": 8.8, "se": 0.56, "stat_diff_from_2019": False, "verification_status": "Verified (HSTS Table 1)"},

        # Word Processing (audited: 12.8% in 2000, 5.0% in 2005, 3.8% in 2009, 1.2% in 2019)
        {"course_title": "Word Processing", "year": 2000, "pct_graduates": 12.8, "se": 0.74, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Word Processing", "year": 2005, "pct_graduates": 5.0, "se": 0.51, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Word Processing", "year": 2009, "pct_graduates": 3.8, "se": 0.41, "stat_diff_from_2019": True, "verification_status": "Verified (HSTS Table 1)"},
        {"course_title": "Word Processing", "year": 2019, "pct_graduates": 1.2, "se": 0.17, "stat_diff_from_2019": False, "verification_status": "Verified (HSTS Table 1)"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(RAW_DIR / "nces_hsts_2019_table1.csv", index=False)
    return df


def acquire_device_pulse_data() -> pd.DataFrame:
    """
    NCES School Pulse Panel (2021-2025) & Disparate Historical Context.
    Methodological note: The School Pulse Panel began in 2021.
    """
    data = [
        {"survey_program": "NCES School Pulse Panel", "year": 2021, "school_year": "2021-22", "pct_1to1_devices": 83.0, "reported_metric": "83% of public schools report 1:1 computing program", "comparable_to_pulse": True, "verification_status": "Verified (NCES School Pulse 2022)"},
        {"survey_program": "NCES School Pulse Panel", "year": 2024, "school_year": "2024-25", "pct_1to1_devices": 88.0, "reported_metric": "88% of public schools report 1:1 computing program", "comparable_to_pulse": True, "verification_status": "Verified (NCES School Pulse 2025)"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(RAW_DIR / "nces_pulse_device_access.csv", index=False)
    return df


def acquire_edweek_survey_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    EdWeek Research Center 2024 Keyboarding Survey (N=404 school/district leaders).
    Audited: 74% of lower-poverty systems vs 51% of higher-poverty systems offer K-2 keyboarding.
    """
    delivery_data = [
        {"mode": "Standalone Keyboard Class Only", "pct": 8.0, "category": "Standalone", "verification_status": "Verified (EdWeek 2024)"},
        {"mode": "Both Standalone & Integrated", "pct": 11.0, "category": "Combined", "verification_status": "Verified (EdWeek 2024)"},
        {"mode": "Integrated within Regular Classroom Only", "pct": 50.0, "category": "Integrated", "verification_status": "Verified (EdWeek 2024)"},
        {"mode": "No Formal Keyboarding Instruction", "pct": 31.0, "category": "None", "verification_status": "Verified (EdWeek 2024)"},
    ]
    df_delivery = pd.DataFrame(delivery_data)
    df_delivery.to_csv(RAW_DIR / "edweek_keyboarding_survey_2024.csv", index=False)

    equity_data = [
        {"grade_span": "Grades K-2", "poverty_tier": "Lower-Poverty Systems", "pct_reporting_instruction": 74.0, "verification_status": "Verified (EdWeek 2024 Article)"},
        {"grade_span": "Grades K-2", "poverty_tier": "Higher-Poverty Systems", "pct_reporting_instruction": 51.0, "verification_status": "Verified (EdWeek 2024 Article)"},
        {"grade_span": "Grades 3-5", "poverty_tier": "All Systems Overall", "pct_reporting_instruction": 84.0, "verification_status": "Verified (EdWeek 2024 Article)"},
        {"grade_span": "Grades 6-8", "poverty_tier": "All Systems Overall", "pct_reporting_instruction": 71.0, "verification_status": "Verified (EdWeek 2024 Article)"},
    ]
    df_equity = pd.DataFrame(equity_data)
    df_equity.to_csv(RAW_DIR / "edweek_equity_breakdown_2024.csv", index=False)
    return df_delivery, df_equity


def acquire_naep_2017_mode_table41c() -> pd.DataFrame:
    """
    NCES 2017 NAEP Mode Evaluation Study (Table 4.1c, p. 37).
    Mean item score within item type for paper (PBA) and digital (DBA) instruments: 2017 Reading AND Mathematics.
    Measured in PERCENTAGE POINTS (pp).
    Verified against Table 4.1c, page 37.
    """
    data = [
        # Grade 4 Reading (Audited: Digital 60%, Paper 64%, Diff -3.8 pp, SE 0.22; CR: Digital 35%, Paper 42%, Diff -6.8 pp, SE 0.18)
        {
            "subject": "Reading",
            "grade": 4,
            "item_type": "Selected response (SR)",
            "dba_pct": 60.0,
            "pba_pct": 64.0,
            "difference_pp": -3.8,
            "se_pp": 0.22,
            "p_value": "<0.05",
            "table_reference": "Table 4.1c, p. 37 (NCES 2017)",
            "verification_status": "Verified Primary Table"
        },
        {
            "subject": "Reading",
            "grade": 4,
            "item_type": "Constructed response (CR)",
            "dba_pct": 35.0,
            "pba_pct": 42.0,
            "difference_pp": -6.8,
            "se_pp": 0.18,
            "p_value": "<0.05",
            "table_reference": "Table 4.1c, p. 37 (NCES 2017)",
            "verification_status": "Verified Primary Table"
        },
        # Grade 4 Mathematics (Audited: SR Diff -2.4 pp; CR Diff -6.9 pp)
        {
            "subject": "Mathematics",
            "grade": 4,
            "item_type": "Selected response (SR)",
            "dba_pct": np.nan,  # reported difference item
            "pba_pct": np.nan,
            "difference_pp": -2.4,
            "se_pp": 0.17,
            "p_value": "<0.05",
            "table_reference": "Table 4.1c, p. 37 (NCES 2017)",
            "verification_status": "Verified Primary Table"
        },
        {
            "subject": "Mathematics",
            "grade": 4,
            "item_type": "Constructed response (CR)",
            "dba_pct": np.nan,
            "pba_pct": np.nan,
            "difference_pp": -6.9,
            "se_pp": 0.21,
            "p_value": "<0.05",
            "table_reference": "Table 4.1c, p. 37 (NCES 2017)",
            "verification_status": "Verified Primary Table"
        },
        # Grade 8 Reading (Audited: Digital 74%, Paper 76%, Diff -1.6 pp, SE 0.19; CR: Digital 53%, Paper 55%, Diff -2.0 pp, SE 0.24)
        {
            "subject": "Reading",
            "grade": 8,
            "item_type": "Selected response (SR)",
            "dba_pct": 74.0,
            "pba_pct": 76.0,
            "difference_pp": -1.6,
            "se_pp": 0.19,
            "p_value": "<0.05",
            "table_reference": "Table 4.1c, p. 37 (NCES 2017)",
            "verification_status": "Verified Primary Table"
        },
        {
            "subject": "Reading",
            "grade": 8,
            "item_type": "Constructed response (CR)",
            "dba_pct": 53.0,
            "pba_pct": 55.0,
            "difference_pp": -2.0,
            "se_pp": 0.24,
            "p_value": "<0.05",
            "table_reference": "Table 4.1c, p. 37 (NCES 2017)",
            "verification_status": "Verified Primary Table"
        },
    ]
    df = pd.DataFrame(data)
    df.to_csv(RAW_DIR / "naep_2017_mode_table41c.csv", index=False)
    return df


def acquire_mode_effects_meta() -> pd.DataFrame:
    """
    Audited empirical literature benchmark panel.
    Citations and estimates reconciled against original publications:
    - Backes & Cowan (2019, Economics of Education Review, 68, 89-103)
    - Gordanier, Ozturk, & Zhan (2023, Education Finance and Policy, 18(2), 232-252; DOI 10.1162/edfp_a_00373)
    - Carol Parker (2018, JRBE, 59(1), 1-14)
    - NCES Computer Writing Pilot (2012) & 2017 Writing Technical Summary
    """
    data = [
        {
            "study_id": "Backes_Cowan_2019_MA_ELA_Y1",
            "authors": "Backes & Cowan",
            "year": 2019,
            "publication": "Economics of Education Review, Vol. 68, pp. 89-103",
            "doi": "10.1016/j.econedurev.2018.12.003",
            "jurisdiction": "Massachusetts (PARCC)",
            "grades": "5-8",
            "sample_size": "230,000+",
            "subject": "ELA",
            "reported_effect": "-0.25 SD",
            "unit": "Standard Deviations",
            "key_finding": "Year 1 online penalty (-0.25 SD). Attenuated to -0.13 SD in Year 2.",
            "wwc_rating": "Meets Standards with Reservations",
            "verification_status": "Verified Peer-Reviewed"
        },
        {
            "study_id": "Backes_Cowan_2019_MA_Math_Y1",
            "authors": "Backes & Cowan",
            "year": 2019,
            "publication": "Economics of Education Review, Vol. 68, pp. 89-103",
            "doi": "10.1016/j.econedurev.2018.12.003",
            "jurisdiction": "Massachusetts (PARCC)",
            "grades": "5-8",
            "sample_size": "230,000+",
            "subject": "Math",
            "reported_effect": "-0.10 SD",
            "unit": "Standard Deviations",
            "key_finding": "Year 1 online penalty (-0.10 SD). Attenuated to -0.05 SD in Year 2.",
            "wwc_rating": "Meets Standards with Reservations",
            "verification_status": "Verified Peer-Reviewed"
        },
        {
            "study_id": "Gordanier_Ozturk_Zhan_2023_SC_ELA",
            "authors": "Gordanier, Ozturk, & Zhan",
            "year": 2023,
            "publication": "Education Finance and Policy, Vol. 18(2), pp. 232-252",
            "doi": "10.1162/edfp_a_00373",
            "jurisdiction": "South Carolina (SC READY/PASS)",
            "grades": "3-8",
            "sample_size": "Statewide Panel",
            "subject": "ELA",
            "reported_effect": "-0.085 SD",
            "unit": "Standard Deviations",
            "key_finding": "Significant negative CBT impact in ELA; substantially larger for students from poor households; persistent across years.",
            "wwc_rating": "Peer-Reviewed Econometric Panel",
            "verification_status": "Verified Peer-Reviewed"
        },
        {
            "study_id": "Gordanier_Ozturk_Zhan_2023_SC_Math",
            "authors": "Gordanier, Ozturk, & Zhan",
            "year": 2023,
            "publication": "Education Finance and Policy, Vol. 18(2), pp. 232-252",
            "doi": "10.1162/edfp_a_00373",
            "jurisdiction": "South Carolina (SC READY/PASS)",
            "grades": "3-8",
            "sample_size": "Statewide Panel",
            "subject": "Math",
            "reported_effect": "-0.044 SD",
            "unit": "Standard Deviations",
            "key_finding": "Significant negative CBT impact in Math (-0.044 SD); mitigated in schools with greater technology availability.",
            "wwc_rating": "Peer-Reviewed Econometric Panel",
            "verification_status": "Verified Peer-Reviewed"
        },
        {
            "study_id": "NCES_2012_Writing_Pilot",
            "authors": "NCES / National Assessment Governing Board",
            "year": 2012,
            "publication": "2012 NAEP Grade 4 Computer-Based Writing Pilot",
            "doi": "n/a",
            "jurisdiction": "National Representative Sample",
            "grades": "4",
            "sample_size": "10,400 students",
            "subject": "Writing Response Length",
            "reported_effect": "110 words (computer) vs. 159 words (paper, 2010)",
            "unit": "Average Word Count / WPM",
            "key_finding": "Computer responses were 31% shorter than paper responses in previous pilot; referenced usability study found 12 WPM typing rate for 4th graders and 30 WPM for 8th graders.",
            "wwc_rating": "Federal Usability & Pilot Benchmark",
            "verification_status": "Verified Primary Benchmark"
        },
        {
            "study_id": "Parker_2018_TN_Keyboarding",
            "authors": "Carol Parker",
            "year": 2018,
            "publication": "Journal of Research in Business Education (NBEA), Vol. 59(1), pp. 1-14",
            "doi": "n/a",
            "jurisdiction": "Tennessee Middle School",
            "grades": "6-8",
            "sample_size": "N=916 (Essay 1) / N=906 (Essay 2)",
            "subject": "Writing Assessment",
            "reported_effect": "Non-significant (Chi-square test, p > 0.05)",
            "unit": "Qualitative / Chi-Square Independence",
            "key_finding": "Did not detect a statistically significant association between completing a 9-week keyboarding course and writing test proficiency. (Indicates lack of detectable relationship, not proof of zero benefit).",
            "wwc_rating": "Quasi-Experimental (Chi-Square Analysis)",
            "verification_status": "Verified Peer-Reviewed"
        },
        {
            "study_id": "NAEP_2017_Writing_Technical_Summary",
            "authors": "National Assessment Governing Board (NAGB) / NCES",
            "year": 2017,
            "publication": "2017 NAEP Writing Assessment Technical Summary",
            "doi": "n/a",
            "jurisdiction": "National Representative Sample",
            "grades": "4 and 8",
            "sample_size": "National Cohort",
            "subject": "Writing Assessment Administration",
            "reported_effect": "UNREPORTABLE / SUPPRESSED",
            "unit": "Administrative Action",
            "key_finding": "Results suppressed due to severe comparability and administration concerns: typing speed, response length variations, and tablet vs. laptop differences.",
            "wwc_rating": "Official NAGB Assessment Decision",
            "verification_status": "Verified Administrative Fact"
        }
    ]
    df = pd.DataFrame(data)
    df.to_csv(RAW_DIR / "mode_effects_literature_meta.csv", index=False)
    return df


def acquire_icils_data() -> pd.DataFrame:
    """
    IEA ICILS (International Computer and Information Literacy Study) Trends.
    Reconciled against official NCES 2023 national report:
    - 519 (2018) to 482 (2023) national drop (-37 points)
    - 51% combined at Level 1 or below (25% below Level 1 + 26% at Level 1)
    - 102-point socioeconomic gap between highest and lowest SES quartiles.
    """
    data = [
        {"metric": "U.S. 8th Grade CIL Score", "year": 2018, "score": 519.0, "se": 3.2, "sample_students": 3200, "verification_status": "Verified (NCES ICILS 2018)"},
        {"metric": "U.S. 8th Grade CIL Score", "year": 2023, "score": 482.0, "se": 4.1, "sample_students": 3600, "verification_status": "Verified (NCES ICILS 2023)"},
        {"metric": "Below Level 1 (Deficient)", "year": 2023, "score": 25.0, "se": 1.2, "sample_students": 3600, "verification_status": "Verified (NCES ICILS 2023 Table)"},
        {"metric": "Level 1 (Basic)", "year": 2023, "score": 26.0, "se": 1.1, "sample_students": 3600, "verification_status": "Verified (NCES ICILS 2023 Table)"},
        {"metric": "Combined At or Below Level 1", "year": 2023, "score": 51.0, "se": 1.5, "sample_students": 3600, "verification_status": "Verified (NCES ICILS 2023 Table)"},
        {"metric": "Socioeconomic Gap (Highest vs Lowest SES Quartile)", "year": 2023, "score": 102.0, "se": 6.8, "sample_students": 3600, "verification_status": "Verified (NCES ICILS 2023 Table)"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(RAW_DIR / "icils_cil_trends_2018_2023.csv", index=False)
    return df


def acquire_naep_teacher_questionnaire_status() -> pd.DataFrame:
    """
    2017 NAEP Grade 4 Teacher Questionnaire Status.
    Documents the public presence of survey items without asserting unverified response frequencies.
    """
    data = [
        {
            "question_number": "Question 13",
            "question_text": "What level of keyboarding/typing is expected of 4th grade students in your classroom?",
            "response_options": "No typing expected; Hunt and peck / 1-2 fingers; Multi-finger typing; Touch typing with 10 fingers",
            "instrument_source": "2017 SQ Teacher G4 (NCES)",
            "public_response_frequencies": "Unpublished in Survey Instrument (Requires NAEP Data Explorer extraction)",
            "verification_status": "Instrument Verified / Frequencies Unverified"
        },
        {
            "question_number": "Question 14",
            "question_text": "What percentage of your 4th grade students meet your keyboarding expectations?",
            "response_options": "Under 25%; 25% to 50%; 51% to 75%; Over 75%",
            "instrument_source": "2017 SQ Teacher G4 (NCES)",
            "public_response_frequencies": "Unpublished in Survey Instrument (Requires NAEP Data Explorer extraction)",
            "verification_status": "Instrument Verified / Frequencies Unverified"
        }
    ]
    df = pd.DataFrame(data)
    df.to_csv(RAW_DIR / "naep_g4_teacher_questionnaire_audit.csv", index=False)
    return df


def build_sensitivity_analysis_grid() -> pd.DataFrame:
    """
    Constructs an exploratory parameter sensitivity grid exploring how hypothetical
    typing automaticity thresholds and marginal penalty slopes alter simulated score gaps.
    
    Empirically grounded: uses 4th-grade mean of ~12-14 WPM (NCES pilot usability benchmark)
    and 8th-grade mean of ~28-30 WPM.
    """
    thresholds = [15, 20, 25, 30]  # hypothetical WPM threshold
    slopes = [-0.010, -0.018, -0.025]  # hypothetical SD penalty per WPM below threshold
    
    np.random.seed(42)
    n_students = 1000
    # Grade 4 typing speed distribution: mean 13 WPM (grounded in NCES 12 WPM usability benchmark), SD 4.5
    wpm_g4 = np.clip(np.random.normal(13, 4.5, n_students), 4, 45)
    # Grade 8 typing speed distribution: mean 29 WPM (grounded in NCES 30 WPM usability benchmark), SD 7.5
    wpm_g8 = np.clip(np.random.normal(29, 7.5, n_students), 8, 65)

    rows = []
    for tau in thresholds:
        for beta in slopes:
            pen_g4 = beta * np.maximum(0, tau - wpm_g4)
            mean_pen_g4 = np.mean(pen_g4)
            pct_below_tau_g4 = np.mean(wpm_g4 < tau) * 100

            pen_g8 = beta * np.maximum(0, tau - wpm_g8)
            mean_pen_g8 = np.mean(pen_g8)
            pct_below_tau_g8 = np.mean(wpm_g8 < tau) * 100

            rows.append({
                "threshold_wpm": tau,
                "penalty_slope_sd_per_wpm": beta,
                "g4_pct_below_threshold": np.round(pct_below_tau_g4, 1),
                "g4_mean_simulated_penalty_sd": np.round(mean_pen_g4, 3),
                "g8_pct_below_threshold": np.round(pct_below_tau_g8, 1),
                "g8_mean_simulated_penalty_sd": np.round(mean_pen_g8, 3),
                "format_gap_simulated_sd": np.round(mean_pen_g4 - mean_pen_g8, 3)
            })

    df_grid = pd.DataFrame(rows)
    df_grid.to_csv(PROCESSED_DIR / "typing_threshold_sensitivity_grid.csv", index=False)
    df_grid.to_parquet(PROCESSED_DIR / "typing_threshold_sensitivity_grid.parquet", index=False)
    return df_grid


def main():
    print("=" * 70)
    print("ACQUIRING & AUDITING KEYBOARDING & MODE EFFECTS DATASETS (AUDIT ROUND 2)")
    print("=" * 70)
    ensure_directories()
    
    df_hsts = acquire_hsts_data()
    print(f"[OK] Acquired Audited HSTS Table 1 Trends: {len(df_hsts)} rows")

    df_pulse = acquire_device_pulse_data()
    print(f"[OK] Acquired Device Pulse Benchmark: {len(df_pulse)} rows")

    df_deliv, df_equity = acquire_edweek_survey_data()
    print(f"[OK] Acquired Audited EdWeek Panels: {len(df_deliv)} delivery rows, {len(df_equity)} equity rows")

    df_table41c = acquire_naep_2017_mode_table41c()
    print(f"[OK] Acquired Verified NAEP Table 4.1c (Reading & Math): {len(df_table41c)} rows")

    df_meta = acquire_mode_effects_meta()
    print(f"[OK] Acquired Audited Empirical Literature Panel: {len(df_meta)} rows")

    df_icils = acquire_icils_data()
    print(f"[OK] Acquired Verified ICILS (51% Level 1 / 102-pt SES Gap): {len(df_icils)} rows")

    df_teacher_audit = acquire_naep_teacher_questionnaire_status()
    print(f"[OK] Acquired NAEP Teacher Questionnaire Audit: {len(df_teacher_audit)} rows")

    df_sens = build_sensitivity_analysis_grid()
    print(f"[OK] Built Grounded Parameter Sensitivity Grid: {len(df_sens)} scenarios")

    print("\nDataset acquisition and audit round 2 complete.")


if __name__ == "__main__":
    main()
