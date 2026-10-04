"""
Analysis: Longitudinal Instructional-Load & School Context Analysis (Study B / Phase 4).
Outputs:
- artifacts/tables/table_b01_longitudinal_dimensions_national.csv
- artifacts/tables/table_b02_balanced_school_panel_context.csv
- artifacts/tables/table_b03_class_size_vs_context_bivariate.csv
- artifacts/tables/table_b04_kc_metro_vs_national_context.csv
- artifacts/figures/fig_b01_longitudinal_context_dimensions.png
- artifacts/figures/fig_b02_class_size_bins_vs_context.png
- artifacts/figures/fig_b03_chronic_absenteeism_distribution_shift.png

Methodological Discipline:
- Keep all dimensions strictly distinct (no composite "index").
- State explicitly that school-level rates describe surrounding context, not section composition.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

DATA_PROCESSED = PROJECT_DIR / "data" / "processed"
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"
TABLES_DIR = ARTIFACTS_DIR / "tables"
FIGURES_DIR = ARTIFACTS_DIR / "figures"

TABLES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Styling configuration
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 13,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
})


def load_data():
    """Load school context panel and filter to secondary schools."""
    parquet_path = DATA_PROCESSED / "school_context_panel.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"Missing {parquet_path}. Run build_school_context_panel.py first.")
    df = pd.read_parquet(parquet_path)
    return df


def generate_table_b01(df):
    """
    Table B1: National Longitudinal Trajectories Across Separate Dimensions (2013-14 to 2023-24).
    Evaluates secondary schools offering core STEM courses.
    """
    print("--> Generating Table B01: National Longitudinal Dimensions...")
    sec = df[df["in_class_size_panel"]].copy()
    
    rows = []
    for w in sorted(sec["crdc_wave"].unique()):
        sub = sec[sec["crdc_wave"] == w]
        sy = sub["school_year"].iloc[0]
        n_sch = len(sub)
        
        rows.append({
            "crdc_wave": w,
            "school_year": sy,
            "schools_n": n_sch,
            "mean_enrollment": sub["school_enrollment"].mean(),
            "mean_class_size_cell": sub["mean_class_size_cell"].mean(),
            "enr_weighted_class_size": (sub["stem_enrolled_tot"] * sub["enr_weighted_class_size"]).sum() / sub["stem_enrolled_tot"].sum() if sub["stem_enrolled_tot"].sum() > 0 else np.nan,
            "mean_ptr": sub["school_ptr"].mean(),
            "median_ptr": sub["school_ptr"].median(),
            "mean_pct_idea": sub["pct_idea"].mean(),
            "median_pct_idea": sub["pct_idea"].median(),
            "mean_pct_504": sub["pct_sec504"].mean(),
            "median_pct_504": sub["pct_sec504"].median(),
            "mean_pct_el": sub["pct_el"].mean(),
            "median_pct_el": sub["pct_el"].median(),
            "mean_pct_chronic_absent": sub["pct_chronic_absent"].mean(),
            "median_pct_chronic_absent": sub["pct_chronic_absent"].median(),
            "p75_pct_chronic_absent": sub["pct_chronic_absent"].quantile(0.75),
            "valid_chronic_absent_n": sub["pct_chronic_absent"].notna().sum(),
            "mean_student_counselor_ratio": sub["student_counselor_ratio"].mean(),
            "median_student_counselor_ratio": sub["student_counselor_ratio"].median(),
        })
        
    df_t1 = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table_b01_longitudinal_dimensions_national.csv"
    df_t1.to_csv(out_csv, index=False)
    print(f"--> Saved Table B01 to {out_csv}")
    return df_t1


def generate_table_b02(df):
    """
    Table B2: Longitudinal Changes within a Continuously Reporting Balanced School Panel.
    Restricts to secondary schools continuously reporting across all 6 waves.
    """
    print("--> Generating Table B02: Balanced School Panel Context...")
    sec = df[df["in_class_size_panel"]].copy()
    
    # Identify schools present in all 6 waves
    sch_waves = sec.groupby("nces_school_id")["crdc_wave"].nunique()
    balanced_sids = sch_waves[sch_waves == 6].index
    print(f"Found {len(balanced_sids):,} schools reporting in all 6 CRDC waves.")
    
    df_bal = sec[sec["nces_school_id"].isin(balanced_sids)].copy()
    
    rows = []
    for w in sorted(df_bal["crdc_wave"].unique()):
        sub = df_bal[df_bal["crdc_wave"] == w]
        sy = sub["school_year"].iloc[0]
        
        rows.append({
            "crdc_wave": w,
            "school_year": sy,
            "balanced_schools_n": len(sub),
            "mean_enrollment": sub["school_enrollment"].mean(),
            "mean_class_size_cell": sub["mean_class_size_cell"].mean(),
            "enr_weighted_class_size": (sub["stem_enrolled_tot"] * sub["enr_weighted_class_size"]).sum() / sub["stem_enrolled_tot"].sum(),
            "mean_ptr": sub["school_ptr"].mean(),
            "mean_pct_idea": sub["pct_idea"].mean(),
            "median_pct_idea": sub["pct_idea"].median(),
            "mean_pct_504": sub["pct_sec504"].mean(),
            "median_pct_504": sub["pct_sec504"].median(),
            "mean_pct_el": sub["pct_el"].mean(),
            "median_pct_el": sub["pct_el"].median(),
            "mean_pct_chronic_absent": sub["pct_chronic_absent"].mean(),
            "median_pct_chronic_absent": sub["pct_chronic_absent"].median(),
            "valid_chronic_absent_n": sub["pct_chronic_absent"].notna().sum(),
        })
        
    df_t2 = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table_b02_balanced_school_panel_context.csv"
    df_t2.to_csv(out_csv, index=False)
    print(f"--> Saved Table B02 to {out_csv}")
    return df_t2


def generate_table_b03(df):
    """
    Table B3: Class Size Bins x Surrounding Instructional Context (2021-22 & 2023-24).
    Cross-tabulates secondary schools categorized by enrollment-weighted class size.
    """
    print("--> Generating Table B03: Class Size Bins x Context...")
    sec = df[df["in_class_size_panel"] & df["crdc_wave"].isin(["2021-22", "2023-24"])].copy()
    
    # We analyze 2021-22 (complete with chronic absenteeism) and 2023-24
    rows = []
    for wave in ["2021-22", "2023-24"]:
        sub_w = sec[sec["crdc_wave"] == wave]
        for cbin in ["<20", "20-24", "25-29", "30+"]:
            sub = sub_w[sub_w["class_size_bin"] == cbin]
            if len(sub) == 0:
                continue
            rows.append({
                "crdc_wave": wave,
                "class_size_bin": cbin,
                "schools_n": len(sub),
                "pct_of_secondary_schools": (len(sub) / len(sub_w)) * 100.0,
                "mean_school_enrollment": sub["school_enrollment"].mean(),
                "mean_class_size": sub["enr_weighted_class_size"].mean(),
                "mean_ptr": sub["school_ptr"].mean(),
                "mean_pct_idea": sub["pct_idea"].mean(),
                "median_pct_idea": sub["pct_idea"].median(),
                "mean_pct_504": sub["pct_sec504"].mean(),
                "median_pct_504": sub["pct_sec504"].median(),
                "mean_pct_el": sub["pct_el"].mean(),
                "median_pct_el": sub["pct_el"].median(),
                "mean_pct_chronic_absent": sub["pct_chronic_absent"].mean() if wave == "2021-22" else np.nan,
                "median_pct_chronic_absent": sub["pct_chronic_absent"].median() if wave == "2021-22" else np.nan,
            })
            
    df_t3 = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table_b03_class_size_vs_context_bivariate.csv"
    df_t3.to_csv(out_csv, index=False)
    print(f"--> Saved Table B03 to {out_csv}")
    return df_t3


def generate_table_b04(df):
    """
    Table B4: Kansas City Metropolitan Area vs. National Benchmark.
    """
    print("--> Generating Table B04: KC Metro vs. National Context...")
    sec = df[df["in_class_size_panel"]].copy()
    
    rows = []
    for w in sorted(sec["crdc_wave"].unique()):
        for pop, is_kc in [("National", False), ("Kansas City Metro", True)]:
            if pop == "Kansas City Metro":
                sub = sec[(sec["crdc_wave"] == w) & sec["is_kc_metro"]]
            else:
                sub = sec[sec["crdc_wave"] == w]
                
            if len(sub) == 0:
                continue
                
            rows.append({
                "crdc_wave": w,
                "population": pop,
                "schools_n": len(sub),
                "mean_enrollment": sub["school_enrollment"].mean(),
                "mean_class_size": sub["enr_weighted_class_size"].mean(),
                "mean_ptr": sub["school_ptr"].mean(),
                "mean_pct_idea": sub["pct_idea"].mean(),
                "mean_pct_504": sub["pct_sec504"].mean(),
                "mean_pct_el": sub["pct_el"].mean(),
                "mean_pct_chronic_absent": sub["pct_chronic_absent"].mean(),
                "median_pct_chronic_absent": sub["pct_chronic_absent"].median(),
            })
            
    df_t4 = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table_b04_kc_metro_vs_national_context.csv"
    df_t4.to_csv(out_csv, index=False)
    print(f"--> Saved Table B04 to {out_csv}")
    return df_t4


def plot_fig_b01(df_t1):
    """
    Figure B1: 4-Panel Plot of Separate Longitudinal Trajectories (2013-14 to 2023-24).
    Panel (a): Secondary Class Size vs Campus PTR
    Panel (b): Student Individualized Accommodations (% IDEA and % Section 504)
    Panel (c): Language Diversity (% English Learners)
    Panel (d): Attendance Disruption (% Chronically Absent)
    """
    print("--> Rendering Figure B01: Longitudinal Context Dimensions...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True)
    
    waves = df_t1["crdc_wave"].tolist()
    x = np.arange(len(waves))
    
    # Panel (a): Class Size vs PTR
    ax = axes[0, 0]
    ax.plot(x, df_t1["enr_weighted_class_size"], marker="o", color="#1f77b4", linewidth=2, label="Secondary Class Size (Enr-Wt)")
    ax.plot(x, df_t1["mean_class_size_cell"], marker="s", color="#1f77b4", linestyle="--", alpha=0.7, label="Secondary Class Size (Cell-Mean)")
    ax.plot(x, df_t1["mean_ptr"], marker="^", color="#d62728", linewidth=2, label="Campus PTR (NCES/CRDC)")
    ax.set_title("(a) Secondary Class Size vs. Campus PTR", fontweight="bold")
    ax.set_ylabel("Students per Class / Teacher")
    ax.set_ylim(12, 22)
    ax.legend(loc="upper right", framealpha=0.9)
    
    # Panel (b): Accommodations (IDEA & 504)
    ax = axes[0, 1]
    ax.plot(x, df_t1["mean_pct_idea"], marker="o", color="#2ca02c", linewidth=2, label="% Students with Disabilities (IDEA)")
    ax.plot(x, df_t1["mean_pct_504"], marker="s", color="#ff7f0e", linewidth=2, label="% Section 504-Only Plans")
    ax.set_title("(b) Individualized Legal Accommodations (% of Enrollment)", fontweight="bold")
    ax.set_ylabel("Percent of Enrolled Students (%)")
    ax.set_ylim(0, 24)
    ax.legend(loc="center left", framealpha=0.9)
    
    # Panel (c): English Learners
    ax = axes[1, 0]
    ax.plot(x, df_t1["mean_pct_el"], marker="o", color="#9467bd", linewidth=2, label="% English Learners (EL / LEP)")
    ax.set_title("(c) English Learner Enrollment (% of Enrollment)", fontweight="bold")
    ax.set_ylabel("Percent of Enrolled Students (%)")
    ax.set_xlabel("CRDC Census Wave")
    ax.set_xticks(x)
    ax.set_xticklabels(waves, rotation=25)
    ax.set_ylim(0, 12)
    ax.legend(loc="upper left", framealpha=0.9)
    
    # Panel (d): Chronic Absenteeism
    ax = axes[1, 1]
    # Filter out 2023-24 where absent is NaN
    abs_mask = df_t1["median_pct_chronic_absent"].notna()
    x_abs = x[abs_mask]
    ax.plot(x_abs, df_t1.loc[abs_mask, "median_pct_chronic_absent"], marker="o", color="#8c564b", linewidth=2, label="Median Secondary School % Absent")
    ax.plot(x_abs, df_t1.loc[abs_mask, "p75_pct_chronic_absent"], marker="^", color="#8c564b", linestyle=":", label="75th Percentile School % Absent")
    ax.axvline(x=3, color="gray", linestyle="--", alpha=0.5, label="COVID Shock (2020-21)")
    ax.set_title("(d) Chronic Student Absenteeism (15+ Days Missed)", fontweight="bold")
    ax.set_ylabel("Percent of Enrolled Students (%)")
    ax.set_xlabel("CRDC Census Wave")
    ax.set_xticks(x)
    ax.set_xticklabels(waves, rotation=25)
    ax.set_ylim(0, 50)
    ax.legend(loc="upper left", framealpha=0.9)
    
    plt.tight_layout()
    out_fig = FIGURES_DIR / "fig_b01_longitudinal_context_dimensions.png"
    plt.savefig(out_fig, bbox_inches="tight")
    plt.close()
    print(f"--> Saved Figure B01 to {out_fig}")


def plot_fig_b02(df):
    """
    Figure B2: Class Size Bins vs Surrounding Instructional Context (2021-22).
    Shows the distribution of surrounding % IDEA, % 504, % EL, and % Chronic Absenteeism.
    """
    print("--> Rendering Figure B02: Class Size Bins vs. Context...")
    df_21 = df[df["in_class_size_panel"] & (df["crdc_wave"] == "2021-22") & df["class_size_bin"].notna()].copy()
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True)
    bin_order = ["<20", "20-24", "25-29", "30+"]
    palette = ["#4575b4", "#74add1", "#fdae61", "#f46d43"]
    
    # 1. % IDEA
    sns.boxplot(data=df_21, x="class_size_bin", y="pct_idea", order=bin_order, ax=axes[0, 0], palette=palette, showfliers=False)
    axes[0, 0].set_title("(a) Surrounding % IDEA (Special Education)", fontweight="bold")
    axes[0, 0].set_ylabel("% of School Enrollment")
    axes[0, 0].set_xlabel("")
    axes[0, 0].set_ylim(0, 35)
    
    # 2. % Section 504
    sns.boxplot(data=df_21, x="class_size_bin", y="pct_sec504", order=bin_order, ax=axes[0, 1], palette=palette, showfliers=False)
    axes[0, 1].set_title("(b) Surrounding % Section 504 Plans", fontweight="bold")
    axes[0, 1].set_ylabel("% of School Enrollment")
    axes[0, 1].set_xlabel("")
    axes[0, 1].set_ylim(0, 15)
    
    # 3. % English Learners
    sns.boxplot(data=df_21, x="class_size_bin", y="pct_el", order=bin_order, ax=axes[1, 0], palette=palette, showfliers=False)
    axes[1, 0].set_title("(c) Surrounding % English Learners", fontweight="bold")
    axes[1, 0].set_ylabel("% of School Enrollment")
    axes[1, 0].set_xlabel("Enrollment-Weighted School Class Size Bin")
    axes[1, 0].set_ylim(0, 30)
    
    # 4. % Chronic Absenteeism
    sns.boxplot(data=df_21, x="class_size_bin", y="pct_chronic_absent", order=bin_order, ax=axes[1, 1], palette=palette, showfliers=False)
    axes[1, 1].set_title("(d) Surrounding % Chronic Absenteeism (2021–22)", fontweight="bold")
    axes[1, 1].set_ylabel("% of School Enrollment")
    axes[1, 1].set_xlabel("Enrollment-Weighted School Class Size Bin")
    axes[1, 1].set_ylim(0, 70)
    
    plt.tight_layout()
    out_fig = FIGURES_DIR / "fig_b02_class_size_bins_vs_context.png"
    plt.savefig(out_fig, bbox_inches="tight")
    plt.close()
    print(f"--> Saved Figure B02 to {out_fig}")


def plot_fig_b03(df):
    """
    Figure B3: Pre-COVID vs Post-COVID Distribution of Chronic Absenteeism in Secondary Schools.
    Compares 2017-18 to 2021-22.
    """
    print("--> Rendering Figure B03: Chronic Absenteeism Distribution Shift...")
    sec = df[df["in_class_size_panel"] & df["crdc_wave"].isin(["2017-18", "2021-22"])].copy()
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    sub17 = sec[(sec["crdc_wave"] == "2017-18") & sec["pct_chronic_absent"].notna()]["pct_chronic_absent"]
    sub21 = sec[(sec["crdc_wave"] == "2021-22") & sec["pct_chronic_absent"].notna()]["pct_chronic_absent"]
    
    sns.kdeplot(sub17, ax=ax, color="#1f77b4", linewidth=2.5, label=f"Pre-COVID (2017–18): Median = {sub17.median():.1f}%", clip=(0, 100))
    sns.kdeplot(sub21, ax=ax, color="#d62728", linewidth=2.5, label=f"Post-COVID (2021–22): Median = {sub21.median():.1f}%", clip=(0, 100))
    
    ax.axvline(sub17.median(), color="#1f77b4", linestyle="--", alpha=0.7)
    ax.axvline(sub21.median(), color="#d62728", linestyle="--", alpha=0.7)
    
    # Highlight threshold >= 30%
    ax.axvline(30, color="gray", linestyle=":", alpha=0.8, label="Severe Disruption Threshold (≥30%)")
    
    pct_gt30_17 = (sub17 >= 30).mean() * 100
    pct_gt30_21 = (sub21 >= 30).mean() * 100
    
    ax.text(32, ax.get_ylim()[1]*0.8, f"Schools ≥30% Absent:\n  2017–18: {pct_gt30_17:.1f}%\n  2021–22: {pct_gt30_21:.1f}% (+{pct_gt30_21-pct_gt30_17:.1f} pp)", fontsize=10, bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9))
    
    ax.set_title("The Attendance Shock: Distribution of Secondary School Chronic Absenteeism Rates", fontweight="bold")
    ax.set_xlabel("Chronic Absenteeism Rate (% of Enrolled Students Absent 15+ Days)")
    ax.set_ylabel("Kernel Density")
    ax.set_xlim(0, 90)
    ax.legend(loc="upper right", framealpha=0.9)
    
    plt.tight_layout()
    out_fig = FIGURES_DIR / "fig_b03_chronic_absenteeism_distribution_shift.png"
    plt.savefig(out_fig, bbox_inches="tight")
    plt.close()
    print(f"--> Saved Figure B03 to {out_fig}")


def run_all_analysis():
    print("=" * 70)
    print("EXECUTING STUDY B ANALYSIS: INSTRUCTIONAL LOAD & SCHOOL CONTEXT")
    print("=" * 70)
    df = load_data()
    print(f"Loaded {len(df):,} total school-wave records from school_context_panel.parquet.")
    
    t1 = generate_table_b01(df)
    t2 = generate_table_b02(df)
    t3 = generate_table_b03(df)
    t4 = generate_table_b04(df)
    
    plot_fig_b01(t1)
    plot_fig_b02(df)
    plot_fig_b03(df)
    
    print("\n" + "=" * 70)
    print("STUDY B ANALYSIS EXECUTION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    run_all_analysis()
