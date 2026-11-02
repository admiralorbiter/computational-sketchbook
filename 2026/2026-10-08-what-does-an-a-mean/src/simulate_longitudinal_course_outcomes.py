"""
src/simulate_longitudinal_course_outcomes.py

SIMULATION MODULE FOR PIPELINE VALIDATION & PRE-ANALYSIS POWER MODELING
========================================================================
WARNING: THIS SCRIPT GENERATES SYNTHETIC OBSERVATIONS FOR METHODOLOGICAL
AND ECONOMETRIC PIPELINE VALIDATION ONLY.

THESE DATA ARE NOT EMPIRICAL KCPS STUDENT RECORDS.
THEY MUST NOT BE PRESENTED AS OBSERVED OUTCOMES OR USED TO DRAW FACTUAL
CONCLUSIONS REGARDING DISTRICT POLICY EFFECTS.

Purpose:
- Validates the Difference-in-Differences (DiD) econometric architecture.
- Tests dynamic policy exposure linkages via `assign_school_policy_exposure()`.
- Establishes statistical power requirements for the eventual empirical study
  when de-identified student course records are obtained from KCPS.

Outputs:
- data/synthetic/kcps_simulated_course_outcomes.csv
- artifacts/tables/table6_simulated_kcps_policy_scenario.csv
- artifacts/figures/05_simulated_policy_scenario_demonstration.png
"""

import sys
from pathlib import Path

# Compatibility fix for PySide6 / Shiboken / Python 3.12 meta-path inspection
try:
    import six
    if hasattr(six, "_SixMetaPathImporter") and not hasattr(six._SixMetaPathImporter, "_path"):
        six._SixMetaPathImporter._path = None
except ImportError:
    pass

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.analyze_institutional_incentives import assign_school_policy_exposure

SYNTHETIC_DIR = BASE_DIR / "data" / "synthetic"
SOURCES_DIR = BASE_DIR / "sources"
TABLES_DIR = BASE_DIR / "artifacts" / "tables"
FIG_DIR = BASE_DIR / "artifacts" / "figures"


def generate_synthetic_scenario(df_evidence: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a synthetic scenario for econometric testing and power modeling.
    Explicitly tags every observation with `is_simulated = True`.
    """
    schools = [
        ("CENTRAL HIGH SCHOOL", "048-078", 0.95),
        ("EAST HIGH SCHOOL", "048-078", 0.92),
        ("LINCOLN COLLEGE PREP.", "048-078", 0.25),
        ("NORTHEAST HIGH", "048-078", 0.94),
        ("SOUTHEAST HIGH SCHOOL", "048-078", 0.93),
        ("PASEO ACAD. OF PERFORMING ARTS", "048-078", 0.65)
    ]
    
    years = ["2021-2022", "2022-2023", "2023-2024", "2024-2025"]
    terms = ["Fall", "Spring"]
    courses = [
        {"code": "MATH101", "name": "Algebra I", "has_eoc": True, "base_f_rate": 0.28, "eoc_prof_base": 0.138},
        {"code": "MATH201", "name": "Geometry", "has_eoc": False, "base_f_rate": 0.25, "eoc_prof_base": np.nan},
        {"code": "ENG101", "name": "English I", "has_eoc": False, "base_f_rate": 0.22, "eoc_prof_base": np.nan},
        {"code": "SCI101", "name": "Biology", "has_eoc": True, "base_f_rate": 0.24, "eoc_prof_base": 0.162},
    ]
    tracks = ["General Education", "Honors / AP / IB"]
    
    records = []
    rng = np.random.default_rng(20261008)
    
    for school_name, dist_code, gen_share in schools:
        campus_base_enr = 180 if "LINCOLN" in school_name else (140 if "EAST" in school_name or "CENTRAL" in school_name else 110)
        
        for yr in years:
            if yr in ["2021-2022", "2022-2023"]:
                era = "Pre-Reform"
            elif yr == "2023-2024":
                era = "Initial 40% Floor"
            else:
                era = "Revised Missing-Work & Exemption"
                
            for term in terms:
                for crs in courses:
                    for trk in tracks:
                        if trk == "General Education":
                            trk_enr = int(campus_base_enr * gen_share * rng.uniform(0.9, 1.1))
                            if trk_enr < 15:
                                trk_enr = 15
                        else:
                            trk_enr = int(campus_base_enr * (1.0 - gen_share) * rng.uniform(0.9, 1.1))
                            if trk_enr < 8:
                                trk_enr = 8
                                
                        # Dynamic policy lookup via evidence register
                        exposure = assign_school_policy_exposure(
                            school_name=school_name,
                            district_code=dist_code,
                            df_evidence=df_evidence,
                            academic_year=yr,
                            course_track=trk
                        )
                        
                        # Simulated theoretical parameters (for power analysis only)
                        if trk == "General Education":
                            if era == "Pre-Reform":
                                f_rate = crs["base_f_rate"] * (1.0 + rng.uniform(-0.03, 0.03))
                            elif era == "Initial 40% Floor":
                                f_rate = crs["base_f_rate"] * 0.48 * (1.0 + rng.uniform(-0.04, 0.04))
                            else:
                                f_rate = crs["base_f_rate"] * 0.67 * (1.0 + rng.uniform(-0.03, 0.03))
                        else:
                            f_rate = 0.042 * (1.0 + rng.uniform(-0.08, 0.08))
                            
                        if term == "Spring":
                            f_rate *= 1.05
                            
                        f_rate = max(0.01, min(0.45, f_rate))
                        
                        count_f = int(round(trk_enr * f_rate))
                        passing_enr = trk_enr - count_f
                        
                        if trk == "General Education":
                            if era == "Pre-Reform":
                                d_share, c_share, b_share, a_share = 0.26, 0.38, 0.24, 0.12
                            elif era == "Initial 40% Floor":
                                d_share, c_share, b_share, a_share = 0.35, 0.35, 0.20, 0.10
                            else:
                                d_share, c_share, b_share, a_share = 0.30, 0.36, 0.22, 0.12
                        else:
                            d_share, c_share, b_share, a_share = 0.08, 0.22, 0.42, 0.28
                            
                        count_d = int(round(passing_enr * d_share))
                        count_c = int(round(passing_enr * c_share))
                        count_b = int(round(passing_enr * b_share))
                        count_a = max(0, passing_enr - (count_d + count_c + count_b))
                        
                        total_enr = count_a + count_b + count_c + count_d + count_f
                        assert total_enr == trk_enr
                        
                        credits_att = round(total_enr * 0.5, 1)
                        credits_ear = round((total_enr - count_f) * 0.5, 1)
                        completion_pct = round((credits_ear / credits_att) * 100.0, 1)
                        
                        if crs["has_eoc"] and term == "Spring":
                            if trk == "General Education":
                                eoc_prof = crs["eoc_prof_base"] * (1.0 + rng.uniform(-0.05, 0.05))
                                eoc_bb = 0.52 * (1.0 + rng.uniform(-0.04, 0.04))
                            else:
                                eoc_prof = 0.72 * (1.0 + rng.uniform(-0.04, 0.04))
                                eoc_bb = 0.08 * (1.0 + rng.uniform(-0.05, 0.05))
                            eoc_prof_pct = round(eoc_prof * 100.0, 1)
                            eoc_bb_pct = round(eoc_bb * 100.0, 1)
                        else:
                            eoc_prof_pct = np.nan
                            eoc_bb_pct = np.nan
                            
                        records.append({
                            # Strict data provenance labels
                            "is_simulated": True,
                            "data_provenance": "SYNTHETIC_SIMULATION_FOR_PIPELINE_VALIDATION",
                            "district_code": dist_code,
                            "district_name": "Kansas City 33",
                            "school_name": school_name,
                            "academic_year": yr,
                            "policy_era": era,
                            "term": term,
                            "course_code": crs["code"],
                            "course_title": crs["name"],
                            "course_track": trk,
                            "simulated_course_enrollment": total_enr,
                            "simulated_count_A": count_a,
                            "simulated_count_B": count_b,
                            "simulated_count_C": count_c,
                            "simulated_count_D": count_d,
                            "simulated_count_F": count_f,
                            "simulated_pct_A": round((count_a / total_enr) * 100.0, 1),
                            "simulated_pct_B": round((count_b / total_enr) * 100.0, 1),
                            "simulated_pct_C": round((count_c / total_enr) * 100.0, 1),
                            "simulated_pct_D": round((count_d / total_enr) * 100.0, 1),
                            "simulated_pct_F": round((count_f / total_enr) * 100.0, 1),
                            "simulated_failure_rate_pct": round((count_f / total_enr) * 100.0, 1),
                            "simulated_credits_attempted": credits_att,
                            "simulated_credits_earned": credits_ear,
                            "simulated_credit_completion_pct": completion_pct,
                            "simulated_eoc_prof_pct": eoc_prof_pct,
                            "simulated_eoc_bb_pct": eoc_bb_pct,
                            # Linked verified policy metadata
                            "policy_exposure_role": exposure["policy_exposure_role"],
                            "grading_model": exposure["grading_model"],
                            "attempted_work_floor": exposure["attempted_work_floor"],
                            "missing_work_rule": exposure["missing_work_rule"],
                            "reassessment_rule": exposure["reassessment_rule"],
                            "engagement_weight_pct": exposure["engagement_weight_pct"],
                            "progress_weight_pct": exposure["progress_weight_pct"],
                            "proficiency_weight_pct": exposure["proficiency_weight_pct"],
                            "audit_status": exposure["audit_status"]
                        })
                        
    return pd.DataFrame(records)


def summarize_simulated_scenario(df: pd.DataFrame) -> pd.DataFrame:
    """Summarizes simulated parameters by policy era and track for methodological pre-analysis."""
    grouped = df.groupby(["policy_era", "course_track"]).agg(
        simulated_course_enrollment=("simulated_course_enrollment", "sum"),
        simulated_f_grades=("simulated_count_F", "sum"),
        simulated_credits_att=("simulated_credits_attempted", "sum"),
        simulated_credits_ear=("simulated_credits_earned", "sum"),
    ).reset_index()
    
    grouped["simulated_failure_rate_pct"] = (grouped["simulated_f_grades"] / grouped["simulated_course_enrollment"]) * 100.0
    grouped["simulated_credit_completion_pct"] = (grouped["simulated_credits_ear"] / grouped["simulated_credits_att"]) * 100.0
    
    alg_eoc = df[(df["course_title"] == "Algebra I") & (df["term"] == "Spring")].groupby(["policy_era", "course_track"]).agg(
        simulated_eoc_prof_pct=("simulated_eoc_prof_pct", "mean"),
        simulated_eoc_bb_pct=("simulated_eoc_bb_pct", "mean")
    ).reset_index()
    
    table6 = pd.merge(grouped, alg_eoc, on=["policy_era", "course_track"])
    
    era_order = {"Pre-Reform": 1, "Initial 40% Floor": 2, "Revised Missing-Work & Exemption": 3}
    table6["era_rank"] = table6["policy_era"].map(era_order)
    table6 = table6.sort_values(by=["course_track", "era_rank"]).drop(columns=["era_rank"])
    
    table6["simulated_failure_rate_pct"] = table6["simulated_failure_rate_pct"].round(1)
    table6["simulated_credit_completion_pct"] = table6["simulated_credit_completion_pct"].round(1)
    table6["simulated_eoc_prof_pct"] = table6["simulated_eoc_prof_pct"].round(1)
    table6["simulated_eoc_bb_pct"] = table6["simulated_eoc_bb_pct"].round(1)
    
    return table6


def plot_simulated_demonstration(df: pd.DataFrame, output_path: Path):
    """Generates an illustrative figure with prominent SIMULATED SCENARIO watermarking."""
    sns.set_theme(style="whitegrid", font="sans-serif")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    
    palette = {"General Education": "#b91c1c", "Honors / AP / IB": "#1e40af"}
    
    era_summary = df.groupby(["policy_era", "course_track"]).apply(
        lambda g: (g["simulated_count_F"].sum() / g["simulated_course_enrollment"].sum()) * 100.0,
        include_groups=False
    ).reset_index(name="simulated_failure_rate_pct")
    
    era_order = ["Pre-Reform", "Initial 40% Floor", "Revised Missing-Work & Exemption"]
    era_labels = ["Pre-Reform\n(2021–23)", "Initial 40% Floor\n(2023–24)", "Revised 10/40/50\n(2024–25)"]
    
    sns.barplot(
        data=era_summary,
        x="policy_era",
        y="simulated_failure_rate_pct",
        hue="course_track",
        order=era_order,
        palette=palette,
        ax=axes[0]
    )
    axes[0].set_title("[SIMULATED SCENARIO - NOT OBSERVED DATA]\nPanel A: Simulated Course Failure Rate", fontsize=10.5, fontweight="bold", pad=10, color="#991b1b")
    axes[0].set_ylabel("Hypothetical Failure Rate (% F)", fontsize=10, fontweight="semibold")
    axes[0].set_xlabel("")
    axes[0].set_xticks(range(len(era_order)))
    axes[0].set_xticklabels(era_labels, fontsize=9)
    axes[0].legend(title="Track", loc="upper right", frameon=True)
    axes[0].yaxis.set_major_formatter(ticker.PercentFormatter())
    
    for p in axes[0].patches:
        val = p.get_height()
        if val > 0:
            axes[0].annotate(f"{val:.1f}%", (p.get_x() + p.get_width() / 2., val + 0.6),
                             ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    axes[0].set_ylim(0, 35)

    credit_summary = df.groupby(["policy_era", "course_track"]).apply(
        lambda g: (g["simulated_credits_earned"].sum() / g["simulated_credits_attempted"].sum()) * 100.0,
        include_groups=False
    ).reset_index(name="simulated_credit_completion_pct")
    
    sns.barplot(
        data=credit_summary,
        x="policy_era",
        y="simulated_credit_completion_pct",
        hue="course_track",
        order=era_order,
        palette=palette,
        ax=axes[1]
    )
    axes[1].set_title("[SIMULATED SCENARIO - NOT OBSERVED DATA]\nPanel B: Simulated Credit Completion Rate", fontsize=10.5, fontweight="bold", pad=10, color="#991b1b")
    axes[1].set_ylabel("Hypothetical Completion Rate (%)", fontsize=10, fontweight="semibold")
    axes[1].set_xlabel("")
    axes[1].set_xticks(range(len(era_order)))
    axes[1].set_xticklabels(era_labels, fontsize=9)
    axes[1].legend().remove()
    axes[1].yaxis.set_major_formatter(ticker.PercentFormatter())
    
    for p in axes[1].patches:
        val = p.get_height()
        if val > 0:
            axes[1].annotate(f"{val:.1f}%", (p.get_x() + p.get_width() / 2., val + 0.8),
                             ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    axes[1].set_ylim(60, 105)

    alg_df = df[(df["course_title"] == "Algebra I") & (df["course_track"] == "General Education")].copy()
    alg_era = alg_df.groupby("policy_era").apply(
        lambda g: pd.Series({
            "pass_rate": ((g["simulated_course_enrollment"].sum() - g["simulated_count_F"].sum()) / g["simulated_course_enrollment"].sum()) * 100.0,
            "eoc_prof": g[g["term"] == "Spring"]["simulated_eoc_prof_pct"].mean()
        }),
        include_groups=False
    ).loc[era_order].reset_index()
    
    x = np.arange(len(era_order))
    width = 0.35
    
    b1 = axes[2].bar(x - width/2, alg_era["pass_rate"], width, label="Hypothetical Pass Rate (A–D)", color="#059669")
    b2 = axes[2].bar(x + width/2, alg_era["eoc_prof"], width, label="Hypothetical EOC Prof. Rate", color="#d97706")
    
    axes[2].set_title("[SIMULATED SCENARIO - NOT OBSERVED DATA]\nPanel C: Simulated Decoupling Gap in Algebra I", fontsize=10.5, fontweight="bold", pad=10, color="#991b1b")
    axes[2].set_ylabel("Percentage (%)", fontsize=10, fontweight="semibold")
    axes[2].set_xlabel("")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(era_labels, fontsize=9)
    axes[2].yaxis.set_major_formatter(ticker.PercentFormatter())
    axes[2].legend(loc="lower right", frameon=True)
    axes[2].set_ylim(0, 105)
    
    for b in b1:
        val = b.get_height()
        axes[2].annotate(f"{val:.1f}%", (b.get_x() + b.get_width()/2., val + 1.2), ha='center', va='bottom', fontsize=8.5, fontweight='bold', color="#059669")
    for b in b2:
        val = b.get_height()
        axes[2].annotate(f"{val:.1f}%", (b.get_x() + b.get_width()/2., val + 1.2), ha='center', va='bottom', fontsize=8.5, fontweight='bold', color="#d97706")
        
    plt.suptitle("ILLUSTRATIVE SIMULATION ONLY: Hypothetical Course Outcomes Under Assumed Policy Scenarios (NOT OBSERVED DATA)",
                 fontsize=11.5, fontweight="bold", y=0.98, color="#991b1b")
    plt.tight_layout()
    plt.subplots_adjust(top=0.86)
    
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[*] Saved Figure 5 (Simulation Demonstration): {output_path}")


def main():
    print("[*] Running Simulation Pipeline for Econometric Pre-Analysis...")
    SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    
    evidence_file = SOURCES_DIR / "kc_policy_exposure_evidence_register.csv"
    df_evidence = pd.read_csv(evidence_file)
    
    df_sim = generate_synthetic_scenario(df_evidence)
    outcomes_path = SYNTHETIC_DIR / "kcps_simulated_course_outcomes.csv"
    df_sim.to_csv(outcomes_path, index=False)
    print(f"[*] Saved synthetic dataset: {outcomes_path} ({len(df_sim)} records, all tagged is_simulated=True)")
    
    table6 = summarize_simulated_scenario(df_sim)
    table6_path = TABLES_DIR / "table6_simulated_kcps_policy_scenario.csv"
    table6.to_csv(table6_path, index=False)
    print(f"[*] Saved Table 6 (Simulated Scenario): {table6_path} ({len(table6)} rows)")
    
    fig5_path = FIG_DIR / "05_simulated_policy_scenario_demonstration.png"
    plot_simulated_demonstration(df_sim, fig5_path)
    print("[*] Simulation pipeline executed successfully.")


if __name__ == "__main__":
    main()
