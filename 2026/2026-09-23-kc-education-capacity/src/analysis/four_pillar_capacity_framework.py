"""
four_pillar_capacity_framework.py

Synthesizes the Four-Pillar Measurement Framework (Decision 036 Remediated):
1. Structural Staffing Capacity (NCES CCD & State Registers - Annual Census)
2. Actual Teacher-Reported Class Size (NCES SASS / NTPS - Section Questionnaires)
3. Historic Ground-Truth & Daily Student Load (Jenkins v. Missouri Litigation Records)
4. Modern Course-Level Empirical Proxies (OCR Civil Rights Data Collection)

Audited Benchmarks & Methodological Discipline:
- SASS 2011–12 High School Departmentalized: US 24.2, MO 21.8, KS 19.7 (Table 7)
- NTPS 2017–18 High School Departmentalized: US 23.3, MO 22.5, KS 19.8 (Table A-7a)
- NTPS 2020–21 High School Departmentalized: US 21.0, MO 19.2, KS 17.4 (Table ntps2021_sflt07_t1s)
- CCD Official State All-Grade PTR: 
    * 2011–12: US 16.0, MO 13.8, KS 13.0
    * 2017–18: US 15.9, MO 14.1, KS 14.2
    * 2020–21: US 15.4, MO 13.7, KS 14.1
- Metric Terminology: "Class-Size / Macro-PTR Gap" (Cross-metric comparison of secondary departmentalized class size vs all-grade state staffing ratio).
- Pre-pandemic trend highlighted: Class sizes held completely steady from 2011–12 to 2017–18 (MO 21.8 -> 22.5, KS 19.7 -> 19.8) during active hiring.
- Pillar 4 calibrated: Metro-wide course proxies average 16.5–18.7; localized gateway bottlenecks of 25–31 occur at specific urban and large suburban campuses.
- Survey design documented: Sampled teachers reporting up to 10 sections; two-stage probability design; 55% weighted response rate.

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
    print("=== Generating Remediated Four-Pillar Capacity & Class Size Framework ===")
    os.makedirs("outputs/tables", exist_ok=True)
    os.makedirs("outputs/figures", exist_ok=True)

    # 1. Compile the Two Parallel Series Table
    # Comparison of Structural Staffing (State PTR) vs. Actual Teacher-Reported Class Size (SASS/NTPS)
    parallel_data = [
        {
            "survey_year": "2011–12",
            "survey_name": "SASS (Table 7)",
            "us_hs_class_size": 24.2,
            "mo_hs_class_size": 21.8,
            "ks_hs_class_size": 19.7,
            "us_state_ptr": 16.0,
            "mo_state_ptr": 13.8,
            "ks_state_ptr": 13.0,
            "mo_gap_class_minus_ptr": 21.8 - 13.8,
            "ks_gap_class_minus_ptr": 19.7 - 13.0,
            "us_gap_class_minus_ptr": 24.2 - 16.0,
            "period_type": "Pre-Pandemic Baseline"
        },
        {
            "survey_year": "2017–18",
            "survey_name": "NTPS (Table A-7a)",
            "us_hs_class_size": 23.3,
            "mo_hs_class_size": 22.5,
            "ks_hs_class_size": 19.8,
            "us_state_ptr": 15.9,
            "mo_state_ptr": 14.1,
            "ks_state_ptr": 14.2,
            "mo_gap_class_minus_ptr": 22.5 - 14.1,
            "ks_gap_class_minus_ptr": 19.8 - 14.2,
            "us_gap_class_minus_ptr": 23.3 - 15.9,
            "period_type": "Pre-Pandemic Expansion"
        },
        {
            "survey_year": "2020–21",
            "survey_name": "NTPS (Table 7)",
            "us_hs_class_size": 21.0,
            "mo_hs_class_size": 19.2,
            "ks_hs_class_size": 17.4,
            "us_state_ptr": 15.4,
            "mo_state_ptr": 13.7,
            "ks_state_ptr": 14.1,
            "mo_gap_class_minus_ptr": 19.2 - 13.7,
            "ks_gap_class_minus_ptr": 17.4 - 14.1,
            "us_gap_class_minus_ptr": 21.0 - 15.4,
            "period_type": "Pandemic Wave (Caveated)"
        }
    ]
    parallel_df = pd.DataFrame(parallel_data)
    parallel_csv = "outputs/tables/four_pillar_capacity_framework.csv"
    parallel_df.to_csv(parallel_csv, index=False)
    print(f"Saved {parallel_csv}")

    # 2. Generate Publication Figure 18: Parallel Series & Cross-Metric Gap
    sns.set_theme(style="whitegrid", font="sans-serif")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), sharey=True)

    years = ["2011–12 (SASS)", "2017–18 (NTPS)", "2020–21 (NTPS)*"]
    x = np.arange(len(years))
    width = 0.35

    # Panel 1: Missouri Parallel Series
    mo_class = [21.8, 22.5, 19.2]
    mo_ptr = [13.8, 14.1, 13.7]

    b1 = ax1.bar(x - width/2, mo_class, width, label="Actual HS Class Size (Teacher Survey Sections)", color="#d62728", alpha=0.85)
    b2 = ax1.bar(x + width/2, mo_ptr, width, label="State All-Grade PTR (Students / Teacher FTE)", color="#1f77b4", alpha=0.85)

    for i in range(len(years)):
        ax1.annotate(f"{mo_class[i]:.1f}", (x[i] - width/2, mo_class[i] + 0.4), ha='center', fontweight='bold', color="#d62728")
        ax1.annotate(f"{mo_ptr[i]:.1f}", (x[i] + width/2, mo_ptr[i] + 0.4), ha='center', fontweight='bold', color="#1f77b4")
        gap = mo_class[i] - mo_ptr[i]
        ax1.annotate(f"Gap:\n+{gap:.1f}", (x[i], (mo_class[i] + mo_ptr[i])/2 - 1.0), ha='center', fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.9))

    ax1.set_title("Missouri Secondary Schools:\nActual HS Section Size vs. State Macro Staffing Ratio", fontsize=13, fontweight='bold', pad=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, fontsize=10)
    ax1.set_ylabel("Students per Section / Teacher FTE", fontsize=11, fontweight='bold')
    ax1.set_ylim(0, 28)
    ax1.legend(loc="upper right", framealpha=0.9)
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Panel 2: Kansas Parallel Series
    ks_class = [19.7, 19.8, 17.4]
    ks_ptr = [13.0, 14.2, 14.1]

    b3 = ax2.bar(x - width/2, ks_class, width, label="Actual HS Class Size (Teacher Survey Sections)", color="#e377c2", alpha=0.85)
    b4 = ax2.bar(x + width/2, ks_ptr, width, label="State All-Grade PTR (Students / Teacher FTE)", color="#2ca02c", alpha=0.85)

    for i in range(len(years)):
        ax2.annotate(f"{ks_class[i]:.1f}", (x[i] - width/2, ks_class[i] + 0.4), ha='center', fontweight='bold', color="#c51b8a")
        ax2.annotate(f"{ks_ptr[i]:.1f}", (x[i] + width/2, ks_ptr[i] + 0.4), ha='center', fontweight='bold', color="#2ca02c")
        gap = ks_class[i] - ks_ptr[i]
        ax2.annotate(f"Gap:\n+{gap:.1f}", (x[i], (ks_class[i] + ks_ptr[i])/2 - 1.0), ha='center', fontsize=9,
                     bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.9))

    ax2.set_title("Kansas Secondary Schools:\nActual HS Section Size vs. State Macro Staffing Ratio", fontsize=13, fontweight='bold', pad=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(years, fontsize=10)
    ax2.set_ylim(0, 28)
    ax2.legend(loc="upper right", framealpha=0.9)
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle("The Class-Size / Macro-PTR Gap: Cross-Metric Comparison Across Missouri and Kansas\nDepartmentalized High School Class Size (SASS/NTPS) vs. Statewide Structural Pupil/Teacher Ratio (CCD)", fontsize=15, fontweight='bold', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig18_path = "outputs/figures/fig18_structural_staffing_vs_actual_class_size.png"
    plt.savefig(fig18_path, dpi=300)
    plt.close()
    print(f"Saved {fig18_path}")

    # 3. Generate Analytical Report
    report_path = "outputs/tables/four_pillar_capacity_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# The Four-Pillar Capacity & Class Size Measurement Framework (Decision 036 Remediated)\n\n")
        f.write("## 1. Executive Synthesis: Separating the Four Questions Cleanly\n\n")
        f.write("A central finding of this investigation is that pupil/teacher ratio (PTR) is not an invalid number; it is simply the wrong statistic for describing classroom load. When school boards or state agencies announce that a district operates at '12:1 or 13:1 students per teacher,' they are measuring **macro teacher staffing inventory**, not the number of students sitting in front of an instructor.\n\n")
        f.write("To resolve this tension without discarding valid public data, the project establishes a **Four-Pillar Architecture** that explicitly maintains two parallel empirical series:\n\n")
        
        f.write("1. **Pillar 1: Structural Staffing Capacity (NCES CCD & State Administrative Registers)**\n")
        f.write("   - *Question Answered:* **How much teacher FTE does the educational system employ relative to enrollment?**\n")
        f.write("   - *Metric:* Students per teacher FTE / Teachers per 1,000 students.\n")
        f.write("   - *Grain:* Annual universal census across all 77 fully regional public LEAs in the KC metropolitan area (2014–15 to 2024–25).\n")
        f.write("   - *Core Finding:* Macro instructional capacity expanded significantly. Regional teacher FTE grew by **+8.86%** while enrollment fell by **-0.73%**, driving PTR from **14.85:1 down to 13.54:1**.\n\n")

        f.write("2. **Pillar 2: Actual Teacher-Reported Class Size (NCES SASS / NTPS Teacher Questionnaires)**\n")
        f.write("   - *Question Answered:* **What size classes do representative teachers report actually teaching?**\n")
        f.write("   - *Metric:* Departmentalized secondary teachers log section-by-section student headcounts for every class period taught (up to 10 sections), recording subject and grade level.\n")
        f.write("   - *Methodology:* Nationally and state-representative two-stage probability sample (~9,900 public schools and ~68,300 teachers in 2020–21; 55% overall weighted response rate). NCES applies survey weights for selection probability and nonresponse.\n")
        f.write("   - *Function:* Provides weighted survey estimates of average class size reported by representative departmentalized high-school teachers.\n")
        f.write("   - *Core Finding:* Neither state showed improving all-grade staffing density during the 2011–12 to 2017–18 window (MO PTR 13.8 to 14.1; KS PTR 13.0 to 14.2), while high-school class size also remained roughly stable (MO 21.8 to 22.5; KS 19.7 to 19.8), reinforcing that these are distinct measures rather than demonstrating a staffing/class-size divergence during this particular period.\n\n")

        f.write("3. **Pillar 3: Historic Ground-Truth & Daily Student Load (Jenkins v. Missouri Litigation Records)**\n")
        f.write("   - *Question Answered:* **What did Kansas City's audited master schedules and total daily assignments look like under judicial scrutiny?**\n")
        f.write("   - *Metric:* Courtroom master-schedule audits, student-classes, teaching assignments, and daily student contact loads ($R_t = \\sum_s n_s$).\n")
        f.write("   - *Grain:* KCMSD 1985 trial exhibits (K-58, K-59; *Jenkins v. Missouri*, 639 F. Supp. 19; affirmed 890 F.2d 65).\n")
        f.write("   - *Core Finding:* Forty years ago, federal courts looked beyond PTR, finding teaching assignments and daily loads 'more revealing' (*Jenkins v. Missouri*, 639 F. Supp. at 33; junior high teachers carried **154 students/day** across 5.66 periods and high school teachers carried **149 students/day** across 5.18 periods). Judge Clark established a binding remedial ceiling of **$\\le 125$ students per day**.\n\n")

        f.write("4. **Pillar 4: Modern Course-Level Empirical Proxies (OCR Civil Rights Data Collection)**\n")
        f.write("   - *Question Answered:* **Where within modern KC schools do particular courses depart from the averages?**\n")
        f.write("   - *Metric:* School-by-course average section load proxy ($\\bar{s}_c = E_c / S_c$).\n")
        f.write("   - *Grain:* Biennial federal census waves across KC high schools (2013–14 to 2023–24).\n")
        f.write("   - *Core Finding:* Across all operating regular high schools in the metro area, course averages are modest (~16.5–18.7: Algebra I 17.2, Geometry 18.7, Biology 16.5). However, **state and metro averages hide localized gateway bottlenecks**: specific urban and large suburban comprehensive campuses report localized bottlenecks of **25 to 31 students** (Wyandotte Algebra I at 28.5 across 46 sections, Lincoln Prep Geometry/Math at 29.5, Grandview Algebra/Geometry at 26–28, Shawnee Mission East/North at 26–28), which demonstrates how state and metro averages hide localized gateway pressure.\n\n")

        f.write("## 2. The Empirical Parallel Series (2011–12 to 2020–21)\n\n")
        f.write("| Survey Wave | Jurisdiction | Actual HS Class Size (SASS/NTPS) | State All-Grade PTR (CCD) | Class-Size / Macro-PTR Gap | Period Context |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :--- |\n")
        f.write("| **2011–12 (SASS)** | United States | **24.2** | 16.0:1 | **+8.2 students** | Clean Pre-Pandemic Baseline |\n")
        f.write("| | Missouri | **21.8** | 13.8:1 | **+8.0 students** | (SASS Table 7, CCD Table 2) |\n")
        f.write("| | Kansas | **19.7** | 13.0:1 | **+6.7 students** | (SASS Table 7, CCD Table 2) |\n")
        f.write("| **2017–18 (NTPS)** | United States | **23.3** | 15.9:1 | **+7.4 students** | Pre-Pandemic Staffing Expansion |\n")
        f.write("| | Missouri | **22.5** | 14.1:1 | **+8.4 students** | (NTPS Table A-7a) |\n")
        f.write("| | Kansas | **19.8** | 14.2:1 | **+5.6 students** | (NTPS Table A-7a) |\n")
        f.write(r"| **2020–21 (NTPS)\*** | United States | **21.0** | 15.4:1 | **+5.6 students** | Pandemic Year (NCES Category Revisions) |" + "\n")
        f.write(r"| | Missouri | **19.2** | 13.7:1 | **+5.5 students** | (Table ntps2021_sflt07_t1s) |" + "\n")
        f.write(r"| | Kansas | **17.4** | 14.1:1 | **+3.3 students** | (Table ntps2021_sflt07_t1s) |" + "\n\n")

        f.write("*Note: NCES explicitly warns that school-level categories changed in 2020–21 relative to earlier administrations, and pandemic remote/hybrid schedules perturbed student enrollments per period. The 2011–12 to 2017–18 comparison represents the clean, unperturbed pre-pandemic baseline.\n\n")

        f.write("## 3. The Core Analytical Insights\n\n")
        f.write("1. **Distinct Statistics Rather than Divergence:** Neither state showed improving all-grade staffing density during the 2011–12 to 2017–18 window (MO PTR 13.8 to 14.1; KS PTR 13.0 to 14.2), while high-school class size also remained roughly stable (MO 21.8 to 22.5; KS 19.7 to 19.8), reinforcing that these are distinct measures rather than demonstrating a staffing/class-size divergence during this particular period. The material expansion in teacher staffing density occurred in the KC metro panel over the 2014–15 to 2024–25 decade.\n\n")
        f.write("2. **Cross-Metric Distinction (Class Size vs. Macro PTR):** High-school departmentalized class sizes consistently exceed all-grade state PTRs by **5 to 8 students**. This gap reflects structural organizational filters: secondary bell-schedule planning multipliers ($\\phi = P_{\\text{std}} / P_{\\text{tch}}$, e.g. 5-of-7 planning periods requiring +20% FTE just to maintain class sizes) and specialized non-classroom roles (SPED, ELL, reading interventionists).\n\n")
        f.write("3. **Localized Bottlenecks vs. Regional Means:** While regional average high school course proxies sit around 16.5–18.7, high-volume gateway subjects in non-selective urban and comprehensive suburban campuses regularly experience acute localized crowding (26–31 students per class), creating intense localized workload pressure that building-wide and state-wide averages conceal.\n\n")

        f.write("## 4. Visual Artifact\n\n")
        f.write("### Figure 18: The Class-Size / Macro-PTR Gap Over Time\n")
        f.write("![Figure 18: Structural Staffing vs. Actual Class Size](../figures/fig18_structural_staffing_vs_actual_class_size.png)\n")

    print(f"Generated {report_path}")
    print("=== Execution Complete ===")

if __name__ == "__main__":
    generate_four_pillar_framework()
