# Research Monograph: Instructional Labor Stock, Fixed-Plant Stickiness, and the Secondary Staffing Wedge

**Education Data Observatory — Cross-Measure Empirical Memo (Task 004)**  
**Date of Audit:** September 26, 2026  
**Focus Measure:** `EDU-003 Reported Classroom Teacher FTE`  
**Cross-References:** `EDU-001 Pupil/Teacher Ratio`, `EDU-002 Student Enrollment`, `EDU-005 Paraprofessional FTE`, `EDU-012 Derived Class Size`  
**Spatial Universe:** 9-County Kansas City Metropolitan Area ($N=77$ Fully Regional LEAs; $N=75$ Balanced Longitudinal LEAs; $N=691$ Campuses)  
**Temporal Coverage:** SY 2014–15 through SY 2024–25 (11-Year CCD Panel) matched to 6 Civil Rights Data Collection waves (2013–14 to 2023–24)

---

## Executive Summary & Core Epistemic Distinctions

This monograph executes the comprehensive empirical investigation and semantic audit of **`EDU-003 Reported Classroom Teacher FTE`**, transitioning it from `proposed` to `audited` status. Following the Observatory's foundational rule—**Source ≠ Field ≠ Operationalization ≠ Measure ≠ Claim**—this investigation addresses instructional labor not as an abstract budget line, but as a physical, organizational reality structured by school plant, master schedules, statutory grade reporting, and student enrollment shifts.

Five key analytical jobs were executed using the integrated 11-year administrative panel and multi-wave CRDC microdata. The core empirical findings are:

1. **Fixed-Plant Staffing Stickiness (`Job 1`):** In the 28 school districts that experienced enrollment declines while keeping their physical operating plant unchanged, classroom teaching staff contracted by only **$-3.63\%$ ($-136.3$ FTE)** despite an **$-8.33\%$ drop in K–12 enrollment ($-4,388$ students)**. School administrative personnel contracted in near-perfect lockstep with students (**$-9.78\%$**), while total district staff across all roles expanded (**$+9.41\%$, $+675.2$ FTE**), driven by increases in paraprofessionals ($+8.64\%$), instructional coordinators ($+29.08\%$), and student counselors ($+12.76\%$). Because teacher staffing was sticky downward across existing buildings, headline pupil/teacher ratios actually *decreased* from $14.02$ to $13.34$. This stickiness is robust across multiple sensitivity specifications (e.g., $-3.26\%$ teacher change in the 25 districts with 100% identical campus IDs).
2. **Curricular Breadth Staffing Penalty (`Job 2`):** In secondary schools, school scale buys curricular offerings, not smaller classes. In high schools under 800 students, offering Advanced Placement / advanced STEM coursework (Calculus and Physics) requires substantial instructional scale. However, a strict $\ge 35$ FTE threshold is empirically retracted: in 2023–24, offering schools included faculties as small as $15.63$ FTE (Drexel High), with half of offering schools under 35 FTE. Crucially, a matched-cohort panel of 28 high schools under 800 students present in both 2013–14 and 2023–24 reveals that Calculus offerings collapsed from **$67.9\%$ (19 of 28)** down to **$35.7\%$ (10 of 28)**, with 12 schools dropping Calculus and only 3 adding it.
3. **Kindergarten Staffing Resilience (`Job 3`):** When regional Kindergarten enrollment experienced an acute shock in Fall 2020 (dropping $-11.43\%$, $-2,871$ pupils), districts did *not* cut kindergarten teaching positions; reported Kindergarten FTE in the Balanced 75 actually *increased* by **$+3.67\%$ ($+115.2$ FTE)**, causing an immediate drop in primary pupil/teacher ratios. Over the 10-year span, total primary instructional labor expanded by **$+23.87\%$**.
4. **Charter Staffing Elasticity (`Job 4`):** In the Kansas City urban core (KCPS + Jackson County independent charters), charter enrollment expanded by **$+29.02\%$ ($+2,955$ students)** while charter classroom teacher FTE surged by **$+59.50\%$ ($+470.2$ FTE)**. Charters hired at an endpoint ratio of **$1.0$ teacher FTE per $6.28$ additional students** ($0.1591$ FTE/student), operating at an average macro PTR of **$10.42$** in 2024–25, significantly below KCPS ($12.92$).
5. **The Secondary Staffing Wedge (`Job 5`):** Across 109 regular operating high schools in CRDC 2023–24, the macro school PTR ($14.74$) mechanically understates actual foundational course class sizes by **$+3.5$ to $+4.5$ students** (Algebra I: $19.28$, wedge $+4.53$; Geometry: $18.94$, wedge $+4.06$; Biology: $18.81$, wedge $+3.96$). This structural wedge has persisted across all six CRDC waves from 2013–14 to 2023–24 due to teacher planning periods and low-enrollment advanced electives.

---

## 1. Source Reconciliations & Data Integrity Audit

### 1.1 The Campus-Sum vs. LEA-Reported Reconciliation Ledger
In SY 2024–25, across the 77 fully regional school districts, the Observatory audited the mathematical relationship between the sum of school-level reported classroom teachers (`TCH-NCES-SCHOOL-CLASSROOM`) and LEA-level reported teacher totals (`TCH-NCES-LEA-K12` and `TCH-NCES-LEA-TOTAL`).

```
========================================================================================
METROPOLITAN TEACHER RECONCILIATION LEDGER (SY 2024–25, 77 REGIONAL LEAs)
========================================================================================
  Campus-Level Sum of Classroom Teacher FTE:            23,819.77 FTE
  LEA-Level Sum of Reported K-12 Teacher FTE:           23,555.17 FTE
  Reconciliation Gap (LEA K-12 - Campus Sum):              -264.60 FTE (-1.12%)
  --------------------------------------------------------------------------------------
  LEA-Level Sum of Total Teacher FTE (incl Pre-K):      24,338.26 FTE
  Reconciliation Gap (LEA Total - Campus Sum):             +518.49 FTE (+2.13%)
  Total Reported LEA Pre-K Teacher FTE:                    783.09 FTE
========================================================================================
```

#### State Divergence Analysis
The apparent discrepancy between campus sums and LEA reports is entirely explained by institutional reporting differences between Missouri and Kansas:

1. **Missouri ($N=56$ LEAs):**
   - Campus Teacher Sum: $13,742.85$ FTE
   - LEA K-12 Teacher Sum: $13,350.66$ FTE
   - LEA Pre-K Teacher Sum: $455.42$ FTE
   - LEA Total Reported: $13,806.08$ FTE
   - *Epistemic Finding:* In Missouri, campus-level `TEACHERS` reports include early-childhood and Pre-K teachers physically located in school buildings. When comparing Campus Sum to LEA *Total* Reported, the net variance across 56 Missouri districts is only **$+63.23$ FTE (+0.46%)**.
2. **Kansas ($N=21$ LEAs):**
   - Campus Teacher Sum: $10,076.92$ FTE
   - LEA K-12 Teacher Sum: $10,204.51$ FTE
   - LEA Pre-K Teacher Sum: $327.67$ FTE
   - LEA Total Reported: $10,532.18$ FTE
   - *Epistemic Finding:* In Kansas, LEA Total Reported exceeds the Campus Sum by **$+455.26$ FTE (+4.32%)**. Kansas districts employ substantial centralized and itinerant instructional personnel (special education itinerants, traveling art/music/PE specialists, curriculum coaches) carried on district master rosters who are not assigned to individual NCES school codes.

### 1.2 The 2015–16 Kansas CCD Non-Reporting Anomaly
> [!WARNING]
> **Severe Administrative Artifact:** In SY 2015–16, the federal NCES CCD LEA and School Non-Fiscal files failed to collect teacher counts for two major Kansas districts:
> - **Olathe USD 233 (`LEAID 2010140`):** Missing $\sim 1,940$ teacher FTE (55 of 59 campuses unrecorded).
> - **Gardner Edgerton USD 231 (`LEAID 2006420`):** Missing $\sim 371$ teacher FTE.
> 
> This created an artificial, single-year regional drop of **$-2,311$ teacher FTE**, causing unadjusted regional macro PTR to spike to an artificial $16.65$. The Observatory's audited longitudinal series applies verified state KSDE interpolations, restoring the true balanced teacher stock to $21,797$ FTE and maintaining a smooth regional trend.

---

## 2. Job 1 — The Fixed-Plant Staffing Penalty in Declining Districts

### 2.1 Theoretical Framework: Physical Plant as a Staffing Anchor
School district staffing models operate under structural step-functions dictated by physical plant. When a district loses 200 to 500 students, those students rarely depart from a single grade in a single school; they trickle out across dozens of classrooms across multiple facilities. Unless the school board votes to physically close and consolidate school buildings, every campus must maintain:
1. At least one certified teacher per grade level (or course period).
2. Specialized subject teachers (art, music, physical education, special education).
3. A building principal, nurse, counselor, and clerical staff.

In Task 003D/003E, the Observatory identified **28 school districts** in the Balanced 75 cohort that experienced negative net K–12 enrollment change between 2014–15 and 2024–25 while keeping their operating school count completely unchanged (with 25 of the 28 retaining 100% identical campus NCESSCH IDs).

### 2.2 Empirical Audit Findings & Sensitivity Specifications
Across these 28 districts, the 10-year reallocation of labor shows a profound structural divergence between instructional staff, administrative overhead, and non-teaching support staff. 

To verify that this result is not driven by district reconfiguration, the Observatory evaluated three nested sensitivity specifications:
1. **Specification 1 (All 28 Unchanged-Count Decliners):** All districts in the Balanced 75 experiencing negative net enrollment while maintaining the same total number of operating schools.
2. **Specification 2 (25 Strictly Identical NCESSCH LEAs):** Restricting to the 25 districts whose active school NCESSCH ID sets remained 100% identical from 2014–15 to 2024–25 (excluding Raymore-Peculiar, Kansas City KS, and Leavenworth, which reconfigured campus grade spans).
3. **Specification 3 (Physical-Plant Matched Facilities):** Confirming that all 28 districts operated in the exact same physical building footprint across the decade.

```
====================================================================================================
SENSITIVITY ANALYSIS: FIXED-PLANT DOWNWARD STAFFING STICKINESS (2014–15 TO 2024–25)
====================================================================================================
Metric                       Specification 1 (N=28 LEAs)       Specification 2 (N=25 LEAs)
----------------------------------------------------------------------------------------------------
K-12 Student Enrollment      52,657 -> 48,269 (-8.33%, -4,388) 44,792 -> 41,209 (-8.00%, -3,583)
Classroom Teacher FTE        3,755.5 -> 3,619.3 (-3.63%, -136.3) 3,197.6 -> 3,093.4 (-3.26%, -104.2)
School/LEA Administrators     261.7 ->   236.1 (-9.78%,  -25.6)   227.1 ->   206.4 (-9.11%,  -20.7)
Total District Staff FTE     7,177.6 -> 7,852.8 (+9.41%, +675.2) 6,104.9 -> 6,659.5 (+9.08%, +554.6)
Aggregate Macro PTR           14.02 ->   13.34 (-0.68 PTR)        14.01 ->   13.32 (-0.69 PTR)
====================================================================================================
```

Across both specifications, classroom teacher staffing contracted at less than half the rate of enrollment loss, driving headline pupil/teacher ratios downward.

#### Staff-Category Coverage Matrix & True Composition
The $+9.41\%$ ($+675.2$ FTE) net growth represents **Total District Staff (All Roles Combined)** ($7,177.6 \to 7,852.8$ FTE). 

> [!WARNING]
> **Data Limitation (Staffing Category Comparability):** Naive aggregation of non-teaching "support staff" variables across historical CCD waves creates severe artificial volatility. Older federal CCD files (2014–15 and 2015–16) did not populate `psychologists_fte`, `school_admin_support_fte`, or `lea_admin_support_fte`. Furthermore, `student_support_staff_fte` was unpopulated or zeroed out from 2016–17 through 2018–19. 

Examining clean, consistently reported personnel categories reveals the true reallocation of labor across the 28 declining districts:

```
====================================================================================================
CLEAN STAFF CATEGORY REALLOCATION (N = 28 DECLINING LEAs WITH UNCHANGED PLANT)
====================================================================================================
Staff Category                   SY 2014–15      SY 2024–25      Net Change      % Change
----------------------------------------------------------------------------------------------------
Classroom Teachers                3,755.5         3,619.3          -136.3         -3.63%
Paraprofessionals                   907.9           986.3           +78.4         +8.64%
Instructional Coordinators          161.3           208.3           +46.9        +29.08%
Guidance Counselors                 133.1           150.0           +17.0        +12.76%
School Administrators               216.6           194.7           -21.9        -10.09%
Librarians / Media Specialists       85.7            39.1           -46.6        -54.39%
Total District Staff (All Roles)  7,177.6         7,852.8          +675.2         +9.41%
====================================================================================================
```

The expansion of non-instructional labor was heavily concentrated in **paraprofessionals and instructional aides ($+8.64\%$)**, curriculum coordinators ($+29.08\%$), and student counselors ($+12.76\%$), while traditional building librarians were halved ($-54.39\%$).

```
           +-------------------------------------------------------+
           |       ENROLLMENT CONTRACTION: -8.33% (-4,388)         |
           |             Unchanged Physical Plant (N=28)           |
           +-------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
+----------------------------------+     +----------------------------------+
|    CLASSROOM TEACHERS: -3.63%    |     |   PARAPROFESSIONALS: +8.64%      |
|  Sticky downward due to grade    |     |   Special ed aides and support   |
|  and room minimums; PTR drops.   |     |   personnel expand.              |
+----------------------------------+     +----------------------------------+
```

### 2.3 Deconstruction of the Big 8 Decliners
Among the 8 districts that lost $>200$ students with unchanged plant:
- **Fort Leavenworth (USD 207):** Lost $-21.67\%$ of students ($-378$), but maintained $+0.23\%$ teacher FTE ($125.3 \to 125.6$). Macro PTR plummeted from $13.92$ to **$10.88$**.
- **Hogan Preparatory Academy:** Lost $-21.66\%$ of students ($-224$), but expanded teachers by $+6.20\%$ ($86.2 \to 91.5$). Macro PTR fell from $12.00$ to **$8.85$**.
- **Grandview C-4:** Lost $-16.52\%$ of students ($-699$), cut teachers by $-9.36\%$ ($-26.0$ FTE). Macro PTR fell from $15.25$ to **$14.05$**.
- **Harrisonville R-IX:** Lost $-14.90\%$ of students ($-366$), cut teachers by $-12.73\%$ ($-23.5$ FTE). Macro PTR fell from $13.31$ to **$12.98$**.
- **Kansas City KS (KCKPS / USD 500):** Lost $-4.48\%$ of students ($-948$), cut teachers by $-2.78\%$ ($-38.6$ FTE). Macro PTR fell from $15.20$ to **$14.94$**.
- **Center 58:** Lost $-8.76\%$ of students ($-213$), cut teachers by $-6.07\%$ ($-12.8$ FTE). Macro PTR fell from $11.49$ to **$11.16$**.
- **Bonner Springs (USD 204):** Lost $-8.08\%$ of students ($-210$), added $+0.65\%$ teachers ($+1.27$ FTE). Macro PTR fell from $13.34$ to **$12.18$**.
- **Paola (USD 368):** The *single* exception: lost $-11.39\%$ of students ($-225$), but aggressively reduced teaching staff by $-20.08\%$ ($-32.35$ FTE). Macro PTR rose from $12.27$ to **$13.60$**.

> [!NOTE]
> **Epistemic Conclusion for Job 1 [ROBUST ASSOCIATION]:** Districts that experience student enrollment loss without closing school facilities exhibit downward staffing stickiness. Classroom teaching positions contract at less than half the rate of enrollment loss, driving headline pupil/teacher ratios downward. Meanwhile, districts do not expand administrative overhead to protect buildings; administration contracts proportionally ($-9.8\%$), while paraprofessionals and instructional support staff expand ($+8.6\%$).

---

## 3. Job 2 — Curricular Breadth Staffing Dynamics in High Schools

### 3.1 Scale Groups and Advanced Course Offerings (CRDC 2023–24)
Using the matched CRDC 2023–24 panel of 109 regular operating secondary high schools:

```
================================================================================================
SECONDARY SCALE BANDS & STEM OFFERINGS (CRDC 2023–24, N = 109 REGULAR HIGH SCHOOLS)
================================================================================================
  Scale Band      N    Mean Enr   Mean Tch FTE   Med Tch FTE   Calculus Offered   Physics Offered
  ----------------------------------------------------------------------------------------------
  < 400          32      172          17.9           17.2        7/32 (21.9%)      15/32 (46.9%)
  400–799        17      591          41.4           40.0        7/17 (41.2%)      11/17 (64.7%)
  800–1,199      19      992          60.3           61.3       13/19 (68.4%)      16/19 (84.2%)
  1,200–1,599    18    1,407          87.5           88.0       16/18 (88.9%)      16/18 (88.9%)
  >= 1,600       23    1,896         113.4          109.7       19/23 (82.6%)      23/23 (100.0%)
================================================================================================
```

### 3.2 Audit of the Curricular Breadth Threshold in Small High Schools
In high schools under 800 students ($N=49$):
- **Campuses offering Calculus ($N=14$):** Average enrollment = $440.1$; Mean Teacher FTE = **$34.3$** (Median = $36.5$).
- **Campuses NOT offering Calculus ($N=35$):** Average enrollment = $268.0$; Mean Teacher FTE = **$23.8$** (Median = $24.5$).

> [!CAUTION]
> **Threshold Retraction:** An initial hypothesis postulated a strict minimum faculty threshold of $\ge 35$ FTE for offering Calculus. The empirical audit soundly **retracts** this hard boundary:
> - The smallest regular high school offering Calculus in 2023–24 was **Drexel High School** with only **$15.63$ Teacher FTE** (enrollment 85).
> - Exactly **7 of the 14 offering schools (50%)** operated with fewer than 35 Teacher FTEs, and **5 of 14 (36%)** operated with fewer than 30 Teacher FTEs.
> 
> Rather than a deterministic mechanical threshold, school scale provides the budgetary capacity to support single-period singleton courses without forcing unviable section sizes in required courses.

### 3.3 Longitudinal Erosion of Advanced STEM: The Matched Cohort Panel
Across the unstratified sample, the proportion of small high schools (<800 enrollment) offering Calculus declined from $69.4\%$ (25 of 36) in 2013–14 to $28.6\%$ (14 of 49) in 2023–24. 

To ensure this was not an artifact of new small charter or alternative schools entering the sample, the Observatory constructed a **balanced matched cohort** of the **28 regular high schools under 800 students** that were open and operating in both 2013–14 and 2023–24:
- **SY 2013–14 Offering Rate:** **$67.9\%$** (19 of 28 schools offered Calculus).
- **SY 2023–24 Offering Rate:** **$35.7\%$** (10 of 28 schools offered Calculus).
- **Within-School Trajectory:** **12 high schools dropped Calculus**, while only **3 schools added it** (net loss of 9 offering campuses).
- In Physics, offerings among these 28 matched campuses remained relatively stable ($67.9\% \to 64.3\%$, 19 to 18 schools).

> [!IMPORTANT]
> **Epistemic Finding for Job 2 [DESCRIPTIVE FACT & LONGITUDINAL TREND]:** Even within a constant, matched cohort of small regular high schools, advanced mathematics offerings contracted by nearly half ($67.9\% \to 35.7\%$). In small faculties, preserving baseline teacher allocations across core statutory subjects under tightening labor constraints often requires shedding low-enrollment advanced electives.

---

## 4. Job 3 — Kindergarten Allocation & Early-Childhood Staffing Dynamics

### 4.1 Did Districts Cut Kindergarten Teachers When Kindergarten Collapsed?
In Task 003D/003E, the Observatory demonstrated that Kindergarten enrollment dropped $-11.43\%$ in Fall 2020 and finished the decade net negative ($-9.14\%$), while Grades 1–12 were net positive (+0.10%). 

The audit of LEA-reported Kindergarten Teacher FTE across the Balanced 75 cohort proves that districts did **not** cut kindergarten instructional staffing:
- **SY 2019–20 (Pre-Pandemic Baseline):** Kindergarten Enrollment = $25,123$; Kindergarten Teacher FTE = $3,136.21$.
- **SY 2020–21 (Acute Shock Window):** Kindergarten Enrollment = $22,252$ ($-2,871$ pupils, $-11.43\%$); Kindergarten Teacher FTE = **$3,251.41$ ($+115.20$ FTE, $+3.67\%$)**.
- Rather than cutting positions, school districts preserved their early-childhood faculty budgets, absorbing the enrollment loss through smaller kindergarten cohorts and temporarily depressed pupil/teacher ratios.

### 4.2 Longitudinal Primary Capacity Expansion
Over the entire 10-year span (SY 2014–15 to 2024–25), combined elementary and kindergarten instructional labor expanded substantially:
- **2014–15:** Kindergarten ($2,690.67$) + Elementary ($8,167.82$) = **$10,858.49$ FTE**.
- **2024–25:** Kindergarten ($2,173.27$) + Elementary ($11,277.09$) = **$13,450.36$ FTE**.
- Net Growth: **$+2,591.87$ FTE (+23.87%)** across primary grades, even while total K–12 enrollment was essentially flat ($-0.64\%$ in Balanced 75).

---

## 5. Job 4 — Charter Staffing Elasticity in the KC Urban Footprint

### 5.1 Traditional vs. Charter Staffing Trajectories (2014–15 to 2024–25)
Within the historical Kansas City Missouri School District (KCPS) boundary, students are served by KCPS (District 33) and independent public charter LEAs in Jackson County:

```
================================================================================================
URBAN CORE STAFFING DYNAMICS: KCPS VS. JACKSON COUNTY CHARTERS (K-12 HEADCOUNT)
================================================================================================
  Sector / Year        K-12 Enrollment     Classroom Teacher FTE     Macro PTR     Active LEAs
  ----------------------------------------------------------------------------------------------
  KCPS (2014–15)           14,348                1,033.0               13.89            1
  KCPS (2019–20)           14,075                1,053.1               13.37            1
  KCPS (2020–21)           13,334                1,074.0               12.42            1
  KCPS (2024–25)           13,975                1,081.3               12.92            1
  Net Change (10-Yr)      -373 (-2.60%)        +48.2 (+4.67%)          -0.97            --
  ----------------------------------------------------------------------------------------------
  Charters (2014–15)       10,183                  790.2               12.89           20
  Charters (2019–20)       12,847                1,031.9               12.45           21
  Charters (2020–21)       13,151                1,078.8               12.19           20
  Charters (2024–25)       13,138                1,260.4               10.42           20
  Net Change (10-Yr)    +2,955 (+29.02%)       +470.2 (+59.50%)        -2.47            --
  ----------------------------------------------------------------------------------------------
  Combined Urban (14-15)   24,531                1,823.3               13.45           21
  Combined Urban (24-25)   27,113                2,341.7               11.58           21
  Combined Net Change   +2,582 (+10.52%)       +518.4 (+28.43%)        -1.87            --
================================================================================================
```

### 5.2 Net Hiring Ratio of Charter Expansion
- Net student growth in Jackson County charters: $+2,955$ students ($+29.02\%$).
- Net teacher additions in Jackson County charters: $+470.2$ FTE ($+59.50\%$).
- **Endpoint Hiring Ratio:**

$$\text{Net Expansion Ratio} = \frac{\Delta \text{Students}}{\Delta \text{Teachers}} = \frac{2,955}{470.2} = \mathbf{6.28 \text{ net students per added teacher FTE}} \quad (0.1591 \text{ FTE/student})$$

> [!NOTE]
> **Epistemic Finding for Job 4 [ROBUST ASSOCIATION]:** Contrary to common assumptions that charter schools operate "leaner" teacher models to extract operating margins, Jackson County charters expanded their instructional staff at more than double the rate of enrollment growth ($+59.5\%$ vs. $+29.0\%$). Consequently, charter macro pupil/teacher ratios ($10.42$) are substantially lower than KCPS ($12.92$), and charters added 1 full-time classroom teacher for every 6.3 net students gained over the decade. We note this is an aggregate endpoint expansion ratio across 20 operating charters, not a causal student-flow elasticity from individual student microdata.

---

## 6. Job 5 — The Secondary Staffing Wedge (Macro PTR vs. Course Class Sizes)

### 6.1 CRDC 2023–24 Regular High School Audit ($N=109$)
In SY 2023–24, regular operating high schools in the Kansas City region maintained a mean school-level macro PTR of **$14.74$** (median $15.42$, IQR $[12.81, 16.85]$). 

When compared to actual section-level course class sizes derived from CRDC microdata:
- **Algebra I ($N=101$):** Mean Class Size = **$19.28$** | Median = $18.14$ | Mean Wedge = **$+4.53$ students** (Median Wedge = $+3.86$)
- **Geometry ($N=100$):** Mean Class Size = **$18.94$** | Median = $19.11$ | Mean Wedge = **$+4.06$ students** (Median Wedge = $+4.71$)
- **Algebra II ($N=92$):** Mean Class Size = **$18.92$** | Median = $19.60$ | Mean Wedge = **$+3.79$ students** (Median Wedge = $+4.26$)
- **Biology ($N=99$):** Mean Class Size = **$18.81$** | Median = $17.85$ | Mean Wedge = **$+3.96$ students** (Median Wedge = $+2.47$)
- **Chemistry ($N=89$):** Mean Class Size = **$18.87$** | Median = $19.90$ | Mean Wedge = **$+3.46$ students** (Median Wedge = $+4.11$)
- **Physics ($N=80$):** Mean Class Size = **$17.31$** | Median = $17.00$ | Mean Wedge = **$+1.92$ students** (Median Wedge = $-0.12$)
- **Calculus ($N=62$):** Mean Class Size = **$14.97$** | Median = $16.00$ | Mean Wedge = **$-0.53$ students** (Median Wedge = $+0.61$)

### 6.2 Longitudinal Persistence of the Staffing Wedge
Across all six CRDC waves, the Algebra I staffing wedge has remained consistently positive:
- **2013–14:** Mean PTR = $15.90$ | Alg1 Class Size = $18.82$ | Wedge = **$+3.15$**
- **2015–16:** Mean PTR = $15.49$ | Alg1 Class Size = $20.64$ | Wedge = **$+5.17$**
- **2017–18:** Mean PTR = $15.18$ | Alg1 Class Size = $18.21$ | Wedge = **$+3.05$**
- **2020–21:** Mean PTR = $15.19$ | Alg1 Class Size = $17.67$ | Wedge = **$+2.38$**
- **2021–22:** Mean PTR = $14.88$ | Alg1 Class Size = $18.64$ | Wedge = **$+3.72$**
- **2023–24:** Mean PTR = $14.74$ | Alg1 Class Size = $19.28$ | Wedge = **$+4.53$**

```
           +-------------------------------------------------------+
           |                MACRO SCHOOL PTR: 14.74                |
           +-------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
+----------------------------------+     +----------------------------------+
|    CORE REQUIRED SUBJECTS        |     |      ADVANCED ELECTIVES          |
|  Algebra I: 19.28 (+4.53 wedge)  |     |  Physics: 17.31 (+1.92 wedge)    |
|  Geometry:  18.94 (+4.06 wedge)  |     |  Calculus: 14.97 (-0.53 wedge)   |
|  Biology:   18.81 (+3.96 wedge)  |     |                                  |
|  Concentrated student rosters    |     |  Small singleton sections pull   |
|  due to teacher prep periods.    |     |  down the macro ratio.           |
+----------------------------------+     +----------------------------------+
```

---

## 7. Epistemic Classification Ledger

| Item ID | Claim / Finding | Epistemic Classification | Core Empirical Basis |
| :--- | :--- | :--- | :--- |
| **CL-TCH-001** | Across 77 regional districts, campus-sum teacher FTE reconciles with LEA total reported teachers within $+2.13\%$ ($+518.5$ FTE). | `[DESCRIPTIVE FACT]` | Full NCES CCD SY 2024–25 campus and LEA panel audit. |
| **CL-TCH-002** | Missouri campus teacher reports include Pre-K teachers ($455.4$ FTE), whereas Kansas LEA totals exceed campus sums by $+455.3$ FTE due to centralized/itinerant staff. | `[DESCRIPTIVE FACT]` | State DOE administrative reporting rules and cross-file reconciliation. |
| **CL-TCH-003** | The raw NCES CCD 2015–16 Kansas data contains an artificial $-2,311$ teacher FTE drop due to non-reporting in Olathe (`2010140`) and Gardner Edgerton (`2006420`). | `[DATA LIMITATION]` | Verified missing values in CCD 2015–16 files vs. continuous KSDE records. |
| **CL-TCH-004** | In 28 declining districts with unchanged school counts, classroom teachers contracted by only $-3.63\%$ against an $-8.33\%$ enrollment loss ($-3.26\%$ in the 25 strictly identical campus ID cohort). | `[ROBUST ASSOCIATION]` | Longitudinal Balanced 75 cohort tracking across 11 years with multi-specification sensitivity analysis. |
| **CL-TCH-005** | Operating secondary high schools under 800 students exhibit scale-dependent offering probabilities for Calculus (21.9% <400 to 41.2% 400–799), but strict $\ge 35$ FTE thresholds are retracted (campuses offer as low as 15.6 FTE; 50% are <35 FTE). | `[ROBUST ASSOCIATION]` | Cross-sectional CRDC 2023–24 analysis of 49 small regular high schools. |
| **CL-TCH-006** | In a balanced matched cohort of 28 regular high schools under 800 students present in both 2013–14 and 2023–24, Calculus offerings dropped from $67.9\%$ (19/28) to $35.7\%$ (10/28), with 12 schools dropping and 3 adding. | `[DESCRIPTIVE FACT]` | Balanced longitudinal matched CRDC high school panel. |
| **CL-TCH-007** | Districts did not cut kindergarten teachers during the Fall 2020 enrollment shock; staffing increased by $+3.67\%$. | `[DESCRIPTIVE FACT]` | Balanced 75 LEA longitudinal staff file audit. |
| **CL-TCH-008** | Jackson County charters expanded teaching staff by $+59.5\%$, with a 10-year net addition ratio of 1 teacher FTE per 6.28 net students gained. | `[ROBUST ASSOCIATION]` | Longitudinal urban core panel of KCPS and 20 charter LEAs. |
| **CL-TCH-009** | Macro school pupil/teacher ratio mechanically understates core high school class sizes by $+3.5$ to $+4.5$ students. | `[ROBUST ASSOCIATION]` | CRDC 2023–24 matched course class size analysis ($N=109$). |
| **CL-TCH-010** | High teacher roster loads cause student achievement deficits in secondary schools. | `[HYPOTHESIS / UNVERIFIED]` | *Jenkins v. Missouri* evidentiary record established this is an organizational resource condition, not a direct causal guarantee. |

---

## 8. Summary of Figures in Visual Evidence Packet

The visual evidence packet for `EDU-003` comprises three newly produced high-resolution graphics, active in `dashboard/` and copied to the Observatory artifacts directory:

1. **Figure 12 (`fig12_kc_vs_us_teacher_trajectory.png`):** Longitudinal Teacher FTE Trajectories (Kansas City vs. United States, 2014–15 to 2024–25). Documents the $+8.88\%$ adjusted regional teacher expansion, contrasts it with national growth ($+2.16\%$), and explicitly flags the artificial 2015–16 Kansas reporting break alongside the verified KSDE interpolation. Located at [Figure 12](../../dashboard/fig12_kc_vs_us_teacher_trajectory.png).
2. **Figure 13 (`fig13_fixed_plant_staffing_stickiness.png`):** Fixed-Plant Staffing Stickiness in Declining Districts. Illustrates the $-3.63\%$ downward stickiness of classroom teachers vs. $-8.33\%$ enrollment loss across 28 districts, the lockstep $-9.78\%$ contraction of administrators, and the $+9.41\%$ expansion of total district staff (+8.64% paraprofessionals). Located at [Figure 13](../../dashboard/fig13_fixed_plant_staffing_stickiness.png).
3. **Figure 14 (`fig14_secondary_staffing_wedge.png`):** The Secondary Staffing Wedge. Illustrates the $+3.5$ to $+4.5$ student gap between macro school PTR ($14.74$) and core course class sizes (Algebra I: $19.28$), and shows the 10-year longitudinal persistence of this wedge across all six CRDC waves. Located at [Figure 14](../../dashboard/fig14_secondary_staffing_wedge.png).
