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

### Decision 026: Phase 3C Sequencing, Kansas Instructional Role Decomposition, and Parallel Phase 4A Section Requests
* **Date:** September 24, 2026
* **Context:** The Step 1A pilot verified close upstream/downstream administrative alignment across 8 benchmark districts (~51% of regional enrollment) across 3 anchor years (2014–15, 2019–20, 2024–25), confirming that federal CCD teacher growth is not a statistical artifact or data fabrication. However, Kansas state reporting reveals an essential structural distinction: KSDE separates *Classroom Teachers* from *Other Teachers (Special Education & Reading Specialists)*, whereas CCD bundles both into total teachers. Reconciling another 50 Missouri LEAs on aggregate numbers offers diminishing returns since MO DESE Screen 18 is the upstream source for federal EDFacts FS059 anyway.
* **Decision:**
  1. **Acknowledge Pilot Empirical Baseline:** Conclude that the macro teacher staffing expansion is real within the state/federal administrative ecosystem. The distortion is primarily one of definition and allocation. Specialized instructional staff are an identifiable component of the denominator; determining whether they are a primary driver requires quantifying how much of the +1,922 FTE expansion occurred in classroom vs. specialized assignments.
  2. **Step 1B-KS Scaling:** Scale Kansas reconciliation and role decomposition across all 21 fully regional Kansas LEAs for 2014–15, 2019–20, and 2024–25:
     $$T_{instructional} = T_{classroom} + T_{other}$$
     $$SpecialistShare = \frac{T_{other}}{T_{classroom} + T_{other}}$$
     $$\Delta T_{instructional} = \Delta T_{classroom} + \Delta T_{other}$$
     Quantify the exact contribution of conventional classroom teachers vs. specialized instructional teachers to total teacher growth.
  3. **Workstream 2 Parallel Metro-Wide Execution:** Compile parallel longitudinal series across all 77 regional LEAs for:
     - IDEA student counts and SPED teacher/para FTE (from EDFacts / IDEA Section 618).
     - Title III EL student counts and instructional staffing.
     - Compute staffing-to-need ratios ($\frac{\text{IDEA Students}}{\text{SPED Teacher FTE}}$, $\frac{\text{SPED Teacher FTE}}{\text{Total Teacher FTE}}$, and decade change in IDEA share vs. SPED staffing share) without manufacturing additive residuals.
  4. **Missouri Pivot:** Deprioritize redundant 56-district aggregate reconciliation; prioritize obtaining detailed Screen 18 duty-code extracts (001–099 splits).
  5. **Immediate Phase 4A Data Request Drafting:** Draft formal research data request specifications for deidentified section-level course assignment extracts from MO DESE (Screen 20 Course Assignment) and KSDE (KEDS/LPR Assignment) in parallel with Phase 3C analysis to avoid project lag.

### Decision 027: The Three-Track Public-Data Ladder, CRDC Course Capacity Panel Harmonization, and the Allocation Wedge Framework
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** Following Phase 3C, which demonstrated that macro teacher staffing expanded primarily in classroom instructional categories and that specialist denominator dilution accounted for only a ~2.7 student-to-teacher difference, the core question shifted to why physical classroom section sizes remain large (24–28+ students) despite falling pupil/teacher ratios. Administrative section-level microdata across two state agencies is fragmented and subject to lengthy governance reviews. To systematically resolve section-level capacity without project stalls, a three-track research ladder was formulated: Track A (Immediate Public Quantitative Data via CRDC and NTPS), Track B (Administrative State & District Section Microdata Requests), and Track C (Independent Photographic Sampling / Elementary Yearbooks).
* **Decision:** Execute Track A immediately and establish the following empirical protocols:
  1. **Six-Wave CRDC Panel Construction:** Ingest, clean, and harmonize all six public biennial waves of the Civil Rights Data Collection (CRDC): 2013–14, 2015–16, 2017–18, 2020–21, 2021–22, and 2023–24. Reconstruct 12-digit NCES school identifiers from `LEAID.zfill(7) + SCHID.zfill(5)` to prevent truncation or scientific notation corruption caused by OCR's Excel export layouts.
  2. **Reserve Code Exception Sanitization:** Enforce strict conversion of all CRDC negative reserve codes (`-1` Missing, `-2` Not Applicable, `-3` Partial/Suppressed, `-5` Edit Check, `-9` Data Suppressed, `-11` Missing/Reserve, `-12` Not Applicable/Reserve) to `NaN` or unoffered; strictly forbid negative integers from entering arithmetic.
  3. **Section Size Estimators:** For 8 secondary academic disciplines (Algebra I, Geometry, Algebra II, Advanced Math, Calculus, Biology, Chemistry, Physics), define:
     $$\text{Mean Section Size}_{s, c, t} = \frac{\text{Students Enrolled}_{s, c, t}}{\text{Number of Classes}_{s, c, t}}$$
     For aggregate regional/group metrics, compute the student-weighted mean ($\frac{\sum \text{Students}}{\sum \text{Classes}}$) rather than an unweighted average of campus means.
  4. **The Allocation Wedge Formalized:** Quantify the gap between actual course section sizes and reported school-wide pupil/teacher ratio:
     $$\text{Allocation Wedge}_{s, c, t} = \text{Mean Section Size}_{s, c, t} - \text{School Pupil/Teacher Ratio (CCD PTR)}_{s, t}$$
     Empirical results demonstrate an average regional Allocation Wedge of **+3.5 to +4.4 students** in secondary core math and science, expanding to **+7.0 to +11.5 students** on large suburban comprehensive high school campuses.
  5. **Curriculum Hierarchy / Course Dilution Hypothesis:** Differentiate Foundation Core courses (Algebra I/II, Geometry, Biology) from Advanced/Specialized courses (Calculus, Physics, Advanced Math). Confirm that schools allocate certified instructional FTE to small specialized and advanced sections (e.g. Calculus at 5–15 students), which pulls down the aggregate building PTR while leaving foundational core classrooms crowded (24–28+ students).
  6. **External Federal Benchmarking:** Triangulate CRDC findings against the National Teacher and Principal Survey (NTPS) secondary departmentalized class-size surveys (~17.4 KS, ~19.2 MO). The concordance confirms that headline pupil/teacher ratios reflect institutional staffing definitions rather than actual classroom student loads, rejecting claims of administrative data falsification while demonstrating metric distortion.

### Decision 028: CRDC Estimand Correction, Matched Allocation-Wedge Aggregation, and Robustness Protocol (Task 004A.1)
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** Methodological review of the CRDC Courses & Classes collection identified critical estimand, aggregation, and measurement constraints: (1) CRDC data represent school-course aggregated offerings ($\frac{\text{Enrollment}}{\text{Classes}}$), not individual classroom section microdata; (2) pooling PTR across all course records introduced structural weighting bias; (3) the 2013–14 wave was temporally misaligned against 2014–15 CCD PTR; and (4) diagnostic outlier trimming ($< 3$ and $> 55$) required scientific sensitivity testing across unfiltered specifications.
* **Decision:** Adopt the following audited protocols:
  1. **Unit of Analysis & Terminology Discipline:** Rename the long file to `kc_crdc_school_course_aggregates_long_2013_14_2023_24.csv`. Strictly refer to the derived quotient ($\frac{\text{num\_enrolled}}{\text{num\_classes}}$) as **school-course average class size** or **reported students per reported class**. Forbid the terms "actual section size", "section-level distribution", or "median section size" in CRDC analysis.
  2. **Class-Weighted vs. Student-Weighted Distinction:** Rename the aggregation $\frac{\sum \text{Enrollment}}{\sum \text{Classes}}$ to **class-weighted average class size**, explicitly documenting that it weights school offerings by the number of sections. Do not claim true student-weighted exposure ($\frac{\sum n_j^2}{\sum n_j}$), which remains an unobservable microdata estimand reserved for Phase 4A.
  3. **Strict School-to-School Matched PTR Comparators:** Compute the allocation wedge row by row at the school-course level:
     $$W_{s,c,t} = \frac{\text{Enrollment}_{s,c,t}}{\text{Classes}_{s,c,t}} - \text{School PTR}_{s,t}$$
     For aggregate metrics, report both:
     - **School-Unweighted Wedge:** Mean ($\overline{W}$) and Median of $W_{s,c,t}$ across distinct contributing schools.
     - **Matched Class-Weighted Allocation Wedge:**
       $$W_{CW} = \frac{\sum \text{Enrollment}_{s,c,t}}{\sum \text{Classes}_{s,c,t}} - \frac{\sum (\text{School PTR}_{s,t} \cdot \text{Classes}_{s,c,t})}{\sum \text{Classes}_{s,c,t}}$$
     Never compare course averages against an unweighted PTR derived from a different or multi-counted school population.
  4. **Contemporaneous 2013–14 CCD Integration:** Ingest the 2013–14 NCES CCD school directory and staffing panel via Urban Institute API (`kc_ccd_school_capacity_2013_14.csv`), ensuring 100% same-year contemporaneous PTR matching across all six survey waves.
  5. **Four-Specification Sensitivity Framework:** Mandate testing across four explicit specifications: Spec 1 (All Valid Nonnegative), Spec 2 (Operating Regular High Schools), Spec 3 (Spec 2 Excl Virtual/Specialized), and Spec 4 (Spec 3 + Diagnostic Outlier Filter). Empirical testing demonstrates the Allocation Wedge is invariant to filtering: Core Math median wedge is $+2.85$ to $+3.00$ pooled and $+3.8$ to $+5.1$ in SY 2023–24 across all specifications.
  6. **Calibrated Substantive Claims:** 
     - Describe the curriculum pattern as "evidence consistent with a curriculum-allocation mechanism", not proof that small Calculus sections causally produce low school PTR.
     - Distinguish regional course averages (~high teens) from large suburban comprehensive high school averages (regularly 24–28+ students).
     - Characterize NTPS departmentalized benchmarks as broadly consistent sanity boundaries.
  7. **Public-Use Disclosure Caveats:** Flag small-cell observations subject to $\pm 1$ student perturbation (Oak Park Calculus, Blue Valley North Algebra I) as diagnostic leads requiring independent verification via district master schedules or public records responses.

### Decision 029: The Schedule-Adjusted Capacity Model & Student Complexity Architecture (Tasks 004B.1 & 004C.1)
* **Status:** Adopted (Calibrated in Tasks 004B.1 & 004C.1)
* **Date:** 2026-09-24
* **Context:** Following the completion of Task 004A.1, the research strategy was refined: (1) public records requests (Track B) were parked to exhaust all purely public data first; (2) the positive gap between headline PTR (~14–16:1) and observed core class sizes (24–28+) required a rigorous mathematical and organizational explanation rather than attributing it to reporting distortion; and (3) teacher perceptions of severe workload overload required reconciliation with administrative data showing an 8.9% expansion in certified teacher staffing. Initial prototypes overclaimed that schedule arithmetic universally explains 80–95% of the wedge and declared premature hypothesis falsification/validation; Task 004B.1 and 004C.1 calibrate these claims.
* **Decision:** Adopt the following explanatory models and empirical architectures:
  1. **Parking of Track B:** Defer external KORA and Sunshine Law requests completely. Exhaust all public artifacts (schedules, negotiated agreements, state accountability regulations, board documents, CRDC complexity tables, EDFacts, and NTPS) first.
  2. **The Schedule-Adjusted Capacity Identity:** Formalize the mathematical bridge between classroom staffing ratios and section sizes:
     $$\boxed{ \overline{\text{Section Size}} \approx \text{PTR}_{class} \times \left(\frac{P_{\text{student}}}{P_{\text{teacher}}}\right) = \text{PTR}_{class} \times \phi }$$
     Recognize that schedule multipliers are regime-dependent: $\phi \approx 1.167$ for traditional 6-of-7 schedules, $\phi \approx 1.333$ for 6-of-8 alternating block schedules, and $\phi = 1.400$ for 5-of-7 teaching loads. Regional expected class sizes under schedule mechanics alone span an envelope of $[\text{PTR} \times 1.167, \text{PTR} \times 1.400]$.
  3. **Calibrated Multi-Stage Capacity Decomposition:** Decompose the gap between reported building PTR and observed core classroom size into three distinct, additive components without universal regional constants:
     $$\text{Observed Core Size} = \text{Reported PTR} + \Delta_1 (\text{Specialist}) + \Delta_2 (\text{Schedule}) + \Delta_3 (\text{Residual})$$
     On large comprehensive suburban campuses with documented 5-of-7 loads (e.g. Shawnee Mission North, Olathe Northwest), schedule mechanics and specialist allocation explain much of the wedge; regionally, their relative weights vary and remain partially unseparated pending section microdata.
  4. **The Shawnee Mission Quasi-Case Study ('5 of 7' Phasing):** The shift from a 6-of-7 teaching load ($\phi \approx 1.167$) to a 5-of-7 teaching load ($\phi = 1.400$), such as Shawnee Mission's Board-approved transition in January 2020, structurally requires an exact **+20.0% increase in teacher FTE** to maintain identical classroom section sizes ($1.400 / 1.167 = 1.20$). Between 2018–19 and 2022–23, Shawnee Mission high school staffing expanded +10.4% (+48.8 FTE) while core math class sizes held steady at 23–25, empirically demonstrating that staffing was absorbed by bought-back planning time.
  5. **The Compound Workload Conceptual Framework (Task 004C.1):** Treat the compound workload formula strictly as a **conceptual framework** illustrating the non-linear interaction of accommodations, chronic absenteeism, and lost planning, rather than an empirically fitted regression:
     $$\text{Instructional Load}_i = \sum_{j=1}^{K_i} \left[ n_{ij} \cdot \left( 1 + \omega_{\text{acc}} \cdot \text{AccShare}_{ij} + \omega_{\text{abs}} \cdot \text{AbsDrag}_{ij} \right) \right] + \text{Compliance}_i + \text{Coverage}_i - \text{ProtectedPlanning}_i$$
     Data from `kc_school_complexity_panel_2015_2024.csv` confirms:
     - Section 504 accommodation plans surged **+93.5%** (6,552 to 12,676 students; reaching 5–10% of suburban high schools).
     - Total legally mandated accommodations (IDEA + 504) expanded to **16.41%** of all students regionally.
     - Chronic absenteeism surged from **12.90%** (2017–18) to **35.14%** (2020–21) during the pandemic shock, and settled into a persistent post-pandemic plateau at **24.68%** (2021–22) and **24.69%** (2022–23) (+11.8 pp above baseline).
     - Staff vacancies (35% in NCES School Pulse Panel) routinely force teachers to surrender planning periods for substitute coverage.
  6. **Calibrated Hypothesis Status:** Retract declarations of decisive falsification/validation. H1b is not supported by public aggregates but is reserved for section microdata; H2 is meaningfully supported for formal legal accommodations, while the broader workload mechanism remains a conceptual synthesis.

### Decision 030: Grounded 10-District Schedule Regime Panel and Public Elementary Class-Size Adjudication
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** Following the calibration of Tasks 004B.1 and 004C.1, empirical grounding required: (1) constructing an explicit 10-district panel of documented bell schedules, periods, and planning rules across metropolitan Kansas City; and (2) determining whether Kansas state administrative publications directly provide elementary class-size ground truth before considering physical yearbook sampling.
* **Decision:**
  1. **10-District Schedule Regime Panel:** Compile `data/raw/schedules/kc_district_schedule_regimes.csv` across 10 representative LEAs (SMSD, Olathe, Blue Valley, KCKPS, KCPS 33, NKC 74, Lee's Summit R-VII, Basehor-Linwood, Richmond R-XVI, Independence 30) documenting contractual planning provisions (MSIP 6 $\ge 250$ min prep, NEA negotiated agreements) and exact multipliers ($\phi = 1.167, 1.333, 1.400$).
  2. **Public Elementary Class-Size Adjudication:**
     - Review of KSDE Building Report Cards (`ksreportcard.ksde.org`) confirms that Kansas does **not** publish an independent section-level class size dataset for elementary or secondary classrooms; published ratios are pupil-teacher staffing ratios.
     - Review of K.S.A. § 72-3123 open-enrollment capacity filings (SMSD Board Policy JBCD, Blue Valley, Olathe) confirms that districts publish capacity planning targets (typically 18–22:1 in K–2, 22–26:1 in 3–5), but not empirical section roster distributions.
     - Consequently, for elementary classrooms, public state administrative records provide planning guidelines and building PTRs, but do not provide section-by-section roster microdata. Physical yearbook photographic sampling (Track C) remains the only feasible independent physical verification method if elementary section headcounts must be observed directly.

### Decision 031: The Teacher Roster Load Paradigm and Jenkins Historical Integration (Tasks 005A, 005B, 005C)
* **Status:** Adopted (SUPERSEDED IN PART BY DECISION 032)

> [!WARNING] SUPERSEDED IN PART BY DECISION 032
> The provisions of Decision 031 concerning direct NTPS teacher-level roster percentile distributions, the progressive collapsing protocol, and the attribution of reliability flags to NCES Standard 4-2 were formally retracted and superseded by Decision 032 (Task 005B.2). In accordance with scientific reproducibility standards, only verbatim published NCES reference table estimates are retained as Class 1 survey metrics, schedule contact loads are strictly classified as Class 3 derived benchmarks, 2015–16 state-level rows are deleted, and cross-era synthesis is framed as discrete benchmarks rather than a longitudinal trend.
* **Date:** 2026-09-24
* **Context:** Following the completion of Tasks 004A.1, 004B.1, and 004C.1, the project reoriented the core inquiry away from "class size" as a single missing variable and toward **Teacher Roster Load**—how school systems translate certified teacher FTE into daily student assignments. Review of historical federal desegregation litigation in Kansas City (*Jenkins v. Missouri*) revealed that forty years ago, the federal court developed the exact capacity measurement architecture we are building today. Tasks 005A, 005B, and 005C reconstruct this historical record, triangulate against federal survey data (NTPS/SASS), and synthesize a 40-year empirical resolution to the education capacity paradox.
* **Decision:** Adopt the following conceptual framework, evidentiary standards, and empirical findings:
  1. **The Teacher Roster Load Metric:** Define the primary operational metric of secondary teacher instructional capacity as total student-seat assignments across the instructional cycle:
     $$\text{Teacher Active Roster Load} = \sum_{j=1}^K n_j \approx \frac{\text{student-class enrollments}}{\text{full-time teachers}}$$
     Distinguish **Active Roster Load** (unique students the teacher grades, accommodates, and advises across the cycle) from **Daily Contact Load** (students sitting in class on a given day). In 5-of-7 and 6-of-7 regimes, active roster equals daily contact; in alternating 8-block regimes, active roster (147 students) is double daily contact (73.5 students).
  2. **Integration of the Jenkins v. Missouri Judicial Blueprint:**
     - **1985 Remedial Order (639 F. Supp. 19):** Classified as `formal_remedial_finding` based on audited master schedule exhibits (K-56, K-58, K-59). The court demonstrated that headline PTR (22:1) obscured ordinary loads (26.6:1) after separating Chapter I specialists (+4.4-student wedge); counted secondary student-class enrollments (37,457 Jr High, 52,362 Sr High) and sections (1,376 Jr High, 1,824 Sr High); established that daily student load (149–154 students/day) was the operative constraint; and established a binding remedial ceiling of $\le 125$ students per secondary teacher per day.
     - **Appellate Affirmance of Maximums (890 F.2d 65 (8th Cir. 1989)):** The appellate court affirmed the remedial use of maximum class sizes, providing historical precedent for treating the upper tail—not merely averages—as policy-relevant. This provides judicial precedent for taking the overloaded tail seriously, though empirical validation of our modern distribution hypothesis (Hypothesis H3) depends on classroom section distributions.
     - **1997 Unitary Status Decision (959 F. Supp. 1151; aff'd 122 F.3d 588):** Classified as `court_observation_not_finding`. The court observed that low building staffing ratios (8.6–18.4:1) were depressed by non-classroom specialists, while ordinary classrooms remained 22–28 students and middle school teachers routinely taught 6 classes with 135–140 students/day.
     - **The Planning-Time Capacity Mechanism:** In 1985, Judge Clark ordered 54 specialists + 31 teachers + 31 aides explicitly to buy 180 minutes of weekly elementary planning time rather than shrinking homeroom size.
  3. **Direct NTPS Survey Architecture & Progressive Collapsing (Task 005B.1):**
     - NCES NTPS 2020–21 data confirms secondary departmentalized class sizes average **21.0 (US)**, **19.2 (MO)**, and **17.4 (KS)**. Statewide estimates may mask metropolitan and suburban differences where comprehensive high schools operate at **23.5–26.5 students**.
     - Longitudinal stability (24.2 in 2011–12; 26.0 in 2015–16; 23.3 in 2017–18; 21.0 in 2020–21) confirms that secondary class sizes have not secularly ballooned.
     - Enforce the **progressive collapsing protocol** for state-by-subject disaggregation to respect NCES disclosure and reliability standards (Standard 4-2):
       $$\text{State} \times \text{Subject} \longrightarrow \text{State} \times \text{Core Academic} \longrightarrow \text{State Overall} \longrightarrow \text{National Subject-Specific}$$
     - Segregate theoretical normal distribution models as *"Illustrative modeled roster-load probabilities under an IID normal section-size assumption"*, recognizing that section correlation and tracking within teachers alter empirical tails.
  4. **The 40-Year Capacity Synthesis (Task 005C.1):**
     - Structure historical comparisons into three rigorous evidence classes: (1) `Measured / Court-Reported` (1985 Jenkins, NTPS survey distributions); (2) `Court Observation (Not Finding)` (1997 Jenkins); and (3) `Modeled from CRDC Mean x Schedule Load` (modern 6-of-7, 5-of-7, 8-block).
     - Historical complexity indicators for 1985 and 1997 are classified as **'Not comparable / no equivalent measure located'**, recognizing that modern Section 504 accommodation documentation and standardized federal chronic absenteeism definitions did not exist during desegregation litigation.
     - Within the modern era (2015–2024), operational student complexity exploded: Section 504 plans surged +93.5% (reaching 5–10% of high school students), total accommodations reached 16.41%, and chronic absenteeism plateaued at 24.69% (+11.8 pp above baseline).
     - **Calibrated Scientific Conclusion:** *Available evidence does not indicate that secondary roster headcount has increased dramatically over the past four decades; historical KCMSD loads were already very high, and modern schedule-based estimates fall in a similar or lower range. Direct modern teacher-level roster-load estimates remain the key missing public measure.*
     - **Qualitative Story:** The number of students on a teacher's roster may not have exploded. The number of individualized instructional problems a teacher has to solve for those students did. Added staffing bought planning time, while remaining classroom hours face unprecedented compound student complexity.

### Decision 032: NTPS Provenance Audit, Retraction of Unverified Survey Distributions, Cross-Era Benchmark Nomenclature, and the Four-Layer Architecture (Tasks 005B.2 & 005C.2)
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** Methodological and reproducibility review of Task 005B.1 and Task 005C.1 identified two critical scientific integrity requirements:
  1. The repository previously reported teacher-level roster load percentiles (P75, P90, median) and tail probabilities (>125, >140, >150) that were reconstructed or modeled from section means and parametric assumptions rather than directly calculated from an audited NCES DataLab session with replicate weights, unweighted n, and variance matrices. Furthermore, 2015–16 state estimates were presented as representative despite NCES explicitly establishing that the 2015–16 NTPS design was not state-representative.
  2. Synthesizing disparate populations (1985 KCMSD desegregation exhibits, 1997 KCMSD hearing observations, modern statewide survey estimates, KC suburban CRDC course aggregates, and modeled schedule regimes) as a single '40-year longitudinal trend' implied continuous demographic and geographic comparability that the data do not support.
* **Decision:**
  1. **Execute Task 005B.2 (NTPS Provenance Audit & Retractions):**
     - Formally retract and delete all unsupported teacher-level percentile distributions and tail probabilities.
     - Retain exclusively verbatim published NCES quantities from official reference tables (2020–21 NTPS Table 7: US 21.0, KS 17.4, MO 19.2; 2017–18 NTPS Table A-7a: US 23.3, KS 19.8, MO 22.5; 2011–12 SASS Table 69: US 24.2, KS 20.5, MO 23.1).
     - Formally remove 2015–16 Kansas and Missouri state rows, preserving 2015–16 exclusively for national comparisons (First Look Table 8: US 26.0). The modern state survey series is strictly: 2017–18 -> 2020–21.
     - Re-attribute '!' and '‡' reporting flags to official published NTPS Table 7 publication conventions (CV 30–50% for '!'; CV >= 50% or too few cases for '‡'), correcting earlier attribution to NCES Standard 4-2 (which governs confidentiality).
     - Classify all student contact loads under schedules as **Class 3: Derived Schedule Benchmarks** (Published Section Mean x Teaching Periods), not measured survey distributions.
  2. **Refactor Task 005C.2 to 'Cross-Era Capacity Benchmarks, 1985–2024':**
     - Rename product and documentation: **Cross-Era Capacity Benchmarks, 1985–2024**.
     - Formally adopt the mandatory comparability guardrail:
       *'The historical and modern observations differ in geography, school population, measurement system, and evidentiary status; they establish scale and continuity, not a single longitudinal estimate.'*
     - Eliminate pseudo-longitudinal claims (e.g. '40-Year Shift: -15%').
     - Classify historical complexity metrics (1985/1997 Section 504 and chronic absenteeism) strictly as: *'Not comparable / no equivalent measure located'*.
  3. **Establish the Public Data Transparency Boundary:**
     - Explicitly document that public data can rigorously establish structural staffing (+8.86% teacher FTE despite flat enrollment of -0.73% across the 56-district metro panel), specialist allocation (+2.7 ratio point wedge), regional school-course means (high teens) alongside mid-20s averages at selected large comprehensive suburban campuses, bell-schedule regimes (5-of-7 vs. 6-of-7), Section 504 accommodations (+93.5% volume), and chronic absenteeism (24.69% plateau).
     - Acknowledge that public data generally cannot reveal the actual distribution of individual KC classroom rosters or the empirical percentage of teachers carrying >140 students; public state releases do not expose this metric, which requires restricted-use microdata or custom DataLab extraction.
  4. **Adopt the Four-Layer Explanatory Architecture:**
     - Layer 1: Institutional Staffing (Pupil/Teacher Ratio; +8.86% teacher FTE, -0.73% enrollment across 56-district metro panel).
     - Layer 2: Instructional Allocation (Classroom vs. specialized personnel, SPED, reading specialists; 88.9% of net instructional-teacher additions across the 19 Kansas USD panel were general classroom teachers).
     - Layer 3: Teacher Assignment Load (Sections taught x students per section; governed by bell-schedule regimes and contractual planning, with Shawnee Mission demonstrating the FTE-to-planning absorption mechanism).
     - Layer 4: Effective Workload (Available public evidence does not indicate a dramatic increase in secondary roster headcount; modern schedule-based loads fall in a similar or lower range compared to Jenkins, but student complexity has surged with 16.4% carrying legal accommodations and 24.7% chronically absent).
  5. **Freeze Public Data Collection:**
     - Cease further public data collection (Track B Sunshine/KORA parked; no internal PREP-KC district access; no elementary yearbook archaeology; no additional board PDF crawls).
     - Transition to final synthesis paper and project documentation based on the four-layer explanatory model.

### Decision 033: Public Course-Load Scenarios, Gateway Bottlenecks, and the Five-Step Reconstruction Ladder (Task 006.1)
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** Methodological review of Task 006 established that while public CRDC course aggregates and bell-schedule parameters reveal substantial course-level loading wedges above building pupil/teacher ratios, multiplying course averages by an arbitrary number of sections ($D \times \bar{s}$) constructs a modeled scenario load, not an observed individual teacher roster. Furthermore, secondary campuses operate under distinct bell-schedule architectures (e.g., KCKPS 8-period alternating block vs. 7-period days), OCR reporting rules introduce timing mismatches between fall class counts and spring course enrollments, and course loading varies intensely across specific gateway subjects within the same department.
* **Decision:**
  1. **Adopt the Five-Step Reconstruction Ladder:**
     $$\boxed{\text{1. Observed}} \quad (E_c, S_c) \longrightarrow \boxed{\text{2. Derived}} \quad \bar{s}_c = \frac{E_c}{S_c} \longrightarrow \boxed{\text{3. Modeled Scenarios}} \quad R_D = D \cdot \bar{s}_c \longrightarrow \boxed{\text{4. Dept Load (Audit)}} \quad \frac{E_{\text{math}}}{T_{\text{math}}} \longrightarrow \boxed{\text{5. Unobserved}} \quad \text{Individual Rosters}$$
     - Level 1 (Observed): School-course enrollment ($E_c$) and class counts ($S_c$) from federal CRDC.
     - Level 2 (Derived Proxy): CRDC school-course load proxy ($\bar{s}_c = E_c / S_c$), recognized as reported students per reported class, subject to OCR timing mismatches (fall class count around Oct 1 vs. spring enrollment snapshot).
     - Level 3 (Modeled Scenarios): Derived scenario loads under explicit teaching duty assignments (e.g., $R_5 = 5\bar{s}$ and $R_6 = 6\bar{s}$).
     - Level 4 (Department Load Attempted): Ratio of covered course enrollments to public subject teacher counts ($E_{\text{math}} / T_{\text{math}}$), audited in Task 006.2.
     - Level 5 (Unobserved): Individual teacher roster distributions, section-level variance, and tail probabilities ($P(R > 140)$), which strictly require student-level SIS microdata or master schedule section tables.
  2. **Calibrate the Public Data Boundary:**
     - Public data is sufficient to prove that building pupil/teacher ratio (PTR) **can materially understate the load represented by particular courses**.
     - Private data is unnecessary to demonstrate this structural mismatch. However, public aggregates alone do not reveal individual teacher rosters.
  3. **Report Pilot Campuses Individually (No Universal Load Assertion):**
     - **Lincoln College Prep (KCPS):** Building PTR is 17.25:1; core math sections average 29.5 students (Geometry 31.0, Algebra II 30.6). A modeled 5-section core assignment corresponds to 147.4 student seats (+61.1 residual over naive PTR), exceeding the Jenkins 125 ceiling.
     - **Grandview Senior High (Grandview C-4):** Building PTR is 16.99:1; core math sections average 24.0 students (Algebra I 25.8, Geometry 25.9), yielding a modeled 5-section load of 120.1 (+35.2 residual) and 6-section load of 144.2. Advanced Math averages 6.8 students.
     - **Ruskin High School (Hickman Mills C-1):** Building PTR is 12.94:1; core math sections average 21.0 students, yielding a modeled 5-section load of 104.8 (+40.1 residual) and 6-section load of 125.7. Advanced Math averages 4.25 students.
     - **Center Senior High (Center 58):** Building PTR is 12.10:1; core math sections average 16.7 students (Algebra I 19.0), yielding a modeled 5-section load of 83.4 (+22.9 residual).
     - **East High School (KCPS):** Building PTR is 13.85:1; core math sections average 17.1 students, yielding a modeled 5-section load of 85.5 (+16.3 residual).
     - **Wyandotte High School (Kansas City USD 500) — The Gateway Bottleneck:** Overall core math averages 20.19 against a 20.10 PTR (virtually zero aggregate wedge). However, Algebra I specifically contains 46 classes enrolling 1,313 students (average 28.54/class). Under Wyandotte's public 8-period Red/White alternating block ($D = 6$), a teacher assigned 6 sections of Algebra I manages a modeled active grading roster of 171.2 students (+50.6 over naive PTR).
  4. **Adopt Defensible Residual Decomposition Terminology:**
     $$\Delta_{\text{total}} = R_{\text{modeled}} - R_{\text{naive}} = \underbrace{D \cdot (\bar{s}_{\text{dept}} - PTR_{\text{bldg}})}_{\text{Course-vs-PTR Residual}} + \underbrace{D \cdot (\bar{s}_{\text{core}} - \bar{s}_{\text{dept}})}_{\text{Core-vs-Advanced Mix Difference}}$$
     - Avoid attributing $\Delta_{\text{sched}}$ solely to causal scheduling/specialists or $\Delta_{\text{track}}$ solely to tracking.
     - Clarify that guidance counselors are categorized separately in CCD staffing and do not depress the teacher denominator.
     - Clarify that state graduation requirements mandate math and science credit totals with specific EOC assessments, but do not dictate universal grade-level course sequencing.

### Decision 034: Department Reconstruction Feasibility Audit & The Personnel Artifact Boundary (Task 006.2)
* **Status:** Adopted
* **Date:** 2026-09-24
* **Context:** Following Task 006.1, the research team tested whether public records could advance from modeled scenario loads (Step 3) to an observed department-level average student-course load (Step 4: $E_{\text{math}} / T_{\text{math}}$), analogous to the 1985 Jenkins remedial audit metric (student-classes per teacher). The audit evaluated publicly available faculty listings, district directories, and state releases across the six urban pilot high schools.
* **Decision:**
  1. **Acknowledge the Breakdown of Public Department-Level Reconstruction:**
     - The empirical audit demonstrates that department-level teacher load reconstruction is **not reliably feasible from public records today**.
     - Across the six pilot campuses, public personnel directories either:
       a) Do not categorize faculty by subject department (Missouri urban districts list teachers under undifferentiated 'Teacher' classifications);
       b) Shield staff rosters behind automated bot verification (KCPS and Center platforms return HTTP 200 Client Challenges to automated inquiries); or
       c) Exhibit severe temporal, taxonomic, and snapshot disconnects when department rosters are exposed.
  2. **Codify the Wyandotte Staffing Disconnect as an Empirical Boundary Case:**
     - Wyandotte's public directory lists 8 Math Teachers. In 2023–24, CRDC reported 121 math classes and 2,351 enrollments, implying $121 / 8 = 15.1$ classes/teacher and $2,351 / 8 = 293.9$ enrollments/teacher.
     - This disconnect reflects three confounding mechanisms:
       - *Timing & Snapshot Aggregation:* CRDC block-schedule reporting can reflect cumulative fall and spring semester classes (~60 concurrent sections per semester requiring ~10 full-time teachers).
       - *Departmental Classification:* Special education co-teachers, bilingual/ESOL math teachers, and instructional coaches are listed under separate departmental headings.
       - *Temporal & Vacancy Lag:* Current web directories reflect 2024–2026 staffing and omit vacancies, long-term substitutes, or adjuncts present during the 2023–24 collection.
     - Computing $E_{\text{math}} / T_{\text{math}}$ from these public listings produces a spurious artifact rather than a true workload metric.
  3. **Establish the Final Public-to-Restricted Boundary:**
     - Public data capability firmly terminates at **Step 3 (Modeled Course-Load Scenarios)**.
     - Reconstructing true department-level teacher loads ($E_{\text{dept}} / T_{\text{dept}}$), individual teacher rosters, or section-level variance requires restricted-use state personnel databases (e.g. KSDE licensed personnel files with assignment codes; Missouri DESE Core Data Educator files) or district master schedule tables.
  4. **Publish Task 006.2 Deliverables:**
     - Audit data: `outputs/tables/task006_2_department_reconstruction_audit.csv`.
     - Analytical report: `outputs/tables/task006_2_department_reconstruction_audit_report.md`.

