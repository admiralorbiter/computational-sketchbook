# Measure Dossier Template

> **Observatory Standard:** Every measure in the Education Data Observatory must maintain a complete dossier prior to empirical correlation, indexing, or dashboard presentation. The durable research unit is the **measure**, not the analysis or the raw file.
> 
> *Rule of thumb: Complete measurement semantics before modeling. Description before explanation.*

---

## 1. Identity & Classification

| Attribute | Specification |
| :--- | :--- |
| **Measure ID** | `EDU-XXX` (e.g., `EDU-001`) |
| **Human-Readable Name** | Clear, standard descriptive name |
| **Short Identifier / Slug** | `lowercase-hyphenated-slug` |
| **Status** | `proposed` \| `audited` \| `validated` \| `deprecated` |
| **Lifecycle Stage** | Epistemic Ladder Stage: `source` $\to$ `measurement` $\to$ `description` $\to$ `validation` $\to$ `relationships` $\to$ `explanation` |
| **Category** | Staffing Capacity \| Enrollment & Demographics \| Student Need & Complexity \| Coursework & Curricular Load \| Fiscal |
| **Derived or Directly Reported** | `Directly Reported` (raw administrative item) \| `Derived` (arithmetic calculation) |
| **Provenance Tier** | `Tier 1: Harmonized National Census` (e.g., NCES CCD)<br/>`Tier 2: State-Specific Disaggregated Administrative System` (e.g., KSDE KPTEN, MO DESE MOSIS)<br/>`Tier 3: Local Administrative / Master Schedule Microdata` (e.g., District SIS, CRDC course sections)<br/>`Tier 4: Sample Survey / Benchmark` (e.g., NCES NTPS/SASS) |

---

## 2. Definitions & Conceptual Boundaries

### 2.1 Plain-Language Definition
*A one-to-two sentence explanation of what this measure represents in everyday terms for a non-technical reader, superintendent, or journalist.*

### 2.2 Formal / Statistical Definition
*The exact mathematical and statistical formulation. Include mathematical notation, equations, and aggregation logic.*

$$\text{Measure}_{i,t} = \frac{\text{Numerator}_{i,t}}{\text{Denominator}_{i,t}}$$

### 2.3 Aggregation & Weighting Discipline
*Explicit mathematical rule for aggregating from the observation unit to higher geographies (district, county, state, nation).*

$$\overline{\text{Measure}}_{\text{aggregate}} = \frac{\sum_{i} \text{Numerator}_i}{\sum_{i} \text{Denominator}_i} \ne \frac{1}{N}\sum_{i} \text{Measure}_i$$

*Specify whether unweighted averaging is prohibited and explain the nature of aggregation bias (e.g., small-school upward distortion).*

### 2.4 Unit & Scale
- **Unit of Measurement:** (e.g., `students_per_fte`, `percent`, `count_persons`, `hours_per_week`)
- **Theoretical Range:** (e.g., $[0, \infty)$, $[0, 100\%]$)
- **Empirical Realistic Range:** (e.g., $8.0$ to $35.0$)
- **Resolution / Precision:** (e.g., rounded to 1 decimal place, full float)

---

## 3. Provenance & Source Mapping

### 3.1 Raw Source Fields
| Source ID | Table / File Name | Field Variable Name | Field Description | Data Type | Notes / Nullable |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `source-id` | `table_name.csv` | `RAW_FIELD_1` | Exact description in codebook | Float/Integer | Codebook definition |
| `source-id` | `table_name.csv` | `RAW_FIELD_2` | Exact description in codebook | Float/Integer | Codebook definition |

### 3.2 Calculation Formula & Intermediate Operations (If Derived)
*Step-by-step arithmetic pipeline including handling of intermediate values, deductions, and fallback rules.*
1. **Deductions:** (e.g., Pre-K enrollment and Pre-K staff deductions).
2. **Intermediate Variables:** Definitions and formulas.
3. **Division Guardrails:** Condition under which denominator is invalid or results in `NaN`.

---

## 4. Scope, Granularity & Temporal Disambiguation

| Dimension | Specification | Notes & Boundary Conditions |
| :--- | :--- | :--- |
| **Target Population** | e.g., Public regular elementary/secondary students | Specify grade levels (Pre-K vs K–12) and student sub-populations |
| **Unit of Observation** | Campus (`NCESSCH`) \| District (`LEAID`) \| Section \| Student | Must distinguish reporting entity from analytical observation unit |
| **Geographic Granularity** | Campus \| LEA \| County \| Metro \| State \| National | Explicitly state geographic boundary rules |
| **Temporal Granularity** | Annual Snapshot \| Biennial Survey \| Cumulative School Year | State the exact collection mechanism |
| **School Year of Reference (SY)** | e.g., `2024-25` | **Primary Indexing Dimension.** Academic year of observation |
| **Collection Snapshot Date** | e.g., On or near October 1 of school year | Official reference date for student/staff counts |
| **Publication / Release Date** | e.g., December 2025 (Provisional), August 2026 (Final) | Calendar date when data was released to the public |
| **Publication Lag** | e.g., 12 to 24 months | Time elapsed between snapshot and public availability |
| **Earliest Available Year** | e.g., SY 1986–87 | Earliest continuous digital or published record |
| **Latest Audited Year** | e.g., SY 2024–25 | Most recent audited release |
| **Expected Update Cadence** | Annual \| Biennial \| Quadrennial | Frequency of future releases |

> [!IMPORTANT]
> **Temporal Disambiguation Standard:** Never use a single calendar year (e.g., "2024") without specifying whether it denotes the **School Year of Reference** (`SY 2024–25`) or the **Data Publication Release Year** (`2024`). The Observatory strictly indexes all measures by School Year of Reference.

---

## 5. Collection Mechanism, Organizational Allocation & Ingestion Mechanics

### 5.1 Collection Mechanism
*How are these numbers collected? Administrative census, survey sampling, statutory compliance filing, civil rights survey, or financial audit? Who reports them (school clerk, LEA central HR, state data team)?*

### 5.2 Organizational Allocation Sensitivity (Campus vs. Central Office)
*How does this measure handle personnel or resources shared across multiple campuses or held centrally at the district office?*
- **Itinerant Staff Allocation:** Are shared teachers (e.g., art, music, SPED, speech) reported as fractional FTEs across school buildings or aggregated at the central office?
- **Central Allocation Gap:** 
  $$\Delta_{\text{central}} = \text{Measure}_{\text{campus\_aggregate}} - \text{Measure}_{\text{district\_direct}}$$
- **Guidance:** Rules for comparing campus-level values across districts with contrasting allocation practices.

### 5.3 Step-by-Step Analytical Filtering & Outlier Protocol
*Standardized 5-step data sanitation protocol required before analysis:*
1. **Exception Code Sanitization:** Map negative exception codes (`-1`, `-2`, `-9`) to `NaN`.
2. **Entity Universe Filtering:** Filter for operating regular public schools (`TYPE == 1`, `STATUS in [1, 3, 8]`).
3. **Threshold Guardrails:** Minimum size requirements (e.g., $\text{Students} \ge 10$, $\text{FTE} \ge 1.0$).
4. **Outlier Triage:** Explicit upper and lower bounds triggering diagnostic review vs. automatic exclusion.
5. **Denominator Weighting:** Enforce ratio-of-sums aggregation for higher geographic units.

### 5.4 Exclusion Rules
*Explicit list of non-standard educational entities that MUST be excluded to prevent catastrophic bias:*
- Virtual / cyber schools.
- Specialized special education day facilities.
- Juvenile justice / detention center schools.
- Career and Technical Education (CTE) centers with shared enrollment.
- Inactive, closed, or future-opening schools.

### 5.5 Missing Values & Native Codebook Flags
| Source Code | Code Meaning | Pipeline Action |
| :--- | :--- | :--- |
| `-1` | Missing / Not reported | Recode to `NaN`; never treat as zero |
| `-2` | Not applicable | Recode to `NaN` or explicit `NA` category |
| `-9` | Suppressed for privacy / FERPA | Recode to `NaN`; flag as `suppressed` |
| `0` | Reported zero | Verify if plausible (e.g., zero teachers with positive enrollment = non-reporting) |

---

## 6. Methodological Breaks & Comparability Warnings

### 6.1 Known Historical Breaks & Variable Shifts
*Chronological register of statutory, survey, or layout changes.*
- **Year YYYY–YY:** Change description, affected variables, and pipeline correction.

### 6.2 Jurisdictional Portability Boundaries
*Why can this measure NOT be compared naively across state lines, district types, or governance models?*
- Differences in state job codes, certification requirements, or administrative definitions.
- Discrepancies between federal CCD aggregates and state report card metrics.

### 6.3 Plausible Measurement Error & Administrative Friction
*Where do errors, distortions, and noise originate in the real world?*
- Roster churn / student mobility between snapshot date and end-of-year testing.
- Rounding of fractional FTE assignments.
- Strategic classification to meet accreditation standards or funding thresholds.

---

## 7. Semantic Auditing: Legitimate vs. Illegitimate Inferences

> [!IMPORTANT]
> The primary epistemic defense of the Observatory is establishing what a measure answers **before** correlating it with anything else.

### 7.1 What Question Does This Measure Legitimately Answer?
*Clear, precise research questions that this metric is structurally and mathematically equipped to address.*
1. 
2. 
3. 

### 7.2 What Question Does This Measure NOT Answer?
*Questions that this metric is frequently misapplied to answer, but cannot answer validly.*
1. 
2. 
3. 

### 7.3 Structural Transformation Multipliers & Wedges
*Mathematical identities and conversion factors that bridge this macro measure to classroom realities.*

$$\text{Classroom Reality} \approx \text{Macro Measure} + \sum \Delta_k$$

- **Wedge $\Delta_1$ (Role Composition):** Difference attributable to specialized non-classroom personnel.
- **Wedge $\Delta_2$ (Schedule Capacity Multiplier $\phi$):** Structural expansion driven by teacher planning and bell schedules:
  $$\phi = \frac{P_{\text{student}}}{P_{\text{teacher}}}$$
- **Wedge $\Delta_3$ (Curricular Distribution):** Allocation differences between elective/advanced courses and core gateway courses.

### 7.4 Common Misinterpretations & Policy Traps
- **Misinterpretation 1:** 
- **Misinterpretation 2:** 

---

## 8. Relational Architecture & Validation

### 8.1 Upstream & Downstream Relationships
- **Derived From (Inputs):** Which constituent measures produce this?
  - `EDU-XXX`: Name
  - `EDU-YYY`: Name
- **Contributes To (Outputs):** Which derived composite measures depend on this?
  - `EDU-ZZZ`: Name

### 8.2 Related & Alternative Measures
| Measure ID | Measure Name | Nature of Difference / Contrast | When to Prefer |
| :--- | :--- | :--- | :--- |
| `EDU-XXX` | Alternative Name | Structural difference in denominator or scope | Specific research context |

### 8.3 Candidate External Validation Sources
*Independent datasets, sample surveys, microdata, or court audits that can triangulate or stress-test this measure.*
- Sample surveys (e.g., NCES NTPS / SASS teacher questionnaires).
- Course-level compliance collections (e.g., OCR CRDC course rosters).
- State longitudinal personnel registers (e.g., KPTEN, MOSIS).
- Non-administrative physical audits (e.g., master schedules, school board filings).

---

## 9. Historical & Institutional Context

*What policy mandates, judicial orders, contractual bargaining rules, or funding formulas govern or distort this measure? (e.g., desegregation remedies, state minimum staffing ratios, class-size reduction grants, collective bargaining planning periods).*

---

## 10. Initial Empirical & Descriptive Sanity Checks

*Mandatory assertions and descriptive checks to execute before including this measure in downstream models:*

- [ ] **Assertion 1 (Non-Negativity):** All negative missing codes mapped to `NaN`. Zero negative values allowed.
- [ ] **Assertion 2 (Range & Extremes):** Min, max, 1st percentile, 99th percentile checked against physical realities.
- [ ] **Assertion 3 (Zero Denominator):** Check for $\text{Denominator} \le 0$; recode invalid ratios to `NaN`.
- [ ] **Assertion 4 (Aggregation Discipline):** Enforce ratio-of-sums aggregation; test difference between unweighted mean and weighted ratio.
- [ ] **Assertion 5 (Longitudinal Discontinuity Detection):** Flag entities exhibiting annual step-changes $> \pm 25\%$ without verified boundary changes.

---

## 11. Observatory Usage & Dashboard Role

- **Dashboard Role:** (e.g., Contextual background metric \| Core exploratory dimension \| Guardrail metric \| Prohibited for headline display).
- **Mandatory Presentation Disclaimer:** Exact standard text required whenever this measure appears in a chart, table, or user-facing view.
- **Dossier Audit History:**
  - `YYYY-MM-DD`: Initial draft authored.
  - `YYYY-MM-DD`: Audited against empirical evidence.
