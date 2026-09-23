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
