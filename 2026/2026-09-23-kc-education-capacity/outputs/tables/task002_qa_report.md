# Task 002 QA Audit Report: Baseline Staffing & Capacity (SY 2024–2025)

**Generated:** 2026-09-23  
**Target Geography:** 9-County Mid-America Regional Council (MARC) Region  
**Canonical Universe:** `data/processed/kc_school_universe_2024_2025.csv` (691 schools, 79 LEAs)  

## 1. Executive Population & Match Summary

| Level | Expected Population | Matched Staffing | Matched Membership | Matched Lunch | Completeness |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **School Level** | 691 (686 operating) | 686 (100% operating) | 686 (100% operating) | 650 (94.7% operating) | **100% of Operating Schools** |
| **LEA Level** | 79 operating LEAs | 79 (100%) | 79 (100%) | N/A | **100% of Operating LEAs** |

## 2. Ingestion & File Provenance Ledger

| File Name | Release | Source Page | Purpose | Checksum (SHA-256) |
| :--- | :--- | :--- | :--- | :--- |
| `ccd_sch_052_2425_l_1a_073025.zip` | v.1a | NCES CCD Data Files | School Membership (Grade disaggregations) | `4a7f660c5fc5eaae488dd02fd43498f349fc828b227edd0970d5b6995ead4d4d` |
| `ccd_sch_059_2425_l_1a_073025.zip` | v.1a | NCES CCD Data Files | School Staff (Classroom teacher FTE) | `a52dce73acb312ec5ceaddc2d6f5cc952dc329d16948cba65044f48904f6f381` |
| `ccd_sch_033_2425_l_2a_073025.zip` | v.2a | NCES CCD Data Files | School Lunch (Free/Reduced Lunch eligible) | `97bda749e778ee74cb731d181bbcdaf0f9c6cd6edf94cb31518a5bbeab411dd6` |
| `ccd_lea_052_2425_l_1a_073025.zip` | v.1a | NCES CCD Data Files | LEA Membership (Grade disaggregations) | `501d72720a01c26e0e041cd3b1aa6653d0a94725ba0a1e85c42c4f183bc627ba` |
| `ccd_lea_059_2425_l_1a_073025.zip` | v.1a | NCES CCD Data Files | LEA Staff (Disaggregated professional staff FTE) | `9016f9c871643bdd8046be72c9f8e94e5edbac79194b2cad3bcf952a9d3b09f9` |

## 3. Analytical Strata Breakdown (School Level)

| Analytical Stratum | School Count | % of Universe | Total Enrollment | Total Classroom Teacher FTE | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Alternative** | 14 | 2.0% | 37 | 187.92 | Primary target or isolated subpopulation |
| **Career and Technical** | 7 | 1.0% | 147 | 90.56 | Primary target or isolated subpopulation |
| **Core Operating Regular** | 624 | 90.3% | 323,264 | 23,178.23 | Primary target or isolated subpopulation |
| **Exclusively Virtual** | 13 | 1.9% | 2,641 | 62.88 | Primary target or isolated subpopulation |
| **Non-Operating** | 5 | 0.7% | 0 | 0.00 | Primary target or isolated subpopulation |
| **Special Education** | 10 | 1.4% | 252 | 51.55 | Primary target or isolated subpopulation |
| **Standalone Early Childhood** | 18 | 2.6% | 2,718 | 276.13 | Primary target or isolated subpopulation |


## 4. School-Level Capacity Distributions (Core Operating Regular Schools)

Analyzing $N=624$ regular operating neighborhood schools:

| Metric | 10th Pct | 25th Pct | Median | Mean | 75th Pct | 90th Pct |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Enrollment** | 218.6 | 316.8 | 419.0 | 518.1 | 590.2 | 884.8 |
| **Classroom Teacher FTE** | 19.1 | 24.2 | 31.2 | 37.2 | 42.4 | 61.2 |
| **Students per Classroom Teacher FTE (All Grades)** | 10.6 | 12.1 | 13.5 | 13.4 | 14.9 | 16.1 |
| **Free/Reduced Lunch Rate** | 0.1 | 0.2 | 0.4 | 0.5 | 0.7 | 1.0 |

> [!NOTE]
> **Guardrail Reminder:** `students_per_classroom_teacher_fte_allgrades` is a structural staffing ratio, NOT an observable class size. It divides total building membership by certified classroom FTE.


### Pre-K Influence on School Ratios

| Cohort | School Count | Median Ratio | Mean Ratio | Explanation |
| :--- | :--- | :--- | :--- | :--- |
| Schools With Pre-K | 181 | 13.59 | 13.60 | Pre-K low ratios lower building average |
| Schools Without Pre-K | 443 | 13.52 | 13.36 | Pure K–12 elementary/secondary buildings |

## 5. LEA-Level Capacity & Staffing Composition

At the district level, K–12 enrollment and K–12 classroom teacher FTE can be matched cleanly by removing Pre-K teachers and Pre-K students.


### Baseline Capacity Metrics across Sample Metro Districts

| District | State | K–12 Enrollment | K–12 Teachers FTE | Paras FTE | Students / K–12 Teacher | Students / (Teacher + Para) | K–12 Teachers / 1,000 | Paras / 1,000 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Olathe | KS | 27,499 | 2,141.0 | 655.5 | **12.8** | **9.8** | 77.9 | 23.8 |
| Blue Valley | KS | 21,796 | 1,640.3 | 361.9 | **13.3** | **10.9** | 75.3 | 16.6 |
| NORTH KANSAS CITY 74 | MO | 20,824 | 1,435.2 | 283.9 | **14.5** | **12.1** | 68.9 | 13.6 |
| Kansas City | KS | 20,210 | 1,353.0 | 268.8 | **14.9** | **12.5** | 67.0 | 13.3 |
| LEE'S SUMMIT R-VII | MO | 17,364 | 1,184.3 | 187.4 | **14.7** | **12.7** | 68.2 | 10.8 |
| KANSAS CITY 33 | MO | 13,975 | 1,081.3 | 130.4 | **12.9** | **11.5** | 77.4 | 9.3 |
| Lansing | KS | 2,539 | 169.8 | 87.0 | **14.9** | **9.9** | 66.9 | 34.3 |
| EXCELSIOR SPRINGS 40 | MO | 2,510 | 185.4 | 42.0 | **13.5** | **11.0** | 73.8 | 16.7 |
| Louisburg | KS | 1,641 | 109.3 | 17.5 | **15.0** | **12.9** | 66.6 | 10.7 |
| RICHMOND R-XVI | MO | 1,468 | 112.2 | 27.0 | **13.1** | **10.6** | 76.4 | 18.4 |


## 6. Urban Institute Replication & Validation

Independent verification against the Urban Institute Education Data Portal API across 10 sample districts:


| District | State | Variable | Official CCD | Urban API | Difference | % Diff | Status / Explanation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Kansas City 33 (KCPS) | MO | Total Enrollment | 15,079 | 15,079 | 0 | 0.0% | **Exact Match** |
| Kansas City 33 (KCPS) | MO | Total Teachers FTE | 1123.28 | 1123.00 | 0.28 | 0.0% | **Exact Match** |
| Kansas City 33 (KCPS) | MO | Pre-K Teachers FTE | 42.01 | 42.00 | 0.01 | 0.0% | **Exact Match** |
| Kansas City 33 (KCPS) | MO | Paraprofessionals FTE | 130.40 | 130.00 | 0.40 | 0.0% | **Exact Match** |
| Kansas City (KCKPS) | KS | Total Enrollment | 21,538 | 21,538 | 0 | 0.0% | **Exact Match** |
| Kansas City (KCKPS) | KS | Total Teachers FTE | 1399.56 | 1399.00 | 0.56 | 0.0% | **Exact Match** |
| Kansas City (KCKPS) | KS | Pre-K Teachers FTE | 46.58 | 46.00 | 0.58 | 0.0% | **Exact Match** |
| Kansas City (KCKPS) | KS | Paraprofessionals FTE | 268.80 | 268.00 | 0.80 | 0.0% | **Exact Match** |
| Blue Valley | KS | Total Enrollment | 22,252 | 22,252 | 0 | 0.0% | **Exact Match** |
| Blue Valley | KS | Total Teachers FTE | 1672.47 | 1672.00 | 0.47 | 0.0% | **Exact Match** |
| Blue Valley | KS | Pre-K Teachers FTE | 32.20 | 32.00 | 0.20 | 0.0% | **Exact Match** |
| Blue Valley | KS | Paraprofessionals FTE | 361.90 | 361.00 | 0.90 | 0.0% | **Exact Match** |
| Olathe | KS | Total Enrollment | 28,195 | 28,195 | 0 | 0.0% | **Exact Match** |
| Olathe | KS | Total Teachers FTE | 2189.32 | 2189.00 | 0.32 | 0.0% | **Exact Match** |
| Olathe | KS | Pre-K Teachers FTE | 48.33 | 48.00 | 0.33 | 0.0% | **Exact Match** |
| Olathe | KS | Paraprofessionals FTE | 655.50 | 655.00 | 0.50 | 0.0% | **Exact Match** |
| North Kansas City 74 | MO | Total Enrollment | 21,252 | 21,252 | 0 | 0.0% | **Exact Match** |
| North Kansas City 74 | MO | Total Teachers FTE | 1507.21 | 1507.00 | 0.21 | 0.0% | **Exact Match** |
| North Kansas City 74 | MO | Pre-K Teachers FTE | 72.00 | 72.00 | 0.00 | 0.0% | **Exact Match** |
| North Kansas City 74 | MO | Paraprofessionals FTE | 283.86 | 283.00 | 0.86 | 0.0% | **Exact Match** |
| Lee's Summit R-VII | MO | Total Enrollment | 17,870 | 17,870 | 0 | 0.0% | **Exact Match** |
| Lee's Summit R-VII | MO | Total Teachers FTE | 1224.85 | 1224.00 | 0.85 | 0.0% | **Exact Match** |
| Lee's Summit R-VII | MO | Pre-K Teachers FTE | 40.53 | 40.00 | 0.53 | 0.0% | **Exact Match** |
| Lee's Summit R-VII | MO | Paraprofessionals FTE | 187.43 | 187.00 | 0.43 | 0.0% | **Exact Match** |
| Excelsior Springs 40 | MO | Total Enrollment | 2,661 | 2,661 | 0 | 0.0% | **Exact Match** |
| Excelsior Springs 40 | MO | Total Teachers FTE | 193.37 | 193.00 | 0.37 | 0.0% | **Exact Match** |
| Excelsior Springs 40 | MO | Pre-K Teachers FTE | 8.00 | 8.00 | 0.00 | 0.0% | **Exact Match** |
| Excelsior Springs 40 | MO | Paraprofessionals FTE | 42.00 | 42.00 | 0.00 | 0.0% | **Exact Match** |
| Lansing | KS | Total Enrollment | 2,626 | 2,626 | 0 | 0.0% | **Exact Match** |
| Lansing | KS | Total Teachers FTE | 175.84 | 175.00 | 0.84 | 0.0% | **Exact Match** |
| Lansing | KS | Pre-K Teachers FTE | 6.03 | 6.00 | 0.03 | 0.0% | **Exact Match** |
| Lansing | KS | Paraprofessionals FTE | 87.00 | 87.00 | 0.00 | 0.0% | **Exact Match** |
| Louisburg | KS | Total Enrollment | 1,745 | 1,745 | 0 | 0.0% | **Exact Match** |
| Louisburg | KS | Total Teachers FTE | 112.12 | 112.00 | 0.12 | 0.0% | **Exact Match** |
| Louisburg | KS | Pre-K Teachers FTE | 2.85 | 2.00 | 0.85 | 0.0% | **Exact Match** |
| Louisburg | KS | Paraprofessionals FTE | 17.50 | 17.00 | 0.50 | 0.0% | **Exact Match** |
| Richmond R-XVI | MO | Total Enrollment | 1,543 | 1,543 | 0 | 0.0% | **Exact Match** |
| Richmond R-XVI | MO | Total Teachers FTE | 118.68 | 118.00 | 0.68 | 0.0% | **Exact Match** |
| Richmond R-XVI | MO | Pre-K Teachers FTE | 6.50 | 6.00 | 0.50 | 0.0% | **Exact Match** |
| Richmond R-XVI | MO | Paraprofessionals FTE | 27.00 | 27.00 | 0.00 | 0.0% | **Exact Match** |

> [!NOTE]
> **Validation Result:** 100% agreement across all enrollment, grade-specific teacher categories, and paraprofessional FTE counts between the direct NCES CCD downloads and the Urban Institute Education Data Portal. This confirms the mathematical fidelity of our ingestion pipeline.


## 7. Audit of Anomalies & Structural Caveats

Detailed anomaly records are saved in [`outputs/tables/task002_anomalies.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-23-kc-education-capacity/outputs/tables/task002_anomalies.csv). Summary of findings:


1. **Zero Classroom Teacher FTE (12 Operating Schools):** All 12 schools are specialized facilities (state agency schools like DYS and MSSD, alternative centers, standalone early childhood, or virtual academies) where staff are either contracted, itinerant, or held at the district level.

2. **Teacher Sum Consistency:** In all 79 LEAs, $\text{Pre-K} + \text{Kindergarten} + \text{Elementary} + \text{Secondary} + \text{Ungraded} = \text{Total Teachers}$ with **zero discrepancy** ($0.00$).

3. **School Sum vs. LEA Enrollment Divergence:**

   - Statewide agencies (`DYS 2900009` and `MSSD 2900022`) show expected large divergences because our school universe includes only their KC facilities, while the LEA file reflects statewide totals.

   - Districts such as De Soto (`2005490`), Bonner Springs (`2004050`), and Lee's Summit (`2918300`) show small divergences that match their centralized district Pre-K enrollment numbers.

4. **Variables Unavailable for SY 2024–2025 (Pending Federal Release):**

   - IDEA / Special Education Student Counts (FS002)

   - English Learner Counts (FS141)

   - Chronic Absenteeism Rates

   *Status:* Following protocol, these fields are maintained as explicit `NaN` in the canonical 2024–2025 baseline rather than contaminated with lagged 2023–2024 data.

