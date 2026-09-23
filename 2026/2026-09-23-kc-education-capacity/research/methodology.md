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
2. **Phase 2 (Task 002): Baseline Staffing & Capacity Panel**
   * Establish a rigorous, single-year structural capacity baseline for School Year 2024–2025 across all 691 schools and 79 operating LEAs.
   * **Strict Same-Year Anchoring:** SY 2024–2025 is the anchor. Secondary EDFacts measures not yet publicly released for 2024–2025 (IDEA counts, EL counts, chronic absenteeism) remain explicit `NaN` to prevent silent temporal confounding.
   * **School-Level Capacity Construction:** School staff files report only total classroom teacher FTE without Pre-K separation. Therefore, school-level capacity is strictly calculated as:
     $$\text{students\_per\_classroom\_teacher\_fte\_allgrades} = \frac{\text{enrollment\_total}}{\text{classroom\_teacher\_fte}}$$
     (K–12 enrollment is never divided by total classroom teacher FTE at the school level).
   * **Analytical Stratification:** Partition schools into mutually exclusive analytical strata (`Core Operating Regular`, `Standalone Early Childhood`, `Exclusively Virtual`, `Special Education`, `Alternative`, `Career and Technical`, `Non-Operating`) so baseline capacity distributions in neighborhood schools are not distorted by specialized programs.
   * **LEA-Level Clean Matching:** Exploit LEA staff disaggregation to construct clean K–12 metrics excluding Pre-K enrollment and Pre-K teachers:
     $$\text{students\_per\_teacher\_fte\_k12} = \frac{\text{enrollment\_k12}}{\text{teachers\_k12\_fte}}$$
     $$\text{students\_per\_teacher\_para\_fte\_k12} = \frac{\text{enrollment\_k12}}{\text{teachers\_k12\_fte} + \text{paraprofessionals\_fte}}$$
     Compute staffing intensity per 1,000 K–12 students across professional staff categories (teachers, paraprofessionals, counselors, psychologists, coordinators, administrators).
   * **Independent Validation:** Replicate data ingestion against the Urban Institute Education Data Portal API across 10 sample districts representing core urban, suburban, exurban, and rural archetypes.
   * **Methodological Guardrails:** Capacity ratios measure structural staffing resources per pupil; they are **never** treated as observable class sizes.
3. **Phase 3: Longitudinal Capacity Panel (10-Year Trend)**
   * Assemble a 10-year panel (2014–15 through 2024–25) to evaluate trajectories of staffing intensity, support staff deployment, and enrollment shifts.
4. **Phase 4: Section-Level Class Size Analysis**
   * Merge state-level course assignment collections (DESE MOSIS Course & Student Assignment records; KSDE open-enrollment capacity and section files) to reconstruct actual classroom section distributions and evaluate the gap between structural capacity ratios and true class sizes.
