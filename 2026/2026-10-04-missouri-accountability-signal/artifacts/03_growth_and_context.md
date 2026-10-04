# Artifact 03: Value-Added Student Growth and Context

## 1. Executive Summary

This artifact addresses **Research Question 2 (Growth)**, **Research Question 4 (Component Decomposition)**, and **Research Question 5 (Status versus Growth)**:
> *How strongly is Missouri's value-added growth measure associated with socioeconomic composition, and do schools with high academic achievement necessarily produce high student growth?*

### Critical Epistemic Framing
This study measures the properties of Missouri's accountability signals. Value-added growth is an econometric construct that conditions on prior student achievement and testing histories. Finding near-zero correlation between growth and poverty does **not** prove that poverty has no impact on student learning over time; rather, it demonstrates that Missouri's growth model mathematically succeeds in neutralizing the cross-sectional correlation between school poverty and measured school progress.

### Key Empirical Takeaways (2025 Cross-Section)
1. **Orthogonality to School Poverty**: Statewide across 1,995 conventional schools with valid growth data, composite growth points earned percentage is virtually uncorrelated with school Free/Reduced Lunch rate ($r = +0.0065, p = 0.771$, Spearman $\rho = -0.0029, R^2 = 0.00004$).
2. **Subject Consistency**: Both English Language Arts ($r = +0.0266, p = 0.235$) and Mathematics growth ($r = -0.0169, p = 0.450$) show small and statistically insignificant associations with poverty. Science exhibits a slight, borderline negative correlation ($r = -0.0608, p = 0.010, R^2 = 0.37\%$).
3. **Status Does Not Guarantee Growth**: The correlation between school academic achievement status (MPI) and student growth is weak ($r = 0.2099, R^2 = 0.0441$), indicating that 95.6% of the variance in growth is uncoupled from status achievement.
4. **Substantial Prevalence of Off-Diagonal Schools (2x2 Matrix)**:
   - **25.3% of conventional schools (505 schools)** are **Low Achievement / High Growth**: high-poverty schools (mean FRPL 71.7%) whose students make above-average academic progress despite low starting scores.
   - **17.0% of conventional schools (338 schools)** are **High Achievement / Low Growth**: low-poverty schools (mean FRPL 39.1%) with high absolute test scores that fail to produce average student gains.

---

## 2. Statewide Empirical Findings (2025 Cross-Section)

The table below presents bivariate regression and correlation statistics between Value-Added Growth points earned percentage and Free/Reduced-Price Lunch (FRPL) percentage:

| Analytic Specification | N Schools | Pearson r | p-value | Spearman ρ | OLS R² | Slope β | Std Error |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **All Conventional (Unweighted)** | 1,995 | **+0.0065** | 0.771 | -0.0029 | **0.0000** | +0.0056 | 0.0192 |
| **All Conventional (Student-Weighted)** | 1,993 | **+0.0061** | 0.786 | -0.0033 | **0.0031** | -0.0480 | 0.0194 |
| **Non-CEP Schools Only** | 1,536 | **-0.0214** | 0.401 | -0.0315 | **0.0005** | -0.0265 | 0.0316 |
| **CEP Participating Schools Only** | 459 | **+0.0148** | 0.752 | +0.0122 | **0.0002** | +0.0156 | 0.0495 |

Regardless of whether schools are weighted equally, weighted by student enrollment, or restricted to Non-CEP schools with audited income documentation, the relationship between value-added growth and school poverty is substantively zero ($|r| \le 0.021$).

---

## 3. Disaggregation by School Level

Unlike academic status—which varies sharply by school configuration—growth remains uniformly uncoupled from poverty across all school levels:

| School Level | N Schools | Mean Growth % Pts | Pearson r vs. FRPL | p-value | OLS R² | Slope β (SE) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Elementary Schools (PK–5/6)** | 1,038 | 61.9% | **-0.0017** | 0.957 | **0.0000** | -0.0016 (0.0292) |
| **Middle Schools (6–8)** | 350 | 62.4% | **-0.0868** | 0.105 | **0.0075** | -0.1050 (0.0647) |
| **High Schools (9–12)** | 415 | 61.3% | **-0.0094** | 0.849 | **0.0001** | -0.0079 (0.0416) |
| **Mixed / Broad Span (K–12, K–8)** | 192 | 61.7% | **+0.1035** | 0.153 | **0.0107** | +0.1082 (0.0754) |

Even in Middle Schools—where poverty explains 58.2% of status achievement—it explains less than **0.8% of the variance in student growth** ($r = -0.0868, p = 0.105$).

---

## 4. Subject-Level Growth Diagnostics

| Content Area | Growth Metric | N Schools | Mean % Pts | Pearson r vs. FRPL | p-value | OLS R² |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **Composite Growth** | `composite_growth_pts_pct` | 1,995 | 61.9% | **+0.0065** | 0.771 | **0.0000** |
| **English Language Arts (ELA)** | `ela_growth_pts_pct` | 1,993 | 61.9% | **+0.0266** | 0.235 | **0.0007** |
| **Mathematics** | `math_growth_pts_pct` | 1,994 | 61.9% | **-0.0169** | 0.450 | **0.0003** |
| **Science** | `science_growth_pts_pct` | 1,789 | 61.5% | **-0.0608** | 0.010 | **0.0037** |

Mathematics and ELA growth show zero empirical association with poverty. Science exhibits a slight negative correlation ($r = -0.0608$), which closely mirrors the pattern identified in DESE's internal growth model diagnostics (see [`artifacts/growth_replication_check.md`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-missouri-accountability-signal/artifacts/growth_replication_check.md)).

---

## 5. Status versus Growth 2x2 Matrix Analysis

To answer **Research Question 5**, we categorize all 1,994 conventional schools with both measures in 2025 into four quadrants based on statewide median thresholds:
- **Median Academic Status MPI**: 380.90
- **Median Value-Added Growth**: 62.50%

| Quadrant Designation | Number of Schools | Share of Conventional Schools | Mean School FRPL % | Mean Status MPI | Mean Growth % Pts |
|:---|:---:|:---:|:---:|:---:|:---:|
| **High Achievement / High Growth** | 659 | **33.0%** | 38.9% | 403.4 | 80.6% |
| **High Achievement / Low Growth** | 338 | **17.0%** | 39.1% | 400.3 | 43.1% |
| **Low Achievement / High Growth** | 505 | **25.3%** | **71.7%** | 352.1 | 80.8% |
| **Low Achievement / Low Growth** | 492 | **24.7%** | **62.8%** | 353.4 | 43.4% |
| **Total Conventional Universe** | **1,994** | **100.0%** | **53.7%** | **377.6** | **61.9%** |

### Key Accountability Implications of the 2x2 Breakdown
1. **The "High-Growth, High-Poverty" Phenomenon (Quadrant 3)**:
   - More than 1 in 4 Missouri public schools (505 schools) serve severely disadvantaged student populations (mean FRPL 71.7%) and achieve low absolute test scores (mean MPI 352.1), but produce **top-half student growth** (mean growth points 80.8%).
   - Under an accountability framework that heavily weights absolute achievement, these schools are flagged as low-performing despite demonstrating above-average instructional effectiveness.
2. **The "High-Status Complacency" Phenomenon (Quadrant 2)**:
   - 338 schools (17.0% of the state) educate low-poverty student populations (mean FRPL 39.1%) and post high absolute scores (mean MPI 400.3), but produce **below-average student growth** (mean growth points 43.1%).
   - These schools maintain high public standing solely due to student entry advantages rather than school-level academic value-add.

---

## 6. Contrast with Total APR Percentage

How does the existing Annual Performance Report (APR) synthesize these two opposing signals?
- **Achievement Status vs. FRPL**: $r = -0.6444, R^2 = 41.52\%$
- **Value-Added Growth vs. FRPL**: $r = +0.0065, R^2 = 0.0042\%$
- **Total APR Percentage vs. FRPL**: $r = -0.4172, R^2 = 17.41\%$ ($\beta = -0.2287, SE = 0.0110$)

Because MSIP 6 combines absolute status (which correlates at -0.64) with growth (which correlates at 0.00), continuous improvement, and attendance, the resulting summary APR percentage exhibits a moderate negative correlation ($r = -0.4172$). The growth component acts as an equity brake: without growth, Missouri's accountability scores would track school poverty at twice the current rate ($R^2$ of 41.5% vs 17.4%).

---

## 7. Graphical Visualization

The scatter plot below displays school growth plotted against Free/Reduced Lunch percentage:

![Figure 2: Value-Added Growth vs. Poverty](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-missouri-accountability-signal/artifacts/figures/02_growth_vs_poverty.png)
