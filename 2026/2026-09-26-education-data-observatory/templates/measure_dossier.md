# Measure Dossier Template

> **Observatory Standard:** Every measure in the Education Data Observatory must maintain a complete dossier prior to empirical correlation, indexing, or dashboard presentation. The durable research unit is the **measure**, connected to external sources via explicit **operationalizations**.
> 
> *Principle: Source ≠ Field ≠ Operationalization ≠ Measure ≠ Claim.*
> *Rule of thumb: Complete measurement semantics before modeling. Description before explanation.*

---

## 1. Identity & Classification

| Attribute | Specification |
| :--- | :--- |
| **Measure ID** | `EDU-XXX` (e.g., `EDU-001`) |
| **Canonical Human-Readable Name** | Clear, standard descriptive name |
| **Short Identifier / Slug** | `lowercase-hyphenated-slug` |
| **Status** | `proposed` \| `audited` \| `validated` \| `deprecated` |
| **Lifecycle Stage** | Epistemic Ladder Stage: `source` $\to$ `field` $\to$ `operationalization` $\to$ `measure` $\to$ `description` $\to$ `validation` $\to$ `relationships` $\to$ `explanation` |
| **Category** | Staffing Capacity \| Enrollment & Demographics \| Student Need & Complexity \| Coursework & Curricular Load \| Fiscal |
| **Construct Nature** | `Directly Reported Administrative Item` \| `Derived Mathematical Construct` \| `Survey Benchmark` |
| **Associated Operationalizations** | Links to operationalization IDs registered in [`../../registry/operationalizations.csv`](../../registry/operationalizations.csv) |

---

## 2. Definitions & Conceptual Boundaries

### 2.1 Plain-Language Definition
*A one-to-two sentence explanation of what this abstract construct represents in everyday terms for a non-technical reader, school board member, or journalist.*

### 2.2 Formal / Statistical Definition
*The exact mathematical or formal specification of the construct.*

$$\text{Construct}_{i,t} = f(\mathbf{x}_{i,t})$$

### 2.3 Aggregation Rules & Multiple Estimands (If Applicable)
*When aggregating across entities (e.g., schools to districts, districts to states), different research questions demand different estimands. Document the valid estimands:*

1. **Pooled / Aggregate Estimand:** What is the rate or density across the entire combined population?
   $$\text{Pooled} = \frac{\sum \text{Numerator}_i}{\sum \text{Denominator}_i}$$
2. **Unweighted Entity Mean:** What does the typical organization or school look like on this dimension?
   $$\text{Mean} = \frac{1}{N}\sum_{i=1}^N \text{Construct}_i$$
3. **Median & Distributional Quantiles:** What does the middle entity look like, and how dispersed are the tails?

*Explain the distinct research question answered by each estimand. Never dismiss an unweighted or pooled metric as inherently "biased" without defining the specific estimand under inquiry.*

### 2.4 Unit & Scale
- **Unit of Measurement:** (e.g., `count_persons`, `percent`, `rate_per_unit`, `index_score`)
- **Theoretical Range:** (e.g., $[0, \infty)$, $[0, 100\%]$)
- **Empirical Realistic Range:** Range observed in typical public settings.

---

## 3. Provenance & Operationalization Inventory

*A single conceptual measure may be implemented through multiple distinct operationalizations across different agencies, jurisdictions, or research studies.*

| Operationalization ID | Implementing Agency / Source | Specific Target Population | Exact Formula / Source Fields | Provenance Tier |
| :--- | :--- | :--- | :--- | :--- |
| `OP-ID-1` | Agency / Table | Target subpopulation | Formula using raw field names | Tier 1 National \| Tier 2 State |
| `OP-ID-2` | Agency / Table | Target subpopulation | Formula using raw field names | Tier 1 National \| Tier 2 State |

---

## 4. Scope, Granularity & Temporal Disambiguation

| Dimension | Specification | Notes & Boundary Conditions |
| :--- | :--- | :--- |
| **Target Population** | e.g., Public elementary and secondary students | Specify grade levels, age ranges, or legal classifications |
| **Unit of Observation** | Campus (`NCESSCH`) \| LEA (`LEAID`) \| Classroom \| Individual | Reporting entity vs. analytical observation unit |
| **Geographic Granularity** | Campus \| LEA \| County \| Metropolitan Area \| State \| National | |
| **Temporal Granularity** | Annual Snapshot \| Cumulative Academic Year \| Biennial Census | |
| **School Year of Reference (SY)** | e.g., `SY 2024–25` | **Primary Indexing Dimension.** Academic year of observation |
| **Collection Reference Date** | e.g., October 1 fall count \| End-of-year attendance audit | Exact date or window when counts are frozen |
| **Publication Release Date** | Calendar date or lag (e.g., +12 months provisional, +24 months final) | Date when public file was released |
| **Earliest Available Year** | e.g., SY 1986–87 | Earliest continuous digital or published record |
| **Latest Audited Year** | e.g., SY 2024–25 | Most recent audited release in the Observatory |
| **Update Cadence** | Annual \| Biennial \| Quadrennial | |

> [!IMPORTANT]
> **Temporal Disambiguation Standard:** Never use an isolated calendar year (e.g., "2024") without specifying whether it denotes the **School Year of Reference** (`SY 2024–25`) or the **Data Publication Release Year** (`2024`). The Observatory strictly indexes all measures by School Year of Reference.

---

## 5. Universe Definitions & Analytical Subsets

> [!NOTE]
> The Observatory preserves unusual observations rather than deleting them. A non-standard school (e.g., a cyber academy or a specialized day school) is valid empirical data about that organizational model, not "dirty data."

### A. Source Universe
*What is the complete universe of entities collected by the underlying data system? (e.g., all operating and non-operating public schools, charter campuses, vocational facilities, state-operated schools, and administrative centers).*

### B. Mathematical Validity Requirements
*Universal mathematical conditions required for the metric to be defined:*
- Non-negative counts: $\text{Field} \ge 0$.
- Non-zero denominator: $\text{Denominator} > 0$ (if a ratio).
- Recoding negative exception codes (`-1`, `-2`, `-9`) to `NaN`.

### C. Entity-Type & Anomaly Flags
*Flags attached to records to characterize their institutional form without deleting them:*
- `flag_virtual`: Cyber or virtual school.
- `flag_special_ed`: Dedicated special education day facility.
- `flag_alternative`: Alternative or disciplinary school.
- `flag_career_tech`: CTE or vocational center with shared/part-time enrollment.
- `flag_outlier_low` / `flag_outlier_high`: Statistical boundary flags triggering audit.

### D. Recommended Analytic Comparison Universes
*Defined entity subsets appropriate for specific research questions:*
- **Standard Regular Public School Comparison Universe:** Operating local regular schools (`TYPE == 1`, `STATUS in [1, 3, 8]`, $\text{Enrollment} \ge 10$).
- **Comprehensive Secondary Universe:** High schools offering standard grade 9–12 core coursework.
- **Specialized Institutional Universe:** Separate panel tracking specialized or alternative facilities.

---

## 6. Known Source Distortions & Organizational Sensitivity

### 6.1 Organizational Allocation Sensitivity (If Applicable)
*Does the organizational assignment of personnel, students, or resources vary across districts? (e.g., itinerant staff assigned to central office vs. campus rosters; shared CTE students; regional cooperatives).*

### 6.2 Known Source-Specific Distortions
*Document agency reporting anomalies, variable renaming history, state reporting exemptions, or suppression rules.*

---

## 7. Semantic Auditing: Legitimate vs. Illegitimate Inferences

### 7.1 What Question Does This Measure Legitimately Answer?
*Clear, precise research questions that this metric is structurally and mathematically equipped to address.*
1. 
2. 

### 7.2 What Question Does This Measure NOT Answer?
*Questions that this metric is frequently misapplied to answer, but cannot answer validly.*
1. 
2. 

### 7.3 Known Transformations & Related Constructs (If Applicable)
*If this measure serves as a component of or proxy for a more complex institutional reality, document the transformation models, empirical multipliers, or decomposition frameworks that connect them.*

### 7.4 Common Misinterpretations & Policy Traps
- **Misinterpretation 1:** 
- **Misinterpretation 2:** 

---

## 8. Relational Architecture & Validation

### 8.1 Upstream & Downstream Relationships
- **Upstream (Inputs):** Constituent measures or raw inputs.
- **Downstream (Outputs):** Composite or derived measures depending on this.

### 8.2 Candidate External Validation Sources
*Independent datasets, sample surveys, microdata, or physical audits that can triangulate or stress-test this measure.*

---

## 9. Historical & Institutional Context

*What policy mandates, statutory funding formulas, court orders, or collective bargaining rules govern or shape this measure?*

---

## 10. Initial Empirical & Descriptive Sanity Checks

*Mandatory descriptive checklist to execute before using this measure in downstream models:*

- [ ] **Range & Extremes Audit:** Min, max, median, 1st and 99th percentiles checked against physical reality.
- [ ] **Missingness & Suppression Analysis:** Documented by year, geography, and entity type.
- [ ] **Zero-Value Audit:** Determine whether zero represents a true count or non-reporting.
- [ ] **Longitudinal Jump Detection:** Flag entities exhibiting annual step-changes $> \pm 25\%$ without verified boundary changes.
- [ ] **Estimand Sensitivity Check:** Compare pooled aggregate, unweighted mean, and median.

---

## 11. Visual Evidence Packet

> [!IMPORTANT]
> The Observatory maintains visual evidence to understand distributions and contexts before modeling. Every visualization must maintain explicit, documented provenance.

### 11.1 Standard Visualization Classes
1. **National Historical Trend:** Longitudinal series displaying multi-year trajectories with explicit source citations.
2. **Distribution & Tails:** Histograms or quantile plots showing medians, IQR, and extreme tails.
3. **National / Regional Contextualization:** Where a local region (e.g., Kansas City) sits within the national distribution.
4. **Internal Geographic / Subgroup Variation:** Disaggregation by locale, district type, or grade span.
5. **Operationalization Sensitivity:** Visual comparison showing how the measure changes under alternative operationalizations.
6. **Cross-Source Contrast:** Juxtaposition against a related or commonly confused measure (e.g., PTR vs. class size), with explicit labels noting different sources and years.

### 11.2 Visual Provenance Standard
Every graphic in the visual packet must document:
- **Measure / Operationalization ID(s):** Exact IDs used.
- **Data Source & Table:** Authoritative agency citation.
- **School Year of Reference:** Specific academic year(s) represented.
- **Target Population & Geography:** Explicit population universe.
- **Figure Classification:** `DESCRIPTIVE OBSERVATION` \| `CROSS-SOURCE COMPARISON` \| `MODEL / SIMULATION`.
- **Generating Pipeline Script:** Path to reproducible script.

---

## 12. Observatory Usage & Status

- **Observatory Role:** (e.g., Core descriptive measure \| Contextual background \| Guardrail metric \| Experimental).
- **Mandatory Presentation Caveats:** Standard disclaimer text required when displayed.
- **Audit History:**
  - `YYYY-MM-DD`: Initial draft authored.
  - `YYYY-MM-DD`: Audited against empirical evidence.
