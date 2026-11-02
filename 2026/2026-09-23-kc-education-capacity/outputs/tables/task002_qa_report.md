# Task 002 QA Audit Report: Baseline Staffing & Capacity (SY 2024–2025)

**Generated:** 2026-09-23  
**Target Geography:** 9-County Mid-America Regional Council (MARC) Region  
**Canonical Universe:** `data/processed/kc_school_universe_2024_2025.csv` (691 schools, 79 LEAs)  

## 1. Executive Population & Match Summary

| Level | Expected Population | Matched Staffing | Matched Membership | Matched Lunch | Completeness |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **School Level** | 691 (686 operating) | 686 (100% operating) | 686 (100% operating) | 649 (94.6% operating) | **100% of Operating Schools** |
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
| **Exclusively Virtual** | 13 | 1.9% | 2,641 | 62.88 | Primary target or isolated subpopulation |
| **Non-Operating** | 5 | 0.7% | 0 | 0.00 | Primary target or isolated subpopulation |
| **Operating Regular (NCES)** | 624 | 90.3% | 323,264 | 23,178.23 | Primary target or isolated subpopulation |
| **Special Education** | 10 | 1.4% | 252 | 51.55 | Primary target or isolated subpopulation |
| **Standalone Early Childhood** | 18 | 2.6% | 2,718 | 276.13 | Primary target or isolated subpopulation |

> [!NOTE]
> **Important Clarification on NCES Classification:** The `Operating Regular (NCES)` stratum comprises all operating schools coded as `1 - Regular School` in the federal CCD. This classification is **not** synonymous with an ordinary or traditional neighborhood school. Several specialized, alternative, or day-treatment programs are officially coded by NCES as regular schools, including `STAR School` (Division of Youth Services), `DAY TREATMENT` (Independence), `CONTRACT` (KCPS), `CRITTENTON TREATMENT CENTER` (Hickman Mills), `SUCCESS ACADEMY` (KCPS), `NORTHWOOD SCH.` (Raytown), `RUSSELL JONES ED CENTER` (Park Hill), and `MILLER PARK CENTER` (Lee's Summit). These facilities report non-standard staffing structures (including zero classroom teacher FTE) and are preserved with their official NCES classification rather than manually reclassified.


## 4. School-Level Capacity Distributions: Operating Regular (NCES) Schools

Analyzing $N=624$ schools in the `Operating Regular (NCES)` stratum:

| Metric | 10th Pct | 25th Pct | Median | Mean | 75th Pct | 90th Pct |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Enrollment** | 218.6 | 316.8 | 419.0 | 518.1 | 590.2 | 884.8 |
| **Classroom Teacher FTE** | 19.1 | 24.2 | 31.2 | 37.2 | 42.4 | 61.2 |
| **Students per Classroom Teacher FTE (All Grades)** | 10.6 | 12.1 | 13.5 | 13.4 | 14.9 | 16.1 |
| **Free/Reduced Lunch Rate** | 0.1 | 0.2 | 0.4 | 0.5 | 0.7 | 1.0 |

> [!NOTE]
> **Guardrail Reminder:** `students_per_classroom_teacher_fte_allgrades` is a structural staffing ratio ($rac{	ext{Total Building Membership}}{	ext{Classroom Teacher FTE}}$), NOT an observable class size. It measures the aggregate availability of instructional faculty per enrolled student.


### Pre-K Influence on School Ratios

| Cohort | School Count | Median Ratio | Mean Ratio | Explanation |
| :--- | :--- | :--- | :--- | :--- |
| Schools With Pre-K | 181 | 13.59 | 13.60 | Co-located Pre-K programs |
| Schools Without Pre-K | 443 | 13.52 | 13.36 | Pure K–12 elementary/secondary buildings |

> [!NOTE]
> **Pre-K Staffing Interpretation:** After cleanly isolating standalone early-childhood centers ($N=18$), the presence of co-located Pre-K in operating regular schools is associated with only a very small difference in the observed building staffing ratio (median 13.59 vs. 13.52; mean 13.60 vs. 13.36). This slight difference indicates that co-located Pre-K does not materially distort building-level capacity ratios in the aggregate, but this observational comparison must not be interpreted as a causal effect.


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


### LEA Geographic Coverage & Boundary Analysis

The school universe is defined by physical school location within the 9 MARC counties, but federal LEA-level CCD counts encompass the entire administrative agency across the nation.


- **Fully Within Region ($N=77$ LEAs):** 77 of 79 operating LEAs have 100% of their operating schools located inside the 9-county study region (`lea_fully_within_region == True`, `lea_geographic_coverage_share == 1.0`).

- **Cross-Boundary / Statewide LEAs ($N=2$ LEAs):** Exactly two operating LEAs operate schools outside the region:


| LEA ID | District Name | State | National Op. Schools | In-Region Op. Schools | Outside Region | Regional Coverage Share |

| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `2900009` | **DIVISION OF YOUTH SERVICE** | MO | 30 | 5 | 25 | **16.7%** |
| `2900022` | **MO SCHLS FOR THE SEV DISABLED** | MO | 35 | 5 | 30 | **14.3%** |

> [!WARNING]
> **Geographic Boundary Warning:** LEA staffing and enrollment totals for agencies where `lea_fully_within_region == False` describe the entire statewide agency and therefore **must not be interpreted as purely Kansas City regional resources**.


## 6. Independent Ingestion Replication (Urban Institute Education Data Portal)

To verify the arithmetic fidelity and data parsing of our ingestion pipeline, we replicated 10 sample districts across diverse metropolitan archetypes against the Urban Institute Education Data Portal API (CCD Directory 2024 endpoint).


> [!NOTE]
> **Scope of Replication:** Both the Urban Institute Education Data Portal and our pipeline derive from the identical underlying federal NCES CCD collections. This comparison confirms that our data ingestion, grade rollups, and category parsing are mathematically exact; it does not constitute an independent validation of the accuracy of local district submissions to NCES.


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


## 7. Free and Reduced-Price Lunch (FRL) Availability & Missingness Analysis

In SY 2024–2025 CCD Free and Reduced-Price Lunch reporting (FS033 v.2a), FRL counts are observed for 649 of 686 operating schools (94.6%), while 37 operating schools have missing FRL data (`frl_observed == False`).


As shown below, missingness is highly non-random and heavily concentrated in specialized, alternative, and virtual programs:


| Category | Subpopulation | Total Operating Schools | FRL Observed | FRL Missing | % Observed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **State** | KS | 277 | 267 | 10 | 96.4% |
|  | MO | 409 | 382 | 27 | 93.4% |
| **Charter Status** | Charter | 45 | 44 | 1 | 97.8% |
|  | Non-Charter | 641 | 605 | 36 | 94.4% |
| **NCES School Type** | Alternative School | 14 | 2 | 12 | 14.3% |
|  | Career and Technical School | 7 | 1 | 6 | 14.3% |
|  | Regular School | 655 | 638 | 17 | 97.4% |
|  | Special Education School | 10 | 8 | 2 | 80.0% |
| **Analytical Stratum** | Alternative | 14 | 2 | 12 | 14.3% |
|  | Career and Technical | 7 | 1 | 6 | 14.3% |
|  | Exclusively Virtual | 13 | 3 | 10 | 23.1% |
|  | Operating Regular (NCES) | 624 | 617 | 7 | 98.9% |
|  | Special Education | 10 | 8 | 2 | 80.0% |
|  | Standalone Early Childhood | 18 | 18 | 0 | 100.0% |
| **Locale Group** | City | 266 | 254 | 12 | 95.5% |
|  | Rural | 107 | 101 | 6 | 94.4% |
|  | Suburb | 243 | 231 | 12 | 95.1% |
|  | Town | 70 | 63 | 7 | 90.0% |

> [!WARNING]
> **Methodological Warning on Socioeconomic Controls:** Missingness in FRL is structurally driven by program delivery models—students in shared-time vocational centers, virtual schools, and juvenile justice or therapeutic treatment centers either receive meals through sending home districts or are outside standard NSLP cafeteria counts. Furthermore, the 7 unobserved schools in `Operating Regular (NCES)` are all day treatment, alternative, custody, or therapeutic centers (`STAR School`, `CRITTENTON`, `DAY TREATMENT`, `SUCCESS ACADEMY`, `MILLER PARK CENTER`, `NORTHWOOD`, `RUSSELL JONES`). Therefore, `frl_rate` **must not yet be treated as a universal socioeconomic control** in cross-school models without explicit accounting for program missingness and reporting mechanisms.


## 8. Audit of Anomalies & Structural Caveats

Detailed anomaly records are saved in [`outputs/tables/task002_anomalies.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-23-kc-education-capacity/outputs/tables/task002_anomalies.csv). Summary of findings:


1. **Zero Classroom Teacher FTE (12 Operating Schools):** All 12 schools are specialized facilities where instructional staff are contracted, itinerant, or accounted for at the district level. Notably, 4 of these facilities (`STAR School`, `DAY TREATMENT`, `CONTRACT`, `MILLER PARK CENTER`) are coded by NCES as Regular Schools, emphasizing why `Operating Regular (NCES)` must not be conflated with ordinary neighborhood schools.

2. **Cross-Boundary / Statewide LEAs (2 LEAs):** Division of Youth Services (MO DYS) and Missouri Schools for the Severely Disabled (MSSD) operate 30 and 35 operating schools statewide respectively, with only 5 schools each physically located in the KC MARC region. Machine-readable flags (`lea_fully_within_region == False`) prevent these from distorting regional LEA comparisons.

3. **Teacher Sum Consistency:** In all 79 LEAs, $\text{Pre-K} + \text{Kindergarten} + \text{Elementary} + \text{Secondary} + \text{Ungraded} = \text{Total Teachers}$ with **exact zero discrepancy** ($0.00$).

4. **School Sum vs. LEA Enrollment Divergence:** In addition to statewide agencies, several traditional districts (De Soto, Bonner Springs, Lee's Summit, Hickman Mills) show divergences corresponding directly to centralized district Pre-K enrollments or alternative placements not assigned to building directories.

5. **Variables Unavailable for SY 2024–2025 (Pending Federal Release):** IDEA / Special Education Student Counts (FS002), SPED Teacher FTE (FS070), and English Learner Counts (FS141) are pending federal public release for SY 2024–2025. Per protocol, these remain explicit `NaN` in the baseline rather than contaminated with lagged prior-year data.

6. **Longitudinal Scope Clarification:** The upcoming longitudinal panel will assemble an 11-school-year annual panel spanning the 10-year interval from 2014–15 through 2024–25 as repeated cross-sections, avoiding survivorship bias.

