# Measure Dossier: EDU-002 — Student Headcount Enrollment

> **Observatory Standard:** Student enrollment is the foundational denominator of public education finance and capacity analysis. Yet in administrative data systems, "how many students there are" is not a single unambiguous quantity. This dossier audits the multi-layered semantics of enrollment: the **LEA–School Membership Reconciliation Gap** (why LEA membership does not equal the sum of school enrollments), the **Pre-K Inclusion Wedge**, the verified taxonomy of **26 operational zero-membership campuses**, the **Fall 2020 enrollment drop**, and the **National Contextualization** of regional school scales.
>
> *Principle: Source ≠ Field ≠ Operationalization ≠ Measure ≠ Claim.*
> *Rule of thumb: Complete measurement semantics before modeling. Description before explanation.*

---

## 1. Identity & Classification

| Attribute | Specification |
| :--- | :--- |
| **Measure ID** | `EDU-002` |
| **Canonical Name** | Student Headcount Enrollment |
| **Short Identifier / Slug** | `student-enrollment` |
| **Status** | `audited` (**FROZEN / READY FOR CROSS-MEASURE USE**) |
| **Lifecycle Stage** | Epistemic Ladder: `source` $\to$ `field` $\to$ `operationalization` $\to$ `measure` $\to$ `description` $\to$ `validation` $\to$ `relationships` $\to$ `explanation` |
| **Category** | Enrollment & Demographics |
| **Construct Nature** | Directly Reported Administrative Census Item (Fall Snapshot Headcount) |
| **Associated Operationalizations** | [`ENR-NCES-FALL-MEMBER-SCH`](../../registry/operationalizations.csv), [`ENR-NCES-FALL-MEMBER-LEA`](../../registry/operationalizations.csv), [`ENR-NCES-K12-MEMBER`](../../registry/operationalizations.csv) |
| **Excluded / Contrasting Constructs** | Average Daily Attendance ([`EDU-015`](../../registry/measures.csv)), State Funding / Weighted Enrollment ([`EDU-016`](../../registry/measures.csv)) |

---

## 2. Definitions & Conceptual Boundaries

### 2.1 Plain-Language Definition
Student Headcount Enrollment is the official count of individual pupils registered on the active membership rolls of a public school campus or local education agency (district) on a designated census date (traditionally on or near October 1 of each school year). It answers a single, narrow question: **"How many individual children are actively enrolled?"**

> [!CAUTION]
> **Enrollment is Neither Attendance Nor State Funding FTE.** 
> 1. An enrolled student is not necessarily in attendance every day. Cumulative student illness and chronic absenteeism create a 6% to 10% wedge between **Membership** (headcount) and **Average Daily Attendance (ADA)**.
> 2. Enrollment is not statutory funding capacity. In Missouri, funding is historically driven by attendance (transitioning to a hybrid count under SB 727); in Kansas, funding formulas apply statutory lookbacks and demographic weightings to audited FTEs.
> 3. Summing school-level enrollments does **not** equal district-level enrollment. In the Kansas City metro area alone, LEA memberships exceed the sum of school rosters by **+2,445 students (+0.74%)**.

### 2.2 Formal / Statistical Definition
For an educational entity $i$ (school campus $s$ or local education agency $d$) in school year $t$:

$$E_{i,t} = \sum_{j \in \mathcal{P}_t} \mathbb{I}\Big(\text{Pupil } j \text{ is actively enrolled in entity } i \text{ as of census date } \tau_t\Big)$$

Where:
- $\mathcal{P}_t$ is the population of children residing within or legally admitted to the jurisdiction in year $t$.
- $\mathbb{I}(\cdot)$ is an indicator function returning 1 if pupil $j$ satisfies state statutory admission, residency, and non-withdrawal criteria on census date $\tau_t$ (e.g., October 1 in MO; September 20 in KS).
- Each student is counted as an integer headcount ($E_{i,t} \in \mathbb{N}_0$) without weighting or fractional proration.

### 2.3 Aggregation Rules & Four Distinct Estimands
When aggregating or summarizing enrollment across a collection of schools (e.g., across a metropolitan region, district, or state), researchers must distinguish between four distinct estimands answering different questions:

$$\begin{aligned}
\text{1. Total Regional / System Scale (Sum):} \quad E_{\text{total}} &= \sum_{i=1}^N E_i \\
\text{2. Unweighted Campus Mean:} \quad \overline{E}_{\text{unweighted}} &= \frac{1}{N}\sum_{i=1}^N E_i \\
\text{3. Median Campus Size & IQR:} \quad E_{\text{median}} &= \text{Median}(E_1, E_2, \dots, E_N) \\
\text{4. Student-Weighted Campus Exposure:} \quad \overline{E}_{\text{student-weighted}} &= \sum_{i=1}^N \left(\frac{E_i}{E_{\text{total}}}\right) E_i = \frac{\sum_{i=1}^N E_i^2}{\sum_{i=1}^N E_i}
\end{aligned}$$

| Estimand | Mathematical Nature | Research Question Answered | Kansas City Metro Benchmark (SY 2024–25) |
| :--- | :--- | :--- | :--- |
| **Total Regional Enrollment** ($\sum E_i$) | Simple sum across all entities | *How many total public school students are enrolled across the regional jurisdiction?* | **327,998 students** (Campus Headcount sum) / **330,443 students** (LEA Member sum) |
| **Median Campus Size** | 50th percentile of campus distribution | *What is the size of the middle/typical school facility, robust to extreme outliers?* | Elementary: **374** \| Middle: **584** \| High: **843** |
| **Unweighted Campus Mean** | Arithmetic mean of school enrollments | *What is the average administrative size of a school building plant?* | Elementary: **390** \| Middle: **559** \| High: **905** |
| **Student-Weighted Campus Exposure** | Student-weighted mean ($\frac{\sum E^2}{\sum E}$) | *What is the enrollment size of the school attended by a randomly selected enrolled student?* | Elementary: **428** \| Middle: **643** \| High: **1,289** |

> [!NOTE]
> **The High School Scale Skew:** While the median Kansas City high school enrolls 843 students, the **student-weighted high school size is 1,289 students**. Because mega-campuses like Blue Springs High (2,429 students) and Liberty North High (2,262 students) hold disproportionate shares of the student population, the typical enrolled teenager attends a high school significantly larger than the median campus building.

### 2.4 Unit & Scale
- **Unit of Measurement:** `students` (discrete integer count of persons).
- **Theoretical Range:** $[0, \infty)$.
- **Empirical Realistic Range:**
  - Individual regular campuses: 20 to ~3,000 students.
  - Kansas City Metro Range (SY 2024–25): Elementary (26 to 1,496); Middle (68 to 1,055); High (10 to 2,429).
  - Operating Zero-Membership Campuses: 26 schools in the KC metro report exactly $E = 0$ (verified shared-time CTE centers, alternative academies, and treatment programs).

---

## 3. Provenance & Operationalization Inventory

The Observatory strictly restricts `EDU-002` to **Student Headcount Enrollment**, cataloging three concrete operationalizations in [`registry/operationalizations.csv`](../../registry/operationalizations.csv):

| Operationalization ID | Implementing Authority | Target Population | Formula / Source Fields | Provenance Tier |
| :--- | :--- | :--- | :--- | :--- |
| **`ENR-NCES-FALL-MEMBER-SCH`** | NCES CCD Non-Fiscal School Universe | All public elementary and secondary schools | `MEMBER` | **Tier 1 National Administrative Census.** Fall snapshot headcount across all grades offered (Pre-K to 12). |
| **`ENR-NCES-FALL-MEMBER-LEA`** | NCES CCD Non-Fiscal LEA Survey | Operating local public school districts | `MEMBER` | **Tier 1 National Administrative Census.** Total LEA membership under district governance. |
| **`ENR-NCES-K12-MEMBER`** | Observatory Research Specification | Regular public elementary and secondary schools / LEAs | $\text{MEMBER} - \max(0, \text{PK})$ | **Tier 1 Research-Derived Adjusted.** Deducts Pre-K enrollment to isolate the conventional K–12 grade span. |

### Conceptual Contrasts (Separate Measures)
The following constructs are **not** operationalizations of `EDU-002` and are formally segregated into separate measures:
- **Average Daily Attendance (ADA) ([`EDU-015`](../../registry/measures.csv)):** Cumulative attendance hours divided by scheduled term hours. Typically 90%–94% of headcount membership.
- **State Funding Enrollment / Weighted Enrollment ([`EDU-016`](../../registry/measures.csv)):** State statutory funding equivalents incorporating statutory lookbacks (e.g., Kansas greater of current year, prior year, or 2-year average) and programmatic weightings (bilingual, at-risk, transportation).

---

## 4. Scope, Granularity & Temporal Disambiguation

| Dimension | Specification | Notes & Boundary Conditions |
| :--- | :--- | :--- |
| **Target Population** | Public elementary and secondary pupils | Includes Pre-K if operated by public LEA |
| **Unit of Observation** | School Campus (`NCESSCH`) or LEA District (`LEAID`) | Must distinguish campus rosters from LEA membership rolls |
| **Geographic Granularity** | Campus, LEA, County, Metropolitan Region, State, National | Aggregation must account for the LEA–School Gap |
| **Temporal Granularity** | Annual Fall Snapshot | Collected on or near October 1 (MO) / September 20 (KS) |
| **School Year of Reference (SY)** | `SY 2024–25` (Anchor Year) | **Primary Indexing Dimension** |
| **Collection Snapshot Date** | October 1 (MO) / September 20 (KS) | Standardized state census dates |
| **Publication / Release Date** | Provisional: +12 to 14 months; Final: +20 to 24 months | Public CCD release lag |
| **Earliest Available Year** | SY 1986–87 | Continuous digital CCD records |
| **Latest Audited Year** | SY 2024–25 | Audited in KC Education Capacity Study |
| **Expected Update Cadence** | Annual | |

> [!IMPORTANT]
> **Analytical Grade-Span vs. Compulsory Attendance:** The operationalization `ENR-NCES-K12-MEMBER` is defined as **K–12 Grade-Span Membership**. K–12 serves as an analytical grade-span boundary isolating elementary and secondary schools from non-compulsory Pre-K. It is **not** synonymous with compulsory attendance: under § 167.031 RSMo, Missouri compulsory attendance begins at age 7; Kansas under K.S.A. 72-3120 defines compulsory attendance by age (7 to 18) rather than grade level.

---

## 5. Universe Definitions & Analytical Subsets (The 4-Tier Universe)

The Observatory preserves unusual educational entities rather than deleting them. An alternative academy or shared-time technical center is valid empirical data about an institutional delivery model, not "dirty data."

### A. Source Universe
All records reported in the NCES CCD Public School Universe Directory (`ccd_sch_029_XX_l_1a.csv`). In the 9-county KC metro area (SY 2024–25), this comprises **691 operating public schools** across **77 operating LEAs**.

### B. Mathematical Validity Requirements
- $E_{i,t} \ge 0$.
- All negative missing/suppression codes (`-1` Missing, `-2` Not Applicable, `-9` Suppressed) recoded to `NaN`.
- Records where $E_{i,t} = 0$ are preserved and evaluated under the zero-membership taxonomy.

### C. Entity-Type & Anomaly Flags
- `flag_zero_membership`: Operating school with $E = 0$ (26 operating schools in KC metro).
- `flag_prek_only`: Dedicated Early Childhood Center enrolling exclusively Pre-K ($100\%$ PK, 18 campuses in KC).
- `flag_virtual`: Virtual / cyber school (e.g., MO Virtual Instruction Program).
- `flag_reconciliation_gap`: LEA where district enrollment exceeds campus sum by $> 2.0\%$ (e.g., Hickman Mills C-1 at $+11.7\%$).

### D. Recommended Analytic Comparison Universes
1. **Standard K–12 Comprehensive Campus Universe:**
   - Operating local regular public schools (`TYPE == 1`, `STATUS in [1, 3, 8]`).
   - Enrollment threshold: $E \ge 10$.
   - Dedicated Pre-K centers and zero-membership CTE campuses tracked in separate panels.
2. **K–12 Grade-Span Membership Universe:**
   - Operationalization: `ENR-NCES-K12-MEMBER` ($E_{\text{K12}} = \text{MEMBER} - \text{PK}$).
   - Ensures cross-district comparability by eliminating early childhood programmatic variation.
3. **Specialized & Vocational Technical Universe:**
   - Dedicated monitoring of regional trade and career centers operating on shared-time enrollment models.

---

## 6. Empirical Source Audits

### 6.1 The LEA–School Membership Reconciliation Gap
In empirical reality, **LEA-reported membership systematically exceeds the sum of school campus memberships**:
$$\Delta_{\text{reconciliation}} = E_{\text{LEA}} - \sum_{s \in \text{LEA}} E_s$$

In the 9-county Kansas City metro area in SY 2024–25:
- Total LEA-reported enrollment: **330,443 students**.
- Sum of school-reported enrollments: **327,998 students**.
- Regional Discrepancy: **$+2,445$ unassigned students (+0.74%)**.

#### Empirical Outlier Ledger (SY 2024–25):
| District Name (State) | LEA Membership | Campus Sum | Reconciliation Gap ($\Delta$) | Gap (%) | Explanatory Status | Candidate Mechanisms / Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Hickman Mills C-1 (MO)** | 5,082 | 4,487 | **+595** | **+11.7%** | `unresolved` | Candidate: Out-of-district day placements, central alternative roster. Queued for audit (`INV-ENR-001`). |
| **MO Schools for Severely Disabled (MO)** | 652 | 96 | **+556** | **+85.3%** | `verified_structure` | State agency reporting structure: regional day facilities held on central district roster (`INV-ENR-003`). |
| **MO Division of Youth Services (MO)** | 496 | 79 | **+417** | **+84.1%** | `verified_structure` | State juvenile justice agency: students held on central administrative roster (`INV-ENR-003`). |
| **De Soto USD 232 (KS)** | 7,370 | 7,142 | **+228** | **+3.1%** | `unresolved` | Candidate: Specialized early childhood / virtual program roster (`INV-ENR-002`). |
| **Shawnee Mission USD 512 (KS)** | 26,050 | 25,867 | **+183** | **+0.7%** | `candidate_mechanism` | Candidate: Central pre-K and specialized day placements. |
| **Lee's Summit R-VII (MO)** | 17,910 | 17,735 | **+175** | **+1.0%** | `candidate_mechanism` | Candidate: Alternative program placements and outplaced special services. |

> [!WARNING]
> **Methodological Consequence:** Summing school-level CCD files systematically undercounts district students and distorts per-pupil calculations. Out-of-district day placements, homebound instruction, hospital programs, regional cooperatives, and central office administrative holding rosters represent **candidate mechanisms** that must be audited district-by-district rather than assumed.

#### Investigation Queue:
- `INV-ENR-001`: Audit Hickman Mills C-1 (+595 gap) against Missouri DESE Core Data/MOSIS student assignment files.
- `INV-ENR-002`: Verify De Soto USD 232 (+228 gap) against KSDE audited September 20 headcounts.
- `INV-ENR-003`: Document state administrative agency reporting rules for DYS and State Schools for Severely Disabled.

---

### 6.2 Verified Taxonomy of Operating Zero-Membership Schools
In SY 2024–25, **26 operating public schools** in the Kansas City metro report `enrollment_total == 0` in NCES CCD files while employing certified teaching staff. An audit of NCES school metadata (`school_type_desc`, `is_vocational`, `is_alternative`, `classroom_teacher_fte`) reveals four distinct institutional models:

1. **Career and Technical Education (CTE) Institutes ($N=6$):**
   - *Campuses:* Cass Career Ctr (14.0 FTE), Excelsior Springs Career Ctr (10.5 FTE), Career & Tech Ctr at Ft. Osage (17.4 FTE), Manual Career Tech Ctr (11.5 FTE), Herndon Career Ctr (19.0 FTE), Northland Career Ctr (13.2 FTE).
   - *Mechanism:* Legitimate **shared-time operational model** explicitly documented by NCES. High school students attend part-time for technical training while their primary membership is credited to their home comprehensive high school.
2. **Alternative Learning Academies & Innovation Studios ($N=11$):**
   - *Campuses:* Center for Educational Development (34.99 FTE), LEAD Innovation Studio (44.71 FTE), Independence Academy (43.80 FTE), Valley View High (23.00 FTE), Raytown Education Ctr (14.00 FTE), Grandview Alternative (10.80 FTE), Lewis and Clark (10.10 FTE), Burke Academy (1.00 FTE), Juvenile Justice Ctr (0.00 FTE), Liberty Academy (0.00 FTE), Center Academy for Success (0.00 FTE).
   - *Mechanism:* Students remain dual-rostered at sending secondary schools or credited at the district level.
3. **Specialized Treatment & Day Centers ($N=7$):**
   - *Campuses:* Success Academy (38.99 FTE), Northwood School (11.50 FTE), Russell Jones Ed Center (10.83 FTE), STAR School (0.00 FTE), Crittenton Treatment Center (1.00 FTE), Day Treatment (0.00 FTE), Miller Park Center (0.00 FTE).
   - *Mechanism:* Psychiatric residential facilities, court-mandated placements, or specialized therapeutic day programs.
4. **Special Education Facilities & Regional Cooperatives ($N=2$):**
   - *Campuses:* B W Sheperd School (MO Schools for Severely Disabled, 0.0 FTE at building), Platte Valley Coop (North Platte Co. R-I, 0.0 FTE at building).
   - *Mechanism:* Centralized cooperative accounting where staff and students are assigned at the LEA or intermediate unit level.

---

### 6.3 State Funding Semantics: Missouri SB 727 & Kansas Formula Audits

#### Missouri Foundation Funding: The SB 727 Transition Break
Prior to FY2026, Missouri state foundation formula distributions were based almost exclusively on **Weighted Average Daily Attendance (WADA)**, not fall enrollment. Beginning in FY2026, **Senate Bill 727 (enacted 2024)** phases weighted membership into the foundation formula over a five-year transition:
- **Pre-FY2026:** Predominantly WADA framework.
- **FY2026:** 90% WADA calculation + 10% weighted membership.
- **FY2027:** 80% WADA + 20% weighted membership.
- **FY2028:** 70% WADA + 30% weighted membership.
- **FY2029:** 60% WADA + 40% weighted membership.
- **FY2030:** Equal **50% WADA / 50% weighted membership** distribution.

This represents a major statutory break in Missouri education finance: the state funding count is transitioning from pure attendance to a hybrid attendance-enrollment construct.

#### Kansas School Finance: Audited FTE and Statutory Lookbacks
In Kansas, under the Kansas School Equity and Enhancement Act (KSEEA, K.S.A. 72-5131 et seq.), state funding enrollment is **not** simply headcount or a half-day kindergarten formula. 
- The base student count is determined by statutory lookback: the **greater of** (1) current-year audited FTE, (2) preceding-year audited FTE, or (3) the average of the preceding two school years.
- Programmatic weightings (At-Risk, High-Density At-Risk, Bilingual, Transportation, CTE, Special Education) are then added to this base to calculate total weighted funding units.

Both state constructs are tracked as separate measures (`EDU-015` and `EDU-016`) rather than conflated with `EDU-002`.

---

## 7. Longitudinal Trajectory & Candidate Hypotheses

Between SY 2014–15 and SY 2024–25 across the 77 school districts of the Kansas City metropolitan area, K–12 public school enrollment followed an observable 11-year trajectory:

```
School Year     KC K-12 Enrollment     Annual Change      Index (2014-15=100)     Descriptive Period Label
------------------------------------------------------------------------------------------------------------------
2014-15         327,699                 --                100.00                  Baseline
2015-16         325,483                 -2,216 (-0.68%)    99.32                  Minor demographic dip
2016-17         326,762                 +1,279 (+0.39%)    99.71                  Suburban growth
2017-18         329,013                 +2,251 (+0.69%)   100.40                  Suburban growth
2018-19         330,064                 +1,051 (+0.32%)   100.72                  Suburban growth
2019-20         330,128                 +64    (+0.02%)   100.74                  PRE-PANDEMIC PEAK
2020-21         322,818                 -7,310 (-2.21%)    98.51                  FALL 2020 ENROLLMENT DROP
2021-22         321,304                 -1,514 (-0.47%)    98.05                  Post-break stabilization
2022-23         322,785                 +1,481 (+0.46%)    98.50                  Partial cohort bounce
2023-24         320,830                 -1,955 (-0.61%)    97.90                  Cohort contraction
2024-25         320,031                 -799   (-0.25%)    97.66                  -3.06% from 2019-20 Peak
```

### The Observed Empirical Facts:
1. **The Fall 2020 Drop:** In a single year, regional K–12 public enrollment dropped by **$-7,310$ students ($-2.21\%$)**.
2. **Post-2020 Stagnation:** Across five subsequent school years, regional public enrollment has remained plateaued between 320,000 and 322,800 students, remaining **$-10,097$ students ($-3.06\%$) below peak**.

### Candidate Hypotheses (Future Research Queue):
The Observatory distinguishes between observed trendlines and causal explanations. The following candidate hypotheses are registered for empirical testing:
- `H-ENR-001`: Kindergarten entry deferral contributed disproportionately to the Fall 2020 enrollment drop.
- `H-ENR-002`: Pandemic-era migration to private schooling, homeschooling, and micro-schooling contributed to the Fall 2020 decline.
- `H-ENR-003`: Post-2020 regional public cohort contraction reflects declining birth cohort volume across MARC counties.
- `H-ENR-004`: Out-migration and exurban residential shifts contributed to stagnation in mature inner-ring districts.

---

## 8. Relational Architecture & Validation

### 8.1 Upstream & Downstream Relationships
- **Upstream (Inputs):** None (Primary administrative reported item).
- **Downstream (Dependent Measures):**
  - [`EDU-001`](../EDU-001-pupil-teacher-ratio/README.md) (Pupil / Teacher Ratio = `EDU-002` / `EDU-003`).
  - `EDU-008` (Chronic Absenteeism Rate = Severely Absent Students / `EDU-002`).
  - Operating Expenditures Per Pupil (Total Expenditures / `EDU-002`).
- **Conceptual Contrasts:**
  - [`EDU-015`](../../registry/measures.csv) (Average Daily Attendance).
  - [`EDU-016`](../../registry/measures.csv) (State Funding / Weighted Enrollment).

### 8.2 Candidate External Validation Sources
- **State Audited Fall Membership (DESE MCDS / KSDE Data Central):** Reconciles preliminary CCD snapshots against state foundation audit counts.
- **U.S. Census Bureau ACS School-Age Population (Ages 5–17):** Establishes public school "capture rate" (public enrollment divided by total resident school-age population).
- **Civil Rights Data Collection (CRDC) Total Enrollment:** Biennial federal compliance audit providing independent demographic cross-tabulations.

---

## 9. Initial Empirical & Descriptive Sanity Checks

Mandatory checklist executed against KC Metropolitan Universe (SY 2024–25, $N = 691$ schools, $N = 77$ LEAs):

- [x] **Negative Value Sanitization:** Zero negative exception codes (`-1`, `-2`, `-9`) present in processed analysis files.
- [x] **Zero-Membership Verification:** 26 zero-membership operating schools audited and verified against NCES shared-time, CTE, alternative, and special education metadata.
- [x] **Reconciliation Gap Documented:** Verified that LEA enrollment ($330,443$) exceeds campus enrollment ($327,998$) by $+2,445$ students across all 77 districts; major district gaps cataloged in outlier ledger.
- [x] **Grade-Span Isolation:** Pre-K enrollment ($10,603$ students) cleanly isolated in `ENR-NCES-K12-MEMBER`.
- [x] **Longitudinal Continuity Check:** Verified 11-year LEA panel without artificial ID breakages.

---

## 10. Visual Evidence Packet

The Observatory maintains five visual artifacts for `EDU-002`, establishing its institutional distribution, aggregation dynamics, longitudinal history, and national benchmark context:

### Figure 4: Campus Institutional Scale — School Size Distributions by Grade Band
![Figure 4: Campus Institutional Scale](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-education-data-observatory/dashboard/fig04_school_size_distribution.png)
- **Classification:** `DESCRIPTIVE OBSERVATION`
- **Purpose:** Document organizational scale variance across grade levels.
- **Source:** NCES CCD Public School Universe Directory File (SY 2024–25). Excludes 26 zero-membership facilities.
- **Generator Script:** [`analysis/cross-measure/generate_edu002_visuals.py`](../../analysis/cross-measure/generate_edu002_visuals.py)

---

### Figure 5: The LEA–School Membership Reconciliation Gap — Where Are the Students?
![Figure 5: LEA-School Membership Reconciliation Gap](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-education-data-observatory/dashboard/fig05_campus_vs_lea_enrollment_gap.png)
- **Classification:** `DESCRIPTIVE OBSERVATION`
- **Purpose:** Expose the empirical gap between district-level membership and the sum of school building rosters.
- **Source:** NCES CCD LEA Survey vs. School Universe Survey (SY 2024–25).
- **Generator Script:** [`analysis/cross-measure/generate_edu002_visuals.py`](../../analysis/cross-measure/generate_edu002_visuals.py)

---

### Figure 6: 11-Year Regional Enrollment Trajectory — The Fall 2020 Drop & Stagnation
![Figure 6: 11-Year Enrollment Trajectory](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-education-data-observatory/dashboard/fig06_longitudinal_enrollment_trajectory.png)
- **Classification:** `DESCRIPTIVE OBSERVATION`
- **Purpose:** Document regional public school enrollment volume across 77 districts from SY 2014–15 to SY 2024–25.
- **Source:** Audited 11-Year NCES CCD LEA Longitudinal Panel (`kc_lea_capacity_long_2014_15_2024_25.csv`).
- **Generator Script:** [`analysis/cross-measure/generate_edu002_visuals.py`](../../analysis/cross-measure/generate_edu002_visuals.py)

---

### Figure 7: Regional vs. National K–12 Enrollment Trajectories (Indexed to 2014–15 = 100)
![Figure 7: Regional vs National Trajectory](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-education-data-observatory/dashboard/fig07_kc_vs_us_enrollment_trajectory.png)
- **Classification:** `CROSS-SOURCE / BENCHMARK COMPARISON`
- **Purpose:** Benchmark Kansas City regional K–12 enrollment trends against the United States total public K–12 enrollment trajectory.
- **Findings:**
  - Regional and national enrollment track with remarkable alignment: both peaked in SY 2019–20 (KC index 100.7; US index 100.5).
  - In Fall 2020, KC metro enrollment fell by **$-2.21\%$**, mirroring the national drop of **$-2.19\%$**.
  - Post-2020, both regional and national public enrollment have remained below pre-pandemic baselines.
- **Sources:** Kansas City: Audited 11-Year NCES CCD LEA Panel (baseline: 327,699 students). United States: NCES Digest of Education Statistics Table 203.10 (baseline: 48,943,226 students; 2023–25 are NCES projections).
- **Generator Script:** [`analysis/cross-measure/generate_national_enrollment_visuals.py`](../../analysis/cross-measure/generate_national_enrollment_visuals.py)

---

### Figure 8: Kansas City School Size Distributions in National Context
![Figure 8: School Size in National Context](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-education-data-observatory/dashboard/fig08_kc_school_size_national_context.png)
- **Classification:** `BENCHMARK COMPARISON`
- **Purpose:** Position Kansas City campus sizes across elementary, middle, and high school grade bands within the national distribution.
- **Findings:**
  - *Elementary:* KC median (374) sits slightly below the national median (~420); KC elementary schools are heavily concentrated in the 300–499 range ($57.5\%$ vs $39.5\%$ nationally).
  - *Middle:* KC median (584) sits above the national median (~540), with $42.6\%$ of middle schools in the 500–699 range (vs $21.3\%$ nationally).
  - *High School:* KC exhibits substantial right-skew: **$44.8\%$ of KC high schools enroll 1,000+ students** (vs $31.3\%$ nationally), driving student-weighted high school size to $1,289$.
- **Sources:** Kansas City: NCES CCD Public School Universe (SY 2024–25, $N=629$ regular operating campuses with enrollment $>0$). United States: NCES Digest of Education Statistics Table 216.40 (SY 2021–22 regular public schools).
- **Generator Script:** [`analysis/cross-measure/generate_national_enrollment_visuals.py`](../../analysis/cross-measure/generate_national_enrollment_visuals.py)

---

## 11. Observatory Usage & Status

- **Observatory Role:** `Core Census Foundation Measure` (Primary denominator for capacity, staffing, and fiscal metrics).
- **Operational Status:** **AUDITED / FROZEN / READY FOR CROSS-MEASURE USE**.
- **Mandatory Presentation Disclaimer:**
  > *"Student enrollment counts denote registered fall headcount membership as of the snapshot date. They do not equal average daily attendance (which is typically 6% to 10% lower due to absenteeism), nor does the sum of individual school enrollments equal total district enrollment due to unassigned, out-of-district, and central administrative student placements."*
- **Audit History:**
  - `2026-09-26 (Task 003)`: Initial measure audited and codified; reconciliation gap documented; 4-tier universe instantiated; Figures 4–6 generated.
  - `2026-09-26 (Task 003B)`: Semantic cleanup completed: ADA and funding FTE separated into proposed measures `EDU-015` and `EDU-016`; "compulsory" replaced with "grade-span"; 26 zero-membership schools audited into 4-part taxonomy; Missouri SB 727 transition and Kansas funding lookbacks documented; candidate hypotheses formalizing the Fall 2020 drop registered; Figures 7 and 8 added with national benchmarks; measure frozen.
