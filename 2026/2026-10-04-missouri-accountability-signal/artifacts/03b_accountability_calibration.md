# Artifact 03b: Accountability Signal Calibration Review

## 1. Overview and Purpose

This artifact documents the final calibration review of **Phases 0 through 6** for the **Missouri Accountability Signal** project. Following rigorous methodological review, several structural refinements were applied:
1. Distinguishing the official growth diagnostic (**Direct Certification**) from the public socioeconomic metric (**FRPL**), and classifying the 2025 direct-certification result as a **carried-forward sensitivity check** due to federal NCES CCD publication lags.
2. Clarifying that public MSIP 6 growth measures are **discretized accountability points** derived from the state value-added model, not continuous student-level residuals.
3. Renaming analyst-created composite metrics (`analyst_composite_status_mpi` and `apr_growth_pts_pct`) and enforcing strict **complete-case subject requirements**.
4. Implementing an exact **enrollment-weighted Pearson correlation** ($r_w$).
5. Auditing the **APR point-accounting counterfactual decomposition**: enumerating all 8 growth columns (All Students + Student Groups) and proving exact arithmetic reconciliation with official APR points.
6. Conducting **district-grouped cross-validation** (`GroupKFold` across 551 LEAs) for starting position models including proportional attendance and fold-safe imputation.
7. Expanding longitudinal stability across multiple year transitions (**2023 $\to$ 2024** and **2024 $\to$ 2025**) using **tie-preserving and discrete point transition metrics** rather than arbitrary row-order quintiles.
8. Incorporating official **NCES Common Core of Data (CCD)** institutional type and virtual school flags into Sample B.
9. Enforcing strict epistemic discipline: **growth measures do not equate to causal school effectiveness**.

---

## 2. Section A: What Survived the Calibration

The central empirical conclusions of the investigation remain robust, well-supported, and statistically validated across all specifications:

1. **Strong Status/Poverty Association**: Absolute academic achievement status remains heavily associated with student socioeconomic composition ($r = -0.6511$, $R^2 = 42.39\%$, enrollment-weighted $r_w = -0.7204, R^2 = 51.90\%$).
2. **Orthogonality of Public Growth Points to Poverty**: Missouri's reported value-added growth points measure remains virtually uncorrelated with school Free/Reduced Lunch ($r = +0.0027, R^2 = 0.0007\%$, weighted $r_w = -0.0508, R^2 = 0.26\%$) and with Direct Certification ($r = +0.0207, R^2 = 0.04\%$).
3. **Decoupling of Status and Growth**: Status achievement alone linearly explains only **4.27% of cross-school variance** in reported growth points ($r = 0.2067$). Status and growth capture fundamentally distinct dimensions of school performance.
4. **Disproportionate Low-Status / High-Growth Presence**: Between **16.9% and 25.5% of all conventional public schools** (335 to 506 schools) fall into the **Low Status / High Growth** quadrant depending on median split strictness—schools serving high-poverty student populations (mean FRPL 71.6% to 73.5%) that achieve above-average growth points.
5. **Marked Stability Divergence**: Achievement status is highly persistent year-over-year ($r = 0.938$, with 65.8% of schools remaining in the identical status quintile), whereas growth points are substantially less persistent ($r = 0.358$, with exact discrete point match at 22.4% and tie-preserving average rank quintile persistence of 33.2%).

---

## 3. Section B: What Changed in the Calibration

| Dimension | Initial Implementation | Calibrated Implementation | Impact / Rationale |
|:---|:---|:---|:---|
| **Sample B (Conventional Universe)** | 2,039 schools (2025) | **2,031 schools** (2025) | Filtered out 8 NCES CCD-classified virtual schools and alternative programs. |
| **Composite Subject Completeness** | Pandas default (`skipna=True`) | **Strict complete cases (`skipna=False`)** | Requires complete data in both ELA and Math. In 2025: 2,027 complete status cases; 1,984 complete growth cases. Explicit cross-tab confirms that 37 of 47 growth-missing schools are PK–3/K–3 elementary schools where students take their first MAP test and lack prior-grade baseline scores. |
| **Weighted Correlation** | Ordinary Pearson $r$ reported on weighted rows | **Exact enrollment-weighted Pearson $r_w$** | Implements $\text{cov}_w(x, y)/\sqrt{\text{var}_w(x)\text{var}_w(y)}$. Weighted status $r_w = -0.7204$ (vs unweighted $-0.6511$). |
| **Growth Model Diagnostics** | Labeled "exact replication" using FRPL | **Split into Direct Certification Reproduction vs. FRPL Sensitivity** | Direct certification obtained via NCES CCD; 2024 DC replicates DESE Table 2. 2025 DC is explicitly classified as a carried-forward sensitivity check (using 2024 CCD baseline) due to federal data publication schedules. |
| **APR Growth Impact** | Evaluative "equity brake" claim; subtracted all-student growth only | **Audited Point-Accounting Reconciliation of All Growth Points** | Enumerated all 8 growth columns (All Students + Student Groups, max 48 pts). Excluding ALL Growth increases APR poverty association from $R^2 = 18.32\%$ ($r = -0.4280$) to **$R^2 = 40.09\%$ ($r = -0.6332$)**—a 21.8 percentage point attenuation. Excluding all-student growth only yields $R^2 = 31.72\%$ ($r = -0.5632$). Discrepancy with total APR points is 0.0. |
| **Starting Position Validation** | In-sample OLS $R^2$ only | **5-Fold GroupKFold Cross-Validation (by District)** | Includes proportional attendance. CV-$R^2$ for prior achievement is **87.95%** (full sample, N=2,010) and **92.82%** (complete cases, N=958). Adding poverty adds **+0.0024 (+0.24%)**; adding demographics & attendance adds **+0.0019 (+0.19%)** beyond poverty. |
| **Longitudinal Stability** | Single transition (2024 $\to$ 2025) | **Multi-year panel (2023 $\to$ 2024 and 2024 $\to$ 2025) + Tie-Preserving Transition Metrics** | Replaced arbitrary row-order sorting (`rank(method='first')`) with exact discrete levels, 4 official MSIP 6 tiers (38.2% same tier, 83.6% within $\pm 1$), and tie-preserving average rank quintiles (33.2% same quintile). |
| **Quadrant Terminology** | Loaded evaluative language ("entry privileges", "complacency") | **Neutral descriptive labeling** | Strictly neutral terms: High Status / High Growth, High Status / Low Growth, Low Status / High Growth, Low Status / Low Growth. |
| **Tie Handling at Median Growth** | Undocumented inclusive split | **Explicit tie documentation & sensitivity** | 365 schools (18.4%) tie at median growth (62.5%). Sensitivity reported across inclusive ($\ge 62.5\%$) and strict ($> 62.5\%$) splits, avoiding arbitrary row-order sorting. |

---

## 4. Section C: Exact Replication and Reproduction Status

The table below reconciles all growth model demographic correlations against official state benchmarks published in DESE's *Growth Model Procedures and Results* (Table 2):

| School Year | Subject | Diagnostic Type | Benchmark Classification | Demographic Metric | Official DESE r | Calculated r | Delta (Calc - Off) | p-value | N Schools | Calibration Status |
|:---:|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **2024** | **Math** | `DC` | `REPLICATION_BENCHMARK` | Direct Certification Rate | **-0.04** | **-0.022** | +0.018 | 0.32 | 1,980 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **ELA** | `DC` | `REPLICATION_BENCHMARK` | Direct Certification Rate | **-0.03** | **-0.013** | +0.017 | 0.57 | 1,980 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Science** | `DC` | `REPLICATION_BENCHMARK` | Direct Certification Rate | **-0.11** | **-0.088** | +0.022 | 0.00 | 1,787 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Math** | `FRL` | `REPLICATION_BENCHMARK` | Free/Reduced Lunch Rate | **-0.02** | **-0.020** | -0.000 | 0.37 | 1,990 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **ELA** | `FRL` | `REPLICATION_BENCHMARK` | Free/Reduced Lunch Rate | **-0.01** | **-0.008** | +0.002 | 0.74 | 1,990 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Science** | `FRL` | `REPLICATION_BENCHMARK` | Free/Reduced Lunch Rate | **-0.06** | **-0.057** | +0.003 | 0.01 | 1,794 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Math** | `URM` | `REPLICATION_BENCHMARK` | DESE URM (Black+Hisp+Native) | **0.00** | **+0.036** | +0.036 | 0.11 | 1,990 | `ROUGH_MATCH` |
| **2024** | **ELA** | `URM` | `REPLICATION_BENCHMARK` | DESE URM (Black+Hisp+Native) | **+0.06** | **+0.036** | -0.024 | 0.10 | 1,990 | `EXACT_OR_TIGHT_MATCH` |
| **2024** | **Science** | `URM` | `REPLICATION_BENCHMARK` | DESE URM (Black+Hisp+Native) | **-0.13** | **-0.102** | +0.028 | 0.00 | 1,794 | `ROUGH_MATCH` |
| **2025** | **Math** | `DC` | `CARRIED_FORWARD_SENSITIVITY` | Direct Certification (2024 CCD Baseline) | **+0.02** | **+0.007** | -0.013 | 0.75 | 1,973 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **ELA** | `DC` | `CARRIED_FORWARD_SENSITIVITY` | Direct Certification (2024 CCD Baseline) | **+0.03** | **+0.030** | +0.000 | 0.18 | 1,973 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Science** | `DC` | `CARRIED_FORWARD_SENSITIVITY` | Direct Certification (2024 CCD Baseline) | **-0.06** | **-0.073** | -0.013 | 0.00 | 1,775 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Math** | `FRL` | `REPLICATION_BENCHMARK` | Free/Reduced Lunch Rate | **-0.01** | **-0.020** | -0.010 | 0.37 | 1,987 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **ELA** | `FRL` | `REPLICATION_BENCHMARK` | Free/Reduced Lunch Rate | **+0.01** | **+0.027** | +0.017 | 0.22 | 1,986 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Science** | `FRL` | `REPLICATION_BENCHMARK` | Free/Reduced Lunch Rate | **-0.05** | **-0.062** | -0.012 | 0.01 | 1,784 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Math** | `URM` | `REPLICATION_BENCHMARK` | DESE URM (Black+Hisp+Native) | **+0.06** | **+0.057** | -0.003 | 0.01 | 1,987 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **ELA** | `URM` | `REPLICATION_BENCHMARK` | DESE URM (Black+Hisp+Native) | **+0.08** | **+0.091** | +0.011 | 0.00 | 1,986 | `EXACT_OR_TIGHT_MATCH` |
| **2025** | **Science** | `URM` | `REPLICATION_BENCHMARK` | DESE URM (Black+Hisp+Native) | **-0.09** | **-0.075** | +0.015 | 0.00 | 1,784 | `EXACT_OR_TIGHT_MATCH` |

**Audit Result**: Across the 15 contemporaneous replication benchmarks (2024 DC, 2024–25 FRL, 2024–25 URM): **13** achieve an `EXACT_OR_TIGHT_MATCH` ($|\Delta r| \le 0.025$) and **2** achieve a `ROUGH_MATCH` ($|\Delta r| \le 0.036$). Zero benchmarks diverge. The 3 carried-forward 2025 DC sensitivity checks all track within $|\Delta r| \le 0.013$.

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
   - DESE calculates student-level value-added growth continuously, but collapses building results into discrete percentage tiers (0%, 25%, 50%, 75%, 100%) in public reporting.
   - This discretization introduces substantial clustering (18.4% of schools tie at exactly 62.5%).
3. **Pending A–F Pilot Ratings**:
   - While the Missouri State Board of Education approved the A–F framework in September 2026, building-level pilot letter grades have not been officially published. Stage II analysis will commence once pilot letter grades are released.
4. **Growth Point Volatility and Decomposition Boundary**:
   - Growth points are substantially less persistent; this study does not decompose how much of that difference reflects true change, sampling variability, model estimation, or discretization.

