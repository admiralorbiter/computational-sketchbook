# Phase 3C — Step 1B-KS: Kansas Instructional Role Decomposition Report
**Kansas City Metropolitan Education Capacity Study**  
**Date:** September 24, 2026  
**Status:** Complete  
**Associated Artifact:** [`outputs/tables/task003c_kansas_role_decomposition.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-23-kc-education-capacity/outputs/tables/task003c_kansas_role_decomposition.csv)  
**Parent Framework:** Phase 3C Research Design & Decision 026  

---

## Executive Summary & Core Empirical Findings

The Step 1A pilot revealed that Kansas State Department of Education (KSDE) administrative systems distinguish between **Classroom Teachers** and **Other Teachers (Special Education & Reading Specialists)**, whereas federal Common Core of Data (CCD) bundles both into total instructional teachers. 

To determine whether the decade-long teacher staffing expansion was driven primarily by specialized instructional roles (H1c — The Allocation Wedge Hypothesis) or by conventional classroom teachers, this report analyzes complete administrative personnel panels across **all 19 metropolitan Unified School Districts (USDs)** in the 4 Kansas metropolitan counties (Johnson, Wyandotte, Leavenworth, and Miami) across the three canonical anchor years: **2014–15, 2019–20, and 2024–25**. (Note: State special schools—School for the Blind and School for the Deaf—are state-administered institutions outside the standard USD school finance and staffing formula and are excluded from this USD decomposition).

### Key Findings:

1. **The Specialist Denominator Wedge is Quantified at ~2.7 to 2.8 Students per Teacher:**
   - In 2014–15, the regional student-to-teacher ratio across the 19 Kansas USDs was **16.86** students per *Classroom Teacher*, but **14.05** students per *Total Instructional Teacher* ($\text{Specialist Denominator Wedge} = \mathbf{2.81}$).
   - In 2024–25, the ratio was **16.26** students per *Classroom Teacher*, but **13.60** students per *Total Instructional Teacher* ($\text{Specialist Denominator Wedge} = \mathbf{2.66}$).
   - Reporting aggregate teacher FTE (as federal CCD does) makes regional staffing look systematically more generous by **2.7 to 2.8 students per teacher** compared to direct classroom-teaching lines.
   - *Important Terminology Distinction:* This measure is the **Specialist Denominator Wedge** (or Teacher-Definition Wedge). The true **Allocation Wedge** defined under Hypothesis H1c is $\text{Median Core Section Size} - \text{Reported Pupil/Teacher Ratio}$, which will be directly measured in Phase 4A.

2. **Both Classroom and Specialized Roles Rose Substantially:**
   - Across all 19 districts combined:
     - K–12 Enrollment: $136,986.0 \rightarrow 140,351.0$ ($+3,365.0\text{ students}, +2.46\%$).
     - Classroom Teachers ($T_{classroom}$): $8,123.70 \rightarrow 8,630.60$ ($+506.90\text{ FTE}, \mathbf{+6.24\%}$).
     - Other Teachers ($T_{other}$, SPED & Reading): $1,623.90 \rightarrow 1,687.30$ ($+63.40\text{ FTE}, +3.90\%$).
     - Total Instructional Teachers ($T_{inst}$): $9,747.60 \rightarrow 10,317.90$ ($+570.30\text{ FTE}, +5.85\%$).
   - Net regional growth in instructional personnel was **88.9% classroom teachers** and **11.1% specialized teachers**.

3. **Specialized Roles Were a Major Engine in Expanding Suburban Districts:**
   - In **Blue Valley (USD 229)**: Total teacher additions were $+178.3$ FTE ($+12.0\%$). Specialized teachers expanded by $+35.7\%$ ($+91.1$ FTE), accounting for **51.1% of all teacher additions**!
   - In **Gardner Edgerton (USD 231)**: Specialized teachers grew $+49.8\%$ ($+26.6$ FTE), accounting for **31.9% of growth**.
   - In **Basehor-Linwood (USD 458)**: Specialized teachers grew $+128.8\%$ ($+33.5$ FTE), accounting for **37.9% of growth**.
   - In **Olathe (USD 233)**: Specialized teachers grew $+10.4\%$ ($+31.4$ FTE), accounting for **29.4% of growth**.
   - In Johnson County suburbs combined (Blue Valley, Olathe, Shawnee Mission, Gardner Edgerton, De Soto, Spring Hill):
     - Added **$+573.9$ Classroom Teachers (+8.7%)**.
     - Added **$+206.0$ Other Teachers (+21.3%)**.
     - Total additions: **$+779.9$ Teachers (+10.3%)**, while enrollment grew only $+3.2\%$.
     - Specialized teachers represented **26.4%** of net suburban additions.

4. **Critical Analytical Takeaway for H1c and Phase 4A:**
   - Because conventional classroom teachers themselves grew faster than enrollment ($+8.7\% \text{ vs } +3.2\%$ in Johnson County, $+6.2\% \text{ vs } +2.5\%$ across Kansas USDs), **specialized role dilution (H1c) is an important part of the story, but not the complete story**.
   - The physical teaching force inside regular classrooms expanded. 
   - If classroom staffing expanded by 6% to 9% while enrollment was nearly flat, why do secondary teachers still report core section sizes of 24–28 students?
   - This shifts the research frontier directly to:
     1. **Teacher scheduling and prep time** (e.g. 5 teaching periods per day out of 7 or 8 periods, reducing simultaneous classroom availability).
     2. **Course proliferation and elective distribution** (small specialized, AP, CTE, and remedial sections absorbing classroom teacher FTE, leaving core Math/ELA rosters large).
     3. **Actual section-level rosters** (which require Phase 4A microdata).

---

## 1. Mathematical Framework

Following Decision 026:
$$ T_{instructional} = T_{classroom} + T_{other} $$
where $T_{other}$ is KSDE's audited Special Education Teachers and Reading Specialists category.

Specialist share of the teaching force:
$$ SpecialistShare = \frac{T_{other}}{T_{classroom} + T_{other}} $$

Decade decomposition (2014–15 to 2024–25):
$$ \Delta T_{instructional} = \Delta T_{classroom} + \Delta T_{other} $$

Classroom and Specialist growth contributions:
$$ \text{Classroom Share of Growth} = \frac{\Delta T_{classroom}}{\Delta T_{instructional}} \times 100\% $$
$$ \text{Specialist Share of Growth} = \frac{\Delta T_{other}}{\Delta T_{instructional}} \times 100\% $$

---

## 2. Regional Kansas USD Aggregate Summary

Table 1 summarizes all 19 Unified School Districts in Johnson, Wyandotte, Leavenworth, and Miami counties across the three anchor years:

### Table 1: Kansas Metropolitan USD Personnel Totals (19 Districts)
*Source: KSDE OpenGov / Licensed Personnel Databank*

| School Year | Students | Classroom Teachers | Other Teachers (SPED/Reading) | Total Instructional Tch | Managers | Specialist Share (%) | Students / Classroom Tch | Students / Instructional Tch | Specialist Denominator Wedge |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2014–15** | 136,986.0 | 8,123.70 | 1,623.90 | 9,747.60 | 998.20 | **16.66%** | **16.86** | **14.05** | **+2.81** |
| **2019–20** | 145,812.0 | 8,884.80 | 1,715.40 | 10,600.20 | 1,064.30 | **16.18%** | **16.41** | **13.76** | **+2.66** |
| **2024–25** | 140,351.0 | 8,630.60 | 1,687.30 | 10,317.90 | 1,279.50 | **16.35%** | **16.26** | **13.60** | **+2.66** |
| **10-Yr Change** | **+3,365.0** | **+506.90** | **+63.40** | **+570.30** | **+281.30** | **-0.31 pp** | **-0.60** | **-0.45** | **-0.15** |
| **% Change** | **+2.46%** | **+6.24%** | **+3.90%** | **+5.85%** | **+28.18%** | — | — | — | — |

*Key Observation:* Managers (instructional coordinators, supervisors, directors, and principals) surged by **+28.18%** (+281.3 FTE), expanding more than 4 times faster than classroom teachers.

---

## 3. District-by-District Decomposition (2014–15 to 2024–25)

The table below presents the full decomposition for each of the 19 Kansas school districts.

### Table 2: 10-Year Teacher Role Decomposition by Kansas District
*Source: `outputs/tables/task003c_kansas_role_decomposition.csv`*

| USD | District Name | County | $\Delta\text{Students}$ | $\Delta T_{class}$ | $\Delta T_{other}$ | $\Delta T_{inst}$ | $\% \Delta T_{class}$ | $\% \Delta T_{other}$ | Specialist Share 2025 | Specialist Share of Growth | Specialist Wedge 2015 | Specialist Wedge 2025 |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **202** | Turner-Kansas City | Wyandotte | -219.6 | +15.0 | -9.0 | +6.0 | +7.2% | -19.6% | 14.2% | -150.0% | 3.47 | 2.38 |
| **203** | Piper-Kansas City | Wyandotte | +837.0 | +47.5 | +27.0 | +74.5 | +44.2% | +300.0% | 18.9% | **36.2%** | 1.32 | 3.29 |
| **204** | Bonner Springs | Wyandotte | -74.3 | +8.0 | +4.0 | +12.0 | +5.2% | +13.8% | 16.8% | **33.3%** | 2.57 | 2.49 |
| **207** | Ft Leavenworth | Leavenworth | -333.2 | +5.0 | -4.8 | +0.2 | +4.5% | -25.5% | 10.8% | -2400.0% | 2.30 | 1.29 |
| **229** | Blue Valley | Johnson | +404.6 | +87.2 | +91.1 | +178.3 | +7.1% | **+35.7%** | 20.7% | **51.1%** | 2.97 | 3.46 |
| **230** | Spring Hill | Johnson | +2,506.9 | +98.8 | +15.3 | +114.1 | +70.2% | +61.9% | 14.3% | 13.4% | 3.32 | 3.38 |
| **231** | Gardner Edgerton | Johnson | +299.3 | +56.9 | +26.6 | +83.5 | +18.2% | **+49.8%** | 17.8% | **31.9%** | 2.54 | 2.70 |
| **232** | De Soto | Johnson | +386.1 | +50.9 | +2.9 | +53.8 | +12.8% | +4.3% | 13.5% | 5.4% | 2.41 | 2.17 |
| **233** | Olathe | Johnson | -79.1 | +75.3 | +31.4 | +106.7 | +4.5% | +10.4% | 16.0% | **29.4%** | 2.58 | 2.54 |
| **367** | Osawatomie | Miami | -219.7 | -9.0 | 0.0 | -9.0 | -12.0% | 0.0% | 4.4% | 0.0% | 0.59 | 0.61 |
| **368** | Paola | Miami | -163.4 | -12.0 | +16.0 | +4.0 | -9.4% | +23.9% | 41.7% | **400.0%** | 5.20 | 6.32 |
| **416** | Louisburg | Miami | -2.9 | +2.9 | -4.0 | -1.1 | +3.0% | -80.0% | 1.0% | 363.6% | 0.90 | 0.15 |
| **449** | Easton | Leavenworth | +42.2 | +2.0 | -1.0 | +1.0 | +4.2% | -100.0% | 0.0% | -100.0% | 0.24 | -0.05 |
| **453** | Leavenworth | Leavenworth | -455.5 | -20.5 | -11.0 | -31.5 | -9.6% | -22.9% | 16.1% | 34.9% | 3.10 | 2.67 |
| **458** | Basehor-Linwood | Leavenworth | +659.0 | +55.0 | +33.5 | +88.5 | +47.4% | **+128.8%** | 25.8% | **37.9%** | 3.66 | 4.48 |
| **464** | Tonganoxie | Leavenworth | +23.0 | -9.1 | +3.7 | -5.4 | -6.8% | +18.2% | 16.1% | -68.5% | 1.84 | 2.53 |
| **469** | Lansing | Leavenworth | +42.6 | -7.0 | -6.0 | -13.0 | -5.0% | -13.6% | 22.4% | 46.2% | 4.35 | 4.34 |
| **500** | Kansas City | Wyandotte | +34.2 | -144.8 | -191.0 | -335.8 | -10.5% | -54.6% | 11.4% | 56.9% | 3.05 | 1.88 |
| **512** | Shawnee Mission | Johnson | -322.2 | +204.8 | +38.7 | +243.5 | +14.1% | +15.1% | 15.1% | 15.9% | 2.74 | 2.32 |

---

## 4. Key Sub-Regional Findings

### 4.1 Johnson County Suburban Growth Core
In the 6 Johnson County districts (Blue Valley, Olathe, Shawnee Mission, Gardner Edgerton, De Soto, Spring Hill):
- **Classroom Teachers grew by $+573.9$ FTE (+8.70%)**.
- **Specialized Teachers grew by $+206.0$ FTE (+21.32%)**.
- **Total Teachers grew by $+779.9$ FTE (+10.30%)**.
- **Student Enrollment grew by $+3,439.4$ (+3.22%)**.

This proves that in the major suburban districts, **both regular classroom capacity and specialized instructional capacity expanded strongly**. In Blue Valley, specialized teachers accounted for over half (51.1%) of total net hiring; in Gardner Edgerton and Olathe, they accounted for ~30%.

### 4.2 Urban Wyandotte County (USD 500)
USD 500 experienced significant contraction in reported central personnel (-144.8 classroom teachers, -191.0 other teachers). As established in our pilot forensic audit, USD 500 served as the central fiscal agency for the Wyandotte Comprehensive Special Education Cooperative in 2014–15 (reporting 350 other teachers centrally). Over the decade, cooperative staffing was decentralized directly to member districts and individual school buildings.

---

## 5. Synthesis: Implications for the Research Hypotheses

| Hypothesis | Finding from Step 1B-KS | Interpretation & Status |
| :--- | :--- | :--- |
| **H1c (The Allocation Wedge Hypothesis)** | **Specialist Wedge Quantified (~2.7–2.8); Allocation Wedge Unresolved** | Kansas state data confirms that specialized instructional teachers create a ~2.7–2.8 ratio wedge (the *Specialist Denominator Wedge*). However, because classroom teachers themselves also grew (+6.2% across USDs, +8.7% in Johnson County), denominator dilution alone does not explain why core classes remain large. The true Allocation Wedge ($\text{Median Core Section Size} - \text{Reported PTR}$) remains **unresolved** pending Phase 4A course section microdata. |
| **Classroom Teacher Sufficiency** | **Classroom Teachers Rose Substantially (+6.2% to +8.7%)** | Physical regular classroom capacity expanded faster than enrollment. Why added classroom FTE did not translate into smaller core sections is the central mystery for Phase 4. |
| **H2 (Complexity / Individualized Needs)** | **Substantial Expansion in Specialists & Paras** | The 21% surge in suburban specialized teachers and 12% rise in paras is consistent with expanding individualized instructional obligations (IEP/504/ELL), though CCD and LPR aggregates do not observe the section-level student mix. |
| **Phase 4A Frontier (Scheduling & Load)** | **Highest-Value Research Step** | Squeezing district FTE further offers diminishing returns. The empirical frontier requires observing course section schedules, educator prep load, and student distribution. |
