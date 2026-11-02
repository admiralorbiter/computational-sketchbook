# Education Data Observatory — Milestone 1 Project Handoff

> **Authoritative Cold-Start Context Document**  
> **Status:** Milestone 1 Complete — Project Paused  
> **Repository:** `admiralorbiter/computational-sketchbook`  
> **Project Directory:** `2026/2026-09-26-education-data-observatory/`  
> **Canonical Milestone Tag:** `education-observatory-milestone-1`  
> **Last Audited & Frozen Checkpoint:** Commit `820455b`  

---

## 1. Project Purpose & Core Architecture

The Education Data Observatory was created to solve a pervasive problem in education research and policy: **construct collapse**. 

Commonly used administrative metrics routinely conflate fundamentally distinct constructs. Most critically, **Pupil/Teacher Ratio (PTR)** is an administrative measure of adult teacher staffing density, yet it is almost universally misinterpreted as a proxy for individual classroom class size, teacher daily contact load, or student peer exposure.

To establish semantic precision, empirical auditability, and mathematical reproducibility, the Observatory enforces a strict **Seven-Layer Epistemic Architecture**:

$$\text{SOURCE} \longrightarrow \text{FIELD} \longrightarrow \text{OPERATIONALIZATION} \longrightarrow \text{MEASURE} \longrightarrow \text{UNIVERSE} \longrightarrow \text{ESTIMAND} \longrightarrow \text{CLAIM}$$

1. **Source:** An authoritative data collection system or administrative agency (e.g., NCES CCD, OCR CRDC, KSDE KPTEN, MO DESE).
2. **Field:** A specific column or variable within an immutable source file (e.g., `TEACHERS`, `MEMBER`).
3. **Operationalization:** A documented aggregation rule or mathematical formula transforming raw fields into a metric (e.g., `PTR-NCES-SCHOOL` vs. `PTR-NCES-LEA`).
4. **Measure:** A standardized conceptual construct cataloged in [`registry/measures.csv`](registry/measures.csv) (e.g., `EDU-001`, `EDU-002`, `EDU-003`).
5. **Universe:** A precisely bounded, reproducible entity population cataloged in [`registry/universes.csv`](registry/universes.csv) (e.g., `KC_BALANCED_LEA_75`, `KC_FULLY_REGIONAL_CURRENT_77`).
6. **Estimand:** A specific mathematical quantity computed over a defined universe (e.g., pooled ratio, unweighted mean, median, student-weighted exposure).
7. **Claim:** An empirical finding formalizing start/end values, absolute change, percent change, and epistemic status in the machine-readable ledger [`analysis/results/claims.csv`](analysis/results/claims.csv).

---

## 2. Current Project State: Milestone 1 Complete

The Observatory has completed **Milestone 1** and is **intentionally paused**:

| Measure ID | Canonical Name | Status | Epistemic Role |
| :--- | :--- | :--- | :--- |
| [`EDU-001`](measures/EDU-001-pupil-teacher-ratio/README.md) | **Pupil / Teacher Ratio (PTR)** | `audited` (**FROZEN**) | Macro teacher staffing density; multi-stage structural bridge to class size |
| [`EDU-002`](measures/EDU-002-student-enrollment/README.md) | **Student Headcount Enrollment** | `audited` (**FROZEN**) | Numerator for student capacity; pipeline shocks; spatial stability |
| [`EDU-003`](measures/EDU-003-total-teacher-fte/README.md) | **Reported Classroom Teacher FTE** | `audited` (**FROZEN**) | Denominator for teacher staffing; downward stickiness; curricular breadth |

- **All Other Measures:** Remain in `proposed` lifecycle status in [`registry/measures.csv`](registry/measures.csv).
- **Next Candidate Measure:** [`EDU-005 Paraprofessional FTE`](registry/measures.csv) is the planned next measure, but it is **DEFERRED** and must **not** be marked "in progress" during the pause.
- **Verification Suite:** 21 automated validation checks in [`scripts/validate_observatory.py`](scripts/validate_observatory.py) pass with 0 errors and 0 warnings.

---

## 3. Epistemic Trust Hierarchy

When resuming this repository or resolving apparent conflicts, future researchers and AI agents must trust artifacts strictly in the following order:

```text
1. Machine-Readable Registries (registry/measures.csv, registry/sources.csv, registry/universes.csv, registry/operationalizations.csv)
   └── 2. Machine-Readable Claims Ledger (analysis/results/claims.csv)
       └── 3. Canonical Measure Dossiers (measures/EDU-*/README.md)
           └── 4. Canonical Source Dossiers (sources/*/README.md)
               └── 5. Canonical Generating Scripts (scripts/generate_claims_ledger.py, analysis/cross-measure/generate_*_visuals.py)
                   └── 6. Cross-Measure Research Memos (analysis/cross-measure/*_memo.md)
                       └── 7. Historical Exploratory Scripts (analysis/cross-measure/task*_*.py, explore_*.py)
                           └── 8. Prose Completion Reports, Turn Summaries & Conversation Transcripts
```

> [!CRITICAL]
> **Prose completion summaries and conversational responses are NOT canonical.** If an old completion report, summary note, or conversation transcript states a number that conflicts with [`analysis/results/claims.csv`](analysis/results/claims.csv) or the registered dossiers, the machine-readable ledger and dossiers govern unconditionally.

---

## 4. Frozen Core Findings by Measure

All headline findings are generated directly from data and cataloged in [`analysis/results/claims.csv`](analysis/results/claims.csv):

### 4.1 EDU-002: Student Headcount Enrollment
- **`CLM-ENR-001` (10-Year Balanced Regional Enrollment):** Across the 75 continuously operating regional LEAs (`KC_BALANCED_LEA_75`), K–12 student headcount was essentially flat: **$320,465 \to 318,406$** ($-2,059$ students, **$-0.64\%$**).
- **`CLM-ENR-002` (Regional Campus vs. LEA Total Membership Gap):** In SY 2024–25 across 77 regional LEAs (`KC_FULLY_REGIONAL_CURRENT_77`), district-reported membership ($330,356$) exceeded campus-aggregated membership ($328,884$) by **$+1,472$ students ($+0.45\%$)**. 61 of 77 LEAs reconcile with zero difference; the gap reflects legitimate central/shared reporting, not "missing" students.
- **`CLM-ENR-002-K12` (Regional Campus vs. LEA K–12 Membership Gap):** Restricting to K–12 grades, the gap narrows to **$+602$ students ($+0.19\%$)**: $318,281 \to 318,883$.
- **`CLM-ENR-003` (10-Year Kindergarten Enrollment Shock):** In `KC_BALANCED_LEA_75`, kindergarten enrollment fell **$-9.14\%$** ($25,622 \to 23,281$, net $-2,341$), heavily concentrated in the Fall 2020 COVID shock ($-11.43\%$). Over the same 10-year span, Grades 1–12 enrollment combined grew slightly ($+0.10\%$).
- **`CLM-ENR-004` (Spatial Centroid Stability):** Between 2014–15 and 2024–25, the enrollment-weighted geographic centroid of the Kansas City region shifted only **$0.32$ miles ($1,686.5$ feet)**. No net outward centrifugal migration was observed.

### 4.2 EDU-003: Reported Classroom Teacher FTE
- **`CLM-TCH-001` (10-Year Balanced K–12 Classroom Teacher FTE):** In `KC_BALANCED_LEA_75`, reported classroom teachers expanded steadily: **$21,582.76 \to 23,500.17$** ($+1,917.41$ FTE, **$+8.88\%$**), even as student enrollment remained flat.
- **`CLM-TCH-001-ALT-TOT` (10-Year Total Teacher FTE including Pre-K):** Including Pre-K teachers, teacher FTE expanded **$+9.33\%$** ($22,210.45 \to 24,283.26$, $+2,072.81$ FTE).
- **`CLM-TCH-001-DYN` (Dynamic Regional LEA K–12 Teacher FTE):** Allowing dynamic district entry/exit (`KC_DYNAMIC_REGIONAL_LEA`), teacher FTE grew **$+8.88\%$** ($21,633.26 \to 23,555.17$, $+1,921.91$ FTE).
- **`CLM-TCH-002` & `CLM-TCH-002-ENR` (Downward Staffing Stickiness):** Across 28 declining LEAs with unchanged operating-school counts (`KC_DECLINING_UNCHANGED_COUNT_28`), enrollment fell **$-8.33\%$** ($52,657 \to 48,269$), but classroom teachers fell only **$-3.63\%$** ($3,755.53 \to 3,619.27$), proving asymmetric downward staffing stickiness.
- **`CLM-TCH-002-SENS` (Staffing Stickiness Sensitivity):** In the stricter sensitivity cohort of 25 LEAs with 100% identical endpoint school IDs (`KC_DECLINING_IDENTICAL_IDS_25`), stickiness replicates cleanly: enrollment fell **$-10.50\%$**, while teacher FTE fell only **$-3.35\%$** ($1,971.52 \to 1,905.48$).
- **`CLM-TCH-003-KS` & `CLM-TCH-003-MO` (Campus vs. LEA Teacher Reporting Gaps):** In SY 2024–25, Kansas LEA-reported teachers exceed campus sums by **$+455.26$ FTE ($+4.32\%$)**; Missouri LEA totals exceed campus sums by **$+63.23$ FTE ($+0.46\%$)**.
- **`CLM-TCH-004` (Matched Small High School Curricular Attrition):** Among 28 continuously operating small high schools ($<800$ students, `KC_SMALL_HS_MATCHED_28`), the proportion offering Calculus fell from **$67.86\%$ to $35.71\%$** ($-32.14$ percentage points, a **$-47.37\%$** relative decline).
- **`CLM-TCH-005` (Secondary Staffing Wedge):** Across 101 regular operating high schools with valid CRDC and CCD data (`KC_REGULAR_HS_2023_24`), mean Algebra I class size ($19.28$) exceeded mean high school macro PTR ($14.76$) by **$+4.53$ students ($+30.66\%$)**.
- **`CLM-TCH-006` (Jackson County Charter Expansion):** In the Jackson County independent charter sector (`KC_JACKSON_CHARTER_LEA_HISTORY`), teacher FTE expanded **$+59.50\%$** ($790.22 \to 1,260.43$), more than double the student growth rate ($+26.15\%$).

### 4.3 EDU-001: Pupil / Teacher Ratio
- **`CLM-PTR-001` (10-Year Balanced Regional PTR Compression):** In `KC_BALANCED_LEA_75`, pooled K–12 PTR compressed downward from **$14.85:1$ to $13.55:1$** ($-1.30$ students/FTE, **$-8.75\%$**).
- **`CLM-PTR-001-DYN` (Dynamic Regional Pooled PTR):** Across dynamic regional boundaries, pooled PTR compressed from **$14.85:1$ to $13.54:1$** ($-1.31$ students/FTE, **$-8.82\%$**).
- **`CLM-PTR-002` (Declining District Staffing Stickiness PTR Impact):** Across 28 declining LEAs with unchanged school counts, PTR compressed from **$14.02:1$ to $13.34:1$** ($-0.68$, **$-4.85\%$**), directly demonstrating that fixed plant stickiness reduces student-teacher ratios.
- **`CLM-PTR-003` (Campus vs. LEA Pooled PTR Gap):** In SY 2024–25 across 77 regional LEAs (`KC_FULLY_REGIONAL_CURRENT_77`), district pooled PTR ($13.57$) was **$0.24$ lower ($-1.74\%$ relative to campus)** than campus-aggregate PTR ($13.81$).

---

## 5. Core Semantic & Methodological Boundaries

Future analyses must respect the following verified methodological rules:

1. **PTR is Teacher Staffing Density, NOT Class Size:** A ratio of 14:1 does not mean classes have 14 students. Secondary core class sizes exceed macro PTR due to bell schedules, planning periods, specialist staff, and course allocation hierarchies.
2. **CRDC Course Mean $\ne$ Section Size:** OCR CRDC reports course enrollment and class counts. Their quotient ($\text{enrollment} / \text{classes}$) yields derived school-course mean section size (`EDU-012`), not student-level exposure or roster records.
3. **Missing / Non-Reporting is NOT Zero:** When an agency omits reporting (e.g., Kansas CCD 2015–16 omitting Olathe and Gardner Edgerton teacher counts, $-2,311$ FTE), it represents federal non-reporting, not workforce contraction. Zeroes and omissions must never be conflated.
4. **LEA Totals and Campus Sums are Distinct Operationalizations:** LEA reporting includes centralized administrative, itinerant, and pre-kindergarten staff who do not head a permanent campus classroom roster.
5. **Dynamic vs. Balanced Universes Answer Different Questions:** Balanced cohorts (`KC_BALANCED_LEA_75`) measure longitudinal change holding the agency sample constant. Dynamic panels (`KC_DYNAMIC_REGIONAL_LEA`) measure contemporaneous systemic capacity including charter openings and closures.
6. **Unchanged School Count $\ne$ Identical Physical Plant:** A district with 4 operating schools in 2014 and 4 in 2024 has unchanged school count, but may have replaced, rebuilt, or reconfigured physical buildings.
7. **Identical NCESSCH Sets = Institutional Continuity Sensitivity Only:** Tracking identical 12-digit NCES school IDs proves findings are robust against administrative turnover, but does not assert physical facility tracking.
8. **Geographic Inclusion Uses the 9-County MARC/Study Region:**
   - **Missouri (5 Counties):** Cass, Clay, Jackson, Platte, Ray.
   - **Kansas (4 Counties):** Johnson, Leavenworth, Miami, Wyandotte.
   - Excludes non-regional counties (e.g., Lafayette).
9. **KCPS + Jackson Charters $\ne$ KCPS Attendance Boundary:** The combined Jackson County public sector includes charter LEAs located in Jackson County, which draws heavily from KCPS geography but does not perfectly map to attendance zones.
10. **Personnel Roles Remain Unresolved Pending Microdata:** While central-office and itinerant teachers are candidate mechanisms for district-campus gaps, personnel role composition cannot be asserted without state-level personnel microdata (e.g., KSDE KPTEN).
11. **Active School Implementation Rule:** Active school universe filtering must strictly use `is_operating == True` rather than raw integer status `operational_status == 1`.

---

## 6. Upstream Data Architecture & Dependencies

The Observatory does **not** store duplicate gigabytes of raw federal and state survey extracts. It consumes validated upstream data panels from its sibling project:

```text
../2026-09-23-kc-education-capacity/data/processed/
```

All ingested panels are cryptographically locked in [`data/upstream_artifacts.csv`](data/upstream_artifacts.csv):

| Artifact ID | Relative Path | Producing Script | SHA-256 Checksum Verified |
| :--- | :--- | :--- | :--- |
| `kc_school_capacity_long_2014_15_2024_25` | `data/processed/kc_school_capacity_long_2014_15_2024_25.csv` | `02_build_longitudinal_capacity_panel.py` | Yes |
| `kc_lea_capacity_long_2014_15_2024_25` | `data/processed/kc_lea_capacity_long_2014_15_2024_25.csv` | `02_build_longitudinal_capacity_panel.py` | Yes |
| `kc_crdc_school_course_capacity_2013_14_2023_24` | `data/processed/kc_crdc_school_course_capacity_2013_14_2023_24.csv` | `05_build_crdc_course_capacity_panel.py` | Yes |
| `kc_elementary_class_size_imputed_2023_24` | `data/processed/kc_elementary_class_size_imputed_2023_24.csv` | `04_estimate_school_level_class_sizes.py` | Yes |
| `kc_secondary_class_size_imputed_2023_24` | `data/processed/kc_secondary_class_size_imputed_2023_24.csv` | `04_estimate_school_level_class_sizes.py` | Yes |
| `kc_capacity_synthesis_2024_25` | `data/processed/kc_capacity_synthesis_2024_25.csv` | `06_synthesize_school_capacity_profile.py` | Yes |

---

## 7. Reproduction & Repository Health Check

To verify repository integrity from a fresh terminal or environment, execute the following 8-step procedure:

```bash
# 1. Ensure you are on main and up to date
git checkout main
git pull origin main

# 2. Review registry files
cat registry/measures.csv
cat registry/universes.csv

# 3. Review machine-readable claims ledger
cat analysis/results/claims.csv

# 4. Regenerate claims ledger directly from data
python scripts/generate_claims_ledger.py

# 5. Execute full repository validation suite (all 21 named tests)
python scripts/validate_observatory.py
```

Expected output:
```text
================================================================================
VALIDATION SUMMARY
================================================================================
Named Tests Evaluated: 21
Tests Passed:          21 / 21
Tests Failed:          0 / 21
Warnings Recorded:     0

All 21 / 21 named validation tests PASSED successfully! Observatory is healthy.
```

> [!CAUTION]
> If any test fails or outputs a warning, **do not proceed** with substantive research. Repair repository integrity first.

---

## 8. Frozen-Measure Reopening Rule

To preserve research integrity and prevent knowledge drift, **`EDU-001`**, **`EDU-002`**, and **`EDU-003`** are permanently frozen.

Future researchers and AI agents must **never** reopen a frozen measure merely because a different aggregation method or cohort definition yields a different number. If a new research question requires a different estimand, register a **new Universe**, define a **new Estimand**, and register a **new Claim**.

Frozen measures may be reopened **only** if one of five strict criteria is demonstrated:
1. **Source / Provenance Error:** An upstream raw data extraction contains corrupted or truncated rows.
2. **Non-Reproducible Calculation:** A reported number cannot be reproduced by executing its registered script against the verified upstream panel.
3. **Misunderstood Source Field:** Documentation reveals an agency reporting definition was fundamentally misunderstood.
4. **Incorrect Universe Implementation:** An analysis script filtered entities inconsistently with the registered universe inclusion rules.
5. **Direct Empirical Contradiction:** New, higher-quality primary microdata directly contradicts a frozen factual claim.

---

## 9. Future Resume Options (Milestone 2)

When the Observatory resumes, candidate next measures include:

1. **[`EDU-005 Paraprofessional FTE`](registry/measures.csv):** The immediate planned next measure. Investigates the massive $+11.85\%$ provisional expansion of instructional aides and its role in modern classroom capacity.
2. **[`EDU-004 State Classroom Teacher FTE`](registry/measures.csv):** Disaggregating general classroom teachers from specialists using state registers (e.g., KSDE KPTEN).
3. **[`EDU-007 Teacher-Reported Average Class Size`](registry/measures.csv):** Benchmark against federal NCES NTPS survey distributions.
4. **[`EDU-008`–`EDU-010` Student Complexity Measures:](registry/measures.csv)** Formalizing IEP special education, Section 504 accommodation load, and English Learner density.
5. **[`EDU-011` & `EDU-012` Course Count & Course Mean Class Size:](registry/measures.csv)** Full cataloging of CRDC secondary offerings and roster means.
6. **[`EDU-013` & `EDU-014` True Section & Exposure Metrics:](registry/measures.csv)** Student-weighted classroom exposure when scheduling microdata becomes available.
7. **[`EDU-017 Operational Expenditures per Pupil`:](registry/measures.csv)** NCES CCD Fiscal survey integration.
