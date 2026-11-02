# Education Data Observatory — Methodological Decision Log

This document records the foundational methodological and architectural decisions established during Milestone 1 (September 2026). Each entry documents the rationale, the alternative rejected, and the rule enforced across the repository.

---

### [2026-09-26] DEC-001: 9-County MARC Regional Geography Standard
- **Context:** Initial exploratory drafts referenced the official federal 14-county Kansas City Metropolitan Statistical Area (MSA) or included peripheral counties such as Lafayette.
- **Decision:** The canonical geographic study boundary is strictly defined as the **9-county Mid-America Regional Council (MARC) study region**:
  - **Missouri (5 Counties):** Cass, Clay, Jackson, Platte, Ray.
  - **Kansas (4 Counties):** Johnson, Leavenworth, Miami, Wyandotte.
- **Rationale:** Outer non-core counties (e.g., Lafayette, Clinton, Caldwell, Ray outlying rural fragments) have distinct institutional, fiscal, and transportation dynamics. Restricting to the 9-county regional planning footprint ensures comparability with regional civic planning and avoids administrative distortion.
- **Enforcement:** Enforced in [`registry/universes.csv`](registry/universes.csv) across all `KC_*` regional universes.

---

### [2026-09-26] DEC-002: Seven-Layer Epistemic Separation
- **Context:** Earlier exploratory iterations routinely collapsed fields, measures, and aggregations into ad-hoc calculations, causing frequent metric conflation.
- **Decision:** All measurement operations must adhere to a strict linear seven-layer pipeline:
  $$\text{SOURCE} \longrightarrow \text{FIELD} \longrightarrow \text{OPERATIONALIZATION} \longrightarrow \text{MEASURE} \longrightarrow \text{UNIVERSE} \longrightarrow \text{ESTIMAND} \longrightarrow \text{CLAIM}$$
- **Rationale:** Conflating operationalizations (e.g., campus vs. LEA reports) or estimands (e.g., pooled vs. unweighted mean) destroys comparability. Decoupling these concepts makes every link auditable.
- **Enforcement:** Enforced by [`registry/measures.csv`](registry/measures.csv), [`registry/operationalizations.csv`](registry/operationalizations.csv), [`registry/universes.csv`](registry/universes.csv), and [`analysis/results/claims.csv`](analysis/results/claims.csv).

---

### [2026-09-26] DEC-003: Dynamic vs. Balanced LEA Universe Separation
- **Context:** Measuring 10-year change across districts with entry and exit (e.g., charter schools opening or closing) produced conflicting baseline and endpoint totals depending on whether closed agencies were dropped.
- **Decision:** Formalize two distinct, mutually exclusive regional longitudinal universes:
  1. **`KC_BALANCED_LEA_75` (Balanced 75 LEA Cohort):** Continuously operating public LEAs present in both 2014–15 and 2024–25 endpoint files ($N=75$). Used exclusively for fixed-sample 10-year growth and capacity trends.
  2. **`KC_DYNAMIC_REGIONAL_LEA` (Dynamic Contemporary Panel):** All operating public LEAs in each respective school year ($N=78 \to 77$). Used for contemporaneous total system capacity.
- **Rationale:** Mixing dynamic entry/exit into longitudinal cohort analysis creates survivor bias or phantom growth. Separating them clarifies what each trend measures.
- **Enforcement:** Enforced in [`registry/universes.csv`](registry/universes.csv) and audited in [`scripts/validate_observatory.py`](scripts/validate_observatory.py).

---

### [2026-09-26] DEC-004: Missing / Non-Reporting $\ne$ Zero
- **Context:** In SY 2015–16, Kansas state reporting omitted teacher records for Olathe and Gardner Edgerton from federal CCD files, causing an apparent $-2,311$ FTE drop. Early drafts mischaracterized this as an abrupt workforce contraction.
- **Decision:** Negative missing codes (`-1`, `-2`, `-9`), omissions, and non-reporting must never be coerced to zero or treated as real institutional shrinkage.
- **Rationale:** Administrative non-reporting is an artifact of survey transmission, not a behavioral labor market shock. Treating missing data as zero produces severe mathematical errors.
- **Enforcement:** Audited in [`measures/EDU-003-total-teacher-fte/README.md`](measures/EDU-003-total-teacher-fte/README.md) and handled with illustrative linear interpolation in macro visuals.

---

### [2026-09-26] DEC-005: Campus vs. LEA Operationalization Distinction
- **Context:** Aggregating school building records yielded different enrollment and teacher counts than district LEA files, leading to confusion over "unassigned" students or staff.
- **Decision:** Campus building rosters and district LEA files are treated as distinct operationalizations.
  - In enrollment (`EDU-002`), the $+1,472$ student gap is documented as central/shared-time program reporting, not missing students.
  - In teachers (`EDU-003`), district totals exceed campus sums because LEAs employ central-office directors, coordinators, and itinerant personnel.
  - In PTR (`EDU-001`), LEA pooled PTR is $0.24$ lower than campus PTR ($-1.74\%$) primarily because the teacher denominator expands ($+518.49$ FTE) by a larger factor than student enrollment ($+1,472$).
- **Rationale:** Neither level is "wrong"; they measure different organizational administrative scopes.
- **Enforcement:** Codified as explicit claims (`CLM-ENR-002`, `CLM-TCH-003-KS`, `CLM-PTR-003`).

---

### [2026-09-26] DEC-006: Four Distinct Estimands for Ratio Aggregation
- **Context:** Early PTR discussions treated "the district PTR" as a single scalar, obscuring substantial building-level variation.
- **Decision:** Every aggregate ratio must specify its estimand:
  1. **Pooled (Aggregate) PTR:** $\sum E / \sum T$ (teacher-FTE-weighted mean).
  2. **Unweighted Mean Campus PTR:** $\frac{1}{N} \sum (E_i / T_i)$ (typical building environment).
  3. **Median Campus PTR:** 50th percentile of campus distribution (robust middle institution).
  4. **Student-Weighted PTR Exposure:** $\sum (E_i^2 / T_i) / \sum E_i$ (experience of an average student).
- **Rationale:** These four statistics answer fundamentally different questions. In Kansas City regular schools, Pooled PTR is $13.72$, Mean is $13.36$, Median is $13.30$, and Student-Weighted Exposure is $13.82$.
- **Enforcement:** Codified in Section 2.3 of [`measures/EDU-001-pupil-teacher-ratio/README.md`](measures/EDU-001-pupil-teacher-ratio/README.md).

---

### [2026-09-26] DEC-007: CRDC Course Mean $\ne$ Individual Section Size
- **Context:** Civil Rights Data Collection (CRDC) course counts were initially cited as if they reported individual classroom section sizes.
- **Decision:** CRDC data yields derived school-course mean section size (`EDU-012` = course enrollment / course section count), not a roster-level microdata distribution (`EDU-013`).
- **Rationale:** CRDC does not report individual section variance within a building. A derived mean of 25.7 Algebra I students could reflect three sections of 25, 26, 26, or two of 35 and one of 7.
- **Enforcement:** Codified in [`registry/measures.csv`](registry/measures.csv) and [`measures/EDU-001-pupil-teacher-ratio/README.md`](measures/EDU-001-pupil-teacher-ratio/README.md).

---

### [2026-09-26] DEC-008: Canonical Active-School Implementation Rule (`is_operating == True`)
- **Context:** Analysis code originally filtered operating schools using `operational_status == 1`, whereas the universe registry defined inclusion as `is_operating == True`. While numerically equivalent in SY 2024–25 (due to missing FTE in the single status-3 school), this created a software-contract mismatch.
- **Decision:** All analysis scripts and claim generators must use the canonical boolean flag `is_operating == True` (which correctly encompasses new, added, reopened, and changed-agency schools) rather than raw integer status codes.
- **Rationale:** Strict adherence to registered universe contracts prevents silent behavioral divergences when panels update.
- **Enforcement:** Enforced by Named Test 21 in [`scripts/validate_observatory.py`](scripts/validate_observatory.py).

---

### [2026-09-26] DEC-009: Unchanged School Count $\ne$ Physical Plant Identity
- **Context:** An earlier research memo asserted that 28 declining districts had "100% frozen physical plant" because their operating school count was unchanged over 10 years (132 schools).
- **Decision:** An unchanged operating school count must never be conflated with unchanged physical capital.
- **Rationale:** Administrative school count is an organizational metric, not a physical building inventory. A district with 4 operating schools in 2014 and 4 in 2024 may have rebuilt, expanded, closed, or consolidated physical facilities while maintaining 4 organizational school records.
- **Enforcement:** Replaced overclaims with precise organizational capacity terminology (`KC_DECLINING_UNCHANGED_COUNT_28`).

---

### [2026-09-26] DEC-010: Identical NCESSCH Sets = Institutional Continuity Sensitivity Only
- **Context:** To evaluate downward staffing stickiness, a subset of 25 LEAs was identified where 100% of 12-digit NCES school IDs matched between 2014–15 and 2024–25.
- **Decision:** This cohort (`KC_DECLINING_IDENTICAL_IDS_25`) is strictly defined as an institutional continuity sensitivity test, not physical plant tracking.
- **Rationale:** NCES school IDs track administrative institutions, not real estate deeds. Showing that staffing stickiness holds across identical ID sets proves the finding is not an artifact of administrative school ID reconfiguration turnover.
- **Enforcement:** Documented in [`registry/universes.csv`](registry/universes.csv) and Claim `CLM-TCH-002-SENS`.

---

### [2026-09-26] DEC-011: Separation of `support_n` from Universe `entity_count`
- **Context:** Early claim records forced `support_n` to equal the universe entity count, causing errors when valid analytic subsets (e.g., 101 high schools with valid Algebra I and PTR out of 109 total regular high schools) were evaluated.
- **Decision:** A claim's `support_n` represents the count of entities with valid, non-missing data contributing to that specific estimand, bounded by `entity_count` ($\text{support\_n} \le \text{entity\_count}$).
- **Rationale:** High-level universe counts define the population boundary; actual estimands frequently require valid joint reporting across multiple fields.
- **Enforcement:** Enforced by Named Test 15 in [`scripts/validate_observatory.py`](scripts/validate_observatory.py).

---

### [2026-09-26] DEC-012: Explicit `percent_basis` Column in Claims Ledger
- **Context:** Different claims used different percentage calculation bases (start value for longitudinal growth; end value for cross-sectional reconciliation gaps; not applicable for physical distances). This caused arithmetic validation ambiguities.
- **Decision:** Every claim in [`analysis/results/claims.csv`](analysis/results/claims.csv) must explicitly register its `percent_basis` (`start_value`, `end_value`, or `not_applicable`).
- **Rationale:** Making the mathematical denominator explicit eliminates ambiguity and enables strict automated arithmetic auditing.
- **Enforcement:** Enforced by Named Test 14 in [`scripts/validate_observatory.py`](scripts/validate_observatory.py).

---

### [2026-09-26] DEC-013: Generated Claims Ledger Owns Numeric Quantities
- **Context:** Previous phases suffered from "narrative drift," where summary reports, memos, and dossiers quoted slightly different figures than the underlying data.
- **Decision:** Structured numeric columns in [`analysis/results/claims.csv`](analysis/results/claims.csv) own all empirical values. Claim `notes` must not duplicate percentages or raw figures, and prose reports cannot override the ledger.
- **Rationale:** Machine-readable ledgers generated directly by code eliminate manual typographical errors and narrative drift.
- **Enforcement:** Enforced by Named Tests 13, 14, 16, and 18 in [`scripts/validate_observatory.py`](scripts/validate_observatory.py).

---

### [2026-09-26] DEC-014: Source Mechanism Hypotheses Remain Candidates Pending Microdata
- **Context:** Initial drafts asserted as established fact that campus/LEA staffing differences were caused by central-office coordinators and itinerant specialists.
- **Decision:** Unverified personnel mechanisms must be explicitly labeled as candidate hypotheses until role-level state personnel microdata (e.g., KSDE KPTEN, MO DESE Core Data) is linked.
- **Rationale:** Administrative totals prove the existence of an FTE wedge, but cannot prove job classifications without disaggregated job assignment codes.
- **Enforcement:** Codified across dossiers and claims ledger notes.

---

### [2026-09-26] DEC-015: Frozen-Measure Reopening Rule
- **Context:** Re-opening audited measures whenever a minor question arose created perpetual review cycles and instability in downstream dependencies.
- **Decision:** Audited measures (`EDU-001`, `EDU-002`, `EDU-003`) are permanently frozen. New findings must be registered as new universes, estimands, or claims. Reopening a frozen measure requires demonstrating:
  1. A source/provenance data corruption error.
  2. A non-reproducible calculation.
  3. A misunderstood source reporting definition.
  4. An incorrect universe implementation filter.
  5. Direct primary microdata contradiction.
- **Rationale:** A measurement observatory requires stable, immutable foundations to build higher-level relational constructs.
- **Enforcement:** Codified in [`HANDOFF.md`](HANDOFF.md) and [`README.md`](README.md).
