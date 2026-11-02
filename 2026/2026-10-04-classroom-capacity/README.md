# Classroom Capacity and Class Size Observatory (`2026-10-04-classroom-capacity`)

An empirical computational observatory investigating the structural size of American classrooms, the staffing-to-classroom wedge, and teacher instructional capacity from federal census data (CRDC, CCD, SASS/NTPS).

---

## 1. Project Overview

This repository answers four foundational empirical questions:
1. **How large are actual U.S. classrooms?**
2. **Have actual class sizes changed over time?**
3. **Has the instructional load placed on a teacher changed even when class size has not?**
4. **What does credible causal research tell us about class-size shifts, particularly in the 25–35 student range?**

### The Core Inquiry
> *Has the instructional capacity demanded of each teacher increased because teachers serve increasingly heterogeneous students with more individualized obligations, even if pupil-teacher ratios and average class sizes appeared stable?*

---

## 2. Directory Architecture

```text
2026-10-04-classroom-capacity/
    README.md                           # Observatory overview and navigation
    docs/
        research_design.md              # Governing design and pre-registered hypotheses (H1–H7)
        variable_crosswalk.md           # CRDC variable harmonization protocol across 6 waves
        methods.md                      # Mathematical estimands, Lower-Bound Theorem, weighting, and fixed-effects models
        limitations.md                  # Epistemic limits and data constraints (7 core boundaries)
    sources/
        source_registry.csv             # Provenance registry of raw data files and archives
        study_registry.csv              # Audit registry of causal and observational studies
        crdc_crosswalk.csv              # Field-by-field variable mapping across 6 waves
    data/
        raw/                            # Raw data link documentation
        intermediate/                   # Working staging tables & versioned caches
        processed/
            crdc_course_panel.parquet   # Harmonized longitudinal school-course panel (rebuilt with strict missingness)
            crdc_national_summary.csv   # National benchmark distributions
            crdc_kc_metro_panel.csv     # Local Kansas City 9-county panel
    src/
        harmonize_crdc.py               # Harmonization pipeline across 6 CRDC waves (strict complete cases)
        build_class_size_panel.py       # Master script generating the parquet panel
        analyze_class_size.py           # Statistical and econometric estimation suite
    tests/
        test_crdc_harmonization.py      # Unit tests for variable harmonization & strict missingness integration
        test_class_size_metrics.py      # Unit tests for weighting formulas, Lower-Bound Theorem & threshold semantics
        test_crosswalks.py              # Crosswalk ID integrity and validity checks
    notebooks/
        01_class_size_measurement.ipynb # Interactive visual walkthrough of Study A
    artifacts/
        01_class_size_measurement.md    # Comprehensive Phase 3 research artifact
        01b_measurement_calibration.md  # Phase 3.1 calibration audit artifact
        01c_final_measurement_certification.md # Phase 3.2 final measurement certification delta
        figures/                        # High-resolution analytical charts (repo-relative paths)
        tables/                         # Exported publication summary tables (Tables 01–06, 04b)
```

---

## 3. Execution Status

- [x] **Phase 0:** Source Registry (`sources/source_registry.csv`)
- [x] **Phase 1:** CRDC Variable Crosswalk (`sources/crdc_crosswalk.csv`, `docs/variable_crosswalk.md`)
- [x] **Phase 2:** Longitudinal Panel Construction & QA Suite (`data/processed/crdc_course_panel.parquet`)
- [x] **Phase 3:** Empirical Class Size Measurement (`artifacts/01_class_size_measurement.md`, `artifacts/01c_final_measurement_certification.md`)
- [x] **Phase 4:** Instructional-Load Panel & Longitudinal Shift Calibration (`artifacts/02b_instructional_load_calibration.md`)
- [x] **Phase 5:** SASS / NTPS Series Triangulation & Benchmark Validation (`artifacts/03_ntps_sass_validation.md`)
- [x] **Phase 6:** Project STAR Canonical Causal Replication & Attrition Audit (`artifacts/04_project_star_causal_replication.md`)
- [x] **Phase 7:** Literature & Econometric Audit: The Secondary Class-Size Void (`artifacts/05_quasi_experimental_literature_audit_and_design.md`)
- [x] **Phase 8:** Empirical Coverage Mapping & Non-Linearity Frontiers
- [ ] **Phase 9A:** Public Natural-Experiment Feasibility Audit (Florida $C=25$ & Missouri/KC Scheduling Rules)
- [ ] **Phase 9B:** Preregistered Administrative Microdata Protocol (14-Variable Specification for FDOE/DESE/Districts)
- [ ] **Phase 9C:** Causal Estimation & Execution
- [ ] **Phase 10:** Final Research Synthesis
