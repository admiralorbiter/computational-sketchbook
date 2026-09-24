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

## Current Status: Phase 3A (Task 003A) Complete

- **Task 001 (Geographic Universe):** Complete. 691 schools across 9 MARC counties established, geocoded, and classified using NCES CCD/EDGE SY 2024–2025.
- **Task 002 & 002B (Baseline Staffing & Capacity):** Complete. School- and LEA-level baseline capacity panels constructed (`kc_school_capacity_2024_2025.csv`, `kc_lea_capacity_2024_2025.csv`), with programmatic LEA geographic coverage metadata, `Operating Regular (NCES)` terminology, FRL missingness analysis, independent Urban Institute ingestion replication, and audited anomalies in `outputs/tables/task002_qa_report.md`.
- **Task 003A (11-Year Longitudinal Data Construction & Audit):** Complete. Downloaded and cataloged all 99 raw NCES archives across 11 school years (2014–15 through 2024–25). Constructed primary repeated cross-section school panel (`kc_school_capacity_long_2014_15_2024_25.csv`, 7,384 records across 730 unique schools), primary repeated cross-section LEA panel (`kc_lea_capacity_long_2014_15_2024_25.csv`, 881 records), secondary balanced panel (`kc_school_balanced_panel_2014_15_2024_25.csv`, 6,820 records across 620 schools), anomaly ledger (`task003a_anomalies.csv`, 100 entries), and audit report (`outputs/tables/task003a_qa_report.md`). Zero discrepancies on 2024–25 baseline parity check.
- **Next Phase (Task 003B):** Longitudinal Capacity Trend Analysis & Formal Hypothesis Testing (H1a, H1b, H2, H3, H4) across the 10-year period.


