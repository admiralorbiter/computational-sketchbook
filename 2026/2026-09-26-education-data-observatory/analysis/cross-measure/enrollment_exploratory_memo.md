# Comprehensive Exploratory Analysis Memo: Exhausting Existing Enrollment Evidence
**Observatory Analysis Document | Measure: `EDU-002 Student Enrollment`**
**Date:** September 26, 2026 | **Author:** Education Data Observatory Team | **Status:** `COMPLETE / FROZEN`

---

## Executive Summary & Mandate

Before advancing to teacher capacity (`EDU-003`), the Education Data Observatory established a foundational mandate: **fully exhaust the empirical evidence within the existing student enrollment data (`EDU-002`) and repair all universe inconsistencies.** 

This memorandum documents the completed audit of the Kansas City metropolitan public school universe across the Common Core of Data (CCD), the 11-year longitudinal panel (SY 2014–15 through SY 2024–25), and cross-measure linkages with the Civil Rights Data Collection (CRDC) and demographic complexity panels. 

All analytical assertions are strictly classified according to the Observatory's epistemic taxonomy:
- `[DESCRIPTIVE FACT]`: Directly observed accounting quantity or mathematical identity from audited data.
- `[ASSOCIATION]`: Observed correlation or statistical relationship across entities without claiming causal direction.
- `[HYPOTHESIS]`: Plausible causal or behavioral mechanism proposed for empirical testing.
- `[DATA LIMITATION]`: Inherent boundary, suppression, timing wedge, or reporting idiosyncrasy of the source.

---

## 1. Audit of the Universe & Reconciliation Gap

### 1.1 The Regional Universe Distinction
`[DATA LIMITATION]` Previous analyses encountered an aggregation discrepancy (+2,445 students) between district-level membership and the sum of school campus rosters. An audit of all 79 LEAs in the raw dataset revealed a critical geographic universe bug: **two state-operated administrative agencies were included whose administrative totals are statewide, but whose campus rosters were clipped to the 9-county KC region.**

`[DESCRIPTIVE FACT]` When the universe is partitioned into fully regional school districts versus statewide administrative agencies:
1. **Fully Regional Public Districts ($N=77$):**
   - Total LEA-reported enrollment: **330,356 students**.
   - Sum of campus-reported enrollments: **328,884 students**.
   - True Regional Reconciliation Gap: **$+1,472$ unassigned students (+0.446% of LEA membership)**.
   - **$61$ of $77$ districts ($79.2\%$)** reconcile with a difference of exactly zero ($\Delta = 0$).
   - **$16$ districts** report positive unassigned students ($\Delta > 0$).
   - **$0$ districts** report negative discrepancies ($\Delta < 0$).
2. **Statewide Administrative Agencies ($N=2$):**
   - *MO Division of Youth Services (DYS):* LEA membership = 496; in-region campus sum = 79; gap = **+417 students** (84.1% outside KC).
   - *MO Schools for the Severely Disabled:* LEA membership = 652; in-region campus sum = 96; gap = **+556 students** (85.3% outside KC).
   - *Combined statewide unassigned students:* **+973 students**. These agencies operate facilities across all 114 Missouri counties; omitting non-KC facilities created the artificial +973 wedge.

### 1.2 Outlier Analysis of the Regional Gap
`[DESCRIPTIVE FACT]` Across the 77 fully regional districts, the +1,472 reconciliation gap is heavily concentrated in a small handful of districts:
- **Hickman Mills C-1 (MO):** LEA = 5,067; Campus Sum = 4,472; **Gap = +595 (+11.7% of district)**.
- **De Soto USD 232 (KS):** LEA = 7,295; Campus Sum = 7,067; **Gap = +228 (+3.1%)**.
- **Shawnee Mission USD 512 (KS):** LEA = 26,513; Campus Sum = 26,330; **Gap = +183 (+0.7%)**.
- **Lee's Summit R-VII (MO):** LEA = 17,870; Campus Sum = 17,695; **Gap = +175 (+1.0%)**.
- **Bonner Springs USD 204 (KS):** LEA = 2,535; Campus Sum = 2,437; **Gap = +98 (+3.9%)**.
- **Turner USD 202 (KS):** LEA = 3,926; Campus Sum = 3,865; **Gap = +61 (+1.6%)**.
- **Paola USD 368 (KS):** LEA = 1,785; Campus Sum = 1,732; **Gap = +53 (+3.0%)**.
- **Blue Valley USD 229 (KS):** LEA = 22,252; Campus Sum = 22,225; **Gap = +27 (+0.1%)**.
- Remaining 8 districts have minor gaps between 1 and 19 students.

`[HYPOTHESIS]` In suburban unified districts (De Soto, Shawnee Mission, Lee's Summit), unassigned students reflect central administrative rolls, homebound instruction, specialized pre-K programs, and private/cooperative day school placements. In Hickman Mills C-1, the magnitude (+595 students, 11.7%) suggests a systematic administrative reporting practice (e.g., holding outplaced alternative, CTE, or virtual students on a central LEA holding roster rather than assigning building-level NCES identifiers).

---

## 2. Longitudinal Universes & Trajectories (2014–15 to 2024–25)

### 2.1 Three Distinct Estimands
`[DATA LIMITATION]` Measuring longitudinal enrollment requires declaring explicit rules for handling district openings, closings, and geographic universe boundaries. The Observatory defines three distinct estimands:

1. **Dynamic Fully Regional Universe ($N=78 \to 77$ LEAs):**
   `[DESCRIPTIVE FACT]` Enforces `lea_fully_within_region == True` in each school year. Captures genuine entries (e.g., new charter LEAs) and exits while excluding statewide agencies.
   - SY 2014–15 Baseline: **321,228 students** ($100.00$)
   - SY 2019–20 Peak: **329,357 students** ($102.53$) — $+8,129$ students ($+2.53\%$)
   - SY 2020–21 Break: **321,732 students** ($100.16$) — $-7,625$ students ($-2.32\%$) in a single year
   - SY 2024–25 Current: **318,883 students** ($99.27$) — Net 10-year change: **$-2,345$ students ($-0.73\%$)**
2. **Balanced 75-LEA Cohort ($N=75$ LEAs):**
   `[DESCRIPTIVE FACT]` Evaluates only the 75 districts operating continuously across all 11 years with complete data.
   - SY 2014–15 Baseline: **320,465 students** ($100.00$)
   - SY 2019–20 Peak: **328,860 students** ($102.62$)
   - SY 2020–21 Break: **321,078 students** ($100.19$) — $-7,782$ students ($-2.37\%$)
   - SY 2024–25 Current: **318,406 students** ($99.36$) — Net 10-year change: **$-2,059$ students ($-0.64\%$)**
3. **Unfiltered Panel (Contaminated):**
   `[DATA LIMITATION]` The raw uncurated panel included statewide agencies that underwent reporting restructuring, dropping from 327,761 to 320,031 ($-2.36\%$). This series is methodologically invalid for regional public school claims and is discarded.

### 2.2 Regional Trajectory vs. National Context
`[ASSOCIATION]` Kansas City public school enrollment diverged from the national trend in two distinct phases:
- **Pre-Pandemic (2014–2019):** KC grew substantially faster than the nation ($+2.53\%$ vs $+0.55\%$ nationally).
- **The Fall 2020 Drop:** KC mirrored the national collapse almost exactly ($-2.32\%$ in KC vs $-2.19\%$ nationally).
- **Post-Pandemic Plateau (2020–2025):** Nationally, public enrollment continued to drift downward (projected to hit $96.81\%$ of baseline by 2024–25). In contrast, Kansas City regional enrollment stabilized into a resilient plateau at $99.27\%$ of baseline.

---

## 3. Exploratory Analysis A: Regional Redistribution

### 3.1 Gross Churn vs. Net Stability
`[DESCRIPTIVE FACT]` Across the Balanced 75 cohort, net regional enrollment fell by only **$-2,059$ students ($-0.64\%$)** over 10 years. However, this macro-stability masks massive geographic redistribution:
- **$29$ districts grew**, adding a combined gross total of **$+11,986$ students**.
- **$46$ districts shrank**, losing a combined gross total of **$-14,045$ students**.

### 3.2 Top Growth and Decline Outliers
`[DESCRIPTIVE FACT]` Growth was heavily concentrated in outer-suburban rings and expanding charter networks:
- **Top Absolute Growth:**
  1. *Spring Hill USD 230 (KS):* $+2,454$ students ($+75.3\%$, $3,257 \to 5,711$)
  2. *North Kansas City 74 (MO):* $+1,562$ students ($+8.1\%$, $19,262 \to 20,824$)
  3. *Park Hill (MO):* $+829$ students ($+7.7\%$, $10,716 \to 11,545$)
  4. *Guadalupe Centers Schools (MO Charter):* $+826$ students ($+116.2\%$, $711 \to 1,537$)
  5. *Piper-Kansas City USD 203 (KS):* $+746$ students ($+38.0\%$, $1,965 \to 2,711$)
  6. *Crossroads Charter Schools (MO Charter):* $+707$ students ($+252.5\%$, $280 \to 987$)
  7. *KIPP Endeavor Academy (MO Charter):* $+695$ students ($+246.5\%$, $282 \to 977$)
  8. *Basehor-Linwood USD 458 (KS):* $+549$ students ($+22.9\%$, $2,393 \to 2,942$)
- **Top Absolute Decline:**
  1. *Hickman Mills C-1 (MO):* $-1,543$ students ($-24.7\%$, $6,244 \to 4,701$)
  2. *Raytown C-2 (MO):* $-1,453$ students ($-16.4\%$, $8,856 \to 7,403$)
  3. *Shawnee Mission USD 512 (KS):* $-1,324$ students ($-4.9\%$, $27,098 \to 25,774$)
  4. *Kansas City USD 500 (KS):* $-948$ students ($-4.5\%$, $21,158 \to 20,210$)
  5. *Olathe USD 233 (KS):* $-940$ students ($-3.3\%$, $28,439 \to 27,499$)
  6. *Independence 30 (MO):* $-743$ students ($-5.2\%$, $14,306 \to 13,563$)
  7. *Grandview C-4 (MO):* $-699$ students ($-16.5\%$, $4,232 \to 3,533$)
  8. *Belton 124 (MO):* $-687$ students ($-14.7\%$, $4,689 \to 4,002$)

### 3.3 County-Level and Distance Dynamics
`[DESCRIPTIVE FACT]` Growth was strictly segregated by county:
- **Growing Counties:** Platte Co., MO ($+1,331$ students, $+8.4\%$); Clay Co., MO ($+1,146$ students, $+2.9\%$); Johnson Co., KS ($+313$ students, $+0.3\%$).
- **Declining Counties:** Ray Co., MO ($-208$, $-6.4\%$); Leavenworth Co., KS ($-369$, $-2.8\%$); Miami Co., KS ($-535$, $-11.0\%$); Wyandotte Co., KS ($-733$, $-2.5\%$); Cass Co., MO ($-1,185$, $-6.7\%$); Jackson Co., MO ($-1,819$, $-1.8\%$).

`[DESCRIPTIVE FACT]` Distance from downtown Kansas City reveals the regional suburban belt (SY 2024–25):
- *0–5 miles:* 87 campuses | 36,035 students ($11.0\%$)
- *5–10 miles:* 138 campuses | 64,531 students ($19.6\%$)
- *10–15 miles:* 130 campuses | 66,552 students ($20.2\%$)
- *15–20 miles:* 140 campuses | 81,220 students ($24.7\%$) — **Peak Regional Belt**
- *20–30 miles:* 143 campuses | 67,720 students ($20.6\%$)
- *30+ miles:* 48 campuses | 13,001 students ($4.0\%$)

`[ASSOCIATION]` More than **$65\%$ of all public school students** in the metropolitan area attend campuses located between 10 and 30 miles from the urban center.

---

## 4. Exploratory Analysis B: System Concentration & Charters

### 4.1 Concentration Metrics
`[DESCRIPTIVE FACT]` Despite having 77 distinct operating school districts, student enrollment is concentrated in the largest municipal and suburban unified districts:
- **Top 5 LEAs:** 119,750 students (**$36.25\%$** of regional enrollment).
  - *Districts:* Olathe ($28,195$), Shawnee Mission ($26,513$), Blue Valley ($22,252$), Kansas City KS ($21,538$), North Kansas City ($21,252$).
- **Top 10 LEAs:** 193,565 students (**$58.59\%$**).
  - *Additional:* Lee's Summit ($17,870$), Kansas City 33 MO ($15,079$), Blue Springs ($14,657$), Independence ($14,272$), Park Hill ($11,937$).
- **Top 20 LEAs:** 257,117 students (**$77.83\%$**).
- **Herfindahl-Hirschman Index (HHI):** **$424.3$**.
  - `[ASSOCIATION]` The HHI value of 424 is far below standard antitrust/concentration thresholds (1,500), confirming that Kansas City's public education governance is geographically decentralized, with no single entity wielding monopoly or dominant-scale enrollment share.

### 4.2 Charter Sector Footprint
`[DESCRIPTIVE FACT]` In SY 2024–25, **$21$ charter LEAs** operate across the region, educating **19,443 students (5.89% of metro public enrollment)**. 
`[DATA LIMITATION]` Charter LEAs operate exclusively on the Missouri side of the state line, and virtually all are concentrated within the historical boundary of Kansas City Public Schools (KCPS / Kansas City 33). Within that urban core footprint, charter LEAs educate over **$40\%$ of all public school students**, creating high localized choice and market fragmentation that is invisible in regional averages.

---

## 5. Exploratory Analysis C: School Scale & Student Exposure

### 5.1 The Exposure Skew Across Grade Bands
`[DESCRIPTIVE FACT]` Evaluating the 665 operating public schools with enrollment $>0$ in SY 2024–25:
- **Elementary ($N=393$):** Median = 374 | Unweighted Mean = 390.1 | Student-Weighted Mean = **444.7** (1.19x median).
- **Middle ($N=122$):** Median = 584 | Unweighted Mean = 559.3 | Student-Weighted Mean = **642.5** (1.10x median).
- **High ($N=114$):** Median = 843 | Unweighted Mean = 904.8 | Student-Weighted Mean = **1,419.2** (1.68x median).

### 5.2 High School Mega-Campuses
`[DESCRIPTIVE FACT]` Campus scale exposure in secondary education is severely right-skewed:
- High schools enrolling $<250$ students make up **$26.3\%$ of high school buildings** ($N=30$, primarily alternative, specialized, and career centers), but educate only **$2.9\%$ of high school students**.
- High schools enrolling $1,000$ to $1,499$ students make up **$20.2\%$ of buildings** ($N=23$) and educate **$27.9\%$ of students**.
- High schools enrolling $1,500+$ students make up **$24.6\%$ of buildings** ($N=28$) and educate **$49.8\%$ of students**.
- Combined, **$77.7\%$ of all high school students in Kansas City attend a campus enrolling 1,000+ students**.

`[ASSOCIATION]` While public discourse and policy debates often envision secondary schools as 800-pupil community institutions, the reality for the typical Kansas City adolescent is a comprehensive suburban mega-campus of 1,400 to 2,400 peers.

---

## 6. Exploratory Analysis D: District Portfolio Response

### 6.1 Asymmetric Portfolio Elasticity
`[DESCRIPTIVE FACT]` Tracking the 75 balanced districts between 2014–15 and 2024–25 reveals an asymmetric institutional response to enrollment changes:

| District Trajectory | Operating Schools Added | Operating Schools Closed | Operating Schools Unchanged | Total Districts |
| :--- | :---: | :---: | :---: | :---: |
| **Enrollment Grew** | 12 | 1 | 16 | 29 |
| **Enrollment Shrank** | 14 | 4 | 28 | 46 |

### 6.2 The Density Hollow-Out in Shrinking Districts
`[DESCRIPTIVE FACT]` When districts grew substantially, they added physical plants:
- Spring Hill added 4 schools ($7 \to 11$), maintaining student density ($465 \to 519$ students/school).
- Park Hill added 3 schools ($17 \to 20$, density $630 \to 577$).
- North Kansas City added 2 schools ($32 \to 34$, density $602 \to 612$).

`[DESCRIPTIVE FACT]` However, when districts experienced sustained enrollment decline, **$28$ of $46$ declining districts ($60.9\%$) kept the exact same number of school buildings open**. As a direct mathematical consequence, campus student density hollowed out:
- *Kansas City KS (USD 500):* Lost $-948$ students while keeping all 43 schools open (density fell from 492 to 470 students/school).
- *Grandview C-4:* Lost $-699$ students while keeping all 9 schools open (density plunged from 470 to 393 students/school, $-77.7$ students/campus).
- *Fort Leavenworth:* Lost $-378$ students while keeping 4 schools open (density fell from 436 to 342, $-94.5$ students/campus).
- *Harrisonville R-IX:* Lost $-366$ students while keeping 7 schools open (density fell from 351 to 299, $-52.3$ students/campus).
- *Paola USD 368:* Lost $-225$ students while keeping 4 schools open (density fell from 494 to 438, $-56.3$ students/campus).

`[HYPOTHESIS]` Closing a school campus carries immense political and community friction. Districts experiencing demographic contraction choose to absorb enrollment loss by reducing building enrollment density rather than shuttering facilities. However, because operating a physical campus incurs substantial fixed overhead (principals, custodians, HVAC, cafeteria staff, office staff), maintaining fixed plant footprints in declining districts inevitably diverts per-pupil funding away from instructional classroom teachers.

---

## 7. Exploratory Analysis E: Pre-K Institutional Structure

`[DESCRIPTIVE FACT]` In SY 2024–25, public schools in the Kansas City metro enrolled **10,603 Pre-K students**. These students are organized into two distinct structural delivery models:
1. **Integrated Elementary Classrooms ($74.4\%$):** **7,885 students** are housed in early childhood classrooms situated within standard K–5 elementary school buildings.
2. **Dedicated Standalone Early Childhood Centers ($25.6\%$):** **2,718 students** attend standalone, dedicated early childhood campuses (e.g., Grace Early Childhood Center in Excelsior Springs with 228 students; Shull Early Learning Center in Raymore-Peculiar with 189 students).

`[DATA LIMITATION]` This structural dichotomy demonstrates why simple "all-grade" enrollment denominators distort capacity and staffing ratios. In dedicated Pre-K centers, staff ratios are governed by early-childhood licensing standards (often 10:1 or lower), whereas elementary schools with integrated Pre-K blend two fundamentally different staffing regimes into a single campus record. The Observatory's strict separation of Pre-K (`ENR-NCES-K12-MEMBER` vs. `ENR-NCES-FALL-MEMBER-SCH`) is essential to prevent systematic distortion.

---

## 8. Exploratory Analysis F: Cross-Measure Connections (CRDC & Complexity)

### 8.1 School Scale vs. Course-Level Class Sizes (CRDC Wave 2021–22)
`[ASSOCIATION]` Linking NCES high school enrollment with CRDC section-level data reveals how campus scale influences actual instructional class size:
- **Introductory Core Courses:**
  - *Algebra I ($N=113$):* Mean Size = 17.1 | Median = 17.4 | Correlation with K–12 Enrollment: **$r = +0.184$**
  - *Biology ($N=116$):* Mean Size = 18.0 | Median = 17.6 | Correlation with K–12 Enrollment: **$r = +0.173$**
  - *Chemistry ($N=100$):* Mean Size = 16.8 | Median = 17.0 | Correlation with K–12 Enrollment: **$r = +0.225$**
  - *Geometry ($N=108$):* Mean Size = 17.7 | Median = 17.8 | Correlation with K–12 Enrollment: **$r = +0.291$**
- **Advanced / Upper-Level Courses:**
  - *Algebra II ($N=100$):* Mean Size = 17.0 | Median = 17.4 | Correlation with K–12 Enrollment: **$r = +0.483$**
  - *Physics ($N=91$):* Mean Size = 14.0 | Median = 14.4 | Correlation with K–12 Enrollment: **$r = +0.471$**

`[HYPOTHESIS]` In foundational courses required for graduation (Algebra I, Biology), class size is tightly governed by district staffing caps and teacher availability, resulting in weak scale correlations ($r \approx 0.17 - 0.18$). However, in elective and advanced courses (Algebra II, Physics), campus scale becomes decisive: large comprehensive high schools have sufficient enrollment volume to fill standard 20–25 student sections, whereas small high schools either operate very small 6–12 student sections or cannot justify offering the course at all.

### 8.2 School Scale vs. Student Demographic Complexity (SY 2023–24)
`[ASSOCIATION]` Linking school enrollment with student demographic complexity indicators reveals consistent negative correlations:
- **Special Education (IDEA / IEP) Share ($N=651$):** Mean = $14.7\%$ | Correlation with Enrollment: **$r = -0.230$**
- **Free/Reduced Lunch (FRL) Rate ($N=642$):** Mean = $48.0\%$ | Correlation with Enrollment: **$r = -0.189$**
- **English Learner (LEP / ELL) Share ($N=651$):** Mean = $10.3\%$ | Correlation with Enrollment: **$r = -0.073$**

`[HYPOTHESIS]` Smaller schools and specialized facilities disproportionately serve higher-need student populations requiring specialized instructional settings, whereas large comprehensive suburban schools serve lower shares of students with IEPs and economic disadvantages.

---

## 9. Research Queue: Highest-Value Unanswered Questions

Having exhausted the descriptive capabilities of existing enrollment data alone, the Observatory registers the following 8 formal research questions for empirical investigation:

1. `RQ-ENR-001` (Administrative Outlier Audit): What specific student roster categories account for the +595 unassigned student gap in Hickman Mills C-1 and the +228 gap in De Soto USD 232?
2. `RQ-ENR-002` (Birth Cohort vs. Market Share): To what extent was the Fall 2020 regional enrollment drop ($-7,625$ students) driven by demographic birth cohort declines versus market-share loss to homeschooling and private schooling?
3. `RQ-ENR-003` (Urban Core Charter Substitution): Over the 11-year panel, has charter expansion in Kansas City 33 generated net new public school enrollment or pure substitution from the traditional district?
4. `RQ-ENR-004` (Fixed-Plant Overhead Penalty): What is the per-pupil operating cost penalty borne by districts that experienced $>15\%$ enrollment declines while maintaining 100% of their physical school plants?
5. `RQ-ENR-005` (Curricular Breadth Threshold): At what minimum high school enrollment threshold does a school become capable of offering advanced STEM electives (Calculus, Physics, AP courses) without creating fiscal deficits?
6. `RQ-ENR-006` (Attendance Wedge by Locale): Does the gap between Fall Enrollment (`EDU-002`) and Average Daily Attendance (`EDU-015`) vary systematically across urban, suburban, and rural locales?
7. `RQ-ENR-007` (Pre-K Delivery Cost Efficiency): Do standalone early childhood centers operate with higher teacher FTE per pupil than elementary-integrated Pre-K classrooms?
8. `RQ-ENR-008` (Missouri SB 727 Transition Modeling): Which Kansas City districts will gain or lose state foundation revenue as Missouri phases from 100% WADA to 50% WADA / 50% weighted membership by FY2030?

---

## 10. Recommended Next Measure: `EDU-003 Classroom Teacher FTE`

With `EDU-002` thoroughly audited, its universes corrected, and its regional distribution dynamics fully exhausted, the Observatory is now prepared to advance to the next foundational measure:

### Justification for `EDU-003 Classroom Teacher FTE`:
1. **Completing the Capacity Ratio:** `EDU-002` (Student Enrollment) serves as the numerator for `EDU-001` (Pupil / Teacher Ratio). Without an equally rigorous operationalization of instructional staffing (`EDU-003`), `EDU-001` remains an ungrounded theoretical construct.
2. **Untangling Staff Categorization Wedges:** Just as enrollment data harbored subtle semantic traps (unassigned students, zero-membership schools, Pre-K mixing), teacher data harbors major definential ambiguities: classroom teachers vs. instructional aides vs. counselors vs. administrators.
3. **Evaluating the Institutional Density Paradox:** The portfolio response findings in this memo revealed that 28 declining districts kept all schools open while enrollment dropped. Only by analyzing teacher FTE (`EDU-003`) can we determine whether districts cut classroom teachers to pay for fixed physical overhead, or whether staffing levels were preserved, causing class sizes to plunge.

**Action:** Recommend initiating `EDU-003 Classroom Teacher FTE` following the Observatory's standardized dossier workflow.
