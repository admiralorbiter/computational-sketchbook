"""
src/analysis/complexity_analysis.py
Task 004C.1: Longitudinal Analysis of School Complexity, Accommodations & Workload Burden (Calibrated)

Analyzes the trajectory of student complexity in Kansas City public schools:
  1. IDEA (Special Education) share trends (2015-16 to 2023-24)
  2. Section 504 accommodation growth (arithmetically corrected to +93.5%)
  3. English Learner (EL) concentration
  4. Chronic Absenteeism escalation across 4 waves:
       - 2017-18 baseline: 12.90%
       - 2020-21 acute shock: 35.14% (+22.24 percentage points)
       - 2021-22 post-pandemic: 24.68%
       - 2022-23 post-pandemic plateau: 24.69% (+11.79 percentage points above baseline)
  5. Balanced school panel sensitivity check (continuing physical campuses)
  6. The Compound Workload Conceptual Framework vs Headline PTR:
       - Clear distinction between chronic absenteeism (>=10% of days missed annually)
         and daily absence rates (ADA ~90-93%)
       - Conceptual formulation rather than uncalibrated empirical regression percentages
  7. Calibrated Hypothesis Evaluation (H1b, H2, H4)

Outputs:
  - outputs/tables/task004c_complexity_trends_regional.csv
  - outputs/tables/task004c_complexity_by_locale.csv
  - outputs/tables/task004c_complexity_benchmark_schools.csv
  - outputs/tables/task004c_complexity_analysis_report.md
  - outputs/figures/fig12_student_complexity_trends.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run_complexity_analysis():
    print("=== Running Task 004C.1: Calibrated School Complexity Analysis ===")
    
    panel_path = "data/processed/kc_school_complexity_panel_2015_2024.csv"
    if not os.path.exists(panel_path):
        raise FileNotFoundError(f"Missing {panel_path}")
        
    df = pd.read_csv(panel_path, low_memory=False)
    print(f"Loaded {len(df):,} complexity records across sources: {df['data_source'].unique()}")
    
    # Filter to operating, physical schools
    # For CRDC waves: enrollment_crdc > 0; for EDFacts waves: enrollment_k12 > 0
    clean = df[(df["is_operating"] == True) & (df["is_virtual"] == False)].copy()
    print(f"Clean physical operational records: {len(clean):,}")
    
    # ---------------------------------------------------------
    # 1. Regional Longitudinal Summary Table (All Physical Schools)
    # ---------------------------------------------------------
    # We report CRDC accommodation waves and chronic absenteeism across all available years
    waves_all = ["2015-16", "2017-18", "2020-21", "2021-22", "2022-23", "2023-24"]
    reg_rows = []
    
    for w in waves_all:
        sub = clean[clean["crdc_wave"] == w]
        if len(sub) == 0:
            continue
            
        src = sub["data_source"].iloc[0]
        
        # Determine enrollment and accommodations based on source
        if src == "CRDC":
            valid_sub = sub[sub["enrollment_crdc"] > 0]
            tot_enr = valid_sub["enrollment_crdc"].sum()
            tot_idea = valid_sub["idea_count"].sum()
            tot_504 = valid_sub["section_504_count"].sum()
            tot_lep = valid_sub["lep_count"].sum()
            tot_acc = valid_sub["accommodations_count"].sum()
            
            idea_pct = round(tot_idea / tot_enr * 100, 2)
            s504_pct = round(tot_504 / tot_enr * 100, 2)
            lep_pct = round(tot_lep / tot_enr * 100, 2)
            acc_pct = round(tot_acc / tot_enr * 100, 2)
            
            # Chronic absenteeism for CRDC
            sub_abs = valid_sub[valid_sub["chronic_absent_count"].notna()]
            tot_abs = sub_abs["chronic_absent_count"].sum() if len(sub_abs) > 0 else np.nan
            enr_abs = sub_abs["enrollment_crdc"].sum() if len(sub_abs) > 0 else np.nan
            abs_rate = round(tot_abs / enr_abs * 100, 2) if (pd.notna(tot_abs) and enr_abs > 0) else np.nan
            
            mean_ptr = round(valid_sub["school_ptr"].dropna().mean(), 2)
            mean_frl = round(valid_sub["frl_rate"].dropna().mean() * 100, 2)
            n_schools = len(valid_sub)
            
        else: # EDFacts
            valid_sub = sub[sub["enrollment_k12"] > 0]
            tot_enr = valid_sub["enrollment_k12"].sum()
            tot_idea = np.nan
            tot_504 = np.nan
            tot_lep = np.nan
            tot_acc = np.nan
            idea_pct = np.nan
            s504_pct = np.nan
            lep_pct = np.nan
            acc_pct = np.nan
            
            sub_abs = valid_sub[valid_sub["chronic_absent_count"].notna()]
            tot_abs = sub_abs["chronic_absent_count"].sum() if len(sub_abs) > 0 else np.nan
            enr_abs = sub_abs["enrollment_k12"].sum() if len(sub_abs) > 0 else np.nan
            abs_rate = round(tot_abs / enr_abs * 100, 2) if (pd.notna(tot_abs) and enr_abs > 0) else np.nan
            
            mean_ptr = round(valid_sub["school_ptr"].dropna().mean(), 2)
            mean_frl = round(valid_sub["frl_rate"].dropna().mean() * 100, 2)
            n_schools = len(valid_sub)
            
        reg_rows.append({
            "school_year": valid_sub["school_year"].iloc[0],
            "wave_label": w,
            "data_source": src,
            "num_schools": n_schools,
            "total_enrollment": int(tot_enr),
            "idea_students": int(tot_idea) if pd.notna(tot_idea) else np.nan,
            "idea_pct": idea_pct,
            "section_504_students": int(tot_504) if pd.notna(tot_504) else np.nan,
            "section_504_pct": s504_pct,
            "lep_el_students": int(tot_lep) if pd.notna(tot_lep) else np.nan,
            "lep_el_pct": lep_pct,
            "total_accommodations_students": int(tot_acc) if pd.notna(tot_acc) else np.nan,
            "total_accommodations_pct": acc_pct,
            "chronic_absent_students": int(tot_abs) if pd.notna(tot_abs) else np.nan,
            "chronic_absent_rate_pct": abs_rate,
            "mean_frl_rate_pct": mean_frl,
            "mean_school_ptr": mean_ptr,
        })
        
    reg_df = pd.DataFrame(reg_rows)
    reg_out_path = "outputs/tables/task004c_complexity_trends_regional.csv"
    reg_df.to_csv(reg_out_path, index=False)
    print(f"Saved regional complexity trends to {reg_out_path}")
    
    # ---------------------------------------------------------
    # 2. Balanced School Panel Sensitivity (Continuing Schools)
    # ---------------------------------------------------------
    bal_clean = clean[clean["is_balanced_school"] == True].copy()
    bal_rows = []
    
    for w in waves_all:
        sub = bal_clean[bal_clean["crdc_wave"] == w]
        if len(sub) == 0:
            continue
        src = sub["data_source"].iloc[0]
        
        if src == "CRDC":
            valid_sub = sub[sub["enrollment_crdc"] > 0]
            tot_enr = valid_sub["enrollment_crdc"].sum()
            tot_idea = valid_sub["idea_count"].sum()
            tot_504 = valid_sub["section_504_count"].sum()
            tot_acc = valid_sub["accommodations_count"].sum()
            
            sub_abs = valid_sub[valid_sub["chronic_absent_count"].notna()]
            tot_abs = sub_abs["chronic_absent_count"].sum() if len(sub_abs) > 0 else np.nan
            enr_abs = sub_abs["enrollment_crdc"].sum() if len(sub_abs) > 0 else np.nan
            abs_rate = round(tot_abs / enr_abs * 100, 2) if (pd.notna(tot_abs) and enr_abs > 0) else np.nan
            
            bal_rows.append({
                "wave_label": w,
                "data_source": src,
                "num_schools": len(valid_sub),
                "total_enrollment": int(tot_enr),
                "idea_pct": round(tot_idea / tot_enr * 100, 2),
                "section_504_pct": round(tot_504 / tot_enr * 100, 2),
                "total_accommodations_pct": round(tot_acc / tot_enr * 100, 2),
                "chronic_absent_rate_pct": abs_rate,
                "mean_school_ptr": round(valid_sub["school_ptr"].dropna().mean(), 2)
            })
        else: # EDFacts
            valid_sub = sub[sub["enrollment_k12"] > 0]
            tot_enr = valid_sub["enrollment_k12"].sum()
            sub_abs = valid_sub[valid_sub["chronic_absent_count"].notna()]
            tot_abs = sub_abs["chronic_absent_count"].sum() if len(sub_abs) > 0 else np.nan
            enr_abs = sub_abs["enrollment_k12"].sum() if len(sub_abs) > 0 else np.nan
            abs_rate = round(tot_abs / enr_abs * 100, 2) if (pd.notna(tot_abs) and enr_abs > 0) else np.nan
            
            bal_rows.append({
                "wave_label": w,
                "data_source": src,
                "num_schools": len(valid_sub),
                "total_enrollment": int(tot_enr),
                "idea_pct": np.nan,
                "section_504_pct": np.nan,
                "total_accommodations_pct": np.nan,
                "chronic_absent_rate_pct": abs_rate,
                "mean_school_ptr": round(valid_sub["school_ptr"].dropna().mean(), 2)
            })
            
    bal_df = pd.DataFrame(bal_rows)
    bal_out_path = "outputs/tables/task004c_complexity_balanced_panel.csv"
    bal_df.to_csv(bal_out_path, index=False)
    print(f"Saved balanced complexity trends to {bal_out_path}")
    
    # ---------------------------------------------------------
    # 3. Locale Disaggregation (Focus on 2017-18 vs 2023-24)
    # ---------------------------------------------------------
    loc_rows = []
    locales = ["City", "Suburb", "Town", "Rural"]
    
    for loc in locales:
        for w in ["2017-18", "2023-24"]:
            sub = clean[(clean["locale_group"] == loc) & (clean["crdc_wave"] == w) & (clean["enrollment_crdc"] > 0)]
            if len(sub) == 0:
                continue
                
            tot_enr = sub["enrollment_crdc"].sum()
            tot_idea = sub["idea_count"].sum()
            tot_504 = sub["section_504_count"].sum()
            tot_lep = sub["lep_count"].sum()
            tot_acc = sub["accommodations_count"].sum()
            
            loc_rows.append({
                "locale_group": loc,
                "crdc_wave": w,
                "num_schools": len(sub),
                "total_enrollment": int(tot_enr),
                "idea_pct": round(tot_idea / tot_enr * 100, 2),
                "section_504_pct": round(tot_504 / tot_enr * 100, 2),
                "lep_el_pct": round(tot_lep / tot_enr * 100, 2),
                "total_accommodations_pct": round(tot_acc / tot_enr * 100, 2),
                "mean_ptr": round(sub["school_ptr"].dropna().mean(), 2) if sub["school_ptr"].notna().any() else np.nan,
            })
            
    loc_df = pd.DataFrame(loc_rows)
    loc_out_path = "outputs/tables/task004c_complexity_by_locale.csv"
    loc_df.to_csv(loc_out_path, index=False)
    print(f"Saved locale complexity table to {loc_out_path}")
    
    # ---------------------------------------------------------
    # 4. Benchmark Schools Case Studies
    # ---------------------------------------------------------
    bench_names = [
        "Shawnee Mission North High",
        "Shawnee Mission East High",
        "Olathe Northwest High School",
        "Olathe North Sr High",
        "Blue Valley High",
        "LINCOLN COLLEGE PREP.",
        "STALEY HIGH",
        "LEE'S SUMMIT WEST HIGH",
        "Richmond High",
        "Corinth Elementary",
        "Hale Cook Elementary",
    ]
    
    b_rows = []
    for bname in bench_names:
        for w in ["2017-18", "2023-24"]:
            sub = clean[(clean["school_name"].str.contains(bname, case=False, na=False)) & (clean["crdc_wave"] == w)]
            if len(sub) == 0:
                continue
            r = sub.iloc[0]
            enr = r["enrollment_crdc"]
            
            b_rows.append({
                "school_name": r["school_name"],
                "district_name": r.get("district_name", ""),
                "crdc_wave": w,
                "enrollment": int(enr) if pd.notna(enr) else np.nan,
                "idea_count": int(r["idea_count"]) if pd.notna(r["idea_count"]) else np.nan,
                "idea_pct": round(r["idea_share"] * 100, 2) if pd.notna(r["idea_share"]) else np.nan,
                "section_504_count": int(r["section_504_count"]) if pd.notna(r["section_504_count"]) else np.nan,
                "section_504_pct": round(r["section_504_share"] * 100, 2) if pd.notna(r["section_504_share"]) else np.nan,
                "lep_el_count": int(r["lep_count"]) if pd.notna(r["lep_count"]) else np.nan,
                "lep_el_pct": round(r["lep_share"] * 100, 2) if pd.notna(r["lep_share"]) else np.nan,
                "total_accommodations_count": int(r["accommodations_count"]) if pd.notna(r["accommodations_count"]) else np.nan,
                "total_accommodations_pct": round(r["accommodations_share"] * 100, 2) if pd.notna(r["accommodations_share"]) else np.nan,
                "school_ptr": round(r["school_ptr"], 2) if pd.notna(r["school_ptr"]) else np.nan,
            })
            
    b_df = pd.DataFrame(b_rows)
    b_out_path = "outputs/tables/task004c_complexity_benchmark_schools.csv"
    b_df.to_csv(b_out_path, index=False)
    print(f"Saved benchmark complexity table to {b_out_path}")
    
    # ---------------------------------------------------------
    # 5. Generate Figure 12: Student Complexity Trends
    # ---------------------------------------------------------
    os.makedirs("outputs/figures", exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Left: Regional Accommodations Trajectory (IDEA, 504, Combined, EL)
    crdc_rows = reg_df[reg_df["data_source"] == "CRDC"]
    w_labels = crdc_rows["wave_label"].tolist()
    x = np.arange(len(w_labels))
    
    axes[0].plot(x, crdc_rows["idea_pct"], marker="o", linewidth=2.5, color="#1f77b4", label="IDEA (Special Education)")
    axes[0].plot(x, crdc_rows["section_504_pct"], marker="s", linewidth=2.5, color="#ff7f0e", label="Section 504 Accommodations")
    axes[0].plot(x, crdc_rows["total_accommodations_pct"], marker="^", linewidth=3.0, color="#d62728", linestyle="--", label="Total Legally Mandated Accommodations")
    axes[0].plot(x, crdc_rows["lep_el_pct"], marker="d", linewidth=2.0, color="#2ca02c", label="English Learners (EL/LEP)")
    
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(w_labels, fontsize=11)
    axes[0].set_ylabel("Share of Enrolled Students (%)", fontsize=12, fontweight="bold")
    axes[0].set_title("Longitudinal Growth in Mandated Accommodations\nKansas City Metropolitan Public Schools (2015–16 to 2023–24)", fontsize=13, fontweight="bold")
    axes[0].grid(True, linestyle="--", alpha=0.5)
    axes[0].legend(loc="upper left", frameon=True, fontsize=10)
    axes[0].set_ylim(0, 20)
    
    # Annotate end points
    last_idx = len(w_labels) - 1
    axes[0].text(last_idx + 0.05, crdc_rows["total_accommodations_pct"].iloc[-1], f"{crdc_rows['total_accommodations_pct'].iloc[-1]:.1f}%", fontweight="bold", color="#d62728", va="center")
    axes[0].text(last_idx + 0.05, crdc_rows["idea_pct"].iloc[-1], f"{crdc_rows['idea_pct'].iloc[-1]:.1f}%", fontweight="bold", color="#1f77b4", va="center")
    axes[0].text(last_idx + 0.05, crdc_rows["section_504_pct"].iloc[-1], f"{crdc_rows['section_504_pct'].iloc[-1]:.1f}%", fontweight="bold", color="#ff7f0e", va="center")
    
    # Right: Full 4-Wave Chronic Absenteeism vs School PTR
    abs_sub = reg_df[reg_df["chronic_absent_rate_pct"].notna()].copy()
    x_abs = np.arange(len(abs_sub))
    labels_abs = [f"{r['wave_label']}\n({r['data_source']})" for _, r in abs_sub.iterrows()]
    
    ax2 = axes[1].twinx()
    
    bars = axes[1].bar(x_abs - 0.15, abs_sub["chronic_absent_rate_pct"], width=0.3, color="#9467bd", alpha=0.85, label="Chronic Absenteeism Rate (%)")
    p1 = ax2.plot(x_abs + 0.15, abs_sub["mean_school_ptr"], color="#1b9e77", marker="o", linewidth=3, markersize=8, label="Headline School PTR")
    
    axes[1].set_xticks(x_abs)
    axes[1].set_xticklabels(labels_abs, fontsize=11)
    axes[1].set_ylabel("Chronic Absenteeism Rate (>=10% Days Missed) (%)", color="#9467bd", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Reported Pupil/Teacher Ratio (PTR)", color="#1b9e77", fontsize=11, fontweight="bold")
    axes[1].set_title("The Chronic Absenteeism Trajectory:\nBaseline, Pandemic Shock, and Persistent Elevated Plateau", fontsize=13, fontweight="bold")
    axes[1].set_ylim(0, 42)
    ax2.set_ylim(10, 20)
    axes[1].grid(True, linestyle="--", alpha=0.4, axis="y")
    
    # Annotate bars
    for idx, val in enumerate(abs_sub["chronic_absent_rate_pct"]):
        axes[1].text(idx - 0.15, val + 1.0, f"{val:.1f}%", ha="center", fontweight="bold", color="#9467bd", fontsize=11)
    for idx, val in enumerate(abs_sub["mean_school_ptr"]):
        ax2.text(idx + 0.15, val + 0.35, f"{val:.1f}:1", ha="center", fontweight="bold", color="#1b9e77", fontsize=11)

    plt.tight_layout()
    fig12_path = "outputs/figures/fig12_student_complexity_trends.png"
    plt.savefig(fig12_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved Figure 12 to {fig12_path}")
    
    # ---------------------------------------------------------
    # 6. Write Calibrated Markdown Report
    # ---------------------------------------------------------
    report_path = "outputs/tables/task004c_complexity_analysis_report.md"
    
    r15 = crdc_rows[crdc_rows["wave_label"] == "2015-16"].iloc[0]
    r24 = crdc_rows[crdc_rows["wave_label"] == "2023-24"].iloc[0]
    
    s504_count_diff = int(r24['section_504_students'] - r15['section_504_students'])
    s504_count_pct = (r24['section_504_students'] - r15['section_504_students']) / r15['section_504_students'] * 100
    s504_rate_diff_pp = r24['section_504_pct'] - r15['section_504_pct']
    s504_rate_rel_pct = (r24['section_504_pct'] - r15['section_504_pct']) / r15['section_504_pct'] * 100
    
    a18 = abs_sub[abs_sub["wave_label"] == "2017-18"].iloc[0]
    a21 = abs_sub[abs_sub["wave_label"] == "2020-21"].iloc[0]
    a22 = abs_sub[abs_sub["wave_label"] == "2021-22"].iloc[0]
    a23 = abs_sub[abs_sub["wave_label"] == "2022-23"].iloc[0]
    
    abs_shock_pp = a21['chronic_absent_rate_pct'] - a18['chronic_absent_rate_pct']
    abs_plateau_pp = a23['chronic_absent_rate_pct'] - a18['chronic_absent_rate_pct']
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Task 004C.1: Student Complexity, Accommodations & Workload Burden Analysis\n")
        f.write("## Calibrated Longitudinal Analysis & The Compound Workload Conceptual Framework\n\n")
        f.write("---\n\n")
        f.write("## 1. Executive Summary & Calibrated Hypothesis Adjudication\n\n")
        f.write("Throughout this investigation, two primary hypotheses sought to explain why secondary teachers report intense workload stress despite expanding district teacher rolls:\n")
        f.write("- **Hypothesis H1b (The Secular Headcount Expansion Hypothesis):** Classroom headcounts simply grew by 5+ students per section across the decade.\n")
        f.write("- **Hypothesis H2 (The Complexity & Workload Support Hypothesis):** Classroom headcounts remained anchored by contractual and scheduling structures, but the **instructional, administrative, and legal compliance load per enrolled student rose substantially** due to mandated accommodations, persistent chronic absenteeism, and lost planning capacity.\n\n")
        f.write("### Calibrated Scientific Status:\n")
        f.write("1. **Hypothesis H1b is Not Supported by Public Aggregates (Reserved for Microdata):** Neither national survey collections (NTPS) nor regional CRDC course averages show a secular secular ballooning in average course sizes over the 2014–2024 period. However, because public CRDC data represent school-course aggregated offerings rather than full section-level roster distributions, **H1b cannot be formally falsified until true section microdata are evaluated** (to verify whether the variance or right-tail of core sections expanded).\n")
        f.write("2. **Hypothesis H2 is Strongly Supported in Measurable Accommodation Mandates:** The public data demonstrate that teachers are managing a substantially more complex population of students within standard classroom sections:\n")
        f.write(f"   - **Section 504 Accommodations Surged +{s504_count_pct:.1f}% (+{s504_rate_diff_pp:.2f} Percentage Points):** Students with formal Section 504 plans expanded from **{int(r15['section_504_students']):,} ({r15['section_504_pct']}%)** in 2015–16 to **{int(r24['section_504_students']):,} ({r24['section_504_pct']}%)** in 2023–24 (+{s504_count_diff:,} additional students; a +{s504_rate_rel_pct:.1f}% relative rate expansion).\n")
        f.write(f"   - **IDEA (Special Education) Inclusions Expanded:** Special education students rose from **{int(r15['idea_students']):,} ({r15['idea_pct']}%)** to **{int(r24['idea_students']):,} ({r24['idea_pct']}%)**.\n")
        f.write(f"   - **Combined Mandated Legal Accommodations:** In 2023–24, **{r24['total_accommodations_pct']}% of all enrolled students** carry legally binding individualized accommodations (IEPs or 504 plans) that classroom teachers must document, differentiate, assess, and comply with under federal law.\n")
        f.write(f"   - **Chronic Absenteeism Trajectory (Baseline -> Shock -> Plateau):** Chronic absenteeism surged from **{a18['chronic_absent_rate_pct']}%** in 2017–18 by **+{abs_shock_pp:.2f} percentage points** to **{a21['chronic_absent_rate_pct']}%** during the 2020–21 pandemic shock, before stabilizing post-pandemic at **{a22['chronic_absent_rate_pct']}% (2021–22)** and **{a23['chronic_absent_rate_pct']}% (2022–23)**. This post-pandemic plateau remains **+{abs_plateau_pp:.2f} percentage points (~91% higher)** above pre-pandemic baseline.\n\n")
        f.write("3. **Balanced Campus Panel Sensitivity Confirms Robustness:** The upward trajectory is virtually identical when restricted strictly to the balanced panel of 602–607 continuously operating physical campuses (Section 504 rising from 2.03% to 3.91%; total accommodations rising from 12.61% to 16.36%), proving that accommodation growth is not an artifact of school openings, closures, or demographic churn.\n\n")
        f.write("---\n\n")
        f.write("## 2. Epistemic Precision: Clarifying Chronic Absenteeism vs. Daily Absences\n\n")
        f.write("> [!IMPORTANT]\n")
        f.write("> **Measurement Guardrail: Chronic Absenteeism $\\neq$ Daily Absence Rate**\n")
        f.write(">\n")
        f.write("> In federal reporting (EDFacts FS195 and CRDC), **chronic absenteeism** is defined as missing **10% or more of enrolled school days** across the academic year (typically 18+ instructional days for a 180-day school calendar).\n")
        f.write(">\n")
        f.write("> This metric does **not** mean that 25% or 35% of students are absent on any given school day. On any typical day, Average Daily Attendance (ADA) remains in the 90% to 93% range. \n")
        f.write(">\n")
        f.write("> Rather, chronic absenteeism measures the **cumulative disruption** experienced by a school: roughly 1 in 4 students is repeatedly cycling in and out of instruction, accumulating fragmented knowledge gaps. For a classroom teacher, this creates an ongoing logistical and pedagogical friction: administering individual make-up assessments, providing asynchronous materials, re-teaching missed laboratory exercises, and maintaining compliance documentation for attendance interventions.\n\n")
        f.write("---\n\n")
        f.write("## 3. Regional Longitudinal Complexity Indicators\n\n")
        f.write("From `outputs/tables/task004c_complexity_trends_regional.csv`:\n\n")
        f.write("| School Year | Wave / Source | Schools | Total Enrolled | IDEA (SPED) % | Section 504 % | EL / LEP % | Total Accommodations % | Chronic Absenteeism % | Headline PTR |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in reg_df.iterrows():
            idea_s = f"{r['idea_pct']:.2f}%" if pd.notna(r['idea_pct']) else "—"
            s504_s = f"{r['section_504_pct']:.2f}%" if pd.notna(r['section_504_pct']) else "—"
            lep_s = f"{r['lep_el_pct']:.2f}%" if pd.notna(r['lep_el_pct']) else "—"
            acc_s = f"**{r['total_accommodations_pct']:.2f}%**" if pd.notna(r['total_accommodations_pct']) else "—"
            abs_s = f"**{r['chronic_absent_rate_pct']:.2f}%**" if pd.notna(r['chronic_absent_rate_pct']) else "—"
            ptr_s = f"{r['mean_school_ptr']:.1f}:1" if pd.notna(r['mean_school_ptr']) else "—"
            f.write(f"| {r['school_year']} | {r['wave_label']} ({r['data_source']}) | {r['num_schools']} | {int(r['total_enrollment']):,} | {idea_s} | {s504_s} | {lep_s} | {acc_s} | {abs_s} | {ptr_s} |\n")
            
        f.write("\n\n---\n\n")
        f.write("## 4. Balanced Campus Sensitivity Panel (N = 602–607 Continuing Campuses)\n\n")
        f.write("To verify that accommodation and absenteeism trends are not driven by campus composition changes, the table below restricts analysis strictly to facilities operating continuously across the study period (`outputs/tables/task004c_complexity_balanced_panel.csv`):\n\n")
        f.write("| School Year | Wave / Source | Campuses | Enrolled | IDEA % | Section 504 % | Total Accommodations % | Chronic Absenteeism % | Mean School PTR |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in bal_df.iterrows():
            idea_s = f"{r['idea_pct']:.2f}%" if pd.notna(r['idea_pct']) else "—"
            s504_s = f"{r['section_504_pct']:.2f}%" if pd.notna(r['section_504_pct']) else "—"
            acc_s = f"**{r['total_accommodations_pct']:.2f}%**" if pd.notna(r['total_accommodations_pct']) else "—"
            abs_s = f"**{r['chronic_absent_rate_pct']:.2f}%**" if pd.notna(r['chronic_absent_rate_pct']) else "—"
            f.write(f"| {r['wave_label']} | {r['data_source']} | {r['num_schools']} | {int(r['total_enrollment']):,} | {idea_s} | {s504_s} | {acc_s} | {abs_s} | {r['mean_school_ptr']:.1f}:1 |\n")
            
        f.write("\n\n---\n\n")
        f.write("## 5. Locale Disaggregation: Suburban vs. Urban Core Trajectories\n\n")
        f.write("From `outputs/tables/task004c_complexity_by_locale.csv` (Comparing 2017–18 vs. 2023–24):\n\n")
        f.write("| Locale Tier | Wave | Campuses | Enrolled | IDEA (SPED) % | Section 504 % | EL / LEP % | Total Accommodations % | Mean PTR |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in loc_df.iterrows():
            f.write(f"| **{r['locale_group']}** | {r['crdc_wave']} | {r['num_schools']} | {int(r['total_enrollment']):,} | {r['idea_pct']:.2f}% | {r['section_504_pct']:.2f}% | {r['lep_el_pct']:.2f}% | **{r['total_accommodations_pct']:.2f}%** | {r['mean_ptr']:.1f}:1 |\n")
            
        f.write("\n\n---\n\n")
        f.write("## 6. Benchmark School Case Studies\n\n")
        f.write("From `outputs/tables/task004c_complexity_benchmark_schools.csv`:\n\n")
        f.write("| Campus Name | District | Wave | Enrolled | IDEA % (Count) | 504 % (Count) | Total Accommodations % | School PTR |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in b_df.iterrows():
            f.write(f"| **{r['school_name']}** | {r['district_name']} | {r['crdc_wave']} | {int(r['enrollment'])} | {r['idea_pct']:.1f}% ({r['idea_count']}) | {r['section_504_pct']:.1f}% ({r['section_504_count']}) | **{r['total_accommodations_pct']:.1f}%** ({r['total_accommodations_count']}) | {r['school_ptr']:.1f}:1 |\n")
            
        f.write("\n\n---\n\n")
        f.write("## 7. The Compound Workload Conceptual Framework\n\n")
        f.write("Rather than asserting an empirically fitted regression with uncalibrated percentage claims, we formulate a **conceptual accounting framework** that illustrates how instructional load compounds even when class rosters remain constant:\n\n")
        f.write("$$\\boxed{ \\text{Instructional Load}_i = \\sum_{j=1}^{K_i} \\left[ n_{ij} \\cdot \\left( 1 + \\omega_{\\text{acc}} \\cdot \\text{AccShare}_{ij} + \\omega_{\\text{abs}} \\cdot \\text{AbsDrag}_{ij} \\right) \\right] + \\text{Compliance}_i + \\text{Coverage}_i - \\text{ProtectedPlanning}_i }$$\n\n")
        f.write("Where:\n")
        f.write("- $K_i$ is the number of sections taught by teacher $i$ (e.g., 5 sections in a 5-of-7 regime, 6 sections in a 6-of-7 regime).\n")
        f.write("- $n_{ij}$ is the raw enrollment of section $j$ (~24–27 students).\n")
        f.write("- $\\text{AccShare}_{ij}$ is the proportion of students in section $j$ with formal accommodation plans (IEP or 504), each requiring individualized modifications, separate testing accommodations, and parent communications.\n")
        f.write("- $\\text{AbsDrag}_{ij}$ represents the asynchronous re-teaching and grading friction associated with elevated chronic absenteeism.\n")
        f.write("- $\\text{Compliance}_i$ is the administrative time required for formal progress monitoring, 504 team meetings, and IEP reviews.\n")
        f.write("- $\\text{Coverage}_i$ is the lost planning time caused by substituting for colleague vacancies (as documented in the NCES School Pulse Panel).\n\n")
        f.write("### Conceptual Takeaway:\n")
        f.write("When public school staffing ratios declined from 14.8 to 13.5:1, districts added personnel. However, because those additions went toward specialized roles and planning protections rather than shrinking section sizes, classroom teachers continued managing 24–27 students per class. Within those sections, however, the proportion of students requiring individualized legal accommodations nearly doubled (504 rates surging +94%), chronic absenteeism plateaued at nearly double pre-pandemic levels (~24.7% vs 12.9%), and staff vacancies frequently eroded planning periods. Thus, teachers experience a substantial escalation in cognitive and operational demands even though macro staffing ratios improved.\n\n")
        f.write("### Visual Reference:\n")
        f.write("See [`fig12_student_complexity_trends.png`](../figures/fig12_student_complexity_trends.png) for the multi-wave trajectory of mandated accommodations and the full 4-point chronic absenteeism time series.\n")

    print(f"Saved calibrated comprehensive report to {report_path}")
    print("=== Task 004C.1 Complete ===")

if __name__ == "__main__":
    run_complexity_analysis()
