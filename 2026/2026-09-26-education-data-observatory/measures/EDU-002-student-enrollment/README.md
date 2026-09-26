# Measure Dossier: EDU-002 — Student Headcount Enrollment

> **Observatory Standard:** Student enrollment is the foundational denominator of public education finance and capacity analysis. Yet in administrative data systems, "how many students there are" is not a single unambiguous quantity. This dossier audits the multi-layered semantics of enrollment: the **Central Aggregation Discrepancy** (why LEA enrollment does not equal the sum of school enrollments), the **Pre-K Inclusion Wedge**, the existence of **26 operational zero-enrollment campuses**, and the post-2020 **Pandemic Enrollment Cliff**.
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
| **Status** | `audited` |
| **Lifecycle Stage** | Epistemic Ladder: `source` $\to$ `field` $\to$ `operationalization` $\to$ `measure` $\to$ `description` $\to$ `validation` $\to$ `relationships` $\to$ `explanation` |
| **Category** | Enrollment & Demographics |
| **Construct Nature** | Directly Reported Administrative Census Item (Fall Snapshot Headcount or Cumulative Attendance) |
| **Associated Operationalizations** | [`ENR-NCES-FALL-MEMBER-SCH`](../../registry/operationalizations.csv), [`ENR-NCES-FALL-MEMBER-LEA`](../../registry/operationalizations.csv), [`ENR-NCES-K12-MEMBER`](../../registry/operationalizations.csv), [`ENR-MO-DESE-ADA`](../../registry/operationalizations.csv), [`ENR-KSDE-FTE`](../../registry/operationalizations.csv) |

---

## 2. Definitions & Conceptual Boundaries

### 2.1 Plain-Language Definition
Student Headcount Enrollment is the official count of individual pupils registered on the active membership rolls of a public school campus or local education agency (district) on a designated census date (traditionally on or near October 1 of each school year).

> [!CAUTION]
> **Enrollment is Neither Attendance Nor Pure Physical Campus Attendance.** 
> 1. An enrolled student is not necessarily present in the building every day; illness and chronic absenteeism create a 6% to 10% wedge between **Membership** and state-funded **Average Daily Attendance (ADA)**.
> 2. Summing school-level enrollments does **not** equal district-level enrollment. In the Kansas City metro area alone, LEA memberships exceed the sum of school rosters by **+2,445 students (+0.74%)** due to out-of-district day placements, regional cooperatives, and central administrative rosters.

### 2.2 Formal / Statistical Definition
For an educational entity $i$ (school campus $s$ or local education agency $d$) in school year $t$:

$$E_{i,t} = \sum_{j \in \mathcal{P}_t} \mathbb{I}\Big(\text{Pupil } j \text{ is actively enrolled in entity } i \text{ as of census date } \tau_t\Big)$$

Where:
- $\mathcal{P}_t$ is the population of all school-aged children residing within or admitted to the jurisdiction in year $t$.
- $\mathbb{I}(\cdot)$ is an indicator function returning 1 if pupil $j$ satisfies state statutory residency, admission, and non-withdrawal criteria on census date $\tau_t$ (e.g., October 1).
- In headcount accounting, each child is unduplicated within a primary jurisdiction ($E_{i,t} \in \mathbb{N}_0$).

### 2.3 Aggregation Rules & Three Distinct Estimands
When aggregating or summarizing enrollment across a collection of schools (e.g., across a metropolitan region, district, or state), researchers must distinguish between three distinct estimands answering different questions:

$$\begin{aligned}
\text{1. Total Regional / System Scale (Sum):} \quad E_{\text{total}} &= \sum_{i=1}^N E_i \\
\text{2. Unweighted Campus Mean:} \quad \overline{E}_{\text{unweighted}} &= \frac{1}{N}\sum_{i=1}^N E_i \\
\text{3. Median Campus Size & IQR:} \quad E_{\text{median}} &= \text{Median}(E_1, E_2, \dots, E_N) \\
\text{4. Student-Weighted Campus Exposure:} \quad \overline{E}_{\text{student-weighted}} &= \sum_{i=1}^N \left(\frac{E_i}{E_{\text{total}}}\right) E_i = \frac{\sum_{i=1}^N E_i^2}{\sum_{i=1}^N E_i}
\end{aligned}$$

| Estimand | Mathematical Nature | Research Question Answered | Kansas City Metro Benchmark (SY 2024–25) |
| :--- | :--- | :--- | :--- |
| **Total Regional Enrollment** ($\sum E_i$) | Simple sum across all entities | *How many total public school students are being educated across the regional jurisdiction?* | **327,998 students** (Campus Headcount sum) / **330,443 students** (LEA Member sum) |
| **Median Campus Size** | 50th percentile of campus distribution | *What is the size of the middle/typical school facility, robust to extreme outliers?* | Elementary: **374** \| Middle: **584** \| High: **843** |
| **Unweighted Campus Mean** | Arithmetic mean of school enrollments | *What is the average administrative size of a school building plant?* | Elementary: **390** \| Middle: **559** \| High: **905** |
| **Student-Weighted Campus Exposure** | Student-weighted mean of school size ($\frac{\sum E^2}{\sum E}$) | *What size campus does the average child actually experience every day?* | Elementary: **428** \| Middle: **643** \| High: **1,289** |

> [!NOTE]
> **The High School Scale Skew:** Notice that while the median Kansas City high school enrolls 843 students, the **student-weighted high school size is 1,289 students**. Because mega-campuses like Blue Springs High (2,429 students) and Liberty North High (2,262 students) hold so many students, the typical teenager attends a high school substantially larger than the median high school building in the directory.

### 2.4 Unit & Scale
- **Unit of Measurement:** `students` (discrete integer headcount).
- **Theoretical Range:** $[0, \infty)$.
- **Empirical Realistic Range:**
  - Individual regular campuses: 20 to ~3,000 students.
  - Kansas City Metro Range (SY 2024–25): Elementary (26 to 1,496); Middle (68 to 1,055); High (10 to 2,429).
  - Operating Zero-Enrollment Campuses: 26 schools in the KC metro report exactly $E = 0$ (shared-time vocational/technical institutes).

---

## 3. Provenance & Operationalization Inventory

The Observatory catalogs five distinct operationalizations of `EDU-002` in [`registry/operationalizations.csv`](../../registry/operationalizations.csv):

| Operationalization ID | Implementing Authority | Target Population | Formula / Source Fields | Provenance Tier |
| :--- | :--- | :--- | :--- | :--- |
| **`ENR-NCES-FALL-MEMBER-SCH`** | NCES CCD Non-Fiscal School Universe | All public elementary and secondary schools | `MEMBER` | **Tier 1 National Administrative Census.** Fall snapshot headcount across all grades offered (Pre-K to 12). |
| **`ENR-NCES-FALL-MEMBER-LEA`** | NCES CCD Non-Fiscal LEA Survey | Operating local public school districts | `MEMBER` | **Tier 1 National Administrative Census.** Total LEA membership. Includes centralized, homebound, and out-of-district day placements. |
| **`ENR-NCES-K12-MEMBER`** | Observatory Research Specification | Regular public elementary and secondary schools | $\text{MEMBER} - \max(0, \text{PK})$ | **Tier 1 Research-Derived Adjusted.** Deducts Pre-K enrollment to isolate mandatory schooling grades K–12. |
| **`ENR-MO-DESE-ADA`** | Missouri DESE School Finance Portal | Missouri public school districts and charters | $\frac{\text{TOTAL\_ATTENDANCE\_HOURS}}{\text{CALENDAR\_HOURS}}$ | **Tier 2 State Administrative Foundation.** Average Daily Attendance determining state foundation aid. |
| **`ENR-KSDE-FTE`** | Kansas State Department of Education | Kansas Unified School Districts (USDs) | Audited FTE (Headcount adjusted for part-time/PK/half-day K) | **Tier 2 State Administrative Foundation.** Audited September 20 full-time equivalent student enrollment. |

---

## 4. Scope, Granularity & Temporal Disambiguation

| Dimension | Specification | Notes & Boundary Conditions |
| :--- | :--- | :--- |
| **Target Population** | Public elementary and secondary pupils | Includes Pre-K if operated by public LEA |
| **Unit of Observation** | School Campus (`NCESSCH`) or LEA District (`LEAID`) | Must distinguish campus rosters from LEA membership rolls |
| **Geographic Granularity** | Campus, LEA, County, Metropolitan Region, State, National | Aggregation must account for the Central Discrepancy |
| **Temporal Granularity** | Annual Fall Snapshot vs. Cumulative Academic Year | NCES CCD is fall snapshot; state ADA is cumulative annual |
| **School Year of Reference (SY)** | `SY 2024–25` (Anchor Year) | **Primary Indexing Dimension** |
| **Collection Snapshot Date** | On or near October 1 (MO) / September 20 (KS) | Standardized state census dates |
| **Publication / Release Date** | Provisional: +12 to 14 months; Final: +20 to 24 months | Public CCD release lag |
| **Earliest Available Year** | SY 1986–87 | Continuous digital CCD records |
| **Latest Audited Year** | SY 2024–25 | Audited in KC Education Capacity Study |
| **Expected Update Cadence** | Annual | |

> [!IMPORTANT]
> **Temporal Disambiguation Standard:** In all Observatory reports, enrollment is indexed by **School Year of Reference** (`SY 2024–25`), never by ambiguous single calendar years.

---

## 5. Universe Definitions & Analytical Subsets (The 4-Tier Universe)

The Observatory preserves unusual educational entities rather than deleting them. A shared-time technical center or a specialized day school is valid empirical data about an institutional model, not "dirty data."

### A. Source Universe
All records reported in the NCES CCD Public School Universe Directory (`ccd_sch_029_XX_l_1a.csv`). In the 9-county KC metro area (SY 2024–25), this comprises **691 operating public schools** across **77 operating LEAs**.

### B. Mathematical Validity Requirements
- $E_{i,t} \ge 0$.
- All negative missing/suppression codes (`-1` Missing, `-2` Not Applicable, `-9` Suppressed) recoded to `NaN`.
- Records where $E_{i,t} = 0$ are preserved and evaluated under the zero-membership taxonomy.

### C. Entity-Type & Anomaly Flags
- `flag_zero_membership`: Operating school with $E = 0$ (26 vocational/CTE centers in KC metro).
- `flag_prek_only`: Dedicated Early Childhood Center enrolling exclusively Pre-K ($100\%$ PK, 18–20 campuses in KC).
- `flag_virtual`: Virtual / cyber school (e.g., MO Virtual Instruction Program).
- `flag_unassigned_gap`: LEA where district enrollment exceeds campus sum by $> 2.0\%$ (e.g., Hickman Mills C-1 at $+11.7\%$).

### D. Recommended Analytic Comparison Universes
1. **Standard K–12 Comprehensive Campus Universe:**
   - Operating local regular public schools (`TYPE == 1`, `STATUS in [1, 3, 8]`).
   - Enrollment threshold: $E \ge 10$.
   - Dedicated Pre-K centers and zero-enrollment CTE campuses tracked in separate panels.
2. **K–12 Compulsory Membership Universe:**
   - Operationalization: `ENR-NCES-K12-MEMBER` ($E_{\text{K12}} = \text{MEMBER} - \text{PK}$).
   - Ensures cross-district comparability by eliminating voluntary early childhood variation.
3. **Specialized & Vocational Technical Universe:**
   - Dedicated monitoring of regional trade and career centers operating on shared-time enrollment models.

---

## 6. Known Source Distortions & The Central Discrepancy

### 6.1 The Central Aggregation Discrepancy ($\text{Enrollment}_{\text{LEA}} \neq \sum \text{Enrollment}_{\text{campus}}$)
A widespread methodological trap in education research is assuming that a school district's total enrollment is equal to the sum of its school building rosters.

In empirical reality, **LEA membership systematically exceeds the sum of campus enrollments**:
$$\Delta_{\text{unassigned}} = E_{\text{LEA}} - \sum_{s \in \text{LEA}} E_s$$

In the 9-county Kansas City metro area in SY 2024–25:
- Total LEA-reported enrollment: **330,443 students**.
- Sum of school-reported enrollments: **327,998 students**.
- Regional Discrepancy: **$+2,445$ unassigned students (+0.74%)**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE CENTRAL AGGREGATION DISCREPANCY                  │
│                                                                        │
│   LEA Official Membership: 330,443 Students                            │
│   ├── Physical Campus Sum: 327,998 Students (99.26%)                   │
│   └── Central / Unassigned:  2,445 Students  (0.74%)                   │
│       ├── Out-of-District Private/Public Specialized Day Placements    │
│       ├── Homebound & Hospital Instructional Programs                  │
│       ├── Regional Multi-District Vocational Cooperatives              │
│       └── Central Office Administrative Holding Accounts               │
└────────────────────────────────────────────────────────────────────────┘
```

#### Empirical Distribution Across KC Districts (SY 2024–25):
- **Hickman Mills C-1 (MO):** LEA reports 5,082 students; campus sum is 4,487. **$+595$ unassigned students (11.7% of district)**.
- **Missouri Schools for the Severely Disabled (MO):** LEA reports 652 students; single physical campus reports 96. **$+556$ unassigned students (85.3% of district)**.
- **Missouri Division of Youth Services (MO):** LEA reports 496 students; single school reports 79. **$+417$ unassigned students (84.1% of district)**.
- **De Soto USD 232 (KS):** LEA reports 7,370 students; campus sum is 7,142. **$+228$ unassigned students (3.1% of district)**.
- **Shawnee Mission USD 512 (KS):** LEA reports 26,050 students; campus sum is 25,867. **$+183$ unassigned students (0.7% of district)**.
- **Lee's Summit R-VII (MO):** LEA reports 17,910 students; campus sum is 17,735. **$+175$ unassigned students (1.0% of district)**.

> [!WARNING]
> **Methodological Consequence:** An analyst who calculates per-pupil expenditures or district-wide staffing ratios by summing school files will systematically underestimate the student population and inflate per-pupil funding.

---

### 6.2 The Pre-K Inclusion Wedge
In the Kansas City metropolitan area (SY 2024–25):
- **10,603 Pre-K students** are enrolled in public school systems, representing **$3.22\%$ of total regional enrollment**.
- **200 out of 691 operating schools ($28.9\%$)** host Pre-K programs.
- **18 to 20 campuses are dedicated Early Childhood Centers** with $100\%$ Pre-K enrollment (e.g., Grace Early Childhood Center in Grandview with 228 Pre-K students; Shull Early Learning Center in Raymore-Peculiar with 189 Pre-K students).

Because Pre-K is non-compulsory and funded heterogeneously across states and districts (often mixed with federal Head Start or local tax levies), including Pre-K in elementary enrollment distorts comparisons of standard K–5 instructional load. The Observatory recommends utilizing `ENR-NCES-K12-MEMBER` when evaluating compulsory educational capacity.

---

### 6.3 Operating Campuses with Zero Primary Enrollment (The Shared-Time CTE Center)
In SY 2024–25, **26 operating public schools** in the Kansas City metro report `enrollment_total == 0`.

These are not abandoned or shuttered facilities. They are **Career and Technical Education (CTE) centers** and specialized vocational institutes (e.g., *Cass Career Center*, *Excelsior Springs Area Career Center*, *Fort Osage Career & Technology Center*). 

- **The Accounting Mechanism:** State reporting standards dictate that high school students attending half-day trade programs remain enrolled in their "home" comprehensive high school for primary membership.
- **The Analytical Hazard:** These campuses report full-time equivalent teachers and capital facilities, but 0 primary students. Any uncritical script computing $\frac{E}{T}$ produces $0.0:1$, distorting both campus PTR distributions and facility utilization metrics unless flagged by `flag_zero_membership`.

---

## 7. Semantic Auditing: Legitimate vs. Illegitimate Inferences

### 7.1 What Question Does Student Enrollment Legitimately Answer?
1. **Institutional & Jurisdictional Scale:** How many children are formally registered in the care and custody of a public school system?
2. **Demographic & Grade-Span Cohort Sizing:** What is the incoming Kindergarten cohort size relative to the graduating 12th-grade class?
3. **Macro Facility Plant Utilization:** How many students are housed within a physical building relative to its architectural design capacity?

### 7.2 What Question Does Student Enrollment NOT Answer?
1. **Daily Classroom Attendance / Seat Fill Rate:** Enrollment does **not** reflect how many students show up on an average Tuesday. In high-poverty secondary schools, a chronic absenteeism rate of $35\%$ means that an enrolled course section of 28 students regularly sees only 18 to 20 students physically present.
2. **State Funding Formula Allocation:** State foundation aid in Missouri is driven by **Average Daily Attendance (ADA)**, not fall enrollment. A district experiencing enrollment growth with declining attendance will suffer state aid reductions.
3. **Instructional Class Size:** Reporting 1,200 students in a high school reveals nothing about whether classes are staffed at 18 or 32 students per room.

---

## 8. Relational Architecture & Validation

### 8.1 Upstream & Downstream Relationships
- **Upstream (Inputs):** None (Primary administrative reported item).
- **Downstream (Dependent Measures):**
  - [`EDU-001`](../EDU-001-pupil-teacher-ratio/README.md) (Pupil / Teacher Ratio = `EDU-002` / `EDU-003`).
  - `EDU-008` (Chronic Absenteeism Rate = Severely Absent Students / `EDU-002`).
  - District Per-Pupil Operating Expenditures (Current Expenditures / `EDU-002`).

### 8.2 Candidate External Validation Sources
- **State Audited Fall Membership (DESE MCDS / KSDE Data Central):** Reconciles preliminary CCD snapshots against state foundation audit counts.
- **U.S. Census Bureau ACS School-Age Population (Ages 5–17):** Establishes public school "capture rate" (public enrollment divided by total resident school-age population).
- **Civil Rights Data Collection (CRDC) Total Enrollment:** Biennial federal compliance audit providing independent demographic cross-tabulations.

---

## 9. Historical & Institutional Context: The Post-2020 Pandemic Cliff

Across the 77 public school districts of the Kansas City metropolitan area, K–12 enrollment followed a distinct 11-year trajectory (SY 2014–15 to SY 2024–25):

```
Year        K-12 Enrollment     Annual Change      Notes
---------------------------------------------------------------------------------
2014-15     327,699             --                 Baseline
2015-16     325,483             -2,216 (-0.68%)    Minor demographic dip
2016-17     326,762             +1,279 (+0.39%)    Steady suburban growth
2017-18     329,013             +2,251 (+0.69%)    Suburban expansion
2018-19     330,064             +1,051 (+0.32%)    Suburban expansion
2019-20     330,128             +64    (+0.02%)    PRE-PANDEMIC PEAK
2020-21     322,818             -7,310 (-2.21%)    COVID-19 CLIFF
2021-22     321,304             -1,514 (-0.47%)    Post-lockdown stabilization
2022-23     322,785             +1,481 (+0.46%)    Partial recovery
2023-24     320,830             -1,955 (-0.61%)    Declining birth cohorts
2024-25     320,031             -799   (-0.25%)    -3.06% from 2019-20 Peak
```

### The Institutional Reality of the Cliff
1. **The Single-Year Plunge:** In the fall of 2020, regional enrollment fell by **$-7,310$ students ($-2.21\%$)**, driven by deferred kindergarten entry, expansion of home-schooling pods, and shifts toward non-traditional learning.
2. **The Stagnation Trap:** Unlike prior recessions, public enrollment did not rebound. By SY 2024–25, enrollment sits at **320,031 students**, representing an ongoing deficit of **$-10,097$ students ($-3.06\%$)** relative to the 2019–20 peak.
3. **The Staffing Paradox Connection:** While regional K–12 enrollment dropped by $-3\%$, total teacher FTE grew $+8.88\%$, directly depressing macro pupil/teacher ratios (`EDU-001`) even as districts face structural operating deficits from falling state attendance aid.

---

## 10. Initial Empirical & Descriptive Sanity Checks

Mandatory checklist executed against KC Metropolitan Universe (SY 2024–25, $N = 691$ schools, $N = 77$ LEAs):

- [x] **Range & Extremes Audit:** School enrollment spans 0 to 2,429. Zero-enrollment schools audited and classified as shared-time CTE centers.
- [x] **Negative Value Sanitization:** Zero negative exception codes (`-1`, `-2`, `-9`) present in processed analysis files.
- [x] **The Central Discrepancy Reconciliation:** Verified that LEA enrollment ($330,443$) exceeds campus enrollment ($327,998$) by $+2,445$ students across all 77 districts.
- [x] **Pre-K Isolation Verification:** Verified that $10,603$ Pre-K students are isolated in `ENR-NCES-K12-MEMBER` to avoid inflating regular K–12 instructional counts.
- [x] **Longitudinal Continuity Check:** Verified 11-year LEA panel without artificial ID breakages.

---

## 11. Visual Evidence Packet

The Observatory maintains three visual artifacts for `EDU-002`, establishing its institutional distribution, aggregation dynamics, and longitudinal history:

### Figure 4: Campus Institutional Scale — School Size Distributions by Grade Band
![Figure 4: Campus Institutional Scale](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-education-data-observatory/dashboard/fig04_school_size_distribution.png)

- **Classification:** `DESCRIPTIVE OBSERVATION`
- **Purpose:** Document the radical difference in organizational scale across grade levels.
- **Findings:**
  - Elementary campuses ($N=393$) are compactly distributed with median enrollment of **374** (IQR: 305 to 473; mean: 390).
  - Middle schools ($N=122$) step up to a median of **584** (IQR: 409 to 688; mean: 559).
  - High schools ($N=114$) exhibit extreme variance and right-skew, spanning from small rural/alternative centers ($<150$) to massive suburban campuses (Blue Springs: 2,429; Blue Springs South: 2,299; Liberty North: 2,262). Median is **843**, mean is **905**, and student-weighted mean is **1,289**.
  - Dedicated Pre-K centers ($N=18$) form an isolated low-enrollment cluster (median: 132, mean: 151).
- **Source:** NCES CCD Public School Universe Directory File (SY 2024–25). Excludes 26 zero-membership CTE centers.
- **Generator Script:** [`analysis/cross-measure/generate_edu002_visuals.py`](../../analysis/cross-measure/generate_edu002_visuals.py)

---

### Figure 5: The Central Aggregation Discrepancy — Where Are the Students?
![Figure 5: Central Aggregation Discrepancy](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-education-data-observatory/dashboard/fig05_campus_vs_lea_enrollment_gap.png)

- **Classification:** `DESCRIPTIVE OBSERVATION`
- **Purpose:** Expose the empirical gap between district-level membership and the sum of school building rosters.
- **Findings:**
  - Shows the top 8 districts where LEA membership exceeds campus rosters.
  - Hickman Mills C-1 accounts for $+595$ unassigned students ($11.7\%$ of district).
  - Specialized state agencies (MO Schools for Severely Disabled and Division of Youth Services) hold $>84\%$ of their students centrally rather than in individual building rosters.
  - Large suburban districts like De Soto ($+228$), Shawnee Mission ($+183$), and Lee's Summit ($+175$) maintain significant cohorts in out-of-district specialized day programs or homebound placements.
- **Source:** NCES CCD LEA Survey vs. School Universe Survey (SY 2024–25).
- **Generator Script:** [`analysis/cross-measure/generate_edu002_visuals.py`](../../analysis/cross-measure/generate_edu002_visuals.py)

---

### Figure 6: 11-Year Regional Enrollment Trajectory — The Pandemic Cliff & Stagnation
![Figure 6: 11-Year Enrollment Trajectory](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-education-data-observatory/dashboard/fig06_longitudinal_enrollment_trajectory.png)

- **Classification:** `DESCRIPTIVE OBSERVATION`
- **Purpose:** Document the macro demographic volume of public education across the Kansas City metropolitan region from SY 2014–15 through SY 2024–25.
- **Findings:**
  - Regional K–12 enrollment grew steadily through the late 2010s, reaching a peak of **330,128 students in SY 2019–20**.
  - With the onset of the pandemic in SY 2020–21, enrollment plunged by **$-7,310$ students ($-2.2\%$)** in a single year.
  - Five years post-pandemic, regional enrollment has failed to rebound, stagnating around **~320,000 students** ($-3.06\%$ below peak).
- **Source:** Audited 11-Year NCES CCD LEA Longitudinal Panel (`kc_lea_capacity_long_2014_15_2024_25.csv`).
- **Generator Script:** [`analysis/cross-measure/generate_edu002_visuals.py`](../../analysis/cross-measure/generate_edu002_visuals.py)

---

## 12. Observatory Usage & Status

- **Observatory Role:** `Core Census Foundation Measure` (Denominator for capacity, staffing, and fiscal metrics).
- **Mandatory Presentation Disclaimer:**
  > *"Student enrollment counts denote registered fall membership as of October 1. They do not equal average daily attendance (which is typically 6% to 10% lower due to absenteeism), nor does the sum of individual school enrollments equal total district enrollment due to centrally assigned and out-of-district student placements."*
- **Audit History:**
  - `2026-09-26`: Initial measure audited and codified; Central Aggregation Discrepancy documented; 4-tier universe instantiated; visual packet Figures 4, 5, and 6 published.
