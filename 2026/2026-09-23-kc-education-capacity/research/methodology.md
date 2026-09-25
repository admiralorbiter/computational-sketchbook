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
   * **Task 003A & 003A.1: Construction, Exception Remediation & Audit Foundation (11 School Years, 10-Year Interval):**
     * Assemble 11 annual school years spanning the decade from 2014–15 through 2024–25.
     * **Primary Panel (Repeated Cross-Sections):** Independently reconstruct the 9-county KC geographic universe in each school year based on active physical building coordinates and county FIPS codes (`kc_school_capacity_long_2014_15_2024_25.csv`, 7,384 school-years, 730 unique schools, ranging from 652 schools in 2015–16 to 691 in 2024–25; `kc_lea_capacity_long_2014_15_2024_25.csv`, 881 LEA-years). Avoids conditioning the historical sample on survival into 2024–25 by capturing all campus openings, closures, consolidations, and relocations.
     * **Historical Exception-Code Remediation (Task 003A.1):** Historical wide-format NCES files contain negative numeric exception codes (`-1` Missing, `-2` Not Applicable, `-9` Suppressed). Systematically convert negative codes to `NaN` or explicit Not Applicable representations prior to arithmetic. True reported 0 values remain distinct from administrative missingness. Automated assertions enforce that 0 negative values exist across all numeric variables in all 11 years.
     * **Dual K–12 Teacher Derivation:** Calculate K–12 teacher FTE as `teachers_total_reported_fte - teachers_prek_fte` (with Pre-K treated as 0 if Not Applicable) and audit against component summation (`teachers_k12_fte_components`).
     * **Resolution of 2015–16 Kansas Suppression:** In 2015–16, Olathe (2010140) and Gardner Edgerton (2006420) had staff counts suppressed (`-9.0`) in federal CCD data. Remediated to `NaN`. On reporting Kansas LEAs, the K–12 student/teacher ratio is 15.03 (smooth with 14.88 in 2014–15 and 14.77 in 2016–17), proving the uncorrected 20.02 spike was an artifact of unhandled NCES suppression.
     * **Standardized Reporting Coverage Quality Tiers:** Audit all series across entity counts and student enrollment, classifying coverage into `complete` (100%), `high_coverage` (95–100%), `partial_coverage` (80–95%), and `insufficient_coverage` (< 80%). Kansas 2015–16 is classified as `insufficient_coverage` (75.9% enrollment coverage) and flagged against unadjusted regional aggregation.
     * **Secondary Balanced Panel:** Isolate the 620 schools observed and operating continuously across all 11 school years (`kc_school_balanced_panel_2014_15_2024_25.csv`, 6,820 rows) for sensitivity analysis.
     * **Directory <-> EDGE Audit Protocol:** Audit every state Directory school against federal EDGE geocodes prior to geographic filtering to surface missing coordinates transparently (`outputs/tables/task003a_anomalies.csv`).
     * **Dual Locale Architecture:** Preserve dynamic historical NCES locale classifications active in each school year alongside fixed 2024–25 classifications.
     * **FRL Measurement Guardrail:** Ingest federal lunch counts faithfully without poverty imputation; enforce guardrail against using FRL as a continuous longitudinal poverty proxy.
     * **Zero Hypothesis Testing Certification:** Task 003A/003A.1 is strictly restricted to data construction, remediation, and auditing. No regressions, statistical significance testing, or directional claims of improvement or deterioration are permitted prior to formal review.
   * **Task 003B: Longitudinal Structural Capacity Analysis (Executed & Frozen):**
     * **Core Research Question:** *How has structural staffing capacity changed across the Kansas City region over the past decade (2014–15 through 2024–25)?*
     * **Dual Estimands:** Prioritizes student-weighted structural ratios ($\frac{\sum \text{Enrollment}}{\sum \text{Teacher FTE}}$) for regional and group aggregates, reporting typical-school median and percentiles (p10, p25, p75, p90) separately to reflect campus distributions.
     * **Non-Causal Accounting Decompositions:** Decomposes endpoint ratio shifts into enrollment changes ($\Delta E, \% \Delta E$), teacher FTE changes ($\Delta T, \% \Delta T$), and ratio changes ($\Delta R, \% \Delta R$).
     * **Key Findings:**
       * Regional LEA pupil/teacher ratio contracted from **14.85 to 13.54** ($−1.31$ students/FTE, $−8.8\%$). Typical regular school median ratio contracted from **15.23 to 13.53** ($−1.70$ students/FTE, $−11.2\%$).
       * Regional K–12 enrollment was flat ($−0.73\%$, $−2,345$ students), while K–12 teacher FTE expanded $+8.88\%$ ($+1,921.91$ FTE) and paraprofessionals expanded $+11.85\%$ ($+565.91$ FTE), proving the capacity expansion was driven by active staff additions rather than enrollment decline.
       * School fixed-effects models on the 620-school balanced panel confirm a within-school trajectory of $\beta = -0.1750\text{ students/FTE per year}$ ($p < 0.0001$; 10-year within-school decline of $−1.75$ students/FTE).
       * Grade band divergence: Primary/Elementary schools expanded capacity significantly (within-school $\beta = -0.2154$), whereas High schools saw minimal change ($\beta = -0.0509$).
     * **Strict Methodological Guardrail:** Staffing ratios are never described as class sizes. Hypotheses H1a, H1b, H2, and H3 remain strictly unadjudicated until Phase 4 section roster data are integrated.
4. **Phase 4: The Four-Pillar Measurement Framework (Class Size vs. Structural Staffing)**
   * Resolves the tension between administrative macro-staffing and classroom reality by explicitly maintaining two parallel empirical series across four integrated evidence layers (Decision 036 Remediated):
     - **Pillar 1: Structural Staffing Capacity (NCES CCD & State Registers):** Annual census across all 77 fully regional public LEAs (and 56 eligible longitudinal districts) tracking Students per Teacher FTE and Teachers per 1,000 students. Measures system-level staffing inventory.
     - **Pillar 2: Actual Teacher-Reported Class Size (NCES SASS / NTPS Teacher Questionnaires):** Sampled departmentalized secondary teachers logging section-by-section student headcounts for every section taught (up to 10). Provides weighted survey estimates of average class size reported by representative departmentalized high-school teachers (2011–12 SASS Table 7: US 24.2, MO 21.8, KS 19.7; 2017–18 NTPS Table A-7a: US 23.3, MO 22.5, KS 19.8; 2020–21 NTPS: US 21.0, MO 19.2, KS 17.4).
     - **Pillar 3: Historic Ground-Truth & Daily Student Load (Jenkins v. Missouri Litigation Records):** Master schedule audits, student-classes, teaching assignments, and daily student contact loads ($R_t = \sum_s n_s$). Documents that court-monitored remedial audits in KC looked beyond PTR, finding teaching assignments and daily loads 'more revealing' (*Jenkins v. Missouri*, 639 F. Supp. at 33) and capping daily loads at $\le 125$ students/day (149–154 baseline).
     - **Pillar 4: Modern Course-Level Empirical Proxies (OCR Civil Rights Data Collection):** Course enrollment divided by reported sections ($\bar{s}_c = E_c / S_c$). While regional average regular high school course proxies sit around 16.5–18.7, specific urban and comprehensive suburban campuses report localized gateway bottlenecks of 25–31 students in Algebra I, Geometry, and Biology, which demonstrates how state and metro averages hide localized gateway pressure.
   * **Core Methodological Contrast:** Neither state showed improving all-grade staffing density during the 2011–12 to 2017–18 window (MO PTR 13.8 to 14.1; KS PTR 13.0 to 14.2), while high-school class size also remained roughly stable (MO 21.8 to 22.5; KS 19.7 to 19.8), reinforcing that these are distinct measures rather than demonstrating a staffing/class-size divergence during this particular period. The resulting Class-Size / Macro-PTR Gap (+5 to +8 students) reflects structural secondary bell-schedule planning multipliers ($\phi = P_{\text{std}} / P_{\text{tch}}$) and specialized non-classroom roles.
   * **The Aggregation Guardrail:** Acknowledge that while SASS/NTPS is far more descriptive of classroom reality than PTR, state averages still smooth over the internal distribution (a state average of 19 naturally combines Algebra I at 29 with Calculus at 11). Pillar 4 (CRDC) and Pillar 3 (Jenkins) provide the critical granular distribution that explains where localized gateway pressure concentrates.



