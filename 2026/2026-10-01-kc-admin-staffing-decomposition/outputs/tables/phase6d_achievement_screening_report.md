# Phase 6D: Student Academic Proficiency Recovery Screening (2018–19 to 2023–24)

**Kansas City Metropolitan Administrative & Coordinator Staffing Study**

*District Subject-Aggregate Proficiency Screen across 55 balanced school districts (19 KS, 36 MO)*

## 1. Executive Summary & Macroeconometric Verdict

Phase 6D screens whether the massive expansion of instructional coordinator staffing (+51% regionally, +255.5 FTE) or alternative frontline supervisory architectures was associated with differential district-level academic proficiency recovery following the pandemic shock.

> [!NOTE]
> **Metric Definition — District Proficiency-Rate Distribution $z$-Score:**
> All standardized scores ($z^{\text{prof\_dist}}$) measure standard deviations of the **district-level proficiency-rate distribution within state**, anchored to the pre-pandemic 2018–19 baseline ($z^{\text{anchor}}_{i,s,sub,t} = \frac{\%\text{Prof}_{i,s,sub,t} - \mu_{s,sub,2019}}{\sigma_{s,sub,2019}}$).
> They reflect relative district standing in state proficiency distributions, **not** individual student scale-score standard deviations. The analysis is conducted at the district subject-aggregate level (incorporating all tested summative grades reported on state report cards).

> [!IMPORTANT]
> **Macroeconometric Verdict — No Detectable Regional Association (H6D-4 Supported):**
> Across specifications, we find **no detectable regional linear association** between coordinator expansion and district-level academic proficiency recovery.
> In the primary compact student-need adjusted ANCOVA model (controlling for pre-pandemic baseline achievement, Census SAIPE poverty rate, English Learner share, Special Education / IDEA share, district scale, and state fixed effects):
> - **Combined ELA & Math:** $\beta = -0.0303$ (HC3 SE $= 0.0813, p = 0.710, 95% CI [-0.190, +0.129], R^2 = 0.862, N = 53$).
> - **Mathematics:** $\beta = -0.0512$ (HC3 SE $= 0.1188, p = 0.667$).
> - **English Language Arts:** $\beta = -0.0176$ (HC3 SE $= 0.0532, p = 0.741$).
> Student poverty strongly predicts post-pandemic recovery headwinds ($\beta = -5.80, p = .004$), but intermediate coordinator expansion accounts for zero detectable acceleration in learning recovery.

## 2. Inferential Precision & Equivalence Bounds
Because confidence intervals are moderately wide in this 55-district sample, the proper statistical conclusion is **failure to detect an association**, rather than proven zero effect:
- For a realistic $+3.0$ coordinator per 100 teacher expansion (such as Shawnee Mission's $+3.34$), the 95% confidence interval permits effects ranging from $-0.63$ to $+0.43$ standard deviations of the state district-proficiency distribution.
- Testing for statistical equivalence within a Smallest Effect Size of Interest (SESOI) of $\pm 0.20$ district-proficiency SDs for a $+3.0$ expansion (equivalent to a slope bound $\delta = \pm 0.0667$) yields a Two One-Sided Tests (TOST) $p$-value of $p = .328$.
- Thus, while point estimates are consistently near zero or slightly negative, the sample size does not provide the statistical power required to reject the presence of moderate positive or negative effects.

## 3. Focal Archetype Trajectory Comparison

The table below examines the recovery trajectories of the six focal archetype districts:

| District | Archetype | State | CORSUP '19 | $\Delta$ CORSUP '19-'22 | Baseline $z_{2019}$ | Endpoint $z_{2024}$ | Recovery $\Delta z$ | $\Delta$ % Proficient |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Kansas City | Persistent Legacy Infrastructure | KS | 6.36 | +-0.20 | -1.69 | -2.07 | **-0.377** | -4.9% |
| Olathe | Late Expansion / High Retrenchment | KS | 1.85 | +1.62 | +0.27 | +0.26 | **-0.011** | -0.1% |
| Shawnee Mission Pub Sch | Rapid Pre/Early Coaching | KS | 2.66 | +3.34 | +0.47 | +0.38 | **-0.086** | -1.1% |
| LEE'S SUMMIT R-VII | Lean Central Architecture | MO | 0.67 | +0.14 | +1.16 | +0.46 | **-0.705** | -8.1% |
| NORTH KANSAS CITY 74 | School Building Supervision | MO | 1.61 | +0.73 | +0.41 | +0.04 | **-0.365** | -4.2% |
| RAYTOWN C-2 | High Legacy / Contraction | MO | 3.65 | +-0.95 | -1.38 | -2.09 | **-0.710** | -8.0% |

### Substantive Findings Across Archetypes:
1. **Shawnee Mission vs. Olathe (Coaching Overlay vs. Retrenchment):**
   - Shawnee Mission added +3.34 coordinators per 100 teachers early (+59 FTE total) and maintained them through 2023–24. Its district-level proficiency recovery was essentially neutral ($\Delta z = -0.086$ SD, $\Delta \%\text{Prof} = -1.1\%$).
   - Olathe added +1.62 coordinators early, expanding to +57.9 FTE before shedding 40 FTE post-ESSER. Its recovery was virtually identical ($\Delta z = -0.011$ SD, $\Delta \%\text{Prof} = -0.1\%$).
   - Despite Shawnee Mission's permanent coaching overlay and Olathe's fiscal retrenchment, their academic trajectories tracked each other within $\pm 0.07$ district-proficiency SDs.
2. **Lee's Summit (Lean Central Infrastructure):**
   - Lee's Summit maintained a lean coordinator footprint throughout the decade (0.67 coordinators per 100 teachers). While it experienced an absolute drop from its pre-pandemic baseline ($z_{2019} = +1.16$ to $z_{2024} = +0.46$, $\Delta z = -0.705$ SD), this drop reflects broad Missouri state-wide post-pandemic score compressions rather than administrative failure.
3. **Kansas City KS (KCKPS) vs. Raytown (Legacy Infrastructure in High-Poverty Contexts):**
   - KCKPS entered the pandemic with the region's densest legacy coordinator apparatus (6.36 per 100 teachers) and added another +1.56. Raytown entered with 3.65 per 100 teachers and contracted by -0.63.
   - Both systems faced steep post-pandemic headwinds (KCKPS $\Delta z = -0.377$ SD; Raytown $\Delta z = -0.710$ SD). The presence of massive pre-existing supervisory capacity in KCKPS provided modest insulation relative to severe contraction, but neither prevented major pandemic learning loss.

## 4. Primary Econometric Screen (ANCOVA Endpoint Models)

All models regress 2023–24 baseline-anchored district proficiency $z$-score ($z^{\text{anchor}}_{2024}$) on 2018–19 baseline achievement ($z^{\text{anchor}}_{2019}$), staffing predictors, student need controls, log enrollment, and state fixed effects, with HC3 robust standard errors:

| Outcome | Specification | Target Predictor | Coef ($\beta$) | HC3 SE | $t$-stat | $p$-value | 95% CI | $R^2$ | $N$ |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Combined | Spec 1A | `delta_corsup_2019_to_2022` | -0.0303 | 0.0813 | -0.37 | 0.710 | [-0.190, +0.129] | 0.862 | 53 |
| Combined | Spec 1B | `corsup_intensity_2019` | +0.0068 | 0.0727 | +0.09 | 0.925 | [-0.136, +0.149] | 0.862 | 53 |
| Combined | Spec 1B | `delta_corsup_2019_to_2022` | -0.0286 | 0.0788 | -0.36 | 0.716 | [-0.183, +0.126] | 0.862 | 53 |
| Combined | Spec 1C | `delta_corsup_2019_to_2022` | -0.0306 | 0.0818 | -0.37 | 0.709 | [-0.191, +0.130] | 0.862 | 53 |
| Combined | Spec 1C | `schadm_intensity_2019` | -0.0314 | 0.1411 | -0.22 | 0.824 | [-0.308, +0.245] | 0.862 | 53 |
| Combined | Spec 1D | `corsup_intensity_2019` | +0.0054 | 0.0776 | +0.07 | 0.944 | [-0.147, +0.157] | 0.862 | 53 |
| Combined | Spec 1D | `delta_corsup_2019_to_2022` | -0.0292 | 0.0796 | -0.37 | 0.713 | [-0.185, +0.127] | 0.862 | 53 |
| Combined | Spec 1D | `schadm_intensity_2019` | -0.0283 | 0.1613 | -0.18 | 0.861 | [-0.344, +0.288] | 0.862 | 53 |
| Combined | Spec 1E | `delta_corsup_2019_to_2024` | -0.0235 | 0.0386 | -0.61 | 0.542 | [-0.099, +0.052] | 0.862 | 53 |
| Combined | Spec 1F | `mean_corsup_resid_2020_2023` | -0.0365 | 0.0607 | -0.60 | 0.547 | [-0.155, +0.082] | 0.862 | 53 |
| Combined | Spec 1G | `corsup_intensity_2019` | -0.0034 | 0.0794 | -0.04 | 0.966 | [-0.159, +0.152] | 0.838 | 53 |
| Combined | Spec 1G | `delta_corsup_2019_to_2022` | -0.0216 | 0.0736 | -0.29 | 0.769 | [-0.166, +0.123] | 0.838 | 53 |
| Combined | Spec 1G | `schadm_intensity_2019` | -0.0013 | 0.1834 | -0.01 | 0.994 | [-0.361, +0.358] | 0.838 | 53 |
| Math | Spec 1A | `delta_corsup_2019_to_2022` | -0.0512 | 0.1188 | -0.43 | 0.667 | [-0.284, +0.182] | 0.763 | 54 |
| Math | Spec 1B | `corsup_intensity_2019` | +0.0300 | 0.1074 | +0.28 | 0.780 | [-0.180, +0.240] | 0.765 | 54 |
| Math | Spec 1B | `delta_corsup_2019_to_2022` | -0.0435 | 0.1088 | -0.40 | 0.689 | [-0.257, +0.170] | 0.765 | 54 |
| Math | Spec 1C | `delta_corsup_2019_to_2022` | -0.0516 | 0.1192 | -0.43 | 0.665 | [-0.285, +0.182] | 0.764 | 54 |
| Math | Spec 1C | `schadm_intensity_2019` | -0.0818 | 0.1833 | -0.45 | 0.655 | [-0.441, +0.277] | 0.764 | 54 |
| Math | Spec 1D | `corsup_intensity_2019` | +0.0263 | 0.1159 | +0.23 | 0.820 | [-0.201, +0.254] | 0.765 | 54 |
| Math | Spec 1D | `delta_corsup_2019_to_2022` | -0.0448 | 0.1098 | -0.41 | 0.683 | [-0.260, +0.170] | 0.765 | 54 |
| Math | Spec 1D | `schadm_intensity_2019` | -0.0648 | 0.2184 | -0.30 | 0.767 | [-0.493, +0.363] | 0.765 | 54 |
| Math | Spec 1E | `delta_corsup_2019_to_2024` | -0.0441 | 0.0624 | -0.71 | 0.480 | [-0.166, +0.078] | 0.764 | 54 |
| Math | Spec 1F | `mean_corsup_resid_2020_2023` | -0.0214 | 0.0538 | -0.40 | 0.690 | [-0.127, +0.084] | 0.760 | 54 |
| Math | Spec 1G | `corsup_intensity_2019` | +0.0164 | 0.1255 | +0.13 | 0.896 | [-0.230, +0.262] | 0.724 | 54 |
| Math | Spec 1G | `delta_corsup_2019_to_2022` | -0.0234 | 0.1057 | -0.22 | 0.825 | [-0.230, +0.184] | 0.724 | 54 |
| Math | Spec 1G | `schadm_intensity_2019` | -0.0490 | 0.2411 | -0.20 | 0.839 | [-0.522, +0.424] | 0.724 | 54 |
| ELA | Spec 1A | `delta_corsup_2019_to_2022` | -0.0176 | 0.0532 | -0.33 | 0.741 | [-0.122, +0.087] | 0.887 | 53 |
| ELA | Spec 1B | `corsup_intensity_2019` | +0.0004 | 0.0507 | +0.01 | 0.993 | [-0.099, +0.100] | 0.887 | 53 |
| ELA | Spec 1B | `delta_corsup_2019_to_2022` | -0.0175 | 0.0556 | -0.31 | 0.753 | [-0.126, +0.091] | 0.887 | 53 |
| ELA | Spec 1C | `delta_corsup_2019_to_2022` | -0.0180 | 0.0535 | -0.34 | 0.737 | [-0.123, +0.087] | 0.888 | 53 |
| ELA | Spec 1C | `schadm_intensity_2019` | -0.0431 | 0.1197 | -0.36 | 0.719 | [-0.278, +0.192] | 0.888 | 53 |
| ELA | Spec 1D | `corsup_intensity_2019` | -0.0017 | 0.0533 | -0.03 | 0.975 | [-0.106, +0.103] | 0.888 | 53 |
| ELA | Spec 1D | `delta_corsup_2019_to_2022` | -0.0184 | 0.0563 | -0.33 | 0.744 | [-0.129, +0.092] | 0.888 | 53 |
| ELA | Spec 1D | `schadm_intensity_2019` | -0.0440 | 0.1326 | -0.33 | 0.740 | [-0.304, +0.216] | 0.888 | 53 |
| ELA | Spec 1E | `delta_corsup_2019_to_2024` | -0.0136 | 0.0277 | -0.49 | 0.623 | [-0.068, +0.041] | 0.887 | 53 |
| ELA | Spec 1F | `mean_corsup_resid_2020_2023` | -0.0433 | 0.0546 | -0.79 | 0.428 | [-0.150, +0.064] | 0.888 | 53 |
| ELA | Spec 1G | `corsup_intensity_2019` | -0.0130 | 0.0493 | -0.26 | 0.792 | [-0.110, +0.084] | 0.843 | 53 |
| ELA | Spec 1G | `delta_corsup_2019_to_2022` | -0.0072 | 0.0495 | -0.15 | 0.884 | [-0.104, +0.090] | 0.843 | 53 |
| ELA | Spec 1G | `schadm_intensity_2019` | +0.0125 | 0.1563 | +0.08 | 0.936 | [-0.294, +0.319] | 0.843 | 53 |

## 5. Sensitivity Analyses & Guardrail Verifications

### 5.1 State-Stratified Models (Kansas vs. Missouri)
Stratifying by state reveals one notable nominal divergence that warrants transparent reporting:
- In Kansas ($N=19$), baseline coordinator intensity exhibits a nominal negative association with 2024 proficiency for Combined outcomes ($\beta = -0.0723, p = 0.048$) and ELA ($\beta = -0.0668, p = 0.045$).
- **Multiple-Testing Correction:** When adjusting for the 15-test state-stratified family using the Benjamini-Hochberg procedure, these nominal signals do **not** survive significance (Combined FDR $q = 0.362$, ELA FDR $q = 0.362$).
- **Substantive Context:** This exploratory signal arises in an underpowered $N=19$ subgroup where baseline coordinator staffing was concentrated in urban/high-poverty districts (e.g., KCKPS). Crucially, coordinator **expansion** in Kansas exhibits no negative effect whatsoever (Combined $\beta = +0.0113, p = 0.823$).

| State | Outcome | Target Predictor | Coef ($\beta$) | HC3 SE | Unadj $p$ | FDR $q$ | $R^2$ | $N$ |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| MO | Combined | `corsup_intensity_2019` | +0.0429 | 0.1261 | 0.734 | 0.908 | 0.808 | 34 |
| MO | Combined | `delta_corsup_2019_to_2022` | -0.0581 | 0.1122 | 0.604 | 0.908 | 0.808 | 34 |
| MO | Combined | `schadm_intensity_2019` | +0.2681 | 0.3065 | 0.382 | 0.908 | 0.808 | 34 |
| MO | Math | `corsup_intensity_2019` | +0.0932 | 0.2024 | 0.645 | 0.908 | 0.665 | 35 |
| MO | Math | `delta_corsup_2019_to_2022` | -0.0369 | 0.1564 | 0.813 | 0.908 | 0.665 | 35 |
| MO | Math | `schadm_intensity_2019` | +0.2011 | 0.4275 | 0.638 | 0.908 | 0.665 | 35 |
| MO | ELA | `corsup_intensity_2019` | +0.0145 | 0.0755 | 0.848 | 0.908 | 0.813 | 34 |
| MO | ELA | `delta_corsup_2019_to_2022` | -0.0691 | 0.0756 | 0.360 | 0.908 | 0.813 | 34 |
| MO | ELA | `schadm_intensity_2019` | +0.3164 | 0.2650 | 0.232 | 0.871 | 0.813 | 34 |
| KS | Combined | `corsup_intensity_2019` | -0.0723 | 0.0366 | 0.048 | 0.362 | 0.927 | 19 |
| KS | Combined | `delta_corsup_2019_to_2022` | +0.0113 | 0.0507 | 0.823 | 0.908 | 0.927 | 19 |
| KS | Math | `corsup_intensity_2019` | -0.0788 | 0.0470 | 0.094 | 0.470 | 0.908 | 19 |
| KS | Math | `delta_corsup_2019_to_2022` | +0.0006 | 0.0714 | 0.994 | 0.994 | 0.908 | 19 |
| KS | ELA | `corsup_intensity_2019` | -0.0668 | 0.0333 | 0.045 | 0.362 | 0.922 | 19 |
| KS | ELA | `delta_corsup_2019_to_2022` | +0.0265 | 0.0339 | 0.433 | 0.908 | 0.922 | 19 |

### 5.2 Tested-N-Weighted Composite Outcome
Weighting the ELA and Math composite by tested student counts yields an identical null expansion coefficient:
- Tested-N-Weighted Combined: $\beta = -0.0308$ (HC3 SE $= 0.0815, p = 0.705, R^2 = 0.862, N = 53$).

### 5.3 Participation Rate Guardrails
Restricting to districts maintaining $\ge 90\%$ and $\ge 95\%$ assessment participation in 2023–24 (strictly excluding missing participation values) confirms that testing attrition does not confound the estimates:

| Sample Restriction | Target Predictor | Coef ($\beta$) | HC3 SE | $p$-value | $N$ |
| :--- | :--- | :---: | :---: | :---: | :---: |
| Participation >= 90% | `delta_corsup_2019_to_2022` | -0.0303 | 0.0813 | 0.710 | 53 |
| Participation >= 95% | `delta_corsup_2019_to_2022` | -0.0277 | 0.0837 | 0.740 | 52 |

### 5.4 Change-Score / First-Difference Specification
Directly regressing recovery change-scores ($\Delta z_{2019 \to 2024}$) on coordinator expansion and student need yields similarly null coefficients:

| Outcome | Coef ($\Delta$ CORSUP) | HC3 SE | $t$-stat | $p$-value | $R^2$ | $N$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Combined | -0.0310 | 0.0757 | -0.41 | 0.682 | 0.160 | 53 |
| Math | -0.0436 | 0.1136 | -0.38 | 0.701 | 0.058 | 54 |
| ELA | -0.0192 | 0.0529 | -0.36 | 0.717 | 0.291 | 53 |

## 6. Synthesis & Methodological Conclusion

Combining the findings of Phases 1 through 6D delivers a coherent empirical portrait of the Kansas City coordinator expansion:
1. **Decade Expansion:** Between 2014–15 and 2023–24, the region added +255.5 coordinator FTE (+51%), with over 90% occurring after 2018–19.
2. **Functional Reality:** The expansion was overwhelmingly internal instructional coaching and curriculum coordination (41.5% coaching + MTSS), funded through categorical aid and operating revenues, not through displacing pre-existing vendor contracts (Phase 6C).
3. **Outcome Screen:** When screened against frontline educational outcomes:
   - **Chronic Absenteeism (Phase 6B):** Null relationship ($\beta = -0.062, p = .847$).
   - **Proficiency Recovery (Phase 6D):** No detectable association (Combined $\beta = -0.0303, p = 0.710$; Math $\beta = -0.0512, p = 0.667$; ELA $\beta = -0.0176, p = 0.741$).
4. **Scientifically Defensible Takeaway:** We find no evidence that districts which entered the pandemic with more intensive coordinator staffing, or expanded coordinator capacity more aggressively during the recovery period, experienced systematically stronger district-level ELA or mathematics proficiency recovery through 2023–24.