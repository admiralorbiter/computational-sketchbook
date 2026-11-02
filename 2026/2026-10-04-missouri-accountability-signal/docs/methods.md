# Methodological Protocol

## 1. Analytic Framework
This project investigates the informational signal within Missouri's school accountability system (MSIP 6) across the 2021–22 through 2024–25 school years (reporting years 2022–2025).

The primary analytical goals are:
1. **Status vs. Growth Decoupling**: Assess the bivariate and multivariate association of status (achievement MPI / percent proficient) vs. value-added growth with school socioeconomic composition (FRPL, direct certification, CEP status).
2. **Accountability Signal Decomposition**: Quantify how much cross-school variation in APR performance score is predicted by student context vs. school growth performance.
3. **Growth Model Audit**: Independently replicate the correlations between Missouri Growth Model outcomes and student economic disadvantage published by DESE in the 2024 and 2025 Growth Model Procedures and Results.
4. **Longitudinal Metric Stability**: Evaluate the year-over-year persistence of achievement, growth, and APR percentages to assess the noise-to-signal ratio of accountability classifications.

## 2. Statistical Claims Hierarchy
In accordance with research standards, all claims are strictly classified:
- `DESCRIPTIVE`: Summary statistics, distributions, and cross-tabulations.
- `ASSOCIATIONAL`: Correlation coefficients (Pearson $r$, Spearman $\rho$) and unadjusted bivariate regressions.
- `PREDICTIVE`: Out-of-sample $R^2$, cross-validated predictive accuracy (GroupKFold grouped by district), and variance explained.
- `LONGITUDINAL_ASSOCIATION`: Within-school fixed effects or year-over-year persistence tracking.
- `REPLICATION`: Independent verification of state agency published diagnostics.
- `CAUSAL`: Not asserted. Observational accountability metrics cannot establish the causal effect of schools or poverty on student outcomes.

## 3. Unit of Analysis and Key Definitions
- Unit: School building $\times$ reporting year.
- Canonical ID: `(school_year, district_code, building_code)` formatted as 6-digit county-district code and 4-digit building code.
- Primary Analysis Year: 2025 cross-section.
- Panel Years: 2022, 2023, 2024, 2025.
