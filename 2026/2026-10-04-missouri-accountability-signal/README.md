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
│   ├── acquire_nces_ccd.py
│   ├── harmonize_apr.py
│   ├── build_school_panel.py
│   ├── classify_schools.py
│   ├── analyze_descriptive.py
│   ├── replicate_growth_demographics.py
│   ├── build_frontier_and_figures.py
│   └── build_publication_figures.py
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
    ├── 03b_accountability_calibration.md
    ├── growth_replication_check.md
    ├── 04_what_does_a_school_score_measure.md
    ├── figures/
    │   ├── 01_achievement_vs_poverty.png
    │   ├── 02_growth_vs_poverty.png
    │   ├── 03_apr_vs_poverty.png
    │   ├── 04_apr_counterfactual_growth.png
    │   ├── 05_accountability_frontier.png
    │   ├── 06_apr_counterfactual_waterfall.png
    │   ├── 07_status_growth_divergence.png
    │   ├── 08_between_within_district_slopes.png
    │   ├── 09_prior_status_prediction_staircase.png
    │   ├── 10_growth_demographic_correlations.png
    │   ├── 11_status_vs_poverty_clean.png
    │   └── 12_status_poverty_by_school_level.png
    └── tables/
        ├── table_accountability_frontier.csv
        ├── table_apr_component_accounting.csv
        ├── table_apr_counterfactual_decomposition.csv
        ├── table_between_within_fixed_effects.csv
        ├── table_bivariate_summary_2025.csv
        ├── table_complete_case_audit.csv
        ├── table_divergent_schools_profile.csv
        ├── table_growth_missing_crosstab.csv
        ├── table_growth_nonpoverty_audit.csv
        ├── table_growth_shapley_decomposition.csv
        ├── table_level_breakdown_2025.csv
        ├── table_quadrant_status_growth_calibrated.csv
        ├── table_quintile_transitions.csv
        ├── table_stability_multi_year.csv
        └── table_starting_position_cv.csv
```

## Running the Pipeline
The pipeline is designed to execute systematically:
- Phase 1: `python src/acquire_apr.py` (download building APR Summary and Supporting files 2022–2025)
- Phase 2: `python src/harmonize_apr.py` (construct variable crosswalk and harmonize outcomes)
- Phase 3: `python src/acquire_context.py` (download FRPL, demographics, attendance, enrollment)
- Phase 4: `python src/build_school_panel.py` (join school-years into master panel)
- Phase 5: `python src/analyze_descriptive.py` (2025 cross-sectional analysis and figures)
- Phase 6: `python src/replicate_growth_demographics.py` (audit DESE Growth Model diagnostics)
- Phase 7: `python src/build_frontier_and_figures.py` (design frontier, Shapley decomposition, fixed effects, publication figures)
- Phase 8: `python src/build_publication_figures.py` (clean standalone essay graphics: Figures 11 & 12)
