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
- [x] **Phase 3:** Empirical Class Size Measurement (`artifacts/01_class_size_measurement.md`, `notebooks/01_class_size_measurement.ipynb`)
- [x] **Phase 3.1:** Methodological Calibration Patch (`artifacts/01b_measurement_calibration.md`)
- [x] **Phase 3.2:** Final Measurement Consistency Patch (`artifacts/01c_final_measurement_certification.md`)
- [ ] **Phase 4:** Instructional-Load Panel (`02_instructional_load.md`)
- [ ] **Phase 5:** SASS / NTPS Series Validation (`ntps_sass_class_size_series.csv`)
- [ ] **Phase 6:** Project STAR Re-Analysis (`03_star_replication.md`)
- [ ] **Phase 7:** Literature Audit Database (`04_literature_audit.md`)
- [ ] **Phase 8:** Evidence Coverage Mapping
- [ ] **Phase 9:** Nonlinearity Testing (20 / 25 / 30 thresholds)
- [ ] **Phase 10:** Final Research Synthesis (`05_synthesis.md`)
