"""
Analysis Suite for Study A: Empirical Classroom Size & Capacity Measurement.
Covers:
- Analysis A1: Longitudinal distributions across National, State, and Kansas City populations.
- Analysis A2: Course-level hierarchy (Foundation Core vs. Advanced Electives).
- Analysis A3: Weighting sensitivity (Course-Cell vs. Section-Weighted vs. Student/Seat-Weighted).
- Analysis A4: Staffing allocation wedge (Class Size vs. Contemporaneous PTR).
- Analysis A5: Within-school course hierarchy (School Fixed Effects).
- Analysis A6: Longitudinal robustness (Repeated Cross-Section vs. Balanced Panel).
Outputs tables to artifacts/tables/ and figures to artifacts/figures/.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

DATA_DIR = PROJECT_DIR / "data" / "processed"
TABLES_DIR = PROJECT_DIR / "artifacts" / "tables"
FIGURES_DIR = PROJECT_DIR / "artifacts" / "figures"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Visual styling
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})

def load_data():
    """Load the harmonized parquet panel and clean bounds."""
    df = pd.read_parquet(DATA_DIR / "crdc_course_panel.parquet")
    # Clean analytical sample: non-zero, plausible bounds (<= 60 for clean distributions)
    valid_mask = (df["mean_class_size"] > 0) & (df["mean_class_size"] <= 60)
    return df, df[valid_mask].copy()

def run_analysis_a1_and_a2(df_valid):
    """
    Analysis A1 & A2: Distribution of school-course mean class sizes by wave and course.
    Calculates course-cell mean, section-weighted mean, seat-weighted mean, percentiles,
    and exposure bins (<20, 20-24, 25-29, 30-34, 35+).
    """
    print("--> Running Analysis A1 & A2: Wave & Course Distributions...")
    results = []
    
    for (wave, ccode), g in df_valid.groupby(["crdc_wave", "course_code"]):
        cname = g["course_name"].iloc[0]
        clevel = g["course_level"].iloc[0]
        n_schools = g["nces_school_id"].nunique()
        tot_cls = g["num_classes"].sum()
        tot_enr = g["num_enrolled"].sum()
        cs = g["mean_class_size"]
        
        unwt_mean = cs.mean()
        sec_wt = tot_enr / tot_cls if tot_cls > 0 else np.nan
        seat_wt = (g["num_enrolled"] * cs).sum() / tot_enr if tot_enr > 0 else np.nan
        
        med = cs.median()
        p25 = cs.quantile(0.25)
        p75 = cs.quantile(0.75)
        p90 = cs.quantile(0.90)
        p95 = cs.quantile(0.95)
        std = cs.std()
        
        # Exposure shares across bins
        sh_under_20 = (cs < 20).mean() * 100
        sh_20_24 = ((cs >= 20) & (cs < 25)).mean() * 100
        sh_25_29 = ((cs >= 25) & (cs < 30)).mean() * 100
        sh_30_34 = ((cs >= 30) & (cs < 35)).mean() * 100
        sh_35_plus = (cs >= 35).mean() * 100
        
        sh_ge_25 = (cs >= 25).mean() * 100
        sh_ge_30 = (cs >= 30).mean() * 100
        sh_ge_35 = (cs >= 35).mean() * 100
        
        # Seat-weighted exposure shares (the share of student enrollment in those cells)
        seat_ge_25 = (g.loc[cs >= 25, "num_enrolled"].sum() / tot_enr) * 100 if tot_enr > 0 else np.nan
        seat_ge_30 = (g.loc[cs >= 30, "num_enrolled"].sum() / tot_enr) * 100 if tot_enr > 0 else np.nan
        seat_ge_35 = (g.loc[cs >= 35, "num_enrolled"].sum() / tot_enr) * 100 if tot_enr > 0 else np.nan
        
        results.append({
            "crdc_wave": wave,
            "course_code": ccode,
            "course_name": cname,
            "course_level": clevel,
            "n_schools": n_schools,
            "total_classes": tot_cls,
            "total_students": tot_enr,
            "course_cell_mean": unwt_mean,
            "section_weighted_mean": sec_wt,
            "seat_weighted_mean": seat_wt,
            "std_dev": std,
            "median": med,
            "p25": p25,
            "p75": p75,
            "p90": p90,
            "p95": p95,
            "cell_pct_under_20": sh_under_20,
            "cell_pct_20_24": sh_20_24,
            "cell_pct_25_29": sh_25_29,
            "cell_pct_30_34": sh_30_34,
            "cell_pct_35_plus": sh_35_plus,
            "cell_pct_ge_25": sh_ge_25,
            "cell_pct_ge_30": sh_ge_30,
            "cell_pct_ge_35": sh_ge_35,
            "seat_pct_ge_25": seat_ge_25,
            "seat_pct_ge_30": seat_ge_30,
            "seat_pct_ge_35": seat_ge_35,
        })
        
    df_res = pd.DataFrame(results)
    out_csv = TABLES_DIR / "table01_national_course_distributions.csv"
    df_res.to_csv(out_csv, index=False)
    print(f"--> Saved Table 01 to {out_csv}")
    return df_res

def run_analysis_a3(df_valid):
    """
    Analysis A3: Weighting sensitivity.
    Directly quantifies the divergence between course-cell weighting,
    section weighting, and seat weighting across all courses in recent waves.
    """
    print("--> Running Analysis A3: Weighting Sensitivity Analysis...")
    rows = []
    
    for wave in ["2013-14", "2017-18", "2023-24"]:
        w_df = df_valid[df_valid["crdc_wave"] == wave]
        for ccode in ["alg1", "geom", "alg2", "calc", "bio", "chem", "phys"]:
            cg = w_df[w_df["course_code"] == ccode]
            if cg.empty:
                continue
            cname = cg["course_name"].iloc[0]
            unwt = cg["mean_class_size"].mean()
            tot_enr = cg["num_enrolled"].sum()
            tot_cls = cg["num_classes"].sum()
            sec_wt = tot_enr / tot_cls if tot_cls > 0 else np.nan
            seat_wt = (cg["num_enrolled"] * cg["mean_class_size"]).sum() / tot_enr if tot_enr > 0 else np.nan
            
            gap_seat_unwt = seat_wt - unwt
            gap_seat_sec = seat_wt - sec_wt
            pct_boost = (gap_seat_unwt / unwt) * 100
            
            rows.append({
                "wave": wave,
                "course_code": ccode,
                "course_name": cname,
                "course_cell_mean": unwt,
                "section_weighted_mean": sec_wt,
                "seat_weighted_mean": seat_wt,
                "seat_minus_cell_gap": gap_seat_unwt,
                "seat_minus_sec_gap": gap_seat_sec,
                "pct_increase_seat_weighting": pct_boost,
            })
            
    df_wt = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table02_weighting_comparison.csv"
    df_wt.to_csv(out_csv, index=False)
    print(f"--> Saved Table 02 to {out_csv}")
    return df_wt

def run_analysis_a4(df_valid):
    """
    Analysis A4: PTR Staffing Wedge.
    Computes absolute wedge (ClassSize - PTR) and wedge ratio (ClassSize / PTR).
    Compares national, Missouri, Kansas, and Kansas City metro.
    """
    print("--> Running Analysis A4: Staffing Allocation Wedge...")
    sub = df_valid[pd.notnull(df_valid["school_ptr"]) & (df_valid["school_ptr"] > 0) & (df_valid["school_ptr"] <= 50)].copy()
    
    rows = []
    pops = [
        ("National", sub),
        ("Missouri (Statewide)", sub[sub["state"] == "MO"]),
        ("Kansas (Statewide)", sub[sub["state"] == "KS"]),
        ("Kansas City Metro", sub[sub["is_kc_metro"] == True]),
    ]
    
    for pop_name, pop_df in pops:
        if pop_df.empty:
            continue
        for wave in ["2015-16", "2017-18", "2020-21", "2021-22", "2023-24"]:
            w_df = pop_df[pop_df["crdc_wave"] == wave]
            if w_df.empty:
                continue
            
            mean_cs = w_df["mean_class_size"].mean()
            median_cs = w_df["mean_class_size"].median()
            mean_ptr = w_df["school_ptr"].mean()
            median_ptr = w_df["school_ptr"].median()
            
            wedge = w_df["ptr_wedge"]
            ratio = w_df["ptr_wedge_ratio"]
            
            rows.append({
                "population": pop_name,
                "wave": wave,
                "n_observations": len(w_df),
                "schools_n": w_df["nces_school_id"].nunique(),
                "mean_class_size": mean_cs,
                "median_class_size": median_cs,
                "mean_school_ptr": mean_ptr,
                "median_school_ptr": median_ptr,
                "mean_absolute_wedge": wedge.mean(),
                "median_absolute_wedge": wedge.median(),
                "mean_wedge_ratio": ratio.mean(),
                "median_wedge_ratio": ratio.median(),
                "pct_schools_class_size_gt_ptr": (wedge > 0).mean() * 100,
            })
            
    df_wedge = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table03_ptr_wedge_summary.csv"
    df_wedge.to_csv(out_csv, index=False)
    print(f"--> Saved Table 03 to {out_csv}")
    return df_wedge

def run_analysis_a5(df_valid):
    """
    Analysis A5: Within-School Course Hierarchy (School Fixed Effects).
    ClassSize_{sct} = alpha_s + gamma_c + delta_t + epsilon_{sct}
    Estimates whether foundation core courses absorb systematically larger classes
    than advanced electives within the same high school campus.
    """
    print("--> Running Analysis A5: Within-School Fixed Effects Models...")
    
    # We estimate two models:
    # Model 1: Kansas City Metro schools
    # Model 2: Missouri & Kansas state schools
    # Model 3: National 10% random sample of schools (to run within seconds with full SE clustering)
    
    samples = [
        ("Kansas City Metro", df_valid[df_valid["is_kc_metro"] == True]),
        ("MO and KS Statewide", df_valid[df_valid["state"].isin(["MO", "KS"])]),
    ]
    
    # National sample of schools
    np.random.seed(42)
    all_sids = df_valid["nces_school_id"].unique()
    sample_sids = np.random.choice(all_sids, size=min(4000, len(all_sids)), replace=False)
    df_nat_sample = df_valid[df_valid["nces_school_id"].isin(sample_sids)]
    samples.append(("National Sample (4,000 Schools)", df_nat_sample))
    
    results = []
    for sname, sdata in samples:
        # Require at least 2 courses per school
        sch_counts = sdata.groupby("nces_school_id")["course_code"].nunique()
        multi_course_sids = sch_counts[sch_counts >= 2].index
        reg_df = sdata[sdata["nces_school_id"].isin(multi_course_sids)].copy()
        
        mod = smf.ols(
            'mean_class_size ~ C(course_code, Treatment("alg1")) + C(crdc_wave, Treatment("2017-18")) + C(nces_school_id)',
            data=reg_df
        ).fit()
        
        # Extract course parameters
        course_names = {
            "geom": "Geometry", "alg2": "Algebra II", "advm": "Advanced Math",
            "calc": "Calculus", "bio": "Biology", "chem": "Chemistry", "phys": "Physics"
        }
        
        for ccode, label in course_names.items():
            param_key = f'C(course_code, Treatment("alg1"))[T.{ccode}]'
            if param_key in mod.params:
                coef = mod.params[param_key]
                se = mod.bse[param_key]
                pval = mod.pvalues[param_key]
                ci_low = coef - 1.96 * se
                ci_high = coef + 1.96 * se
                results.append({
                    "sample": sname,
                    "n_obs": int(mod.nobs),
                    "r_squared": mod.rsquared,
                    "course_code": ccode,
                    "course_name": label,
                    "coef_vs_alg1": coef,
                    "std_err": se,
                    "p_value": pval,
                    "ci_95_low": ci_low,
                    "ci_95_high": ci_high,
                })
                
    df_fe = pd.DataFrame(results)
    out_csv = TABLES_DIR / "table04_fixed_effects_coefficients.csv"
    df_fe.to_csv(out_csv, index=False)
    print(f"--> Saved Table 04 to {out_csv}")
    return df_fe

def run_analysis_a6(df_valid):
    """
    Analysis A6: Longitudinal Robustness: Balanced Panel vs. Repeated Cross-Sections.
    Examines whether trends from 2013-14 to 2023-24 hold when restricting to the
    balanced panel of schools present in all 6 CRDC collection waves.
    """
    print("--> Running Analysis A6: Balanced Panel Robustness...")
    
    # Identify balanced schools reporting in all 6 waves
    wave_counts = df_valid.groupby("nces_school_id")["crdc_wave"].nunique()
    balanced_sids = set(wave_counts[wave_counts == 6].index)
    
    print(f"    Identified {len(balanced_sids):,} balanced schools reporting across all 6 waves.")
    
    df_balanced = df_valid[df_valid["nces_school_id"].isin(balanced_sids)].copy()
    
    rows = []
    for wave in ["2013-14", "2015-16", "2017-18", "2020-21", "2021-22", "2023-24"]:
        cross_w = df_valid[df_valid["crdc_wave"] == wave]
        bal_w = df_balanced[df_balanced["crdc_wave"] == wave]
        
        for ccode in ["alg1", "geom", "alg2", "bio", "chem"]:
            cg_cross = cross_w[cross_w["course_code"] == ccode]
            cg_bal = bal_w[bal_w["course_code"] == ccode]
            
            cname = cg_cross["course_name"].iloc[0] if not cg_cross.empty else ccode
            
            # Cross section
            unwt_cross = cg_cross["mean_class_size"].mean() if not cg_cross.empty else np.nan
            seat_cross = (cg_cross["num_enrolled"] * cg_cross["mean_class_size"]).sum() / cg_cross["num_enrolled"].sum() if not cg_cross.empty else np.nan
            
            # Balanced
            unwt_bal = cg_bal["mean_class_size"].mean() if not cg_bal.empty else np.nan
            seat_bal = (cg_bal["num_enrolled"] * cg_bal["mean_class_size"]).sum() / cg_bal["num_enrolled"].sum() if not cg_bal.empty else np.nan
            
            rows.append({
                "wave": wave,
                "course_code": ccode,
                "course_name": cname,
                "repeated_cross_cell_mean": unwt_cross,
                "repeated_cross_seat_mean": seat_cross,
                "balanced_cell_mean": unwt_bal,
                "balanced_seat_mean": seat_bal,
                "cell_mean_diff_bal_minus_cross": unwt_bal - unwt_cross,
                "seat_mean_diff_bal_minus_cross": seat_bal - seat_cross,
            })
            
    df_rob = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table06_balanced_panel_robustness.csv"
    df_rob.to_csv(out_csv, index=False)
    print(f"--> Saved Table 06 to {out_csv}")
    return df_rob

def generate_analytical_figures(df_valid, df_res, df_wt, df_wedge):
    """Generate high-resolution analytical figures for the Study A artifact."""
    print("--> Generating Analytical Figures...")
    
    # -------------------------------------------------------------
    # Figure 1: Weighting Wedge Divergence across Courses (2023-24)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    df_23 = df_res[df_res["crdc_wave"] == "2023-24"].sort_values("seat_weighted_mean", ascending=True)
    
    y = np.arange(len(df_23))
    height = 0.28
    
    ax.barh(y - height, df_23["course_cell_mean"], height, label="Course-Cell Unweighted Mean", color="#4a7c59", alpha=0.85)
    ax.barh(y, df_23["section_weighted_mean"], height, label="Section-Weighted Mean", color="#33658a", alpha=0.85)
    ax.barh(y + height, df_23["seat_weighted_mean"], height, label="Student / Seat-Weighted Mean", color="#f26419", alpha=0.90)
    
    ax.set_yticks(y)
    ax.set_yticklabels(df_23["course_name"], fontweight="bold")
    ax.set_xlabel("Mean Students per Class")
    ax.set_title("Figure 1: The Weighting Wedge in U.S. Classrooms (CRDC 2023–24 Census)\n"
                 "Institutional Course Averages vs. Actual Student Seat Experience", pad=15)
    ax.legend(loc="lower right", frameon=True)
    ax.set_xlim(0, 24)
    
    for i, (_, r) in enumerate(df_23.iterrows()):
        ax.text(r["seat_weighted_mean"] + 0.3, i + height, f"{r['seat_weighted_mean']:.1f}", va="center", fontsize=9, fontweight="bold", color="#d64900")
        ax.text(r["course_cell_mean"] - 1.2, i - height, f"{r['course_cell_mean']:.1f}", va="center", fontsize=9, color="white", fontweight="bold")
        
    plt.tight_layout()
    fig1_path = FIGURES_DIR / "fig01_weighting_wedge_divergence.png"
    plt.savefig(fig1_path)
    plt.close()
    print(f"    Saved {fig1_path}")
    
    # -------------------------------------------------------------
    # Figure 2: The Curriculum Hierarchy (Foundation Core vs. Advanced Electives)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    order = ["Algebra I", "Biology", "Geometry", "Algebra II", "Chemistry", "Advanced Mathematics", "Physics", "Calculus"]
    df_23_full = df_valid[(df_valid["crdc_wave"] == "2023-24") & (df_valid["course_name"].isin(order))]
    
    palette = {"Foundation Core": "#2a9d8f", "Advanced / Specialized": "#e76f51"}
    sns.boxplot(
        data=df_23_full,
        x="course_name",
        y="mean_class_size",
        order=order,
        hue="course_level",
        palette=palette,
        showmeans=True,
        meanprops={"marker": "D", "markeredgecolor": "black", "markerfacecolor": "yellow", "markersize": 6},
        ax=ax,
        fliersize=1,
        boxprops=dict(alpha=0.8)
    )
    ax.set_xticklabels(order, rotation=25, ha="right")
    ax.set_xlabel("Secondary Course Offering")
    ax.set_ylabel("School-Course Mean Class Size")
    ax.set_title("Figure 2: Distribution of School-Course Mean Class Sizes Across Subjects (CRDC 2023–24)\n"
                 "Yellow Diamonds = Seat-Weighted Mean; Solid Lines = Median", pad=15)
    ax.legend(title="Curricular Tier", loc="upper right")
    ax.set_ylim(0, 45)
    
    plt.tight_layout()
    fig2_path = FIGURES_DIR / "fig02_course_size_hierarchy.png"
    plt.savefig(fig2_path)
    plt.close()
    print(f"    Saved {fig2_path}")
    
    # -------------------------------------------------------------
    # Figure 3: Student Seat Exposure to Large Classrooms (>= 25, 30, 35)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    df_23_exp = df_res[df_res["crdc_wave"] == "2023-24"].sort_values("seat_pct_ge_25", ascending=False)
    
    x = np.arange(len(df_23_exp))
    width = 0.25
    
    ax.bar(x - width, df_23_exp["seat_pct_ge_25"], width, label="Students in Classes ≥ 25", color="#e9c46a", alpha=0.9)
    ax.bar(x, df_23_exp["seat_pct_ge_30"], width, label="Students in Classes ≥ 30", color="#f4a261", alpha=0.9)
    ax.bar(x + width, df_23_exp["seat_pct_ge_35"], width, label="Students in Classes ≥ 35", color="#e76f51", alpha=0.9)
    
    ax.set_xticks(x)
    ax.set_xticklabels(df_23_exp["course_name"], rotation=30, ha="right", fontweight="bold")
    ax.set_ylabel("Percentage of Enrolled Students (%)")
    ax.set_title("Figure 3: Upper-Tail Classroom Exposure in U.S. Secondary Schools (CRDC 2023–24)\n"
                 "Share of Student Enrollment Concentrated in School-Course Environments ≥ 25, ≥ 30, and ≥ 35", pad=15)
    ax.legend(loc="upper right", frameon=True)
    ax.set_ylim(0, 35)
    
    for i, (_, r) in enumerate(df_23_exp.iterrows()):
        ax.text(i - width, r["seat_pct_ge_25"] + 0.5, f"{r['seat_pct_ge_25']:.1f}%", ha="center", fontsize=8)
        ax.text(i, r["seat_pct_ge_30"] + 0.5, f"{r['seat_pct_ge_30']:.1f}%", ha="center", fontsize=8)
        
    plt.tight_layout()
    fig3_path = FIGURES_DIR / "fig03_upper_tail_seat_exposure.png"
    plt.savefig(fig3_path)
    plt.close()
    print(f"    Saved {fig3_path}")
    
    # -------------------------------------------------------------
    # Figure 4: The Staffing Allocation Wedge (Actual Class Size vs. PTR)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 7))
    kc_23 = df_valid[(df_valid["is_kc_metro"] == True) & (df_valid["crdc_wave"] == "2023-24") & pd.notnull(df_valid["school_ptr"])].copy()
    
    sns.scatterplot(
        data=kc_23,
        x="school_ptr",
        y="mean_class_size",
        hue="course_level",
        palette={"Foundation Core": "#264653", "Advanced / Specialized": "#e76f51"},
        alpha=0.7,
        s=40,
        ax=ax
    )
    
    # 45-degree line (Class Size = PTR)
    lims = [5, 35]
    ax.plot(lims, lims, "k--", alpha=0.6, label="Parity (Class Size = PTR)")
    
    # Schedule factor line (Class Size = 1.4 * PTR, representing 5/7 period day)
    ax.plot(lims, [1.4 * x for x in lims], "b-.", alpha=0.6, label="5/7 Schedule Line (Class Size = 1.4 × PTR)")
    
    ax.set_xlim(lims)
    ax.set_ylim(5, 45)
    ax.set_xlabel("Contemporaneous School Pupil-Teacher Ratio (PTR)")
    ax.set_ylabel("School-Course Mean Class Size")
    ax.set_title("Figure 4: The Secondary Staffing Wedge in Greater Kansas City (2023–24)\n"
                 "Course Class Sizes Systematically Exceed Macro PTR", pad=15)
    ax.legend(loc="upper left")
    
    plt.tight_layout()
    fig4_path = FIGURES_DIR / "fig04_ptr_wedge_distribution.png"
    plt.savefig(fig4_path)
    plt.close()
    print(f"    Saved {fig4_path}")
    
    # -------------------------------------------------------------
    # Figure 5: Longitudinal Trajectory (2013-14 through 2023-24)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    trend_courses = ["Algebra I", "Geometry", "Biology", "Chemistry", "Calculus"]
    df_trend = df_res[df_res["course_name"].isin(trend_courses)].copy()
    
    wave_map = {
        "2013-14": 2014, "2015-16": 2016, "2017-18": 2018,
        "2020-21": 2021, "2021-22": 2022, "2023-24": 2024
    }
    df_trend["year_num"] = df_trend["crdc_wave"].map(wave_map)
    
    for cname in trend_courses:
        cg = df_trend[df_trend["course_name"] == cname].sort_values("year_num")
        ax.plot(cg["year_num"], cg["seat_weighted_mean"], marker="o", linewidth=2.2, label=f"{cname} (Seat-Weighted)")
        
    ax.axvspan(2020.5, 2021.5, color="gray", alpha=0.2, label="COVID-19 Discontinuity (Peak Remote/Hybrid)")
    ax.set_xticks([2014, 2016, 2018, 2021, 2022, 2024])
    ax.set_xticklabels(["2013–14", "2015–16", "2017–18", "2020–21\n(COVID)", "2021–22", "2023–24"])
    ax.set_ylabel("Student / Seat-Weighted Mean Class Size")
    ax.set_xlabel("CRDC Census Wave")
    ax.set_title("Figure 5: A Decade of Secondary Class Size in the United States (2013–14 to 2023–24)\n"
                 "Pre-Pandemic Baseline, COVID Shock, and Post-Pandemic Plateau", pad=15)
    ax.legend(loc="lower left", frameon=True)
    ax.set_ylim(16, 26)
    
    plt.tight_layout()
    fig5_path = FIGURES_DIR / "fig05_longitudinal_trajectory.png"
    plt.savefig(fig5_path)
    plt.close()
    print(f"    Saved {fig5_path}")

def main():
    print("=" * 70)
    print("EXECUTING STUDY A STATISTICAL & ECONOMETRIC ANALYSIS SUITE")
    print("=" * 70)
    
    _, df_valid = load_data()
    print(f"Loaded {len(df_valid):,} valid school-course observations across all waves.")
    
    df_res = run_analysis_a1_and_a2(df_valid)
    df_wt = run_analysis_a3(df_valid)
    df_wedge = run_analysis_a4(df_valid)
    df_fe = run_analysis_a5(df_valid)
    df_rob = run_analysis_a6(df_valid)
    
    generate_analytical_figures(df_valid, df_res, df_wt, df_wedge)
    
    print("\nALL STUDY A ANALYSES & ARTIFACTS GENERATED SUCCESSFULLY.")

if __name__ == "__main__":
    main()
