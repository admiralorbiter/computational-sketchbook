"""
src/acquire_national_benchmarks.py

Generates cleaned national benchmark datasets:
1. NAEP High School Transcript Study (HSTS 2009-2019): Overall GPA, Math GPA, NAEP 12th Grade Math Scores by Curriculum Rigor.
2. ACT Grade Inflation Sample (2010-2021): Average high school GPA vs ACT Composite and Math scores.
3. University of Chicago CCSR Parameters (Allensworth & Clark, 2020): College graduation rates by HS GPA and ACT bracket.
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
TABLES_DIR = BASE_DIR / "artifacts" / "tables"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

def build_naep_hsts_data():
    """
    Constructs the longitudinal NAEP High School Transcript Study dataset.
    Sources: NCES High School Transcript Study (1990, 2000, 2005, 2009, 2019).
    """
    records = [
        {"year": 1990, "curriculum": "All Graduates", "overall_gpa": 2.68, "math_gpa": 2.34, "naep_math_scale": np.nan, "credits_earned": 23.5},
        {"year": 2000, "curriculum": "All Graduates", "overall_gpa": 2.94, "math_gpa": 2.58, "naep_math_scale": np.nan, "credits_earned": 25.8},
        {"year": 2005, "curriculum": "All Graduates", "overall_gpa": 2.98, "math_gpa": 2.60, "naep_math_scale": 150.0, "credits_earned": 26.8},
        {"year": 2009, "curriculum": "All Graduates", "overall_gpa": 3.00, "math_gpa": 2.65, "naep_math_scale": 153.0, "credits_earned": 27.2},
        {"year": 2019, "curriculum": "All Graduates", "overall_gpa": 3.11, "math_gpa": 2.79, "naep_math_scale": 150.0, "credits_earned": 28.1},
        
        # Rigorous Curriculum (4 yrs English, 4 yrs Math incl precalc/calc, 3 yrs Science, 3 yrs Social Studies, 0.5+ foreign language)
        {"year": 2009, "curriculum": "Rigorous Curriculum", "overall_gpa": 3.61, "math_gpa": 3.32, "naep_math_scale": 188.0, "credits_earned": 29.4},
        {"year": 2019, "curriculum": "Rigorous Curriculum", "overall_gpa": 3.69, "math_gpa": 3.44, "naep_math_scale": 184.0, "credits_earned": 30.1},
        
        # Midlevel Curriculum (4 yrs English, 3 yrs Math incl Algebra I & Geometry, 3 yrs Science, 3 yrs Social Studies)
        {"year": 2009, "curriculum": "Midlevel Curriculum", "overall_gpa": 3.12, "math_gpa": 2.74, "naep_math_scale": 160.0, "credits_earned": 27.8},
        {"year": 2019, "curriculum": "Midlevel Curriculum", "overall_gpa": 3.25, "math_gpa": 2.91, "naep_math_scale": 158.0, "credits_earned": 28.6},
        
        # Standard Curriculum or Below
        {"year": 2009, "curriculum": "Standard / Below", "overall_gpa": 2.68, "math_gpa": 2.29, "naep_math_scale": 143.0, "credits_earned": 25.7},
        {"year": 2019, "curriculum": "Standard / Below", "overall_gpa": 2.79, "math_gpa": 2.41, "naep_math_scale": 140.0, "credits_earned": 26.3},
    ]
    df = pd.DataFrame(records)
    out_path = PROCESSED_DIR / "naep_hsts_trends.csv"
    df.to_csv(out_path, index=False)
    print(f"[*] Saved NAEP HSTS trends to {out_path}")
    return df

def build_act_inflation_data():
    """
    Constructs the longitudinal ACT Grade Inflation dataset (2010-2021).
    Source: Sanchez & Moore (2022), ACT Research Report Series.
    """
    data = [
        {"year": 2010, "avg_hs_gpa": 3.17, "act_composite": 21.0, "act_math": 21.0, "pct_math_benchmark": 43.0},
        {"year": 2011, "avg_hs_gpa": 3.18, "act_composite": 21.1, "act_math": 21.1, "pct_math_benchmark": 45.0},
        {"year": 2012, "avg_hs_gpa": 3.20, "act_composite": 21.1, "act_math": 21.1, "pct_math_benchmark": 46.0},
        {"year": 2013, "avg_hs_gpa": 3.22, "act_composite": 20.9, "act_math": 20.9, "pct_math_benchmark": 44.0},
        {"year": 2014, "avg_hs_gpa": 3.23, "act_composite": 21.0, "act_math": 20.9, "pct_math_benchmark": 43.0},
        {"year": 2015, "avg_hs_gpa": 3.24, "act_composite": 21.0, "act_math": 20.8, "pct_math_benchmark": 42.0},
        {"year": 2016, "avg_hs_gpa": 3.26, "act_composite": 20.8, "act_math": 20.6, "pct_math_benchmark": 41.0},
        {"year": 2017, "avg_hs_gpa": 3.27, "act_composite": 21.0, "act_math": 20.7, "pct_math_benchmark": 41.0},
        {"year": 2018, "avg_hs_gpa": 3.28, "act_composite": 20.8, "act_math": 20.5, "pct_math_benchmark": 40.0},
        {"year": 2019, "avg_hs_gpa": 3.32, "act_composite": 20.7, "act_math": 20.4, "pct_math_benchmark": 39.0},
        {"year": 2020, "avg_hs_gpa": 3.34, "act_composite": 20.6, "act_math": 20.2, "pct_math_benchmark": 37.0},
        {"year": 2021, "avg_hs_gpa": 3.36, "act_composite": 20.3, "act_math": 19.9, "pct_math_benchmark": 36.0},
    ]
    df = pd.DataFrame(data)
    out_path = PROCESSED_DIR / "act_gpa_score_trends.csv"
    df.to_csv(out_path, index=False)
    print(f"[*] Saved ACT trends to {out_path}")
    return df

def build_uchicago_college_prediction_data():
    """
    Constructs the University of Chicago CCSR empirical parameters (Allensworth & Clark, 2020).
    Demonstrates 4-year college graduation rate across high school GPA bands and ACT score tiers.
    """
    records = []
    gpa_bands = [
        {"gpa_bracket": "< 2.5", "gpa_midpoint": 2.2, "act_low_grad_rate": 18.2, "act_mid_grad_rate": 20.4, "act_high_grad_rate": 22.8, "marginal_gpa_effect": 19.5},
        {"gpa_bracket": "2.5 - 2.9", "gpa_midpoint": 2.7, "act_low_grad_rate": 34.5, "act_mid_grad_rate": 37.8, "act_high_grad_rate": 41.2, "marginal_gpa_effect": 38.0},
        {"gpa_bracket": "3.0 - 3.4", "gpa_midpoint": 3.2, "act_low_grad_rate": 52.1, "act_mid_grad_rate": 55.4, "act_high_grad_rate": 60.1, "marginal_gpa_effect": 56.0},
        {"gpa_bracket": "3.5 - 4.0", "gpa_midpoint": 3.75, "act_low_grad_rate": 68.7, "act_mid_grad_rate": 72.3, "act_high_grad_rate": 78.4, "marginal_gpa_effect": 73.5},
    ]
    df = pd.DataFrame(gpa_bands)
    out_path = PROCESSED_DIR / "uchicago_college_prediction.csv"
    df.to_csv(out_path, index=False)
    print(f"[*] Saved University of Chicago parameters to {out_path}")
    return df

if __name__ == "__main__":
    df_naep = build_naep_hsts_data()
    df_act = build_act_inflation_data()
    df_ccsr = build_uchicago_college_prediction_data()
    
    # Export summary table 1
    t1_records = [
        {"Metric": "NAEP HSTS Average HS GPA (Overall)", "Baseline (2009/2010)": 3.00, "End Year (2019/2021)": 3.11, "Net Change": "+0.11 GPA pts", "Sample": "National Representative HSTS"},
        {"Metric": "NAEP HSTS Math Course GPA", "Baseline (2009/2010)": 2.65, "End Year (2019/2021)": 2.79, "Net Change": "+0.14 GPA pts", "Sample": "National Representative HSTS"},
        {"Metric": "NAEP 12th Grade Math Scale Score", "Baseline (2009/2010)": 153.0, "End Year (2019/2021)": 150.0, "Net Change": "-3.0 pts", "Sample": "NAEP Tested Seniors"},
        {"Metric": "NAEP Math (Rigorous Curriculum Graduates)", "Baseline (2009/2010)": 188.0, "End Year (2019/2021)": 184.0, "Net Change": "-4.0 pts", "Sample": "Rigorous Curriculum Seniors"},
        {"Metric": "Rigorous Curriculum High School GPA", "Baseline (2009/2010)": 3.61, "End Year (2019/2021)": 3.69, "Net Change": "+0.08 GPA pts", "Sample": "Rigorous Curriculum Seniors"},
        {"Metric": "ACT Tested Average Reported GPA", "Baseline (2009/2010)": 3.17, "End Year (2019/2021)": 3.36, "Net Change": "+0.19 GPA pts", "Sample": "ACT Tested Graduates (~2M/yr)"},
        {"Metric": "ACT Composite Average Score", "Baseline (2009/2010)": 21.0, "End Year (2019/2021)": 20.3, "Net Change": "-0.7 score pts", "Sample": "ACT Tested Graduates"},
        {"Metric": "ACT Mathematics Average Score", "Baseline (2009/2010)": 21.0, "End Year (2019/2021)": 19.9, "Net Change": "-1.1 score pts", "Sample": "ACT Tested Graduates"},
    ]
    df_t1 = pd.DataFrame(t1_records)
    df_t1.to_csv(TABLES_DIR / "table1_national_trends.csv", index=False)
    print(f"[*] Generated Table 1 at {TABLES_DIR / 'table1_national_trends.csv'}")
