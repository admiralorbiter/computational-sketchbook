# Artifact 02: Academic Achievement Status and Student Context

## 1. Executive Summary

This artifact addresses **Research Question 1 (Achievement Status)** and **Research Question 6 (Starting Position)**:
> *When Missouri reports that a school is performing well or poorly based on absolute academic achievement, how strongly does that signal track the socioeconomic composition and starting position of its students?*

### Critical Epistemic Framing
This is an **accountability measurement and predictive decomposition study**, not a causal experiment. These estimates do **not** claim that poverty *causes* lower achievement, nor that schools *cause* low performance. Rather, they establish the degree to which Missouri's existing academic status metric reflects the demographic composition and historical baseline of the student body attending the school.

### Key Empirical Takeaways (2025 Cross-Section)
1. **Strong Baseline Association**: Across Missouri's 2,039 conventional public schools (Sample B), building academic achievement status (MAP Performance Index, MPI) is strongly and negatively associated with student poverty ($r = -0.6444$, Spearman $\rho = -0.6274$, $p < 10^{-230}$).
2. **Predictive Magnitude**: In simple bivariate regression, school poverty accounts for **41.5% of the variance** in statewide achievement status ($R^2 = 0.4152$; student-weighted $R^2 = 0.5085$). Every 10 percentage point increase in school FRPL is associated with an **8.14-point decrease in composite MPI** ($\beta = -0.8137, SE = 0.0214$).
3. **Elevated Gradient in Middle and Elementary Bands**: The relationship is sharpest in middle schools ($r = -0.7628, R^2 = 58.2\%$) and elementary schools ($r = -0.7042, R^2 = 49.6\%$), moderating in high schools ($r = -0.4410, R^2 = 19.4\%$).
4. **Dominance of Prior Starting Position**: When a school's prior-year achievement is known, prior achievement alone accounts for **87.9% of current achievement variance** ($R^2 = 0.8792$). Adding poverty increases explained variance by merely **0.31 percentage points** ($\Delta R^2 = 0.0031$), and adding full demographic controls increases it by only **0.38 percentage points** ($\Delta R^2 = 0.0038$). This demonstrates that student demographic advantages and disadvantages are already deeply embedded in a school's historical baseline.

---

## 2. Statewide Empirical Findings (2025 Cross-Section)

The table below presents bivariate regression and correlation statistics between MAP Performance Index (MPI) and Free/Reduced-Price Lunch (FRPL) percentage across different analytical specifications:

| Analytic Specification | N Schools | Pearson r | p-value | Spearman ρ | OLS R² | Slope β | Std Error |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **All Conventional (Unweighted)** | 2,037 | **-0.6444** | $2.19 \times 10^{-239}$ | -0.6274 | **0.4152** | -0.8137 | 0.0214 |
| **All Conventional (Student-Weighted)** | 2,035 | **-0.6466** | $2.49 \times 10^{-241}$ | -0.6290 | **0.5085** | -0.8755 | 0.0191 |
| **Non-CEP Schools Only** | 1,566 | **-0.5834** | $1.73 \times 10^{-143}$ | -0.5551 | **0.3404** | -0.8437 | 0.0297 |
| **CEP Participating Schools Only** | 471 | **-0.3389** | $4.00 \times 10^{-14}$ | -0.3283 | **0.1149** | -0.5926 | 0.0760 |

### Substantive Interpretation of CEP vs. Non-CEP
In Community Eligibility Provision (CEP) schools, individual lunch applications are not collected, and federal reimbursement is based on direct certification multipliers, causing reported FRPL to concentrate near 100%. This ceiling compresses the variance of measured poverty, attenuating the bivariate correlation ($r = -0.3389$). In Non-CEP schools, where household eligibility is continuously documented, the negative relationship remains pronounced ($r = -0.5834$, $\beta = -0.8437$).

---

## 3. Disaggregation by School Level

Accountability signals behave differently across school organizational configurations:

| School Level | N Schools | Mean FRPL % | Mean Status MPI | Pearson r vs. FRPL | OLS R² | Slope β (SE) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Elementary Schools (PK–5/6)** | 1,043 | 53.9% | 382.2 | **-0.7042** | **0.4959** | -0.8931 (0.0279) |
| **Middle Schools (6–8)** | 350 | 54.1% | 374.3 | **-0.7628** | **0.5819** | -1.1578 (0.0526) |
| **High Schools (9–12)** | 451 | 51.5% | 370.4 | **-0.4410** | **0.1945** | -0.4907 (0.0471) |
| **Mixed / Broad Span (K–12, K–8)** | 193 | 58.7% | 371.4 | **-0.4798** | **0.2302** | -0.5694 (0.0753) |

- **Middle Schools** exhibit the strongest socioeconomic gradient: poverty alone predicts nearly **58.2% of the variance** in middle school MAP performance index, with a steep slope of -1.16 MPI points per 1% poverty.
- **High Schools** display a substantially weaker gradient ($R^2 = 19.5\%$, $\beta = -0.4907$). This reflects greater course selection heterogeneity, differential high school dropout/retention patterns, and the fact that high school accountability relies on End-of-Course (EOC) assessments administered to specific subsets of students rather than universal grade-level cohorts.

---

## 4. Subject-Level Achievement Comparisons

The negative association between absolute performance and poverty is remarkably consistent across academic content areas:

| Content Area | Measure Analyzed | N Schools | Mean MPI | Pearson r vs. FRPL | OLS R² | Slope β (SE) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **English Language Arts (ELA)** | `ela_status_mpi` | 2,035 | 381.1 | **-0.6369** | **0.4056** | -0.7115 (0.0191) |
| **Mathematics** | `math_status_mpi` | 2,037 | 373.2 | **-0.6199** | **0.3842** | -0.9193 (0.0258) |
| **Science** | `science_status_mpi` | 1,854 | 372.5 | **-0.6076** | **0.3692** | -0.7605 (0.0231) |

Mathematics displays the steepest slope ($\beta = -0.9193$), while ELA displays the highest total variance explained ($R^2 = 40.56\%$).

---

## 5. Starting Position and Incremental Information

To answer **Research Question 6**, we test whether student composition measures provide new predictive information once a school's starting performance position is already established:

$$
\text{Model 1: } \text{Achievement}_{2025} = \alpha + \beta_1 \text{Achievement}_{2024} + \epsilon
$$
$$
\text{Model 2: } \text{Achievement}_{2025} = \alpha + \beta_1 \text{Achievement}_{2024} + \beta_2 \text{FRPL}_{2025} + \epsilon
$$
$$
\text{Model 3: } \text{Achievement}_{2025} = \alpha + \beta_1 \text{Achievement}_{2024} + \beta_2 \text{FRPL} + \beta_3 \text{URM} + \beta_4 \text{IEP} + \beta_5 \text{EL} + \epsilon
$$

Across $N = 2,027$ conventional schools with consecutive annual observations:

| Regression Model | Covariates Included | Overall R² | Incremental ΔR² | F-statistic (Model) |
|:---|:---|:---:|:---:|:---:|
| **Model 0 (Poverty Alone)** | FRPL % | 0.4152 | — | 1,444.6 ($p < 10^{-200}$) |
| **Model 1 (Starting Position Alone)** | Prior Year Achievement (2024 MPI) | **0.8792** | Baseline | 14,750.8 ($p = 0.00$) |
| **Model 2 (+ School Poverty)** | Prior Achievement + FRPL % | **0.8823** | **+0.0031** | 7,591.2 ($p = 0.00$) |
| **Model 3 (+ Full Demographics)** | Prior Ach + FRPL + URM + IEP + EL | **0.8830** | **+0.0038** | 3,052.4 ($p = 0.00$) |

### Analytical Conclusion on Starting Position
Prior achievement is an overwhelmingly strong predictor of subsequent achievement ($R^2 = 87.9\%$). Controlling for prior achievement leaves virtually no residual variance that can be explained by poverty or demographics ($\Delta R^2 < 0.4\%$). 

This confirms that:
1. School test scores are fundamentally sticky over time.
2. In an accountability system that rewards high absolute achievement, the metric predominantly rewards schools for the demographic starting positions of the students who walk through their doors.

---

## 6. Graphical Visualization

The scatter plot below illustrates the distribution of 2025 conventional schools across poverty levels, with fitted regression lines for the statewide universe, Non-CEP schools, and CEP schools:

![Figure 1: Academic Achievement vs. Poverty](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-10-04-missouri-accountability-signal/artifacts/figures/01_achievement_vs_poverty.png)
