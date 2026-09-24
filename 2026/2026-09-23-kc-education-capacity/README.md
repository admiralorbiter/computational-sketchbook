# Kansas City Education Capacity Study (`kc_education_capacity`)

A quantitative investigation into adult instructional capacity, classroom load, and class-size distributions across the 9-county Kansas City bi-state metropolitan area (MARC region).

---

## Central Question

*What are the constraints on a good education, which ones can schools actually change, and which interventions relieve multiple constraints at once?*

Specifically, is insufficient adult instructional capacity the primary unmodeled constraint driving teacher overload—and are reported headline pupil/teacher ratios actively obscuring actual classroom distributions?

---

## Geographic Universe

The study encompasses the official **9-county Mid-America Regional Council (MARC)** Kansas City region:
* **Missouri (5 Counties):** Jackson, Clay, Platte, Cass, Ray
* **Kansas (4 Counties):** Johnson, Wyandotte, Leavenworth, Miami

Schools are classified by objective NCES standardized locale classifications:
* **City** (Urban Core: KCPS, KCKPS, Center, etc.)
* **Suburb** (Inner and Outer Ring Suburbs: Shawnee Mission, Blue Valley, Olathe, North Kansas City, Lee's Summit, Blue Springs, etc.)
* **Town** (Independent peripheral towns)
* **Rural** (Farmland and exurban communities)

---

## Directory Structure

```text
kc_education_capacity/
├── README.md                 # Project overview and instructions
├── research/                 # Theoretical framework, hypotheses, research questions, dictionary
│   ├── questions.md
│   ├── hypotheses.md
│   ├── methodology.md
│   ├── decisions.md
│   └── data_dictionary.md
├── data/
│   ├── raw/                  # Immutable original downloads
│   │   ├── nces/
│   │   ├── missouri/
│   │   └── kansas/
│   ├── interim/              # Intermediate transformations
│   ├── processed/            # Final analysis datasets
│   └── manifest.csv          # Audit ledger of all external downloads (URLs, dates, SHA256)
├── src/                      # Reproducible pipeline code
│   ├── download/             # Ingestion scripts
│   ├── clean/                # Harmonization and universe construction
│   ├── geography/            # Spatial distance and locale metrics
│   └── analysis/             # Statistical models and simulations
├── notebooks/                # Exploratory computational notebooks
│   ├── 01_geography.ipynb
│   ├── 02_baseline_capacity.ipynb
│   ├── 03_longitudinal.ipynb
│   └── 04_class_size.ipynb
├── outputs/                  # Exported artifacts
│   ├── figures/
│   └── tables/
└── requests/                 # Formal state data request documentation
    ├── missouri/
    └── kansas/
```

---

## Current Status: Phase 3C Complete; Task 004A (CRDC Course Capacity Panel) Complete; Launching Phase 4 Microdata Tracks

- **Task 001 (Geographic Universe):** Complete. 691 schools across 9 MARC counties established, geocoded, and classified using NCES CCD/EDGE SY 2024–2025.
- **Task 002 & 002B (Baseline Staffing & Capacity):** Complete. School- and LEA-level baseline capacity panels constructed (`kc_school_capacity_2024_2025.csv`, `kc_lea_capacity_2024_2025.csv`), with programmatic LEA geographic coverage metadata, `Operating Regular (NCES)` terminology, FRL missingness analysis, independent Urban Institute ingestion replication, and audited anomalies in `outputs/tables/task002_qa_report.md`.
- **Task 003A & 003A.1 (11-Year Longitudinal Data Construction, Exception Remediation & Audit):** Complete.
  - Ingested and cataloged all 99 raw NCES archives spanning 11 school years (2014–15 through 2024–25).
  - Remediated all historical negative NCES exception codes (`-1` Missing, `-2` Not Applicable, `-9` Suppressed) to `NaN` or explicit Not Applicable representations prior to arithmetic.
  - Implemented dual K–12 teacher FTE derivations (`Total - PreK` audited against component summation), setting missing/suppressed measures to `NaN`.
  - Resolved 2015–16 Kansas discontinuity: identified NCES staff suppression in Olathe and Gardner Edgerton; confirmed reporting ratio of 15.03 on valid LEAs, while classifying Kansas 2015–16 as `insufficient_coverage (< 80%)`.
  - Automated integrity assertions verified **0 negative values** across all numeric analytical variables in all 11 years.
  - Automated baseline parity check confirmed **exact 100% parity (0 discrepancies)** with frozen Task 002B baseline for 2024–25.
  - Constructed primary repeated cross-section school panel (`kc_school_capacity_long_2014_15_2024_25.csv`, 7,384 records across 730 unique schools), primary repeated cross-section LEA panel (`kc_lea_capacity_long_2014_15_2024_25.csv`, 881 records), secondary balanced panel (`kc_school_balanced_panel_2014_15_2024_25.csv`, 6,820 records across 620 schools), anomaly ledger (`task003a_anomalies.csv`, 409 entries), and reporting coverage table (`task003a1_reporting_coverage.csv`, 66 rows). Full audit documented in `outputs/tables/task003a_qa_report.md`.
- **Task 003B & 003B.1 (Longitudinal Structural Capacity Analysis & Report Integrity):** Complete (`outputs/tables/task003b_analysis_report.md`).
  - **Empirical Pipeline:** Executed `src/analysis/longitudinal_capacity_analysis.py`, generating 7 audited output CSV tables and 7 publication-quality figures in `outputs/figures/`.
  - **Core Findings:**
    - Regional LEA student-weighted pupil/teacher ratio contracted from **14.85 to 13.54** ($−1.31$ students per teacher FTE, $−8.82\%$). Typical regular school median ratio contracted from **15.23 to 13.53** ($−1.70$ students per teacher FTE, $−11.16\%$).
    - Non-causal decomposition establishes that regional K–12 enrollment was flat ($−0.73\%$, $−2,345$ students), while K–12 teacher FTE expanded $+8.88\%$ ($+1,921.91$ FTE) and paraprofessionals expanded $+11.85\%$ ($+565.91$ FTE), proving the capacity expansion was driven by active staff additions rather than enrollment decline.
    - School fixed-effects models on the 620-school balanced panel confirm a within-school trajectory of $\beta = -0.1750\text{ students/FTE per year}$ ($p < 0.0001$; implied 10-year within-school decline of $−1.75$ students/FTE).
    - Grade band divergence: Primary/Elementary schools expanded capacity significantly (within-school $\beta = -0.2152$), whereas High schools saw minimal change ($\beta = -0.0531$).
    - Missouri and Kansas exhibited near-identical starting levels (14.82 vs 14.88) and parallel decade slopes ($-0.1581$ vs $-0.1623$).
  - **Strict Methodological Guardrail:** Staffing ratios measure macro capacity and are never described as class sizes. Hypotheses H1a, H1b, H2, and H3 remain strictly unadjudicated.
- **Phase 3C (Staffing Metric & Allocation Audit):** Complete.
  - **Step 1A (State Staffing Reconciliation Pilot):** Complete (`outputs/tables/task003c_state_replication_pilot_report.md`). Audited 8 benchmark districts across anchor years (2014–15, 2019–20, 2024–25); 17/24 comparisons within 2%, 23/24 within 5% (median difference 1.47%). Confirmed state administrative systems reproduce the macro teacher expansion and identified Kansas's structural separation of Classroom Teachers vs. Other Teachers (SPED/Reading).
  - **Step 1B-KS (Kansas Role Decomposition across 19 Metropolitan USDs):** Complete (`outputs/tables/task003c_kansas_role_decomposition_report.md`). Quantified the **Specialist Denominator Wedge** at **2.66 to 2.81 students per teacher** between classroom ratios (16.86 -> 16.26) and total instructional ratios (14.05 -> 13.60). Proved that in major Johnson County suburbs, both classroom teachers (+8.7%) and specialized teachers (+21.3%) expanded faster than enrollment (+3.2%). At the 19-USD aggregate, 88.9% of net instructional additions were classroom teachers, demonstrating that specialist dilution alone does not explain why core classes remain large.
  - **Workstream 2 (Parallel Specialized Personnel & Non-Teaching Staff):** Complete across all 77 fully regional LEAs (`outputs/tables/task003c_workstream2_regional_staff_need_report.md`). Tracked parallel series showing paraprofessionals (+11.85%), instructional coordinators (+49.74%), counselors (+18.92%), and administrators (+16.62%) expanded faster than enrollment (-0.73%), separating non-teaching organizational support from the teacher denominator.
- **Task 004A (Civil Rights Data Collection Course Capacity Panel & The Allocation Wedge):** Complete (`outputs/tables/task004_crdc_analysis_report.md`).
  - **Empirical Pipeline:** Executed `src/download/download_historical_crdc.py`, `src/clean/build_crdc_course_panel.py`, and `src/analysis/crdc_capacity_analysis.py` across all 6 public CRDC waves (2013–14, 2015–16, 2017–18, 2020–21, 2021–22, 2023–24). Produced harmonized school panel (3,914 school-years) and long sections panel (31,312 records).
  - **Core Findings & Hypothesis Adjudication:**
    - Directly quantified the **Allocation Wedge** ($\text{Course Mean Class Size} - \text{School PTR}$): regional high school Algebra I (+3.50), Geometry (+4.42), Algebra II (+3.93), and Chemistry (+4.33) substantially exceed building-wide pupil/teacher ratios.
    - Large suburban comprehensive high schools experience a massive wedge of **+7.0 to +11.5 students**: e.g., Shawnee Mission North (Algebra I 25.7 vs 14.2 PTR; Wedge +11.5), Olathe Northwest (Geometry 27.1 vs 16.6 PTR; Wedge +10.5), Olathe North (Algebra II 26.5 vs 14.9 PTR; Wedge +11.6), and Lincoln College Prep (Algebra II 30.6 vs 17.2 PTR; Wedge +13.4).
    - Validated the **Curriculum Hierarchy / Course Dilution Hypothesis**: schools allocate certified teachers to low-enrollment advanced seminars (Calculus mean 16.14, with sections as low as 4.7) and specialized programs, compressing aggregate school PTR while foundation core classrooms remain crowded (24–28+ students).
    - Successfully triangulated against external federal NTPS secondary departmentalized survey averages (~17.4 KS / ~19.2 MO).
- **Phase 4A Launch (Course Section Microdata Requests):**
  - **Data Request Specifications & Two-Tier Architecture:** Formulated in `research/phase4a_data_request_specifications.md`. Includes Tier 1 (roster-level surrogate IDs) and Tier 2 (agency-aggregated fallback), distinguishing teacher student-seat load from unique student roster load.
  - **Agency Submission Packages:** Formally prepared in `requests/missouri/mo_dese_course_section_request_cover_letter.md` and `requests/kansas/ksde_course_section_request_cover_letter.md` for transmission to MO DESE (MOSIS Screen 20 + Screen 18) and KSDE (KEDX + EDCS).
  - **District Level Requests (Track B):** Packaged in `requests/districts/` (`DISTRICT_RECORDS_REQUEST_FRAMEWORK.md`, `kansas_kora_district_requests.md`, `missouri_sunshine_district_requests.md`, and `district_request_ledger.csv`) covering 9 target LEAs (Shawnee Mission, Olathe, Blue Valley, KCKPS, Basehor-Linwood, KCPS, North Kansas City, Lee's Summit, Richmond) requesting existing SIS master schedule section exports without student PII.
  - **Photographic Sampling Protocol (Track C):** Fully designed in `research/elementary_yearbook_sampling_protocol.md` establishing a 12-school stratified matrix across 3 anchor years for independent photometric homeroom class size enumeration, supported by `data/raw/yearbooks/yearbook_homeroom_ledger.csv`.





