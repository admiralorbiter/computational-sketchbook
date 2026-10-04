# Study B Measurement Certification: School-Level Instructional Load & Context Intensification (Phase 4.1 Calibration Patch)

**Study:** Study B — Teacher Instructional Load & Classroom Context  
**Document Type:** Certified Calibration & Empirical Findings  
**Date:** October 4, 2026  
**Status:** **CERTIFIED (Phase 4.1 Calibration Patch Complete)**  
**Preregistration Hypotheses Addressed:** H5  
**Primary Deliverables:**
- Canonical Context Panel: [`data/processed/school_context_panel.parquet`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/data/processed/school_context_panel.parquet) (582,178 school-waves)
- Secondary School Panel: [`data/processed/school_context_secondary_panel.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/data/processed/school_context_secondary_panel.csv) (163,027 school-waves)
- Certified Tables: [`artifacts/tables/table_b01_longitudinal_dimensions_national.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/tables/table_b01_longitudinal_dimensions_national.csv), [`table_b02_balanced_school_panel_context.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/tables/table_b02_balanced_school_panel_context.csv), [`table_b03_class_size_vs_context_bivariate.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/tables/table_b03_class_size_vs_context_bivariate.csv), [`table_b04_kc_metro_vs_national_context.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/tables/table_b04_kc_metro_vs_national_context.csv)
- Certified Visualizations: [`artifacts/figures/fig_b01_longitudinal_context_dimensions.png`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/figures/fig_b01_longitudinal_context_dimensions.png), [`fig_b02_class_size_bins_vs_context.png`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/figures/fig_b02_class_size_bins_vs_context.png), [`fig_b03_chronic_absenteeism_distribution_shift.png`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/figures/fig_b03_chronic_absenteeism_distribution_shift.png)

---

## 1. Executive Summary & Calibration Overview

Phase 4.1 executes a comprehensive methodological calibration patch for Study B. Following rigorous audit, all empirical headline claims, longitudinal trend series, balanced panel comparisons, and weighting identities have been re-anchored on defensible federal administrative foundations.

### Headline Empirical Findings

1. **Class Size Trajectory Eased Rather Than Remained Flat:**
   - Over the full 2013–14 to 2023–24 decade, student/enrolled-weighted secondary STEM class size declined from **22.40 to 19.72** students (a **12.0% easing**, or -2.68 students).
   - Post-2020, secondary class sizes fully stabilized in the narrow range of **19.7 to 20.1** students (2020–21: 19.90; 2021–22: 20.08; 2023–24: 19.72).
   - Macro campus PTR similarly eased from **15.36 to 14.10**.
   - *Substantive implication:* The core empirical phenomenon is not that headcount remained flat while demands exploded; rather, **even as numerical secondary class size eased by 12% and stabilized at ~20 students, the instructional environment surrounding the secondary classroom became substantially more intensive across multiple distinct dimensions.**

2. **Section 504 Accommodation Growth More Than Doubled:**
   - The share of secondary students served under Section 504-only rose from **2.24% in 2013–14 to 5.45% in 2023–24** in pooled student calculations (**+143% relative growth**), and from **2.15% to 5.06%** in school-weighted averages (**+135%**).
   - Combined students served under IDEA or Section 504-only rose from **13.79% to 19.00% of all enrolled secondary students** (reaching nearly **1 in every 5 enrolled students** nationally).
   - Within the continuously reporting 6-wave balanced panel ($N = 11,286$ secondary schools), pooled Section 504-only prevalence surged from **2.29% to 5.84%** (**+155% relative increase** on identical schools).

3. **Language Diversity Expanded by Over 60%:**
   - English Learner (EL) prevalence expanded from **5.64% in 2013–14 to 9.11% in 2023–24** in pooled secondary student calculations (**+61.5% relative growth**), and from **5.24% to 7.66%** in school-weighted averages.
   - In the 6-wave balanced panel, pooled EL prevalence rose from **5.26% to 9.49%** (**+80.4% relative growth** on identical schools).

4. **Severe Chronic Attendance Shock Confirmed Under Consistent Federal Post-2016 Definition:**
   - Disconnecting the incompatible pre-2016 CRDC definition (15+ days missed) from the post-2016 EDFacts definition ($\ge 10\%$ of enrolled days), secondary school chronic absenteeism escalated dramatically:
   - In the matched balanced panel of **20,075 identical secondary schools** continuously observed under EDFacts, median chronic absenteeism surged from **18.90% in 2017–18 to 31.96% in 2021–22** (**+13.06 percentage points / +69.1% relative increase**).
   - When excluding schools where student turnover resulted in cumulative counts exceeding October snapshot enrollment (clean $\le 100\%$ sample), the matched median rose from **17.85% to 30.08%** (**+12.23 percentage points / +68.5% relative increase**).
   - The share of secondary schools experiencing severe attendance disruption ($\ge 30\%$ chronically absent) jumped from **20.7% in 2017–18 to 57.0% in 2021–22** (+36.3 percentage points).

---

## 2. Methodological Calibrations Certified in Phase 4.1

The following nine calibration patches have been implemented, tested, and certified:

### Calibration 1: Federal Chronic Absenteeism Definition Break
- **Federal Background:** The 2013–14 and 2015–16 CRDC defined a chronically absent student as someone absent 15 or more school days during the academic year. Beginning in 2016–17 under the Every Student Succeeds Act (ESSA) and the transition to EDFacts Data Group 814 (DG814), the federal definition standardized to missing 10% or more of enrolled school days.
- **Correction Applied:** 
  1. Separate data fields and rate calculations were created: `crdc_absent_15d_count` / `pct_crdc_absent_15d` for 2013–14 and 2015–16; `edfacts_absent_10pct_count` / `pct_edfacts_absent_10pct` for 2017–18, 2020–21, and 2021–22.
  2. The previous cross-regime comparison (14.29% $\to$ 32.29%, "+126%") was invalid due to changing thresholds and has been completely removed.
  3. The headline longitudinal attendance result is anchored strictly on the consistent post-2016 EDFacts regime: **18.90% in 2017–18 $\to$ 31.96% in 2021–22 (+69.1%)** in matched schools.
  4. 2020–21 chronic absenteeism data ($N = 1,501$ secondary schools out of 24,684 in the class-size panel, or **6.0% coverage**) suffered massive non-reporting due to federal COVID waivers under ESSA. It is formally marked with `is_absent_waiver_year = True`, excluded from continuous trend lines, and displayed as a disconnected hollow marker.

### Calibration 2: Denominator Provenance & Mobility Flags
- **Provenance Discrepancy:** EDFacts DG814 counts students who were enrolled at any point during a 12-month period and missed $\ge 10\%$ of enrolled days. CRDC school enrollment is an October snapshot. In high-mobility schools, alternative education campuses, and transfer centers, cumulative annual students exceed October enrollment.
- **Correction Applied:**
  1. The code no longer silently clips ratios at 100.
  2. A dedicated boolean flag is created: `flag_absent_gt_enrollment = (chronic_absent_count > school_enrollment)`.
  3. Nationally, this flag identifies 7.1% of secondary schools in 2017–18 and 8.5% in 2021–22.
  4. Two distinct rates are provided and reported side-by-side: `pct_edfacts_absent_10pct` (unclipped raw ratio) and `pct_chronic_absent_clean` (masked to NaN for flagged schools). Both series demonstrate the identical ~68–69% surge.

### Calibration 3: Weighting Identities & Metric Precision
- **Weighting Separation:** To avoid confusion between school-level averages and population student shares, both estimands are reported side-by-side across all tables:
  - **School-Weighted Mean:** $\frac{1}{M}\sum \frac{Y_i}{E_i}$ (reflects the experience of the average school campus).
  - **Pooled Student-Weighted Rate:** $\frac{\sum Y_i}{\sum E_i}$ (reflects the experience of the average enrolled secondary student).
- **Rule Enforced:** The phrasing "X% of students" is strictly restricted to pooled student-weighted rates.

### Calibration 4: Construct Terminology for Section 504
- **Legal Background:** CRDC explicitly disaggregates students with disabilities into two mutually exclusive federal categories:
  1. Students served under the Individuals with Disabilities Education Act (IDEA).
  2. Students served under Section 504 only (excluding students served under IDEA).
  While written Section 504 accommodation plans are standard administrative practice, 34 C.F.R. Part 104 does not strictly mandate a written document in every single case.
- **Terminology Certified:**
  - Renamed from "students with formal legal plans" to: **"students served under IDEA or Section 504-only"** or **"students carrying individualized disability-related service or accommodation obligations."**
  - Combining IDEA and 504 counts (`idea_or_504_count`) is mathematically valid because CRDC's 504 field explicitly excludes IDEA students.

### Calibration 5: Measure-Specific Balanced Panels (Table B2)
- **Methodological Fix:** The previous panel called 18,606 schools "balanced" based solely on presence in the course panel, despite absenteeism missingness in 2020–21. Table B2 is now reconstructed as three measure-specific balanced panels:
  - **Panel A (Accommodations & EL Balanced):** Exactly **11,286 secondary schools** continuously observed with valid IDEA, Section 504, and EL data across all 6 waves from 2013–14 through 2023–24.
  - **Panel B (EDFacts Chronic Absenteeism Balanced):** Exactly **20,075 secondary schools** continuously observed under the consistent EDFacts definition in both 2017–18 and 2021–22.
  - **Panel C (CRDC 15+ Days Absenteeism Balanced):** Exactly **21,470 secondary schools** continuously observed under the CRDC 15+ days definition in both 2013–14 and 2015–16.

### Calibration 6: Harmonized Weighting & Kansas City Canonical PTR (Table B4)
- **Harmonized Weighting:** Table B4 previously reported an unweighted average of school enrollment-weighted class size (17.37), conflicting with Table B1's national figure (22.40). Table B4 now reports student-weighted class size ($\sum E_i \bar{C}_i / \sum E_i$), producing exact alignment (22.40 National, 22.51 KC in 2013–14; 20.08 National, 19.06 KC in 2021–22).
- **Canonical KC PTR:** Raw CRDC staffing ratios in 2021–22 produced an anomalous KC mean PTR of 20.91 due to an unedited outlier alternative program ("500 Reach", reporting 0.2 FTE teachers). Table B4 now carries forward the validated canonical CCD PTR from Phase 3, resolving the anomaly: **2021–22 KC mean PTR is 13.76**, aligning cleanly with adjacent waves (14.25 in 2017–18, 14.34 in 2020–21, 13.82 in 2023–24).

### Calibration 7: Strict Nonbinary (_X) Reserve-Code Semantics
- **Frequency Audit Results:**
  - In **2023–24 CRDC**, 100% of schools (97,094 / 97,094) report `-10` across all `_X` variables (`TOT_ENR_X`, `IDEA_X`, `504_X`, `EL_X`). Code `-10` indicates structurally not collected / reserved.
  - In **2021–22 CRDC**, 92,805 schools (94.7%) report `-9` (not collected/optional); 2,850 (2.9%) report `-12` (not applicable); exactly 0 report privacy suppression (`-5`); and 2,354 schools report positive nonbinary enrollment.
- **Helper Implementation:** `sum_enrollment_with_nonbinary()` explicitly distinguishes structural skips (`-9`, `-10`, `-12`, which default to binary $M + F$) from suppression (`-5`, `-6`, which evaluate to NaN under `require_complete=True`).

### Calibration 8: Toned-Down Mechanism Claims
- **504 Staffing:** Removed overstatements that Section 504 students "receive no extra aides." Acknowledged that while Section 504 obligations require general education teachers to implement accommodations in regular classrooms, staffing models and related aids vary across districts.
- **EL Instruction:** Replaced universal claims of "dual-language materials" with accurate language: **language scaffolding, accessible instruction, and appropriate language supports.**

### Calibration 9: Strict Epistemic Guardrail & H5 Hypothesis Verdict
- **Epistemic Principle:** School-level prevalence describes the surrounding institutional context; it does NOT represent the composition of any particular Biology, Geometry, or Physics section.
- **Text Cleaned:** Removed all statements projecting school-level percentages onto hypothetical teacher rosters (e.g. struck "a teacher with five 20-student sections now manages 32 chronically absent students").
- **H5 Preregistration Verdict:**
  > **SUPPORTED — SCHOOL-CONTEXT INTENSIFICATION; TEACHER-LEVEL LOAD NOT YET ESTABLISHED**
  > (Phase 4 confirms substantial school-level context intensification; verification of micro-level teacher rosters and individualized workload is reserved for Phase 5 / NTPS).

---

## 3. Certified Tables

### Table B1: National Longitudinal Trajectories Across Separate Dimensions (2013–14 to 2023–24)
*Universe: Secondary schools offering core STEM courses ($N = 23,939$ to $27,983$ schools per wave).*

| CRDC Wave | School Year | Schools ($N$) | Student-Wt Class Size | Campus PTR | School % IDEA | Pooled % IDEA | School % 504 | Pooled % 504 | School % IDEA/504 | Pooled % IDEA/504 | School % EL | Pooled % EL | EDFacts 10% Median | Clean 10% Median | Pooled 10% Absent | EDFacts Valid $N$ | Flagged $>100\%$ |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2013–14** | 2013–14 | 27,983 | 22.40 | 15.36 | 14.82% | 11.60% | 2.15% | 2.24% | 17.00% | 13.79% | 5.24% | 5.64% | *Regime 1* (14.20%) | — | 18.17% | 27,982 | 0.7% |
| **2015–16** | 2015–16 | 23,939 | 22.23 | 14.85 | 16.00% | 11.98% | 2.73% | 2.78% | 18.70% | 14.69% | 5.11% | 5.59% | *Regime 1* (17.32%) | — | 21.08% | 23,935 | 1.1% |
| **2017–18** | 2017–18 | 24,326 | 21.17 | 14.59 | 15.75% | 12.47% | 3.23% | 3.41% | 18.99% | 15.88% | 5.52% | 6.23% | **19.10%** | **17.91%** | 21.82% | 21,645 | 7.1% |
| **2020–21** | 2020–21 | 24,684 | 19.90 | 14.38 | 16.73% | 13.12% | 4.15% | 4.39% | 20.91% | 17.35% | 6.27% | 7.04% | *Waiver Year* (21.96%) | 21.37% | 29.71% | 1,486 | 2.5% |
| **2021–22** | 2021–22 | 25,147 | 20.08 | 14.30 | 17.09% | 13.24% | 5.41% | 4.68% | 19.83% | 16.64% | 8.75% | 7.68% | **32.29%** | **30.08%** | 34.74% | 22,733 | 8.5% |
| **2023–24** | 2023–24 | 25,026 | 19.72 | 14.10 | 16.89% | 13.55% | 5.06% | 5.45% | 21.95% | 19.00% | 7.66% | 9.11% | — | — | — | 0 | — |

*Notes:*  
1. *Regime 1 (2013–14 and 2015–16) reflects CRDC definition of 15+ school days missed.*  
2. *Regime 2 (2017–18 onward) reflects federal EDFacts DG814 definition of missing $\ge 10\%$ of enrolled days.*  
3. *2020–21 chronic absenteeism had ~6% reporting coverage due to federal COVID waivers and is non-representative.*  
4. *"Flagged $>100\%$" identifies schools where 12-month cumulative absent count exceeded October snapshot enrollment due to student mobility.*

---

### Table B2: Longitudinal Changes within Measure-Specific Balanced Panels

#### Panel A: 6-Wave Accommodations & EL Balanced Panel ($N = 11,286$ continuously reporting secondary schools)
| Wave | School Year | Student-Wt Class Size | Campus PTR | School % IDEA | Pooled % IDEA | School % 504 | Pooled % 504 | School % IDEA/504 | Pooled % IDEA/504 | School % EL | Pooled % EL |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2013–14** | 2013–14 | 22.24 | 16.30 | 12.39% | 11.52% | 2.36% | 2.29% | 14.75% | 13.81% | 4.80% | 5.26% |
| **2015–16** | 2015–16 | 22.38 | 16.22 | 12.69% | 11.76% | 2.98% | 2.91% | 15.67% | 14.67% | 5.03% | 5.56% |
| **2017–18** | 2017–18 | 21.35 | 15.84 | 12.96% | 12.01% | 3.67% | 3.60% | 16.63% | 15.61% | 5.73% | 6.33% |
| **2020–21** | 2020–21 | 19.40 | 15.65 | 13.82% | 12.81% | 4.82% | 4.75% | 18.65% | 17.56% | 6.69% | 7.38% |
| **2021–22** | 2021–22 | 19.78 | 15.47 | 13.97% | 13.01% | 5.18% | 5.12% | 19.15% | 18.13% | 7.24% | 8.00% |
| **2023–24** | 2023–24 | 19.64 | 15.32 | 14.30% | 13.30% | 5.83% | 5.84% | 20.13% | 19.14% | 8.45% | 9.49% |
| **Change** | *Decade Shift* | **-2.60 (-11.7%)** | **-0.98** | **+1.91 pp** | **+1.78 pp** | **+3.47 pp (+147%)** | **+3.55 pp (+155%)** | **+5.38 pp** | **+5.33 pp** | **+3.65 pp** | **+4.23 pp (+80.4%)** |

#### Panel B: Matched EDFacts Chronic Absenteeism Panel ($N = 20,075$ continuously reporting secondary schools)
| Wave | School Year | School Median % Absent | Clean Median % Absent ($\le 100\%$) | School Mean % Absent | Clean Mean % Absent | Pooled % Absent | Flagged $>100\%$ |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **2017–18** | 2017–18 | 18.90% | 17.85% | 31.91% | 22.55% | 21.74% | 6.44% |
| **2021–22** | 2021–22 | 31.96% | 30.08% | 44.85% | 33.88% | 34.75% | 7.70% |
| **Change** | *Post-COVID Surge* | **+13.06 pp (+69.1%)** | **+12.23 pp (+68.5%)** | **+12.94 pp** | **+11.33 pp** | **+13.01 pp (+59.8%)** | +1.26 pp |

#### Panel C: Matched CRDC 15+ Days Absenteeism Panel ($N = 21,470$ continuously reporting secondary schools)
| Wave | School Year | School Median % Absent | Clean Median % Absent | School Mean % Absent | Clean Mean % Absent | Pooled % Absent | Flagged $>100\%$ |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **2013–14** | 2013–14 | 15.67% | 15.53% | 21.68% | 20.72% | 19.36% | 0.77% |
| **2015–16** | 2015–16 | 17.50% | 17.29% | 23.47% | 22.48% | 21.06% | 0.93% |
| **Change** | *Early CRDC Drift* | **+1.83 pp (+11.7%)** | **+1.76 pp** | **+1.79 pp** | **+1.76 pp** | **+1.70 pp** | +0.16 pp |

---

### Table B3: Class Size Bins $\times$ Surrounding Context (2021–22 & 2023–24)

| Wave | Class Size Bin | Schools ($N$) | % Schools | Mean School Enr | Student-Wt Class Size | Campus PTR | School % IDEA | Pooled % IDEA | School % 504 | Pooled % 504 | School % IDEA/504 | Pooled % IDEA/504 | School % EL | Pooled % EL | EDFacts 10% Median | Clean 10% Median | Pooled 10% Absent |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2021–22** | $<20$ | 18,537 | 73.7% | 529.6 | 14.71 | 13.13 | 18.37% | 13.83% | 5.83% | 4.97% | 20.79% | 17.22% | 8.73% | 7.45% | 32.76% | 30.03% | 35.82% |
| **2021–22** | $20\text{--}24$ | 3,975 | 15.8% | 1,037.0 | 22.24 | 16.65 | 13.60% | 12.58% | 4.65% | 4.76% | 17.79% | 16.44% | 8.76% | 8.10% | 31.28% | 30.81% | 34.11% |
| **2021–22** | $25\text{--}29$ | 1,721 | 6.8% | 1,236.4 | 27.13 | 18.72 | 13.23% | 12.17% | 3.85% | 3.71% | 16.51% | 14.94% | 9.16% | 8.47% | 30.58% | 29.97% | 32.20% |
| **2021–22** | $30+$ | 887 | 3.5% | 1,184.0 | 38.19 | 19.33 | 14.15% | 12.55% | 4.31% | 3.79% | 17.67% | 15.44% | 8.35% | 6.95% | 30.46% | 28.52% | 32.51% |
| **2023–24** | $<20$ | 18,750 | 74.9% | 533.4 | 14.79 | 13.04 | 18.07% | 14.27% | 5.20% | 5.67% | 23.28% | 19.93% | 7.08% | 8.96% | — | — | — |
| **2023–24** | $20\text{--}24$ | 3,905 | 15.6% | 1,081.0 | 22.24 | 16.38 | 13.31% | 12.53% | 4.82% | 5.48% | 18.13% | 18.01% | 9.30% | 9.56% | — | — | — |
| **2023–24** | $25\text{--}29$ | 1,578 | 6.3% | 1,194.4 | 27.08 | 18.30 | 13.33% | 12.24% | 4.39% | 4.72% | 17.72% | 16.96% | 9.85% | 9.78% | — | — | — |
| **2023–24** | $30+$ | 773 | 3.1% | 1,251.6 | 37.85 | 19.01 | 13.68% | 12.60% | 4.23% | 4.62% | 17.92% | 17.22% | 9.09% | 7.80% | — | — | — |

---

### Table B4: Kansas City Metropolitan Area vs. National Benchmark (Harmonized Weighting & Certified PTR)

| Wave | Population | Schools ($N$) | Mean School Enr | Student-Wt Class Size | Campus PTR (Certified) | School % IDEA | Pooled % IDEA | School % 504 | Pooled % 504 | School % IDEA/504 | Pooled % IDEA/504 | School % EL | Pooled % EL | EDFacts 10% Median |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2013–14** | National | 27,983 | 691.1 | 22.40 | 15.36 | 14.82% | 11.60% | 2.15% | 2.24% | 17.00% | 13.79% | 5.24% | 5.64% | — |
| **2013–14** | KC Metro | 146 | 805.2 | 22.51 | 14.51 | 13.56% | 9.27% | 1.71% | 2.05% | 15.31% | 11.21% | 4.70% | 4.71% | — |
| **2015–16** | National | 23,939 | 682.6 | 22.23 | 14.85 | 16.00% | 11.98% | 2.73% | 2.78% | 18.70% | 14.69% | 5.11% | 5.59% | — |
| **2015–16** | KC Metro | 114 | 864.4 | 23.03 | 14.03 | 13.41% | 9.84% | 2.19% | 2.40% | 15.57% | 12.20% | 4.82% | 5.16% | — |
| **2017–18** | National | 24,326 | 679.3 | 21.17 | 14.59 | 15.75% | 12.47% | 3.23% | 3.41% | 18.99% | 15.88% | 5.52% | 6.23% | 19.10% |
| **2017–18** | KC Metro | 115 | 866.9 | 21.02 | 14.25 | 13.04% | 9.90% | 3.31% | 3.62% | 16.35% | 13.52% | 5.34% | 6.11% | 16.35% |
| **2020–21** | National | 24,684 | 687.1 | 19.90 | 14.38 | 16.73% | 13.12% | 4.15% | 4.39% | 20.91% | 17.35% | 6.27% | 7.04% | 21.96% |
| **2020–21** | KC Metro | 117 | 872.3 | 17.79 | 14.34 | 17.21% | 10.94% | 3.53% | 4.22% | 20.74% | 15.16% | 5.61% | 5.79% | 63.98% |
| **2021–22** | National | 25,147 | 683.8 | 20.08 | 14.30 | 17.09% | 13.24% | 5.41% | 4.68% | 19.83% | 16.64% | 8.75% | 7.68% | 32.29% |
| **2021–22** | KC Metro | 122 | 841.2 | 19.06 | **13.76** | 16.69% | 11.57% | 4.44% | 4.58% | 17.28% | 15.62% | 7.73% | 6.09% | 27.45% |
| **2023–24** | National | 25,026 | 685.0 | 19.72 | 14.10 | 16.89% | 13.55% | 5.06% | 5.45% | 21.95% | 19.00% | 7.66% | 9.11% | — |
| **2023–24** | KC Metro | 121 | 866.0 | 20.63 | 13.82 | 14.97% | 10.97% | 4.29% | 5.38% | 19.26% | 16.35% | 6.18% | 6.26% | — |

---

## 4. Visual Evidence & Trajectories

### Figure B01: Longitudinal Context Dimensions (2013–14 to 2023–24)
![Figure B01](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/figures/fig_b01_longitudinal_context_dimensions.png)

*Figure B01 highlights:*
- **Panel (a):** Secondary class size eased by 12% over the full decade (22.40 $\to$ 19.72) and stabilized post-2020 at ~19.7–20.1 students, alongside campus PTR (15.36 $\to$ 14.10).
- **Panel (b):** Individualized disability accommodations expanded dramatically: Section 504-only prevalence more than doubled (2.24% $\to$ 5.45% pooled), while combined IDEA/504 reached 19.00% of all enrolled secondary students.
- **Panel (c):** Language diversity increased steadily (+61.5% in pooled EL share, from 5.64% to 9.11%).
- **Panel (d):** Chronic absenteeism clearly separates the incompatible federal definitions: Regime 1 (CRDC 15+ days) and Regime 2 (EDFacts $\ge 10\%$ days), displaying the dramatic post-2016 surge from 19.10% to 32.29% median absent.

### Figure B02: Class Size Bins vs. Context (2021–22)
![Figure B02](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/figures/fig_b02_class_size_bins_vs_context.png)

### Figure B03: Chronic Absenteeism Distribution Shift (EDFacts Consistent Definition)
![Figure B03](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/artifacts/figures/fig_b03_chronic_absenteeism_distribution_shift.png)

*Figure B03 highlights:*
- Demonstrates the rightward distribution shift under the consistent EDFacts definition.
- Pre-COVID (2017–18) clean median was 17.85%; post-COVID (2021–22) clean median reached 30.08%.
- Schools with severe attendance disruption ($\ge 30\%$ chronically absent) jumped from **20.7% to 57.0%** (+36.3 percentage points).

---

## 5. Preregistration Hypotheses Evaluation

| Hypothesis | Original Prediction | Certified Empirical Verdict | Evidence & Rationale |
|:---|:---|:---|:---|
| **H5: Teacher Instructional Load Intensification** | Average class size may not have risen dramatically, but teacher instructional load increased due to greater student heterogeneity and legal obligations. | **SUPPORTED — SCHOOL-CONTEXT INTENSIFICATION; TEACHER-LEVEL LOAD NOT YET ESTABLISHED** | Confirmed at the school-context level: secondary class sizes eased by 12% and stabilized at ~20 students, while surrounding legal accommodation obligations reached 19.0% of students (+143% in 504), EL prevalence rose by +61%, and federal chronic absenteeism rose from 18.9% to 32.0% (+69%). Epistemic guardrail strictly maintained: confirmation of micro-level teacher rosters and section-level load is reserved for Phase 5 (NTPS). |

---

## 6. Verification and Readiness for Phase 5

The test suite in [`tests/test_school_context_panel.py`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-classroom-capacity/tests/test_school_context_panel.py) passes **31 out of 31 tests cleanly (100%)**, verifying:
1. Complete separation of CRDC 15+ days and EDFacts 10% regimes.
2. Flagging of denominator mobility discordance (`flag_absent_gt_enrollment`) and preservation of unclipped rates.
3. Outcome-specific balanced panels ($N = 11,286$ for accommodations; $N = 20,075$ for EDFacts absenteeism).
4. Strict weighting identities (school-weighted vs. pooled student-weighted).
5. Nonbinary reserve-code handling (`sum_enrollment_with_nonbinary`).
6. Canonical Kansas City PTR matching Phase 3 CCD metadata (resolving the 20.91 anomaly).

With Phase 4.1 fully calibrated, verified, and certified, Study B is frozen. The research program is now positioned for Phase 5 (National Teacher and Principal Survey microdata).
