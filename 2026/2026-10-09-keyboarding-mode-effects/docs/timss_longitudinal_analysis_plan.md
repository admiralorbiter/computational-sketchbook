# Pre-Registration & Statistical Analysis Plan: TIMSS 2019–2023 Longitudinal Attribution (Study D)

**Document**: `docs/timss_longitudinal_analysis_plan.md`  
**Author**: Computational Sketchbook Observatory  
**Date**: October 2026 (Study D Frozen Specification)  
**Status**: Pre-Registered Research Protocol (Frozen Prior to Outcome Estimation)  

---

## 1. Research Objectives & Epistemic Boundaries

### Central Empirical Question
Between 2019 and 2023, the reported average mathematics achievement of U.S. fourth graders declined by **18 scale score points** (from 535 to 517). In parallel, Study A established that fourth graders faced a within-school **$-2.73$ percentage-point penalty** on constructed-response items under digital administration.

This investigation addresses two core questions:
1. **The Longitudinal Format Question**: Did U.S. fourth-grade mathematics performance decline disproportionately on constructed-response (CR) items relative to multiple-choice (MC) items between 2019 and 2023?
2. **The Measurement vs. Latent Ability Question**: Does any observed format divergence exceed what would be expected from a general decline in mathematical ability given the non-linear, floor-free item response functions of constructed-response questions?

### Epistemic Demarcation & Guardrails
1. **Level Differences vs. Trend Attribution**: A constant digital interface penalty drops out of longitudinal first differences ($\Delta_{2023-2019}$). For digital assessment to explain a downward score trend, the format penalty must have widened over time, or the assessment composition must have shifted toward vulnerable formats.
2. **Prohibition of Scale-Score Division Fallacy**: Researchers must never divide raw percentage-point changes $\Delta p$ by the 18-point IRT scale decline $\Delta \text{Scale}$.
3. **Correlation vs. Causation in Repeated Digital Cohorts**: Because both the 2019 and 2023 cohorts were tested digitally, an observed widening of the constructed-response deficit is consistent with increased interface friction, but equally consistent with disproportionate post-pandemic instructional losses in multi-step problem solving and written mathematical reasoning.

---

## 2. Sample Definitions & Data Sources

### Primary Analytical Sample (Standard eTIMSS Linkage)
- **Item Universe**: Exactly **84 common scaling items** (32 Multiple Choice, 52 Constructed Response) administered in both 2019 and 2023 across the 7 standard non-PSI trend blocks.
- **2019 Microdata**: `data/raw/timss_2019/asausam7.sav` ($N = 8,776$ students across 287 schools and 507 classrooms; Booklets 1–14).
- **2023 Microdata**: `data/raw/timss_2023/asausam8.sav` ($N = 9,090$ students across 242 schools and 479 classrooms; Booklets 1–14).
- **Sampling Weights**: Student weight `TOTWGT` in `asausam7.sav` and `asausam8.sav`, replicating official published national benchmarks (534.73 $\to$ 535.0 in 2019; 516.93 $\to$ 517.0 in 2023).

### Secondary Robustness Sample (PSI Inclusion)
- **Item Universe**: Exactly **100 common scaling items** (33 Multiple Choice, 67 Constructed Response) adding the 16 scaling items from interactive PSI block `A_MD4`.
- **2019 Microdata**: `data/raw/timss_2019/asausaz7.sav` ($N = 10,029$ students, Booklets 1–16) with recalibrated `TOTWGT` (replicated 5-PV mean = 533.53).
- **2023 Microdata**: `data/raw/timss_2023/asausam8.sav` ($N = 9,090$ students).

### The 31-Item Historical Mode-Sensitivity Subsample
- Exactly **31 common scaling items** (14 Multiple Choice, 17 Constructed Response) appearing in:
  1. The 2019 Paper Bridge administration ($N = 1,652$ students, Study A).
  2. The 2019 Digital eTIMSS administration ($N = 8,776$ students, Study A/C).
  3. The 2023 Digital group-adaptive administration ($N = 9,090$ students, Study C/D).
- Serves as an exploratory bridge linking empirical 2019 mode vulnerability to subsequent longitudinal change.

---

## 3. Outcome Metrics & Scoring Rules

### Scored Item Accuracy ($Y_{ijt}$)
For student $i$ on item $j$ in year $t \in \{2019, 2023\}$:
- **1-Point Items**: Full credit ($Y = 1.0$) for correct responses (code 10–19); zero ($Y = 0.0$) for incorrect responses (code 70–79), omitted responses (code 99), and not-reached responses (code 96).
- **2-Point Items**: Full credit ($Y = 1.0$) for 2-point responses (code 20–29); partial credit ($Y = 0.5$) for 1-point responses (code 10–19); zero ($Y = 0.0$) for incorrect, omitted, or not-reached.
- **Unadministered Items**: If an item was not in the student's assigned booklet, $Y_{ijt}$ is treated as system-missing (`NaN`) and excluded from the item denominator.

### IEA PSI Sensitivity Protocol
In IEA's official 2019 PSI scaling, not-reached items in Booklets 15–16 were treated as unadministered due to 34% noncompletion. In Study D:
- **Specification 1 (Standard)**: All not-reached items scored zero.
- **Specification 2 (IEA PSI Convention)**: Not-reached items in block `A_MD4` treated as unadministered.

---

## 4. Statistical Models & Estimands

### Layer A: Repeated Cross-Sections Difference-in-Differences
The primary empirical model is:
$$Y_{ijt} = \alpha_j + \lambda_t + \beta (\text{CR}_j \times \text{Post2023}_t) + \mathbf{X}_{it}' \gamma + \epsilon_{ijt}$$
where:
- $\alpha_j$ are **item fixed effects** (absorbing baseline item difficulty).
- $\lambda_t$ is the **year fixed effect** (measuring the baseline trend on Multiple Choice items).
- $\text{CR}_j$ is an indicator for Constructed Response format.
- $\beta$ is the **Difference-in-Differences estimand**:
  $$\beta = (\text{CR}_{2023} - \text{CR}_{2019}) - (\text{MC}_{2023} - \text{MC}_{2019})$$
- Standard errors are clustered at the school level (`IDSCHOOL`) and evaluated against survey replication weights (150 BRR/JK2 replicate weights).

#### Prespecified Sensitivity Adjustments:
1. **Domain-by-Year Interactions**: Adding $\text{Domain}_j \times \text{Post2023}_t$ to prevent topic shifts from biasing $\beta$.
2. **Booklet Exposure Weights**: Student-normalized vs. raw sampling weights.
3. **100-Item Pool**: Estimating the model with and without PSI items.

---

### Layer B: IRT Expected-Proficiency Shift Benchmark
Because CR items have steeper discrimination and lack guessing floors, a general decline in math ability produces a larger raw-score drop on CR items even with zero interface drift.

1. **Expected Item Curve**:
   For each item $j$, let $P_j(Y=k \mid \theta)$ be its calibrated item response function.
   Expected score under proficiency distribution $F_t(\theta)$:
   $$\widehat{p}_{jt}^0 = \int E[Y_j \mid \theta] \, dF_t(\theta)$$
2. **Expected Format Divergence**:
   $$\beta_{\text{expected}} = \left(\frac{1}{N_{\text{CR}}} \sum_{j \in \text{CR}} \Delta \widehat{p}_j^0\right) - \left(\frac{1}{N_{\text{MC}}} \sum_{j \in \text{MC}} \Delta \widehat{p}_j^0\right)$$
3. **Excess Format Divergence**:
   $$\boxed{\beta_{\text{excess}} = \beta_{\text{observed}} - \beta_{\text{expected}}}$$
   - If $\beta_{\text{excess}} \approx 0$, the larger CR decline is fully explained by general mathematical learning loss under standard psychometric test theory.
   - If $\beta_{\text{excess}} < -2.0$ pp, there is evidence of format-specific differential item functioning (DIF) or measurement drift.

---

### Layer C: Exact Non-Response & Pacing Accounting Decomposition
Using the accounting identity $E[Y] = P(\text{attempt}) \cdot E[Y \mid \text{attempt}]$, we decompose the observed score change:
$$\Delta E[Y] = \underbrace{\Delta A \cdot \bar{S}}_{\text{Completion Component}} + \underbrace{\Delta S \cdot \bar{A}}_{\text{Attempted Performance Component}}$$
where $A = 1 - P(\text{omitted}) - P(\text{not reached})$ and $S$ is accuracy among attempted items.
- Estimated separately for Multiple Choice and Constructed Response.

---

### Layer D: Historical Mode-Sensitivity Linkage (31 Items)
For the 31 items observed in 2019 paper, 2019 digital, and 2023 digital:
- Define 2019 mode vulnerability: $M_j = P_{2019,\text{digital},j} - P_{2019,\text{paper},j}$.
- Define 2019–2023 longitudinal change: $T_j = P_{2023,\text{digital},j} - P_{2019,\text{digital},j}$.
- Model:
  $$T_j = \gamma_0 + \gamma_1 M_j + \mathbf{Z}_j' \delta + u_j$$
- **Mechanical Correlation Guardrail**: Split the 2019 digital sample into two independent random halves ($S_1, S_2$). Compute $M_j$ using $S_1$ and $T_j$ using $S_2$ to eliminate spurious correlated sampling noise.

---

### Layer E: Behavioral Screen Timing Models (78 Screens)
Student-level log-duration models on the 78 primary screens:
$$\ln(\text{Duration}_{ist}) = \mu_s + \tau_t + \theta (\text{CR}_s \times \text{Post2023}_t) + \mathbf{B}_{ist}' \psi + \nu_{ist}$$
where $\mathbf{B}_{ist}$ controls for block sequence (Part 1 vs. Part 2 of booklet) and group-adaptive difficulty assignment.

---

### Layer F: Scale-Score Counterfactual Scenario Modeling
To bound the potential contribution of measurement drift to the national 18-point scale score decline without the division fallacy:
1. Estimate counterfactual 2023 scale scores under a scenario where the excess CR drift is set to zero:
   $$S_{2023,\text{counterfactual}} = \mathcal{M}\left(\theta \mid \mathbf{Y}_{\text{adj}}\right)$$
2. Compute the scenario scale difference:
   $$\Delta_{\text{scenario}} = S_{2023,\text{counterfactual}} - S_{2023,\text{observed}}$$
3. Strictly report as: "Share of observed score decline under specified measurement counterfactual," never "Percentage of decline caused by technology."

---

## 5. Predefined Decision Benchmarks

| Estimated $\beta_{\text{observed}}$ or $\beta_{\text{excess}}$ | Statistical Threshold | Substantive Interpretation | Inference Boundaries |
| :--- | :--- | :--- | :--- |
| **$\beta < -2.0$ pp** | Negative & Statistically Significant ($p < 0.05$) | **Widening Format Disparity** | Consistent with expanding interface friction, but equally consistent with post-pandemic instructional losses in multi-step problem solving and written reasoning. |
| **$-2.0 \le \beta \le +2.0$ pp** | Statistically Indistinguishable from Zero (with tight 95% CI) | **Format-Parallel Trend** | Inconsistent with an expanding format penalty. Point estimate inside interval is NOT proof of parallel trend if CI is wide (e.g., spanning $\pm 4$ pp). Equivalence test must reject $\pm 2.0$ pp bound. |
| **$\beta > +2.0$ pp** | Positive & Statistically Significant ($p < 0.05$) | **Constructed-Response Resilience** | Inconsistent with expanding keyboarding mode penalty. |

---

## 6. Execution Roadmap & Staging

1. **Phase 1: Pre-Registration & Panel Construction** (`docs/timss_longitudinal_analysis_plan.md` & `src/analyze_timss_longitudinal.py`).
2. **Phase 2: Scored Outcome Estimation** (Difference-in-Differences and decomposition tables).
3. **Phase 3: IRT Expected Benchmark & 31-Item Sensitivity Analysis**.
4. **Phase 4: Screen Process Behavioral Regressions**.
5. **Phase 5: Automated Testing & Verification Suite**.
