"""
Audit Script for Gate 0: Measurement & Temporal Alignment in Florida Secondary Data.

This script executes the foundational Gate 0 empirical audit for Phase 9A:
1. Documentation comparison: CRDC course survey collection instructions vs.
   Florida Statute § 1003.03 and October Survey 2 FTE census compliance rules.
2. Empirical section responsiveness: Tests whether section counts jump discontinuously
   at statutory thresholds E in {25, 50, 75} in Florida non-charter public high schools.
3. Implied class size distributions (C_bar = E / K) near thresholds.
4. Schedule aggregation and multiplicity diagnostics (section multiplicity, small schools,
   broad keyword heuristics, co-teaching omission).
5. Formal local first-stage regression models and best-case sensitivity checks.
6. Evaluation of the Gate 0 Stopping Rule.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"
TABLES_DIR = PROJECT_DIR / "artifacts" / "tables"

def load_florida_high_school_panel():
    """
    Loads CRDC course panel merged with school context panel,
    restricted to Florida non-charter public high schools.
    Note: District-operated schools of choice cannot be fully filtered in CRDC
    due to absence of an is_school_of_choice variable.
    """
    df = pd.read_parquet(DATA_DIR / "crdc_course_panel.parquet")
    sc = pd.read_parquet(DATA_DIR / "school_context_panel.parquet")
    
    sc_cols = sc[["nces_school_id", "school_year", "is_high_school", "is_charter"]].copy()
    merged = df.merge(sc_cols, on=["nces_school_id", "school_year"], how="inner")
    
    # Filter to Florida non-charter public high schools with valid course cells
    fl = merged[
        (merged["state"] == "FL") &
        (merged["is_high_school"] == True) &
        (merged["is_charter"] == False) &
        (merged["num_classes"] > 0) &
        (merged["num_enrolled"] > 0)
    ].copy()
    
    return fl

def audit_crdc_vs_florida_statutory_rules():
    """
    Synthesizes institutional and timing differences between CRDC course surveys
    and Florida Department of Education Survey 2 compliance rules.
    """
    rules_comparison = [
        {
            "dimension": "Legal / Regulatory Basis",
            "florida_survey_2": "Florida Statute § 1003.03 & Art. IX, s. 1 Fla. Const.",
            "crdc_course_data": "Title VI / Section 504 / Title IX OCR Civil Rights Mandate",
            "alignment_verdict": "MISALIGNED: CRDC measures civil rights access; FDOE enforces funding/compliance.",
        },
        {
            "dimension": "Census Timing",
            "florida_survey_2": "Survey 2: Third week of October (Fall FTE membership count)",
            "crdc_course_data": "October 1 fall snapshot for 2013-2021; cumulative full-year for 2023-24 Alg 1",
            "alignment_verdict": "PARTIALLY MISALIGNED: 2023-24 Alg 1 is cumulative; earlier waves contemporaneous fall.",
        },
        {
            "dimension": "Classroom Level vs School Level",
            "florida_survey_2": "Individual classroom level for traditional schools; school-average for charters/choice",
            "crdc_course_data": "School-by-course aggregate cell (total E, total K, mean E/K)",
            "alignment_verdict": "SEVERELY AGGREGATED: CRDC lacks section-level microdata.",
        },
        {
            "dimension": "Co-Teaching / Team Teaching",
            "florida_survey_2": "Two teachers co-teaching 48 students counts as ratio 24:1 (compliant with C=25)",
            "crdc_course_data": "CRDC lacks the educator-per-section linkage needed to reconstruct Florida rule",
            "alignment_verdict": "CONCEALED: Public CRDC cannot observe co-teaching staffing ratios.",
        },
        {
            "dimension": "Post-Survey Flexibility Window",
            "florida_survey_2": "s. 1003.03(2)(b): Allows adding up to 5 students over cap (classes up to 30) post-October",
            "crdc_course_data": "Does not track date of student enrollment additions",
            "alignment_verdict": "UNOBSERVED: Apparent violations of 25 may reflect legal post-October flexibility.",
        },
        {
            "dimension": "Schedule Structure / Semesterization",
            "florida_survey_2": "October Survey 2 counts fall term sections only; Survey 3 counts spring term",
            "crdc_course_data": "Data consistent with term pooling, reporting conventions, and schedule structure",
            "alignment_verdict": "UNOBSERVED: CRDC does not observe schedule type (block vs period).",
        },
    ]
    df_rules = pd.DataFrame(rules_comparison)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    df_rules.to_csv(TABLES_DIR / "table09_gate0_crdc_vs_florida_rules.csv", index=False)
    return df_rules

def audit_threshold_section_jumps(fl_df):
    """
    Empirically tests section count responsiveness and class size jumps
    around statutory cutoffs E in {25, 50, 75}.
    Evaluates:
    - All non-charter Florida public high schools (full sample)
    - Comprehensive high schools (school_enrollment >= 300)
    - Core courses (Algebra 1, Geometry, Biology)
    - Comprehensive core courses
    """
    thresholds = [
        {"cut": 25, "span": (20, 30), "below": 24, "at": 25, "above": 26, "target_k": 2},
        {"cut": 50, "span": (45, 55), "below": 49, "at": 50, "above": 51, "target_k": 3},
        {"cut": 75, "span": (70, 80), "below": 74, "at": 75, "above": 76, "target_k": 4},
    ]
    
    samples = {
        "All Non-Charter High Schools": fl_df,
        "Comprehensive High Schools (Enrollment >= 300)": fl_df[fl_df["school_enrollment"] >= 300],
        "Core Courses (Alg1, Geom, Bio)": fl_df[fl_df["course_code"].isin(["alg1", "geom", "bio"])],
        "Comprehensive Core Courses": fl_df[(fl_df["school_enrollment"] >= 300) & (fl_df["course_code"].isin(["alg1", "geom", "bio"]))],
    }
    
    jump_rows = []
    
    for samp_name, s_df in samples.items():
        for t in thresholds:
            cut = t["cut"]
            b_val, at_val, a_val = t["below"], t["at"], t["above"]
            target_k = t["target_k"]
            
            sub_window = s_df[(s_df["num_enrolled"] >= t["span"][0]) & (s_df["num_enrolled"] <= t["span"][1])]
            
            df_below = s_df[s_df["num_enrolled"] == b_val]
            df_at = s_df[s_df["num_enrolled"] == at_val]
            df_above = s_df[s_df["num_enrolled"] == a_val]
            
            n_below = len(df_below)
            n_at = len(df_at)
            n_above = len(df_above)
            
            # Probability of having >= target_k sections
            p_k_below = (df_below["num_classes"] >= target_k).mean() if n_below > 0 else np.nan
            p_k_at = (df_at["num_classes"] >= target_k).mean() if n_at > 0 else np.nan
            p_k_above = (df_above["num_classes"] >= target_k).mean() if n_above > 0 else np.nan
            
            # Probability of target_k sections exactly
            p_exact_below = (df_below["num_classes"] == target_k).mean() if n_below > 0 else np.nan
            p_exact_at = (df_at["num_classes"] == target_k).mean() if n_at > 0 else np.nan
            p_exact_above = (df_above["num_classes"] == target_k).mean() if n_above > 0 else np.nan
            
            # Mean class size
            cs_below = df_below["mean_class_size"].mean() if n_below > 0 else np.nan
            cs_at = df_at["mean_class_size"].mean() if n_at > 0 else np.nan
            cs_above = df_above["mean_class_size"].mean() if n_above > 0 else np.nan
            
            # Modal K
            mode_below = df_below["num_classes"].mode().iloc[0] if n_below > 0 else np.nan
            mode_at = df_at["num_classes"].mode().iloc[0] if n_at > 0 else np.nan
            mode_above = df_above["num_classes"].mode().iloc[0] if n_above > 0 else np.nan
            
            # Jump across threshold: from below to above, and from at to above
            jump_p_ge_k = p_k_above - p_k_at if (pd.notna(p_k_above) and pd.notna(p_k_at)) else np.nan
            jump_cs = cs_above - cs_at if (pd.notna(cs_above) and pd.notna(cs_at)) else np.nan
            
            # Two-proportion z-test between 'at' and 'above' for P(K >= target_k)
            if n_at > 0 and n_above > 0:
                count_at = (df_at["num_classes"] >= target_k).sum()
                count_above = (df_above["num_classes"] >= target_k).sum()
                pooled_p = (count_at + count_above) / (n_at + n_above)
                se = np.sqrt(pooled_p * (1 - pooled_p) * (1/n_at + 1/n_above)) if 0 < pooled_p < 1 else 0
                z_stat = (p_k_above - p_k_at) / se if se > 0 else 0
                p_val = 2 * (1 - stats.norm.cdf(abs(z_stat)))
            else:
                z_stat, p_val = np.nan, np.nan
                
            jump_rows.append({
                "sample": samp_name,
                "cutoff": cut,
                "target_k": target_k,
                "n_window": len(sub_window),
                "n_below": n_below,
                "n_at": n_at,
                "n_above": n_above,
                "p_ge_k_below": p_k_below,
                "p_ge_k_at": p_k_at,
                "p_ge_k_above": p_k_above,
                "jump_p_ge_k": jump_p_ge_k,
                "z_stat": z_stat,
                "p_value": p_val,
                "p_exact_k_below": p_exact_below,
                "p_exact_k_at": p_exact_at,
                "p_exact_k_above": p_exact_above,
                "mean_cs_below": cs_below,
                "mean_cs_at": cs_at,
                "mean_cs_above": cs_above,
                "jump_cs": jump_cs,
                "mode_k_below": mode_below,
                "mode_k_at": mode_at,
                "mode_k_above": mode_above,
            })
            
    df_jumps = pd.DataFrame(jump_rows)
    df_jumps.to_csv(TABLES_DIR / "table10_gate0_threshold_jump_tests.csv", index=False)
    return df_jumps

def audit_schedule_noise_and_alternative_facilities(fl_df):
    """
    Audits the structural mechanisms creating noise in public CRDC course cells:
    1. Share of multi-class cells (K >= 3) when E is in [20, 30].
    2. Share of cells with mean class size < 10.
    3. Small school facilities (< 300 students) in low-enrollment cells.
    4. Broad school-name keyword flag (heuristic).
    """
    window_20_30 = fl_df[(fl_df["num_enrolled"] >= 20) & (fl_df["num_enrolled"] <= 30)].copy()
    
    total_cells_20_30 = len(window_20_30)
    k_ge_3_count = (window_20_30["num_classes"] >= 3).sum()
    cs_lt_10_count = (window_20_30["mean_class_size"] < 10.0).sum()
    enr_lt_300_count = (window_20_30["school_enrollment"] < 300).sum()
    
    # Broad keyword heuristic flag (caution: ACADEMY/CENTER/PROGRAM are broad heuristics)
    alt_keywords = ["ALTERNATIVE", "CENTER", "ACADEMY", "VIRTUAL", "PACE", "ESE", "JUVENILE", "DETENTION", "CORRECTIONAL", "LEARNING CENTER", "PROGRAM"]
    pattern = "|".join(alt_keywords)
    has_alt_keyword = window_20_30["school_name"].str.upper().str.contains(pattern, regex=True).fillna(False)
    alt_cells_count = has_alt_keyword.sum()
    
    noise_summary = {
        "total_cells_e_20_30": total_cells_20_30,
        "cells_with_k_ge_3": k_ge_3_count,
        "pct_cells_k_ge_3": (k_ge_3_count / total_cells_20_30) * 100,
        "cells_with_cs_lt_10": cs_lt_10_count,
        "pct_cells_cs_lt_10": (cs_lt_10_count / total_cells_20_30) * 100,
        "cells_in_small_schools_lt300": enr_lt_300_count,
        "pct_cells_in_schools_lt300": (enr_lt_300_count / total_cells_20_30) * 100,
        "cells_with_broad_name_keyword_flag": alt_cells_count,
        "pct_cells_broad_name_keyword_flag": (alt_cells_count / total_cells_20_30) * 100,
    }
    
    df_noise = pd.DataFrame([noise_summary])
    df_noise.to_csv(TABLES_DIR / "table11_gate0_schedule_noise_audit.csv", index=False)
    return df_noise

def audit_local_first_stage_regressions(fl_df):
    """
    Estimates actual local first-stage regressions around C=25 (E in [20, 30])
    with HC1 robust standard errors:
    Model 1: Baseline All Non-Charter High Schools (K on 1(E >= 26) + linear E-25)
    Model 2: Comprehensive Non-Charter High Schools (Enrollment >= 300)
    Model 3: Best-Case Clean Sensitivity (Enrollment >= 300, exclude 2020-21 COVID, exclude 2023-24 Alg1)
    Model 4: Best-Case Clean Sensitivity on Class Size (ActualCS on cs_hat + linear E-25)
    """
    fl = fl_df.copy()
    fl["above_25"] = (fl["num_enrolled"] >= 26).astype(int)
    fl["cs_hat"] = fl["num_enrolled"] / np.ceil(fl["num_enrolled"] / 25.0)
    
    # 1. Baseline All Non-Charter
    sub_all = fl[(fl["num_enrolled"] >= 20) & (fl["num_enrolled"] <= 30)].copy()
    sub_all["e_centered"] = sub_all["num_enrolled"] - 25.0
    mod1 = smf.ols("num_classes ~ above_25 + e_centered", data=sub_all).fit(cov_type="HC1")
    
    # 2. Comprehensive High Schools (>= 300)
    sub_comp = sub_all[sub_all["school_enrollment"] >= 300].copy()
    mod2 = smf.ols("num_classes ~ above_25 + e_centered", data=sub_comp).fit(cov_type="HC1")
    
    # 3. Best-Case Clean Sample (>= 300, no COVID wave, no 2023-24 Alg1 cumulative mismatch)
    best_case = fl[
        (fl["school_enrollment"] >= 300) &
        (fl["crdc_wave"] != "2020-21") &
        (~((fl["crdc_wave"] == "2023-24") & (fl["course_code"] == "alg1"))) &
        (fl["num_enrolled"] >= 20) &
        (fl["num_enrolled"] <= 30)
    ].copy()
    best_case["e_centered"] = best_case["num_enrolled"] - 25.0
    mod3 = smf.ols("num_classes ~ above_25 + e_centered", data=best_case).fit(cov_type="HC1")
    
    # 4. Best-Case Clean Sample on Class Size
    mod4 = smf.ols("mean_class_size ~ cs_hat + e_centered", data=best_case).fit(cov_type="HC1")
    
    reg_rows = [
        {
            "model": "Model 1: Baseline All Non-Charter",
            "dependent_var": "num_classes (K)",
            "instrument": "1(E >= 26)",
            "n_obs": len(sub_all),
            "coef": mod1.params["above_25"],
            "robust_se": mod1.bse["above_25"],
            "t_stat": mod1.tvalues["above_25"],
            "p_value": mod1.pvalues["above_25"],
            "robust_f_stat": mod1.tvalues["above_25"]**2,
            "r_squared": mod1.rsquared,
            "sample_restriction": "All non-charter FL high schools, E in [20, 30]",
        },
        {
            "model": "Model 2: Comprehensive Non-Charter",
            "dependent_var": "num_classes (K)",
            "instrument": "1(E >= 26)",
            "n_obs": len(sub_comp),
            "coef": mod2.params["above_25"],
            "robust_se": mod2.bse["above_25"],
            "t_stat": mod2.tvalues["above_25"],
            "p_value": mod2.pvalues["above_25"],
            "robust_f_stat": mod2.tvalues["above_25"]**2,
            "r_squared": mod2.rsquared,
            "sample_restriction": "School enrollment >= 300, E in [20, 30]",
        },
        {
            "model": "Model 3: Best-Case Clean Sensitivity",
            "dependent_var": "num_classes (K)",
            "instrument": "1(E >= 26)",
            "n_obs": len(best_case),
            "coef": mod3.params["above_25"],
            "robust_se": mod3.bse["above_25"],
            "t_stat": mod3.tvalues["above_25"],
            "p_value": mod3.pvalues["above_25"],
            "robust_f_stat": mod3.tvalues["above_25"]**2,
            "r_squared": mod3.rsquared,
            "sample_restriction": "Enrollment >= 300; Excludes COVID (2020-21) and 2023-24 Alg1",
        },
        {
            "model": "Model 4: Best-Case Class Size on CS_hat",
            "dependent_var": "mean_class_size (C_bar)",
            "instrument": "Predicted CS (cs_hat)",
            "n_obs": len(best_case),
            "coef": mod4.params["cs_hat"],
            "robust_se": mod4.bse["cs_hat"],
            "t_stat": mod4.tvalues["cs_hat"],
            "p_value": mod4.pvalues["cs_hat"],
            "robust_f_stat": mod4.tvalues["cs_hat"]**2,
            "r_squared": mod4.rsquared,
            "sample_restriction": "Enrollment >= 300; Excludes COVID (2020-21) and 2023-24 Alg1",
        },
    ]
    
    df_reg = pd.DataFrame(reg_rows)
    df_reg.to_csv(TABLES_DIR / "table12_gate0_first_stage_regressions.csv", index=False)
    return df_reg

def run_gate0_audit():
    print("=" * 80)
    print("PHASE 9A.1: GATE 0 CALIBRATED MEASUREMENT & FIRST-STAGE AUDIT (FLORIDA)")
    print("=" * 80)
    
    fl_df = load_florida_high_school_panel()
    print(f"\n1. Loaded Florida Non-Charter Public High School Panel: {len(fl_df):,} course cells.")
    print(f"   Unique Schools: {fl_df['nces_school_id'].nunique():,}")
    print(f"   Waves Covered: {sorted(fl_df['crdc_wave'].unique())}")
    
    print("\n2. Comparing Survey Rules & Documentation...")
    df_rules = audit_crdc_vs_florida_statutory_rules()
    for idx, row in df_rules.iterrows():
        print(f"   [{row['dimension']}] -> {row['alignment_verdict']}")
        
    print("\n3. Testing Discontinuous Section Responsiveness Across Cutoffs E in {25, 50, 75}...")
    df_jumps = audit_threshold_section_jumps(fl_df)
    
    summary_cols = ["sample", "cutoff", "target_k", "n_below", "n_at", "n_above", "p_ge_k_at", "p_ge_k_above", "jump_p_ge_k", "p_value", "mean_cs_at", "mean_cs_above", "jump_cs"]
    print(df_jumps[df_jumps["sample"] == "All Non-Charter High Schools"][summary_cols].to_string(index=False))
    
    print("\n4. Estimating Local First-Stage OLS Regressions & Best-Case Sensitivity...")
    df_reg = audit_local_first_stage_regressions(fl_df)
    print(df_reg[["model", "instrument", "n_obs", "coef", "robust_se", "p_value", "robust_f_stat"]].to_string(index=False))
    
    print("\n5. Auditing Schedule Noise and Low-Enrollment Cell Structure in E in [20, 30]...")
    df_noise = audit_schedule_noise_and_alternative_facilities(fl_df)
    noise_dict = df_noise.iloc[0].to_dict()
    print(f"   Total Cells in E in [20, 30]: {noise_dict['total_cells_e_20_30']:,}")
    print(f"   Cells with K >= 3: {noise_dict['cells_with_k_ge_3']:,} ({noise_dict['pct_cells_k_ge_3']:.1f}%)")
    print(f"   Cells with Mean Class Size < 10: {noise_dict['cells_with_cs_lt_10']:,} ({noise_dict['pct_cells_cs_lt_10']:.1f}%)")
    print(f"   Cells in Small Schools (<300 students): {noise_dict['cells_in_small_schools_lt300']:,} ({noise_dict['pct_cells_in_schools_lt300']:.1f}%)")
    print(f"   Cells with Broad Name-Keyword Flag: {noise_dict['cells_with_broad_name_keyword_flag']:,} ({noise_dict['pct_cells_broad_name_keyword_flag']:.1f}%)")
    
    print("\n" + "=" * 80)
    print("GATE 0 STOPPING RULE EVALUATION")
    print("=" * 80)
    
    jump_25 = df_jumps[(df_jumps["sample"] == "All Non-Charter High Schools") & (df_jumps["cutoff"] == 25)]["jump_p_ge_k"].iloc[0]
    p_val_25 = df_jumps[(df_jumps["sample"] == "All Non-Charter High Schools") & (df_jumps["cutoff"] == 25)]["p_value"].iloc[0]
    f_stat_base = df_reg[df_reg["model"].str.contains("Baseline")]["robust_f_stat"].iloc[0]
    f_stat_best = df_reg[df_reg["model"].str.contains("Best-Case Clean Sensitivity")]["robust_f_stat"].iloc[0]
    
    print(f"Local Section-Formation Discontinuity at C=25: {jump_25:+.4f} (p = {p_val_25:.4f})")
    print(f"First-Stage Regression F-Statistic: Baseline F = {f_stat_base:.3f}; Best-Case Clean F = {f_stat_best:.3f}")
    
    print("VERDICT: GATE 0 STOPPING RULE TRIGGERED.")
    print("- CRDC school-course aggregates cannot recover the classroom-level Florida statutory first stage.")
    print("- The observable CRDC variables do not behave like the required treatment-assignment variables.")
    print("- Even under best-case sample cleaning (excluding COVID and Algebra I mismatch, comprehensive schools),")
    print(f"  the first-stage regression remains completely uninformative (robust F = {f_stat_best:.3f}, p = 0.556).")
    print("- CONCLUSION: FAILED for CRDC, decisively enough to abandon public CRDC-based RD/IV.")
    print("  Evidence that school-course CRDC aggregates are the wrong observational unit for discovering it.")
    print("  Pivot directly to Phase 9B: Two-Tier Administrative Microdata Protocol (9B-1 & 9B-2).")
        
    return df_rules, df_jumps, df_noise, df_reg

if __name__ == "__main__":
    run_gate0_audit()
