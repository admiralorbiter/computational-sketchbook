# Project Decisions Log

## Architecture & Data Governance

### Decision 001: Separation of Raw, Interim, and Processed Data
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Scientific reproducibility requires that raw source files remain immutable.
* **Decision:** All files downloaded directly from NCES, DESE, or KSDE are placed in `data/raw/<source>/` and never altered. Every transformation produces a distinct file in `data/interim/` or `data/processed/`. All source downloads are tracked with SHA256 checksums in `data/manifest.csv`.

### Decision 002: School Physical Location as Inclusion Criterion
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** School district boundaries often cross county borders (e.g., a district headquartered in Jackson County may operate a building across the county line, or a rural district headquartered outside the 9 counties may operate an attendance center inside).
* **Decision:** We use the school building's physical location (county and geographic coordinates from the NCES EDGE Geocode file) for geographic inclusion in the 9-county regional frame. District LEA IDs are retained for hierarchical aggregation.

### Decision 003: Objective Urbanicity via NCES Locales
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Arbitrary labeling of districts as "urban," "suburban," or "rural" introduces researcher bias.
* **Decision:** Urbanicity is strictly derived from the official 12 NCES locale codes, aggregated into the 4 standard families (`City`, `Suburb`, `Town`, `Rural`). Continuous spatial distance from downtown Kansas City ($39.1027^\circ \text{N}, -94.5779^\circ \text{W}$) will be retained as an orthogonal continuous variable.

### Decision 004: Preservation of Specialized and Virtual Schools
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Virtual, alternative, and special education schools have unique enrollment and staffing structures that can distort regular classroom averages.
* **Decision:** No public schools are discarded from the master population file. Instead, explicit typology and virtual status flags are attached to each record to allow reproducible cohort filtering in downstream analyses.

### Decision 005: School Year & Release Version Selection for Task 001
* **Status:** Adopted (Refined)
* **Date:** 2026-09-23
* **Context:** Selection of the base year requires complete directory, school characteristics, and geographic geocode/locale files. Accurate release provenance must be documented.
* **Decision:** Selected School Year **2024–2025** using the official **v.1a** release for CCD Directory (`ccd_sch_029_2425_w_1a_073025.zip`) and CCD School Characteristics (`ccd_sch_129_2425_w_1a_073025.zip`), joined with the 2024–2025 NCES EDGE Geocode dataset (`EDGE_GEOCODE_PUBLICSCH_2425.zip`). The subsequent year 2025–2026 is excluded as it is an incomplete preliminary directory release (v.0a) lacking characteristics, membership, and spatial geocodes.

### Decision 006: Operational Status Logic & Active Cohort Definitions
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** NCES operational status (`SY_STATUS`) classifies schools as Open (1), Closed (2), New (3), Added (4), Changed Boundary (5), Inactive (6), Future (7), or Reopened (8). Treating only status 1 as "open" incorrectly groups newly opened schools (status 3) with closed or future facilities.
* **Decision:** Distinguish two separate operational flags in the processed universe:
  1. `is_operating`: Evaluates to `True` for all schools actively providing instruction in the survey year (status 1 = Open, status 3 = New, status 4 = Added, status 5 = Changed Agency/Boundary, status 8 = Reopened). Evaluates to `False` for status 2 (Closed), status 6 (Inactive), and status 7 (Future).
  2. `is_continuing_school`: Evaluates to `True` strictly for continuing operational facilities (status 1 = Open).

### Decision 007: Anchor Year (SY 2024–2025) and Strict Year Matching
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Federal data releases occur on staggered timelines. In NCES CCD, SY 2024–2025 school membership, LEA membership, school staff (classroom teachers), LEA professional staff, and lunch data are published (v.1a/v.2a), whereas some secondary EDFacts files (IDEA, EL, chronic absenteeism) lag or are pending federal release.
* **Decision:** Establish SY 2024–2025 as the firm anchor year for the baseline capacity panel. Never mix school years within the canonical baseline datasets (`kc_school_capacity_2024_2025.csv` and `kc_lea_capacity_2024_2025.csv`). Variables pending federal release for 2024–2025 remain explicit `NaN`. Any lagged contextual variables (e.g., 2023–2024 chronic absenteeism) are strictly isolated in a separate context file (`data/processed/kc_lagged_context.csv`).

### Decision 008: School-Level Capacity Metric Construction
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** In NCES CCD School Staff (FS059), teachers are reported only as total `TEACHERS` (classroom teacher FTE). Pre-K classroom teachers cannot be separated from K–12 teachers at the school building level. Dividing K–12 enrollment by total classroom teacher FTE would artificially deflate the ratio in schools that offer Pre-K.
* **Decision:** At the school level, the primary structural capacity ratio is strictly defined as matched total membership divided by total classroom teacher FTE:
  $$\text{students\_per\_classroom\_teacher\_fte\_allgrades} = \frac{\text{enrollment\_total}}{\text{classroom\_teacher\_fte}}$$
  Never divide K–12 enrollment by total classroom teacher FTE at the school level. Furthermore, strictly preserve the guardrail that this metric represents a structural capacity ratio, not an observed class size.

### Decision 009: LEA-Level Capacity Ratios and Staffing Disaggregation
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Unlike the school file, the NCES CCD LEA Staff dataset (FS059) reports teachers broken down by level (Pre-K, Kindergarten, Elementary, Secondary, Ungraded) and disaggregates specialized staff (paraprofessionals, counselors, psychologists, coordinators, administrators).
* **Decision:** Construct clean K–12 measures at the LEA level:
  1. $\text{teachers\_k12\_fte} = \text{Kindergarten} + \text{Elementary} + \text{Secondary} + \text{Ungraded Teachers}$ (excluding Pre-K teachers).
  2. $\text{enrollment\_k12} = \text{enrollment\_total} - \text{enrollment\_pk}$.
  3. $\text{students\_per\_teacher\_fte\_k12} = \frac{\text{enrollment\_k12}}{\text{teachers\_k12\_fte}}$.
  4. $\text{students\_per\_teacher\_para\_fte\_k12} = \frac{\text{enrollment\_k12}}{\text{teachers\_k12\_fte} + \text{paraprofessionals\_fte}}$ (explicitly avoiding the overly broad label "instructional adults").
  5. Staffing intensity rates per 1,000 K–12 students for all professional categories.
  6. Never add specialized counts (such as SPED or Title III teachers) to total teacher FTE, as they are non-mutually exclusive subcategories.

### Decision 010: Analytical Strata Taxonomy & Regular School Definition
* **Status:** Adopted (Refined in Task 002B)
* **Date:** 2026-09-23
* **Context:** Specialized schools (virtual, alternative, special education, standalone Pre-K, CTE) operate under structurally distinct staffing models and caseload constraints compared to traditional neighborhood schools. However, NCES `school_type == 1` ("Regular School") is not synonymous with an ordinary neighborhood school—facilities such as DAY TREATMENT, CONTRACT, STAR School, and MILLER PARK CENTER are officially classified as regular schools by NCES despite reporting non-standard staffing structures.
* **Decision:** Assign every school mutually exclusive analytical strata:
  1. `Non-Operating` (~is_operating)
  2. `Exclusively Virtual` (is_virtual)
  3. `Special Education` (is_special_ed)
  4. `Alternative` (is_alternative)
  5. `Career and Technical` (is_vocational)
  6. `Standalone Early Childhood` (is_standalone_pk)
  7. `Operating Regular (NCES)` (operating regular schools per NCES classification)
  Strictly preserve official NCES classifications without ad-hoc name-based reclassification, and refrain from creating subjective "neighborhood school" subsets without independently defensible criteria.

### Decision 011: Independent Ingestion Replication via Urban Institute API
* **Status:** Adopted (Refined in Task 002B)
* **Date:** 2026-09-23
* **Context:** Verifying ingestion pipelines against third-party aggregations ensures that raw NCES CCD parsing, grade rollups, and staff categories match national benchmarks. However, because both pipelines derive from federal CCD submissions, this constitutes ingestion replication rather than independent confirmation of underlying CCD accuracy.
* **Decision:** Replicate a 10-district sample representing diverse metropolitan archetypes against the Urban Institute Education Data Portal API. Validate total enrollment, total teacher FTE, Pre-K teacher FTE, and paraprofessional FTE to confirm arithmetic and parsing consistency.

### Decision 012: LEA Geographic Coverage and Cross-Boundary Agency Accounting
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** The school universe is bounded by physical location within the 9 MARC counties, but federal LEA-level CCD counts encompass entire administrative agencies. Statewide agencies (e.g. MO Division of Youth Services and MO Schools for the Severely Disabled) operate facilities across Missouri, creating large divergences between regional school sums and LEA totals.
* **Decision:** Programmatically determine geographic coverage for all 79 LEAs by checking the complete national CCD directory. Add machine-readable metadata fields (`lea_total_operating_schools_national`, `lea_operating_schools_in_region`, `lea_operating_schools_outside_region`, `lea_geographic_coverage_share`, `lea_fully_within_region`). Flag partial-coverage LEAs in the anomaly ledger and explicitly document that LEA measures for `lea_fully_within_region == False` represent statewide operations rather than Kansas City regional capacity.

### Decision 013: Free and Reduced-Price Lunch Missingness and Socioeconomic Controls
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Free and reduced-price lunch eligibility (FS033) is unobserved for 37 operating schools. Missingness is heavily non-random, concentrating in shared-time vocational centers, virtual schools, and day-treatment or juvenile justice programs.
* **Decision:** Add `frl_observed` boolean flag to the school capacity baseline. Do not impute missing FRL values. Require that `frl_rate` not be treated as a universal socioeconomic control in downstream models without explicit accounting for program delivery missingness.

### Decision 014: Longitudinal Panel Structure and Survivorship Bias Avoidance
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Constructing a historical panel by filtering historical data to current 2024–2025 schools introduces severe survivorship bias by omitting schools that closed, reorganized, or merged during the decade.
* **Decision:** Phase 3 will construct an 11-school-year annual panel spanning the 10-year interval from 2014–15 through 2024–25 by independently reconstructing the KC 9-county geographic universe in each school year as repeated cross-sections. A balanced panel of continuously observed facilities will be generated as a secondary sensitivity check.

### Decision 015: Longitudinal Repeated Cross-Sections Primacy and Avoidance of Current-Cohort Survivorship Bias
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** In educational capacity analysis over a 10-year period, conditioning on survival into 2024–25 introduces substantial bias by ignoring school closures, consolidations, charter turnovers, and suburban boundary shifts.
* **Decision:** Establish `kc_school_capacity_long_2014_15_2024_25.csv` as the primary analytical foundation, built from independent annual cross-sections based on physical school building geocodes within the 9 MARC counties for each year $t \in [2014\text{–}15, \dots, 2024\text{–}25]$. Every school operating in each year is included regardless of subsequent survival or historical existence, avoiding conditioning the historical sample on survival into 2024–25. Annual school counts range from 652 (2015–16) to 691 (2024–25).

### Decision 016: Secondary Balanced Panel Definition and Dual Locale Architecture
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** While repeated cross-sections accurately measure aggregate capacity, distinguishing genuine within-school staffing trends from campus openings and closures requires a balanced panel. Furthermore, NCES locale codes are updated periodically (e.g. following Decennial Census boundary revisions), conflating demographic reclassification with actual urbanization shifts.
* **Decision:** Construct a secondary balanced panel (`kc_school_balanced_panel_2014_15_2024_25.csv`) comprising the 620 schools that were observed and continuously operating in the 9-county region across all 11 school years (`balanced_panel_eligible == True`). Preserve dynamic historical locale codes (`locale_code_year`, `locale_group_year`) alongside fixed 2024–25 locale assignments (`locale_code_fixed_2024_2025`, `locale_group_fixed_2024_2025`) for sensitivity controls. Attach school-level longitudinal transition summary flags (`grade_span_changed_any`, `lea_changed_any`, `school_type_changed_any`, `locale_changed_any`).

### Decision 017: Longitudinal FRL Measurement Guardrail
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** In 2016–17, federal EDFacts reporting transitioned from wide lunch files to long formats, coincident with widespread adoption and expansion of the Community Eligibility Provision (CEP) and direct certification. Raw counts of free and reduced-price lunch eligibility (FRL) exhibit structural breaks across the decade.
* **Decision:** Ingest FRL data faithfully (`frl_eligible`, `frl_rate`, `frl_observed`) without continuous poverty imputation. Enforce a strict methodological guardrail: FRL must NOT be used as a continuous longitudinal poverty proxy across the decade, and downstream trend models must not infer student poverty trajectories from federal lunch eligibility rates without controlling for policy breaks.

### Decision 018: Explicit Directory <-> EDGE Geocode Match Audit Protocol
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Geocoded datasets can silently omit schools present in state administrative directories if physical coordinates are pending or unassigned, leading to invisible attrition.
* **Decision:** Audit every school record in Missouri (29) and Kansas (20) across both the CCD Directory and EDGE Geocode files for all 11 years prior to geographic bounding. Log any school present in Directory but omitted from EDGE (or present in EDGE but omitted from Directory) explicitly in `outputs/tables/task003a_anomalies.csv` to ensure 100% transparency of coverage.

### Decision 019: Systematic NCES Historical Negative Exception-Code Remediation (-1, -2, -9)
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** Historical wide-format NCES CCD files (specifically 2014–15 and 2015–16) utilize negative numeric exception codes to represent administrative data states: `-1` (Missing / Not Reported), `-2` (Not Applicable), and `-9` (Suppressed / Data Withheld to protect confidentiality). Ingesting these values as raw floats without exception parsing corrupts arithmetic operations, leading to negative staff FTEs, distorted ratios, or spurious zeros when filled.
* **Decision:** Systematically convert all negative exception codes in historical raw files to `NaN` or explicit Not Applicable representations prior to arithmetic or derivation. Never allow negative codes to participate in additions, subtractions, aggregations, or denominator construction. Preserve true reported 0 values as distinct from administrative missingness (`NaN`). All negative exception instances are logged in `outputs/tables/task003a_anomalies.csv`. Automated assertions strictly enforce that 0 negative values exist in cleaned analytical columns.

### Decision 020: Dual K–12 Derived Teacher Formula and Pre-K Non-Applicability Handling
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** In historical LEA staff files, summing individual grade-level teacher components (Kindergarten, Elementary, Secondary, Ungraded) is fragile because specific components (e.g. Ungraded Teachers) frequently carry `-2.0` (Not Applicable) or `-1.0` (Missing) codes even when an agency's total teachers and Pre-K teachers are fully reported.
* **Decision:** Adopt `teachers_k12_fte = teachers_total_reported_fte - teachers_prek_fte` as the primary derived measure where both values are valid non-negative numbers. Where Pre-K is Not Applicable (`-2.0`, meaning no Pre-K program operates in the LEA), Pre-K teachers are treated as 0, setting `teachers_k12_fte = teachers_total_reported_fte`. If total teachers or Pre-K teachers are missing or suppressed, `teachers_k12_fte` is set to `NaN`. Simultaneously retain `teachers_k12_fte_components` where all components are valid as an automated QA audit check.

### Decision 021: Standardized Reporting Coverage Quality Tiers
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** Aggregate pupil/teacher ratios can appear distorted if calculated across universes where large agencies have suppressed or missing data, creating severe artificial discontinuities. Downstream longitudinal analyses must know whether an annual aggregate is representative of the metropolitan area or state.
* **Decision:** For every annual school and LEA series, compute reporting coverage across both entity counts and represented student enrollment. Classify reporting coverage into four objective tiers:
  1. `complete`: 100.0% of regional enrollment represented by valid entities.
  2. `high_coverage`: 95.0% to < 100.0% of regional enrollment represented.
  3. `partial_coverage`: 80.0% to < 95.0% of regional enrollment represented.
  4. `insufficient_coverage`: < 80.0% of regional enrollment represented.
Catalog these metrics in `outputs/tables/task003a1_reporting_coverage.csv` and report them in QA documentation. Require that any series in the `insufficient_coverage` tier be flagged and excluded from unadjusted trend regressions.

### Decision 023: Structural Capacity Estimand Protocol (Student-Weighted Aggregates vs. Typical-School Distributions)
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** A fundamental distinction exists between measuring what the overall student population experienced structurally versus what the typical school campus looked like. Averaging entity-level ratios creates severe distortion by weighting a 50-student rural school identically to a 2,500-student comprehensive high school.
* **Decision:** For all regional, state, locale, and grade-band aggregates in Task 003B, adopt the **student-weighted staffing ratio** ($\frac{\sum \text{Enrollment}}{\sum \text{Teacher FTE}}$) as the primary system-level estimand. Never average individual entity ratios to compute a group ratio. Concurrently report the **typical-school distribution** (median, IQR [p25–p75], p10, and p90) as a separate and explicitly labeled metric describing campus-level variation. Apply the same protocol to the combined teacher-plus-paraprofessional ratio ($\frac{\sum \text{Enrollment}}{\sum \text{Teachers} + \sum \text{Paras}}$).

### Decision 024: Non-Causal Accounting Decompositions and Strict Phase 4 Guardrails
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** Understanding decade-long capacity changes requires determining whether declining ratios stem from shrinking student enrollments or expanding teacher headcounts. Furthermore, macro staffing ratios must not be conflated with classroom section sizes.
* **Decision:** Decompose all 10-year endpoint and subperiod staffing ratio shifts into separate non-causal accounting components: enrollment change ($\Delta E$, $\% \Delta E$), teacher FTE change ($\Delta T$, $\% \Delta T$), and ratio change ($\Delta R$, $\% \Delta R$). Establish that over the 2014–15 to 2024–25 period, regional K–12 enrollment was essentially flat ($-0.73\%$), while teacher FTE expanded $+8.88\%$, proving that ratio reductions reflect active staff expansion rather than student depopulation. Strictly forbid describing staffing ratios as class sizes and forbid claiming adjudication of Hypotheses H1a, H1b, H2, or H3, preserving these questions for Phase 4 section-level roster research.

### Decision 025: Insertion of Phase 3C (Staffing Integrity & Allocation Audit) and the Allocation Wedge Framework
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** The Phase 3 macro finding established a substantial structural capacity expansion ($+1,921.91$ LEA teacher FTE, $+8.88\%$; student-weighted PTR falling $14.85 \rightarrow 13.54$). NCES explicitly documents that pupil/teacher ratios include teachers for students with disabilities and other specialized teachers, whereas those teachers are generally excluded from class-size calculations. Moving directly to massive state section requests without validating underlying staffing categories risks confusing administrative reporting artifacts with real instructional allocation shifts.
* **Decision:** Insert **Phase 3C (Staffing Integrity & Allocation Audit)** prior to Phase 4, adopting the following governance protocols:
  1. **Source Reconciliation (Pilot First):** Treat comparisons between NCES CCD and state records (KSDE and MO DESE) as upstream/downstream administrative source reconciliation rather than independent replication. Before any statewide bulk ingestion, execute a targeted **Step 1A Pilot** across 3–4 districts per state (KS: Olathe USD 233, KCKPS USD 500, Blue Valley USD 229, Shawnee Mission USD 512; MO: KCPS 33, North Kansas City 74, Lee's Summit R-VII, Independence 30) for anchor years 2014–15, 2019–20, and 2024–25.
  2. **Decomposition Structure:** In Workstream 2, decompose teacher FTE itself (SPED teachers, resource, intervention, co-teachers) separately from non-teacher support growth (coordinators, counselors, psychologists, support staff), explicitly documenting that non-teacher categories do not explain classroom-teacher FTE growth.
  3. **Deferral of Additive Residuals:** Strictly forbid calculating an additive general-education residual ($\text{Teachers}_{\text{Total}} - \text{Teachers}_{\text{SPED}} - \text{Teachers}_{\text{EL}}$) from broad federal collections because Title III FS067 reports unduplicated teacher headcounts (not FTE) that include content teachers, mixing units and risking double-counting. Retain specialized categories as parallel series until mutually exclusive FTE categories are demonstrated from state assignment microdata.
  4. **Phase 4 Split:** Subdivide Phase 4 into **Phase 4A** (Actual Section & Roster Distributions, Student-Weighted Exposure, Teacher Roster Load, and Allocation Diagnostics) and **Phase 4B** (Classroom Complexity Overlay: IEP, ELL, chronic absenteeism, and student mobility at the section level).





