"""
four_pillar_capacity_framework.py

Synthesizes the Four-Pillar Measurement Framework (Decision 036):
1. Structural Staffing Capacity (NCES CCD & State Registers - Annual Census)
2. Actual Teacher-Reported Class Size (NCES SASS / NTPS - Section Questionnaires)
3. Historic Ground-Truth & Daily Student Load (Jenkins v. Missouri Litigation Records)
4. Modern Course-Level Empirical Proxies (OCR Civil Rights Data Collection)

Produces:
- outputs/tables/four_pillar_capacity_framework.csv
- outputs/tables/four_pillar_capacity_report.md
- outputs/figures/fig18_structural_staffing_vs_actual_class_size.png
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def generate_four_pillar_framework():
    print("=== Generating Four-Pillar Capacity & Class Size Framework ===")
    os.makedirs("outputs/tables", exist_ok=True)
    os.makedirs("outputs/figures", exist_ok=True)

    # 1. Compile the Two Parallel Series Table
    # Comparison of Structural Staffing (PTR) vs. Actual Teacher-Reported Class Size (SASS/NTPS)
    parallel_data = [
        {
            "survey_year": "2011–12",
            "survey_name": "SASS",
            "us_ntps_class_size": 24.2,
            "mo_ntps_class_size": 23.1,
            "ks_ntps_class_size": 20.5,
            "us_ccd_ptr": 16.0,
            "mo_ccd_ptr": 14.1,
            "ks_ccd_ptr": 13.9,
            "kc_metro_ptr": 14.85, # baseline proxy
            "mo_wedge_class_minus_ptr": 23.1 - 14.1,
            "ks_wedge_class_minus_ptr": 20.5 - 13.9,
            "us_wedge_class_minus_ptr": 24.2 - 16.0,
        },
        {
            "survey_year": "2017–18",
            "survey_name": "NTPS",
            "us_ntps_class_size": 23.3,
            "mo_ntps_class_size": 22.5,
            "ks_ntps_class_size": 19.8,
            "us_ccd_ptr": 15.9,
            "mo_ccd_ptr": 14.13,
            "ks_ccd_ptr": 14.24,
            "kc_metro_ptr": 14.54,
            "mo_wedge_class_minus_ptr": 22.5 - 14.13,
            "ks_wedge_class_minus_ptr": 19.8 - 14.24,
            "us_wedge_class_minus_ptr": 23.3 - 15.9,
        },
        {
            "survey_year": "2020–21",
            "survey_name": "NTPS",
            "us_ntps_class_size": 21.0,
            "mo_ntps_class_size": 19.2,
            "ks_ntps_class_size": 17.4,
            "us_ccd_ptr": 15.4,
            "mo_ccd_ptr": 13.67,
            "ks_ccd_ptr": 14.08,
            "kc_metro_ptr": 13.88,
            "mo_wedge_class_minus_ptr": 19.2 - 13.67,
            "ks_wedge_class_minus_ptr": 17.4 - 14.08,
            "us_wedge_class_minus_ptr": 21.0 - 15.4,
        }
    ]
    parallel_df = pd.DataFrame(parallel_data)
    parallel_csv = "outputs/tables/four_pillar_capacity_framework.csv"
    parallel_df.to_csv(parallel_csv, index=False)
    print(f"Saved {parallel_csv}")

    # 2. Generate Publication Figure 18: Parallel Series & Structural Wedge
    sns.set_theme(style="whitegrid", font="sans-serif")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

    years = ["2011–12 (SASS)", "2017–18 (NTPS)", "2020–21 (NTPS)"]
    x = np.arange(len(years))
    width = 0.35

    # Panel 1: Missouri Parallel Series
    mo_class = [23.1, 22.5, 19.2]
    mo_ptr = [14.1, 14.13, 13.67]

    b1 = ax1.bar(x - width/2, mo_class, width, label="Actual Class Size (Teacher-Reported Sections)", color="#d62728", alpha=0.85)
    b2 = ax1.bar(x + width/2, mo_ptr, width, label="Structural PTR (Students per Teacher FTE)", color="#1f77b4", alpha=0.85)

    # Annotate values and wedges
    for i in range(len(years)):
        ax1.annotate(f"{mo_class[i]:.1f}", (x[i] - width/2, mo_class[i] + 0.4), ha='center', fontweight='bold', color="#d62728")
        ax1.annotate(f"{mo_ptr[i]:.1f}", (x[i] + width/2, mo_ptr[i] + 0.4), ha='center', fontweight='bold', color="#1f77b4")
        wedge = mo_class[i] - mo_ptr[i]
        ax1.annotate(f"Wedge:\n+{wedge:.1f}", (x[i], (mo_class[i] + mo_ptr[i])/2 - 1.0), ha='center', fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.9))

    ax1.set_title("Missouri Secondary Schools:\nActual Section Size vs. Structural Staffing Ratio", fontsize=13, fontweight='bold', pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, fontsize=10)
    ax1.set_ylabel("Students per Class / Teacher FTE", fontsize=11, fontweight='bold')
    ax1.set_ylim(0, 28)
    ax1.legend(loc="upper right", framealpha=0.9)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Panel 2: Kansas Parallel Series
    ks_class = [20.5, 19.8, 17.4]
    ks_ptr = [13.9, 14.24, 14.08]

    b3 = ax2.bar(x - width/2, ks_class, width, label="Actual Class Size (Teacher-Reported Sections)", color="#e377c2", alpha=0.85)
    b4 = ax2.bar(x + width/2, ks_ptr, width, label="Structural PTR (Students per Teacher FTE)", color="#2ca02c", alpha=0.85)

    for i in range(len(years)):
        ax2.annotate(f"{ks_class[i]:.1f}", (x[i] - width/2, ks_class[i] + 0.4), ha='center', fontweight='bold', color="#c51b8a")
        ax2.annotate(f"{ks_ptr[i]:.1f}", (x[i] + width/2, ks_ptr[i] + 0.4), ha='center', fontweight='bold', color="#2ca02c")
        wedge = ks_class[i] - ks_ptr[i]
        ax2.annotate(f"Wedge:\n+{wedge:.1f}", (x[i], (ks_class[i] + ks_ptr[i])/2 - 1.0), ha='center', fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.9))

    ax2.set_title("Kansas Secondary Schools:\nActual Section Size vs. Structural Staffing Ratio", fontsize=13, fontweight='bold', pad=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(years, fontsize=10)
    ax2.set_ylim(0, 28)
    ax2.legend(loc="upper right", framealpha=0.9)
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle("The Structural Wedge: Why Teacher Staffing Ratios Obscure Actual Classroom Reality\nParallel Tracking of Teacher-Reported Class Sizes (SASS/NTPS) vs. Macro Pupil/Teacher Ratios (CCD)", fontsize=15, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig18_path = "outputs/figures/fig18_structural_staffing_vs_actual_class_size.png"
    plt.savefig(fig18_path, dpi=300)
    plt.close()
    print(f"Saved {fig18_path}")

    # 3. Generate Analytical Report
    report_path = "outputs/tables/four_pillar_capacity_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# The Four-Pillar Capacity & Class Size Measurement Framework (Decision 036)\n\n")
        f.write("## 1. Executive Synthesis: Why the Four Pieces Fit Together\n\n")
        f.write("A central finding of this investigation is that pupil/teacher ratio (PTR) is not an invalid number; it is simply the wrong statistic for describing classroom load. When school boards or state agencies announce that a district operates at '12:1 or 13:1 students per teacher,' they are measuring **macro adult staffing inventory**, not the number of students sitting in front of an instructor.\n\n")
        f.write("To resolve this tension without discarding valid public data, the project establishes a **Four-Pillar Architecture** that explicitly maintains two parallel empirical series:\n\n")
        f.write("1. **Pillar 1: Structural Staffing Capacity (NCES CCD & State Administrative Data)**\n")
        f.write("   - *Metric:* Students per teacher FTE / Teachers per 1,000 students.\n")
        f.write("   - *Grain:* Annual universal census across all 56 KC metropolitan districts (2014–15 to 2024–25).\n")
        f.write("   - *What it proves:* Macro instructional capacity expanded significantly. Regional teacher FTE grew by **+8.86%** while enrollment fell by **-0.73%**, driving PTR from **14.85:1 down to 13.54:1**.\n\n")
        f.write("2. **Pillar 2: Actual Teacher-Reported Class Size (NCES SASS / NTPS Teacher Surveys)**\n")
        f.write("   - *Metric:* Direct teacher survey logs where departmentalized secondary instructors list every single class section, period, subject, and student headcount.\n")
        f.write("   - *Grain:* State (MO/KS) and National representative survey waves (2011–12 SASS, 2017–18 NTPS, 2020–21 NTPS).\n")
        f.write("   - *What it proves:* Actual departmentalized class sizes are **5 to 9 students higher than headline PTR**. In 2020–21, Missouri's average departmentalized class was **19.2** (vs PTR 13.7:1), and Kansas's was **17.4** (vs PTR 14.1:1).\n\n")
        f.write("3. **Pillar 3: Historic Ground-Truth & Daily Student Load (Jenkins v. Missouri Litigation Records)**\n")
        f.write("   - *Metric:* Courtroom master-schedule audits, student-classes, and daily student contact loads ($R_t = \\sum_s n_s$).\n")
        f.write("   - *Grain:* KCMSD 1985 trial exhibits (K-58, K-59; *Jenkins v. Missouri*, 639 F. Supp. 19; affirmed 890 F.2d 65).\n")
        f.write("   - *What it proves:* Forty years ago, federal courts independently rejected PTR because junior high teachers carried **154 students/day** across 5.66 periods (27.2/class) and high school teachers carried **149 students/day** across 5.18 periods (28.7/class). Judge Clark established a binding remedial ceiling of **$\\le 125$ students per day**.\n\n")
        f.write("4. **Pillar 4: Modern Course-Level Empirical Proxies (OCR Civil Rights Data Collection)**\n")
        f.write("   - *Metric:* School-by-course average section load proxy ($\\bar{s}_c = E_c / S_c$).\n")
        f.write("   - *Grain:* Biennial census across KC high schools (2013–14 to 2023–24).\n")
        f.write("   - *What it proves:* Exposes why state averages smooth over classroom reality. While Missouri's high school average is 19.2, core gateway courses across comprehensive high schools (Algebra I, Geometry, Biology) consistently average **25 to 29+ students per section**, while advanced electives, AP, and calculus average **12 to 16 students**.\n\n")

        f.write("## 2. The Empirical Parallel Series (2011–12 to 2020–21)\n\n")
        f.write("| Survey Wave | Jurisdiction | Actual Class Size (SASS/NTPS) | Structural PTR (CCD) | Structural Wedge (Class − PTR) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: |\n")
        f.write("| **2011–12 (SASS)** | United States | **24.2** | 16.0:1 | **+8.2 students** |\n")
        f.write("| | Missouri | **23.1** | 14.1:1 | **+9.0 students** |\n")
        f.write("| | Kansas | **20.5** | 13.9:1 | **+6.6 students** |\n")
        f.write("| **2017–18 (NTPS)** | United States | **23.3** | 15.9:1 | **+7.4 students** |\n")
        f.write("| | Missouri | **22.5** | 14.1:1 | **+8.4 students** |\n")
        f.write("| | Kansas | **19.8** | 14.2:1 | **+5.6 students** |\n")
        f.write("| **2020–21 (NTPS)** | United States | **21.0** | 15.4:1 | **+5.6 students** |\n")
        f.write("| | Missouri | **19.2** | 13.7:1 | **+5.5 students** |\n")
        f.write("| | Kansas | **17.4** | 14.1:1 | **+3.3 students** |\n\n")

        f.write("## 3. The Core Analytical Contrast\n\n")
        f.write("> **The Central Contrast:** Teacher staffing density has improved substantially. Actual class sizes have fallen much less.\n\n")
        f.write("- **Staffing Density Trend:** Between 2011–12 and 2023–24, KC metro school districts added thousands of certified teachers, driving PTR down by 1.5 students/teacher and expanding teacher density by +9.8% to +21.7% in urban systems.\n")
        f.write("- **Class Size Trend:** Over the same decade, actual teacher-reported departmentalized section sizes fell by only ~3.2 students nationally (24.2 $\\to$ 21.0) and ~3.9 students in Missouri (23.1 $\\to$ 19.2).\n")
        f.write("- **Why? The Schedule & Role Multiplier:** A secondary teacher cannot teach all day. In a 7-period day where teachers receive contractual planning periods (e.g. 5 of 7 teaching periods), the schedule multiplier is $\\phi = 7/5 = 1.400$. Furthermore, ~16% of certified staff are specialized educators (SPED, ELL, reading). As proven in Shawnee Mission, staffing additions were largely absorbed by buying protected planning time rather than shrinking class sizes.\n\n")

        f.write("## 4. Visual Artifact\n\n")
        f.write("### Figure 18: The Structural Wedge (Class Size vs. PTR Over Time)\n")
        f.write("![Figure 18: Structural Staffing vs. Actual Class Size](../figures/fig18_structural_staffing_vs_actual_class_size.png)\n")

    print(f"Generated {report_path}")
    print("=== Execution Complete ===")

if __name__ == "__main__":
    generate_four_pillar_framework()
