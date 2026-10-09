# Measuring Educational Opportunity: Proxy Definitions, Subject Concealment, and Denominator Wedges (`2026-10-09-crdc-opportunity-measurement`)

An empirical measurement study and observational pilot evaluating how administrative proxy definitions, survey skip logic, and denominator choices shape educational opportunity metrics across Missouri public high schools.

---

## 1. Project Overview & Empirical Motivation

When policymakers, parents, and researchers evaluate secondary school quality, they rely on administrative indicators:
- *"Does a school offer Advanced Placement (AP)?"*
- *"Do students have access to foundational STEM coursework like Physics or Computer Science?"*

However, empirical evaluation routinely breaks down across three distinct measurement pathologies:
1. **Indicator Misinterpretation**: Survey indicators often measure reported *student participation/enrollment* rather than institutional *course availability*, fundamentally changing what research questions can be credibly answered.
2. **Proxy Blind Spots**: Relying on an AP-only measure blinds researchers to parallel institutional routes (such as Dual Enrollment and dual credit partnerships).
3. **Denominator Divergence**: Reporting unweighted institutional counts (*"a third of high schools lack physics"*) describes a vastly different social reality than reporting student exposure (*"less than a fifth of students attend a school without physics"*), because course offerings scale directly with student body size.

This computational sketchbook implements a disciplined **Six-Point Study Admission Gate** and carries out three bounded empirical measurement studies using official administrative records from the **2021–22 Civil Rights Data Collection (CRDC)** and **NCES Common Core of Data (CCD)**.

---

## 2. The Six-Point Study Admission Gate

Before specifying regressions or attempting causal inference, empirical work must satisfy this six-point admission gate:

1. **Retrieval & Usability**: The underlying records are retrieved, and required fields contain audited, usable values.
2. **Fixed Population & Denominator**: Population boundaries, exclusions, and denominators are fixed in code and narrative prior to analysis.
3. **Written Calculation/Model**: The calculation or statistical estimator is written down explicitly.
4. **Directional Neutrality**: A result of any direction—including no difference or an unexpected null—substantively answers the question.
5. **Audited Sensitivity Check**: Remaining structural uncertainty (such as conflicting inter-agency reporting) is bounded by a specified sensitivity check.
6. **Scholarly & Survey Integrity**: The exact contribution is checked against prior literature and official survey documentation.

### Research Stage Demarcation

```mermaid
flowchart TD
    A["Raw Administrative Records\n(NCES CCD & OCR CRDC)"] --> B["Population Definition & Bounded Funnel\n(Exclusions explicitly audited)"]
    B --> C{"Six-Point Admission Gate"}
    C -->|Meets 6-Point Rule| D["Stage 1: Measurement Study\n(Direct Counts, Denominator Wedges, Contingencies)"]
    D --> E["Stage 2: Association Study\n(Conditioned comparisons, separate models)"]
    E --> F["Stage 3: Causal Design\n(Exogenous shock, credible identification)"]
    C -->|Fails 6-Point Rule| G["Quarantine / Rejection"]
```

---

## 3. Bounded Population Accounting Funnel

Our target population is **regular public high schools serving exactly grades 9–12 in Missouri during SY 2021–22**.

| Stage | Cohort Description | Count | Excluded | Retained | Rationale / Exclusions |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | Missouri Regular Public Schools (CCD) | 2,298 | 0 | 100.0% | State universe of open regular schools |
| **2** | Classified Exactly Grades 9–12 & Open (CCD) | 318 | 1,980 | 13.8% | Excludes elementary, middle, combined 7–12, and inactive schools |
| **3** | Matched to CRDC Records | 317 | 1 | 99.7% | 1 school (*Hawthorn High School* in Kansas City, `290060803317`) missing in CRDC |
| **4** | Consistent Grades 9–12 Reporting in CRDC | **307** | 10 | 96.5% | Baseline study sample; all 4 grades reported "Yes", others "No" |
| **Sensitivity** | Quarantined Conflicting Grade-Span Records | **10** | — | — | Retained for broad sensitivity checks (total N=317) |

### The 10 Quarantined Conflicting Schools:
- *Rock Bridge Sr. High, David H. Hickman High, Muriel W. Battle High School, Central High, Doniphan High*: Reported Preschool (`PS`) alongside grades 9–12.
- *Bourbon High School, Gallatin High, Mound City High*: Reported K–12 (`PS, KG, G01–G12`).
- *Grain Valley High*: Reported Ungraded (`UG`) alongside grades 9–12.
- *Carnahan School of the Future*: Reported grades 10–12 (`G10–G12`).

---

## 4. Master Findings Scorecard

| Study | Narrow Question | Baseline (N=307) | Sensitivity (N=317) | Delta | Substantive Conclusion |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Study 1 (Pilot)** | Dual Enrollment rate among schools reporting No AP | **92.9%**<br>(105 / 113) | **93.1%**<br>(108 / 116) | +0.18 pp | An AP-only opportunity measure misses **93%** of non-AP schools that report advanced course participation through dual enrollment. |
| **Study 2** | Curricular concealment: No AP Computer Science among AP schools | **65.5%**<br>(127 / 194) | **64.2%**<br>(129 / 201) | -1.28 pp | An umbrella "AP" label conceals that nearly two-thirds of AP high schools offer zero AP Computer Science. |
| **Study 3** | Denominator wedge: Schools vs. Students reporting Zero Physics | **14.88 pp**<br>(32.9% vs 18.0%) | **15.46 pp**<br>(33.1% vs 17.7%) | +0.58 pp | Institutional counts overstate student-level absence by ~15 pp because zero-physics schools are small rural/community schools. |

---

## 5. Granular Study Summaries

### Study 1 (Pilot): AP vs. Dual-Enrollment Opportunity Blind Spots
- **Survey Documentation Fact**: CRDC items `SCH_APENR_IND` and `SCH_DUAL_IND` measure *reported student enrollment/participation*, not mere course catalog listings.
- **The Four-Cell Contingency Matrix (N=307)**:
  - *Neither Route*: **8 schools (2.6%)**
  - *Dual Enrollment Only*: **105 schools (34.2%)**
  - *AP Only*: **14 schools (4.6%)**
  - *Both Routes*: **180 schools (58.6%)**
- **Key Finding**: Of the 113 high schools reporting no AP participation, **105 (92.9%)** report dual-enrollment participation.
- **Sensitivity Check**: Across all 317 matched schools, **108 of 116 (93.1%)** report dual enrollment (+0.18 pp difference).
- **Epistemic Scope**: Answers how often an AP-only measure misses schools reporting participation through another advanced route. Does *not* evaluate course quality, transferability of credits, or student completion benefits.

### Study 2: Curricular Concealment in AP (The Case of Computer Science)
- **The Epistemic Problem**: Umbrella indicators reward schools for any AP offering, concealing whether high-demand technical courses exist.
- **Key Finding**: Among 194 AP-participating high schools, **127 (65.5%)** report zero AP Computer Science participation. Only 67 schools report students taking AP Computer Science.
- **Sensitivity Check**: 129 of 201 AP-participating schools (64.2%) report no AP CS.
- **Epistemic Scope**: Demonstrates that school-level umbrella labels systematically conceal subject-level curricular absence.

### Study 3: The Denominator Wedge (Schools vs. Students in Physics Provision)
- **The Epistemic Problem**: Confusing institutional availability ($P_{\\text{school}}$) with student exposure ($P_{\\text{student}}$).
- **Key Finding**:
  - $P_{\\text{school}}$: 101 of 307 schools (**32.90%**) report zero physics classes.
  - $P_{\\text{student}}$: 40,707 of 225,889 students (**18.02%**) attend those schools.
  - **Denominator Wedge**: **14.88 percentage points** ($32.90\\% - 18.02\\%$).
- **Institutional Scale Driver**: Zero-physics schools average **403 students** (median 271), whereas physics-offering schools average **899 students** (median 718).
- **Epistemic Scope**: Proves that unweighted school counts overstate student-level absence by nearly double because zero-physics schools are disproportionately small.

---

## 6. Directory Architecture

```text
2026-10-09-crdc-opportunity-measurement/
├── README.md                           # Observatory synthesis and evidence scorecard
├── docs/
│   ├── methodological_framework.md     # The Six-Point Admission Gate & research stages
│   └── crdc_documentation_notes.md     # Survey question text & offering vs participation distinction
├── data/
│   ├── raw/                            # Extracted Missouri-specific subsets from CCD & CRDC
│   │   ├── mo_ccd_directory_2021_22.csv
│   │   ├── mo_crdc_school_char_2021_22.csv
│   │   ├── mo_crdc_ap_2021_22.csv
│   │   ├── mo_crdc_dual_2021_22.csv
│   │   ├── mo_crdc_physics_2021_22.csv
│   │   ├── mo_crdc_computer_science_2021_22.csv
│   │   └── mo_crdc_enrollment_2021_22.csv
│   └── processed/
│       ├── mo_high_school_crdc_measurement_panel_2021_22.parquet # Master tidy analysis panel (318 rows)
│       ├── mo_high_school_crdc_measurement_panel_2021_22.csv
│       ├── population_exclusion_funnel.csv
│       ├── study1_ap_dual_summary.csv
│       ├── study2_ap_cs_concealment.csv
│       └── study3_physics_denominator_wedge.csv
├── src/
│   ├── build_panel.py                  # Panel construction pipeline with strict population funnel
│   ├── analyze_measurement.py          # Standalone analytical replication script
│   ├── generate_figures.py             # Generates publication figures for artifacts/
│   └── build_notebook.py               # Generates and executes the Jupyter notebook
├── notebooks/
│   └── 01_measuring_educational_opportunity.ipynb # Executed interactive research notebook
├── tests/
│   └── test_replication_accounting.py  # Pytest suite verifying all sample sizes and calculations
└── artifacts/
    ├── fig1_ap_dual_contingency.png    # 4-cell matrix & conditional breakdown
    ├── fig2_ap_cs_concealment.png      # AP Computer Science concealment rate
    └── fig3_physics_denominator_wedge.png # School vs student denominator wedge & scale
```

---

## 7. Reproduction Instructions

To reproduce all datasets, tests, figures, and executed notebook from scratch:

```powershell
# 1. Build the harmonized measurement panel and population funnel
python 2026/2026-10-09-crdc-opportunity-measurement/src/build_panel.py

# 2. Run the analytical verification script
python 2026/2026-10-09-crdc-opportunity-measurement/src/analyze_measurement.py

# 3. Generate high-resolution figures
python 2026/2026-10-09-crdc-opportunity-measurement/src/generate_figures.py

# 4. Run the automated pytest replication suite
pytest 2026/2026-10-09-crdc-opportunity-measurement/tests/test_replication_accounting.py -v

# 5. Build and execute the interactive Jupyter Notebook
python 2026/2026-10-09-crdc-opportunity-measurement/src/build_notebook.py
```
