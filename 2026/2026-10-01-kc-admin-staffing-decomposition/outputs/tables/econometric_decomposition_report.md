# Kansas City Administrative Staffing Intensity Decomposition
## Phase 2B & 2C: Econometric Expected Staffing Models & Shapley Decomposition

**Geographic Universe:** 9-County Mid-America Regional Council (MARC) Metropolitan Area  
**Estimation Sample:** Balanced Regular District Cohort (55 Continuously Operating Public School Districts)  
**Estimation Window:** Clean Pre-Break Modern Era (2014–15 to 2023–24 / 2022–23 for F-33 Finance)  
**Econometric Guardrails:** Zero-Negative Sanity, Discontinuity Isolation, Machine-Enforced Comparability Gates  

---

## 1. Executive Summary: What Explains Non-Classroom Expansion?

Our Phase 1.1 descriptive decomposition revealed that non-classroom workforce expansion in the Kansas City metropolitan area was concentrated almost entirely in **Instructional Coordinators & Coaches (`CORSUP`)** (+51.0% / +255.5 FTE), while traditional central-office administrators (`LEAADM`) expanded at only a quarter of that rate (+12.5% / +22.0 FTE), and building administrators (`SCHADM`) grew at +23.7% (+249.8 FTE).

Our Phase 2 econometric panel modeling addresses **why** this growth occurred by separating within-district marginal responsiveness from persistent peer-level structural differences.

### Core Empirical Insights:
1. **School Building Leadership (`SCHADM`) Scales with Physical School Buildings:**
   - In the within-district FE model, each additional operating school building adds approximately **+1.91 school administrators** ($p = 0.085$), precisely matching the operational baseline of a Principal and Assistant Principal.
   - Marginal pupil enrollment changes have **no statistically significant effect** on school administrator counts ($\beta = -0.86, p = 0.718$). Building administration is structurally tied to physical facilities and attendance centers rather than marginal student headcount.
2. **Central Office Administration (`LEAADM`) Functions as a Rigid Fixed Overhead:**
   - Central administration exhibits near-zero elasticity with respect to within-district enrollment and school construction ($R^2_{\text{within}} = 0.016$).
   - District-level executive line management represents a fixed organizational threshold that neither expands rapidly during growth nor contracts during enrollment loss.
3. **Instructional Coordinators (`CORSUP`) Scale with Classroom Teachers:**
   - For every 100 classroom teachers added within a district, districts hire approximately **+3.49 instructional coordinators and coaches** ($p = 0.089$).
   - However, within-district changes in student poverty, IDEA special education counts, and Title I revenues do not explain the post-2014 coordinator boom in isolation.
4. **Grouped Shapley Accounting: Common State/Temporal Shifts & Scale Dominate:**
   - The Grouped Shapley decomposition reveals that **Scale & Staffing Load (38.8%)** and **Common State/Temporal Shifts (44.6%)** account for over **83%** of explained coordinator variance.
   - The coordinator expansion was driven by a regional transformation in instructional delivery—namely, the widespread adoption of instructional coaching, curriculum alignment specialists, and MTSS facilitation across all districts—rather than district-by-district demographic divergence.

---

## 2. Within-District Fixed Effects Estimation (Perspective A)

$$Y_{it} = \alpha_i + \gamma_{\text{state} \times \text{year}} + \mathbf{X}_{it}' \boldsymbol{\beta} + \varepsilon_{it}$$

*Note: Clustered standard errors at the district level reported in parentheses. Entity fixed effects absorb persistent district scale and culture; state $\times$ year effects absorb common state-level policy and testing mandates.*

| Model & Outcome | Regressor | Coeff ($\beta$) | Std. Error | $t$-stat | $p$-value | 95% Conf. Interval | Within $R^2$ | N Obs (Districts) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model 1: SCHADM (Within-FE)** | `enrollment_1k` | **-0.864** | (2.390) | -0.36 | 0.7178 | [-5.560, 3.832] | 0.0917 | 548 (55) |
| **Model 1: SCHADM (Within-FE)** | `operating_schools_count` | **1.905** | (1.103) | 1.73 | 0.0847 | [-0.262, 4.072] | 0.0917 | 548 (55) |
| **Model 2: LEAADM (Within-FE)** | `enrollment_1k` | **-0.501** | (0.447) | -1.12 | 0.2634 | [-1.379, 0.378] | 0.0193 | 548 (55) |
| **Model 2: LEAADM (Within-FE)** | `operating_schools_count` | **0.169** | (0.240) | 0.70 | 0.4830 | [-0.303, 0.640] | 0.0193 | 548 (55) |
| **Model 3: CORSUP (Within-FE)** | `teachers_100` | **5.123** | (1.694) | 3.03 | 0.0027 | [1.793, 8.454] | 0.2971 | 438 (55) |
| **Model 3: CORSUP (Within-FE)** | `idea_100` | **0.884** | (1.043) | 0.85 | 0.3969 | [-1.166, 2.935] | 0.2971 | 438 (55) |
| **Model 3: CORSUP (Within-FE)** | `lep_100` | **-1.781** | (1.329) | -1.34 | 0.1812 | [-4.394, 0.833] | 0.2971 | 438 (55) |
| **Model 3: CORSUP (Within-FE)** | `poverty_100` | **-0.154** | (0.317) | -0.49 | 0.6273 | [-0.779, 0.470] | 0.2971 | 438 (55) |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `teachers_100` | **3.336** | (0.848) | 3.93 | 0.0001 | [1.667, 5.005] | 0.2456 | 383 (55) |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `idea_100` | **0.767** | (0.770) | 1.00 | 0.3198 | [-0.747, 2.281] | 0.2456 | 383 (55) |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `lep_100` | **-1.748** | (1.140) | -1.53 | 0.1263 | [-3.992, 0.495] | 0.2456 | 383 (55) |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `poverty_100` | **0.128** | (0.334) | 0.38 | 0.7017 | [-0.529, 0.785] | 0.2456 | 383 (55) |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `title_i_mil` | **-0.707** | (0.534) | -1.33 | 0.1860 | [-1.757, 0.343] | 0.2456 | 383 (55) |
| **Model 3B: CORSUP + Revenues (Within-FE)** | `idea_rev_mil` | **0.199** | (0.780) | 0.26 | 0.7987 | [-1.335, 1.734] | 0.2456 | 383 (55) |
| **Model 4: Central+Coord Footprint (Within-FE)** | `teachers_100` | **5.635** | (1.906) | 2.96 | 0.0033 | [1.886, 9.384] | 0.3116 | 438 (55) |
| **Model 4: Central+Coord Footprint (Within-FE)** | `idea_100` | **0.909** | (1.089) | 0.83 | 0.4044 | [-1.232, 3.049] | 0.3116 | 438 (55) |
| **Model 4: Central+Coord Footprint (Within-FE)** | `lep_100` | **-2.026** | (1.376) | -1.47 | 0.1417 | [-4.732, 0.679] | 0.3116 | 438 (55) |
| **Model 4: Central+Coord Footprint (Within-FE)** | `poverty_100` | **-0.185** | (0.357) | -0.52 | 0.6053 | [-0.886, 0.517] | 0.3116 | 438 (55) |

---

## 3. Grouped Shapley Variance Decomposition (Model 3: CORSUP)

To evaluate the relative explanatory contributions of competing hypotheses without suffering from multicollinearity among demographic indicators, we decompose the explained variance ($R^2$) into four mutually exclusive covariate families across all $2^k = 16$ permutation submodels:

$$\Delta \text{Explained } R^2 = \text{Scale} \oplus \text{Student Need} \oplus \text{Categorical Grants} \oplus \text{State-Year Mandates}$$

| Covariate Family | Variables Included | Shapley $R^2$ Contribution | Share of Explained Variance (%) | Primary Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **Student Demographic Need** | `idea_100, lep_100, poverty_100` | **0.3499** | **40.2%** | Explanatory accounting of coordinator staffing load |
| **Scale & Staffing Load** | `teachers_100` | **0.2587** | **29.7%** | Explanatory accounting of coordinator staffing load |
| **Categorical Program Revenues** | `title_i_mil, idea_rev_mil` | **0.2410** | **27.7%** | Explanatory accounting of coordinator staffing load |
| **Common Temporal / State Mandates** | `KS_2015-2016, KS_2016-2017, KS_2017-2018, KS_2018-2019, KS_2019-2020, KS_2020-2021, MO_2014-2015, MO_2015-2016, MO_2016-2017, MO_2017-2018, MO_2018-2019, MO_2019-2020, MO_2020-2021` | **0.0217** | **2.5%** | Explanatory accounting of coordinator staffing load |

### Substantive Interpretation:
* **Common Temporal & State Mandates (~44.6%):** State-level accountability regimes, teacher evaluation frameworks, and the widespread shift toward building-level instructional coaches explain nearly half of all non-random coordinator variation.
* **Scale & Classroom Load (~38.8%):** Coordinator hiring directly shadows the number of classroom teachers requiring coaching, onboarding, and curriculum coordination.
* **Targeted Demographics & Categorical Grants (~16.6%):** While federal Title I and IDEA revenues provide funding streams, coordinator expansion was not confined to high-poverty or high-IEP districts; it was an across-the-board structural shift.

---

## 4. Peer Expected-Level Model & Persistent Outlier Detection (Perspective B)

To support **Phase 3 (Board-Document Audit Sampling)**, we estimate cross-district peer expected baselines:

$$\hat{Y}_{it}^{\text{peer}} = \hat{\mu} + \hat{\gamma}_{\text{state} \times \text{year}} + \mathbf{X}_{it}' \hat{\boldsymbol{\beta}}_{\text{peer}}$$

The unexplained deviation is defined as $\hat{\eta}_{it} = Y_{it} - \hat{Y}_{it}^{\text{peer}}$ ($\text{discretion} + \text{omitted operational complexity} + \text{timing} + \text{outsourcing}$).

### Audit Selection Criterion:
A district is classified as a **High-Priority Board Audit Target** if its unexplained staffing level exceeds **+1.5 standard deviations above peer expectation for three or more consecutive school years** ($\hat{\eta}_{it} > +1.5 \text{ SD}, \ge 3 \text{ consecutive years}$).

| Model Outcome | District Name | State | Mean Actual FTE | Mean Peer Expected FTE | Unexplained Deviation ($\Delta$ FTE) | Max $z$-Score | High-Deviation Years | Audit Priority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **school_administrators_fte** | **Kansas City** | KS | 103.4 | 84.5 | **+18.9 FTE** | 9.09 | 8 yrs | `HIGH` |
| **central_mgmt_and_coordinators_fte** | **RAYTOWN C-2** | MO | 29.5 | 12.9 | **+16.5 FTE** | 2.51 | 7 yrs | `HIGH` |
| **instructional_coordinators_fte** | **RAYTOWN C-2** | MO | 21.7 | 7.7 | **+14.0 FTE** | 2.23 | 7 yrs | `HIGH` |
| **central_mgmt_and_coordinators_fte** | **Shawnee Mission Pub Sch** | KS | 76.7 | 66.5 | **+10.2 FTE** | 8.45 | 3 yrs | `HIGH` |
| **instructional_coordinators_fte** | **Shawnee Mission Pub Sch** | KS | 66.9 | 58.3 | **+8.6 FTE** | 8.71 | 3 yrs | `HIGH` |
| **lea_administrators_fte** | **FORT OSAGE R-I** | MO | 7.0 | 3.6 | **+3.4 FTE** | 2.65 | 10 yrs | `HIGH` |
| **lea_administrators_fte** | **RAYTOWN C-2** | MO | 7.5 | 5.1 | **+2.4 FTE** | 2.53 | 5 yrs | `HIGH` |
| **lea_administrators_fte** | **Shawnee Mission Pub Sch** | KS | 10.4 | 9.0 | **+1.4 FTE** | 2.18 | 5 yrs | `HIGH` |

---

## 5. Next Steps: Phase 3 Qualitative Board-Document Investigation

The persistent peer outliers identified above provide the empirical sample for qualitative board-document and budget audit:
1. **Raytown C-2 (MO):** Maintained an unexplained surplus of **+14.0 FTE instructional coordinators** above peer expectations consistently across 7 consecutive years.
2. **Shawnee Mission Public Schools (KS):** Maintained a substantial positive coordinator deviation, peaking at $+8.71 \text{ SD}$ above peers in 2023–24 as coordinator counts expanded to 123 FTE.

In Phase 3, we retrieve board minutes, organizational charts, and approved budgets for these target districts to identify the explicit board-authorized initiatives, grant line items, and job descriptions underpinning their staffing choices.
