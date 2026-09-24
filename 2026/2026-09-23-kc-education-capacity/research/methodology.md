# Research Methodology: Kansas City Education Capacity Study

## Geographic Boundaries
* **Target Universe:** The 9-county Mid-America Regional Council (MARC) Kansas City metropolitan area.
  * **Missouri (5 Counties):** Jackson, Clay, Platte, Cass, Ray.
  * **Kansas (4 Counties):** Johnson, Wyandotte, Leavenworth, Miami.
* **Inclusion Rule:** Physical school location (building coordinates and county assignment), rather than district administrative headquarters location. This ensures schools operating within the 9-county envelope are captured regardless of cross-boundary district governance.
* **Objective Urbanicity Classification:** Use the NCES 12-category locale classification scheme collapsed into the 4 standardized NCES families:
  * **City:** Large (11), Midsize (12), Small (13)
  * **Suburb:** Large (21), Midsize (22), Small (23)
  * **Town:** Fringe (31), Distant (32), Remote (33)
  * **Rural:** Fringe (41), Distant (42), Remote (43)
* Continuous spatial gradient: Calculate Euclidean and network distance from downtown Kansas City (e.g., City Hall at $39.1027^\circ \text{N}, 94.5779^\circ \text{W}$) to test the "donut" hypothesis without subjective categorization.

## School Population Scope & Classification
* **No silent exclusions:** All public schools reported in official state and federal directories are retained in the master universe file.
* **Typology Flags:**
  * Regular elementary/secondary schools
  * Special education schools
  * Vocational / technical schools
  * Alternative education schools
  * Charter schools (independent LEAs vs. district-sponsored)
  * Virtual / online schools (categorized as exclusively virtual, primarily virtual, or hybrid/none)
* Retaining all facilities with explicit flags enables deliberate analytical filtering (e.g., assessing classroom loads in regular neighborhood schools vs. specialized caseloads) without discarding records prematurely.

## Phased Execution Model
1. **Phase 1 (Task 001): Research Population Universe**
   * Establish the definitive single-year base population of schools across the 9 MARC counties using official NCES CCD and EDGE Geocode files.
   * Generate QA metrics and audit anomalies (virtual schools, county boundary crossings, unassigned locales).
2. **Phase 2 (Task 002 & 002B): Baseline Staffing & Capacity Panel**
   * Establish a rigorous, single-year structural capacity baseline for School Year 2024–2025 across all 691 schools and 79 operating LEAs.
   * **Strict Same-Year Anchoring:** SY 2024–2025 is the anchor. Secondary EDFacts measures not yet publicly released for 2024–2025 (IDEA counts, EL counts, chronic absenteeism) remain explicit `NaN` to prevent silent temporal confounding.
   * **School-Level Capacity Construction:** School staff files report only total classroom teacher FTE without Pre-K separation. Therefore, school-level capacity is strictly calculated as:
     $$\text{students\_per\_classroom\_teacher\_fte\_allgrades} = \frac{\text{enrollment\_total}}{\text{classroom\_teacher\_fte}}$$
     (K–12 enrollment is never divided by total classroom teacher FTE at the school level).
   * **Analytical Stratification:** Partition schools into mutually exclusive analytical strata (`Operating Regular (NCES)`, `Standalone Early Childhood`, `Exclusively Virtual`, `Special Education`, `Alternative`, `Career and Technical`, `Non-Operating`). Explicitly note that `Operating Regular (NCES)` indicates NCES `school_type == 1` and is **not** synonymous with traditional neighborhood schools, as it contains specialized facilities (e.g. DAY TREATMENT, CONTRACT, STAR School, MILLER PARK CENTER).
   * **LEA-Level Clean Matching:** Exploit LEA staff disaggregation to construct clean K–12 metrics excluding Pre-K enrollment and Pre-K teachers:
     $$\text{students\_per\_teacher\_fte\_k12} = \frac{\text{enrollment\_k12}}{\text{teachers\_k12\_fte}}$$
     $$\text{students\_per\_teacher\_para\_fte\_k12} = \frac{\text{enrollment\_k12}}{\text{teachers\_k12\_fte} + \text{paraprofessionals\_fte}}$$
     Compute staffing intensity per 1,000 K–12 students across professional staff categories (teachers, paraprofessionals, counselors, psychologists, coordinators, administrators).
   * **LEA Geographic Coverage Auditing:** Audit all 79 LEAs against the complete national CCD directory to identify cross-boundary operations. Flag LEAs operating schools outside the 9 counties (`lea_fully_within_region == False`, e.g. MO DYS and MSSD) so statewide totals are not confused with Kansas City regional capacity.
   * **Independent Ingestion Replication:** Replicate data ingestion against the Urban Institute Education Data Portal API across 10 sample districts representing core urban, suburban, exurban, and rural archetypes. Replicates parsing, aggregation, and arithmetic against identical federal CCD collections without claiming independent confirmation of underlying CCD accuracy.
   * **Socioeconomic Missingness Warning:** Free and reduced-price lunch eligibility (FS033) is missing for 37 operating schools in a non-random pattern concentrated in shared-time CTE, virtual, and day-treatment programs. `frl_rate` must not be treated as a universal socioeconomic control without accounting for reporting missingness.
   * **Methodological Guardrails:** Capacity ratios measure structural staffing resources per pupil; they are **never** treated as observable class sizes.
3. **Phase 3: Longitudinal Capacity Panel (Task 003A & 003B)**
   * **Task 003A: Construction & Audit Foundation (11 School Years, 10-Year Interval):**
     * Assemble 11 annual school years spanning the decade from 2014–15 through 2024–25.
     * **Primary Panel (Repeated Cross-Sections):** Independently reconstruct the 9-county KC geographic universe in each school year based on active physical building coordinates and county FIPS codes (`kc_school_capacity_long_2014_15_2024_25.csv`, 7,384 school-years, 730 unique schools; `kc_lea_capacity_long_2014_15_2024_25.csv`, 881 LEA-years). Prevents current-cohort survivorship bias by capturing all campus openings, closures, consolidations, and relocations.
     * **Secondary Balanced Panel:** Isolate the 620 schools observed and operating continuously across all 11 school years (`kc_school_balanced_panel_2014_15_2024_25.csv`, 6,820 rows). Serves strictly as a sensitivity control to differentiate within-campus staffing adjustments from geographic/portfolio turnover.
     * **Directory <-> EDGE Audit Protocol:** Audit every state Directory school against federal EDGE geocodes prior to geographic filtering to surface missing coordinates transparently (`outputs/tables/task003a_anomalies.csv`).
     * **Dual Locale Architecture:** Preserve dynamic historical NCES locale classifications active in each school year (`locale_code_year`, `locale_group_year`) alongside fixed 2024–25 classifications (`locale_code_fixed_2024_2025`, `locale_group_fixed_2024_2025`) to test sensitivity against Decennial Census boundary revisions.
     * **FRL Measurement Guardrail:** Ingest federal lunch counts faithfully without poverty imputation; strictly enforce that FRL cannot serve as a continuous longitudinal poverty proxy due to the 2016–17 federal reporting shift and CEP expansion.
     * **Zero Hypothesis Testing Certification:** Task 003A is strictly restricted to data construction and auditing. No regressions, statistical significance testing, or directional claims of improvement or deterioration are permitted prior to formal review.
   * **Task 003B: Longitudinal Hypothesis & Trend Analysis:**
     * Evaluate decade-long trends in student-to-teacher capacity across urban, suburban, and rural strata using both repeated cross-sections and balanced panel specifications.
4. **Phase 4: Section-Level Class Size Analysis**
   * Merge state-level course assignment collections (DESE MOSIS Course & Student Assignment records; KSDE open-enrollment capacity and section files) to reconstruct actual classroom section distributions and evaluate the gap between structural capacity ratios and true class sizes.

