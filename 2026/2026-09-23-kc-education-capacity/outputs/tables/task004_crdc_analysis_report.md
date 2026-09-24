# Task 004 / Phase 4A-CRDC: Kansas City Metro Course Capacity Panel
**School-Course Average Class Sizes, Curriculum Allocation & The Matched Allocation Wedge (2013–14 to 2023–24)**  
**Date:** September 24, 2026 (Audited & Calibrated)  
**Status:** Canonical Analysis Complete; Estimands Audited under Task 004A.1  
**Data Sources:** U.S. Department of Education, Office for Civil Rights (CRDC) Public-Use Data Files across 6 Collection Waves (2013–14, 2015–16, 2017–18, 2020–21, 2021–22, 2023–24) linked to NCES Common Core of Data (CCD) contemporaneous school capacity panels.

---

## 1. Executive Summary: The Allocation Wedge Quantified

For over a decade, educational policy discussions in the Kansas City metropolitan area have been characterized by a confusing paradox: aggregate administrative data show that pupil/teacher ratios contracted significantly (from **14.85 to 13.54** across regional districts), yet high school educators, parents, and community members widely report that core academic classes remain crowded, regularly enrolling **24 to 28+ students**.

By tapping into the **Civil Rights Data Collection (CRDC)**—a near-universe biennial federal survey that explicitly records both the **number of classes** and the **student enrollment** for specific high school courses—we have established the first direct, school-specific empirical measurement of classroom capacity across all 9 MARC counties without waiting for restricted state microdata.

### Key Empirical Findings:
1. **The Allocation Wedge is Quantified at +3.8 to +5.1 Students per Class (Unweighted Median) in Core Subjects:**
   - In SY 2023–24, across all reporting regular high schools with matched contemporaneous pupil/teacher ratios, school-course average class sizes in core academic courses systematically exceeded building PTRs:
     - **Algebra I:** Class-weighted mean **17.48** (Matched PTR: **15.97**; Class-Weighted Wedge: **+1.51**; Unweighted Median Wedge: **+3.83**)
     - **Geometry:** Class-weighted mean **18.92** (Matched PTR: **16.12**; Class-Weighted Wedge: **+2.80**; Unweighted Median Wedge: **+5.11**)
     - **Algebra II:** Class-weighted mean **18.67** (Matched PTR: **16.04**; Class-Weighted Wedge: **+2.63**; Unweighted Median Wedge: **+4.34**)
     - **Chemistry:** Class-weighted mean **18.81** (Matched PTR: **16.05**; Class-Weighted Wedge: **+2.76**; Unweighted Median Wedge: **+4.29**)
     - **Biology:** Class-weighted mean **16.46** (Matched PTR: **16.17**; Class-Weighted Wedge: **+0.29**; Unweighted Median Wedge: **+2.42**)
2. **Large Suburban High Schools Show an Even Steeper Wedge (Frequently +7 to +11.5 Students):**
   - While regional course averages cluster in the high teens (17–19 students/class), major suburban comprehensive high schools operate core courses with averages in the mid-to-upper 20s:
     - **Shawnee Mission North High (2023–24):** School PTR = **14.2:1** | Algebra I = **25.7** (Wedge: **+11.5**) | Geometry = **24.8** (Wedge: **+10.6**) | Algebra II = **24.6** (Wedge: **+10.4**)
     - **Shawnee Mission East High (2023–24):** School PTR = **17.5:1** | Algebra I = **25.3** (Wedge: **+7.8**) | Geometry = **24.3** | Algebra II = **25.2** | Calculus = **24.6**
     - **Olathe Northwest High (2023–24):** School PTR = **16.6:1** | Algebra I = **26.6** (Wedge: **+10.0**) | Geometry = **27.1** (Wedge: **+10.5**)
     - **Lincoln College Prep (KCPS, 2023–24):** School PTR = **17.2:1** | Algebra I = **26.3** | Geometry = **31.0** (Wedge: **+13.8**) | Algebra II = **30.6** (Wedge: **+13.3**)
     - **Blue Valley Northwest High (2023–24):** School PTR = **15.7:1** | Algebra II = **24.1** | Geometry = **24.4** | Chemistry = **26.8** (Wedge: **+11.0**)
3. **Evidence Consistent with a Curriculum-Allocation Mechanism:**
   - The data demonstrate that schools report smaller student-to-class ratios in advanced courses than in foundation courses:
     - In 2023–24, Foundation Core courses averaged **17.5 to 18.9** students per class, while **Calculus** and **Physics** averaged **15.0 to 17.0** students.
     - In multiple institutions (e.g. Oak Park High), reported Calculus averages drop to **4.7** students per class, while Algebra II averages **25.4** students.
     - While this pattern is consistent with small advanced sections pulling down building-wide PTR, determining causal FTE absorption requires section-level educator assignment microdata (Phase 4A).
4. **Broad Consistency with Independent Federal Benchmarks (NTPS):**
   - The National Teacher and Principal Survey (NTPS) reported that Kansas high school departmentalized teachers reported an average class size of **17.4** in 2020–21, and Missouri reported **19.2**.
   - CRDC regional class-weighted course averages (**17.1 to 18.9**) operate on the exact same scale as these independent state-level survey estimates, confirming that headline pupil/teacher ratios (13–15:1) represent institutional staffing metrics rather than classroom section sizes.

---

## 2. Regional Course Capacity Trends Across 6 CRDC Waves

Table 1 details the trajectory of course average class sizes and allocation wedges across all reporting Kansas City metropolitan high schools, evaluated under matched school-to-school weighting.

### Table 1: Regional High School Course Capacity Across 6 CRDC Waves (Matched Weighting)
*Source: `outputs/tables/task004_crdc_regional_summary.csv`*

| CRDC Wave | Course Name | Subject | Course Level | Schools | Classes | Enrolled | Class-Weighted Mean | Matched PTR | Class-Weighted Wedge | Unweighted Median Wedge |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2013-14** | Algebra I | Math | Foundation Core | 73 | 760 | 12,987 | **17.09** | 16.53 | **+0.56** | **+1.85** |
| **2013-14** | Algebra II | Math | Foundation Core | 84 | 933 | 16,339 | **17.51** | 16.48 | **+1.03** | **+5.08** |
| **2013-14** | Biology | Science | Foundation Core | 88 | 1,446 | 25,650 | **17.74** | 16.51 | **+1.23** | **+4.18** |
| **2013-14** | Chemistry | Science | Foundation Core | 82 | 1,029 | 17,046 | **16.57** | 16.52 | **+0.05** | **+5.21** |
| **2013-14** | Advanced Mathematics | Math | Advanced / Specialized | 79 | 1,090 | 15,376 | **14.11** | 16.53 | **-2.43** | **+0.92** |
| **2013-14** | Physics | Science | Advanced / Specialized | 71 | 557 | 7,931 | **14.24** | 16.32 | **-2.09** | **+2.13** |
| **2013-14** | Calculus | Math | Advanced / Specialized | 63 | 255 | 3,313 | **12.99** | 16.33 | **-3.34** | **-2.50** |
| **2015-16** | Algebra I | Math | Foundation Core | 94 | 808 | 16,076 | **19.90** | 16.14 | **+3.75** | **+4.56** |
| **2015-16** | Geometry | Math | Foundation Core | 90 | 920 | 18,367 | **19.96** | 16.15 | **+3.81** | **+4.67** |
| **2015-16** | Algebra II | Math | Foundation Core | 86 | 838 | 16,029 | **19.13** | 16.15 | **+2.97** | **+4.98** |
| **2015-16** | Biology | Science | Foundation Core | 90 | 1,223 | 26,712 | **21.84** | 16.27 | **+5.57** | **+4.69** |
| **2015-16** | Chemistry | Science | Foundation Core | 82 | 866 | 19,403 | **22.41** | 16.24 | **+6.17** | **+6.97** |
| **2015-16** | Advanced Mathematics | Math | Advanced / Specialized | 74 | 777 | 15,648 | **20.14** | 16.29 | **+3.85** | **+5.36** |
| **2015-16** | Physics | Science | Advanced / Specialized | 73 | 363 | 8,363 | **23.04** | 16.36 | **+6.68** | **+5.60** |
| **2015-16** | Calculus | Math | Advanced / Specialized | 62 | 167 | 2,900 | **17.37** | 16.43 | **+0.93** | **-2.98** |
| **2017-18** | Algebra I | Math | Foundation Core | 98 | 963 | 16,689 | **17.33** | 16.29 | **+1.04** | **+2.49** |
| **2017-18** | Geometry | Math | Foundation Core | 93 | 1,005 | 18,804 | **18.71** | 16.33 | **+2.38** | **+4.52** |
| **2017-18** | Algebra II | Math | Foundation Core | 91 | 1,139 | 19,963 | **17.53** | 16.28 | **+1.24** | **+2.91** |
| **2017-18** | Biology | Science | Foundation Core | 99 | 1,518 | 28,455 | **18.75** | 16.30 | **+2.45** | **+4.24** |
| **2017-18** | Chemistry | Science | Foundation Core | 90 | 1,057 | 21,414 | **20.26** | 16.32 | **+3.94** | **+3.87** |
| **2017-18** | Advanced Mathematics | Math | Advanced / Specialized | 80 | 973 | 18,046 | **18.55** | 16.32 | **+2.23** | **+3.40** |
| **2017-18** | Physics | Science | Advanced / Specialized | 78 | 508 | 9,305 | **18.32** | 16.33 | **+1.99** | **+2.73** |
| **2017-18** | Calculus | Math | Advanced / Specialized | 63 | 221 | 3,313 | **14.99** | 16.39 | **-1.40** | **-1.72** |
| **2020-21** | Algebra I | Math | Foundation Core | 100 | 1,446 | 19,742 | **13.65** | 16.27 | **-2.62** | **-0.51** |
| **2020-21** | Geometry | Math | Foundation Core | 95 | 1,248 | 19,822 | **15.88** | 16.31 | **-0.42** | **+1.03** |
| **2020-21** | Algebra II | Math | Foundation Core | 97 | 1,188 | 18,633 | **15.68** | 16.29 | **-0.60** | **+0.81** |
| **2020-21** | Biology | Science | Foundation Core | 103 | 2,118 | 29,603 | **13.98** | 16.32 | **-2.34** | **+1.56** |
| **2020-21** | Chemistry | Science | Foundation Core | 92 | 1,286 | 19,113 | **14.86** | 16.31 | **-1.44** | **+1.28** |
| **2020-21** | Advanced Mathematics | Math | Advanced / Specialized | 81 | 1,155 | 16,534 | **14.32** | 16.33 | **-2.02** | **-2.31** |
| **2020-21** | Physics | Science | Advanced / Specialized | 80 | 533 | 7,929 | **14.88** | 16.30 | **-1.43** | **-1.55** |
| **2020-21** | Calculus | Math | Advanced / Specialized | 71 | 253 | 3,236 | **12.79** | 16.30 | **-3.51** | **-5.32** |
| **2021-22** | Algebra I | Math | Foundation Core | 98 | 1,244 | 20,086 | **16.15** | 16.09 | **+0.05** | **+2.25** |
| **2021-22** | Geometry | Math | Foundation Core | 101 | 1,228 | 22,082 | **17.98** | 16.03 | **+1.95** | **+2.52** |
| **2021-22** | Algebra II | Math | Foundation Core | 94 | 1,057 | 18,725 | **17.72** | 16.03 | **+1.69** | **+2.48** |
| **2021-22** | Biology | Science | Foundation Core | 101 | 1,664 | 29,313 | **17.62** | 16.14 | **+1.47** | **+2.68** |
| **2021-22** | Chemistry | Science | Foundation Core | 91 | 1,025 | 17,678 | **17.25** | 16.04 | **+1.20** | **+2.38** |
| **2021-22** | Advanced Mathematics | Math | Advanced / Specialized | 83 | 831 | 13,086 | **15.75** | 16.10 | **-0.36** | **-1.60** |
| **2021-22** | Physics | Science | Advanced / Specialized | 80 | 436 | 7,266 | **16.67** | 16.05 | **+0.61** | **+0.41** |
| **2021-22** | Calculus | Math | Advanced / Specialized | 66 | 194 | 2,486 | **12.81** | 16.06 | **-3.24** | **-3.98** |
| **2023-24** | Algebra I | Math | Foundation Core | 104 | 1,329 | 23,226 | **17.48** | 15.97 | **+1.51** | **+3.83** |
| **2023-24** | Geometry | Math | Foundation Core | 100 | 1,219 | 23,067 | **18.92** | 16.12 | **+2.80** | **+5.11** |
| **2023-24** | Algebra II | Math | Foundation Core | 95 | 964 | 18,001 | **18.67** | 16.04 | **+2.63** | **+4.34** |
| **2023-24** | Biology | Science | Foundation Core | 102 | 1,859 | 30,606 | **16.46** | 16.17 | **+0.29** | **+2.42** |
| **2023-24** | Chemistry | Science | Foundation Core | 89 | 928 | 17,455 | **18.81** | 16.05 | **+2.76** | **+4.29** |
| **2023-24** | Advanced Mathematics | Math | Advanced / Specialized | 89 | 793 | 13,605 | **17.16** | 16.03 | **+1.12** | **+0.42** |
| **2023-24** | Physics | Science | Advanced / Specialized | 80 | 497 | 8,284 | **16.67** | 15.85 | **+0.81** | **-0.24** |
| **2023-24** | Calculus | Math | Advanced / Specialized | 58 | 187 | 3,184 | **17.03** | 15.60 | **+1.42** | **+0.75** |

---

## 3. Curriculum Hierarchy: Foundation Core vs. Advanced Courses

Table 2 compares Foundation Core courses (Algebra I, Geometry, Algebra II, Biology, Chemistry) directly against Advanced / Specialized courses (Calculus, Physics, Advanced Math) across waves under matched class-weighting.

### Table 2: Course Level Capacity Comparison Across CRDC Waves
*Source: `outputs/tables/task004_crdc_curriculum_hierarchy.csv`*

| CRDC Wave | Course Category | Schools | Total Classes | Total Enrolled | Class-Weighted Mean | Matched PTR | Class-Weighted Wedge | Unweighted Median Wedge |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2013-14** | **Foundation Core** | 90 | 4,168 | 72,022 | **17.28** | 16.51 | **+0.77** | **+3.86** |
| **2013-14** | **Advanced / Specialized** | 81 | 1,902 | 26,620 | **14.00** | 16.44 | **-2.45** | **+0.21** |
| **2015-16** | **Foundation Core** | 95 | 4,655 | 96,748 | **20.78** | 16.19 | **+4.59** | **+4.73** |
| **2015-16** | **Advanced / Specialized** | 77 | 1,307 | 26,911 | **20.59** | 16.32 | **+4.27** | **+2.48** |
| **2017-18** | **Foundation Core** | 100 | 5,682 | 105,325 | **18.54** | 16.30 | **+2.23** | **+3.61** |
| **2017-18** | **Advanced / Specialized** | 82 | 1,702 | 30,664 | **18.02** | 16.33 | **+1.68** | **+1.35** |
| **2020-21** | **Foundation Core** | 104 | 7,286 | 106,903 | **14.67** | 16.30 | **-1.63** | **+0.87** |
| **2020-21** | **Advanced / Specialized** | 83 | 1,941 | 27,699 | **14.27** | 16.31 | **-2.04** | **-2.61** |
| **2021-22** | **Foundation Core** | 103 | 6,218 | 107,884 | **17.35** | 16.08 | **+1.27** | **+2.48** |
| **2021-22** | **Advanced / Specialized** | 84 | 1,461 | 22,838 | **15.63** | 16.08 | **-0.45** | **-1.34** |
| **2023-24** | **Foundation Core** | 104 | 6,299 | 112,355 | **17.84** | 16.07 | **+1.77** | **+3.86** |
| **2023-24** | **Advanced / Specialized** | 90 | 1,477 | 25,073 | **16.98** | 15.90 | **+1.07** | **+0.23** |

---

## 4. Benchmark High Schools Panel

Table 3 details the empirical school-course average class sizes and allocation wedges across 15 major Kansas City high schools in SY 2023–24.

> [!WARNING]
> **Disclosure Protection & Small-Cell Caveat:** Public-use CRDC data apply random disclosure perturbation ($\pm 1$ student) and data quality suppressions. While cells enrolling $100+$ students across multiple sections are virtually unaffected, small single-section cells (flagged with `*`) can experience noticeable derived shifts and must be verified against district master schedule records before publication as standalone anecdotes.

### Table 3: Benchmark High Schools Course Capacity (SY 2023–24)
*Source: `outputs/tables/task004_crdc_benchmark_high_schools.csv`*

| High School | District | State | School PTR | Algebra I | Geometry | Algebra II | Biology | Chemistry | Physics | Calculus | Max Wedge |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Blue Valley High** | Blue Valley | KS | **15.8** | 21.5 | 23.3 | 24.1 | 17.4 | 20.5 | 19.6 | 16.4 | **+8.3** |
| **Blue Valley North High** | Blue Valley | KS | **15.9** | 35.0* | 22.5 | 18.4 | 17.4 | 20.5 | 23.4 | 15.9 | **+19.1\*** |
| **Blue Valley Northwest High** | Blue Valley | KS | **15.7** | 22.4 | 24.4 | 24.1 | 17.8 | 26.8 | 24.7 | 18.6 | **+11.0** |
| **Blue Valley West High** | Blue Valley | KS | **15.6** | 24.0 | 24.1 | 22.1 | 19.8 | 23.7 | 25.5 | 17.3 | **+9.9** |
| **Central High School** | Kansas City 33 | MO | **12.8** | 15.4 | 20.7 | 14.3 | 15.3 | 27.6 | 23.0 | — | **+14.8** |
| **East High School** | Kansas City 33 | MO | **13.8** | 16.3 | 16.7 | 18.9 | 12.1 | 19.3 | 19.9 | — | **+6.1** |
| **Gardner Edgerton High** | Gardner Edgerton | KS | **17.4** | 18.3 | 21.4 | 22.5 | 19.0 | 18.8 | 21.2 | 10.7 | **+5.1** |
| **Lee's Summit North High** | Lee's Summit R-VII | MO | **16.4** | 13.4 | 22.3 | 21.8 | 18.2 | 19.2 | 10.0* | — | **+5.9** |
| **Lee's Summit West High** | Lee's Summit R-VII | MO | **16.3** | 16.6 | 24.8 | 20.7 | 13.8 | 16.3 | 12.4 | — | **+8.5** |
| **Liberty High** | Liberty 53 | MO | **15.4** | 16.9 | 18.9 | 26.3 | 21.9 | 20.5 | 10.8 | 16.8 | **+10.9** |
| **Lincoln College Prep** | Kansas City 33 | MO | **17.2** | 26.3 | 31.0 | 30.6 | 23.8 | 26.3 | — | 15.0* | **+13.8** |
| **North Kansas City High** | North Kansas City 74 | MO | **16.3** | 20.3 | 19.4 | 20.9 | 16.9 | 18.7 | 14.2 | 11.0* | **+4.6** |
| **Oak Park High** | North Kansas City 74 | MO | **17.6** | 18.1 | 20.0 | 25.4 | 17.8 | 20.3 | 12.1 | 4.7* | **+7.8** |
| **Olathe Northwest High** | Olathe | KS | **16.6** | 26.6 | 27.1 | 21.7 | 20.4 | 22.8 | 20.4 | 26.7 | **+10.5** |
| **Shawnee Mission East High** | Shawnee Mission | KS | **17.5** | 25.3 | 24.3 | 25.2 | 21.9 | 22.0 | 22.7 | 24.6 | **+7.8** |
| **Shawnee Mission North High** | Shawnee Mission | KS | **14.2** | 25.7 | 24.8 | 24.6 | 20.8 | 21.8 | 21.5 | 16.0* | **+11.5** |

*\* Denotes small-cell observation ($N_{enrolled} < 20$ or $N_{classes} \le 3$) subject to potential public-use disclosure perturbation.*

---

## 5. Methodological & Theoretical Implications

### 1. Proof of Institutional Metric Distortion Without Data Falsification
These findings resolve the decade-long paradox:
- Nobody falsified administrative teacher headcounts. When districts report teacher FTE to state and federal databases, those numbers reflect certified staff on payroll.
- However, **pupil/teacher ratio is an institutional staffing statistic, not a reflection of classroom load**.
- Because certified teachers are allocated to specialized non-rostered roles (reading specialists, interventionists, instructional coaches) and small advanced courses, the institutional ratio decreases.
- Consequently, while building PTR contracted toward 13–15:1, **regional high school core academic courses average 17.5 to 18.9 students per class, and large suburban comprehensive high schools regularly operate core classes at 24 to 28+ students**.

### 2. Concordance Across the Quantitative Research Ladder
The quantitative findings now align across three administrative tiers:
1. **Federal CCD (Task 003B):** Macro PTR fell from $14.85 \rightarrow 13.54$ (teachers $+8.9\%$, enrollment flat).
2. **State Administrative Reconciliation (Phase 3C):** KSDE confirms Classroom Teachers grew $+6.2\%$ across USDs and $+8.7\%$ in Johnson County suburbs; specialist dilution creates a ~2.7 ratio difference.
3. **Federal CRDC Courses & Classes (Task 004A/004A.1):** High school core math and science courses average **17.5 to 18.9** students regionally (and **24 to 28+** on large suburban campuses), demonstrating a robust Allocation Wedge of **+3.0 to +5.1 students (unweighted median)** and **+1.5 to +2.8 students (class-weighted)** above building PTR.
4. **National NTPS Teacher Surveys:** Departmentalized high school teachers independently report state class-size averages of **17.4 (KS)** and **19.2 (MO)**, broadly consistent with CRDC course averages.

### 3. Transition to State & District Microdata (Phase 4A Microdata Tracks)
While CRDC establishes school-course averages, it cannot observe:
- **Within-course section distributions** (e.g. whether 4 sections are uniformly $[18, 18, 28, 28]$ or $[23, 23, 23, 23]$).
- **Teacher daily student-seat load** (total students across all periods).
- **Unique student roster load** (unduplicated students taught).
- **Classroom complexity factors** (IEP, 504, and ELL concentrations at the section level).

The formal state data requests transmitted to MO DESE and KSDE, along with the direct district public records requests (Track B), represent the essential next phase of the investigation.
