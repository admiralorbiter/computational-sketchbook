# Missouri Accountability Signal: Empirical Analysis of MSIP 6 Measures

## Overview
This computational sketchbook analyzes the empirical behavior of Missouri's public school accountability measures (MSIP 6) across the 2021–22 through 2024–25 school years (reporting years 2022–2025). The central objective is to determine what existing school performance measures actually capture prior to the implementation of Missouri's new A–F grading framework under Executive Order 26-01.

## Key Questions
1. **Achievement Status vs. Student Composition**: How strongly is academic achievement associated with school socioeconomic disadvantage?
2. **Growth vs. Student Composition**: How strongly is Missouri's value-added growth measure associated with socioeconomic composition, and does this replicate DESE's published diagnostic claims?
3. **Status vs. Growth Quadrants**: How commonly do low-achievement schools achieve high growth, and vice versa?
4. **APR Decomposition**: Which components dominate variation in overall Annual Performance Report scores?
5. **Metric Stability**: How persistent are school achievement, growth, and APR ratings from year to year?

## Repository Structure
```
2026/2026-10-04-missouri-accountability-signal/
├── README.md
├── docs/
│   ├── research_design.md
│   ├── variable_crosswalk.csv
│   ├── methods.md
│   ├── exclusions.md
│   └── limitations.md
├── sources/
│   └── source_registry.csv
├── data/
│   ├── raw/
│   ├── intermediate/
│   └── processed/
├── src/
│   ├── acquire_apr.py
│   ├── acquire_context.py
│   ├── harmonize_apr.py
│   ├── build_school_panel.py
│   ├── classify_schools.py
│   ├── analyze_descriptive.py
│   ├── analyze_status_growth.py
│   ├── replicate_growth_demographics.py
│   └── build_artifacts.py
├── tests/
│   ├── test_source_files.py
│   ├── test_school_keys.py
│   ├── test_ranges.py
│   ├── test_apr_arithmetic.py
│   ├── test_year_crosswalk.py
│   └── test_join_coverage.py
└── artifacts/
    ├── 01_data_inventory.md
    ├── 02_achievement_and_context.md
    ├── 03_growth_and_context.md
    ├── growth_replication_check.md
    └── figures/
```

## Running the Pipeline
The pipeline is designed to execute systematically:
- Phase 1: `python src/acquire_apr.py` (download building APR Summary and Supporting files 2022–2025)
- Phase 2: `python src/harmonize_apr.py` (construct variable crosswalk and harmonize outcomes)
- Phase 3: `python src/acquire_context.py` (download FRPL, demographics, attendance, enrollment)
- Phase 4: `python src/build_school_panel.py` (join school-years into master panel)
- Phase 5: `python src/analyze_descriptive.py` (2025 cross-sectional analysis and figures)
- Phase 6: `python src/replicate_growth_demographics.py` (audit DESE Growth Model diagnostics)
