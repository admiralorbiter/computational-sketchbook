# Phase 6 Exploratory Screening: Organizational Architecture and Attendance Recovery

## Executive Summary

Phase 6 extends the certified Phase 1–5 staffing decomposition into outcome recovery, evaluating whether
different regional configurations of **instructional coordination (`CORSUP`)**, **building supervision (`SCHADM`)**,
and **central administration (`LEAADM`)** are systematically associated with post-pandemic student attendance patterns.

### Key Exploratory Findings:
1. **Proportional Mean Reversion Dominates Attendance Recovery:** Across the balanced 55 districts, post-peak recovery
   (the change in chronic absenteeism from 2021–22 to 2022–23) is overwhelmingly driven by the magnitude of the initial shock
   (bivariate $r = -0.530$; multivariate robust $t = -2.82$, $p = 0.005$). Districts that absorbed the highest attendance spikes in 2021–22 exhibited the largest point drops.
2. **State Differences in Attendance Movement:** Kansas districts experienced greater raw post-peak declines in chronic absenteeism (mean -3.9 pts) than Missouri peers (mean +1.5 pts), but in the multivariate specification controlling for peak shock, this gap narrows (coef = -0.80 pts, $t = -0.56$, $p = 0.574$). In net disruption (2017–18 to 2022–23), Kansas saw higher growth in absenteeism (coef = +4.70 pts, $t = 2.15$, $p = 0.032$).
3. **Null Direct Architecture Association:** Controlling for peak shock, student poverty, and state jurisdiction, neither pre-pandemic
   instructional coordinator intensity (robust coef = -0.0366, $t = -0.16$, $p = 0.871$) nor school administrator density (robust coef = -0.1929, $t = -0.10$, $p = 0.923$)
   exhibits a statistically significant linear association with the speed of post-pandemic attendance recovery across all 55 districts.
4. **Poverty Anchors Net Long-Term Disruption:** In evaluating net disruption from 2017–18 baseline to 2022–23 ($R^2 = 0.720$),
   student poverty is the paramount predictor (robust coef = +115.89, $t = +5.26$, $p < 0.001$), completely absorbing supervisory variations.
5. **The KCKPS vs. SMSD Case Comparison:** Kansas City USD 500 achieved the largest single-district post-peak reduction in chronic absence
   in the focal cohort (**-10.3 percentage points**, from 54.3% to 44.0%), consistent with intense building-level administrative triage
   (3.28 admins/school). However, when conditioning on its elevated 54.3% peak baseline, its recovery trajectory is consistent with proportional mean reversion.

---

## 1. Continuous Regional Architecture Coordinates (2018–19 Baseline)

Rather than treating organizational design as categorical dummy variables, Phase 6 maps every district into continuous coordinate space:
- **Instructional Coordination Intensity:** Unexplained coordinator FTE per 100 teachers (`corsup_resid_rate`) from Model 3.
- **School Supervisory Density:** Unexplained building administrators per operating school (`schadm_resid_rate`) from Model 1.
- **Central Line Administration:** Unexplained central line directors per 1,000 pupils (`leaadm_resid_rate`) from Model 2.

### Table 1.1: Focal District Architecture Coordinates & Attendance Trajectory

| District | State | Pre-COVID CORSUP Rate | Pre-COVID SCHADM / School | 2017–18 Baseline Absent % | 2021–22 Peak Absent % | 2022–23 Post-Peak Absent % | Recovery Delta (21-22 to 22-23) | Net Disruption (17-18 to 22-23) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **KANSAS CITY** | KS | 6.36 / 100 tchs | 2.13 admins | 22.2% | 54.3% | 44.0% | **-10.3 pts** | **+21.8 pts** |
| **OLATHE** | KS | 1.85 / 100 tchs | 1.90 admins | 2.2% | 20.0% | 25.3% | **+5.3 pts** | **+23.1 pts** |
| **SHAWNEE MISSION PUB SCH** | KS | 2.66 / 100 tchs | 1.99 admins | 16.6% | 22.5% | 23.9% | **+1.4 pts** | **+7.3 pts** |
| **LEE`S SUMMIT R-VII** | MO | 0.67 / 100 tchs | 2.28 admins | 7.1% | 11.5% | 13.2% | **+1.7 pts** | **+6.1 pts** |
| **NORTH KANSAS CITY 74** | MO | 1.61 / 100 tchs | 2.21 admins | 7.5% | 17.5% | 18.7% | **+1.2 pts** | **+11.2 pts** |
| **RAYTOWN C-2** | MO | 3.65 / 100 tchs | 1.55 admins | 14.1% | 23.9% | 28.6% | **+4.7 pts** | **+14.5 pts** |

---

## 2. Bivariate Correlation Screen Across All 55 Districts

### Table 2.1: Correlations with Post-Pandemic Attendance Recovery & Net Disruption

| Predictor Variable | Correlation with Post-Peak Recovery Delta (21-22 -> 22-23) | Correlation with Net Disruption Delta (17-18 -> 22-23) | Sample N |
| :--- | :---: | :---: | :---: |
| **CORSUP / 100 Teachers (2018-19)** | `-0.035` | `+0.187` | 55 |
| **CORSUP Peer Residual Rate (2018-19)** | `+0.018` | `-0.136` | 55 |
| **SCHADM / School (2018-19)** | `-0.205` | `+0.242` | 55 |
| **SCHADM Peer Residual Rate (2018-19)** | `-0.090` | `+0.181` | 55 |
| **LEAADM / 1,000 Pupils (2018-19)** | `+0.033` | `-0.304` | 55 |
| **Supervisory Footprint / 100 Teachers (2018-19)** | `-0.018` | `-0.094` | 55 |
| **Baseline Absenteeism % (2017-18)** | `-0.453` | `-0.384` | 52 |
| **Peak Shock Absenteeism % (2021-22)** | `-0.530` | `+0.404` | 55 |
| **Census Poverty Rate (2018-19)** | `-0.030` | `+0.510` | 55 |

> [!NOTE]
> **Interpretation of Signs:** In the *Post-Peak Recovery Delta* column, **negative values indicate improving attendance** (a reduction in chronic absenteeism). Thus, negative correlations indicate variables associated with stronger attendance recovery.

---

## 3. Multivariate Econometric Screening Regressions

### Table 3.1: Model 1 — Post-Peak Recovery Delta (2021–22 $\to$ 2022–23)
**Specification:** $\Delta Absence_i^{21-22 \to 22-23} = \alpha + \beta_1 SCHADMResid_{i,pre} + \beta_2 CORSUPResid_{i,pre} + \beta_3 PeakAbsence_i + \beta_4 Poverty_i + \beta_5 Kansas_i + \epsilon_i$
**Sample:** $N = 55$ districts | **$R^2 = 0.521$** (Adj $R^2 = 0.472$) | **HC3 Robust Standard Errors**

| Variable | Robust Coefficient | Robust Std Error | $t$-statistic | $p$-value | 95% Confidence Interval |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `const` | **+4.6780** | 1.3057 | +3.58 | 0.000 | `[+2.1189, +7.2371]` |
| `schadm_resid_rate_2018_19` | **-0.1929** | 1.9876 | -0.10 | 0.923 | `[-4.0885, +3.7028]` |
| `corsup_resid_rate_2018_19` | **-0.0366** | 0.2256 | -0.16 | 0.871 | `[-0.4787, +0.4056]` |
| `absent_rate_2021_22_pct` | **-0.4704** | 0.1667 | -2.82 | 0.005 | `[-0.7971, -0.1436]` |
| `saipe_poverty_pct` | **+51.8538** | 26.4707 | +1.96 | 0.050 | `[-0.0277, +103.7354]` |
| `is_ks` | **-0.8024** | 1.4267 | -0.56 | 0.574 | `[-3.5986, +1.9938]` |

### Table 3.2: Model 2 — Net Disruption Delta (2017–18 $\to$ 2022–23)
**Specification:** $\Delta Absence_i^{17-18 \to 22-23} = \alpha + \beta_1 SCHADMResid_{i,pre} + \beta_2 CORSUPResid_{i,pre} + \beta_3 BaselineAbsence_i + \beta_4 Poverty_i + \beta_5 Kansas_i + \epsilon_i$
**Sample:** $N = 52$ districts | **$R^2 = 0.720$** (Adj $R^2 = 0.689$) | **HC3 Robust Standard Errors**

| Variable | Robust Coefficient | Robust Std Error | $t$-statistic | $p$-value | 95% Confidence Interval |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `const` | **+6.4410** | 2.2502 | +2.86 | 0.004 | `[+2.0306, +10.8513]` |
| `schadm_resid_rate_2018_19` | **+1.1828** | 3.1490 | +0.38 | 0.707 | `[-4.9892, +7.3547]` |
| `corsup_resid_rate_2018_19` | **-0.0200** | 0.4073 | -0.05 | 0.961 | `[-0.8183, +0.7782]` |
| `absent_rate_2017_18_pct` | **-0.9341** | 0.3155 | -2.96 | 0.003 | `[-1.5524, -0.3157]` |
| `saipe_poverty_pct` | **+115.8850** | 22.0225 | +5.26 | 0.000 | `[+72.7217, +159.0484]` |
| `is_ks` | **+4.7018** | 2.1885 | +2.15 | 0.032 | `[+0.4125, +8.9911]` |

---

## 4. Methodological Conclusions & Recommended Phase 6 Sequence

1. **Chronic Absenteeism Signal Assessment:** Across the full 55-district sample, student attendance recovery behaves as a broad
   macro-demographic phenomenon dominated by baseline shock magnitude, poverty concentration, and state jurisdiction. Organizational
   staffing architectures do not exhibit a large standalone linear association with districtwide attendance recovery rates.
2. **Implications for SMSD vs. KCKPS:** While KCKPS's building administrative density aligns intuitively with intensive student attendance
   triage, the quantitative recovery of -10.3 percentage points is statistically commensurate with its elevated 54.3% peak baseline.
3. **Priority Next Step — Fiscal Substitution (Workstream 6C):** Because attendance recovery is confounded by macro-demographic forces,
   **purchased-services substitution** represents a considerably cleaner mechanism test. Investigating whether in-house coordinator hiring
   displaced external consultant expenditures (Object 300/400) provides an unambiguous organizational insourcing test without ecological confounding.
4. **Achievement Recovery (Workstream 6D):** Evaluating standardized math/ELA scale score recovery (KAP/MAP) remains the intellectual core
   for assessing instructional coaching efficacy, requiring within-state $\times$ grade $\times$ subject standardization.
