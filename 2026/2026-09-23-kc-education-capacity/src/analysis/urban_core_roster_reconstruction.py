"""
src/analysis/urban_core_roster_reconstruction.py
Task 006.1: Public Course-Load Scenarios & Gateway Bottlenecks for Selected Urban High Schools

Investigates the extent to which public CRDC course aggregates can model secondary course loads without
student microdata, while maintaining strict epistemic boundaries between observed course means, derived
schedule scenarios, and unobserved individual teacher rosters.

Pilot Cohort:
  - Kansas City 33: Lincoln College Prep, East High School
  - Grandview C-4: Grandview Senior High
  - Hickman Mills C-1: Ruskin High School
  - Center 58: Center Senior High
  - Kansas City USD 500 (KCKPS): Wyandotte High School

Outputs:
  - outputs/tables/task006_urban_roster_reconstruction.csv
  - outputs/tables/task006_urban_roster_reconstruction_report.md
  - outputs/figures/fig15_urban_core_teacher_load_wedge.png
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run_urban_reconstruction():
    print("=== Running Task 006.1: Public Course-Load Scenarios & Gateway Bottlenecks ===")
    
    # 1. Load CRDC Course Aggregates
    df = pd.read_csv("data/processed/kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv")
    latest_year = df["school_year"].max()
    latest_hs = df[(df["school_year"] == latest_year) & (df["school_level"] == "High")].copy()
    
    # Selected urban-core pilot campuses
    target_schools = [
        {"name": "LINCOLN COLLEGE PREP.", "district": "KANSAS CITY 33", "label": "Lincoln Prep\n(KCPS)", "schedule_regime": "7-period / hybrid", "typical_duty": 5},
        {"name": "GRANDVIEW SR. HIGH", "district": "GRANDVIEW C-4", "label": "Grandview High\n(Grandview C-4)", "schedule_regime": "7-period day", "typical_duty": 5},
        {"name": "RUSKIN HIGH SCHOOL", "district": "HICKMAN MILLS C-1", "label": "Ruskin High\n(Hickman Mills)", "schedule_regime": "7-period day", "typical_duty": 5},
        {"name": "CENTER SR. HIGH", "district": "CENTER 58", "label": "Center High\n(Center 58)", "schedule_regime": "7-period day", "typical_duty": 5},
        {"name": "EAST HIGH SCHOOL", "district": "KANSAS CITY 33", "label": "East High\n(KCPS)", "schedule_regime": "7-period / hybrid", "typical_duty": 5},
        {"name": "Wyandotte High", "district": "Kansas City", "label": "Wyandotte High\n(KCKPS)", "schedule_regime": "8-period Red/White block", "typical_duty": 6}
    ]
    
    core_math = ["alg1", "geom", "alg2"]
    adv_math = ["advm", "calc"]
    math_all = core_math + adv_math
    
    records = []
    
    for sch in target_schools:
        sdata = latest_hs[(latest_hs["school_name"] == sch["name"]) & (latest_hs["district_name"] == sch["district"])]
        if len(sdata) == 0:
            continue
        
        row0 = sdata.iloc[0]
        enr = row0["enrollment_k12"]
        fte = row0["classroom_teacher_fte"]
        ptr = row0["school_ptr"]
        state = row0["state"]
        
        # Course-specific extractions
        alg1 = sdata[sdata["course_code"] == "alg1"]
        alg1_cls = alg1["num_classes"].sum() if len(alg1) > 0 else 0
        alg1_enr = alg1["num_enrolled"].sum() if len(alg1) > 0 else 0
        alg1_sz = alg1_enr / alg1_cls if alg1_cls > 0 else np.nan
        
        geom = sdata[sdata["course_code"] == "geom"]
        geom_cls = geom["num_classes"].sum() if len(geom) > 0 else 0
        geom_enr = geom["num_enrolled"].sum() if len(geom) > 0 else 0
        geom_sz = geom_enr / geom_cls if geom_cls > 0 else np.nan
        
        alg2 = sdata[sdata["course_code"] == "alg2"]
        alg2_cls = alg2["num_classes"].sum() if len(alg2) > 0 else 0
        alg2_enr = alg2["num_enrolled"].sum() if len(alg2) > 0 else 0
        alg2_sz = alg2_enr / alg2_cls if alg2_cls > 0 else np.nan
        
        # Math department aggregates
        m_all = sdata[sdata["course_code"].isin(math_all)]
        m_classes = m_all["num_classes"].sum()
        m_enrolled = m_all["num_enrolled"].sum()
        dept_size = m_enrolled / m_classes if m_classes > 0 else np.nan
        
        # Core Math combined
        m_core = sdata[sdata["course_code"].isin(core_math)]
        c_classes = m_core["num_classes"].sum()
        c_enrolled = m_core["num_enrolled"].sum()
        core_size = c_enrolled / c_classes if c_classes > 0 else np.nan
        
        # Adv Math combined
        m_adv = sdata[sdata["course_code"].isin(adv_math)]
        a_classes = m_adv["num_classes"].sum()
        a_enrolled = m_adv["num_enrolled"].sum()
        adv_size = a_enrolled / a_classes if a_classes > 0 else np.nan
        
        # Schedule scenarios: R5 = 5 * s_bar; R6 = 6 * s_bar
        # Naive expectations from PTR
        naive_r5 = 5 * ptr if pd.notnull(ptr) else np.nan
        naive_r6 = 6 * ptr if pd.notnull(ptr) else np.nan
        
        # Modeled course-group loads under 5-section scenario
        modeled_core_r5 = 5 * core_size if pd.notnull(core_size) else np.nan
        modeled_adv_r5 = 5 * adv_size if pd.notnull(adv_size) else np.nan
        modeled_dept_r5 = 5 * dept_size if pd.notnull(dept_size) else np.nan
        modeled_alg1_r5 = 5 * alg1_sz if pd.notnull(alg1_sz) else np.nan
        
        # Modeled course-group loads under 6-section scenario
        modeled_core_r6 = 6 * core_size if pd.notnull(core_size) else np.nan
        modeled_adv_r6 = 6 * adv_size if pd.notnull(adv_size) else np.nan
        modeled_dept_r6 = 6 * dept_size if pd.notnull(dept_size) else np.nan
        modeled_alg1_r6 = 6 * alg1_sz if pd.notnull(alg1_sz) else np.nan
        
        # Residuals under 5-section scenario
        # Total residual: Modeled Core Load minus Naive PTR Load
        total_wedge_r5 = modeled_core_r5 - naive_r5 if pd.notnull(modeled_core_r5) else np.nan
        # Course-vs-PTR residual: Modeled Dept Mean minus Naive PTR Load
        course_ptr_residual_r5 = modeled_dept_r5 - naive_r5 if pd.notnull(modeled_dept_r5) else np.nan
        # Core-vs-advanced mix difference: Modeled Core Mean minus Modeled Dept Mean
        course_mix_diff_r5 = modeled_core_r5 - modeled_dept_r5 if pd.notnull(modeled_core_r5) and pd.notnull(modeled_dept_r5) else np.nan
        pct_wedge_r5 = (total_wedge_r5 / naive_r5 * 100) if pd.notnull(naive_r5) and naive_r5 > 0 else np.nan
        
        # Typical-duty modeled load for this campus
        typ_d = sch["typical_duty"]
        typical_modeled_core = typ_d * core_size if pd.notnull(core_size) else np.nan
        typical_naive = typ_d * ptr if pd.notnull(ptr) else np.nan
        typical_wedge = typical_modeled_core - typical_naive if pd.notnull(typical_modeled_core) else np.nan
        
        # Required math teachers under typical duty
        req_math_fte = m_classes / typ_d if m_classes > 0 else np.nan
        
        records.append({
            "school_name": sch["name"],
            "district_name": sch["district"],
            "display_label": sch["label"],
            "schedule_regime": sch["schedule_regime"],
            "typical_duty": typ_d,
            "state": state,
            "enrollment": enr,
            "classroom_teacher_fte": fte,
            "building_ptr": ptr,
            "alg1_classes": alg1_cls,
            "alg1_enrolled": alg1_enr,
            "alg1_mean_size": alg1_sz,
            "geom_classes": geom_cls,
            "geom_enrolled": geom_enr,
            "geom_mean_size": geom_sz,
            "alg2_classes": alg2_cls,
            "alg2_enrolled": alg2_enr,
            "alg2_mean_size": alg2_sz,
            "core_math_classes": c_classes,
            "core_math_enrolled": c_enrolled,
            "core_math_size": core_size,
            "adv_math_classes": a_classes,
            "adv_math_enrolled": a_enrolled,
            "adv_math_size": adv_size,
            "dept_math_classes": m_classes,
            "dept_math_enrolled": m_enrolled,
            "dept_math_size": dept_size,
            "req_math_fte_typical": req_math_fte,
            "naive_r5": naive_r5,
            "modeled_core_r5": modeled_core_r5,
            "modeled_adv_r5": modeled_adv_r5,
            "modeled_dept_r5": modeled_dept_r5,
            "modeled_alg1_r5": modeled_alg1_r5,
            "total_wedge_r5": total_wedge_r5,
            "course_ptr_residual_r5": course_ptr_residual_r5,
            "course_mix_diff_r5": course_mix_diff_r5,
            "pct_wedge_r5": pct_wedge_r5,
            "naive_r6": naive_r6,
            "modeled_core_r6": modeled_core_r6,
            "modeled_adv_r6": modeled_adv_r6,
            "modeled_dept_r6": modeled_dept_r6,
            "modeled_alg1_r6": modeled_alg1_r6,
            "typical_naive": typical_naive,
            "typical_modeled_core": typical_modeled_core,
            "typical_wedge": typical_wedge
        })
        
    res_df = pd.DataFrame(records)
    
    # 2. Export Master CSV
    os.makedirs("outputs/tables", exist_ok=True)
    res_df.to_csv("outputs/tables/task006_urban_roster_reconstruction.csv", index=False)
    print("Exported outputs/tables/task006_urban_roster_reconstruction.csv")
    
    # 3. Generate Publication Figure 15 with Defensible Labels
    os.makedirs("outputs/figures", exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.5, 7.0))
    
    # Style configurations
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#333333"
    plt.rcParams["axes.linewidth"] = 0.8
    
    labels = res_df["display_label"].tolist()
    x = np.arange(len(labels))
    width = 0.26
    
    # --- PANEL 1: Modeled Scenario Roster Loads (5-Section Scenario) ---
    rects1 = ax1.bar(x - width, res_df["naive_r5"], width, label="Administrative Baseline (5 × Building PTR)", color="#4A90E2", edgecolor="#1C3F73", alpha=0.9)
    rects2 = ax1.bar(x, res_df["modeled_core_r5"], width, label="Modeled Core-Math Load (5 Sections @ Core Mean)", color="#D0021B", edgecolor="#7A000E", alpha=0.9)
    rects3 = ax1.bar(x + width, res_df["modeled_adv_r5"].fillna(0), width, label="Modeled Advanced Math Load (5 Sections @ Adv Mean)", color="#7ED321", edgecolor="#3E6B11", alpha=0.85)
    
    # Reference line for Jenkins / Standard High School Full-Day Cap (125 students = 5 x 25)
    ax1.axhline(125, color="#D9534F", linestyle="--", linewidth=1.5, alpha=0.85, label="Jenkins 1985 Remedial Ceiling (125 students/day)")
    
    # Bar value labels
    for rect in rects1:
        h = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width()/2., h + 2, f"{h:.0f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#1C3F73")
    for rect in rects2:
        h = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width()/2., h + 2, f"{h:.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#7A000E")
    for rect in rects3:
        h = rect.get_height()
        if h > 5:
            ax1.text(rect.get_x() + rect.get_width()/2., h + 2, f"{h:.0f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#3E6B11")
        elif h == 0:
            ax1.text(rect.get_x() + rect.get_width()/2., 4, "N/A", ha="center", va="bottom", fontsize=8, color="#666666", style="italic")
            
    # Add annotation for Wyandotte Gateway Bottleneck
    w_idx = 5
    ax1.annotate("Algebra I Gateway:\n28.5/class (143 std/5 sec)\n46 classes, 1,313 enr",
                 xy=(w_idx, res_df["modeled_core_r5"].iloc[w_idx]),
                 xytext=(w_idx - 0.5, 128),
                 arrowprops=dict(facecolor="#333333", shrink=0.08, width=1.0, headwidth=5),
                 fontsize=8, fontweight="bold", bbox=dict(boxstyle="round,pad=0.3", fc="#FFF3CD", ec="#856404", lw=0.8))
            
    ax1.set_title("Panel A: Course-Level Class Sizes & Modeled Five-Section Loads", fontsize=11.5, fontweight="bold", pad=12)
    ax1.set_ylabel("Modeled Daily Student Load (5 Sections @ Course Mean)", fontsize=10.5, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=9.0)
    ax1.set_ylim(0, 175)
    ax1.legend(loc="upper right", fontsize=8.0, framealpha=0.95)
    ax1.grid(axis="y", linestyle=":", alpha=0.6)
    
    # --- PANEL 2: Residual Decomposition (Course vs. PTR Residual & Course-Mix Difference) ---
    p1 = ax2.bar(x, res_df["course_ptr_residual_r5"], width=0.45, label="Course-vs-PTR Residual (5 × [Dept Mean - PTR])", color="#F5A623", edgecolor="#9B6005", alpha=0.9)
    p2 = ax2.bar(x, res_df["course_mix_diff_r5"], width=0.45, bottom=res_df["course_ptr_residual_r5"], label="Core-vs-Advanced Mix Difference (5 × [Core Mean - Dept Mean])", color="#9013FE", edgecolor="#4A0587", alpha=0.9)
    
    # Total wedge labels on top of stacked bars
    for i in range(len(res_df)):
        tot = res_df["total_wedge_r5"].iloc[i]
        pct = res_df["pct_wedge_r5"].iloc[i]
        bot = res_df["course_ptr_residual_r5"].iloc[i] + res_df["course_mix_diff_r5"].iloc[i]
        if tot >= 0:
            ax2.text(x[i], max(bot, 0) + 2, f"+{tot:.1f}\n(+{pct:.0f}%)", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#333333")
        else:
            ax2.text(x[i], bot - 6, f"{tot:.1f}", ha="center", va="top", fontsize=8.5, fontweight="bold", color="#333333")
            
    ax2.set_title("Panel B: Course-Level Residual Over Building PTR (Five-Section Scenario)", fontsize=11.5, fontweight="bold", pad=12)
    ax2.set_ylabel("Modeled Load Residual Over Naive PTR (Students / Teacher)", fontsize=10.5, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9.0)
    ax2.set_ylim(-15, 80)
    ax2.axhline(0, color="#333333", linewidth=0.8)
    ax2.legend(loc="upper right", fontsize=8.0, framealpha=0.95)
    ax2.grid(axis="y", linestyle=":", alpha=0.6)
    
    plt.suptitle("Figure 15: Public Course-Load Modeling for Selected Urban Kansas City High Schools (SY 2023–24)\nComparing Course-Level CRDC Enrollment Means Against Administrative Pupil/Teacher Ratios", fontsize=12.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    
    fig_path = "outputs/figures/fig15_urban_core_teacher_load_wedge.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated {fig_path}")
    
    # 4. Generate Formal Markdown Report
    report_path = "outputs/tables/task006_urban_roster_reconstruction_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Task 006.1: Public Course-Load Scenarios & Gateway Bottlenecks\n\n")
        f.write("## 1. Epistemic Framing & The Five-Step Reconstruction Ladder\n\n")
        f.write("This pilot investigates the extent to which public data can recover secondary instructional workload without student microdata, while respecting the strict epistemic boundary between observed course aggregates and unobserved individual teacher rosters:\n\n")
        f.write("```\n")
        f.write("                          THE FIVE-STEP RECONSTRUCTION LADDER\n")
        f.write("========================================================================================\n")
        f.write("[1. OBSERVED]            School-course enrollment and class counts (CRDC: E_c, S_c)\n")
        f.write("                         --> Objective public empirical fact from federal collection.\n")
        f.write("----------------------------------------------------------------------------------------\n")
        f.write("[2. DERIVED]             Course-average class load (s_bar_c = E_c / S_c)\n")
        f.write("                         --> Exact mathematical average per reported course section.\n")
        f.write("----------------------------------------------------------------------------------------\n")
        f.write("[3. MODELED SCENARIOS]   Schedule scenario loads (R_5 = 5 * s_bar_c; R_6 = 6 * s_bar_c)\n")
        f.write("                         --> Modeled seat burden for a teacher assigned D sections of course c.\n")
        f.write("----------------------------------------------------------------------------------------\n")
        f.write("[4. DEPARTMENT LOAD]     Enrollment per teacher (E_math / T_math)\n")
        f.write("                         --> Average covered student-course enrollments per subject teacher.\n")
        f.write("----------------------------------------------------------------------------------------\n")
        f.write("[5. STILL UNOBSERVED]    Individual teacher roster distribution (P(R > 140), section variance)\n")
        f.write("                         --> Requires student-level SIS microdata or section schedule tables.\n")
        f.write("========================================================================================\n")
        f.write("```\n\n")
        
        f.write("## 2. Core Empirical Findings: Selected Urban High School Pilot (SY 2023–24)\n\n")
        f.write("Public CRDC data demonstrates that building-level pupil/teacher ratio (PTR) **can materially understate the load represented by particular courses**. However, the phenomenon is **not universal across all schools or all courses**, and depends heavily on gateway course concentration and course-mix differences:\n\n")
        
        f.write("### Table 1: Course-Level Averages and Modeled Scenario Loads\n\n")
        f.write("| School Campus | District | Building PTR | Alg I Mean | Geom Mean | Alg 2 Mean | Core Math Mean | Adv Math Mean | Modeled R5 (5 × Core) | Modeled R6 (6 × Core) | Naive R5 (5 × PTR) | R5 Residual (Δtotal) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, r in res_df.iterrows():
            adv_str = f"{r['adv_math_size']:.1f}" if pd.notnull(r["adv_math_size"]) else "N/A"
            f.write(f"| {r['school_name']} | {r['district_name']} | {r['building_ptr']:.2f}:1 | {r['alg1_mean_size']:.1f} | {r['geom_mean_size']:.1f} | {r['alg2_mean_size']:.1f} | {r['core_math_size']:.1f} | {adv_str} | {r['modeled_core_r5']:.1f} | {r['modeled_core_r6']:.1f} | {r['naive_r5']:.1f} | **+{r['total_wedge_r5']:.1f}** |\n")
            
        f.write("\n\n## 3. Detailed Campus Analyses\n\n")
        f.write("1. **Lincoln College Preparatory Academy (KCPS):**\n")
        f.write("   - Building PTR is 17.25:1, which naively suggests a modest 5-period load of 86.3 students.\n")
        f.write("   - However, reported core math classes average **29.5 students** (Geometry at 31.0, Algebra II at 30.6). A teacher assigned five such sections would carry a modeled load of **147.4 students/day**—surpassing the 1985 Jenkins remedial ceiling (125 students).\n")
        f.write("   - The **+61.1 student residual** over naive PTR reflects two distinct public factors: a course-vs-PTR residual of +29.3 students (department mean of 23.1 vs. PTR 17.25) and a core-vs-advanced mix difference of +31.8 students (core mean 29.5 vs. advanced mean 14.8).\n\n")
        
        f.write("2. **Grandview Senior High (Grandview C-4):**\n")
        f.write("   - Building PTR is 16.99:1 (85.0 naive 5-section load).\n")
        f.write("   - Core Algebra I (25.8) and Geometry (25.9) produce a core mean of 24.0 students, corresponding to a modeled 5-section load of **120.1 students** (+35.2 student residual). Under a 6-section assignment, this load reaches **144.2 students**.\n")
        f.write("   - Advanced Math averages 6.8 students and Calculus averages 3.0 students, generating a course-mix difference of +10.8 students.\n\n")
        
        f.write("3. **Ruskin High School (Hickman Mills C-1):**\n")
        f.write("   - Building PTR is 12.94:1 (64.7 naive 5-section load).\n")
        f.write("   - Core math sections average 21.0 students (Geometry 21.8, Algebra II 21.1, Algebra I 20.2), corresponding to a modeled 5-section load of **104.8 students** (+40.1 student residual) and a 6-section load of **125.7 students**.\n")
        f.write("   - Advanced math averages 4.25 students (Calculus 8.0, Advanced Math 3.0).\n\n")
        
        f.write("4. **Center Senior High (Center 58):**\n")
        f.write("   - Building PTR is 12.10:1 (60.5 naive load).\n")
        f.write("   - Core math sections average 16.7 students (Algebra I at 19.0), corresponding to a modeled 5-section load of **83.4 students** (+22.9 student residual). Because Center reported zero advanced mathematics sections in CRDC 2023–24, 100% of this residual is between the department average and building PTR.\n\n")
        
        f.write("5. **East High School (KCPS):**\n")
        f.write("   - Building PTR is 13.85:1 (69.3 naive load).\n")
        f.write("   - Core math sections average 17.1 students (Algebra I 19.0, Algebra II 18.9, Geometry 12.3), corresponding to a modeled 5-section load of **85.5 students** (+16.3 student residual).\n\n")
        
        f.write("6. **Wyandotte High School (Kansas City USD 500) — The Gateway Bottleneck Counterexample:**\n")
        f.write("   - Building PTR is 20.10:1.\n")
        f.write("   - Aggregate core math averages **20.19 students**, yielding virtually **zero aggregate wedge (+0.09)** over building PTR. This demonstrates that core load wedges are not an automatic institutional artifact.\n")
        f.write("   - However, course-level disaggregation reveals an acute **gateway bottleneck in Algebra I**: **46 classes enrolling 1,313 students (average 28.54 students/class)**.\n")
        f.write("   - Under Wyandotte's public 8-period Red/White alternating-block schedule (where full-time teachers typically instruct 6 blocks across the two-day cycle), an Algebra I instructor carrying 6 sections would manage a modeled active grading roster of **171.2 students** (+50.6 students above naive 6-period PTR). Even under 5 sections, the load is **142.7 students**.\n")
        f.write("   - In contrast, subsequent courses see substantial drop-offs (Geometry averages 14.3; Algebra II averages 14.1).\n\n")
        
        f.write("## 4. Methodological Clarifications & Guardrails\n\n")
        f.write("1. **Graduation Requirements vs. Funneling:** Missouri requires 3 mathematics and 3 science credits with End-of-Course (EOC) exams in Algebra I and Biology (Geometry is optional). Kansas requires 3 math units and 3 science units incorporating algebraic and geometric concepts. These courses are broadly enrolled foundation and gateway courses, but state law does not mandate a universal 9th/10th grade sequence.\n")
        f.write("2. **Staffing Denominator Definitions:** The Common Core of Data (CCD) pupil/teacher ratio divides enrollment by full-time equivalent classroom teachers. Guidance counselors are reported under a separate non-instructional staffing category and do not depress the teacher denominator. Specialized instructional staff (e.g. special education resource teachers or Title I reading teachers coded as classroom teachers) do contribute to the denominator gap.\n")
        f.write("3. **The Limits of Public Data:** Public CRDC records allow researchers to establish that core course sections frequently exceed building PTR, and that gateway courses can absorb massive enrollments. However, public aggregates cannot reveal the joint distribution of individual teacher rosters, section-level variance, or true teacher-level tail probabilities. Those measures remain behind the public data transparency boundary.\n\n")
        
        f.write("## 5. Visual Artifact\n\n")
        f.write("![Figure 15: Public Course-Load Modeling for Selected Urban High Schools](../figures/fig15_urban_core_teacher_load_wedge.png)\n")
        
    print(f"Generated {report_path}")
    print("=== Task 006.1 Complete ===")

if __name__ == "__main__":
    run_urban_reconstruction()
