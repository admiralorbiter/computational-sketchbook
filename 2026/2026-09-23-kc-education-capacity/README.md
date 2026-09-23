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

## Current Status: Phase 1 (Task 001)

Establishing the baseline geographic school universe for the Kansas City bi-state region using official National Center for Education Statistics (NCES) Common Core of Data (CCD) and Education Demographic and Geographic Estimates (EDGE) datasets.
