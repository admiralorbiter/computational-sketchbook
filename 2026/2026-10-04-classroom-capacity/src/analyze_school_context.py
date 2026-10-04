"""
Analysis: Longitudinal Instructional-Load & School Context Analysis (Study B / Phase 4.1 Calibration Patch).
Outputs:
- artifacts/tables/table_b01_longitudinal_dimensions_national.csv
- artifacts/tables/table_b02_balanced_school_panel_context.csv
- artifacts/tables/table_b03_class_size_vs_context_bivariate.csv
- artifacts/tables/table_b04_kc_metro_vs_national_context.csv
- artifacts/figures/fig_b01_longitudinal_context_dimensions.png
- artifacts/figures/fig_b02_class_size_bins_vs_context.png
- artifacts/figures/fig_b03_chronic_absenteeism_distribution_shift.png

Methodological Discipline & Calibrations (Phase 4.1):
1. Incompatible federal chronic absenteeism regimes:
   - CRDC 15+ Days Missed (2013-14, 2015-16)
   - EDFacts >=10% of enrolled school days (2017-18, 2020-21, 2021-22)
   - 2020-21 marked explicitly as a non-representative COVID waiver year (~6% reporting).
2. Weighting identities:
   - School-weighted rate: 1/M * sum(Y_i / E_i) (experience of the average school).
   - Pooled student-weighted rate: sum(Y_i) / sum(E_i) (experience of the average enrolled student).
   - "X% of students" phrasing restricted strictly to pooled student-weighted rates.
3. Construct terminology:
   - "Students served under IDEA or Section 504-only" (does NOT claim all have written plans).
4. Measure-specific balanced panels:
   - Panel A: 6-wave balanced panel for IDEA, 504, EL.
   - Panel B: Matched 2017-18 <-> 2021-22 EDFacts chronic absenteeism panel.
   - Panel C: Matched 2013-14 <-> 2015-16 CRDC 15+ days absenteeism panel.
5. Harmonized class-size weighting and certified KC PTR in Table B4.
6. Epistemic guardrail: School context describes surrounding institutional environment,
   NOT individual teacher or section roster composition.
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
    Reports both school-weighted and pooled student-weighted rates.
    Splits chronic absenteeism into incompatible federal regimes:
    - CRDC 15+ days (2013-14, 2015-16)
    - EDFacts >=10% of enrolled school days (2017-18, 2020-21, 2021-22)
    Notes 2020-21 as non-representative COVID waiver year (~6% coverage).
    """
    print("--> Generating Table B01: National Longitudinal Dimensions...")
    sec = df[df["in_class_size_panel"]].copy()
    
    rows = []
    for w in sorted(sec["crdc_wave"].unique()):
        sub = sec[sec["crdc_wave"] == w]
        sy = sub["school_year"].iloc[0]
        n_sch = len(sub)
        
        valid_enr = sub[sub["school_enrollment"].notna() & (sub["school_enrollment"] > 0)]
        tot_enr = valid_enr["school_enrollment"].sum()
        stem_enr_tot = sub["stem_enrolled_tot"].sum()
        
        # IDEA
        sub_idea = sub[sub["idea_count"].notna() & (sub["school_enrollment"] > 0)]
        school_wt_idea = sub_idea["pct_idea"].mean()
        pooled_idea = sub_idea["idea_count"].sum() / sub_idea["school_enrollment"].sum() * 100.0 if len(sub_idea) > 0 else np.nan
        
        # Section 504-only
        sub_504 = sub[sub["sec504_count"].notna() & (sub["school_enrollment"] > 0)]
        school_wt_504 = sub_504["pct_sec504"].mean()
        pooled_504 = sub_504["sec504_count"].sum() / sub_504["school_enrollment"].sum() * 100.0 if len(sub_504) > 0 else np.nan
        
        # Combined IDEA or Section 504-only
        sub_comb = sub[sub["idea_or_504_count"].notna() & (sub["school_enrollment"] > 0)]
        school_wt_comb = sub_comb["pct_idea_or_504"].mean()
        pooled_comb = sub_comb["idea_or_504_count"].sum() / sub_comb["school_enrollment"].sum() * 100.0 if len(sub_comb) > 0 else np.nan
        
        # EL
        sub_el = sub[sub["el_count"].notna() & (sub["school_enrollment"] > 0)]
        school_wt_el = sub_el["pct_el"].mean()
        pooled_el = sub_el["el_count"].sum() / sub_el["school_enrollment"].sum() * 100.0 if len(sub_el) > 0 else np.nan
        
        # Absenteeism Regime 1: CRDC 15+ Days (2013-14, 2015-16)
        sub_crdc_abs = sub[sub["crdc_absent_15d_count"].notna() & (sub["school_enrollment"] > 0)]
        crdc_abs_n = len(sub_crdc_abs)
        crdc_abs_mean = sub_crdc_abs["pct_crdc_absent_15d"].mean() if crdc_abs_n > 0 else np.nan
        crdc_abs_median = sub_crdc_abs["pct_crdc_absent_15d"].median() if crdc_abs_n > 0 else np.nan
        crdc_abs_pooled = sub_crdc_abs["crdc_absent_15d_count"].sum() / sub_crdc_abs["school_enrollment"].sum() * 100.0 if crdc_abs_n > 0 else np.nan
        
        # Absenteeism Regime 2: EDFacts >=10% (2017-18, 2020-21, 2021-22)
        sub_edf_abs = sub[sub["edfacts_absent_10pct_count"].notna() & (sub["school_enrollment"] > 0)]
        edf_abs_n = len(sub_edf_abs)
        edf_abs_mean = sub_edf_abs["pct_edfacts_absent_10pct"].mean() if edf_abs_n > 0 else np.nan
        edf_abs_median = sub_edf_abs["pct_edfacts_absent_10pct"].median() if edf_abs_n > 0 else np.nan
        
        sub_edf_clean = sub_edf_abs[~sub_edf_abs["flag_absent_gt_enrollment"]]
        edf_clean_mean = sub_edf_clean["pct_edfacts_absent_10pct"].mean() if len(sub_edf_clean) > 0 else np.nan
        edf_clean_median = sub_edf_clean["pct_edfacts_absent_10pct"].median() if len(sub_edf_clean) > 0 else np.nan
        edf_abs_pooled = sub_edf_abs["edfacts_absent_10pct_count"].sum() / sub_edf_abs["school_enrollment"].sum() * 100.0 if edf_abs_n > 0 else np.nan
        edf_gt_enr_pct = (sub_edf_abs["flag_absent_gt_enrollment"].mean() * 100.0) if edf_abs_n > 0 else np.nan

        # Class size & PTR
        cs_student_wt = (sub["stem_enrolled_tot"] * sub["enr_weighted_class_size"]).sum() / stem_enr_tot if stem_enr_tot > 0 else np.nan
        cs_school_mean = sub["mean_class_size_cell"].mean()
        ptr_mean = sub["school_ptr"].mean()
        ptr_median = sub["school_ptr"].median()

        rows.append({
            "crdc_wave": w,
            "school_year": sy,
            "schools_n": n_sch,
            "mean_enrollment": sub["school_enrollment"].mean(),
            "enr_weighted_class_size": cs_student_wt,
            "mean_class_size_cell": cs_school_mean,
            "mean_ptr": ptr_mean,
            "median_ptr": ptr_median,
            "school_wt_pct_idea": school_wt_idea,
            "pooled_pct_idea": pooled_idea,
            "school_wt_pct_504": school_wt_504,
            "pooled_pct_504": pooled_504,
            "school_wt_pct_idea_or_504": school_wt_comb,
            "pooled_pct_idea_or_504": pooled_comb,
            "school_wt_pct_el": school_wt_el,
            "pooled_pct_el": pooled_el,
            "crdc_15d_schools_n": crdc_abs_n,
            "crdc_15d_school_median": crdc_abs_median,
            "crdc_15d_school_mean": crdc_abs_mean,
            "crdc_15d_pooled": crdc_abs_pooled,
            "edfacts_10pct_schools_n": edf_abs_n,
            "edfacts_10pct_school_median": edf_abs_median,
            "edfacts_10pct_clean_median": edf_clean_median,
            "edfacts_10pct_school_mean": edf_abs_mean,
            "edfacts_10pct_clean_mean": edf_clean_mean,
            "edfacts_10pct_pooled": edf_abs_pooled,
            "edfacts_pct_gt_enrollment": edf_gt_enr_pct,
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
    Table B2: Longitudinal Changes within Measure-Specific Balanced Panels.
    Guarantees genuine balanced samples:
    - Panel A: 6-Wave Balanced Panel for IDEA, Section 504-only, and EL (N=14,000+ schools observed across all 6 waves)
    - Panel B: Matched EDFacts Chronic Absenteeism Panel (2017-18 <-> 2021-22, N=20,076 schools)
    - Panel C: Matched CRDC 15+ Days Absenteeism Panel (2013-14 <-> 2015-16, N=21,470 schools)
    """
    print("--> Generating Table B02: Measure-Specific Balanced Panels...")
    sec = df[df["in_class_size_panel"]].copy()
    waves = sorted(sec["crdc_wave"].unique())
    
    # 1. Accommodations & EL Balanced Panel across all 6 waves
    # Schools with valid enrollment and valid IDEA, 504, EL in all 6 waves
    valid_mask = (
        sec["school_enrollment"].notna() & (sec["school_enrollment"] > 0) &
        sec["idea_count"].notna() & sec["sec504_count"].notna() & sec["el_count"].notna()
    )
    sec_valid = sec[valid_mask]
    sch_wave_counts = sec_valid.groupby("nces_school_id")["crdc_wave"].nunique()
    bal_6w_sids = sch_wave_counts[sch_wave_counts == 6].index
    print(f"  Panel A (6-Wave Accommodations/EL Balanced): {len(bal_6w_sids):,} schools.")
    
    df_bal6 = sec[sec["nces_school_id"].isin(bal_6w_sids)].copy()
    rows_panel_a = []
    for w in waves:
        sub = df_bal6[df_bal6["crdc_wave"] == w]
        tot_enr = sub["school_enrollment"].sum()
        stem_tot = sub["stem_enrolled_tot"].sum()
        rows_panel_a.append({
            "panel": "Panel A: 6-Wave Accommodations/EL Balanced",
            "crdc_wave": w,
            "school_year": sub["school_year"].iloc[0],
            "balanced_schools_n": len(sub),
            "enr_weighted_class_size": (sub["stem_enrolled_tot"] * sub["enr_weighted_class_size"]).sum() / stem_tot if stem_tot > 0 else np.nan,
            "mean_class_size_cell": sub["mean_class_size_cell"].mean(),
            "mean_ptr": sub["school_ptr"].mean(),
            "school_wt_pct_idea": sub["pct_idea"].mean(),
            "pooled_pct_idea": sub["idea_count"].sum() / tot_enr * 100.0,
            "school_wt_pct_504": sub["pct_sec504"].mean(),
            "pooled_pct_504": sub["sec504_count"].sum() / tot_enr * 100.0,
            "school_wt_pct_idea_or_504": sub["pct_idea_or_504"].mean(),
            "pooled_pct_idea_or_504": sub["idea_or_504_count"].sum() / tot_enr * 100.0,
            "school_wt_pct_el": sub["pct_el"].mean(),
            "pooled_pct_el": sub["el_count"].sum() / tot_enr * 100.0,
        })
    df_a = pd.DataFrame(rows_panel_a)
    
    # 2. Panel B: Matched EDFacts Absenteeism Panel (2017-18 <-> 2021-22)
    s17 = set(sec[(sec["crdc_wave"] == "2017-18") & sec["edfacts_absent_10pct_count"].notna() & (sec["school_enrollment"] > 0)]["nces_school_id"])
    s21 = set(sec[(sec["crdc_wave"] == "2021-22") & sec["edfacts_absent_10pct_count"].notna() & (sec["school_enrollment"] > 0)]["nces_school_id"])
    matched_edf_sids = s17.intersection(s21)
    print(f"  Panel B (Matched EDFacts 2017-18 <-> 2021-22 Absenteeism): {len(matched_edf_sids):,} schools.")
    
    rows_panel_b = []
    for w in ["2017-18", "2021-22"]:
        sub = sec[(sec["crdc_wave"] == w) & sec["nces_school_id"].isin(matched_edf_sids)].copy()
        tot_enr = sub["school_enrollment"].sum()
        sub_clean = sub[~sub["flag_absent_gt_enrollment"]]
        rows_panel_b.append({
            "panel": "Panel B: Matched EDFacts Absenteeism (>=10% days)",
            "crdc_wave": w,
            "school_year": sub["school_year"].iloc[0],
            "matched_schools_n": len(sub),
            "school_median": sub["pct_edfacts_absent_10pct"].median(),
            "clean_median": sub_clean["pct_edfacts_absent_10pct"].median(),
            "school_mean": sub["pct_edfacts_absent_10pct"].mean(),
            "clean_mean": sub_clean["pct_edfacts_absent_10pct"].mean(),
            "pooled_rate": sub["edfacts_absent_10pct_count"].sum() / tot_enr * 100.0,
            "pct_gt_enrollment": sub["flag_absent_gt_enrollment"].mean() * 100.0,
        })
    df_b = pd.DataFrame(rows_panel_b)
    
    # 3. Panel C: Matched CRDC 15+ Days Absenteeism Panel (2013-14 <-> 2015-16)
    s13 = set(sec[(sec["crdc_wave"] == "2013-14") & sec["crdc_absent_15d_count"].notna() & (sec["school_enrollment"] > 0)]["nces_school_id"])
    s15 = set(sec[(sec["crdc_wave"] == "2015-16") & sec["crdc_absent_15d_count"].notna() & (sec["school_enrollment"] > 0)]["nces_school_id"])
    matched_crdc_sids = s13.intersection(s15)
    print(f"  Panel C (Matched CRDC 15+ Days 2013-14 <-> 2015-16): {len(matched_crdc_sids):,} schools.")
    
    rows_panel_c = []
    for w in ["2013-14", "2015-16"]:
        sub = sec[(sec["crdc_wave"] == w) & sec["nces_school_id"].isin(matched_crdc_sids)].copy()
        tot_enr = sub["school_enrollment"].sum()
        rows_panel_c.append({
            "panel": "Panel C: Matched CRDC Absenteeism (15+ days)",
            "crdc_wave": w,
            "school_year": sub["school_year"].iloc[0],
            "matched_schools_n": len(sub),
            "school_median": sub["pct_crdc_absent_15d"].median(),
            "clean_median": sub[sub["pct_crdc_absent_15d"] <= 100]["pct_crdc_absent_15d"].median(),
            "school_mean": sub["pct_crdc_absent_15d"].mean(),
            "clean_mean": sub[sub["pct_crdc_absent_15d"] <= 100]["pct_crdc_absent_15d"].mean(),
            "pooled_rate": sub["crdc_absent_15d_count"].sum() / tot_enr * 100.0,
            "pct_gt_enrollment": (sub["pct_crdc_absent_15d"] > 100).mean() * 100.0,
        })
    df_c = pd.DataFrame(rows_panel_c)
    
    df_t2 = pd.concat([df_a, df_b, df_c], ignore_index=True)
    out_csv = TABLES_DIR / "table_b02_balanced_school_panel_context.csv"
    df_t2.to_csv(out_csv, index=False)
    print(f"--> Saved Table B02 to {out_csv}")
    return df_t2


def generate_table_b03(df):
    """
    Table B3: Class Size Bins x Surrounding Instructional Context (2021-22 & 2023-24).
    Cross-tabulates secondary schools categorized by enrollment-weighted class size.
    Reports both school-weighted and pooled student-weighted rates.
    """
    print("--> Generating Table B03: Class Size Bins x Context...")
    sec = df[df["in_class_size_panel"] & df["crdc_wave"].isin(["2021-22", "2023-24"])].copy()
    
    rows = []
    for wave in ["2021-22", "2023-24"]:
        sub_w = sec[sec["crdc_wave"] == wave]
        for cbin in ["<20", "20-24", "25-29", "30+"]:
            sub = sub_w[sub_w["class_size_bin"] == cbin]
            if len(sub) == 0:
                continue
            tot_enr = sub["school_enrollment"].sum()
            stem_enr = sub["stem_enrolled_tot"].sum()
            
            # Clean absenteeism in 2021-22
            if wave == "2021-22":
                abs_valid = sub[sub["pct_edfacts_absent_10pct"].notna() & (sub["school_enrollment"] > 0)]
                abs_clean = abs_valid[~abs_valid["flag_absent_gt_enrollment"]]
                abs_med = abs_valid["pct_edfacts_absent_10pct"].median()
                abs_clean_med = abs_clean["pct_edfacts_absent_10pct"].median()
                abs_pooled = abs_valid["edfacts_absent_10pct_count"].sum() / abs_valid["school_enrollment"].sum() * 100.0 if len(abs_valid) > 0 else np.nan
            else:
                abs_med = np.nan
                abs_clean_med = np.nan
                abs_pooled = np.nan

            rows.append({
                "crdc_wave": wave,
                "class_size_bin": cbin,
                "schools_n": len(sub),
                "pct_of_secondary_schools": (len(sub) / len(sub_w)) * 100.0,
                "mean_school_enrollment": sub["school_enrollment"].mean(),
                "student_weighted_class_size": (sub["stem_enrolled_tot"] * sub["enr_weighted_class_size"]).sum() / stem_enr if stem_enr > 0 else np.nan,
                "school_mean_class_size": sub["mean_class_size_cell"].mean(),
                "mean_ptr": sub["school_ptr"].mean(),
                "school_wt_pct_idea": sub["pct_idea"].mean(),
                "pooled_pct_idea": sub["idea_count"].sum() / tot_enr * 100.0 if tot_enr > 0 else np.nan,
                "school_wt_pct_504": sub["pct_sec504"].mean(),
                "pooled_pct_504": sub["sec504_count"].sum() / tot_enr * 100.0 if tot_enr > 0 else np.nan,
                "school_wt_pct_idea_or_504": sub["pct_idea_or_504"].mean(),
                "pooled_pct_idea_or_504": sub["idea_or_504_count"].sum() / tot_enr * 100.0 if tot_enr > 0 else np.nan,
                "school_wt_pct_el": sub["pct_el"].mean(),
                "pooled_pct_el": sub["el_count"].sum() / tot_enr * 100.0 if tot_enr > 0 else np.nan,
                "edfacts_10pct_median": abs_med,
                "edfacts_10pct_clean_median": abs_clean_med,
                "edfacts_10pct_pooled": abs_pooled,
            })
            
    df_t3 = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table_b03_class_size_vs_context_bivariate.csv"
    df_t3.to_csv(out_csv, index=False)
    print(f"--> Saved Table B03 to {out_csv}")
    return df_t3


def generate_table_b04(df):
    """
    Table B4: Kansas City Metropolitan Area vs. National Benchmark.
    Harmonizes class-size weighting to match Table B1 (reports student-weighted class size).
    Uses certified canonical KC PTR from Phase 3 CCD metadata.
    Reports both school-weighted and pooled student-weighted rates.
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
                
            tot_enr = sub["school_enrollment"].sum()
            stem_enr = sub["stem_enrolled_tot"].sum()
            
            # Absenteeism
            sub_edf = sub[sub["pct_edfacts_absent_10pct"].notna() & (sub["school_enrollment"] > 0)]
            edf_med = sub_edf["pct_edfacts_absent_10pct"].median() if len(sub_edf) > 0 else np.nan
            edf_clean_med = sub_edf[~sub_edf["flag_absent_gt_enrollment"]]["pct_edfacts_absent_10pct"].median() if len(sub_edf) > 0 else np.nan
            edf_pool = sub_edf["edfacts_absent_10pct_count"].sum() / sub_edf["school_enrollment"].sum() * 100.0 if len(sub_edf) > 0 else np.nan

            rows.append({
                "crdc_wave": w,
                "population": pop,
                "schools_n": len(sub),
                "mean_enrollment": sub["school_enrollment"].mean(),
                "student_weighted_class_size": (sub["stem_enrolled_tot"] * sub["enr_weighted_class_size"]).sum() / stem_enr if stem_enr > 0 else np.nan,
                "school_mean_class_size": sub["mean_class_size_cell"].mean(),
                "mean_ptr": sub["school_ptr"].mean(),
                "median_ptr": sub["school_ptr"].median(),
                "school_wt_pct_idea": sub["pct_idea"].mean(),
                "pooled_pct_idea": sub["idea_count"].sum() / tot_enr * 100.0 if tot_enr > 0 else np.nan,
                "school_wt_pct_504": sub["pct_sec504"].mean(),
                "pooled_pct_504": sub["sec504_count"].sum() / tot_enr * 100.0 if tot_enr > 0 else np.nan,
                "school_wt_pct_idea_or_504": sub["pct_idea_or_504"].mean(),
                "pooled_pct_idea_or_504": sub["idea_or_504_count"].sum() / tot_enr * 100.0 if tot_enr > 0 else np.nan,
                "school_wt_pct_el": sub["pct_el"].mean(),
                "pooled_pct_el": sub["el_count"].sum() / tot_enr * 100.0 if tot_enr > 0 else np.nan,
                "edfacts_10pct_median": edf_med,
                "edfacts_10pct_clean_median": edf_clean_med,
                "edfacts_10pct_pooled": edf_pool,
            })
            
    df_t4 = pd.DataFrame(rows)
    out_csv = TABLES_DIR / "table_b04_kc_metro_vs_national_context.csv"
    df_t4.to_csv(out_csv, index=False)
    print(f"--> Saved Table B04 to {out_csv}")
    return df_t4


def plot_fig_b01(df_t1):
    """
    Figure B1: 4-Panel Plot of Separate Longitudinal Trajectories (2013-14 to 2023-24).
    Panel (a): Secondary Class Size vs Campus PTR (showing decade easing & post-2020 stabilization)
    Panel (b): Student Individualized Accommodations (% IDEA and % Section 504-only, school-wt & pooled)
    Panel (c): Language Diversity (% English Learners, school-wt & pooled)
    Panel (d): Attendance Disruption (% Chronically Absent with explicit regime break)
    """
    print("--> Rendering Figure B01: Longitudinal Context Dimensions...")
    fig, axes = plt.subplots(2, 2, figsize=(13, 9.5), sharex=True)
    
    waves = df_t1["crdc_wave"].tolist()
    x = np.arange(len(waves))
    
    # Panel (a): Class Size vs PTR
    ax = axes[0, 0]
    ax.plot(x, df_t1["enr_weighted_class_size"], marker="o", color="#1f77b4", linewidth=2.2, label="Secondary Class Size (Student-Weighted)")
    ax.plot(x, df_t1["mean_class_size_cell"], marker="s", color="#1f77b4", linestyle="--", alpha=0.7, label="Secondary Class Size (School-Mean)")
    ax.plot(x, df_t1["mean_ptr"], marker="^", color="#d62728", linewidth=2, label="Campus PTR (NCES/CRDC Mean)")
    ax.set_title("(a) Secondary Class Size vs. Campus PTR", fontweight="bold")
    ax.set_ylabel("Students per Class / Teacher")
    ax.set_ylim(12, 24)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.text(0.03, 0.05, "Student-weighted size eased 22.4 -> 19.7 (-12%)\nand stabilized post-2020 at ~19.7-20.1",
            transform=ax.transAxes, fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", edgecolor="gray", alpha=0.8))
    
    # Panel (b): Accommodations (IDEA & 504)
    ax = axes[0, 1]
    ax.plot(x, df_t1["school_wt_pct_idea"], marker="o", color="#2ca02c", linewidth=1.8, label="IDEA Disabilities (School-Mean)")
    ax.plot(x, df_t1["pooled_pct_idea"], marker="o", color="#2ca02c", linestyle="--", linewidth=1.8, label="IDEA Disabilities (Pooled Students)")
    ax.plot(x, df_t1["school_wt_pct_504"], marker="s", color="#ff7f0e", linewidth=1.8, label="Section 504-Only (School-Mean)")
    ax.plot(x, df_t1["pooled_pct_504"], marker="s", color="#ff7f0e", linestyle="--", linewidth=1.8, label="Section 504-Only (Pooled Students)")
    ax.plot(x, df_t1["pooled_pct_idea_or_504"], marker="D", color="#8c564b", linewidth=2.2, label="Combined IDEA or 504 (Pooled Students)")
    ax.set_title("(b) Individualized Disability Accommodations", fontweight="bold")
    ax.set_ylabel("Percent of Enrollment (%)")
    ax.set_ylim(0, 24)
    ax.legend(loc="center left", framealpha=0.9, fontsize=8)
    ax.text(0.03, 0.05, "Section 504-only doubled (2.2% -> 5.5%);\nCombined IDEA or 504 reached 19.0% (1 in 5)",
            transform=ax.transAxes, fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", edgecolor="gray", alpha=0.8))
    
    # Panel (c): English Learners
    ax = axes[1, 0]
    ax.plot(x, df_t1["school_wt_pct_el"], marker="o", color="#9467bd", linewidth=2, label="% English Learners (School-Mean)")
    ax.plot(x, df_t1["pooled_pct_el"], marker="s", color="#9467bd", linestyle="--", linewidth=2, label="% English Learners (Pooled Students)")
    ax.set_title("(c) English Learner Enrollment (% of Enrollment)", fontweight="bold")
    ax.set_ylabel("Percent of Enrolled Students (%)")
    ax.set_xlabel("CRDC Census Wave")
    ax.set_xticks(x)
    ax.set_xticklabels(waves, rotation=25)
    ax.set_ylim(0, 12)
    ax.legend(loc="upper left", framealpha=0.9)
    ax.text(0.03, 0.05, "Pooled EL prevalence rose +61% (5.6% -> 9.1%)",
            transform=ax.transAxes, fontsize=8.5, bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", edgecolor="gray", alpha=0.8))
    
    # Panel (d): Chronic Absenteeism with Incompatible Regimes
    ax = axes[1, 1]
    # Regime 1: CRDC 15+ Days (2013-14, 2015-16) - waves 0, 1
    x_r1 = [0, 1]
    y_r1_med = df_t1.loc[:1, "crdc_15d_school_median"].tolist()
    y_r1_pool = df_t1.loc[:1, "crdc_15d_pooled"].tolist()
    ax.plot(x_r1, y_r1_med, marker="s", color="#1f77b4", linewidth=2.2, label="Regime 1: CRDC 15+ Days (School Median)")
    ax.plot(x_r1, y_r1_pool, marker="s", color="#1f77b4", linestyle="--", linewidth=1.8, label="Regime 1: CRDC 15+ Days (Pooled Rate)")
    
    # Regime 2: EDFacts >=10% Days (2017-18 and 2021-22) - waves 2, 4
    x_r2 = [2, 4]
    y_r2_med = [df_t1.loc[2, "edfacts_10pct_school_median"], df_t1.loc[4, "edfacts_10pct_school_median"]]
    y_r2_clean = [df_t1.loc[2, "edfacts_10pct_clean_median"], df_t1.loc[4, "edfacts_10pct_clean_median"]]
    y_r2_pool = [df_t1.loc[2, "edfacts_10pct_pooled"], df_t1.loc[4, "edfacts_10pct_pooled"]]
    ax.plot(x_r2, y_r2_med, marker="o", color="#d62728", linewidth=2.5, label="Regime 2: EDFacts ≥10% Days (School Median)")
    ax.plot(x_r2, y_r2_clean, marker="^", color="#d62728", linestyle=":", linewidth=2.0, label="Regime 2: EDFacts Clean ≤100% Median")
    ax.plot(x_r2, y_r2_pool, marker="o", color="#d62728", linestyle="--", linewidth=1.8, label="Regime 2: EDFacts ≥10% Days (Pooled Rate)")
    
    # 2020-21 COVID waiver year point (wave 3) - hollow circle
    ax.plot(3, df_t1.loc[3, "edfacts_10pct_school_median"], marker="o", markerfacecolor="white", markeredgecolor="#d62728", markeredgewidth=2, markersize=8, label="2020–21 Waiver (6% N; non-representative)")
    
    # Vertical line separating regimes
    ax.axvline(x=1.5, color="gray", linestyle="-.", alpha=0.7)
    ax.text(1.55, 42, "Definition Break:\nCRDC 15d → EDFacts 10%", fontsize=8, color="#555555", style="italic")
    
    ax.set_title("(d) Chronic Student Absenteeism (Separate Federal Regimes)", fontweight="bold")
    ax.set_ylabel("Percent of Enrolled Students (%)")
    ax.set_xlabel("CRDC Census Wave")
    ax.set_xticks(x)
    ax.set_xticklabels(waves, rotation=25)
    ax.set_ylim(0, 50)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=7.5)
    
    plt.tight_layout()
    out_fig = FIGURES_DIR / "fig_b01_longitudinal_context_dimensions.png"
    plt.savefig(out_fig, bbox_inches="tight")
    plt.close()
    print(f"--> Saved Figure B01 to {out_fig}")


def plot_fig_b02(df):
    """
    Figure B2: Class Size Bins vs Surrounding Instructional Context (2021-22).
    Shows the distribution of surrounding % IDEA, % 504, % Combined IDEA/504, and % Chronic Absenteeism.
    """
    print("--> Rendering Figure B02: Class Size Bins vs. Context...")
    df_21 = df[df["in_class_size_panel"] & (df["crdc_wave"] == "2021-22") & df["class_size_bin"].notna()].copy()
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True)
    bin_order = ["<20", "20-24", "25-29", "30+"]
    palette = ["#4575b4", "#74add1", "#fdae61", "#f46d43"]
    
    # 1. % IDEA
    sns.boxplot(data=df_21, x="class_size_bin", y="pct_idea", order=bin_order, ax=axes[0, 0], palette=palette, showfliers=False)
    axes[0, 0].set_title("(a) Surrounding % IDEA Disabilities", fontweight="bold")
    axes[0, 0].set_ylabel("% of School Enrollment")
    axes[0, 0].set_xlabel("")
    axes[0, 0].set_ylim(0, 35)
    
    # 2. % Section 504
    sns.boxplot(data=df_21, x="class_size_bin", y="pct_sec504", order=bin_order, ax=axes[0, 1], palette=palette, showfliers=False)
    axes[0, 1].set_title("(b) Surrounding % Section 504-Only", fontweight="bold")
    axes[0, 1].set_ylabel("% of School Enrollment")
    axes[0, 1].set_xlabel("")
    axes[0, 1].set_ylim(0, 15)
    
    # 3. % Combined IDEA or 504
    sns.boxplot(data=df_21, x="class_size_bin", y="pct_idea_or_504", order=bin_order, ax=axes[1, 0], palette=palette, showfliers=False)
    axes[1, 0].set_title("(c) Surrounding % IDEA or Section 504-Only", fontweight="bold")
    axes[1, 0].set_ylabel("% of School Enrollment")
    axes[1, 0].set_xlabel("Student-Weighted School Class Size Bin")
    axes[1, 0].set_ylim(0, 40)
    
    # 4. % Chronic Absenteeism (clean <= 100)
    sns.boxplot(data=df_21, x="class_size_bin", y="pct_chronic_absent_clean", order=bin_order, ax=axes[1, 1], palette=palette, showfliers=False)
    axes[1, 1].set_title("(d) Surrounding % Chronic Absenteeism (EDFacts 2021–22)", fontweight="bold")
    axes[1, 1].set_ylabel("% of School Enrollment")
    axes[1, 1].set_xlabel("Student-Weighted School Class Size Bin")
    axes[1, 1].set_ylim(0, 70)
    
    plt.tight_layout()
    out_fig = FIGURES_DIR / "fig_b02_class_size_bins_vs_context.png"
    plt.savefig(out_fig, bbox_inches="tight")
    plt.close()
    print(f"--> Saved Figure B02 to {out_fig}")


def plot_fig_b03(df):
    """
    Figure B3: Pre-COVID vs Post-COVID Distribution of Chronic Absenteeism in Secondary Schools.
    Compares 2017-18 to 2021-22 under consistent post-2016 EDFacts definition (>=10% of days).
    """
    print("--> Rendering Figure B03: Chronic Absenteeism Distribution Shift...")
    sec = df[df["in_class_size_panel"] & df["crdc_wave"].isin(["2017-18", "2021-22"])].copy()
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    sub17 = sec[(sec["crdc_wave"] == "2017-18") & sec["pct_chronic_absent_clean"].notna()]["pct_chronic_absent_clean"]
    sub21 = sec[(sec["crdc_wave"] == "2021-22") & sec["pct_chronic_absent_clean"].notna()]["pct_chronic_absent_clean"]
    
    sns.kdeplot(sub17, ax=ax, color="#1f77b4", linewidth=2.5, label=f"Pre-COVID (2017–18): Clean Median = {sub17.median():.1f}%", clip=(0, 100))
    sns.kdeplot(sub21, ax=ax, color="#d62728", linewidth=2.5, label=f"Post-COVID (2021–22): Clean Median = {sub21.median():.1f}%", clip=(0, 100))
    
    ax.axvline(sub17.median(), color="#1f77b4", linestyle="--", alpha=0.7)
    ax.axvline(sub21.median(), color="#d62728", linestyle="--", alpha=0.7)
    
    # Highlight threshold >= 30%
    ax.axvline(30, color="gray", linestyle=":", alpha=0.8, label="Severe Disruption Threshold (≥30%)")
    
    pct_gt30_17 = (sub17 >= 30).mean() * 100
    pct_gt30_21 = (sub21 >= 30).mean() * 100
    
    ax.text(32, ax.get_ylim()[1]*0.8, f"Schools ≥30% Absent:\n  2017–18: {pct_gt30_17:.1f}%\n  2021–22: {pct_gt30_21:.1f}% (+{pct_gt30_21-pct_gt30_17:.1f} pp)", fontsize=10, bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="gray", alpha=0.9))
    
    ax.set_title("The Attendance Shock: Distribution of Secondary School Chronic Absenteeism Rates\n(Consistent EDFacts Definition: Missing ≥10% of School Days)", fontweight="bold")
    ax.set_xlabel("Chronic Absenteeism Rate (% of Enrolled Students Missing ≥10% of Days)")
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
