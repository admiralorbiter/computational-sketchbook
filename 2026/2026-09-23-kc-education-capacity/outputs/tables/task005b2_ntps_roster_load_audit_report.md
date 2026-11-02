# Task 005B.2: NTPS Provenance & Reproducibility Audit Report
## Verifying Official NCES Published Estimates, Retracting Unverified Distributions, and Benchmarking Derived Schedule Loads

**Date:** September 2026  
**Status:** Task 005B.2 COMPLETE — Scientific Provenance Enforced  
**Evidence Architecture:** Class 1 (Measured / Published NCES Quantities) vs. Class 3 (Derived Schedule Benchmarks)  

---

## 1. Executive Summary: The Provenance Audit & Resolution

This audit evaluates the reproducibility and evidentiary provenance of all teacher class size and secondary roster-load estimates derived from the National Center for Education Statistics (NCES) National Teacher and Principal Survey (NTPS) and Schools and Staffing Survey (SASS).

### Core Findings & Epistemic Corrections:
1. **Verbatim Published Quantities Preserved:**
   - Official NCES published state and national departmentalized secondary class sizes are verified directly from published reference tables:
     - **2020–21 NTPS Table 7:** United States = **21.0**, Kansas = **17.4**, Missouri = **19.2** (Middle: US 22.0, KS 19.8, MO 18.5; Elementary self-contained: US 19.1, KS 17.9, MO 18.2).
     - **2017–18 NTPS Table A-7a:** United States = **23.3**, Kansas = **19.8**, Missouri = **22.5**.
     - **2011–12 SASS Table 69:** United States = **24.2**, Kansas = **20.5**, Missouri = **23.1**.
     - **2015–16 NTPS First Look Table 8:** United States = **26.0** (National only).
2. **Retraction of Reconstructed Survey Distributions:**
   - In previous working drafts, teacher-level roster percentiles (median, P75, P90) and tail probabilities ($P(R > 125)$, $P(R > 140)$, $P(R > 150)$) were computed using section multipliers and parametric assumptions rather than directly exported from an audited NCES DataLab session with replicate weights, unweighted $n$, and variance matrices.
   - **Action Taken:** In strict adherence to scientific integrity, **all unverified teacher-level percentiles and tail probabilities are formally deleted and retracted**. They are not presented as survey-measured distributions.
3. **Removal of 2015–16 State-Level Estimates:**
   - NCES documentation explicitly establishes that the **2015–16 NTPS was designed only for national representation**, not for state-representative estimates. State-representative sampling began with the 2017–18 NTPS administration.
   - **Action Taken:** The 2015–16 Kansas and Missouri state rows have been **completely removed**. The modern state longitudinal series is strictly: **2017–18 $\longrightarrow$ 2020–21**.
4. **Correction of NCES Technical Standards Attribution:**
   - In previous drafts, reporting flags (`!` and `‡`) were attributed to NCES Statistical Standard 4-2. NCES Standard 4-2 actually governs *Maintaining Confidentiality*, not statistical reliability.
   - **Action Taken:** Reporting conventions are now cited directly to the official published **NTPS Table 7 Technical Notes**:
     - `!`: *Interpret data with caution. The coefficient of variation (CV) is between 30% and 50% (i.e., the standard error is at least 30% and less than 50% of the estimate).*
     - `‡`: *Reporting standards not met. Either there are too few cases for a reliable analysis, or the coefficient of variation (CV) is 50% or greater (i.e., the standard error is 50% or more of the estimate).*
5. **Clear Classification of Derived Schedule Benchmarks:**
   - While the NTPS teacher questionnaire asks departmentalized teachers for their number of sections (T0065/T0240) and section-by-section student counts (T0260–T0269), public tables publish only average section size $\bar{{n}}$, not the joint distribution of total student assignments $E[\sum_j n_j]$.
   - Multiplying published section means by contract teaching periods (e.g., $17.4 \times 5 = 87.0$; $19.2 \times 6 = 115.2$; $24.5 \times 6 = 147.0$) produces valuable operational benchmarks, but these are now classified strictly as **Class 3: Derived Schedule Benchmarks**, not measured survey distributions.

---

## 2. Genuinely Published NCES Survey Quantities (Class 1)

The following table presents all verified quantities published directly by NCES in official reference tables. Every row represents an official public release:

| Survey Cycle | Geography | School Level | Instructional Arrangement | Published Class Size | Flag | Source Reference |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **2020–21 NTPS** | **United States** | Secondary / High School | Departmentalized | **21.0** | | NCES Table 7 |
| **2020–21 NTPS** | **Missouri** | Secondary / High School | Departmentalized | **19.2** | | NCES Table 7 |
| **2020–21 NTPS** | **Kansas** | Secondary / High School | Departmentalized | **17.4** | | NCES Table 7 |
| **2020–21 NTPS** | **United States** | Middle School | Departmentalized | **22.0** | | NCES Table 7 |
| **2020–21 NTPS** | **Missouri** | Middle School | Departmentalized | **18.5** | | NCES Table 7 |
| **2020–21 NTPS** | **Kansas** | Middle School | Departmentalized | **19.8** | | NCES Table 7 |
| **2020–21 NTPS** | **United States** | Elementary School | Self-Contained | **19.1** | | NCES Table 7 |
| **2020–21 NTPS** | **Missouri** | Elementary School | Self-Contained | **18.2** | | NCES Table 7 |
| **2020–21 NTPS** | **Kansas** | Elementary School | Self-Contained | **17.9** | | NCES Table 7 |
| **2017–18 NTPS** | **United States** | Secondary / High School | Departmentalized | **23.3** | | NCES Table A-7a |
| **2017–18 NTPS** | **Missouri** | Secondary / High School | Departmentalized | **22.5** | | NCES State Library |
| **2017–18 NTPS** | **Kansas** | Secondary / High School | Departmentalized | **19.8** | | NCES State Library |
| **2011–12 SASS** | **United States** | Secondary / High School | Departmentalized | **24.2** | | NCES SASS Table 69 |
| **2011–12 SASS** | **Missouri** | Secondary / High School | Departmentalized | **23.1** | | NCES SASS Table 69 |
| **2011–12 SASS** | **Kansas** | Secondary / High School | Departmentalized | **20.5** | | NCES SASS Table 69 |
| **2015–16 NTPS** | **United States** | Secondary / High School | Departmentalized | **26.0** | | NCES First Look Table 8 *(National Only)* |

> [!NOTE]
> **Longitudinal Trajectory:** Across the ten-year period from 2011–12 to 2020–21, departmentalized secondary class sizes reported by teachers in official NCES surveys have **declined moderately or remained flat** in both states and nationally:
> - **United States:** 24.2 (2012) $\longrightarrow$ 23.3 (2018) $\longrightarrow$ 21.0 (2021)
> - **Missouri:** 23.1 (2012) $\longrightarrow$ 22.5 (2018) $\longrightarrow$ 19.2 (2021)
> - **Kansas:** 20.5 (2012) $\longrightarrow$ 19.8 (2018) $\longrightarrow$ 17.4 (2021)
> 
> *Statewide survey estimates may mask metro/suburban differences.*

---

## 3. Class 3: Derived Schedule Benchmarks & The Jenkins 125 Ceiling

Under secondary departmentalized schooling, individual teacher student volume is determined by the interaction between average class size and contract bell schedules:

$$\text{{Derived Contact Load}} = \overline{{n}} \times P_{{\text{{teacher}}}}$$

The table below calculates derived student loads across three standard schedule regimes and compares them against the **historical remedial ceiling of $\le 125$ students per teacher per day** established in *Jenkins v. Missouri*, 639 F. Supp. 19 (W.D. Mo. 1985):

| Baseline Class Size Metric | Schedule Regime | Teaching Sections | Daily Contact Load | Active Grading Roster | Jenkins Remedial Ceiling | Load vs. Ceiling | Operating Assessment |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Kansas NTPS Mean (17.4)** | Contractual 5-of-7 | 5 | **87.0** | **87.0** | 125.0 | **-38.0** | Substantially below remedial ceiling |
| **Kansas NTPS Mean (17.4)** | Traditional 6-of-7 | 6 | **104.4** | **104.4** | 125.0 | **-20.6** | Well below remedial ceiling |
| **Kansas NTPS Mean (17.4)** | Alternating 8-Block | 3 | **52.2** | **104.4** | 125.0 | **-20.6** | Low daily contact; modest active roster |
| **Missouri NTPS Mean (19.2)** | Contractual 5-of-7 | 5 | **96.0** | **96.0** | 125.0 | **-29.0** | Substantially below remedial ceiling |
| **Missouri NTPS Mean (19.2)** | Traditional 6-of-7 | 6 | **115.2** | **115.2** | 125.0 | **-9.8** | Below remedial ceiling |
| **Missouri NTPS Mean (19.2)** | Alternating 8-Block | 3 | **57.6** | **115.2** | 125.0 | **-9.8** | Low daily contact; below ceiling |
| **United States NTPS Mean (21.0)** | Contractual 5-of-7 | 5 | **105.0** | **105.0** | 125.0 | **-20.0** | 20 students below remedial ceiling |
| **United States NTPS Mean (21.0)** | Traditional 6-of-7 | 6 | **126.0** | **126.0** | 125.0 | **+1.0** | Exactly touches remedial ceiling |
| **KC Suburban CRDC Core (24.5)** | Contractual 5-of-7 | 5 | **122.5** | **122.5** | 125.0 | **-2.5** | **Complies with Jenkins ceiling (SMSD model)** |
| **KC Suburban CRDC Core (24.5)** | Traditional 6-of-7 | 6 | **147.0** | **147.0** | 125.0 | **+22.0** | **Exceeds Jenkins ceiling by +22 students** |
| **KC Suburban CRDC Core (24.5)** | Alternating 8-Block | 3 | **73.5** | **147.0** | 125.0 | **+22.0 (Active)** | Low daily contact; high active grading roster |

---

## 4. The Microdata Transparency Boundary

The core conceptual contribution of this audit is documenting precisely **where public administrative data end and where restricted microdata begin**:

```
                       THE PUBLIC DATA TRANSPARENCY BOUNDARY
========================================================================================
LEVEL 1: Institutional Staffing  --> CCD / State Personnel Reports
                                     (FTE, Enrollment, Building Pupil/Teacher Ratio)
                                     STATUS: FULLY PUBLIC & AUDITED (Tasks 001-003)
----------------------------------------------------------------------------------------
LEVEL 2: Instructional Allocation --> State Role Codes / Special Education Densities
                                     (Classroom vs. Specialist Teachers, SPED FTE)
                                     STATUS: FULLY PUBLIC & RECONCILED (Task 003C)
----------------------------------------------------------------------------------------
LEVEL 3: Course-Level Capacity   --> CRDC Course Catalogs / NTPS State Tables
                                     (Average class size in Algebra II, Chemistry, etc.)
                                     STATUS: FULLY PUBLIC & AUDITED (Task 004A.1)
----------------------------------------------------------------------------------------
LEVEL 4: Teacher Roster Load     --> Sum of sections for named/individual teachers
                                     (R_i = sum_j n_{ij}, percentile tails, distribution)
                                     STATUS: RESTRICTED-USE / DATALAB ONLY
                                     NOT AVAILABLE IN PUBLIC AGGREGATE TABLES
========================================================================================
```

### The Analytical Implication:
1. Public data can rigorously establish structural staffing (+8.9% teacher FTE despite flat enrollment of -0.73%), specialist allocations (+2.7 ratio point wedge), regional school-course means (high teens) alongside mid-20s averages at selected large comprehensive suburban campuses, bell-schedule regimes (5-of-7 vs. 6-of-7), accommodations (+93.5% Section 504), and chronic absenteeism (24.69%).
2. Public data **cannot** reveal the empirical distribution of individual teacher active roster loads or the precise percentage of teachers carrying $>140$ students.
3. Therefore, claiming that modern teachers empirically carry fewer students than Jenkins-era teachers would require restricted-use microdata or custom DataLab extraction. What the public evidence *does* demonstrate is that **available public evidence does not indicate a dramatic increase in secondary roster headcount; modern schedule-based loads fall in a similar or lower range (87–147 students) compared to the Jenkins era (149–154 students)**, while student complexity has surged dramatically.

---

## 5. Provenance Sign-Off & Status

- **Task 005B.2 Status:** COMPLETE and FROZEN.
- **Unsupported Percentiles:** Deleted and retracted.
- **2015–16 State Rows:** Deleted (survey design restriction).
- **NCES Standards:** Technical notes correctly cited to NTPS Table 7 publication conventions.
- **Derived Benchmarks:** Clearly classified as Class 3 schedule models.
