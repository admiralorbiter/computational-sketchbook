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
| **Category** | e.g., Staffing Capacity \| Enrollment & Demographics \| Student Need & Complexity \| Coursework & Curricular Load \| Fiscal |
| **Derived or Directly Reported** | `Directly Reported` (raw from agency) \| `Derived` (arithmetic calculation) |

---

## 2. Definitions & Conceptual Boundaries

### 2.1 Plain-Language Definition
*A one-to-two sentence explanation of what this measure represents in everyday terms for a non-technical reader, superintendent, or journalist.*

### 2.2 Formal / Statistical Definition
*The exact mathematical and statistical formulation. Include mathematical notation, equations, and aggregation logic.*

$$\text{Measure} = \frac{\text{Numerator}}{\text{Denominator}}$$

### 2.3 Unit & Scale
- **Unit of Measurement:** (e.g., students per teacher FTE, percent of enrollment, count of persons, hours per week)
- **Theoretical Range:** (e.g., $[0, \infty)$, $[0, 100\%]$)
- **Empirical Realistic Range:** (e.g., $8.0$ to $35.0$)

---

## 3. Provenance & Source Mapping

### 3.1 Raw Source Fields
| Source ID | Table / File Name | Field Variable Name | Field Description | Data Type | Notes / Nullable |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `source-id` | `table_name.csv` | `RAW_FIELD_1` | Exact description in codebook | Float/Integer | Codebook definition |
| `source-id` | `table_name.csv` | `RAW_FIELD_2` | Exact description in codebook | Float/Integer | Codebook definition |

### 3.2 Calculation Formula (If Derived)
*Detailed step-by-step arithmetic derivation including intermediate variable handling, rounding rules, and aggregation order (e.g., ratio of sums vs. sum of ratios).*

- **Numerator:** Exactly which fields are summed, filtered, or weighted.
- **Denominator:** Exactly which fields are summed, filtered, or weighted.
- **Weighting Scheme:** (e.g., unweighted campus level, student-weighted district level, teacher-weighted section level).

---

## 4. Scope, Granularity & Coverage

| Dimension | Specification | Notes & Boundary Conditions |
| :--- | :--- | :--- |
| **Target Population** | e.g., Public regular elementary/secondary students | Specify grade levels (PreK vs K-12), school types included |
| **Unit of Observation** | e.g., Campus (School) \| LEA (District) \| Classroom Section \| Student | Must distinguish reporting unit from observation unit |
| **Geographic Granularity** | e.g., Campus \| LEA \| County \| Metro (MARC) \| State \| National | |
| **Temporal Granularity** | e.g., Annual Fall Snapshot \| Biennial Survey \| Cumulative School Year | State the official collection date (e.g., October 1) |
| **Earliest Known Availability** | e.g., SY 1986–87 | Earliest continuous digital or published record |
| **Latest Known Availability** | e.g., SY 2024–25 | Most recent audited release |
| **Expected Update Cadence** | e.g., Annual (provisional in Spring, final in Autumn) | Publication lag from collection date |

---

## 5. Collection Mechanism & Ingestion Mechanics

### 5.1 Collection Mechanism
*How are these numbers collected? Administrative census, survey sampling, statutory compliance filing, civil rights survey, or financial audit? Who reports them (school clerk, LEA central HR, state data team)?*

### 5.2 Inclusion Rules
*Which entities or records are legitimately included in this measure?*
- School type inclusions (e.g., Regular local public schools, charter schools, vocational schools).
- Operational status criteria (e.g., Open, operating, non-zero enrollment).

### 5.3 Exclusion Rules
*Which entities or records MUST be excluded to prevent catastrophic bias?*
- Exclusions (e.g., Virtual-only academies, specialized special-education day facilities, detention centers, closed campuses, summer-only facilities).

### 5.4 Missing Values & Suppression Codes
*Explicit inventory of negative numbers, codes, and character flags used by the source agency.*

| Source Code | Meaning | Remediation Action in Observatory Pipeline |
| :--- | :--- | :--- |
| `-1` | Missing / Not reported | Recode to `NaN`; do NOT treat as zero |
| `-2` | Not applicable | Recode to `NaN` or explicit `NA` category |
| `-9` | Suppressed for privacy / FERPA | Recode to `NaN`; flag as `suppressed` |
| `.` / `NULL` | Empty cell | Verify reason; recode to `NaN` |

---

## 6. Methodological Breaks & Comparability Warnings

### 6.1 Known Methodological Changes
*Chronological list of changes to definitions, reporting guidelines, survey forms, or federal statutes that affect longitudinal consistency.*

- **Year YYYY–YY:** Change description and impact.
- **Year YYYY–YY:** Change description and impact.

### 6.2 Comparability Warnings across Jurisdictions / Time
*Why can this measure NOT be compared naively across state lines, district types, or decades?*
- State-to-state variation in job codes or categorization.
- Differences between federal CCD definitions and state report card definitions.

### 6.3 Plausible Measurement Error
*Where do the errors come from?*
- Roster churn / mobility between snapshot date and end of year.
- Split-campus or itinerant personnel allocation ambiguities.
- Part-time FTE rounding errors.
- Self-reporting social desirability or regulatory avoidance.

---

## 7. Semantic Auditing: Legitimate vs. Illegitimate Inferences

> [!IMPORTANT]
> The primary epistemic defense of the Observatory is establishing what a measure answers **before** correlating it with anything else.

### 7.1 What Question Does This Measure Legitimately Answer?
*Clear, precise research questions that this number is structurally and mathematically equipped to address.*
1. 
2. 
3. 

### 7.2 What Question Does This Measure NOT Answer?
*Questions that this number is frequently forced to answer, but cannot answer validly.*
1. 
2. 
3. 

### 7.3 Common Misinterpretations & Traps
*Document widely held public, journalistic, or academic misconceptions.*
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
| Measure ID | Measure Name | Nature of Difference / Contrast |
| :--- | :--- | :--- |
| `EDU-XXX` | Alternative Name | Why and when would a researcher choose that over this? |

### 8.3 Candidate External Validation Sources
*Independent datasets, surveys, or audits that can triangulate or stress-test this measure.*
- Independent administrative sources (e.g., State retirement board records vs. district headcount).
- Sample surveys (e.g., NCES NTPS teacher self-reports).
- Microdata / Course files (e.g., Civil Rights Data Collection section records).

---

## 9. Historical & Institutional Context

*What policy mandates, judicial orders, contractual bargaining rules, or funding formulas govern or distort this measure? (e.g., desegregation remedies, state minimum staffing ratios, class-size reduction grants, collective bargaining planning periods).*

---

## 10. Initial Empirical & Descriptive Sanity Checks

*Mandatory descriptive checklist to execute before using this measure in any cross-measure analysis:*

- [ ] **Range & Extremes Audit:** Min, max, 1st percentile, 99th percentile checked against physical realities.
- [ ] **Missingness Pattern:** Missing rate calculated overall, by year, by state, and by locale.
- [ ] **Zero-Value Audit:** Confirm whether zero is mathematically plausible or indicates non-reporting.
- [ ] **Longitudinal Jump Detection:** Flag entities exhibiting annual shifts $> \pm 30\%$ without known boundary changes.
- [ ] **Weighting Parity Check:** Compare unweighted campus mean against student-weighted district mean.

---

## 11. Observatory Usage & Dashboard Role

- **Dashboard Role:** (e.g., Contextual background metric \| Core exploratory dimension \| Guardrail metric \| NOT RECOMMENDED for headline display).
- **Presentation Caveat:** Standard disclaimer text required whenever this measure appears in a chart or table.
- **Dossier Audit History:**
  - `YYYY-MM-DD`: Initial draft authored.
  - `YYYY-MM-DD`: Audited against empirical evidence.
