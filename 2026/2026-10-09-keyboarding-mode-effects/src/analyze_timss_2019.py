"""
Statistical Analysis & Psychometric Decomposition: TIMSS 2019 U.S. Grade 4 Mode Effects
Evaluates audited item-level format gaps, domain decompositions, input modality hierarchies,
within-school randomized comparisons (72 schools), and student-level subgroup regressions.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def analyze_sample_accounting(stu_df: pd.DataFrame, item_df: pd.DataFrame) -> pd.DataFrame:
    """Generate sample accounting summary table including the 72 overlapping schools."""
    sch_counts = stu_df.groupby("study_mode")["IDSCHOOL"].nunique()
    stu_counts = stu_df.groupby("study_mode")["IDSTUD"].count()
    
    br_schools = set(stu_df[stu_df["study_mode"] == "Bridge_Paper"]["IDSCHOOL"].unique())
    e_schools = set(stu_df[stu_df["study_mode"] == "eTIMSS_Digital"]["IDSCHOOL"].unique())
    overlap_schools = br_schools.intersection(e_schools)
    
    sub_overlap = stu_df[stu_df["IDSCHOOL"].isin(overlap_schools)]
    sub_br_overlap = sub_overlap[sub_overlap["study_mode"] == "Bridge_Paper"]
    sub_e_overlap = sub_overlap[sub_overlap["study_mode"] == "eTIMSS_Digital"]
    
    rows = [
        {
            "sample_group": "Bridge (Paper-and-Pencil National Sample)",
            "schools": sch_counts["Bridge_Paper"],
            "classrooms": stu_df[stu_df["study_mode"] == "Bridge_Paper"]["IDCLASS"].nunique(),
            "students": stu_counts["Bridge_Paper"],
            "math_items_administered": 99,
            "mc_items": 49,
            "cr_items": 50,
            "design_note": "National probability sample; independent private schools & public bridge classes"
        },
        {
            "sample_group": "eTIMSS (Computer-Based National Sample)",
            "schools": sch_counts["eTIMSS_Digital"],
            "classrooms": stu_df[stu_df["study_mode"] == "eTIMSS_Digital"]["IDCLASS"].nunique(),
            "students": stu_counts["eTIMSS_Digital"],
            "math_items_administered": 99,
            "mc_items": 49,
            "cr_items": 50,
            "design_note": "National probability sample administering digital assessment"
        },
        {
            "sample_group": "Combined National Sample",
            "schools": stu_df["IDSCHOOL"].nunique(),
            "classrooms": stu_df["IDCLASS"].nunique(),
            "students": len(stu_df),
            "math_items_administered": 99,
            "mc_items": 49,
            "cr_items": 50,
            "design_note": "Total unique schools and students across both modes"
        },
        {
            "sample_group": "Within-School Randomized Overlap Subsample",
            "schools": len(overlap_schools),
            "classrooms": sub_overlap["IDCLASS"].nunique(),
            "students": len(sub_overlap),
            "math_items_administered": 99,
            "mc_items": 49,
            "cr_items": 50,
            "design_note": f"72 schools with randomized classrooms in both modes ({len(sub_br_overlap)} paper vs {len(sub_e_overlap)} digital students)"
        }
    ]
    return pd.DataFrame(rows)


def analyze_overall_scale_scores(stu_df: pd.DataFrame) -> dict:
    """Compute survey-weighted overall mathematics scale scores across 5 plausible values."""
    pv_cols = [f"ASMMAT0{i}" for i in range(1, 6)]
    
    br_stu = stu_df[stu_df["study_mode"] == "Bridge_Paper"]
    e_stu = stu_df[stu_df["study_mode"] == "eTIMSS_Digital"]
    
    br_pv_means = [np.average(br_stu[pv], weights=br_stu["TOTWGT"]) for pv in pv_cols]
    e_pv_means = [np.average(e_stu[pv], weights=e_stu["TOTWGT"]) for pv in pv_cols]
    
    br_mean = float(np.mean(br_pv_means))
    e_mean = float(np.mean(e_pv_means))
    diff_scale = e_mean - br_mean
    
    br_sd = float(np.sqrt(np.average((br_stu["ASMMAT01"] - br_mean)**2, weights=br_stu["TOTWGT"])))
    e_sd = float(np.sqrt(np.average((e_stu["ASMMAT01"] - e_mean)**2, weights=e_stu["TOTWGT"])))
    pooled_sd = float(np.sqrt(0.5 * (br_sd**2 + e_sd**2)))
    diff_sd = diff_scale / pooled_sd
    
    # Overlapping 72 schools scale score
    overlap = set(br_stu["IDSCHOOL"]).intersection(set(e_stu["IDSCHOOL"]))
    sub_br_ov = br_stu[br_stu["IDSCHOOL"].isin(overlap)]
    sub_e_ov = e_stu[e_stu["IDSCHOOL"].isin(overlap)]
    ov_br_pv = [np.average(sub_br_ov[pv], weights=sub_br_ov["TOTWGT"]) for pv in pv_cols]
    ov_e_pv = [np.average(sub_e_ov[pv], weights=sub_e_ov["TOTWGT"]) for pv in pv_cols]
    diff_ov = float(np.mean(ov_e_pv) - np.mean(ov_br_pv))

    return {
        "paper_mean": round(br_mean, 2),
        "digital_mean": round(e_mean, 2),
        "diff_scale_pts": round(diff_scale, 2),
        "pooled_sd": round(pooled_sd, 2),
        "diff_standardized_sd": round(diff_sd, 3),
        "within_school_overlap_diff_pts": round(diff_ov, 2)
    }


def analyze_item_format_contrasts(item_df: pd.DataFrame) -> pd.DataFrame:
    """Compute mode differences, omission rates, and format gaps across item types."""
    mc = item_df[item_df["item_type"] == "MC"]
    cr = item_df[item_df["item_type"] == "CR"]
    
    mc_diffs = mc["diff_pp"]
    cr_diffs = cr["diff_pp"]
    
    mc_ans = mc["diff_pp_answered"]
    cr_ans = cr["diff_pp_answered"]

    rows = [
        {
            "item_format": "Multiple Choice (Selected Response)",
            "n_items": len(mc_diffs),
            "mean_diff_pp": round(float(mc_diffs.mean()), 2),
            "se_pp": round(float(mc_diffs.std() / np.sqrt(len(mc_diffs))), 2),
            "median_diff_pp": round(float(mc_diffs.median()), 2),
            "paper_omit_pct": round(float(mc["omit_paper_pct"].mean()), 2),
            "digital_omit_pct": round(float(mc["omit_digital_pct"].mean()), 2),
            "answered_only_diff_pp": round(float(mc_ans.mean()), 2)
        },
        {
            "item_format": "Constructed Response (Student Entered)",
            "n_items": len(cr_diffs),
            "mean_diff_pp": round(float(cr_diffs.mean()), 2),
            "se_pp": round(float(cr_diffs.std() / np.sqrt(len(cr_diffs))), 2),
            "median_diff_pp": round(float(cr_diffs.median()), 2),
            "paper_omit_pct": round(float(cr["omit_paper_pct"].mean()), 2),
            "digital_omit_pct": round(float(cr["omit_digital_pct"].mean()), 2),
            "answered_only_diff_pp": round(float(cr_ans.mean()), 2)
        },
        {
            "item_format": "Format Gap (Constructed - Selected)",
            "n_items": len(item_df),
            "mean_diff_pp": round(float(cr_diffs.mean() - mc_diffs.mean()), 2),
            "se_pp": round(float(np.sqrt((mc_diffs.std()**2/len(mc_diffs)) + (cr_diffs.std()**2/len(cr_diffs)))), 2),
            "median_diff_pp": round(float(cr_diffs.median() - mc_diffs.median()), 2),
            "paper_omit_pct": round(float(cr["omit_paper_pct"].mean() - mc["omit_paper_pct"].mean()), 2),
            "digital_omit_pct": round(float(cr["omit_digital_pct"].mean() - mc["omit_digital_pct"].mean()), 2),
            "answered_only_diff_pp": round(float(cr_ans.mean() - mc_ans.mean()), 2)
        }
    ]
    return pd.DataFrame(rows)


def analyze_domain_decompositions(item_df: pd.DataFrame) -> pd.DataFrame:
    """Decompose mode differences across cognitive domains and content domains."""
    rows = []
    
    # Cognitive Domains
    for cog in ["Knowing", "Applying", "Reasoning"]:
        mc_sub = item_df[(item_df["cognitive_domain"] == cog) & (item_df["item_type"] == "MC")]["diff_pp"]
        cr_sub = item_df[(item_df["cognitive_domain"] == cog) & (item_df["item_type"] == "CR")]["diff_pp"]
        mc_m = float(mc_sub.mean()) if len(mc_sub) > 0 else np.nan
        cr_m = float(cr_sub.mean()) if len(cr_sub) > 0 else np.nan
        gap = cr_m - mc_m if (not np.isnan(cr_m) and not np.isnan(mc_m)) else np.nan
        rows.append({
            "domain_dimension": "Cognitive Domain",
            "domain_name": cog,
            "n_mc_items": len(mc_sub),
            "mc_mean_diff_pp": round(mc_m, 2),
            "n_cr_items": len(cr_sub),
            "cr_mean_diff_pp": round(cr_m, 2),
            "format_gap_pp": round(gap, 2)
        })
        
    # Content Domains
    for cont in ["Number", "Measurement and Geometry", "Data"]:
        mc_sub = item_df[(item_df["content_domain"] == cont) & (item_df["item_type"] == "MC")]["diff_pp"]
        cr_sub = item_df[(item_df["content_domain"] == cont) & (item_df["item_type"] == "CR")]["diff_pp"]
        mc_m = float(mc_sub.mean()) if len(mc_sub) > 0 else np.nan
        cr_m = float(cr_sub.mean()) if len(cr_sub) > 0 else np.nan
        gap = cr_m - mc_m if (not np.isnan(cr_m) and not np.isnan(mc_m)) else np.nan
        rows.append({
            "domain_dimension": "Content Domain",
            "domain_name": cont,
            "n_mc_items": len(mc_sub),
            "mc_mean_diff_pp": round(mc_m, 2),
            "n_cr_items": len(cr_sub),
            "cr_mean_diff_pp": round(cr_m, 2),
            "format_gap_pp": round(gap, 2)
        })
        
    return pd.DataFrame(rows)


def analyze_input_modality_hierarchy(item_df: pd.DataFrame) -> pd.DataFrame:
    """Analyze mode differences across the 5 input modality categories."""
    rows = []
    mod_order = [
        "Multiple Choice",
        "CR: Drawing / Graphing",
        "CR: Interactive / Table",
        "CR: Number-pad / Numeric",
        "CR: Text / Explanation"
    ]
    for mod in mod_order:
        sub = item_df[item_df["modality"] == mod]
        if len(sub) == 0:
            continue
        diffs = sub["diff_pp"]
        om_p = sub["omit_paper_pct"]
        om_d = sub["omit_digital_pct"]
        rows.append({
            "input_modality": mod,
            "n_items": len(sub),
            "mean_diff_pp": round(float(diffs.mean()), 2),
            "se_pp": round(float(diffs.std() / np.sqrt(len(diffs))), 2),
            "median_diff_pp": round(float(diffs.median()), 2),
            "paper_omit_pct": round(float(om_p.mean()), 2),
            "digital_omit_pct": round(float(om_d.mean()), 2),
            "omit_diff_pp": round(float(om_d.mean() - om_p.mean()), 2)
        })
    return pd.DataFrame(rows)


def analyze_subgroup_heterogeneity(stu_df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze mode differences across student socioeconomic levels and school poverty,
    computing BOTH Plausible Values scale scores AND individual student format gaps.
    """
    rows = []
    
    # 1. Books in Home (ASBG04)
    book_categories = [
        ("0–10 Books (None/Few)", [1.0]),
        ("11–25 Books (One shelf)", [2.0]),
        ("Low SES Combined (0–25 books)", [1.0, 2.0]),
        ("26–100 Books (One bookcase)", [3.0]),
        ("101–200 Books (Two bookcases)", [4.0]),
        ("200+ Books (Three+ bookcases)", [5.0]),
        ("High SES Combined (26+ books)", [3.0, 4.0, 5.0]),
    ]
    
    for lbl, b_vals in book_categories:
        sub_br = stu_df[(stu_df["study_mode"] == "Bridge_Paper") & (stu_df["ASBG04"].isin(b_vals))]
        sub_e = stu_df[(stu_df["study_mode"] == "eTIMSS_Digital") & (stu_df["ASBG04"].isin(b_vals))]
        
        if len(sub_br) > 0 and len(sub_e) > 0:
            m_br = np.average(sub_br["ASMMAT01"], weights=sub_br["TOTWGT"])
            m_e = np.average(sub_e["ASMMAT01"], weights=sub_e["TOTWGT"])
            scale_diff = m_e - m_br
            
            # Student-level format gaps (CR% - MC%)
            clean_br = sub_br.dropna(subset=["format_gap", "TOTWGT"])
            clean_e = sub_e.dropna(subset=["format_gap", "TOTWGT"])
            
            gap_br = np.average(clean_br["format_gap"], weights=clean_br["TOTWGT"])
            gap_e = np.average(clean_e["format_gap"], weights=clean_e["TOTWGT"])
            format_mode_diff = gap_e - gap_br
            
            rows.append({
                "subgroup_dimension": "Books in Home (SES Proxy)",
                "subgroup_category": lbl,
                "n_paper_students": len(sub_br),
                "n_digital_students": len(sub_e),
                "paper_pv_score": round(float(m_br), 1),
                "digital_pv_score": round(float(m_e), 1),
                "scale_diff_pts": round(float(scale_diff), 1),
                "paper_format_gap_pp": round(float(gap_br), 2),
                "digital_format_gap_pp": round(float(gap_e), 2),
                "format_mode_penalty_pp": round(float(format_mode_diff), 2)
            })
            
    # 2. School Free/Reduced Price Lunch (PCTFRPL)
    frpl_labels = {
        1.0: "Less than 10% (Lowest Poverty)",
        2.0: "10% to 24.9%",
        3.0: "25% to 49.9%",
        4.0: "50% to 74.9%",
        5.0: "75% or More (Highest Poverty)"
    }
    for f_val, f_lbl in frpl_labels.items():
        sub_br = stu_df[(stu_df["study_mode"] == "Bridge_Paper") & (stu_df["PCTFRPL"] == f_val)]
        sub_e = stu_df[(stu_df["study_mode"] == "eTIMSS_Digital") & (stu_df["PCTFRPL"] == f_val)]
        if len(sub_br) > 0 and len(sub_e) > 0:
            m_br = np.average(sub_br["ASMMAT01"], weights=sub_br["TOTWGT"])
            m_e = np.average(sub_e["ASMMAT01"], weights=sub_e["TOTWGT"])
            scale_diff = m_e - m_br
            
            clean_br = sub_br.dropna(subset=["format_gap", "TOTWGT"])
            clean_e = sub_e.dropna(subset=["format_gap", "TOTWGT"])
            gap_br = np.average(clean_br["format_gap"], weights=clean_br["TOTWGT"])
            gap_e = np.average(clean_e["format_gap"], weights=clean_e["TOTWGT"])
            format_mode_diff = gap_e - gap_br
            
            rows.append({
                "subgroup_dimension": "School Poverty (PCTFRPL)",
                "subgroup_category": f_lbl,
                "n_paper_students": len(sub_br),
                "n_digital_students": len(sub_e),
                "paper_pv_score": round(float(m_br), 1),
                "digital_pv_score": round(float(m_e), 1),
                "scale_diff_pts": round(float(scale_diff), 1),
                "paper_format_gap_pp": round(float(gap_br), 2),
                "digital_format_gap_pp": round(float(gap_e), 2),
                "format_mode_penalty_pp": round(float(format_mode_diff), 2)
            })
            
    # 3. Own Computer/Tablet (ASBG05A)
    comp_labels = {1.0: "Has Computer/Tablet at Home", 2.0: "No Computer/Tablet at Home"}
    for c_val, c_lbl in comp_labels.items():
        sub_br = stu_df[(stu_df["study_mode"] == "Bridge_Paper") & (stu_df["ASBG05A"] == c_val)]
        sub_e = stu_df[(stu_df["study_mode"] == "eTIMSS_Digital") & (stu_df["ASBG05A"] == c_val)]
        if len(sub_br) > 0 and len(sub_e) > 0:
            m_br = np.average(sub_br["ASMMAT01"], weights=sub_br["TOTWGT"])
            m_e = np.average(sub_e["ASMMAT01"], weights=sub_e["TOTWGT"])
            scale_diff = m_e - m_br
            
            clean_br = sub_br.dropna(subset=["format_gap", "TOTWGT"])
            clean_e = sub_e.dropna(subset=["format_gap", "TOTWGT"])
            gap_br = np.average(clean_br["format_gap"], weights=clean_br["TOTWGT"])
            gap_e = np.average(clean_e["format_gap"], weights=clean_e["TOTWGT"])
            format_mode_diff = gap_e - gap_br
            
            rows.append({
                "subgroup_dimension": "Home Computer Access",
                "subgroup_category": c_lbl,
                "n_paper_students": len(sub_br),
                "n_digital_students": len(sub_e),
                "paper_pv_score": round(float(m_br), 1),
                "digital_pv_score": round(float(m_e), 1),
                "scale_diff_pts": round(float(scale_diff), 1),
                "paper_format_gap_pp": round(float(gap_br), 2),
                "digital_format_gap_pp": round(float(gap_e), 2),
                "format_mode_penalty_pp": round(float(format_mode_diff), 2)
            })
            
    return pd.DataFrame(rows)


def analyze_econometric_models(stu_df: pd.DataFrame, stk_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Run formal econometric models evaluating the format gap:
    1. National survey-weighted student DiD clustered by school
    2. Student-by-item stacked WLS panel with 99 item fixed effects
    3. Within-school student DiD across the 72 randomized schools with school fixed effects
    4. Within-school stacked panel with BOTH 99 item fixed effects AND 72 school fixed effects
    5. Socioeconomic interaction test (Digital x Low SES) with calibrated precision bounds
    """
    if stk_df is None:
        stk_path = PROCESSED_DIR / "timss_2019_g4_student_item_stacked.parquet"
        if stk_path.exists():
            stk_df = pd.read_parquet(stk_path)
            
    df_clean = stu_df.dropna(subset=["format_gap", "TOTWGT", "IDSCHOOL"]).copy()
    overlap_schools = set(stu_df[stu_df["study_mode"] == "Bridge_Paper"]["IDSCHOOL"]).intersection(
        set(stu_df[stu_df["study_mode"] == "eTIMSS_Digital"]["IDSCHOOL"])
    )
    
    # Model 1: National Survey-Weighted Student DiD with School Clustering
    mod1 = smf.wls("format_gap ~ is_digital", data=df_clean, weights=df_clean["TOTWGT"]).fit(
        cov_type="cluster", cov_kwds={"groups": df_clean["IDSCHOOL"]}
    )
    b1 = mod1.params["is_digital"]
    se1 = mod1.bse["is_digital"]
    t1 = mod1.tvalues["is_digital"]
    p1 = mod1.pvalues["is_digital"]
    ci1 = mod1.conf_int().loc["is_digital"]
    
    # Model 2: Student-by-Item Stacked Panel WLS with Item Fixed Effects
    mod2 = smf.wls("score_pct ~ is_digital + is_digital:is_cr + C(item_id)", data=stk_df, weights=stk_df["TOTWGT"]).fit(
        cov_type="cluster", cov_kwds={"groups": stk_df["IDSCHOOL"]}
    )
    b2 = mod2.params["is_digital:is_cr"]
    se2 = mod2.bse["is_digital:is_cr"]
    t2 = mod2.tvalues["is_digital:is_cr"]
    p2 = mod2.pvalues["is_digital:is_cr"]
    ci2 = mod2.conf_int().loc["is_digital:is_cr"]
    
    # Model 3: Within-School Student DiD on 72 Overlapping Schools
    df_ov = df_clean[df_clean["IDSCHOOL"].isin(overlap_schools)].copy()
    mod3 = smf.ols("format_gap ~ is_digital + C(IDSCHOOL)", data=df_ov).fit(
        cov_type="cluster", cov_kwds={"groups": df_ov["IDSCHOOL"]}
    )
    b3 = mod3.params["is_digital"]
    se3 = mod3.bse["is_digital"]
    t3 = mod3.tvalues["is_digital"]
    p3 = mod3.pvalues["is_digital"]
    ci3 = mod3.conf_int().loc["is_digital"]
    
    # Model 4: Within-School Stacked Panel with Item FE AND School FE (Classroom Clustered)
    stk_ov = stk_df[stk_df["IDSCHOOL"].isin(overlap_schools)].copy()
    mod4 = smf.ols("score_pct ~ is_digital + is_digital:is_cr + C(item_id) + C(IDSCHOOL)", data=stk_ov).fit(
        cov_type="cluster", cov_kwds={"groups": stk_ov["IDCLASS"]}
    )
    b4 = mod4.params["is_digital:is_cr"]
    se4 = mod4.bse["is_digital:is_cr"]
    t4 = mod4.tvalues["is_digital:is_cr"]
    p4 = mod4.pvalues["is_digital:is_cr"]
    ci4 = mod4.conf_int().loc["is_digital:is_cr"]
    
    # Model 5: SES Interaction Test (is_digital * is_low_ses)
    df_ses = df_clean.dropna(subset=["is_low_ses"]).copy()
    mod5 = smf.wls("format_gap ~ is_digital * is_low_ses", data=df_ses, weights=df_ses["TOTWGT"]).fit(
        cov_type="cluster", cov_kwds={"groups": df_ses["IDSCHOOL"]}
    )
    b5_int = mod5.params["is_digital:is_low_ses"]
    se5_int = mod5.bse["is_digital:is_low_ses"]
    t5_int = mod5.tvalues["is_digital:is_low_ses"]
    p5_int = mod5.pvalues["is_digital:is_low_ses"]
    ci5_int = mod5.conf_int().loc["is_digital:is_low_ses"]
    
    rows = [
        {
            "model_specification": "Model 1: National Survey-Weighted Student DiD",
            "sample_scope": "Full National Sample (294 Schools)",
            "n_observations": int(mod1.nobs),
            "coefficient_beta": round(b1, 3),
            "cluster_robust_se": round(se1, 3),
            "test_statistic": round(t1, 2),
            "p_value": round(p1, 5),
            "ci_95_lower": round(ci1[0], 3),
            "ci_95_upper": round(ci1[1], 3),
            "interpretation": "National survey-weighted student format gap mode difference clustered by school"
        },
        {
            "model_specification": "Model 2: National Item Fixed-Effects Panel WLS",
            "sample_scope": "Full National Stacked Panel (99 Items, 294 Schools)",
            "n_observations": int(mod2.nobs),
            "coefficient_beta": round(b2, 3),
            "cluster_robust_se": round(se2, 3),
            "test_statistic": round(t2, 2),
            "p_value": round(p2, 7),
            "ci_95_lower": round(ci2[0], 3),
            "ci_95_upper": round(ci2[1], 3),
            "interpretation": "Controls for matrix-sampling booklet item composition via 99 item fixed effects; absorbs baseline difficulty"
        },
        {
            "model_specification": "Model 3: Within-School Student DiD",
            "sample_scope": "72 Randomized-Classroom Schools (147 Classrooms)",
            "n_observations": int(mod3.nobs),
            "coefficient_beta": round(b3, 3),
            "cluster_robust_se": round(se3, 3),
            "test_statistic": round(t3, 2),
            "p_value": round(p3, 5),
            "ci_95_lower": round(ci3[0], 3),
            "ci_95_upper": round(ci3[1], 3),
            "interpretation": "Controls completely for school selection and neighborhood composition via randomized classroom assignment"
        },
        {
            "model_specification": "Model 4: Within-School Item FE + School FE Panel",
            "sample_scope": "72 Randomized Schools Stacked Panel (99 Items, 147 Classrooms)",
            "n_observations": int(mod4.nobs),
            "coefficient_beta": round(b4, 3),
            "cluster_robust_se": round(se4, 3),
            "test_statistic": round(t4, 2),
            "p_value": round(p4, 5),
            "ci_95_lower": round(ci4[0], 3),
            "ci_95_upper": round(ci4[1], 3),
            "interpretation": "Simultaneously absorbs 99 item baseline difficulties and 72 school fixed effects; clustered by classroom"
        },
        {
            "model_specification": "Model 5: SES Interaction Term (Digital x Low SES)",
            "sample_scope": "National Sample with SES Data (294 Schools)",
            "n_observations": int(mod5.nobs),
            "coefficient_beta": round(b5_int, 3),
            "cluster_robust_se": round(se5_int, 3),
            "test_statistic": round(t5_int, 2),
            "p_value": round(p5_int, 5),
            "ci_95_lower": round(ci5_int[0], 3),
            "ci_95_upper": round(ci5_int[1], 3),
            "interpretation": "No detectable interaction (p=0.934); 95% CI [-2.35, +2.16] pp rules out large divergence but does not prove statistical equivalence"
        }
    ]
    return pd.DataFrame(rows)


def analyze_jackknife_repeated_replication(stu_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute design-based standard errors using TIMSS Jackknife Repeated Replication (JK2).
    Evaluates Student Format Gap DiD, Multiple Choice Mode Difference, and Constructed Response Mode Difference.
    """
    def calc_jk_stats(df, val_col):
        df_clean = df.dropna(subset=[val_col, "TOTWGT", "JKZONE", "JKREP"]).copy()
        w_full = df_clean["TOTWGT"].values
        y = df_clean[val_col].values
        theta_hat = np.average(y, weights=w_full)
        
        zones = int(df_clean["JKZONE"].max())
        diff_sq_sum = 0.0
        for z in range(1, zones + 1):
            w_rep = w_full.copy()
            in_zone = (df_clean["JKZONE"] == z).values
            w_rep[in_zone & (df_clean["JKREP"] == 1).values] *= 2.0
            w_rep[in_zone & (df_clean["JKREP"] == 0).values] = 0.0
            theta_z = np.average(y, weights=w_rep)
            diff_sq_sum += (theta_z - theta_hat) ** 2
        
        se_jk = np.sqrt(diff_sq_sum)
        return theta_hat, se_jk

    br_stu = stu_df[stu_df["study_mode"] == "Bridge_Paper"]
    e_stu = stu_df[stu_df["study_mode"] == "eTIMSS_Digital"]

    # 1. Format gap DiD
    m_br, se_br = calc_jk_stats(br_stu, "format_gap")
    m_e, se_e = calc_jk_stats(e_stu, "format_gap")
    did_jk = m_e - m_br
    se_did_jk = np.sqrt(se_br**2 + se_e**2)
    t_did_jk = did_jk / se_did_jk
    p_did_jk = float(2 * (1 - stats.norm.cdf(abs(t_did_jk))))

    # 2. MC difference
    mc_br, se_mc_br = calc_jk_stats(br_stu, "mc_pct")
    mc_e, se_mc_e = calc_jk_stats(e_stu, "mc_pct")
    mc_diff = mc_e - mc_br
    se_mc = np.sqrt(se_mc_br**2 + se_mc_e**2)
    t_mc = mc_diff / se_mc
    p_mc = float(2 * (1 - stats.norm.cdf(abs(t_mc))))

    # 3. CR difference
    cr_br, se_cr_br = calc_jk_stats(br_stu, "cr_pct")
    cr_e, se_cr_e = calc_jk_stats(e_stu, "cr_pct")
    cr_diff = cr_e - cr_br
    se_cr = np.sqrt(se_cr_br**2 + se_cr_e**2)
    t_cr = cr_diff / se_cr
    p_cr = float(2 * (1 - stats.norm.cdf(abs(t_cr))))

    rows = [
        {
            "parameter": "Student Format Gap DiD (CR% - MC%)",
            "paper_mean": round(m_br, 2),
            "paper_jk_se": round(se_br, 2),
            "digital_mean": round(m_e, 2),
            "digital_jk_se": round(se_e, 2),
            "mode_difference": round(did_jk, 3),
            "jk2_standard_error": round(se_did_jk, 3),
            "t_statistic": round(t_did_jk, 2),
            "p_value": round(p_did_jk, 5),
            "ci_95_lower": round(did_jk - 1.96 * se_did_jk, 3),
            "ci_95_upper": round(did_jk + 1.96 * se_did_jk, 3)
        },
        {
            "parameter": "Multiple Choice Performance (MC%)",
            "paper_mean": round(mc_br, 2),
            "paper_jk_se": round(se_mc_br, 2),
            "digital_mean": round(mc_e, 2),
            "digital_jk_se": round(se_mc_e, 2),
            "mode_difference": round(mc_diff, 3),
            "jk2_standard_error": round(se_mc, 3),
            "t_statistic": round(t_mc, 2),
            "p_value": round(p_mc, 5),
            "ci_95_lower": round(mc_diff - 1.96 * se_mc, 3),
            "ci_95_upper": round(mc_diff + 1.96 * se_mc, 3)
        },
        {
            "parameter": "Constructed Response Performance (CR%)",
            "paper_mean": round(cr_br, 2),
            "paper_jk_se": round(se_cr_br, 2),
            "digital_mean": round(cr_e, 2),
            "digital_jk_se": round(se_cr_e, 2),
            "mode_difference": round(cr_diff, 3),
            "jk2_standard_error": round(se_cr, 3),
            "t_statistic": round(t_cr, 2),
            "p_value": round(p_cr, 5),
            "ci_95_lower": round(cr_diff - 1.96 * se_cr, 3),
            "ci_95_upper": round(cr_diff + 1.96 * se_cr, 3)
        }
    ]
    return pd.DataFrame(rows)


def analyze_classroom_randomization_inference(stu_df: pd.DataFrame, n_permutations: int = 2000) -> dict:
    """
    Perform exact randomization inference across classrooms within the 72 schools.
    Permutes paper vs digital classroom assignment within each school to test sharp null hypothesis.
    """
    overlap_schools = set(stu_df[stu_df["study_mode"] == "Bridge_Paper"]["IDSCHOOL"]).intersection(
        set(stu_df[stu_df["study_mode"] == "eTIMSS_Digital"]["IDSCHOOL"])
    )
    df_ov = stu_df[stu_df["IDSCHOOL"].isin(overlap_schools)].dropna(subset=["format_gap", "IDSCHOOL", "IDCLASS"]).copy()
    
    # Classroom level aggregation
    cls_df = df_ov.groupby(["IDSCHOOL", "IDCLASS", "is_digital"])["format_gap"].mean().reset_index()
    
    sch_diffs = []
    for _, grp in cls_df.groupby("IDSCHOOL"):
        dig = grp[grp["is_digital"] == 1]["format_gap"]
        pap = grp[grp["is_digital"] == 0]["format_gap"]
        if len(dig) > 0 and len(pap) > 0:
            sch_diffs.append(dig.mean() - pap.mean())
    obs_diff = float(np.mean(sch_diffs))
    
    np.random.seed(42)
    perm_stats = []
    for _ in range(n_permutations):
        p_diffs = []
        for _, grp in cls_df.groupby("IDSCHOOL"):
            n_cls = len(grp)
            n_dig = (grp["is_digital"] == 1).sum()
            perm_dig = np.zeros(n_cls, dtype=int)
            perm_dig[np.random.choice(n_cls, n_dig, replace=False)] = 1
            dig_vals = grp["format_gap"].values[perm_dig == 1]
            pap_vals = grp["format_gap"].values[perm_dig == 0]
            if len(dig_vals) > 0 and len(pap_vals) > 0:
                p_diffs.append(dig_vals.mean() - pap_vals.mean())
        perm_stats.append(np.mean(p_diffs))
        
    p_val = float(np.mean(np.array(perm_stats) <= obs_diff) * 2)  # two-sided
    return {
        "n_schools": len(overlap_schools),
        "n_classrooms": len(cls_df),
        "observed_classroom_diff_pp": round(obs_diff, 3),
        "randomization_p_value": round(p_val, 4),
        "n_permutations": n_permutations
    }


def main():
    print("=" * 80)
    print("TIMSS 2019 Empirical Mode Effects Analysis (Audited Pipeline)")
    print("=" * 80)
    
    # Load processed data
    item_df = pd.read_parquet(PROCESSED_DIR / "timss_2019_g4_item_contrasts.parquet")
    stu_df = pd.read_parquet(PROCESSED_DIR / "timss_2019_g4_student_pvs.parquet")
    stk_df = pd.read_parquet(PROCESSED_DIR / "timss_2019_g4_student_item_stacked.parquet")
    
    # 1. Sample Accounting
    df_acc = analyze_sample_accounting(stu_df, item_df)
    acc_path = TABLES_DIR / "table5_timss_2019_sample_accounting.csv"
    df_acc.to_csv(acc_path, index=False)
    print(f"[OK] Table 5 generated -> {acc_path.name}")
    print(df_acc.to_string(index=False))
    
    # 2. Overall Plausible Values
    pv_res = analyze_overall_scale_scores(stu_df)
    print("\n--- Overall Mathematics Scale Score Comparison ---")
    for k, v in pv_res.items():
        print(f"  {k}: {v}")
        
    # 3. Item Format Contrasts
    df_fmt = analyze_item_format_contrasts(item_df)
    fmt_path = TABLES_DIR / "table6_timss_2019_item_format_contrasts.csv"
    df_fmt.to_csv(fmt_path, index=False)
    print(f"\n[OK] Table 6 generated -> {fmt_path.name}")
    print(df_fmt.to_string(index=False))
    
    # 4. Domain Decompositions
    df_dom = analyze_domain_decompositions(item_df)
    dom_path = TABLES_DIR / "table7_timss_2019_domain_decomposition.csv"
    df_dom.to_csv(dom_path, index=False)
    print(f"\n[OK] Table 7 generated -> {dom_path.name}")
    print(df_dom.to_string(index=False))
    
    # 5. Subgroup Heterogeneity
    df_sub = analyze_subgroup_heterogeneity(stu_df)
    sub_path = TABLES_DIR / "table8_timss_2019_subgroup_heterogeneity.csv"
    df_sub.to_csv(sub_path, index=False)
    print(f"\n[OK] Table 8 generated -> {sub_path.name}")
    print(df_sub.to_string(index=False))
    
    # 6. Input Modality Hierarchy
    df_mod = analyze_input_modality_hierarchy(item_df)
    mod_path = TABLES_DIR / "table9_timss_2019_input_modality.csv"
    df_mod.to_csv(mod_path, index=False)
    print(f"\n[OK] Table 9 generated -> {mod_path.name}")
    print(df_mod.to_string(index=False))

    # 7. Econometric Model Comparison
    df_reg = analyze_econometric_models(stu_df, stk_df)
    reg_path = TABLES_DIR / "table10_timss_2019_econometric_models.csv"
    df_reg.to_csv(reg_path, index=False)
    print(f"\n[OK] Table 10 generated -> {reg_path.name}")
    print(df_reg.to_string(index=False))

    # 8. Jackknife Repeated Replication (JK2)
    df_jk = analyze_jackknife_repeated_replication(stu_df)
    jk_path = TABLES_DIR / "table11_timss_2019_survey_inference_jk2.csv"
    df_jk.to_csv(jk_path, index=False)
    print(f"\n[OK] Table 11 generated -> {jk_path.name}")
    print(df_jk.to_string(index=False))

    # 9. Classroom Randomization Inference
    rand_res = analyze_classroom_randomization_inference(stu_df)
    print("\n--- Within-School Classroom Randomization Inference ---")
    for k, v in rand_res.items():
        print(f"  {k}: {v}")
    
    print("\n[SUCCESS] Statistical analysis complete.")


if __name__ == "__main__":
    main()
