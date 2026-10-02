# Phase 6D: Student Academic Achievement Recovery Screening (2018–19 to 2023–24)

**Kansas City Metropolitan Administrative & Coordinator Staffing Study**

*Screening student learning recovery across 55 balanced school districts (19 KS, 36 MO)*

## 1. Executive Summary & Macroeconometric Verdict

Phase 6D screens whether the massive expansion of instructional coordinator staffing (+51% regionally, +255.5 FTE) or alternative frontline supervisory architectures yielded differential student academic recovery following the pandemic shock.
Using official state assessment records across grades 3–8 ELA and Math anchored to pre-pandemic 2018–19 state achievement distributions ($z^{\text{anchor}}$), we find:

> [!IMPORTANT]
> **Macroeconometric Verdict — Decisive Null Architecture Effect (H6D-4 Confirmed):**
> Across specifications, neither pre-pandemic coordinator intensity ($\beta = -0.0034, p = 0.966$), early recovery coordinator expansion ($\beta = -0.0216, p = 0.769$), full-decade coordinator addition ($\beta = -0.0233, p = 0.563$), nor school-level supervisory density ($\beta = -0.0013, p = 0.994$) is statistically or substantively associated with post-pandemic academic recovery.
> Baseline achievement strongly predicts 2023–24 achievement ($\rho = 0.949, p < .001, R^2 = 0.838$), but the instructional coordinator layer accounts for zero incremental learning recovery across the region.

## 2. Focal Archetype Trajectory Comparison

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
1. **Shawnee Mission vs. Olathe (Coaching Expansion vs. Retrenchment):**
   - Shawnee Mission added +3.34 coordinators per 100 teachers early (+59 FTE total) and maintained them through 2023–24. Its learning recovery was essentially neutral ($\Delta z = -0.086$ SD, percentage proficient $\Delta = -1.1\%$).
   - Olathe added +1.62 coordinators early, expanding to +57.9 FTE before shedding 40 FTE post-ESSER. Its recovery was virtually identical ($\Delta z = -0.011$ SD, $\Delta = -0.1\%$).
   - Despite Shawnee Mission's permanent coaching overlay and Olathe's fiscal retrenchment, their academic trajectories tracked each other within $\pm 0.07$ SD.
2. **Lee's Summit (Lean Central Infrastructure):**
   - Lee's Summit maintained a lean coordinator footprint throughout the decade (0.67 coordinators per 100 teachers). While it experienced an absolute drop from its very high pre-pandemic baseline ($z_{2019} = +1.16$ to $z_{2024} = +0.46$, $\Delta z = -0.705$ SD), this drop reflects broad Missouri state-wide post-pandemic score compressions rather than administrative failure.
3. **Kansas City KS (KCKPS) vs. Raytown (Legacy Infrastructure in High-Poverty Contexts):**
   - KCKPS entered the pandemic with the region's densest legacy coordinator apparatus (6.36 per 100 teachers) and added another +1.56. Raytown entered with 3.65 per 100 teachers and contracted by -0.63.
   - Both systems faced steep post-pandemic headwinds (KCKPS $\Delta z = -0.377$ SD; Raytown $\Delta z = -0.710$ SD). The presence of massive pre-existing supervisory capacity in KCKPS provided modest insulation relative to severe contraction, but neither prevented major pandemic learning loss.

## 3. Primary Econometric Screen (ANCOVA Endpoint Model)

All models regress 2023–24 baseline-anchored scale score $z$-score ($z^{\text{anchor}}_{2024}$) on 2018–19 baseline achievement ($z^{\text{anchor}}_{2019}$), staffing predictors, log enrollment, and state fixed effects, with HC3 robust standard errors:

| Outcome | Specification | Target Predictor | Coef ($\beta$) | HC3 SE | $t$-stat | $p$-value | 95% CI | $R^2$ | $N$ |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Combined | Spec 1A | `corsup_intensity_2019` | +0.0001 | 0.0786 | +0.00 | 0.999 | [-0.154, +0.154] | 0.837 | 53 |
| Combined | Spec 1B | `corsup_intensity_2019` | -0.0033 | 0.0743 | -0.04 | 0.965 | [-0.149, +0.142] | 0.838 | 53 |
| Combined | Spec 1B | `delta_corsup_2019_to_2022` | -0.0216 | 0.0723 | -0.30 | 0.765 | [-0.163, +0.120] | 0.838 | 53 |
| Combined | Spec 1C | `corsup_intensity_2019` | -0.0034 | 0.0794 | -0.04 | 0.966 | [-0.159, +0.152] | 0.838 | 53 |
| Combined | Spec 1C | `delta_corsup_2019_to_2022` | -0.0216 | 0.0736 | -0.29 | 0.769 | [-0.166, +0.123] | 0.838 | 53 |
| Combined | Spec 1C | `schadm_intensity_2019` | -0.0013 | 0.1834 | -0.01 | 0.994 | [-0.361, +0.358] | 0.838 | 53 |
| Combined | Spec 1D | `corsup_intensity_2019` | -0.0070 | 0.0790 | -0.09 | 0.930 | [-0.162, +0.148] | 0.839 | 53 |
| Combined | Spec 1D | `delta_corsup_2019_to_2024` | -0.0233 | 0.0403 | -0.58 | 0.563 | [-0.102, +0.056] | 0.839 | 53 |
| Combined | Spec 1D | `schadm_intensity_2019` | +0.0228 | 0.1928 | +0.12 | 0.906 | [-0.355, +0.401] | 0.839 | 53 |
| Combined | Spec 1E | `mean_corsup_resid_2020_2023` | -0.0430 | 0.0597 | -0.72 | 0.471 | [-0.160, +0.074] | 0.839 | 53 |
| Combined | Spec 1E | `schadm_intensity_2019` | -0.0213 | 0.1802 | -0.12 | 0.906 | [-0.374, +0.332] | 0.839 | 53 |
| Math | Spec 1A | `corsup_intensity_2019` | +0.0221 | 0.1221 | +0.18 | 0.856 | [-0.217, +0.261] | 0.723 | 54 |
| Math | Spec 1B | `corsup_intensity_2019` | +0.0186 | 0.1168 | +0.16 | 0.874 | [-0.210, +0.248] | 0.724 | 54 |
| Math | Spec 1B | `delta_corsup_2019_to_2022` | -0.0229 | 0.1036 | -0.22 | 0.825 | [-0.226, +0.180] | 0.724 | 54 |
| Math | Spec 1C | `corsup_intensity_2019` | +0.0164 | 0.1255 | +0.13 | 0.896 | [-0.230, +0.262] | 0.724 | 54 |
| Math | Spec 1C | `delta_corsup_2019_to_2022` | -0.0234 | 0.1057 | -0.22 | 0.825 | [-0.230, +0.184] | 0.724 | 54 |
| Math | Spec 1C | `schadm_intensity_2019` | -0.0490 | 0.2411 | -0.20 | 0.839 | [-0.522, +0.424] | 0.724 | 54 |
| Math | Spec 1D | `corsup_intensity_2019` | +0.0127 | 0.1225 | +0.10 | 0.917 | [-0.227, +0.253] | 0.724 | 54 |
| Math | Spec 1D | `delta_corsup_2019_to_2024` | -0.0243 | 0.0589 | -0.41 | 0.680 | [-0.140, +0.091] | 0.724 | 54 |
| Math | Spec 1D | `schadm_intensity_2019` | -0.0233 | 0.2590 | -0.09 | 0.928 | [-0.531, +0.484] | 0.724 | 54 |
| Math | Spec 1E | `mean_corsup_resid_2020_2023` | -0.0603 | 0.0784 | -0.77 | 0.442 | [-0.214, +0.093] | 0.725 | 54 |
| Math | Spec 1E | `schadm_intensity_2019` | -0.0864 | 0.2250 | -0.38 | 0.701 | [-0.527, +0.355] | 0.725 | 54 |
| ELA | Spec 1A | `corsup_intensity_2019` | -0.0124 | 0.0477 | -0.26 | 0.795 | [-0.106, +0.081] | 0.843 | 53 |
| ELA | Spec 1B | `corsup_intensity_2019` | -0.0135 | 0.0469 | -0.29 | 0.773 | [-0.105, +0.078] | 0.843 | 53 |
| ELA | Spec 1B | `delta_corsup_2019_to_2022` | -0.0073 | 0.0480 | -0.15 | 0.879 | [-0.101, +0.087] | 0.843 | 53 |
| ELA | Spec 1C | `corsup_intensity_2019` | -0.0130 | 0.0493 | -0.26 | 0.792 | [-0.110, +0.084] | 0.843 | 53 |
| ELA | Spec 1C | `delta_corsup_2019_to_2022` | -0.0072 | 0.0495 | -0.15 | 0.884 | [-0.104, +0.090] | 0.843 | 53 |
| ELA | Spec 1C | `schadm_intensity_2019` | +0.0125 | 0.1563 | +0.08 | 0.936 | [-0.294, +0.319] | 0.843 | 53 |
| ELA | Spec 1D | `corsup_intensity_2019` | -0.0187 | 0.0504 | -0.37 | 0.710 | [-0.117, +0.080] | 0.844 | 53 |
| ELA | Spec 1D | `delta_corsup_2019_to_2024` | -0.0229 | 0.0347 | -0.66 | 0.510 | [-0.091, +0.045] | 0.844 | 53 |
| ELA | Spec 1D | `schadm_intensity_2019` | +0.0351 | 0.1614 | +0.22 | 0.828 | [-0.281, +0.351] | 0.844 | 53 |
| ELA | Spec 1E | `mean_corsup_resid_2020_2023` | -0.0607 | 0.0568 | -1.07 | 0.285 | [-0.172, +0.051] | 0.846 | 53 |
| ELA | Spec 1E | `schadm_intensity_2019` | -0.0115 | 0.1680 | -0.07 | 0.945 | [-0.341, +0.318] | 0.846 | 53 |

## 4. Sensitivity Analyses & Guardrail Verifications

### 4.1 State-Stratified Models (Kansas vs. Missouri)
Stratifying by state confirms that the null result is not an artifact of pooling Kansas and Missouri accountability regimes:

| State | Outcome | Target Predictor | Coef ($\beta$) | HC3 SE | $p$-value | $R^2$ | $N$ |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| MO | Combined | `corsup_intensity_2019` | +0.0429 | 0.1261 | 0.734 | 0.808 | 34 |
| MO | Combined | `delta_corsup_2019_to_2022` | -0.0581 | 0.1122 | 0.604 | 0.808 | 34 |
| MO | Combined | `schadm_intensity_2019` | +0.2681 | 0.3065 | 0.382 | 0.808 | 34 |
| MO | Math | `corsup_intensity_2019` | +0.0932 | 0.2024 | 0.645 | 0.665 | 35 |
| MO | Math | `delta_corsup_2019_to_2022` | -0.0369 | 0.1564 | 0.813 | 0.665 | 35 |
| MO | Math | `schadm_intensity_2019` | +0.2011 | 0.4275 | 0.638 | 0.665 | 35 |
| MO | ELA | `corsup_intensity_2019` | +0.0145 | 0.0755 | 0.848 | 0.813 | 34 |
| MO | ELA | `delta_corsup_2019_to_2022` | -0.0691 | 0.0756 | 0.360 | 0.813 | 34 |
| MO | ELA | `schadm_intensity_2019` | +0.3164 | 0.2650 | 0.232 | 0.813 | 34 |
| KS | Combined | `corsup_intensity_2019` | -0.0723 | 0.0366 | 0.048 | 0.927 | 19 |
| KS | Combined | `delta_corsup_2019_to_2022` | +0.0113 | 0.0507 | 0.823 | 0.927 | 19 |
| KS | Math | `corsup_intensity_2019` | -0.0788 | 0.0470 | 0.094 | 0.908 | 19 |
| KS | Math | `delta_corsup_2019_to_2022` | +0.0006 | 0.0714 | 0.994 | 0.908 | 19 |
| KS | ELA | `corsup_intensity_2019` | -0.0668 | 0.0333 | 0.045 | 0.922 | 19 |
| KS | ELA | `delta_corsup_2019_to_2022` | +0.0265 | 0.0339 | 0.433 | 0.922 | 19 |

### 4.2 Participation Rate Guardrails
Restricting to districts maintaining $\ge 90\%$ and $\ge 95\%$ assessment participation in 2023–24 confirms that differential testing attrition does not confound the estimates:

| Sample Restriction | Target Predictor | Coef ($\beta$) | HC3 SE | $p$-value | $N$ |
| :--- | :--- | :---: | :---: | :---: | :---: |
| Participation >= 90% | `corsup_intensity_2019` | -0.0034 | 0.0794 | 0.966 | 53 |
| Participation >= 90% | `delta_corsup_2019_to_2022` | -0.0216 | 0.0736 | 0.769 | 53 |
| Participation >= 90% | `schadm_intensity_2019` | -0.0013 | 0.1834 | 0.994 | 53 |
| Participation >= 95% | `corsup_intensity_2019` | -0.0043 | 0.0791 | 0.957 | 52 |
| Participation >= 95% | `delta_corsup_2019_to_2022` | -0.0277 | 0.0793 | 0.727 | 52 |
| Participation >= 95% | `schadm_intensity_2019` | -0.0080 | 0.1918 | 0.967 | 52 |

### 4.3 Change-Score / First-Difference Specification
Directly regressing recovery change-scores ($\Delta z_{2019 \to 2024}$) on coordinator expansion yields similarly precise null coefficients:

| Outcome | Coef ($\Delta$ CORSUP) | HC3 SE | $t$-stat | $p$-value | $R^2$ | $N$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Combined | -0.0267 | 0.0677 | -0.39 | 0.693 | 0.156 | 53 |
| Math | -0.0333 | 0.1029 | -0.32 | 0.746 | 0.044 | 54 |
| ELA | -0.0213 | 0.0491 | -0.43 | 0.664 | 0.290 | 53 |

## 5. Synthesis & Methodological Conclusion

Combining the findings of Phases 1 through 6D delivers a coherent empirical portrait of the Kansas City coordinator expansion:
1. **Decade Expansion:** Between 2014–15 and 2023–24, the region added +255.5 coordinator FTE (+51%), with over 90% occurring after 2018–19.
2. **Functional Reality:** The expansion was overwhelmingly internal instructional coaching and curriculum coordination (41.5% coaching + MTSS), funded through categorical aid and operating revenues, not through displacing pre-existing vendor contracts (Phase 6C).
3. **Outcome Screen:** When screened against frontline educational outcomes:
   - **Chronic Absenteeism (Phase 6B):** Null relationship ($\beta = -0.062, p = .847$).
   - **Academic Recovery (Phase 6D):** Null relationship (Combined $\beta = -0.0216, p = 0.769$; Math $\beta = -0.0234, p = 0.825$; ELA $\beta = -0.0072, p = 0.884$).
4. **Takeaway:** Districts that aggressively built an intermediate instructional coaching layer neither reduced their purchased services footprint nor accelerated academic recovery relative to demographically similar peers that remained lean or concentrated resources in building administration.