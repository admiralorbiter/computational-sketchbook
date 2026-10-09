"""
src/analyze_mode_effects.py

Performs formal statistical analysis, effect size contrast decomposition,
and psychometric construct-irrelevant variance (CIV) accounting for
the Keyboarding & Digital Assessment Mode Effects Observatory.
"""

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"


def ensure_directories():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)


def analyze_divergent_trends():
    """Computes rate of change and divergence ratios between device access and typing coursework."""
    df_hsts = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "nces_hsts_2019_table1.csv")
    df_pulse = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "nces_pulse_device_access.csv")

    kb_2000 = df_hsts[(df_hsts["course_title"] == "Keyboarding") & (df_hsts["year"] == 2000)]["pct_graduates"].values[0]
    kb_2019 = df_hsts[(df_hsts["course_title"] == "Keyboarding") & (df_hsts["year"] == 2019)]["pct_graduates"].values[0]

    dev_2013 = df_pulse[df_pulse["year"] == 2013]["pct_1to1_devices"].values[0]
    dev_2024 = df_pulse[df_pulse["year"] == 2024]["pct_1to1_devices"].values[0]

    kb_rel_change = (kb_2019 - kb_2000) / kb_2000 * 100
    kb_abs_change = kb_2019 - kb_2000

    dev_rel_change = (dev_2024 - dev_2013) / dev_2013 * 100
    dev_abs_change = dev_2024 - dev_2013

    table1_data = [
        {
            "indicator": "High School Graduates Earning Keyboarding Credit",
            "baseline_val": f"{kb_2000:.1f}% (2000)",
            "recent_val": f"{kb_2019:.1f}% (2019)",
            "abs_change_pp": f"{kb_abs_change:.1f} pp",
            "rel_change_pct": f"{kb_rel_change:.1f}%",
            "source": "NCES NAEP HSTS Table 1"
        },
        {
            "indicator": "Public Schools with 1-to-1 Student Device Programs",
            "baseline_val": f"{dev_2013:.1f}% (2013)",
            "recent_val": f"{dev_2024:.1f}% (2024)",
            "abs_change_pp": f"+{dev_abs_change:.1f} pp",
            "rel_change_pct": f"+{dev_rel_change:.1f}%",
            "source": "NCES School Pulse Panel (2025)"
        },
        {
            "indicator": "US 8th-Grade Computer & Information Literacy (ICILS)",
            "baseline_val": "519 pts (2018)",
            "recent_val": "482 pts (2023)",
            "abs_change_pp": "-37.0 scale pts",
            "rel_change_pct": "-7.1% (-0.37 SD)",
            "source": "IEA ICILS 2018 / 2023"
        }
    ]
    df_table1 = pd.DataFrame(table1_data)
    df_table1.to_csv(TABLES_DIR / "table1_hsts_course_trends.csv", index=False)
    return df_table1


def analyze_meta_contrasts():
    """Calculates key empirical contrasts across published mode effect studies."""
    df_meta = pd.read_csv(DATA_DIR / "master_mode_effects_benchmark.csv")

    # 1. NAEP Grade 4: Format Wedge (CR vs MC)
    g4_mc = df_meta[df_meta["study_id"] == "NAEP_2017_DBA_G4_Reading_MC"]["effect_size_sd"].values[0]
    g4_cr = df_meta[df_meta["study_id"] == "NAEP_2017_DBA_G4_Reading_CR"]["effect_size_sd"].values[0]
    format_wedge_g4 = g4_cr - g4_mc

    # 2. NAEP Grade 8: Format Wedge (CR vs MC)
    g8_mc = df_meta[df_meta["study_id"] == "NAEP_2017_DBA_G8_Reading_MC"]["effect_size_sd"].values[0]
    g8_cr = df_meta[df_meta["study_id"] == "NAEP_2017_DBA_G8_Reading_CR"]["effect_size_sd"].values[0]
    format_wedge_g8 = g8_cr - g8_mc

    # 3. Developmental Attenuation: Grade 8 CR vs Grade 4 CR
    dev_attenuation = g8_cr - g4_cr

    # 4. Backes & Cowan MA: Subject Wedge (ELA vs Math Year 1)
    ma_ela_y1 = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_ELA_Y1"]["effect_size_sd"].values[0]
    ma_mat_y1 = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_Math_Y1"]["effect_size_sd"].values[0]
    subject_wedge_ma = ma_ela_y1 - ma_mat_y1

    # 5. Backes & Cowan MA: Multi-year Persistence (Year 2 / Year 1)
    ma_ela_y2 = df_meta[df_meta["study_id"] == "Backes_Cowan_2019_MA_ELA_Y2"]["effect_size_sd"].values[0]
    persistence_ratio_ela = ma_ela_y2 / ma_ela_y1

    contrasts = [
        {
            "contrast_name": "NAEP G4 Item Format Wedge (Constructed Response vs. Multiple Choice)",
            "estimate_sd": format_wedge_g4,
            "interpretation": "Mode penalty is virtually 0 on MC (-0.01 SD) but severe on typed CR (-0.18 SD), yielding a -0.17 SD format penalty."
        },
        {
            "contrast_name": "NAEP Age Attenuation (Grade 8 CR vs. Grade 4 CR)",
            "estimate_sd": dev_attenuation,
            "interpretation": "Older students recover +0.10 SD, cutting the constructed-response mode penalty by more than half (55.6% reduction)."
        },
        {
            "contrast_name": "MA PARCC Subject Wedge (ELA vs. Math in Year 1)",
            "estimate_sd": subject_wedge_ma,
            "interpretation": "ELA (-0.25 SD) incurs a 2.5x larger penalty than Math (-0.10 SD) due to extensive essay and passage transcription demands."
        },
        {
            "contrast_name": "MA PARCC Mode Penalty Second-Year Persistence (ELA)",
            "estimate_sd": ma_ela_y2,
            "interpretation": f"Diminishes from -0.25 SD to -0.13 SD ({persistence_ratio_ela*100:.1f}% remaining penalty), proving familiarity reduces but does not eliminate penalty."
        }
    ]
    df_contrasts = pd.DataFrame(contrasts)
    df_contrasts.to_csv(TABLES_DIR / "table2_mode_effects_meta.csv", index=False)
    return df_contrasts


def analyze_instruction_equity():
    """Synthesizes the EdWeek 2024 instruction distribution and poverty gradient."""
    df_deliv = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "edweek_keyboarding_survey_2024.csv")
    df_equity = pd.read_csv(PROJECT_ROOT / "data" / "raw" / "edweek_equity_breakdown_2024.csv")

    # K-2 disparity ratio
    k2_low_pov = df_equity[(df_equity["grade_span"] == "Grades K-2") & (df_equity["poverty_tier"] == "Lower-Poverty Systems")]["pct_reporting_instruction"].values[0]
    k2_high_pov = df_equity[(df_equity["grade_span"] == "Grades K-2") & (df_equity["poverty_tier"] == "Higher-Poverty Systems")]["pct_reporting_instruction"].values[0]
    k2_ratio = k2_low_pov / k2_high_pov

    summary = [
        {
            "dimension": "Instructional Delivery Model",
            "metric": "Standalone Keyboarding Class (Standalone or Combined)",
            "value": "19.0%",
            "benchmark_context": "Only ~1 in 5 districts offer a dedicated typing course."
        },
        {
            "dimension": "Instructional Delivery Model",
            "metric": "Integrated within Regular Classroom Only",
            "value": "50.0%",
            "benchmark_context": "Half of districts rely on teachers embedding typing into subject matter."
        },
        {
            "dimension": "Instructional Delivery Model",
            "metric": "No Formal Keyboarding Instruction",
            "value": "31.0%",
            "benchmark_context": "Nearly a third of school systems provide zero structured keyboarding."
        },
        {
            "dimension": "Early-Grade Equity (K-2)",
            "metric": "Lower-Poverty Systems Reporting K-2 Instruction",
            "value": f"{k2_low_pov:.1f}%",
            "benchmark_context": "Over one-third of affluent systems introduce keyboarding early."
        },
        {
            "dimension": "Early-Grade Equity (K-2)",
            "metric": "Higher-Poverty Systems Reporting K-2 Instruction",
            "value": f"{k2_high_pov:.1f}%",
            "benchmark_context": f"Lower-poverty systems are {k2_ratio:.1f}x more likely to provide early typing."
        }
    ]
    df_summary = pd.DataFrame(summary)
    df_summary.to_csv(TABLES_DIR / "table3_edweek_instruction_equity.csv", index=False)
    return df_summary


def analyze_civ_simulation():
    """
    Evaluates the simulated psychometric measurement error decomposition.
    Calculates proportion of score variance attributable to interface friction.
    """
    df_sim = pd.read_parquet(DATA_DIR / "construct_irrelevant_variance_simulation.parquet")

    # Grade 4 vs Grade 8 Constructed Response Penalty
    g4_pen = df_sim[df_sim["grade"] == 4]["delta_cr_mode"].mean()
    g8_pen = df_sim[df_sim["grade"] == 8]["delta_cr_mode"].mean()

    # SES gap in CR penalty
    g4_low_ses = df_sim[(df_sim["grade"] == 4) & (df_sim["low_ses"] == 1)]["delta_cr_mode"].mean()
    g4_high_ses = df_sim[(df_sim["grade"] == 4) & (df_sim["low_ses"] == 0)]["delta_cr_mode"].mean()

    # Variance decomposition on Grade 4 CR Digital
    g4_data = df_sim[df_sim["grade"] == 4]
    var_total = np.var(g4_data["score_cr_digital"])
    var_true = np.var(g4_data["theta_true"])
    var_penalty = np.var(g4_data["typing_civ_penalty"])
    civ_variance_share = var_penalty / var_total

    print(f"Simulation Analysis:")
    print(f"  - Grade 4 CR Mode Penalty Mean: {g4_pen:.3f} SD")
    print(f"  - Grade 8 CR Mode Penalty Mean: {g8_pen:.3f} SD")
    print(f"  - Grade 4 SES Disparity in CR Penalty: Low SES={g4_low_ses:.3f} SD vs High SES={g4_high_ses:.3f} SD (Gap: {g4_low_ses - g4_high_ses:.3f} SD)")
    print(f"  - Construct-Irrelevant Interface Variance Share at Grade 4: {civ_variance_share*100:.1f}% of total test score variance")


def build_research_agenda_matrix():
    """Constructs the research agenda matrix separating Claim 1 from Claim 2."""
    agenda = [
        {
            "claim_level": "Claim 1: Interface Friction Penalty",
            "proposition": "Students lose test score points specifically because of interface/keyboarding bottlenecks on digital assessments.",
            "evidentiary_status": "STRONG EMPIRICAL SUPPORT",
            "replicated_evidence": "Backes & Cowan (2019: -0.25 SD ELA); NAEP 2017 Mode Study (-0.18 SD on G4 CR vs -0.01 SD on MC); 2017 NAEP Writing failure.",
            "next_research_step": "Within-student randomized crossover study: Paper essay vs. Laptop essay with timed WPM and error tracking."
        },
        {
            "claim_level": "Claim 2: Macro Score Decline Mechanism",
            "proposition": "The national decline in student test scores over the past decade was primarily caused by the decline of keyboarding instruction.",
            "evidentiary_status": "UNSUPPORTED / CONFOUNDED",
            "replicated_evidence": "NAEP 2017+ scores are statistically linked/equated; declines continued in 2022-2024 post-pandemic; TN study found null effect of typing class alone.",
            "next_research_step": "Quarantine claim from causal attribution; focus rather on measurement validity and construct-irrelevant variance."
        }
    ]
    df_agenda = pd.DataFrame(agenda)
    df_agenda.to_csv(TABLES_DIR / "table4_research_agenda_matrix.csv", index=False)
    return df_agenda


def main():
    print("=" * 70)
    print("ANALYZING KEYBOARDING & DIGITAL ASSESSMENT MODE EFFECTS")
    print("=" * 70)
    ensure_directories()
    
    t1 = analyze_divergent_trends()
    print(f"[OK] Generated Table 1: Divergent Trends Summary ({len(t1)} rows)")

    t2 = analyze_meta_contrasts()
    print(f"[OK] Generated Table 2: Empirical Mode Contrasts ({len(t2)} rows)")

    t3 = analyze_instruction_equity()
    print(f"[OK] Generated Table 3: Instruction Equity Summary ({len(t3)} rows)")

    t4 = build_research_agenda_matrix()
    print(f"[OK] Generated Table 4: Research Agenda Demarcation ({len(t4)} rows)")

    analyze_civ_simulation()
    print("\nStatistical and psychometric analysis complete.")


if __name__ == "__main__":
    main()
