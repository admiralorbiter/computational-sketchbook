# Artifact 03b: Accountability Signal Calibration Review

## 1. Overview and Purpose

This artifact documents the comprehensive calibration review of **Phases 0 through 6** for the **Missouri Accountability Signal** project. Following methodological review, several structural refinements were applied:
1. Distinguishing the official growth diagnostic (**Direct Certification**) from the public socioeconomic metric (**FRPL**).
2. Clarifying that public MSIP 6 growth measures are **discretized accountability points** derived from the state value-added model, not continuous student-level residuals.
3. Renaming analyst-created composite metrics (`analyst_composite_status_mpi` and `apr_growth_pts_pct`) and enforcing strict **complete-case subject requirements**.
4. Implementing an exact **enrollment-weighted Pearson correlation** ($r_w$).
5. Replacing speculative claims with an exact **APR point-accounting counterfactual decomposition** (actual APR vs. APR excluding growth points).
6. Conducting **district-grouped cross-validation** (`GroupKFold` across 551 LEAs) for starting position models.
7. Expanding longitudinal stability across multiple year transitions (**2023 $\to$ 2024** and **2024 $\to$ 2025**) and computing quintile transition rates.
8. Incorporating official **NCES Common Core of Data (CCD)** institutional type and virtual school flags into Sample B.
9. Enforcing strict epistemic discipline: **growth measures do not equate to causal school effectiveness**.

---

## 2. Section A: What Survived the Calibration

The central empirical conclusions of the investigation remain robust, well-supported, and statistically validated across all specifications:

1. **Strong Status/Poverty Association**: Absolute academic achievement status remains heavily associated with student socioeconomic composition ($r = -0.6511$, $R^2 = 42.39\%$, enrollment-weighted $r_w = -0.7204, R^2 = 51.90\%$).
2. **Orthogonality of Public Growth Points to Poverty**: Missouri's reported value-added growth points measure remains virtually uncorrelated with school Free/Reduced Lunch ($r = +0.0027, R^2 = 0.0007\%$, weighted $r_w = -0.0508, R^2 = 0.26\%$) and with Direct Certification ($r = +0.0207, R^2 = 0.04\%$).
3. **Decoupling of Status and Growth**: Status achievement alone linearly explains only **4.27% of cross-school variance** in reported growth points ($r = 0.2067$). Status and growth capture fundamentally distinct dimensions of school performance.
4. **Disproportionate Low-Status / High-Growth Presence**: Between **21.2% and 25.5% of all conventional public schools** (420 to 506 schools) fall into the **Low Status / High Growth** quadrant—schools serving high-poverty student populations (mean FRPL 71.6%) that achieve above-average growth points.
5. **Marked Stability Divergence**: Achievement status is highly persistent year-over-year ($r = 0.938$, with 65.8% of schools remaining in the identical status quintile), whereas growth points exhibit low temporal persistence ($r = 0.358$, with only 31.3% remaining in the identical growth quintile).

---

## 3. Section B: What Changed in the Calibration

| Dimension | Initial Implementation | Calibrated Implementation | Impact / Rationale |
|:---|:---|:---|:---|
| **Sample B (Conventional Universe)** | 2,039 schools (2025) | **2,031 schools** (2025) | Filtered out 8 NCES CCD-classified virtual schools and alternative programs. |
| **Composite Subject Completeness** | Pandas default (`skipna=True`) | **Strict complete cases (`skipna=False`)** | Requires complete data in both ELA and Math. In 2025: 2,027 complete status cases (2 Math-only excluded); 1,984 complete growth cases (1 ELA-only, 2 Math-only excluded). |
| **Weighted Correlation** | Ordinary Pearson $r$ reported on weighted rows | **Exact enrollment-weighted Pearson $r_w$** | Implements $\text{cov}_w(x, y)/\sqrt{\text{var}_w(x)\text{var}_w(y)}$. Weighted status $r_w = -0.7204$ (vs unweighted $-0.6511$). |
| **Growth Model Diagnostics** | Labeled "exact replication" using FRPL | **Split into Direct Certification Reproduction vs. FRPL Sensitivity** | Direct certification obtained via NCES CCD; aligns with DESE Table 2 economic metric. |
| **APR Growth Impact** | Evaluative "equity brake" claim based on $R^2$ contrast | **Exact Point-Accounting Counterfactual Decomposition** | Growth points mathematically removed from actual APR points possible/earned. Excluding growth increases APR poverty association from $R^2 = 18.3\%$ to $R^2 = 31.5\%$. |
| **Starting Position Validation** | In-sample OLS $R^2$ only | **5-Fold GroupKFold Cross-Validation (by District)** | Out-of-sample CV-$R^2$ for prior achievement alone is **88.04%**; adding poverty adds **+0.0022**; adding full demographics adds **+0.0015**. |
| **Longitudinal Stability** | Single transition (2024 $\to$ 2025) | **Multi-year panel (2023 $\to$ 2024 and 2024 $\to$ 2025) + Quintile Transitions** | Demonstrated identical stability across both transitions ($r \approx 0.936$ status vs $r \approx 0.356$ growth). |
| **Quadrant Terminology** | Loaded evaluative language ("entry privileges", "complacency") | **Neutral descriptive labeling** | Strictly neutral terms: High Status / High Growth, High Status / Low Growth, Low Status / High Growth, Low Status / Low Growth. |
| **Tie Handling at Median Growth** | Undocumented inclusive split | **Explicit tie documentation & sensitivity** | 365 schools (18.4%) tie at median growth (62.5%). Sensitivity reported across inclusive ($\ge 62.5\%$), strict ($> 62.5\%$), and percentile ranks. |

---

## 4. Section C: Exact Replication and Reproduction Status

The table below reconciles all growth model demographic correlations against official state benchmarks published in DESE's *Growth Model Procedures and Results* (Table 2):

| School Year | Subject | Diagnostic Type | Demographic Metric | Official DESE r | Calculated r | Delta (Calc - Off) | p-value | N Schools | Calibration Status |
|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **2024** | **Math** | `DC` | Direct Certification % | **-0.04** | **-0.022** | +0.018 | 0.32 | 1,980 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **ELA** | `DC` | Direct Certification % | **-0.03** | **-0.013** | +0.017 | 0.57 | 1,980 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Science** | `DC` | Direct Certification % | **-0.11** | **-0.088** | +0.022 | 0.00 | 1,787 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Math** | `FRL` | Free/Reduced Lunch % | **-0.02** | **-0.020** | -0.000 | 0.37 | 1,990 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **ELA** | `FRL` | Free/Reduced Lunch % | **-0.01** | **-0.008** | +0.002 | 0.74 | 1,990 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Science** | `FRL` | Free/Reduced Lunch % | **-0.06** | **-0.057** | +0.003 | 0.01 | 1,794 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Math** | `URM` | DESE URM (Black+Hisp+Native) | **0.00** | **+0.036** | +0.036 | 0.11 | 1,990 | `ROUGH_MATCH` |
| **2024** | **ELA** | `URM` | DESE URM (Black+Hisp+Native) | **+0.06** | **+0.036** | -0.024 | 0.10 | 1,990 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Science** | `URM` | DESE URM (Black+Hisp+Native) | **-0.13** | **-0.102** | +0.028 | 0.00 | 1,794 | `ROUGH_MATCH` |
| **2025** | **Math** | `DC` | Direct Certification % (2024 Baseline) | **+0.02** | **+0.007** | -0.013 | 0.75 | 1,973 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **ELA** | `DC` | Direct Certification % (2024 Baseline) | **+0.03** | **+0.030** | +0.000 | 0.18 | 1,973 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Science** | `DC` | Direct Certification % (2024 Baseline) | **-0.06** | **-0.073** | -0.013 | 0.00 | 1,775 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Math** | `FRL` | Free/Reduced Lunch % | **-0.01** | **-0.020** | -0.010 | 0.37 | 1,987 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **ELA** | `FRL` | Free/Reduced Lunch % | **+0.01** | **+0.027** | +0.017 | 0.22 | 1,986 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Science** | `FRL` | Free/Reduced Lunch % | **-0.05** | **-0.062** | -0.012 | 0.01 | 1,784 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Math** | `URM` | DESE URM (Black+Hisp+Native) | **+0.06** | **+0.057** | -0.003 | 0.01 | 1,987 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **ELA** | `URM` | DESE URM (Black+Hisp+Native) | **+0.08** | **+0.091** | +0.011 | 0.00 | 1,986 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Science** | `URM` | DESE URM (Black+Hisp+Native) | **-0.09** | **-0.075** | +0.015 | 0.00 | 1,784 | `EXACT_OR_TIGHT_MATCH` |

**Audit Result**: 16 out of 18 benchmarks achieve an `EXACT_OR_TIGHT_MATCH` ($|\Delta r| \le 0.024$). The remaining two benchmarks achieve a `ROUGH_MATCH` ($|\Delta r| \le 0.036$). Zero benchmarks diverge.

---

## 5. Section D: Official vs. Analyst-Created Metrics

To eliminate ambiguity, all variables analyzed in this study are explicitly designated as either official state accountability metrics or analyst-derived constructs:

| Variable Name in Panel | Classification | Official Source / Calculation Formula | Substantive Role |
|:---|:---:|:---|:---|
| `apr_pct` | **OFFICIAL DESE METRIC** | `mo_apr_summary_{yr}_building.xlsx` (`TOTAL_POINTS_EARNED_PCT`) | Primary MSIP 6 public accountability rating |
| `apr_points_earned` | **OFFICIAL DESE METRIC** | Total APR points earned (`TOTAL_POINTS_EARNED`) | Numerator of official APR score |
| `apr_points_possible` | **OFFICIAL DESE METRIC** | Total APR points possible (`TOTAL_POINTS_POSSIBLE`) | Denominator of official APR score |
| `ela_status_mpi` | **OFFICIAL DESE METRIC** | ELA MAP Performance Index (`ELA_ALL_STATUS_MPI`) | Official continuous academic achievement status in ELA |
| `math_status_mpi` | **OFFICIAL DESE METRIC** | Math MAP Performance Index (`MATH_ALL_STATUS_MPI`) | Official continuous academic achievement status in Math |
| `science_status_mpi` | **OFFICIAL DESE METRIC** | Science MAP Performance Index (`SCIENCE_ALL_STATUS_MPI`) | Official continuous academic achievement status in Science |
| `ela_growth_pts_pct` | **OFFICIAL DESE METRIC** | ELA Growth Points Earned % (`ELA_ALL_GROWTH_POINTS_EARNED_PCT`) | Discretized growth points (0, 25, 50, 75, 100%) |
| `math_growth_pts_pct` | **OFFICIAL DESE METRIC** | Math Growth Points Earned % (`MATH_ALL_GROWTH_POINTS_EARNED_PCT`) | Discretized growth points (0, 25, 50, 75, 100%) |
| `science_growth_pts_pct` | **OFFICIAL DESE METRIC** | Science Growth Points Earned % (`SCIENCE_ALL_GROWTH_POINTS_EARNED_PCT`) | Discretized growth points (0, 25, 50, 75, 100%) |
| `attendance_pct` | **OFFICIAL DESE METRIC** | Proportional Attendance Rate (`PROPORTIONAL_ATTENDANCE_TOTAL_PCT`) | Missouri 90/90 attendance standard |
| `direct_cert_pct` | **OFFICIAL FEDERAL METRIC** | NCES CCD Directory (`direct_certification / enrollment * 100`) | Headcount of students certified for free meals without application |
| `analyst_composite_status_mpi` | **ANALYST-DERIVED METRIC** | `mean(ela_status_mpi, math_status_mpi, skipna=False)` | Complete-case academic achievement status composite |
| `apr_growth_pts_pct` | **ANALYST-DERIVED METRIC** | `mean(ela_growth_pts_pct, math_growth_pts_pct, skipna=False)` | Complete-case two-subject APR growth points percentage |
| `dese_urm_pct` | **ANALYST-DERIVED METRIC** | `Black% + Hispanic% + Native American%` | Reconstructed demographic metric matching DESE Growth Model definition |
| `sample_b_conventional` | **ANALYST-DERIVED METRIC** | Institutional filter excluding virtual, alt, CTE, sped, and PK-2 | Primary conventional accountability analytic universe |

---

## 6. Section E: Remaining Unknowns and Methodological Caveats

1. **Growth Measures $\neq$ Causal School Effectiveness**:
   - The value-added growth model conditions on prior test history and grade-level baselines, successfully attenuating cross-sectional poverty correlations.
   - However, value-added residuals do not fully control for unobserved student sorting, family resources, out-of-school tutoring, peer effects, or test measurement error. They must be interpreted as *adjusted performance indicators*, not pure causal school value-add.
2. **Discretization of Public Growth Points**:
   - DESE calculates student-level value-added growth continuously, but collapses building results into five discrete percentage tiers (0%, 25%, 50%, 75%, 100%) in public reporting.
   - This discretization introduces clustering and ties (18.4% of schools tie at 62.5%), attenuating annual variance and slightly dampening correlations.
3. **Pending A–F Pilot Ratings**:
   - While the Missouri State Board of Education approved the A–F framework in September 2026, building-level pilot letter grades have not been officially published. Stage II analysis will commence once pilot letter grades are released.
4. **Small-School Sampling Variability**:
   - Smaller schools ($N < 100$) exhibit higher year-over-year growth point volatility due to smaller cohort sizes, underscoring that single-year growth signals contain substantial sampling noise.
