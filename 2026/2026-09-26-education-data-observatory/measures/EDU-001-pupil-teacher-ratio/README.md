# Measure Dossier: EDU-001 — Pupil / Teacher Ratio (PTR)

> **Observatory Standard:** This dossier represents the calibration specimen for the Education Data Observatory. It consolidates authoritative source definitions, empirical findings, and structural models established across four decades of public data in the Kansas City Education Capacity Study ([`kc_education_capacity`](../../../2026/2026-09-23-kc-education-capacity/README.md)).

---

## 1. Identity & Classification

| Attribute | Specification |
| :--- | :--- |
| **Measure ID** | `EDU-001` |
| **Canonical Name** | Pupil / Teacher Ratio (PTR) |
| **Short Identifier / Slug** | `pupil-teacher-ratio` |
| **Status** | `audited` |
| **Lifecycle Stage** | Epistemic Ladder: `source` $\to$ `field` $\to$ `operationalization` $\to$ `measure` $\to$ `description` $\to$ `validation` $\to$ `relationships` $\to$ `explanation` |
| **Category** | Staffing Capacity |
| **Construct Nature** | Derived Mathematical Construct (Ratio of Enrollment to Teacher FTE) |
| **Associated Operationalizations** | [`PTR-NCES-SCHOOL`](../../registry/operationalizations.csv), [`PTR-NCES-LEA`](../../registry/operationalizations.csv), [`PTR-OBS-K12-ADJUSTED`](../../registry/operationalizations.csv), [`PTR-KSDE-CLASSROOM`](../../registry/operationalizations.csv) |

---

## 2. Definitions & Conceptual Boundaries

### 2.1 Plain-Language Definition
Pupil/Teacher Ratio (PTR) is a macro-level administrative measure of adult staffing density. It measures the total count of enrolled students divided by the full-time equivalent (FTE) count of teachers employed by a school or district.

> [!CAUTION]
> **PTR is NOT Class Size.** A pupil/teacher ratio of 14:1 does **not** mean there are 14 students in a classroom. In secondary schools with 14:1 PTR, typical core academic classrooms regularly contain 24 to 28+ students due to contractual planning periods, specialist role assignments, and course enrollment patterns.

### 2.2 Formal / Statistical Definition
For an educational observation unit $i$ (school campus or district LEA) in school year $t$:

$$\text{PTR}_{i,t} = \frac{E_{i,t}}{T_{i,t}}$$

Where:
- $E_{i,t}$ is student headcount enrollment.
- $T_{i,t}$ is full-time equivalent (FTE) teachers.

### 2.3 Aggregation Rules & Three Distinct Estimands
When examining a collection of schools (e.g., across an LEA, metropolitan region, or state), researchers must choose an estimand based on their specific research question. None of these is inherently "biased"; they answer fundamentally different questions:

$$\begin{aligned}
\text{1. Pooled (Aggregate) PTR:} \quad \overline{\text{PTR}}_{\text{pooled}} &= \frac{\sum_{i=1}^N E_i}{\sum_{i=1}^N T_i} = \sum_{i=1}^N \left(\frac{T_i}{\sum_{j} T_j}\right) \frac{E_i}{T_i} = \sum_{i=1}^N w_i \cdot r_i \\
\text{2. Unweighted Mean School PTR:} \quad \overline{\text{PTR}}_{\text{unweighted}} &= \frac{1}{N}\sum_{i=1}^N \frac{E_i}{T_i} = \frac{1}{N}\sum_{i=1}^N r_i \\
\text{3. Median School PTR:} \quad \text{PTR}_{\text{median}} &= \text{Median}(r_1, r_2, \dots, r_N)
\end{aligned}$$

| Estimand | Mathematical Nature | Research Question Answered | Behavioral Characteristics |
| :--- | :--- | :--- | :--- |
| **Pooled PTR** ($\frac{\sum E}{\sum T}$) | Teacher-FTE-weighted mean of school PTRs ($w_i = \frac{T_i}{\sum T}$) | *What is the macro adult staffing density across the entire combined student and teacher population?* | Dominated by large high schools and suburban campuses; reflects total regional fiscal investment. |
| **Unweighted Mean School PTR** | Simple arithmetic mean across school campuses | *What staffing ratio does the typical public school campus exhibit?* | Gives equal weight to small rural schools, alternative centers, and large comprehensive campuses. Sensitive to small-school tails. |
| **Median School PTR** | 50th percentile of campus distribution | *What does the middle school look like in the institutional distribution?* | Robust to extreme outliers (both small low-PTR specialized day centers and large high-PTR cyber academies). |

---

## 3. Provenance & Operationalization Inventory

The Observatory catalogs multiple distinct operationalizations of `EDU-001` in [`registry/operationalizations.csv`](../../registry/operationalizations.csv):

| Operationalization ID | Implementing Authority | Target Population | Formula / Source Fields | Staff Scope & Completeness |
| :--- | :--- | :--- | :--- | :--- |
| **`PTR-NCES-SCHOOL`** | NCES CCD Non-Fiscal School Universe | All public elementary and secondary schools | $\frac{\text{MEMBER}}{\text{TEACHERS}}$ | **FTE Classroom Teachers.** Excludes librarians, counselors, administrators, and central itinerant staff. |
| **`PTR-NCES-LEA`** | NCES CCD Non-Fiscal LEA Survey | Operating public school districts | $\frac{\sum \text{MEMBER}}{\sum \text{TEACHERS}}$ | **District-Wide Total Teacher FTE.** Includes central-office and itinerant teachers. |
| **`PTR-OBS-K12-ADJUSTED`** | Observatory Research Specification | Regular elementary & secondary schools | $\frac{\text{MEMBER} - \max(0, \text{PK})}{\text{TEACHERS} - \max(0, \text{TEACHERS\_PK})}$ | **K–12 Classroom Staffing.** Deducts Pre-K enrollment and reported Pre-K teachers to avoid early childhood distortion. |
| **`PTR-KSDE-CLASSROOM`** | KSDE KPTEN / CPFS System | Kansas Unified School Districts | $\frac{\text{Headcount}}{\text{FTE Classroom Teachers}}$ | **General Classroom Teachers Only.** Strictly excludes SPED, Title I, and reading specialists. |

---

## 4. Scope, Granularity & Temporal Disambiguation

| Dimension | Specification | Notes & Boundary Conditions |
| :--- | :--- | :--- |
| **Target Population** | Public K–12 students and certified classroom teachers | Grade levels and staff scope depend on operationalization |
| **Unit of Observation** | School campus (`NCESSCH`) or LEA District (`LEAID`) | Must distinguish campus reporting from district reporting |
| **Geographic Granularity** | Campus, LEA, County, Metropolitan Region, State, National | |
| **Temporal Granularity** | Annual Fall Snapshot | Collected on or near October 1 of academic year |
| **School Year of Reference (SY)** | `SY 2024–25` (Anchor Year) | **Primary Indexing Dimension** |
| **Collection Snapshot Date** | October 1 of school year | Universal state fall count date |
| **Publication / Release Date** | Provisional: +12 to 14 months; Final: +20 to 24 months | Public availability date |
| **Earliest Available Year** | SY 1986–87 | Continuous digital non-fiscal records |
| **Latest Audited Year** | SY 2024–25 | Audited in KC Education Capacity Study |
| **Expected Update Cadence** | Annual | |

> [!IMPORTANT]
> **Temporal Disambiguation Standard:** Never use an isolated calendar year (e.g., "2024") without specifying whether it denotes the **School Year of Reference** (`SY 2024–25`) or the **Data Publication Release Year** (`2024`). The Observatory strictly indexes all measures by School Year of Reference.

---

## 5. Universe Definitions & Analytical Subsets

> [!NOTE]
> The Observatory preserves unusual observations rather than deleting them. A cyber charter school with a PTR of 70:1, or a specialized therapeutic center with a PTR of 3:1, is valid empirical data about that organizational form, not "dirty data."

### A. Source Universe
All records present in the raw NCES CCD Public School Universe Directory file (`ccd_sch_029_XX_l_1a.csv`), including regular local public schools, special education schools, vocational/technical schools, alternative schools, charter campuses, and state-operated facilities.

### B. Mathematical Validity Requirements
To compute a mathematically defined ratio:
- $E_{i,t} \ge 0$ and $T_{i,t} > 0$.
- All negative missing/suppression codes (`-1`, `-2`, `-9`) mapped to `NaN`.
- Records where $T_{i,t} = 0$ with $E_{i,t} > 0$ are classified as `validity_failure_zero_denominator` and evaluated for staff non-reporting.

### C. Entity-Type & Anomaly Flags
Records are tagged with descriptive flags to allow researchers to construct customized subsets:
- `flag_virtual`: Virtual / cyber school (`VIRTUAL == 'YES'`).
- `flag_special_ed`: Dedicated special education day facility (`TYPE == 2`).
- `flag_vocational`: Vocational / CTE center (`TYPE == 3`).
- `flag_alternative`: Alternative / disciplinary facility (`TYPE == 4`).
- `flag_low_ratio`: PTR $< 6.0$ (trigger for specialized staffing audit).
- `flag_high_ratio`: PTR $> 35.0$ (trigger for non-reporting or cyber audit).

### D. Recommended Analytic Comparison Universes
1. **Standard Regular Public School Universe:**
   - Operating local regular public schools (`TYPE == 1`, `STATUS in [1, 3, 8]`).
   - Non-zero thresholds: $E \ge 10$ and $T \ge 1.0$.
   - Flagged outliers retained and reported in distributional tables.
2. **Comprehensive Secondary Academic Universe:**
   - Regular high schools offering standard grades 9–12 core academic coursework.
3. **Alternative & Specialized Facility Universe:**
   - Distinct panel evaluating non-traditional delivery models without contaminating regular school distributions.

---

## 6. Staff Semantics & Organizational Sensitivity

### 6.1 Authoritative NCES Teacher Semantics
Authoritative NCES documentation specifies:
- In the **CCD Public School Universe**, the reported teacher field represents **Full-Time Equivalent (FTE) Classroom Teachers**.
- It does **not** include guidance counselors, librarians, instructional coordinators, school principals, or paraprofessionals.
- **Why the "Specialist Wedge" Still Occurs:** In federal CCD reporting, states categorize certified reading specialists, special education resource teachers, and pull-out interventionists under "classroom teachers" if they hold teaching certificates, even when they do not manage general classroom rosters. In Kansas, state data systems (`KPTEN`) disaggregate classroom teachers from specialized teachers; in federal data, they remain pooled.

### 6.2 Organizational Allocation Sensitivity (Campus vs. Central Office)
- In many LEAs, itinerant specialists (elementary art, music, physical education, speech) are assigned to the district central office (`LEAID`) rather than individual school building rosters (`NCESSCH`).
- This produces the **Central Allocation Gap**:
  $$\Delta_{\text{central}} = \text{PTR}_{\text{campus\_aggregate}} - \text{PTR}_{\text{district\_direct}}$$
- In metropolitan Kansas City, large suburban districts show $\Delta_{\text{central}} \in [0.8, 2.2]$ students/FTE. Analysts comparing individual schools across districts must account for whether itinerant staff are held centrally or distributed to buildings.

---

## 7. Semantic Auditing: The Epistemic Defense

### 7.1 What Question Does PTR Legitimately Answer?
1. **Systemic Adult Staffing Density:** How many certified instructional teachers does an educational system employ relative to its student body?
2. **Longitudinal Resource Allocation Trends:** Did a district or region actively expand teaching payroll over a decade, independent of student enrollment growth?
3. **Macro Fiscal Capacity Baseline:** What is the macro staffing burden carried by the operating fund?

### 7.2 What Question Does PTR NOT Answer?
1. **Classroom Congestion / Roster Size:** It does **not** reveal how many students are sitting in 3rd period Geometry.
2. **Teacher Daily Workload / Contact Load:** It does **not** indicate how many unique student papers, grades, and parent communications a secondary teacher manages daily.
3. **Student Peer Exposure:** It does **not** reflect the classroom environment experienced by an average child during instructional time.

### 7.3 Calibrated Empirical Decomposition (Kansas City Secondary Model)
In the Kansas City Education Capacity Study, empirical microdata across 6 waves of CRDC course records and state personnel registers revealed the multi-stage structural bridge between macro PTR and secondary core class sizes:

$$\text{Observed Core Section Size} \approx \text{PTR}_{\text{macro}} + \Delta_1 + \Delta_2 + \Delta_3$$

- **Wedge $\Delta_1$ (Specialist Denominator Wedge $\approx +2.7$):** Accounting for certified specialists who do not head general rosters.
- **Wedge $\Delta_2$ (Schedule Planning Multiplier $\phi \approx +5.7$ to $+8.0$):** Contractually protected teacher planning time requires $\phi = \frac{P_{\text{student}}}{P_{\text{teacher}}}$. Under a standard "5 of 7" secondary teaching regime ($\phi = 1.400$), only $5/7$ of teachers are in front of students at any bell.
- **Wedge $\Delta_3$ (Curricular Allocation Residual $\approx -1.5$ to $+5.0$):** High school course catalogs distribute seats heterogeneously; low-enrollment advanced and specialized electives force core gateway sections (Algebra I, Biology) to expand.

---

## 8. Relational Architecture & Validation

### 8.1 Upstream & Downstream Relationships
- **Derived From (Inputs):** `EDU-002` (Student Enrollment) and `EDU-003` (Reported Classroom Teacher FTE).
- **Contrasts With:** `EDU-004` (Classroom Teacher FTE - KSDE audited), `EDU-006` (School-Course Class Size - CRDC), `EDU-007` (Survey Class Size - NTPS).

### 8.2 Candidate External Validation Sources
- **NCES NTPS / SASS Public School Teacher Questionnaire:** Nationally and state-representative self-reported class size.
- **OCR Civil Rights Data Collection (CRDC):** Course-level enrollment and class counts.
- **State Personnel Registries (KSDE KPTEN / MO DESE MOSIS):** Administrative microdata with distinct job codes.
- **Historical Judicial Records (*Jenkins v. Missouri*):** Federal court desegregation daily contact load audits.

---

## 9. Historical & Institutional Context

Between 2014–15 and 2024–25 in the Kansas City metropolitan area, K–12 enrollment was flat ($-0.73\%$), while teacher FTE expanded $+8.88\%$, driving regional PTR down from $14.85:1$ to $13.54:1$. Yet classroom teachers reported no relief in class sizes.

The institutional explanation: Districts utilized staff additions to reduce secondary teaching loads from "6 of 7" periods to "5 of 7" periods (e.g., Shawnee Mission Board of Education, January 2020). Shifting from $6/7$ to $5/7$ structurally demands a **$+20\%$ staffing increase** just to maintain constant class sizes. Districts hired teachers to buy back teacher planning and grading time, not to shrink class rosters.

---

## 10. Initial Empirical & Descriptive Sanity Checks

- [ ] **Sanitization Assertion:** All negative codes (`-1`, `-2`, `-9`) mapped to `NaN`. Zero negative values allowed.
- [ ] **Denominator Assertion:** Filter $T > 0$; tag zero-denominator records for staff non-reporting audit.
- [ ] **Outlier Triage:** Flag PTR $< 6.0$ and PTR $> 35.0$ for institutional audit (preserve observations).
- [ ] **Estimand Verification:** Report both Pooled PTR and Median School PTR when summarizing districts.
- [ ] **Longitudinal Jump Detection:** Flag entities exhibiting annual step-changes $> \pm 25\%$ without verified boundary changes.

---

## 11. Visual Evidence Packet

The Observatory maintains three visual artifacts for `EDU-001`, documenting their provenance and analytical classifications:

### Figure 1: Illustrative Cross-Source Comparison — Macro PTR vs. Secondary Classroom Reality
- **Classification:** `CROSS-SOURCE COMPARISON`
- **Purpose:** Illustrate that administrative staffing ratios (CCD) systematically sit 6 to 14 students below secondary classroom class sizes across multiple jurisdictions.
- **Provenance by Bar:**
  1. *United States (National):* Macro PTR = **15.4:1** (NCES Digest of Education Statistics 2022, Table 208.20, SY 2020–21; note that national totals are suppressed in preliminary 2024–25 CCD Table 2). Secondary Departmentalized Class Size = **23.3** (NCES NTPS 2017–18 Table A-7a; 2020–21 NTPS published at 21.0).
  2. *Missouri (Statewide):* Macro PTR = **13.8:1** (CCD SY 2020–21). High School Class Size = **22.5** (NTPS 2017–18 Table A-7a).
  3. *Kansas (Statewide):* Macro PTR = **13.6:1** (CCD SY 2020–21). High School Class Size = **19.8** (NTPS 2017–18 Table A-7a).
  4. *Shawnee Mission North HS (KC Suburb):* Macro PTR = **14.2:1** (CCD SY 2021–22). Algebra I Mean Class Size = **25.7** (CRDC SY 2021–22 course enrollment / classes).
  5. *Lincoln College Prep (KCPS Urban Core):* Macro PTR = **17.3:1** (CCD SY 2021–22). Geometry Mean Class Size = **31.0** (CRDC SY 2021–22 course enrollment / classes).
- **Caveat:** Bars represent asynchronous reference periods and distinct estimands; they are intentionally juxtaposed to demonstrate that the macro-to-classroom gap is a systemic property of secondary schooling rather than a local data error.
- **Generator Script:** [`analysis/cross-measure/generate_observatory_visuals.py`](../../analysis/cross-measure/generate_observatory_visuals.py)

### Figure 2: The Kansas City 10-Year Capacity Paradox (SY 2014–15 to SY 2024–25)
- **Classification:** `DESCRIPTIVE OBSERVATION`
- **Purpose:** Document the longitudinal divergence between flat student enrollment ($-0.73\%$, $-2,345$ students) and expanding instructional staffing ($+8.88\%$ teachers, $+11.85\%$ paraprofessionals), which drove regional pooled PTR down from $14.85:1$ to $13.54:1$.
- **Population:** 77 public school districts in the 9-county Mid-America Regional Council (MARC) region.
- **Source:** Audited NCES CCD LEA Longitudinal Panel (`kc_lea_capacity_long_2014_15_2024_25.csv`).
- **Generator Script:** [`analysis/cross-measure/generate_observatory_visuals.py`](../../analysis/cross-measure/generate_observatory_visuals.py)

### Figure 3: Multi-Stage Waterfall Decomposition (Shawnee Mission North Case)
- **Classification:** `MODEL / CALIBRATED CASE STUDY`
- **Purpose:** Demonstrate how the Schedule Capacity Identity ($\phi = 1.400$), Specialist Wedge ($\Delta_1$), and Curricular Hierarchy Residual ($\Delta_3$) bridge the $11.5$-student gap between a $14.19:1$ macro PTR and an observed $25.71$ Algebra I class size.
- **Status:** Empirical calibration model, not a raw descriptive census.
- **Generator Script:** [`analysis/cross-measure/generate_observatory_visuals.py`](../../analysis/cross-measure/generate_observatory_visuals.py)

---

## 12. Observatory Usage & Status

- **Observatory Role:** `Contextual Background Metric` (Systemic Investment Layer).
- **Prohibited Use:** Prohibited as a standalone measure of student classroom exposure, class size, or teacher workload.
- **Mandatory Presentation Disclaimer:**
  > *"Pupil/Teacher Ratio measures total system adult staffing density. It does not reflect individual classroom class sizes, which in secondary schools are typically 40% to 80% higher due to planning schedules, specialist roles, and course enrollment patterns."*
- **Dossier Audit History:**
  - `2026-09-26`: Initial calibration dossier drafted.
  - `2026-09-26 (Task 002B)`: Audited against authoritative NCES documentation; aggregation semantics corrected to Pooled PTR; four-tier universe implemented; visual evidence provenance codified.
