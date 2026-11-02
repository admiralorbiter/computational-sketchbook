# Study C / Phase 5.1: SASS & NTPS Survey Triangulation and Estimand Crosswalk
## Cross-Source Triangulation Between Administrative Census Data and Teacher Survey Benchmarks

**Date:** October 2026  
**Status:** Phase 5.1 COMPLETE — Calibrated Empirical Triangulation & Crosswalk  
**Working Repository:** `2026-10-04-classroom-capacity`  
**Prior Certified Phases:** Study A (Phases 0–3.2a: Measurement Certification) | Study B (Phases 4–4.1b: School Context Calibration)  
**Test Suite:** 44/44 tests passing (`pytest tests/`)

---

## 1. Executive Summary & Core Research Questions

This study establishes the empirical crosswalk between **universal administrative census data** (the Civil Rights Data Collection [CRDC] and Common Core of Data [CCD]) and **direct teacher self-reports** from the National Center for Education Statistics (NCES) sample surveys: the **Schools and Staffing Survey (SASS, 1999–2012)** and the **National Teacher and Principal Survey (NTPS, 2015–2021)**.

### The Four Governing Questions of Phase 5.1:
1. **How do teacher-reported survey benchmarks triangulate against CRDC-derived school-course estimands?**
2. **What do historical SASS and NTPS survey benchmarks show across the last two decades (1999–2000 to 2020–21) when accounting for series definition breaks?**
3. **How do Missouri, Kansas, and the Kansas City metropolitan area compare to the national distribution of state averages?**
4. **When section headcounts are combined with secondary bell schedules, how do modeled roster loads compare against historical remedial capacity benchmarks?**

---

### Key Findings Summary:

> [!IMPORTANT]
> **1. Cross-Source Triangulation of Class Size Estimands:**  
> The NTPS teacher-reported benchmark is much closer numerically to the CRDC enrollment-weighted lower-bound proxy ($C$) than to universal pupil-teacher ratios (PTR) or unweighted school-course cell means ($A$). Across contemporaneous waves, high school teachers reported departmentalized classes averaging **21.0** (2020–21), **23.3** (2017–18), and **26.0** (2015–16). Over the same periods, CRDC enrollment-weighted core secondary means were **20.10**, **21.51**, and **22.64** (gaps of $+0.90$, $+1.79$, and $+3.36$ students). By contrast, CRDC unweighted cell means ($A \approx 15.42\text{--}17.61$) undercount teacher survey benchmarks by **5.58 to 8.39 students**, and CCD macro PTR ($15.4\text{--}16.1$) undercounts by **5.60 to 9.90 students**. Estimand $C$ remains an enrollment-weighted lower-bound proxy because CRDC cannot observe within-cell section variance ($\sigma_i^2$).

> [!NOTE]
> **2. Historical Survey Benchmarks and Series Definition Breaks:**  
> The older SASS grade-span series reports grades 7–12 departmentalized averages of **23.6** (1999–00), **24.7** (2003–04), **23.4** (2007–08), and **26.8** (2011–12). A separate high-school-specific grades 9–12 series begins in 2011–12 at **24.2** and continues with NTPS benchmarks of **26.0** (2015–16), **23.3** (2017–18), and **21.0** (2020–21). These should be treated as overlapping benchmark series with different definitions, not one continuous trend. Furthermore, NCES explicitly cautions that 2020–21 school-level categories differ from previous administrations and were collected under pandemic instructional conditions. Meanwhile, elementary self-contained classrooms have remained remarkably flat across 22 years: **21.1** (1999–00), **20.4** (2003–04), **20.0** (2007–08), **21.2** (2011–12), and **19.1** (2020–21).

> [!TIP]
> **3. State Distribution Parameters & Distinguishing Units of Analysis:**  
> In the 2020–21 NTPS 50-state distribution of departmentalized high school class sizes, the national benchmark is **21.0**, with a state median of **20.0** (P25 = **17.80**, P75 = **21.80**). Kansas (**17.4**) ranks 40th of 51 jurisdictions, placing it in the **lower quartile** (below P25). Missouri (**19.2**) ranks 33rd of 51 (lower-middle). These statewide survey estimates pool all school districts and locales across each state. By contrast, individual comprehensive suburban high schools in the Kansas City metropolitan area report core course cell means averaging **22.3 to 24.5 students**—demonstrating that suburban teachers operate in course environments substantially larger than statewide aggregate benchmarks.

> [!WARNING]
> **4. Secondary Bell Schedules vs. Historical KCMSD Jenkins Benchmark:**  
> Secondary teacher contact volume is a multiplicative function of section headcount and bell schedules ($\text{Active Roster} = \bar{n} \times k$). In *Jenkins v. Missouri*, 639 F. Supp. 19 (W.D. Mo. 1985), the federal district court established a remedial goal of $\le 125$ students per teacher per day specifically for KCMSD secondary teachers. While surrounding suburban districts and national benchmarks are not bound by this desegregation order, it serves as a valuable historical reference for instructional capacity. In suburban core sections (24.5 students), a traditional 6-of-7 schedule places **147.0 active students** on a teacher's roster (**+22.0 students** above the 125 benchmark). Under a contractual 5-of-7 schedule (2 prep/duty periods), the roster drops to **122.5 students** (**-2.5 students** below the benchmark).

> [!CAUTION]
> **5. Illustrative Modeling Scenarios of Individual Instructional Accommodations:**  
> Multiplying certified school-level accommodation rates by modeled teacher rosters provides illustrative scenarios under proportional assignment (uniform random mixing), not observed teacher-level loads. In the secondary high school universe (2023–24 CRDC rates: 13.55% IDEA IEP, 5.45% Section 504, 9.49% EL), a teacher with 105 active students would proportionally encounter $\approx 19.9$ accommodated students and $\approx 10.0$ ELs; a teacher with 147 active students would proportionally encounter $\approx 27.9$ accommodated students and $\approx 14.0$ ELs. Chronic absence is excluded from roster models because school-level DG814 proxy rates cannot be treated as individual student probabilities. Because individual teacher rosters and non-random course tracking are unobserved in public data, **Hypothesis H5 is supported at the school-context level, while teacher-level loads remain unobserved.**

---

## 2. The Public Data Transparency Boundary

To preserve strict scientific integrity, this study adheres to the four-tier public data transparency hierarchy:

```
                       THE PUBLIC DATA TRANSPARENCY BOUNDARY
========================================================================================
LEVEL 1: Institutional Staffing  --> CCD Universal Personnel Reports
                                      (FTE Teachers, Enrollment, Macro Pupil/Teacher Ratio)
                                      STATUS: UNIVERSAL CENSUS / PUBLICLY AUDITED
----------------------------------------------------------------------------------------
LEVEL 2: School Program Context  --> CRDC School Catalogs / EDFacts DG814
                                      (Building IDEA IEP, 504 plans, EL counts, Absence proxy)
                                      STATUS: UNIVERSAL CENSUS / PUBLICLY AUDITED
----------------------------------------------------------------------------------------
LEVEL 3: Course / Class Capacity --> CRDC Course Catalogs / NTPS State Reference Tables
                                      (Estimand A cell mean, Estimand C proxy, NTPS survey mean)
                                      STATUS: PUBLICLY AVAILABLE
----------------------------------------------------------------------------------------
LEVEL 4: Teacher Active Roster   --> Sum of assigned students for individual teachers
                                      (R_i = sum_j n_{ij}, percentile tails, micro-rosters)
                                      STATUS: RESTRICTED-USE ONLY / NCES DATALAB
                                      UNOBSERVED IN PUBLIC ADMINISTRATIVE TABLES
========================================================================================
```

### Classification of Evidence:
- **Class 1: Measured / Published Survey Statistic:** Verbatim figures published directly by NCES in official reference tables (e.g., NTPS 2020–21 Table 7, SASS Digest tables).
- **Class 2: Administrative Census Derived Estimand:** School-course averages calculated from CRDC microdata (Estimand A cell mean, Estimand B section-weighted mean, and Estimand C enrollment-weighted lower-bound proxy).
- **Class 3: Derived Operational Model / Scenario:** Mathematical models combining section averages with bell schedules ($\text{Load} = \bar{n} \times k$) or proportional mixing scenarios.

---

## 3. Methodological Estimand Crosswalk: CRDC vs. NTPS

Table C02 presents the crosswalk between administrative census metrics (CCD and CRDC) and teacher-reported survey data (NTPS) across contemporaneous collection waves, restoring the frozen Study A nomenclature:

### Table C02: Methodological Crosswalk Across Class Size Estimands

| School Year | CRDC Wave | CCD Macro PTR | Estimand A: CRDC Unweighted Cell Mean | Estimand B: CRDC Section-Weighted Mean | Estimand C: CRDC Student-Weighted Proxy | NTPS HS Dept Class Size | NTPS Elem Self-Contained | Gap $C - A$ | Weighting Gap ($C - B$) | Staffing Wedge ($C - \text{PTR}$) | Triangulation Gap ($\text{NTPS} - C$) | Survey Wedge ($\text{NTPS} - \text{PTR}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2013–14** | 2013–14 | 16.1 | 17.40 | 16.90 | 22.14 | *No survey* | *No survey* | **+4.74** | **+5.24** | **+6.04** | — | — |
| **2015–16** | 2015–16 | 16.1 | 17.61 | 17.85 | 22.64 | **26.0** | *No survey* | **+5.03** | **+4.79** | **+6.54** | **+3.36** | **+9.90** |
| **2017–18** | 2017–18 | 16.0 | 16.69 | 17.38 | 21.51 | **23.3** | *No survey* | **+4.82** | **+4.12** | **+5.51** | **+1.79** | **+7.30** |
| **2020–21** | 2020–21 | 15.4 | 15.42 | 15.50 | 20.10 | **21.0** | **19.1** | **+4.68** | **+4.60** | **+4.70** | **+0.90** | **+5.60** |
| **2021–22** | 2021–22 | 15.4 | 15.52 | 15.47 | 20.43 | *No survey* | *No survey* | **+4.91** | **+4.95** | **+5.03** | — | — |
| **2023–24** | 2023–24 | 15.3 | 15.36 | 15.46 | 20.01 | *Pending* | *Pending* | **+4.65** | **+4.55** | **+4.71** | — | — |

*Source: [table_c02_crdc_vs_ntps_crosswalk.csv](tables/table_c02_crdc_vs_ntps_crosswalk.csv). Note: CRDC metrics reflect secondary core courses (Algebra II, Biology, Chemistry). CCD PTR from Digest Table 208.20. NTPS figures verbatim from NCES Table 7, Table 8, and Table A-7a.*

![Figure C02: CRDC vs NTPS Comparison](figures/fig_c02_crdc_vs_ntps_comparison.png)

### Key Methodological Insights from Table C02:
1. **Numerical Proximity to Estimand $C$:** In 2020–21, the difference between what high school teachers reported to NTPS (**21.0**) and the CRDC enrollment-weighted proxy (**20.10**) was **0.90 students** ($\approx 4\%$). In 2017–18, the difference was **1.79 students**. This demonstrates that the enrollment-weighted proxy falls much closer to teacher-reported survey benchmarks than unweighted administrative aggregates do.
2. **Divergence from Unweighted Cell Means (Estimand $A$):** In 2020–21, the CRDC unweighted cell mean was **15.42**—falling **5.58 students** below the teacher survey benchmark (21.0). Unweighted cell averages give equal weight to tiny rural campuses with single-digit course sections, understating the classroom environments experienced by most teachers.
3. **Divergence from Macro PTR:** CCD macro pupil-teacher ratios (15.3 to 16.1) understate teacher-reported high school classes by **5.60 to 9.90 students**. This gap reflects non-teaching preparation periods ($\approx 20\text{--}25\%$ of the instructional day) and specialized support staff.
4. **Estimand $C$ Remains a Lower-Bound Proxy:** Estimand $C$ weights school-course cell means by total enrollment ($\frac{\sum E_i \bar{C}_i}{\sum E_i}$), but cannot observe section-level variance within schools ($\frac{\sum K_i \sigma_i^2}{\sum E_i}$). Hence, Estimand $C$ is a mathematical lower-bound proxy for student-experienced section size.

---

## 4. Historical SASS & NTPS Benchmark Series

Table C01 compiles the published teacher survey benchmarks across 7 survey cycles:

### Table C01: Long-Run SASS/NTPS Class Size Series (US, MO, KS)

| Survey Cycle | School Year | Geography | School Level | Instructional Type | Published Mean | SE | Flag | Estimand Definition | Source Reference |
| :--- | :---: | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **1999–00 (SASS)** | 1999–00 | United States | Elementary School | Self-Contained | **21.1** | 0.10 | | Grades K–5/6 Self-Contained | Digest 2004 Table 68 |
| **1999–00 (SASS)** | 1999–00 | Missouri | Elementary School | Self-Contained | **20.7** | 0.60 | | Grades K–5/6 Self-Contained | Digest 2004 Table 68 |
| **1999–00 (SASS)** | 1999–00 | Kansas | Elementary School | Self-Contained | **18.3** | 0.40 | | Grades K–5/6 Self-Contained | Digest 2004 Table 68 |
| **1999–00 (SASS)** | 1999–00 | United States | Secondary / Grades 7–12 | Departmentalized | **23.6** | 0.10 | | Grades 7–12 Departmentalized | Digest 2004 Table 68 |
| **1999–00 (SASS)** | 1999–00 | Missouri | Secondary / Grades 7–12 | Departmentalized | **21.0** | 0.40 | | Grades 7–12 Departmentalized | Digest 2004 Table 68 |
| **1999–00 (SASS)** | 1999–00 | Kansas | Secondary / Grades 7–12 | Departmentalized | **20.9** | 0.30 | | Grades 7–12 Departmentalized | Digest 2004 Table 68 |
| **2003–04 (SASS)** | 2003–04 | United States | Elementary School | Self-Contained | **20.4** | 0.15 | | Grades K–5/6 Self-Contained | Digest 2006 Table 64 |
| **2003–04 (SASS)** | 2003–04 | Missouri | Elementary School | Self-Contained | **19.1** | 0.51 | | Grades K–5/6 Self-Contained | Digest 2006 Table 64 |
| **2003–04 (SASS)** | 2003–04 | Kansas | Elementary School | Self-Contained | **19.2** | 0.68 | | Grades K–5/6 Self-Contained | Digest 2006 Table 64 |
| **2003–04 (SASS)** | 2003–04 | United States | Secondary / Grades 7–12 | Departmentalized | **24.7** | 0.14 | | Grades 7–12 Departmentalized | Digest 2006 Table 64 |
| **2003–04 (SASS)** | 2003–04 | Missouri | Secondary / Grades 7–12 | Departmentalized | **22.9** | 0.65 | | Grades 7–12 Departmentalized | Digest 2006 Table 64 |
| **2003–04 (SASS)** | 2003–04 | Kansas | Secondary / Grades 7–12 | Departmentalized | **22.2** | 0.76 | | Grades 7–12 Departmentalized | Digest 2006 Table 64 |
| **2007–08 (SASS)** | 2007–08 | United States | Elementary School | Self-Contained | **20.0** | 0.14 | | Grades K–5/6 Self-Contained | Digest 2010 Table 71 |
| **2007–08 (SASS)** | 2007–08 | Missouri | Elementary School | Self-Contained | **19.4** | 0.53 | | Grades K–5/6 Self-Contained | Digest 2010 Table 71 |
| **2007–08 (SASS)** | 2007–08 | Kansas | Elementary School | Self-Contained | **19.5** | 0.64 | | Grades K–5/6 Self-Contained | Digest 2010 Table 71 |
| **2007–08 (SASS)** | 2007–08 | United States | Secondary / Grades 7–12 | Departmentalized | **23.4** | 0.16 | | Grades 7–12 Departmentalized | Digest 2010 Table 71 |
| **2007–08 (SASS)** | 2007–08 | Missouri | Secondary / Grades 7–12 | Departmentalized | **20.6** | 0.61 | | Grades 7–12 Departmentalized | Digest 2010 Table 71 |
| **2007–08 (SASS)** | 2007–08 | Kansas | Secondary / Grades 7–12 | Departmentalized | **21.0** | 0.94 | | Grades 7–12 Departmentalized | Digest 2010 Table 71 |
| **2011–12 (SASS)** | 2011–12 | United States | Elementary School | Self-Contained | **21.2** | 0.18 | | Grades K–5/6 Self-Contained | Digest 2019 Table 209.30 |
| **2011–12 (SASS)** | 2011–12 | Missouri | Elementary School | Self-Contained | **20.2** | 0.83 | | Grades K–5/6 Self-Contained | Digest 2019 Table 209.30 |
| **2011–12 (SASS)** | 2011–12 | Kansas | Elementary School | Self-Contained | **20.4** | 0.86 | | Grades K–5/6 Self-Contained | Digest 2019 Table 209.30 |
| **2011–12 (SASS)** | 2011–12 | United States | Secondary / Grades 7–12 | Departmentalized | **26.8** | 0.22 | | Grades 7–12 Departmentalized | Digest 2019 Table 209.30 |
| **2011–12 (SASS)** | 2011–12 | Missouri | Secondary / Grades 7–12 | Departmentalized | **26.8** | 1.18 | | Grades 7–12 Departmentalized | Digest 2019 Table 209.30 |
| **2011–12 (SASS)** | 2011–12 | Kansas | Secondary / Grades 7–12 | Departmentalized | **24.6** | 1.21 | | Grades 7–12 Departmentalized | Digest 2019 Table 209.30 |
| **2011–12 (SASS)** | 2011–12 | United States | High School | Departmentalized | **24.2** | — | | Grades 9–12 Departmentalized | SASS 2011–12 First Look Table 7 |
| **2011–12 (SASS)** | 2011–12 | Missouri | High School | Departmentalized | **21.8** | — | | Grades 9–12 Departmentalized | SASS 2011–12 First Look Table 7 |
| **2011–12 (SASS)** | 2011–12 | Kansas | High School | Departmentalized | **19.7** | — | | Grades 9–12 Departmentalized | SASS 2011–12 First Look Table 7 |
| **2015–16 (NTPS)** | 2015–16 | United States | High School | Departmentalized | **26.0** | — | | Grades 9–12 Departmentalized | NTPS 2015–16 First Look Table 8 |
| **2017–18 (NTPS)** | 2017–18 | United States | High School | Departmentalized | **23.3** | — | | Grades 9–12 Departmentalized | NTPS 2017–18 Table A-7a |
| **2017–18 (NTPS)** | 2017–18 | Missouri | High School | Departmentalized | **22.5** | — | | Grades 9–12 Departmentalized | NTPS 2017–18 Table A-7a |
| **2017–18 (NTPS)** | 2017–18 | Kansas | High School | Departmentalized | **19.8** | — | | Grades 9–12 Departmentalized | NTPS 2017–18 Table A-7a |
| **2020–21 (NTPS)** | 2020–21 | United States | High School | Departmentalized | **21.0** | — | | Grades 9–12 Departmentalized | NTPS 2020–21 Table 7 |
| **2020–21 (NTPS)** | 2020–21 | Missouri | High School | Departmentalized | **19.2** | — | | Grades 9–12 Departmentalized | NTPS 2020–21 Table 7 |
| **2020–21 (NTPS)** | 2020–21 | Kansas | High School | Departmentalized | **17.4** | — | | Grades 9–12 Departmentalized | NTPS 2020–21 Table 7 |
| **2020–21 (NTPS)** | 2020–21 | United States | Middle School | Departmentalized | **22.0** | — | | Grades 5/6–8 Departmentalized | NTPS 2020–21 Table 7 |
| **2020–21 (NTPS)** | 2020–21 | Missouri | Middle School | Departmentalized | **18.5** | — | | Grades 5/6–8 Departmentalized | NTPS 2020–21 Table 7 |
| **2020–21 (NTPS)** | 2020–21 | Kansas | Middle School | Departmentalized | **19.8** | — | | Grades 5/6–8 Departmentalized | NTPS 2020–21 Table 7 |
| **2020–21 (NTPS)** | 2020–21 | United States | Elementary School | Self-Contained | **19.1** | — | | Grades K–5/6 Self-Contained | NTPS 2020–21 Table 7 |
| **2020–21 (NTPS)** | 2020–21 | Missouri | Elementary School | Self-Contained | **18.2** | — | | Grades K–5/6 Self-Contained | NTPS 2020–21 Table 7 |
| **2020–21 (NTPS)** | 2020–21 | Kansas | Elementary School | Self-Contained | **17.9** | — | | Grades K–5/6 Self-Contained | NTPS 2020–21 Table 7 |

*Source: [table_c01_sass_ntps_longitudinal_series.csv](tables/table_c01_sass_ntps_longitudinal_series.csv).*

![Figure C01: SASS/NTPS Longitudinal Trajectory](figures/fig_c01_sass_ntps_longitudinal_trajectory.png)

### Methodological Notes on Series Definition Breaks:
- **Grades 7–12 vs. Grades 9–12 Series:** The older SASS series defined secondary departmentalized instruction across grades 7–12, reporting national averages of 23.6 (1999–00), 24.7 (2003–04), 23.4 (2007–08), and **26.8 (2011–12)**. In 2011–12, NCES also introduced a high-school-specific (grades 9–12) departmentalized series at **24.2**, which continued into NTPS at 26.0 (2015–16), 23.3 (2017–18), and 21.0 (2020–21). These represent overlapping series with distinct estimand scopes rather than a single continuous trend.
- **2020–21 Definition Changes & Pandemic Conditions:** NCES documentation explicitly warns that 2020–21 school-level categories differ from previous NTPS administrations and should be compared over time with caution. Additionally, the 2020–21 survey was administered during widespread COVID-19 instructional modifications.
- **Elementary Stability:** Elementary self-contained classrooms have remained consistently centered around 19 to 21 students across all administrations.

---

## 5. National 50-State Distribution & State Comparative Analysis

Table C03 summarizes the 2020–21 NTPS state-level distribution across all 50 states and the District of Columbia:

### Table C03: NTPS 2020–21 State Distribution Parameters

| Metric / Parameter | Secondary Departmentalized (Grades 9–12) | Middle School Departmentalized (Grades 5/6–8) | Elementary Self-Contained (Grades K–5/6) | Distributional Notes |
| :--- | :---: | :---: | :---: | :--- |
| **National Population Benchmark** | **21.0** | **22.0** | **19.1** | Published verbatim NCES Table 7 national estimate |
| **50-State + DC Mean** | **19.85** | **21.16** | **18.47** | Unweighted average across 51 state jurisdictions |
| **50-State + DC Median** | **20.00** | **20.90** | **18.30** | Median state entity |
| **25th Percentile (P25)** | **17.80** | **19.40** | **17.55** | Lower quartile threshold |
| **75th Percentile (P75)** | **21.80** | **23.10** | **19.35** | Upper quartile threshold |
| **State Minimum** | **13.4** (Maine) | **14.2** (Maine) | **14.2** (Maine) | Sparsely populated state entity |
| **State Maximum** | **27.6** (Nevada) | **27.5** (California) | **23.0** (California) | Rapidly growing western state entities |
| **Missouri State Average** | **19.2** | **18.5** | **18.2** | **Rank 33 of 51** (Lower-middle distribution, below state median of 20.00) |
| **Kansas State Average** | **17.4** | **19.8** | **17.9** | **Rank 40 of 51** (Lower quartile, below P25 threshold of 17.80) |

*Source: [table_c03_ntps_2020_21_state_distribution.csv](tables/table_c03_ntps_2020_21_state_distribution.csv).*

![Figure C03: NTPS State Distribution](figures/fig_c03_ntps_state_distribution.png)

### State Comparative Insights & Unit-of-Analysis Separation:
- **State Rankings:** Kansas (17.4) ranks 40th of 51 jurisdictions, placing it in the **lower quartile** nationally (below P25 = 17.80). Missouri (19.2) ranks 33rd of 51, falling in the lower-middle portion of the state distribution.
- **Separation of Units of Analysis:** State averages pool all schools and districts statewide without locale disaggregation. By contrast, individual comprehensive suburban high schools in the Kansas City metropolitan area report core course cell means averaging **22.3 to 24.5 students** (e.g., Shawnee Mission, Olathe, North Kansas City, Lee's Summit). A school-level mean cannot be directly evaluated against a distribution of state averages (which would commit an ecological fallacy); rather, the contrast demonstrates that suburban secondary teachers operate in instructional environments substantially larger than statewide aggregate benchmarks.

---

## 6. Secondary Bell Schedules & Historical KCMSD Jenkins Benchmark

Secondary departmentalized teachers instruct multiple sections each day. Total contact volume is a multiplicative function of section headcount and bell schedules:

$$\text{Active Roster Load} = \overline{n} \times k_{\text{active}}$$
$$\text{Daily Contact Load} = \overline{n} \times k_{\text{daily}}$$

In *Jenkins v. Missouri*, 639 F. Supp. 19 (W.D. Mo. 1985), the federal district court established a **remedial goal of $\le 125$ students per teacher per day** specifically for secondary teachers in the Kansas City, Missouri School District (KCMSD). While non-KCMSD districts and national benchmarks are not bound by this court order, it provides a valuable historical baseline for evaluating teacher instructional load.

### Table C04: Secondary Teacher Student Loads Under Standard Schedules vs. Jenkins Benchmark

| Operating Environment | Section Mean ($\overline{n}$) | Bell Schedule Regime | Daily Teaching Sections | Active Cycle Sections | Daily Contact Students | Active Grading Roster | Jenkins Historical Benchmark | Delta vs. Historical Benchmark | Benchmark Comparison | Operating Context |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **Kansas NTPS Mean** | 17.4 | Contractual 5-of-7 | 5 | 5 | **87.0** | **87.0** | 125.0 | **-38.0** | Below historical KCMSD benchmark (-38.0) | 5 teaching periods + 2 duty/prep periods |
| **Kansas NTPS Mean** | 17.4 | Traditional 6-of-7 | 6 | 6 | **104.4** | **104.4** | 125.0 | **-20.6** | Below historical KCMSD benchmark (-20.6) | 6 teaching periods + 1 prep period |
| **Kansas NTPS Mean** | 17.4 | Alternating 8-Block | 3 | 6 | **52.2** | **104.4** | 125.0 | **-20.6** | Below historical KCMSD benchmark (-20.6) | 6 active courses on A/B rotation; 3 daily |
| **Missouri NTPS Mean** | 19.2 | Contractual 5-of-7 | 5 | 5 | **96.0** | **96.0** | 125.0 | **-29.0** | Below historical KCMSD benchmark (-29.0) | 5 teaching periods + 2 duty/prep periods |
| **Missouri NTPS Mean** | 19.2 | Traditional 6-of-7 | 6 | 6 | **115.2** | **115.2** | 125.0 | **-9.8** | Below historical KCMSD benchmark (-9.8) | 6 teaching periods + 1 prep period |
| **Missouri NTPS Mean** | 19.2 | Alternating 8-Block | 3 | 6 | **57.6** | **115.2** | 125.0 | **-9.8** | Below historical KCMSD benchmark (-9.8) | 6 active courses on A/B rotation; 3 daily |
| **US National Benchmark** | 21.0 | Contractual 5-of-7 | 5 | 5 | **105.0** | **105.0** | 125.0 | **-20.0** | Below historical KCMSD benchmark (-20.0) | 5 teaching periods + 2 duty/prep periods |
| **US National Benchmark** | 21.0 | Traditional 6-of-7 | 6 | 6 | **126.0** | **126.0** | 125.0 | **+1.0** | Above historical KCMSD benchmark (+1.0) | 6 teaching periods + 1 prep period |
| **US National Benchmark** | 21.0 | Alternating 8-Block | 3 | 6 | **63.0** | **126.0** | 125.0 | **+1.0** | Above historical KCMSD benchmark (+1.0) | 6 active courses on A/B rotation; 3 daily |
| **KC Suburban Comp HS** | 22.3 | Contractual 5-of-7 | 5 | 5 | **111.5** | **111.5** | 125.0 | **-13.5** | Below historical KCMSD benchmark (-13.5) | 5 teaching periods + 2 duty/prep periods |
| **KC Suburban Comp HS** | 22.3 | Traditional 6-of-7 | 6 | 6 | **133.8** | **133.8** | 125.0 | **+8.8** | Above historical KCMSD benchmark (+8.8) | 6 teaching periods + 1 prep period |
| **KC Suburban Comp HS** | 22.3 | Alternating 8-Block | 3 | 6 | **66.9** | **133.8** | 125.0 | **+8.8** | Above historical KCMSD benchmark (+8.8) | 6 active courses on A/B rotation; 3 daily |
| **KC Suburban Core Academic** | 24.5 | Contractual 5-of-7 | 5 | 5 | **122.5** | **122.5** | 125.0 | **-2.5** | Below historical KCMSD benchmark (-2.5) | Contractual 5-of-7 model (SMSD) |
| **KC Suburban Core Academic** | 24.5 | Traditional 6-of-7 | 6 | 6 | **147.0** | **147.0** | 125.0 | **+22.0** | Above historical KCMSD benchmark (+22.0) | Traditional 6-period load |
| **KC Suburban Core Academic** | 24.5 | Alternating 8-Block | 3 | 6 | **73.5** | **147.0** | 125.0 | **+22.0** | Above historical KCMSD benchmark (+22.0) | Alternating 8-block load (NKC / Olathe) |

*Source: [table_c04_teacher_schedule_roster_loads.csv](tables/table_c04_teacher_schedule_roster_loads.csv).*

![Figure C04: Schedule Regime Roster Load](figures/fig_c04_schedule_regime_roster_load.png)

### Schedule Architecture Insights:
1. **Contractual Schedule Buffers:** In suburban high schools where core sections average 24.5 students, a traditional 6-of-7 schedule results in **147.0 active students** on a teacher's roster (**+22.0 students** above the historical 125 benchmark). Contractual schedules that limit teaching to 5-of-7 (granting 2 prep/duty periods) reduce the active roster to **122.5 students**, bringing total volume below the historical benchmark.
2. **Block Schedule Decoupling:** Alternating 8-block schedules decouple daily contact from cumulative grading load. While daily contact drops to **52 to 74 students/day** across 3 longer blocks, the cumulative active grading roster remains identical to the 6-period load (**104 to 147 unique students**).

---

## 7. Illustrative Scenarios of Proportional Accommodation Exposure

> [!WARNING]
> **Methodological Modeling Guardrail:**  
> Individual teacher rosters and student assignment non-randomness are unobserved in public administrative data. Table C05 presents **illustrative model scenarios** under the assumption of uniform proportional mixing within a school, applying certified Study B rates for secondary high schools. Chronic absenteeism is excluded because school-level DG814 snapshot rates cannot be treated as individual student probabilities. These scenarios do not constitute directly observed teacher-level data.

### Table C05: Illustrative Scenario of Proportional Accommodation Exposure (Secondary High School Universe)

| Scenario Archetype | School Level | Schedule Model | Active Roster Headcount | Proportional IDEA IEP (13.55%) | Proportional Section 504 (5.45%) | Proportional Combined Accommodations (19.00%) | Proportional English Learners (9.49%) | Model Assumptions & Notes |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Secondary Teacher: Contractual 5-of-7 (US NTPS Benchmark)** | High School / Secondary | 5 sections @ 21.0 students | **105.0** | **14.2** | **5.7** | **19.9** | **10.0** | Proportional mixing model; 5 teaching periods @ 21.0 national mean |
| **Secondary Teacher: Traditional 6-of-7 (US NTPS Benchmark)** | High School / Secondary | 6 sections @ 21.0 students | **126.0** | **17.1** | **6.9** | **23.9** | **12.0** | Proportional mixing model; 6 teaching periods @ 21.0 national mean |
| **Secondary Teacher: Alternating 8-Block (US NTPS Benchmark)** | High School / Secondary | 6 sections @ 21.0 students (3 daily) | **126.0** | **17.1** | **6.9** | **23.9** | **12.0** | Proportional mixing model; 6 active sections on A/B rotation |
| **Suburban Comprehensive HS Teacher (Contractual 5-of-7)** | High School / Secondary | 5 sections @ 24.5 core students | **122.5** | **16.6** | **6.7** | **23.3** | **11.6** | Proportional mixing model; CRDC measured core average (24.5) |
| **Suburban Comprehensive HS Teacher (Traditional 6-of-7)** | High School / Secondary | 6 sections @ 24.5 core students | **147.0** | **19.9** | **8.0** | **27.9** | **14.0** | Proportional mixing model; CRDC measured core average (24.5) |
| **Suburban Comprehensive HS Teacher (Alternating 8-Block)** | High School / Secondary | 6 sections @ 24.5 core students (3 daily) | **147.0** | **19.9** | **8.0** | **27.9** | **14.0** | Proportional mixing model; CRDC measured core average (24.5) |

*Source: [table_c05_teacher_iep_el_exposure.csv](tables/table_c05_teacher_iep_el_exposure.csv). Note: Rates from Study B national secondary pooled benchmarks (2023–24 CRDC: IDEA 13.55%, 504 5.45%, Combined 19.00%; EL 9.49% from balanced panel). Actual teacher rosters unobserved.*

---

## 8. Pre-Registered Hypotheses Status & Scientific Verdicts

| Hypothesis | Pre-Registered Claim | Phase 5.1 Evidence & Finding | Certified Status |
| :--- | :--- | :--- | :---: |
| **H1: PTR Divergence** | Class size systematically exceeds macro pupil-teacher ratio. | Both CRDC Estimand C (20.0–22.6) and NTPS teacher reports (21.0–26.0) exceed CCD macro PTR (15.3–16.1) by $+4.7$ to $+9.9$ students. | **CONFIRMED** |
| **H2: Weighting Matters** | Student-weighted averages exceed unweighted cell means. | CRDC Estimand C exceeds Estimand A by $+4.7$ to $+5.0$ students and Estimand B by $+4.1$ to $+5.2$ students. NTPS teacher reports align much closer to C than to A. | **CONFIRMED** |
| **H3: The Upper Tail Matters** | Averages obscure a substantial tail of students in large sections. | CONFIRMED in Study A: national CRDC distributions show a substantial enrollment share in high-mean school-course cells; Phase 5 adds contextual schedule scenarios showing how large course environments can translate into substantial modeled roster loads. | **CONFIRMED** |
| **H4: Class Size Persistence** | Class sizes remained flat or eased moderately. | Elementary self-contained has remained virtually static for 22 years (19.1–21.2); high school departmentalized benchmarks moved from 24.2 (2012) and 26.0 (2016) to 21.0 (2021). | **CONFIRMED** *(Series definition breaks noted)* |
| **H5: Instructional Load Escalation** | Individualized instructional obligations increased even as headcount was stable. | School-level concentrations of IEP, 504, and EL students increased substantially. However, because individual teacher rosters and assignment non-randomness are unobserved in public data, teacher-level load cannot be confirmed as an empirical fact. | **SUPPORTED — SCHOOL-CONTEXT INTENSIFICATION; TEACHER-LEVEL LOAD NOT YET ESTABLISHED** |

---

## 9. Deliverables & Next Phase Scope (Phase 6)

### Calibrated Deliverables:
- `src/build_ntps_sass_series.py`: Canonical SASS/NTPS ingestion pipeline (40 authentic published survey records; synthetic subject projections moved to separate scenario file).
- `src/analyze_ntps_sass_validation.py`: Estimand crosswalk (with restored Study A nomenclature) and schedule modeling engine.
- `tests/test_ntps_sass_series.py`: 9 unit tests verifying source provenance, nomenclature, figure-table identity, and modeling guardrails (44/44 pytest suite passing).
- `data/processed/ntps_sass_class_size_series.csv`: 40-record canonical published series.
- `data/processed/analyst_subject_scenarios.csv`: 24-record separate scenario projection table.
- `artifacts/tables/table_c01_sass_ntps_longitudinal_series.csv`: Historical benchmark table.
- `artifacts/tables/table_c02_crdc_vs_ntps_crosswalk.csv`: Estimand crosswalk table.
- `artifacts/tables/table_c03_ntps_2020_21_state_distribution.csv`: 50-state distribution table.
- `artifacts/tables/table_c04_teacher_schedule_roster_loads.csv`: Schedule regime roster load table.
- `artifacts/tables/table_c05_teacher_iep_el_exposure.csv`: Illustrative proportional exposure scenarios.
- `artifacts/figures/fig_c01_sass_ntps_longitudinal_trajectory.png`: Historical benchmark chart with series breaks.
- `artifacts/figures/fig_c02_crdc_vs_ntps_comparison.png`: Cross-source triangulation chart (dynamically generated from Table C02).
- `artifacts/figures/fig_c03_ntps_state_distribution.png`: 50-state horizontal bar distribution.
- `artifacts/figures/fig_c04_schedule_regime_roster_load.png`: Secondary schedules vs. historical KCMSD Jenkins benchmark.

---

### Scope & Evidentiary Boundaries for Phase 6 (Project STAR Experimental Replication)

When advancing to Phase 6 (Project STAR Replication), the following evidentiary boundaries will govern:
1. **Experimental Scope (K–3):** Project STAR experimentally evaluated classes of **13–17 students** against regular classes of **22–25 students** in grades K–3. It provides rigorous causal evidence on class size reductions in early elementary grades, but **cannot causally extrapolate to class size margins at 25 vs. 30 or 35 students in modern secondary schools**. That higher-grade/nonlinear question belongs to quasi-experimental studies (e.g., Maimonides' Rule / population variation) and the literature audit.
2. **Microdata Boundary (Public vs. Restricted):** Public Project STAR microdata enable exact replication of experimental achievement effects (Krueger 1999 intent-to-treat and treatment-on-treated models, school fixed effects, attrition tests, and non-compliance audits). However, long-run economic outcomes (Chetty et al. 2011) rely on confidential IRS tax record linkages that are restricted; Phase 6 will audit and synthesize published Chetty et al. findings rather than claiming to recreate restricted tax linkages from public data.
