# Econometric & Analytical Methodology (Certified Final)

**Project:** Kansas City Administrative Staffing Intensity Decomposition  
**Status:** Certified Final Econometric Framework (Phases 1–4 Complete)  
**Date:** October 1, 2026  
**Scope:** Bi-State Kansas City Metropolitan Area (9 MARC Counties: Jackson, Clay, Platte, Cass, Ray [MO]; Johnson, Wyandotte, Leavenworth, Miami [KS])

---

## 1. Central Research Objective

This investigation addresses four linked empirical questions regarding public school staffing in the Kansas City metropolitan area over the 2014–2024 decade:
1. **Descriptive Decomposition:** How has supervisory and administrative staffing intensity changed across functional roles relative to classroom teachers and enrollment?
2. **Measurement Integrity:** Which historical trends reflect actual personnel changes versus state survey classification artifacts, and how must empirical models be gated?
3. **Explanatory Modeling:** To what extent can coordinator expansion be explained by classroom teacher scale, student demographics, baseline capacity, and state jurisdiction?
4. **Fiscal Materiality:** How financially material would alternative administrative staffing baselines be, and what feasible base salary raises could be funded for classroom teachers after accounting for mandatory employer marginal payroll taxes?

---

## 2. Sample Design & Analytical Cohorts

To ensure longitudinal integrity and avoid bias from charter entry/exit or district boundary adjustments, all modeling is conducted on a strictly matched cohort:
- **Balanced Presence Cohort (`is_balanced_presence_cohort_55 = True`):** 55 continuously operating, regular public school districts present in all reporting years from 2014–15 to 2023–24 across the 9 MARC counties (19 in Kansas, 36 in Missouri).
- **Modern Harmonized Era (2014–15 to 2023–24):** A 10-year clean window establishing stable reporting following the 2014 Missouri Title I coordinator reclassification and preceding the 2024–25 Kansas building-administrator reporting break.
- **Complete Demographic Cohort (`is_complete_outcome_cohort_53 = True`):** 53 districts possessing complete annual demographic reporting used for endpoint robustness testing.

---

## 3. Data Provenance & Harmonization

Data are harmonized across federal and state administrative collections:
- **Staffing Outcomes:** National Center for Education Statistics (NCES) Common Core of Data (CCD) School District Staff Survey (EDFacts File FS059 / Line 059).
- **Physical Scale:** NCES CCD Public Elementary/Secondary School Universe Survey (FS029) for active operating school facilities.
- **Poverty Covariate:** U.S. Census Bureau Small Area Income and Poverty Estimates (SAIPE) school-district child poverty estimates (ages 5–17 in poverty). Free and Reduced-Price Lunch (FRPL) is excluded due to Community Eligibility Provision (CEP) and direct-certification reporting breaks.
- **Special Populations (IDEA & LEP):** Harmonized district totals derived from Civil Rights Data Collection (CRDC) school-level complexity surveys with linear interpolation between biennial collection waves.
- **State Administrative Registries:** Kansas State Department of Education (KSDE) Superintendent's Organization Report (SO66) and Missouri Department of Elementary and Secondary Education (DESE) Core Data / MOSIS.

### Machine-Enforced Comparability Gates
1. **Kansas 2024–25 Building Administrator Break:** In the preliminary 2024–25 CCD release, Kansas omitted Assistant Principals from `SCHADM` (-36.8% statewide collapse). Models isolate the clean 2014–23 window and flag Kansas 2024–25 observations.
2. **Missouri 2013–14 Central Reclassification:** Missouri districts shifted curriculum coordinators from general district administration (`LEAADM`) into instructional coordinators (`CORSUP`). 20-year trends are evaluated using the safe composite `central_mgmt_and_coordinators_fte`.
3. **Student Support (STUSUP) Reporting Void (2016–2018):** Federal extracts recorded 0.00 FTE across all Kansas and Missouri districts. Broad STUSUP is quarantined, and Guidance Counselors (`GUI` / `counselors_fte`) is utilized as the verified longitudinal pupil support metric.

---

## 4. Econometric Modeling Perspectives

Rather than estimating a single pooled administrative regression, we deploy three tailored econometric perspectives:

### Perspective A: Within-District Fixed Effects Panel (Within-FE)
$$Y_{it} = \alpha_i + \gamma_{\text{state} \times \text{year}} + \mathbf{X}_{it}' \boldsymbol{\beta} + \varepsilon_{it}$$
- Estimates within-district marginal responsiveness to scale, facility, and staffing shifts.
- Uses entity fixed effects ($\alpha_i$) to absorb persistent district scale and operating philosophy.
- Uses state $\times$ year effects ($\gamma_{\text{state} \times \text{year}}$) to absorb common macroeconomic and state-policy shifts.
- Clustered standard errors at the district entity level.

### Perspective B: Long-Difference Growth Decomposition & Sensitivity Family
$$\Delta CORSUP_i = \alpha + \beta_1 \Delta \text{Teachers}_{100, i} + \beta_2 \Delta \text{Poverty}_{100, i} + \beta_3 \Delta \text{IDEA}_{100, i} + \beta_4 \Delta \text{LEP}_{100, i} + \beta_5 \text{KS}_i + \varepsilon_i$$
- **Estimation:** Models 10-year growth directly between 2014–15 and 2023–24 clean endpoints ($N = 55$).
- **Inference:** Reports both classical OLS standard errors and HC3 heteroskedasticity-robust standard errors.
- **Sensitivity Suite:**
  - *Model A (Baseline Count Model):* Absolute count changes (/ 100 students). Teacher growth is directionally positive ($\beta = +11.12$, classic $p < 0.0001$, HC3 robust $p = 0.107$).
  - *Model B (Baseline Capacity Added):* Adds 2014 initial coordinator FTE (`base_corsup_fte`) to test convergence ($\beta_{\text{base}} = -0.401$, classic $p = 0.052$). Under HC3 robust inference, SE is 0.641 ($p = 0.531$, 95% CI [-1.66, +0.85]), consistent with convergence but not robustly distinguishable from zero.
  - *Model C (Demographic Share / Rate Changes):* Replaces count changes with percentage-point rate changes ($\Delta \text{PovertyRatePct}, \Delta \text{IDEAShare}, \Delta \text{LEPShare}$). Demographic rates show no detectable independent effect ($p > 0.30$, $R^2 = 0.317$), indicating that baseline count models captured geographic scale sorting rather than student need composition shifts.
  - *Model D (Observed CRDC Endpoints 2015–2023, $N=53$):* Evaluates growth directly from observed 2015–16 CRDC wave without backward projection ($R^2 = 0.748$; teacher coefficient is sensitive to start year: $\beta = +1.15, p = 0.814$).
  - *Model E (Post-2017 CRDC Wave 2017–2023, $N=55$):* Evaluates growth across modern post-2017 federal reporting regime ($R^2 = 0.654, \beta = +10.84, p = 0.055$).
- **Leave-One-District-Out (LODO) Influence Diagnostics:** Refits Model A omitting each district in turn to quantify leverage (identifying Shawnee Mission, KCKPS, and Olathe as key suburban/urban drivers).
- **Grouped Shapley Accounting with 500-Draw Bootstrap:** Decomposes $R^2$ into Teacher Scale Growth (27.7% [95% CI: 5.0%, 53.3%]), Student Need Shifts (66.2% [95% CI: 37.3%, 88.0%]), and State Jurisdiction (6.1% [95% CI: 2.2%, 28.2%]). In the 4-group specification, Baseline Capacity accounts for 6.8% [95% CI: 1.0%, 27.4%].

### Perspective C: Peer Expected-Level Model & Outlier Sampling
$$\hat{Y}_{it}^{\text{peer}} = \hat{\mu} + \hat{\gamma}_{\text{state} \times \text{year}} + \mathbf{X}_{it}' \hat{\boldsymbol{\beta}}_{\text{peer}}$$
- **Model 1 (SCHADM):** Conditioned on `operating_schools_count` and `enrollment_1k`.
- **Model 2 (LEAADM):** Conditioned on `enrollment_1k` and `operating_schools_count`.
- **Model 3 (CORSUP):** Conditioned on `teachers_100`.
- **Model 4 (Combined Footprint):** Conditioned on `teachers_100`.
- **Diagnostics:** Computes **externally studentized residuals** ($t_i$) and scale-normalized residual intensities (FTE per 100 teachers, per school, and per 1,000 pupils).
- **Priority Outlier Threshold:** Identified as districts with $t_{it} > +1.5$ for $\ge 3$ school years (6 unique districts detected, 4 prioritized for qualitative board audit).

---

## 5. Fiscal Materiality Methodology

To determine whether non-classroom staffing shifts are financially material, Phase 4 runs three counterfactual simulations using empirical compensation parameters from `data/processed/compensation_benchmarks.csv`:

### Parameter Matrix (FY 2024 State Filings)
- **Kansas:** Sourced from KSDE SO66 reports. Total coordinator compensation = **$99,450.00** ($76,500 base + 30.0% benefits). Mandatory employer marginal fringe on raises = **21.22%** (KPERS retirement 12.57% + Death & Disability 1.00% + FICA/Medicare 7.65%; divisor = 1.2122).
- **Missouri:** Sourced from MO DESE Core Data / MOSIS. Total coordinator compensation = **$93,600.00** ($72,000 base + 30.0% benefits). Mandatory employer marginal fringe on raises = **15.95%** (PSRS retirement 14.50% + Medicare 1.45%; divisor = 1.1595).
- **Reconstruction:** Kansas 2015–16 reporting omissions (Olathe USD 233 and Gardner Edgerton USD 231) are linearly interpolated between clean CCD endpoints and validated against state personnel records (documented in `data/processed/kansas_2015_16_reconstruction.csv`).

### Counterfactual Scenarios
1. **Counterfactual 1 (Coordinator Intensity Rollback):**
   - Evaluates the annual expenditure released if coordinator intensity were maintained at the 2014–15 regional baseline (2.41 per 100 teachers).
   - Applied state-specifically: Releases **$21,645,003.97 annually** in 2023–24 (217.81 FTE).
   - 10-year cumulative absorption: **$72,296,352.01** (725.86 FTE-years); 9-year clean un-interpolated sum: **$67,674,988.62** (679.39 FTE-years). Baseline expenditure savings in 2014–15 and 2018–19 are strictly $0.00.
2. **Counterfactual 2 (Positive Peer Deviation Trimming):**
   - Evaluates hypothetical savings from trimming positive residuals down to regression conditional means ($Y_{it} > \hat{Y}_{it}^{\text{peer}}$).
   - Releases **$41,737,693.51 annually** across 360.87 FTE in 2023–24.
3. **Counterfactual 3 (Reallocation into Classroom Teacher Pay):**
   - Distinguishes **Gross Employer Compensation Equivalent** ($\text{Savings} / N_{\text{teachers}}$) from **Feasible Base Salary Raise** ($\text{Savings} / [N_{\text{teachers}} \times (1 + \text{MarginalFringe})]$).
   - Demonstrates that for intensive coaching districts like Shawnee Mission USD 512, coordinator rollback funds a **+$4,117.30 base salary raise (+7.7% on base pay)** per teacher or **136.0 additional classroom teachers** funded at total compensation ($68,514).
