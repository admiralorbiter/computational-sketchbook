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

### Decision 010: Analytical Strata Taxonomy
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Specialized schools (virtual, alternative, special education, standalone Pre-K, CTE) operate under structurally distinct staffing models and caseload constraints compared to traditional neighborhood schools. Mixing them into overall capacity distributions skews baseline statistics.
* **Decision:** Assign every school mutually exclusive analytical strata:
  1. `Non-Operating` (~is_operating)
  2. `Exclusively Virtual` (is_virtual)
  3. `Special Education` (is_special_ed)
  4. `Alternative` (is_alternative)
  5. `Career and Technical` (is_vocational)
  6. `Standalone Early Childhood` (is_standalone_pk)
  7. `Core Operating Regular` (operating regular neighborhood schools)

### Decision 011: Independent Validation via Urban Institute API
* **Status:** Adopted
* **Date:** 2026-09-23
* **Context:** Verifying ingestion pipelines against independent third-party aggregations ensures that raw NCES CCD data parsing, grade rollups, and staff categories match national benchmarks.
* **Decision:** Replicate a 10-district sample representing diverse metropolitan archetypes (Urban Core MO/KS, Large Suburb MO/KS, High-Wealth Suburb, Exurban/Town MO/KS, Outer Rural MO/KS) against the Urban Institute Education Data Portal API. Validate total enrollment, total teacher FTE, Pre-K teacher FTE, and paraprofessional FTE to confirm exact arithmetic consistency.
