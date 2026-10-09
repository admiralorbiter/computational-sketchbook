"""
Statistical Analysis & Psychometric Decomposition: TIMSS 2019 U.S. Grade 4 Mode Effects
Evaluates item-level format gaps, domain decompositions, and subgroup interactions.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def analyze_sample_accounting(stu_df: pd.DataFrame, item_df: pd.DataFrame) -> pd.DataFrame:
    """Generate sample accounting summary table."""
    sch_counts = stu_df.groupby("study_mode")["IDSCHOOL"].nunique()
    stu_counts = stu_df.groupby("study_mode")["IDSTUD"].count()
    
    rows = [
        {"sample_group": "Bridge (Paper-and-Pencil)", "schools": sch_counts["Bridge_Paper"], "students": stu_counts["Bridge_Paper"], "math_items_administered": 99, "mc_items": 49, "cr_items": 50},
        {"sample_group": "eTIMSS (Computer-Based)", "schools": sch_counts["eTIMSS_Digital"], "students": stu_counts["eTIMSS_Digital"], "math_items_administered": 99, "mc_items": 49, "cr_items": 50},
        {"sample_group": "Combined Total / Anchor Overlap", "schools": stu_df["IDSCHOOL"].nunique(), "students": len(stu_df), "math_items_administered": 99, "mc_items": 49, "cr_items": 50},
    ]
    df_acc = pd.DataFrame(rows)
    return df_acc


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
    
    # Standard deviation pooled
    br_sd = float(np.sqrt(np.average((br_stu["ASMMAT01"] - br_mean)**2, weights=br_stu["TOTWGT"])))
    e_sd = float(np.sqrt(np.average((e_stu["ASMMAT01"] - e_mean)**2, weights=e_stu["TOTWGT"])))
    pooled_sd = float(np.sqrt(0.5 * (br_sd**2 + e_sd**2)))
    diff_sd = diff_scale / pooled_sd
    
    return {
        "paper_mean": round(br_mean, 2),
        "digital_mean": round(e_mean, 2),
        "diff_scale_pts": round(diff_scale, 2),
        "pooled_sd": round(pooled_sd, 2),
        "diff_standardized_sd": round(diff_sd, 3)
    }


def analyze_item_format_contrasts(item_df: pd.DataFrame) -> pd.DataFrame:
    """Compute mode differences and format gaps across item types."""
    mc_diffs = item_df[item_df["item_type"] == "MC"]["diff_pp"]
    cr_diffs = item_df[item_df["item_type"] == "CR"]["diff_pp"]
    
    t_stat, p_val = stats.ttest_ind(cr_diffs, mc_diffs, equal_var=False)
    
    rows = [
        {
            "item_format": "Multiple Choice (Selected Response)",
            "n_items": len(mc_diffs),
            "mean_diff_pp": round(float(mc_diffs.mean()), 2),
            "se_pp": round(float(mc_diffs.std() / np.sqrt(len(mc_diffs))), 2),
            "median_diff_pp": round(float(mc_diffs.median()), 2),
            "min_diff_pp": round(float(mc_diffs.min()), 2),
            "max_diff_pp": round(float(mc_diffs.max()), 2)
        },
        {
            "item_format": "Constructed Response (Student Entered)",
            "n_items": len(cr_diffs),
            "mean_diff_pp": round(float(cr_diffs.mean()), 2),
            "se_pp": round(float(cr_diffs.std() / np.sqrt(len(cr_diffs))), 2),
            "median_diff_pp": round(float(cr_diffs.median()), 2),
            "min_diff_pp": round(float(cr_diffs.min()), 2),
            "max_diff_pp": round(float(cr_diffs.max()), 2)
        },
        {
            "item_format": "Format Gap (Constructed - Selected)",
            "n_items": len(item_df),
            "mean_diff_pp": round(float(cr_diffs.mean() - mc_diffs.mean()), 2),
            "se_pp": round(float(np.sqrt((mc_diffs.std()**2/len(mc_diffs)) + (cr_diffs.std()**2/len(cr_diffs)))), 2),
            "median_diff_pp": round(float(cr_diffs.median() - mc_diffs.median()), 2),
            "min_diff_pp": np.nan,
            "max_diff_pp": np.nan
        }
    ]
    return pd.DataFrame(rows)


def analyze_domain_decompositions(item_df: pd.DataFrame) -> pd.DataFrame:
    """Decompose mode differences across content domains and cognitive domains."""
    rows = []
    
    # Cognitive Domains
    cog_groups = item_df.groupby(["cognitive_domain", "item_type"])["diff_pp"]
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


def analyze_subgroup_heterogeneity(stu_df: pd.DataFrame) -> pd.DataFrame:
    """Analyze mode differences across student socioeconomic levels and school poverty."""
    rows = []
    
    # 1. Books in Home (ASBG04)
    book_labels = {
        1.0: "0–10 Books (None/Few)",
        2.0: "11–25 Books (One shelf)",
        3.0: "26–100 Books (One bookcase)",
        4.0: "101–200 Books (Two bookcases)",
        5.0: "200+ Books (Three+ bookcases)"
    }
    for b_val, b_lbl in book_labels.items():
        sub_br = stu_df[(stu_df["study_mode"] == "Bridge_Paper") & (stu_df["ASBG04"] == b_val)]
        sub_e = stu_df[(stu_df["study_mode"] == "eTIMSS_Digital") & (stu_df["ASBG04"] == b_val)]
        if len(sub_br) > 0 and len(sub_e) > 0:
            m_br = np.average(sub_br["ASMMAT01"], weights=sub_br["TOTWGT"])
            m_e = np.average(sub_e["ASMMAT01"], weights=sub_e["TOTWGT"])
            diff = m_e - m_br
            rows.append({
                "subgroup_dimension": "Books in Home (SES Proxy)",
                "subgroup_category": b_lbl,
                "n_paper_students": len(sub_br),
                "n_digital_students": len(sub_e),
                "paper_pv_score": round(float(m_br), 1),
                "digital_pv_score": round(float(m_e), 1),
                "scale_diff_pts": round(float(diff), 1)
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
            diff = m_e - m_br
            rows.append({
                "subgroup_dimension": "School Poverty (PCTFRPL)",
                "subgroup_category": f_lbl,
                "n_paper_students": len(sub_br),
                "n_digital_students": len(sub_e),
                "paper_pv_score": round(float(m_br), 1),
                "digital_pv_score": round(float(m_e), 1),
                "scale_diff_pts": round(float(diff), 1)
            })
            
    # 3. Own Computer/Tablet (ASBG05A)
    comp_labels = {1.0: "Has Computer/Tablet at Home", 2.0: "No Computer/Tablet at Home"}
    for c_val, c_lbl in comp_labels.items():
        sub_br = stu_df[(stu_df["study_mode"] == "Bridge_Paper") & (stu_df["ASBG05A"] == c_val)]
        sub_e = stu_df[(stu_df["study_mode"] == "eTIMSS_Digital") & (stu_df["ASBG05A"] == c_val)]
        if len(sub_br) > 0 and len(sub_e) > 0:
            m_br = np.average(sub_br["ASMMAT01"], weights=sub_br["TOTWGT"])
            m_e = np.average(sub_e["ASMMAT01"], weights=sub_e["TOTWGT"])
            diff = m_e - m_br
            rows.append({
                "subgroup_dimension": "Home Computer Access",
                "subgroup_category": c_lbl,
                "n_paper_students": len(sub_br),
                "n_digital_students": len(sub_e),
                "paper_pv_score": round(float(m_br), 1),
                "digital_pv_score": round(float(m_e), 1),
                "scale_diff_pts": round(float(diff), 1)
            })
            
    return pd.DataFrame(rows)


def main():
    print("=" * 80)
    print("TIMSS 2019 Empirical Mode Effects Analysis")
    print("=" * 80)
    
    # Load processed data
    item_df = pd.read_parquet(PROCESSED_DIR / "timss_2019_g4_item_contrasts.parquet")
    stu_df = pd.read_parquet(PROCESSED_DIR / "timss_2019_g4_student_pvs.parquet")
    
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
    
    print("\n[SUCCESS] Statistical analysis complete.")


if __name__ == "__main__":
    main()
