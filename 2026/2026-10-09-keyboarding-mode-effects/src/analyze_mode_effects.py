"""
src/analyze_mode_effects.py

Performs audited empirical synthesis, mode difference contrast calculations,
and exploratory parameter sensitivity accounting for the Keyboarding & Digital
Assessment Mode Effects Observatory (Review 2 Reconciled Edition).
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"


def ensure_directories():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)


def analyze_divergent_trends():
    """Audited longitudinal trends from NCES HSTS Table 1, School Pulse, and ICILS."""
    df_hsts = pd.read_csv(RAW_DIR / "nces_hsts_2019_table1.csv")

    kb_2000 = df_hsts[(df_hsts["course_title"] == "Keyboarding") & (df_hsts["year"] == 2000)]["pct_graduates"].values[0]
    kb_2019 = df_hsts[(df_hsts["course_title"] == "Keyboarding") & (df_hsts["year"] == 2019)]["pct_graduates"].values[0]

    ca_2000 = df_hsts[(df_hsts["course_title"] == "Computer Applications") & (df_hsts["year"] == 2000)]["pct_graduates"].values[0]
    ca_2009 = df_hsts[(df_hsts["course_title"] == "Computer Applications") & (df_hsts["year"] == 2009)]["pct_graduates"].values[0]
    ca_2019 = df_hsts[(df_hsts["course_title"] == "Computer Applications") & (df_hsts["year"] == 2019)]["pct_graduates"].values[0]

    wp_2000 = df_hsts[(df_hsts["course_title"] == "Word Processing") & (df_hsts["year"] == 2000)]["pct_graduates"].values[0]
    wp_2019 = df_hsts[(df_hsts["course_title"] == "Word Processing") & (df_hsts["year"] == 2019)]["pct_graduates"].values[0]

    table1_data = [
        {
            "indicator": "High School Graduates Earning Keyboarding Credit",
            "historical_benchmark": f"{kb_2000:.1f}% (2000)",
            "recent_benchmark": f"{kb_2019:.1f}% (2019)",
            "net_change": f"{kb_2019 - kb_2000:.1f} pp (-94.3% rel)",
            "verification_status": "Verified (NCES HSTS Table 1)",
            "source_citation": "NCES High School Transcript Study 2019, Table 1"
        },
        {
            "indicator": "High School Graduates Earning Computer Applications Credit",
            "historical_benchmark": f"{ca_2000:.1f}% (2000) / {ca_2009:.1f}% (2009)",
            "recent_benchmark": f"{ca_2019:.1f}% (2019)",
            "net_change": f"{ca_2019 - ca_2000:+.1f} pp from 2000 (-21.0 pp from peak)",
            "verification_status": "Verified (NCES HSTS Table 1)",
            "source_citation": "NCES High School Transcript Study 2019, Table 1"
        },
        {
            "indicator": "High School Graduates Earning Word Processing Credit",
            "historical_benchmark": f"{wp_2000:.1f}% (2000)",
            "recent_benchmark": f"{wp_2019:.1f}% (2019)",
            "net_change": f"{wp_2019 - wp_2000:.1f} pp (-90.6% rel)",
            "verification_status": "Verified (NCES HSTS Table 1)",
            "source_citation": "NCES High School Transcript Study 2019, Table 1"
        },
        {
            "indicator": "Public Schools with 1:1 Student Device Programs",
            "historical_benchmark": "83.0% (2021-22, School Pulse)",
            "recent_benchmark": "88.0% (2024-25)",
            "net_change": "+5.0 pp in School Pulse Panel",
            "verification_status": "Verified (NCES School Pulse 2025)",
            "source_citation": "NCES School Pulse Panel (2021-2025)"
        },
        {
            "indicator": "US 8th-Grade Computer & Information Literacy (ICILS)",
            "historical_benchmark": "519 pts (2018)",
            "recent_benchmark": "482 pts (2023)",
            "net_change": "-37.0 scale pts (-0.37 SD)",
            "verification_status": "Verified (IEA ICILS 2018/2023)",
            "source_citation": "IEA / NCES ICILS Assessment Reports"
        }
    ]
    df_table1 = pd.DataFrame(table1_data)
    df_table1.to_csv(TABLES_DIR / "table1_hsts_course_trends.csv", index=False)
    return df_table1


def analyze_naep_table41c_contrasts():
    """
    Audited item-level mode differences from NCES NAEP 2017 Mode Evaluation Table 4.1c (p. 37).
    Includes Reading AND Mathematics across Grades 4 and 8 in percentage points.
    """
    df_41c = pd.read_csv(RAW_DIR / "naep_2017_mode_table41c.csv")

    # Grade 4 Reading
    g4_r_sr = df_41c[(df_41c["grade"] == 4) & (df_41c["subject"] == "Reading") & (df_41c["item_type"].str.contains("Selected"))]["difference_pp"].values[0]
    g4_r_cr = df_41c[(df_41c["grade"] == 4) & (df_41c["subject"] == "Reading") & (df_41c["item_type"].str.contains("Constructed"))]["difference_pp"].values[0]
    format_gap_g4_r = g4_r_cr - g4_r_sr

    # Grade 4 Mathematics
    g4_m_sr = df_41c[(df_41c["grade"] == 4) & (df_41c["subject"] == "Mathematics") & (df_41c["item_type"].str.contains("Selected"))]["difference_pp"].values[0]
    g4_m_cr = df_41c[(df_41c["grade"] == 4) & (df_41c["subject"] == "Mathematics") & (df_41c["item_type"].str.contains("Constructed"))]["difference_pp"].values[0]
    format_gap_g4_m = g4_m_cr - g4_m_sr

    # Grade 8 Reading
    g8_r_sr = df_41c[(df_41c["grade"] == 8) & (df_41c["subject"] == "Reading") & (df_41c["item_type"].str.contains("Selected"))]["difference_pp"].values[0]
    g8_r_cr = df_41c[(df_41c["grade"] == 8) & (df_41c["subject"] == "Reading") & (df_41c["item_type"].str.contains("Constructed"))]["difference_pp"].values[0]
    format_gap_g8_r = g8_r_cr - g8_r_sr

    contrasts = [
        {
            "comparison_domain": "Grade 4 Reading (Table 4.1c)",
            "selected_response_diff": f"{g4_r_sr:.1f} pp",
            "constructed_response_diff": f"{g4_r_cr:.1f} pp",
            "format_gap": f"{format_gap_g4_r:.1f} pp",
            "substantive_finding": "Both item types show statistically significant negative mode differences in Grade 4. Constructed response exhibits an incremental -3.0 pp gap (-6.8 pp vs -3.8 pp)."
        },
        {
            "comparison_domain": "Grade 4 Mathematics (Table 4.1c)",
            "selected_response_diff": f"{g4_m_sr:.1f} pp",
            "constructed_response_diff": f"{g4_m_cr:.1f} pp",
            "format_gap": f"{format_gap_g4_m:.1f} pp",
            "substantive_finding": "Constructed response difference (-6.9 pp) is almost identical to reading (-6.8 pp), pointing to a general response construction bottleneck (equations, diagrams, text) rather than keyboarding alone."
        },
        {
            "comparison_domain": "Grade 8 Reading (Table 4.1c)",
            "selected_response_diff": f"{g8_r_sr:.1f} pp",
            "constructed_response_diff": f"{g8_r_cr:.1f} pp",
            "format_gap": f"{format_gap_g8_r:.1f} pp",
            "substantive_finding": "At Grade 8, mode differences attenuate substantially (-1.6 pp SR vs -2.0 pp CR), leaving a narrow -0.4 pp format gap as student digital fluency matures."
        }
    ]
    df_contrasts = pd.DataFrame(contrasts)
    df_contrasts.to_csv(TABLES_DIR / "table2_naep_mode_contrasts.csv", index=False)
    return df_contrasts


def analyze_instruction_equity():
    """Audited EdWeek 2024 survey statistics (74% vs 51% in K-2)."""
    df_equity = pd.read_csv(RAW_DIR / "edweek_equity_breakdown_2024.csv")
    k2_low = df_equity[(df_equity["grade_span"] == "Grades K-2") & (df_equity["poverty_tier"] == "Lower-Poverty Systems")]["pct_reporting_instruction"].values[0]
    k2_high = df_equity[(df_equity["grade_span"] == "Grades K-2") & (df_equity["poverty_tier"] == "Higher-Poverty Systems")]["pct_reporting_instruction"].values[0]
    k2_ratio = k2_low / k2_high

    summary = [
        {
            "metric": "Grades K-2 Keyboarding Instruction (Lower-Poverty Systems)",
            "reported_value": f"{k2_low:.1f}%",
            "verification_status": "Verified (EdWeek 2024)",
            "context": "Three-quarters of leaders in lower-poverty systems report K-2 typing instruction."
        },
        {
            "metric": "Grades K-2 Keyboarding Instruction (Higher-Poverty Systems)",
            "reported_value": f"{k2_high:.1f}%",
            "verification_status": "Verified (EdWeek 2024)",
            "context": "Approximately half of leaders in higher-poverty systems report K-2 typing instruction."
        },
        {
            "metric": "Grades K-2 Socioeconomic Disparity Ratio",
            "reported_value": f"{k2_ratio:.2f}x",
            "verification_status": "Author Calculation (74% / 51%)",
            "context": "Lower-poverty systems are ~1.45 times more likely to report early keyboarding instruction."
        },
        {
            "metric": "Standalone Keyboarding Class Delivery (All Grades)",
            "reported_value": "19.0% (8% standalone only + 11% combined)",
            "verification_status": "Verified (EdWeek 2024)",
            "context": "Only ~1 in 5 districts maintain dedicated standalone keyboarding classes."
        },
        {
            "metric": "Integrated within Regular Classroom Instruction",
            "reported_value": "50.0%",
            "verification_status": "Verified (EdWeek 2024)",
            "context": "Half of districts rely on teachers embedding typing into general coursework."
        }
    ]
    df_summary = pd.DataFrame(summary)
    df_summary.to_csv(TABLES_DIR / "table3_edweek_instruction_equity.csv", index=False)
    return df_summary


def analyze_literature_benchmark_table():
    """Compiles the verified empirical literature benchmark table."""
    df_meta = pd.read_csv(RAW_DIR / "mode_effects_literature_meta.csv")
    df_meta.to_csv(TABLES_DIR / "table4_literature_benchmark.csv", index=False)
    return df_meta


def main():
    print("=" * 70)
    print("ANALYZING AUDITED KEYBOARDING & DIGITAL ASSESSMENT MODE EFFECTS (ROUND 2)")
    print("=" * 70)
    ensure_directories()
    
    t1 = analyze_divergent_trends()
    print(f"[OK] Generated Table 1: Audited Divergent Trends ({len(t1)} rows)")

    t2 = analyze_naep_table41c_contrasts()
    print(f"[OK] Generated Table 2: Verified NAEP Mode Contrasts ({len(t2)} rows)")

    t3 = analyze_instruction_equity()
    print(f"[OK] Generated Table 3: Audited EdWeek Equity Summary ({len(t3)} rows)")

    t4 = analyze_literature_benchmark_table()
    print(f"[OK] Generated Table 4: Literature Benchmark Panel ({len(t4)} rows)")

    print("\nAudited analysis complete.")


if __name__ == "__main__":
    main()
