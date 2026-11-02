# Artifact 01: Data Inventory and Panel Construction

## 1. Overview and Purpose

This artifact documents the comprehensive data universe assembled for the **Missouri Accountability Signal** sketchbook. The master analytical dataset combines statewide longitudinal records from the Missouri Department of Elementary and Secondary Education (DESE) Missouri Comprehensive Data System (MCDS) across the **MSIP 6** accountability era (**2022 through 2025**).

The resulting panel contains **8,705 building-year observations** spanning 93 harmonized attributes.

---

## 2. Source Registry Summary

A total of **19 raw data files** have been ingested, cryptographically verified via SHA-256 hashes, and cataloged in [`sources/source_registry.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-missouri-accountability-signal/sources/source_registry.csv).

| Source Family | Description | School Years | File Format | Level | Source ID |
|:---|:---|:---:|:---:|:---:|:---|
| **APR Summary** | Annual Performance Report Building Summary (Total Points, CI, Performance) | 2022, 2023, 2024, 2025 | XLSX | Building | `APR_SUMM_{YR}_BLD` |
| **APR Supporting** | MAP Status MPI, Growth Points %, Participant & Accountable Student Counts | 2022, 2023, 2024, 2025 | XLSX | Building | `APR_SUPP_{YR}_BLD` |
| **Socioeconomic (FRPL & CEP)** | Longitudinal Free/Reduced Lunch Headcount, Membership, and CEP Status | 2010–2026 | XLSX | Building | `SES_FRPL_LONGITUDINAL` |
| **Demographics & Subgroups** | Race/ethnicity percentages, IEP rate, LEP/ELL percentage, Title I status | 2006–2025 | XLSX | Building | `STUDENT_DEMOGRAPHICS_LONGITUDINAL` |
| **Enrollment** | Longitudinal Fall K-12 building headcounts by grade | 1991–2025 | XLSX | Building | `SCHOOL_ENROLLMENT_LONGITUDINAL` |
| **Attendance** | Proportional Attendance Rate (90/90 standard) and Chronic Absenteeism | 2018–2025 | XLSX | Building | `ATTENDANCE_PROPORTIONAL_BUILDING` |
| **Mobility** | Inbound, outbound, and total student mobility rates | 2018–2025 | XLSX | Building | `STUDENT_MOBILITY_BUILDING` |
| **Special Education Part B** | Special education assessment participation rates | 2023, 2024, 2025 | XLSX | Building | `SPED_PART_B_SCHOOL_{YR}` |
| **Growth Model Technical Docs** | Growth Model Procedures, Diagnostic Tables, and Technical Primer | 2024, 2025, Primer | PDF | Statewide Model | `GROWTH_MODEL_DOC_{YR}` |

---

## 3. Analytic Samples Definition

Per Research Design v0.1 Section 8, the study constructs three strictly defined nested analytic samples:

1. **Sample A — All Public Schools (Universe)**:
   - Includes every public school building record published by DESE in the Annual Performance Report files.
   - Used exclusively for gross descriptive counts, baseline auditing, and tracking statewide attrition.
   - Total records: **8,705 building-years** (2,128 in 2022; 2,295 in 2023; 2,143 in 2024; 2,139 in 2025).

2. **Sample B — Conventional Accountability Schools (Primary Analytic Universe)**:
   - The primary evaluative unit for all cross-sectional and regression analyses.
   - Applies clear, objective exclusion rules to omit specialized or non-comparable facilities:
     - Excludes specialized facilities, juvenile detention centers, residential treatment programs, and career/technical centers (`SPECIALIZED_FACILITY_OR_CTC`).
     - Excludes early-childhood and primary centers serving only grades PK through 2 (`NO_TESTED_GRADES_PK_2`), as these schools do not administer state MAP assessments.
     - Excludes buildings with zero valid points possible or wholly suppressed accountability scores (`NO_VALID_APR_OUTCOME`).
   - Sample B size: **2,039 schools in 2025** (8,246 total building-years across 2022–2025).

3. **Sample C — Stable Balanced Longitudinal Panel**:
   - The subset of Sample B schools that maintain uninterrupted presence across all four MSIP 6 accountability years (**2022, 2023, 2024, and 2025**).
   - Used for longitudinal stability, multi-year drift, and cohort-tracking analyses to ensure results are not confounded by school openings, closures, or boundary reconfigurations.
   - Sample C size: exactly **2,005 unique schools** followed across all 4 years (**8,020 building-years**).

---

## 4. Sample Attrition and Exclusion Audit

The following table provides the exact breakdown of school inclusion and exclusions by academic year:

| Metric / Category | 2022 | 2023 | 2024 | 2025 | Total Panel |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Sample A (Total Ingested APR Universe)** | **2,128** | **2,295** | **2,143** | **2,139** | **8,705** |
| *Exclusions:* | | | | | |
| — Early Childhood / Non-Tested Grades (PK–2) | 93 | 94 | 92 | 88 | 367 |
| — Specialized Facilities / Juvenile / Tech Centers | 0 | 39 | 1 | 1 | 41 |
| — Missing / Zero Points Possible APR Outcome | 0 | 34 | 6 | 11 | 51 |
| **Sample B (Conventional Accountability Schools)** | **2,035** | **2,128** | **2,044** | **2,039** | **8,246** |
| *Longitudinal Continuity Filter:* | | | | | |
| — Schools Missing in One or More MSIP 6 Years | 30 | 123 | 39 | 34 | 226 |
| **Sample C (Balanced 4-Year Stable Panel)** | **2,005** | **2,005** | **2,005** | **2,005** | **8,020** |

---

## 5. Sample B Composition by School Level

School levels are categorized using an automated grade-span parser based on official beginning and ending grade configurations (`BEG_GRADE` and `END_GRADE`):
- **Elementary**: Ending grade $\le 6$ and beginning grade $\le 5$ (e.g., K–5, PK–6, K–4).
- **Middle**: Ending grade in $\{7, 8, 9\}$ and beginning grade $\ge 5$ (e.g., 6–8, 7–8, 5–8).
- **High**: Ending grade 12 and beginning grade $\ge 7$ (e.g., 9–12, 7–12).
- **Mixed**: Broad spans crossing standard bands (e.g., K–8, PK–12).

| School Level | 2022 | 2023 | 2024 | 2025 | Share in 2025 |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Elementary Schools** | 1,043 | 1,047 | 1,043 | 1,043 | 51.15% |
| **Middle Schools** | 350 | 349 | 350 | 350 | 17.17% |
| **High Schools** | 473 | 473 | 459 | 453 | 22.22% |
| **Mixed / Broad Span** | 169 | 259 | 192 | 193 | 9.47% |
| **Total Sample B** | **2,035** | **2,128** | **2,044** | **2,039** | **100.00%** |

---

## 6. Data Completeness and Join Match Rates

All auxiliary contextual files were matched to the APR universe using the standardized compound primary key `(school_year, district_code, building_code)`. Join match rates for Sample B schools exceed 99.5%, far surpassing the required 98% threshold:

| Ingested Dataset | Join Match Rate | Missing Count (2025) | Missing Pct (2025) | Notes |
|:---|:---:|:---:|:---:|:---|
| **Student Demographics & Race** | 100.00% | 0 | 0.00% | Full statewide building coverage |
| **Enrollment Headcount** | 99.85% | 3 | 0.15% | 3 tiny specialized LEA buildings |
| **Free & Reduced-Price Lunch (FRPL)** | 100.00% | 0 | 0.00% | Reconciled longitudinal file + demographics |
| **Community Eligibility Provision (CEP)** | 100.00% | 0 | 0.00% | Binary participation flag |
| **Proportional Attendance (90/90)** | 99.56% | 9 | 0.44% | Minor suppression in very small schools |
| **Student Mobility Rates** | 99.95% | 1 | 0.05% | Near-perfect coverage |
| **Academic Achievement (Status MPI)** | 99.90% | 2 | 0.10% | 2 schools with suppressed test pools (< 10) |
| **Value-Added Growth Points %** | 97.84% | 44 | 2.16% | 44 high schools taking only EOCs without growth |
| **Total APR Percentage Earned** | 100.00% | 0 | 0.00% | Complete outcome reporting |

---

## 7. Variable Crosswalk and Harmonization Summary

The complete variable crosswalk is maintained in [`docs/variable_crosswalk.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-missouri-accountability-signal/docs/variable_crosswalk.csv). Key harmonization decisions include:

1. **APR Percentage Scaling**:
   - In 2022, DESE reported `PERCENT_POINTS_EARNED` as a decimal proportion ($0.0 \le p \le 1.0$; mean 0.672).
   - In 2023–2025, DESE reported `TOTAL_POINTS_EARNED_PCT` on a 0–100 percentage scale (mean ~68.8).
   - The 2022 metric is rescaled by multiplying by 100 to establish a uniform percentage scale across all panel years (`DIRECTLY_COMPARABLE`).

2. **Socioeconomic Status (FRPL & CEP)**:
   - Longitudinal FRPL percentage in `mo_frpl_building_2009_2026.xlsx` is provided on a decimal scale ($0.0 \le p \le 1.0$), scaled to 0–100%.
   - In Community Eligibility Provision (CEP) schools, individual lunch applications are waived and schools claim up to 100% reimbursement. Consequently, FRPL exhibits an artificial ceiling in CEP buildings. Both continuous FRPL and binary `cep_flag` are recorded to enable separate subgroup modeling (`COMPARABLE_WITH_CAVEAT`).

3. **Status MPI vs. Growth Points**:
   - Academic Status MPI is measured continuously on DESE's 100.0 to 500.0 scale across all four years (`DIRECTLY_COMPARABLE`).
   - Growth is reported as standardized z-scores in 2022 (`ALL_ELA_CURR_GROWTH_ZSCORE`), but as percentage of points earned across five tiers (0%, 25%, 50%, 75%, 100%) in 2023–2025 (`COMPARABLE_WITH_CAVEAT`).
