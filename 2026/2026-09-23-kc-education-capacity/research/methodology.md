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
   * Integrate school-level teacher FTE, student enrollment, student/teacher ratios, SPED/ELL counts, and economic disadvantage indicators.
3. **Phase 3: Longitudinal Capacity Panel (10-Year Trend)**
   * Assemble a 10-year panel (2014–15 through latest complete year) to evaluate trajectories of staffing and student support demands.
4. **Phase 4: Section-Level Class Size Analysis**
   * Merge state-level assignment collections (DESE MOSIS Course & Student Assignment records; KSDE open-enrollment capacity and section files) to reconstruct actual classroom distributions.
