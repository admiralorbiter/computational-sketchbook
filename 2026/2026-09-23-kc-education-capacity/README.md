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

## Current Status: Phase 3B Complete; Transitioning to Phase 3C

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
- **Next Phase (Phase 3C — Staffing Metric & Allocation Audit):**
  - Independent state replication: Reconcile NCES teacher FTE against KSDE (SO66/LPR) and MO DESE (Core Data / MOSIS) for anchor years (2014–15, 2019–20, 2024–25).
  - Staffing decomposition: Quantify shifts in SPED teachers, SPED paras, IDEA enrollment, EL enrollment, Title III teachers, and non-teaching support staff (coordinators, counselors, psychologists).
  - External benchmarking: Triangulate with Civil Rights Data Collection (CRDC) and National Teacher and Principal Survey (NTPS) class-size estimates.
- **Subsequent Phase 4 (Section-Level Micro Analysis):**
  - **Phase 4A (Section & Roster Distributions):** Directly measure course section sizes, student exposure to large classes ($\ge 25, \ge 30, \ge 33$), teacher roster loads, and allocation diagnostics ("ghost class" / schedule distributions).
  - **Phase 4B (Classroom Complexity Overlay):** Integrate section-level IEP, ELL, chronic absenteeism, and student mobility metrics.





