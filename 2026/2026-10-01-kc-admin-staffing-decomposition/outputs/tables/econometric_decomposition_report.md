# Kansas City Administrative Staffing Intensity Decomposition
## Phase 2B & 2C: Econometric Expected Staffing Models & Growth Decomposition

**Geographic Universe:** 9-County Mid-America Regional Council (MARC) Metropolitan Area  
**Estimation Sample:** Balanced Regular District Cohort (55 Continuously Operating Public School Districts)  
**Estimation Window:** Clean Pre-Break Modern Era (2014–15 to 2023–24 / 2020–21 for Complete Demographics)  
**Econometric Guardrails:** Zero-Negative Sanity, Discontinuity Isolation, Machine-Enforced Comparability Gates  

---

## 1. Executive Summary: What Explains Non-Classroom Expansion?

Our Phase 1.1 descriptive decomposition revealed that non-classroom workforce expansion across the Kansas City metropolitan area was concentrated in **Instructional Coordinators & Coaches (`CORSUP`)** (+51.0% / +255.5 FTE), while traditional central-office line administrators (`LEAADM`) expanded at only a quarter of that rate (+12.5% / +22.0 FTE), and building administrators (`SCHADM`) grew at +23.7% (+249.8 FTE).

Our Phase 2 econometric panel modeling addresses **why** this growth occurred by separating within-district marginal responsiveness from persistent peer-level structural differences.

### Core Empirical Insights:
1. **School Building Leadership (`SCHADM`) Suggests Facility Scaling:**
   - In the within-district FE model, each additional operating school building adds approximately **+1.91 school administrators** ($p = 0.085, 95\% \text{ CI } [-0.26, 4.07]$). This point estimate is suggestive of roughly 1 principal plus 1 assistant principal per school, though with marginal significance and wide confidence intervals.
   - Marginal pupil enrollment changes have **no statistically significant effect** on school administrator counts ($\beta = -0.86, p = 0.718$). Building administration is structurally anchored to physical facilities rather than marginal pupil headcount.
2. **Central Office Administration (`LEAADM`) Functions as a Rigid Overhead:**
   - Central administration exhibits near-zero elasticity with respect to within-district enrollment and school construction ($R^2_{\text{within}} = 0.019$).
   - District-level executive line management represents a rigid organizational structure that neither expands rapidly during growth nor contracts during enrollment decline.
3. **Instructional Coordinators (`CORSUP`) Scale with Classroom Teachers:**
   - Within districts, coordinator staffing exhibits a strong and statistically significant relationship with teacher staffing: for every 100 classroom teachers added, districts add approximately **+5.12 coordinators** ($p = 0.0027, 95\% \text{ CI } [1.79, 8.45]$).
   - In the 10-year long-difference growth model, teacher growth is directionally positive ($\beta = +11.12$), though less precise under HC3 heteroskedasticity-robust inference ($p = 0.107$) and sensitive to start year (Model D 2015–2023: $\beta = +1.15, p = 0.814$; Model E 2017–2023: $\beta = +10.84, p = 0.055$). Student demographic count changes (poverty, IDEA, LEP) are negatively correlated with coordinator expansion in the count specification ($\beta_{\text{poverty}} = -0.96, p = 0.0000$).
4. **Substantive Growth Interpretation (Count Sorting vs. Demographic Rates):**
   - In the baseline count model, **66.2% of explained variance** is attributed to the Student Need Shifts group. However, our sensitivity family reveals that this variance reflects **geographic student count sorting** (rapid enrollment and teacher expansion in suburban Johnson and Clay county districts while urban core districts like KCKPS and KCPS already operated high baseline coordinator structures in 2014) rather than increases in student need rates.
   - When demographic changes are specified as **percentage-point share/rate changes** (Model C), the demographic variables show **no detectable independent association** with coordinator growth ($p > 0.30$: poverty $p = 0.336$, IDEA $p = 0.849$, LEP $p = 0.601$), and $R^2$ drops from 0.692 to 0.317. Changes in demographic composition show no detectable independent association with coordinator growth in the rate-based specification. The large count-based associations appear to reflect metropolitan scale and geographic sorting, while the within-district panel provides the strongest evidence linking coordinator staffing to teacher staffing.
   - Baseline capacity in Model B exhibits a negative point estimate ($\beta = -0.401$), consistent with convergence, but is not robustly distinguishable from zero under HC3 inference ($p = 0.531$).
   - Bootstrap resampling (500 draws) reveals wide confidence intervals on Shapley shares: Teacher Scale Growth accounts for **27.7% [95% CI: 5.0%, 53.3%]**, Student Need Shifts account for **66.2% [95% CI: 37.3%, 88.0%]**, and State Jurisdiction accounts for **6.1% [95% CI: 2.2%, 28.2%]**.

---

## 2. Within-District Fixed Effects Estimation (Perspective A)

$$Y_{it} = \alpha_i + \gamma_{\text{state} \times \text{year}} + \mathbf{X}_{it}' \boldsymbol{\beta} + \varepsilon_{it}$$

*Note: Clustered standard errors at the district level. Entity fixed effects absorb persistent district scale and culture; state $\times$ year effects absorb common state-level shifts.*

| Model & Outcome | Regressor | Coeff ($\beta$) | Std. Error | $t$-stat | $p$-value | 95% Conf. Interval | Within $R^2$ | N Obs (Years) | Observed Demog % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model 1: SCHADM (Within-FE)** | `enrollment_1k` | -0.864 | (2.390) | -0.36 | 0.7178 | [-5.56, 3.83] | 0.092 | 548 (10 yrs) | N/A% |
| **Model 1: SCHADM (Within-FE)** | `operating_schools_count` | 1.905 | (1.103) | 1.73 | 0.0847 | [-0.26, 4.07] | 0.092 | 548 (10 yrs) | N/A% |
| **Model 2: LEAADM (Within-FE)** | `enrollment_1k` | -0.501 | (0.447) | -1.12 | 0.2634 | [-1.38, 0.38] | 0.019 | 548 (10 yrs) | N/A% |
| **Model 2: LEAADM (Within-FE)** | `operating_schools_count` | 0.169 | (0.240) | 0.70 | 0.4830 | [-0.30, 0.64] | 0.019 | 548 (10 yrs) | N/A% |
| **Model 3: CORSUP (Within-FE)** | `teachers_100` | 5.123 | (1.694) | 3.03 | 0.0027 | [1.79, 8.45] | 0.297 | 438 (8 yrs) | 49.8% |
| **Model 3: CORSUP (Within-FE)** | `idea_100` | 0.884 | (1.043) | 0.85 | 0.3969 | [-1.17, 2.93] | 0.297 | 438 (8 yrs) | 49.8% |
| **Model 3: CORSUP (Within-FE)** | `lep_100` | -1.781 | (1.329) | -1.34 | 0.1812 | [-4.39, 0.83] | 0.297 | 438 (8 yrs) | 49.8% |
| **Model 3: CORSUP (Within-FE)** | `poverty_100` | -0.154 | (0.317) | -0.49 | 0.6273 | [-0.78, 0.47] | 0.297 | 438 (8 yrs) | 49.8% |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `teachers_100` | 3.485 | (2.040) | 1.71 | 0.0886 | [-0.53, 7.50] | 0.246 | 383 (7 yrs) | 42.6% |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `idea_100` | 0.776 | (0.763) | 1.02 | 0.3098 | [-0.72, 2.28] | 0.246 | 383 (7 yrs) | 42.6% |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `lep_100` | -1.748 | (1.142) | -1.53 | 0.1271 | [-4.00, 0.50] | 0.246 | 383 (7 yrs) | 42.6% |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `poverty_100` | 0.136 | (0.348) | 0.39 | 0.6966 | [-0.55, 0.82] | 0.246 | 383 (7 yrs) | 42.6% |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `title_i_mil` | -0.682 | (0.724) | -0.94 | 0.3472 | [-2.11, 0.74] | 0.246 | 383 (7 yrs) | 42.6% |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `idea_rev_mil` | 0.186 | (0.739) | 0.25 | 0.8018 | [-1.27, 1.64] | 0.246 | 383 (7 yrs) | 42.6% |
| **Model 4: Central+Coord Footprint (Within-FE)** | `teachers_100` | 5.635 | (1.906) | 2.96 | 0.0033 | [1.89, 9.38] | 0.312 | 438 (8 yrs) | 49.8% |
| **Model 4: Central+Coord Footprint (Within-FE)** | `idea_100` | 0.909 | (1.089) | 0.83 | 0.4044 | [-1.23, 3.05] | 0.312 | 438 (8 yrs) | 49.8% |
| **Model 4: Central+Coord Footprint (Within-FE)** | `lep_100` | -2.026 | (1.376) | -1.47 | 0.1417 | [-4.73, 0.68] | 0.312 | 438 (8 yrs) | 49.8% |
| **Model 4: Central+Coord Footprint (Within-FE)** | `poverty_100` | -0.185 | (0.357) | -0.52 | 0.6053 | [-0.89, 0.52] | 0.312 | 438 (8 yrs) | 49.8% |

---

## 3. Long-Difference Growth Model & Sensitivity Suite (Perspective B)

$$\Delta CORSUP_i^{2014 \to 2023} = \alpha + \beta_1 \Delta Teachers_{100, i} + \beta_2 \Delta Poverty_{100, i} + \beta_3 \Delta IDEA_{100, i} + \beta_4 \Delta LEP_{100, i} + \beta_5 \mathbb{I}(\text{KS})_i + \varepsilon_i$$

### 3.1 Long-Difference Baseline OLS Estimates ($N = 55$ Districts, $R^2 = 0.692$)
*Both classical OLS standard errors and HC3 heteroskedasticity-robust standard errors are reported.*

| Regressor | Description | Coeff ($\beta$) | Classic SE ($p$-val) | HC3 Robust SE ($p$-val) | 95% HC3 Conf. Interval |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `const` | Long-difference regressor | **-0.401** | (1.664, $p=0.8104$) | (1.687, $p=0.8119$) | [-3.71, 2.91] |
| `d_teachers_100` | Long-difference regressor | **11.118** | (2.069, $p=0.0000$) | (6.899, $p=0.1071$) | [-2.40, 24.64] |
| `d_poverty_100` | Long-difference regressor | **-0.957** | (0.213, $p=0.0000$) | (0.804, $p=0.2341$) | [-2.53, 0.62] |
| `d_idea_100` | Long-difference regressor | **-0.649** | (0.588, $p=0.2756$) | (2.436, $p=0.7900$) | [-5.42, 4.12] |
| `d_lep_100` | Long-difference regressor | **-3.634** | (0.534, $p=0.0000$) | (4.585, $p=0.4280$) | [-12.62, 5.35] |
| `is_ks` | Long-difference regressor | **1.502** | (2.741, $p=0.5863$) | (5.411, $p=0.7814$) | [-9.10, 12.11] |

### 3.2 Full Growth Sensitivity Family (Models A through E)

To evaluate structural stability, we test five distinct formulations across specifications and cohorts:

| Model Specification | Key Regressors | $R^2$ | $N$ | Substantive Diagnostic |
| :--- | :--- | :---: | :---: | :--- |
| **Model A: Baseline Count Model** | $\Delta \text{Teachers}_{100}, \Delta \text{Poverty}_{100}, \Delta \text{IDEA}_{100}, \Delta \text{LEP}_{100}, \text{KS}$ | 0.692 | 55 | Scale & geographic sorting capture 69% of variance; HC3 SE on teachers = 6.90 ($p = 0.107$). |
| **Model B: Baseline 2014 Capacity** | Model A + `base_corsup_fte` (2014 initial coordinators) | 0.764 | 55 | Point estimate consistent with convergence ($\beta_{\text{base}} = -0.401$), but HC3 robust SE is 0.641 ($p = 0.531$, 95% CI [-1.66, 0.85]). |
| **Model C: Demographic Rates (% pts)** | $\Delta \text{Teachers}_{100}, \Delta \text{PovertyRate}, \Delta \text{IDEAShare}, \Delta \text{LEPShare}, \text{Base}$ | 0.317 | 55 | Demographic rate changes show no detectable independent effect ($p > 0.30$: poverty $p = 0.336$, IDEA $p = 0.849$, LEP $p = 0.601$), while teacher scaling remains directionally positive. |
| **Model D: Observed CRDC Endpoints** | Model B estimated on 2015–16 $\to$ 2023–24 observed CRDC wave | 0.748 | 53 | Un-interpolated federal wave endpoints; teacher coefficient is sensitive to start year ($\beta = 1.15, p = 0.814$). |
| **Model E: Post-2017 CRDC Wave** | Model B estimated on 2017–18 $\to$ 2023–24 observed CRDC wave | 0.654 | 55 | Modern post-2017 federal reporting regime ($R^2 = 0.654$); teacher scaling coefficient is positive and marginally significant ($\beta = +10.84, p = 0.055$). |

### 3.3 Leave-One-District-Out (LODO) Influence Analysis (Top 5 Districts)

To verify that the $\beta_{\text{teachers}} = +11.12$ coefficient is not driven by an individual suburban mega-district, we refit Model A dropping each district in turn:

| Excluded District | State | $\beta_{\text{teachers}}$ (Excluded) | Coefficient Shift ($\Delta \beta$) | $R^2$ Excluded | Influence Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Shawnee Mission Pub Sch** | KS | 7.366 | **-3.752** | 0.559 | High-leverage district in long-difference sample |
| **Kansas City** | KS | 7.435 | **-3.683** | 0.755 | High-leverage district in long-difference sample |
| **Olathe** | KS | 7.534 | **-3.584** | 0.642 | High-leverage district in long-difference sample |
| **NORTH KANSAS CITY 74** | MO | 9.445 | **-1.673** | 0.777 | High-leverage district in long-difference sample |
| **HICKMAN MILLS C-1** | MO | 12.559 | **+1.441** | 0.719 | High-leverage district in long-difference sample |

### 3.4 Grouped Shapley Variance Decomposition & Bootstrap Confidence Intervals

Decomposing the $R^2$ across covariate families with 500-draw bootstrap confidence intervals:

| Covariate Family | Variables Included | Shapley $R^2$ Contribution | Share of Variance (%) | Bootstrap 95% Confidence Interval | Substantive Meaning |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Student Need Shifts** | `d_poverty_100, d_idea_100, d_lep_100` | **0.4578** | **66.2%** | [37.3%, 88.0%] | Student count sorting (suburban headcount expansion) |
| **Teacher Scale Growth** | `d_teachers_100` | **0.1919** | **27.7%** | [5.0%, 53.3%] | Core instructional scale expansion |
| **State Jurisdiction** | `is_ks` | **0.0420** | **6.1%** | [2.2%, 28.2%] | Bi-state institutional/statutory divergence |

*In the 4-group specification including Baseline Capacity ($R^2 = 0.764$), Baseline Capacity accounts for **6.8% [95% CI: 1.0%, 27.4%]**, consistent with convergence among early intensifiers.*

---

## 4. Peer Expected-Level Model & Persistent Outlier Detection (Perspective C)

To support **Phase 3 (Board-Document Qualitative Audit)**, we estimate cross-district peer expected baselines:

$$\hat{Y}_{it}^{\text{peer}} = \hat{\mu} + \hat{\gamma}_{\text{state} \times \text{year}} + \mathbf{X}_{it}' \hat{\boldsymbol{\beta}}_{\text{peer}}$$

- **Model 1 (SCHADM):** Conditioned on `operating_schools_count` and `enrollment_1k`.
- **Model 2 (LEAADM):** Conditioned on `enrollment_1k` and `operating_schools_count`.
- **Model 3 (CORSUP):** Conditioned on `teachers_100`.
- **Model 4 (Combined):** Conditioned on `teachers_100`.

Outliers are identified using **externally studentized residuals** ($t_i$) and scale-normalized residual intensities:

### Audit Selection Criterion:
A district is classified as a persistent outlier if its externally studentized residual exceeds $+1.5$ standard deviations above peer expectation for three or more school years ($t_{it} > +1.5, \ge 3 \text{ years}$).

Across all four peer models, **6 unique districts** met this persistent outlier rule: Kansas City USD 500, Shawnee Mission USD 512, Fort Osage R-I, Raytown C-2, Belton 124, and Independence 30. From these detected outliers, **four priority districts** were selected for in-depth Phase 3 document and board audit: Shawnee Mission USD 512 (large suburban coordinator expansion), Kansas City USD 500 (extraordinary building-level administrative and coordinator intensity), Fort Osage R-I (persistent central line overhead), and Raytown C-2 (persistent central line overhead and layered curriculum supervision).

Notably, **Kansas City USD 500 (KCKPS)** emerges as an extraordinary multi-dimensional outlier: in addition to building administration ($t_{\text{max}} = 10.11$, +1.28 admins/school), KCKPS is an enormous persistent instructional coordinator outlier in Model 3, maintaining a mean unexplained deviation of **+56.3 FTE coordinators** above peer expectations ($t_{\text{max}} = 6.98$, +3.79 coordinators per 100 teachers) across **10 out of 10 panel years**. KCKPS thus operates with the highest combined supervisory intensity in the metropolitan area.

| Model Outcome | District Name | State | Mean Actual FTE | Mean Peer Expected FTE | Unexplained Deviation ($\Delta$ FTE) | Max Studentized $z$ | Mean Residual Rate | High-Deviation Years | Audit Priority |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **school_administrators_fte** | **Kansas City** | KS | 103.4 | 84.5 | **+18.9 FTE** | 10.11 | +0.44 per school | 8 yrs | `HIGH` |
| **central_mgmt_and_coordinators_fte** | **Kansas City** | KS | 110.4 | 55.1 | **+55.3 FTE** | 7.43 | +3.72 per 100 teachers | 10 yrs | `HIGH` |
| **instructional_coordinators_fte** | **Kansas City** | KS | 103.6 | 47.3 | **+56.3 FTE** | 6.98 | +3.79 per 100 teachers | 10 yrs | `HIGH` |
| **central_mgmt_and_coordinators_fte** | **Shawnee Mission Pub Sch** | KS | 84.5 | 65.4 | **+19.1 FTE** | 5.58 | +1.02 per 100 teachers | 5 yrs | `HIGH` |
| **instructional_coordinators_fte** | **Shawnee Mission Pub Sch** | KS | 74.1 | 56.2 | **+17.9 FTE** | 5.46 | +0.95 per 100 teachers | 5 yrs | `HIGH` |
| **lea_administrators_fte** | **FORT OSAGE R-I** | MO | 7.0 | 3.6 | **+3.4 FTE** | 2.65 | +0.69 per 1k pupils | 10 yrs | `HIGH` |
| **lea_administrators_fte** | **RAYTOWN C-2** | MO | 7.5 | 5.1 | **+2.4 FTE** | 2.54 | +0.28 per 1k pupils | 5 yrs | `HIGH` |
| **lea_administrators_fte** | **BELTON 124** | MO | 5.5 | 3.1 | **+2.4 FTE** | 2.27 | +0.52 per 1k pupils | 5 yrs | `HIGH` |
| **lea_administrators_fte** | **Shawnee Mission Pub Sch** | KS | 10.4 | 9.0 | **+1.4 FTE** | 2.22 | +0.05 per 1k pupils | 5 yrs | `HIGH` |
| **lea_administrators_fte** | **INDEPENDENCE 30** | MO | 9.1 | 7.1 | **+2.0 FTE** | 1.80 | +0.14 per 1k pupils | 3 yrs | `HIGH` |

---

## 5. Summary & Hand-off to Phase 3 and Phase 4

1. **Phase 3 Qualitative Audit:** Investigates board minutes and organizational charts for the four prioritized persistent peer outliers (Shawnee Mission USD 512, Kansas City USD 500, Raytown C-2, Fort Osage R-I) from among the 6 detected outlier districts.
2. **Phase 4 Fiscal Simulation:** Evaluates the dollar stakes of coordinator rollback and peer-expected capping, applying exact state-specific compensation pricing ($99,450 for KS, $93,600 for MO) and statutory employer marginal fringe benefit loads (21.22% for KS, 15.95% for MO).
