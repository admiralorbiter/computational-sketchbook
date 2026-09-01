# Subject-Stratified Teacher Pipeline Model v2.0

A comprehensive Markov state-space framework for modeling the U.S. K-12 teacher workforce pipeline from preparation through career progression and attrition.

## Overview

This model tracks the flow of individuals through the teacher pipeline:
- **Preparation** → Program enrollment and completion
- **Entry** → Licensure and hiring into public K-12 teaching
- **Progression** → Experience accumulation across career bands
- **Transitions** → Movement to administration, coaching, other roles
- **Attrition** → Departure from teaching (reserve pool, other education, exit)

### Key Features

| Feature | Description |
|---------|-------------|
| **Subject Stratification** | 7 subject categories aligned with NTPS and Title II |
| **Experience Bands** | Early (0-2yr), Mid (3-9yr), Late (10+yr) career stages |
| **11-State Space** | Full tracking from program enrollment through exit |
| **Re-entry Dynamics** | Reserve pool of licensed non-teachers who may return |
| **Cross-Subject Mobility** | Teachers moving between subject areas |
| **Time-Varying Parameters** | Attrition rates vary by period (pre-pandemic, pandemic, recovery) |

## Files Included

### Documentation
- **`Teacher_Pipeline_Model_v2_Complete.docx`** - Full specification document with all parameters, data sources, and calibration methodology
- **`Teacher_Pipeline_Model_Research_Framework.docx`** - Original research framework with literature review

### Python Implementation
- **`teacher_pipeline_model.py`** - Core model classes (`TeacherPipelineModel`, `ModelCalibrator`, projection functions)
- **`data_construction.py`** - Utilities for building model inputs from federal data (NTPS, Title II, IPEDS)
- **`sensitivity_validation.py`** - Sensitivity analysis and validation framework

## Quick Start

```python
from teacher_pipeline_model import TeacherPipelineModel, Subject, State, project_workforce

# Initialize model
model = TeacherPipelineModel()

# Set initial teacher counts (2017-18 baseline)
teacher_counts = {
    Subject.ELEM: 1_750_000,
    Subject.SPED: 450_000,
    Subject.ELA: 320_000,
    Subject.STEM: 380_000,
    Subject.SOCSCI: 200_000,
    Subject.LANG: 120_000,
    Subject.OTHER: 500_000,
}

# Initialize with experience distribution
experience_dist = {State.T0: 0.15, State.T1: 0.35, State.T2: 0.50}
model.initialize_state(year=2017, teacher_counts=teacher_counts, 
                       experience_distribution=experience_dist)

# Get current workforce summary
print(model.summary_dataframe())
```

## State Space

For each of the 7 subjects, the model tracks 11 states:

| State | Name | Description |
|-------|------|-------------|
| P | Program | Enrolled in teacher preparation |
| L | Licensed | Completed program, seeking employment |
| R | Reserve | Licensed but not teaching K-12 |
| T0 | Early Career | Teaching, 0-2 years experience |
| T1 | Mid Career | Teaching, 3-9 years experience |
| T2 | Late Career | Teaching, 10+ years experience |
| A | Admin | Administration/coaching/specialist |
| O_K12 | Other K-12 | Non-teaching K-12 staff |
| E_other | Other Ed | Left for other education (private, higher ed) |
| E_non | Non-Ed | Left education sector |
| X | Exit | Deceased/emigrated (absorbing) |

## Subject Categories

| Code | Category | NTPS Fields |
|------|----------|-------------|
| ELEM | Elementary | General elementary education |
| SPED | Special Education | All special education categories |
| ELA | English/LA | English, language arts, reading |
| STEM | STEM | Math, science, computer science |
| SOCSCI | Social Studies | History, civics, geography, economics |
| LANG | Languages | ESL, foreign/world languages |
| OTHER | Other | Arts, music, PE, CTE |

## Key Parameters

### Attrition Rates

| Period | Baseline Rate | Source |
|--------|---------------|--------|
| 2010-2014 | 6.0% | TFS 2008-09 |
| 2015-2019 | 7.0% | TFS 2012-13 |
| 2020-2021 | 6.5% | Early pandemic |
| 2021-2022 | 9.0% | RAND 2022 |
| 2023-2025 | 7.5% | Post-pandemic |

### Subject Multipliers

Applied to baseline rate: λ_subject = λ_baseline × multiplier

| Subject | Multiplier | Notes |
|---------|------------|-------|
| ELEM | 0.95 | Below average |
| SPED | 1.30 | Highest attrition |
| ELA | 0.95 | Below average |
| STEM | 1.20 | Tech sector competition |
| SOCSCI | 0.90 | Lowest attrition |
| LANG | 1.15 | Small programs, isolation |
| OTHER | 0.85 | High commitment |

### Experience Modifiers

| Band | Modifier | Notes |
|------|----------|-------|
| T0 (0-2yr) | 1.60 | Highest attrition |
| T1 (3-9yr) | 0.85 | Stabilized |
| T2 (10+yr) | 0.90 | Rising with retirement |

## Data Sources

### Primary Federal Sources
- **NTPS/SASS** (nces.ed.gov/surveys/ntps) - Teacher characteristics, subject distribution
- **TFS** (Teacher Follow-up Survey) - Attrition rates, destinations
- **Title II** (title2.ed.gov) - Program enrollment, completers, pass rates
- **Digest of Education Statistics** - Total counts, staff data

### Anchor Years for Calibration
- 2011-12 (SASS)
- 2015-16 (NTPS)
- 2017-18 (NTPS) - Primary calibration target
- 2020-21 (NTPS) - Pandemic validation

## Calibration Process

1. **Compute subject counts**: N_{t,s} = Total_teachers × Subject_percentage
2. **Apply attrition**: Survivors = N_start × (1 - λ)^Δ
3. **Compute entrants needed**: Entrants = N_end - Survivors
4. **Solve for hire rate**: h = Entrants / (Completers × PassRate)
5. **Adjust re-entry if h > 1**: Excess filled from reserve pool

## Sensitivity Analysis

The `sensitivity_validation.py` module provides:

- **One-at-a-time (OAT) sensitivity**: Varies each parameter while holding others constant
- **Monte Carlo simulation**: Quantifies output uncertainty with N=1000 samples
- **Sobol indices**: Identifies which parameters contribute most to variance
- **Validation framework**: Compares simulated outputs to observed data

### Key Parameters to Test (High Priority)
1. Baseline attrition rate (2023-2025)
2. STEM attrition multiplier
3. SPED attrition multiplier
4. Early-career experience modifier
5. Re-entry rate from reserve pool

## Scenarios

Pre-defined scenarios in `sensitivity_validation.py`:

| Scenario | Description |
|----------|-------------|
| Baseline | Central estimates, normalization by 2025 |
| High_Attrition | Elevated rates persist, weak re-entry |
| Low_Attrition | Below pre-pandemic, strong re-entry |
| STEM_Crisis | Severe STEM shortage, declining completers |
| SPED_Improvement | Policy intervention improves retention |
| Pipeline_Recovery | Enrollment rebounds post-pandemic |

## Limitations

1. **National scope**: Does not capture state/district variation
2. **Demand exogenous**: Class sizes and budgets not modeled endogenously
3. **Salary implicit**: Wage effects captured in baseline rates, not explicit
4. **Alternative certification**: Grouped with traditional; could be separated
5. **School-type homogeneity**: High-poverty schools have ~50% higher attrition

## Future Extensions

- State-level disaggregation
- School-poverty dimension
- Explicit salary-attrition relationship
- Traditional vs. alternative pathway separation
- Demand model with enrollment projections

## References

### Key Research
- Nguyen et al. (2019) - Meta-analysis of attrition factors
- Carver-Thomas & Darling-Hammond (2019) - Teacher turnover analysis
- Billingsley & Bettini (2019) - SPED attrition review
- Ingersoll & May (2012) - STEM turnover study
- RAND (2025) - Post-pandemic turnover trends

### NCES Tables
- Table 208.20: Teachers, enrollment, ratios
- Table 209.10: Teacher characteristics
- Table 213.10: Staff by assignment
- NCES 2024-039: TFS 2021-22 results
- NCES 2015-337: BTLS 5-year tracking

## Version History

- **v1.0** - Initial research framework with literature review
- **v2.0** - Complete subject-stratified Markov model with:
  - 11-state space per subject
  - Re-entry dynamics (reserve pool)
  - Cross-subject mobility
  - Sensitivity/validation framework
  - Python implementation
