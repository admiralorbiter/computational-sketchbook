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
   - Within districts, coordinator staffing has a strong, positive relationship with teacher staffing: for every 100 classroom teachers added, districts add approximately **+5.12 coordinators** ($p = 0.0027, 95\% \text{ CI } [1.79, 8.45]$).
   - In the 10-year long-difference growth model, teacher growth is strongly predictive ($\beta = +11.12, p < 0.0001$), while student demographic changes (poverty, IDEA, LEP) are either statistically indistinguishable from zero or negatively correlated with coordinator expansion ($\beta_{\text{poverty}} = -0.96, p = 0.0000$).
4. **Substantive Growth Interpretation:**
   - Coordinator staffing expanded fastest in growing suburban districts alongside classroom teacher hiring.
   - Within districts, coordinator staffing is strongly associated with teacher staffing; the current econometric modeling establishes this scale linkage, but does not attribute the common regional upward shift to specific isolated state mandates or demographic divergence.

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

## 3. Long-Difference Growth Model & Grouped Shapley Accounting (Perspective B)

$$\Delta CORSUP_i^{2014 \to 2023} = \alpha + \beta_1 \Delta Teachers_{100, i} + \beta_2 \Delta Poverty_{100, i} + \beta_3 \Delta IDEA_{100, i} + \beta_4 \Delta LEP_{100, i} + \beta_5 \mathbb{I}(\text{KS})_i + \varepsilon_i$$

### 3.1 Long-Difference OLS Estimates ($N = 55$ Districts, $R^2 = 0.692$)

| Regressor | Description | Coeff ($\beta$) | Std. Error | $t$-stat | $p$-value | 95% Conf. Interval |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `const` | Long-difference regressor | **-0.401** | (1.664) | -0.24 | 0.8104 | [-3.75, 2.94] |
| `d_teachers_100` | Long-difference regressor | **11.118** | (2.069) | 5.37 | 0.0000 | [6.96, 15.28] |
| `d_poverty_100` | Long-difference regressor | **-0.957** | (0.213) | -4.50 | 0.0000 | [-1.38, -0.53] |
| `d_idea_100` | Long-difference regressor | **-0.649** | (0.588) | -1.10 | 0.2756 | [-1.83, 0.53] |
| `d_lep_100` | Long-difference regressor | **-3.634** | (0.534) | -6.80 | 0.0000 | [-4.71, -2.56] |
| `is_ks` | Long-difference regressor | **1.502** | (2.741) | 0.55 | 0.5863 | [-4.01, 7.01] |

### 3.2 Grouped Shapley Decomposition of Growth Variance

| Covariate Family | Variables Included | Shapley $R^2$ Contribution | Share of Explained Variance (%) | Primary Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **Student Need Shifts** | `d_poverty_100, d_idea_100, d_lep_100` | **0.4578** | **66.2%** | Explanatory accounting of 10-year coordinator growth |
| **Teacher Scale Growth** | `d_teachers_100` | **0.1919** | **27.7%** | Explanatory accounting of 10-year coordinator growth |
| **State Jurisdiction** | `is_ks` | **0.0420** | **6.1%** | Explanatory accounting of 10-year coordinator growth |

---

## 4. Peer Expected-Level Model & Persistent Outlier Detection (Perspective C)

To support **Phase 3 (Board-Document Audit Sampling)**, we estimate cross-district peer expected baselines:

$$\hat{Y}_{it}^{\text{peer}} = \hat{\mu} + \hat{\gamma}_{\text{state} \times \text{year}} + \mathbf{X}_{it}' \hat{\boldsymbol{\beta}}_{\text{peer}}$$

The unexplained deviation is defined as $\hat{\eta}_{it} = Y_{it} - \hat{Y}_{it}^{\text{peer}}$.

### Audit Selection Criterion:
A district is classified as a **High-Priority Board Audit Target** if its unexplained staffing level exceeds **+1.5 standard deviations above peer expectation for three or more consecutive school years** ($\hat{\eta}_{it} > +1.5 \text{ SD}, \ge 3 \text{ consecutive years}$).

| Model Outcome | District Name | State | Mean Actual FTE | Mean Peer Expected FTE | Unexplained Deviation ($\Delta$ FTE) | Max $z$-Score | High-Deviation Years | Audit Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **school_administrators_fte** | **Kansas City** | KS | 103.4 | 84.5 | **+18.9 FTE** | 9.09 | 8 yrs | `HIGH` |
| **central_mgmt_and_coordinators_fte** | **Kansas City** | KS | 110.4 | 55.1 | **+55.3 FTE** | 6.96 | 10 yrs | `HIGH` |
| **instructional_coordinators_fte** | **Kansas City** | KS | 103.6 | 47.3 | **+56.3 FTE** | 6.58 | 10 yrs | `HIGH` |
| **central_mgmt_and_coordinators_fte** | **Shawnee Mission Pub Sch** | KS | 84.5 | 65.4 | **+19.1 FTE** | 5.34 | 5 yrs | `HIGH` |
| **instructional_coordinators_fte** | **Shawnee Mission Pub Sch** | KS | 74.1 | 56.2 | **+17.9 FTE** | 5.23 | 5 yrs | `HIGH` |
| **lea_administrators_fte** | **FORT OSAGE R-I** | MO | 7.0 | 3.6 | **+3.4 FTE** | 2.65 | 10 yrs | `HIGH` |
| **lea_administrators_fte** | **RAYTOWN C-2** | MO | 7.5 | 5.1 | **+2.4 FTE** | 2.53 | 5 yrs | `HIGH` |
| **lea_administrators_fte** | **Shawnee Mission Pub Sch** | KS | 10.4 | 9.0 | **+1.4 FTE** | 2.18 | 5 yrs | `HIGH` |

---

## 5. Summary & Hand-off to Phase 3 and Phase 4

1. **Phase 3 Qualitative Audit:** Investigates board minutes and organizational charts for the persistent peer outliers identified above (Shawnee Mission USD 512, Kansas City USD 500, Raytown C-2, Fort Osage R-I).
2. **Phase 4 Fiscal Simulation:** Evaluates the dollar stakes of coordinator rollback and peer-expected capping, accounting for mandatory employer marginal fringe benefit loads.
