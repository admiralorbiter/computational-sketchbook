"""
Notebook Generation Script: 06_timss_longitudinal_attribution.ipynb
Generates and executes the Study D longitudinal attribution notebook establishing:
1. Difference-in-Differences format models across primary 84 and secondary 100 pools (Table 21)
2. Non-response completion vs attempted performance decomposition with content-domain nuances (Table 22)
3. Historical 31-item mode sensitivity linkage from Study A (Table 23)
4. Screen-level process timing panel across 77 pure screens (Table 24)
5. Exploratory synthetic IRT sensitivity demonstration across parameter grids (Table 25)
6. Calibrated synthesis separating Track 1 (interface mechanism) from Track 2 (trend attribution)
"""

from pathlib import Path
import nbformat as nbf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOKS_DIR / "06_timss_longitudinal_attribution.ipynb"


def build_longitudinal_notebook():
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3 (ipykernel)",
        "language": "python",
        "name": "python3"
    }
    nb.metadata["language_info"] = {
        "name": "python",
        "version": "3.12.0"
    }

    cells = []

    # ==============================================================================
    # Title & Study D Research Framing
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""# TIMSS 2019–2023 Grade 4 Longitudinal Attribution & Psychometric Evaluation
## Testing Mode Sensitivity, Process Timing, and Non-Response Decay Against the National Mathematics Score Decline (`06_timss_longitudinal_attribution`)

**Author**: Computational Sketchbook Observatory  
**Date**: October 2026 (Study D Longitudinal Attribution Edition)  
**Primary Datasets**: 
- TIMSS 2019 Grade 4 U.S. Public-Use Microdata (`asausam7.sav`, `asausaz7.sav`)
- TIMSS 2023 Grade 4 U.S. Public-Use Microdata (`asausam8.sav`, `aspusam8.sav`)
- Audited Primary Common-Item Inventory (84 Standard Scaling Items: 32 Multiple Choice, 52 Constructed Response)
- Secondary Robustness Pool (100 Scaling Items including Problem Solving and Inquiry)
- Deduplicated Screen-Level Process Timing Panel (77 Pure Screens, $N = 190,058$ examinee-screen interactions)  
**Pre-Registered Protocol**: [`docs/timss_longitudinal_analysis_plan.md`](../docs/timss_longitudinal_analysis_plan.md)  
**Experimental Protocol**: [`docs/experimental_design_protocol.md`](../docs/experimental_design_protocol.md)

---

### Executive Summary & Methodological Demarcation

Between 2019 and 2023, the reported average mathematics achievement of U.S. fourth-grade students on the TIMSS international assessment declined by **18 scale score points** (from 535 to 517, $SE = 2.4$, $p < 0.001$). In parallel, NAEP fourth-grade mathematics scores declined by **3 scale score points** (from 240 in 2019 to 237 in 2024).

In Study A, our within-school item-controlled analysis of TIMSS 2019 demonstrated that fourth graders suffered a robust **$-2.73$ percentage-point penalty** on constructed-response mathematics questions under digital administration ($-2.58$ pp among officially invariant items).

This raises the central empirical question for **Track 2 (National Trend Attribution)**:  
> **Did interface and response-entry friction contribute to the post-2019 score drop, or is the score decline driven primarily by post-pandemic learning loss?**

#### Calibrated Scientific Findings
The empirical evidence provides meaningful constraints on what drove the 2019–2023 score decline, but requires careful epistemic boundaries:

1. **Difference-in-Differences Format Divergence (Table 21)**:  
   Across the primary 84 common scaling items ($N = 214,056$ student-by-item observations across 12,060 examinees), the additional constructed-response decline relative to multiple choice is relatively small: **$-0.97$ pp** in the primary item fixed-effects model ($SE = 0.49$, $p = 0.047$). Point estimates remain stable across alternative specifications ($-0.89$ to $-1.19$ pp), providing useful evidence against an expanding, severe constructed-response interface penalty. However, statistical significance is inferentially sensitive ($p = 0.016$ to $0.078$), the content-adjusted confidence interval extends below $-2.0$ pp, and standard errors use school-level clustering rather than full survey replicate weights.
2. **Non-Response Decomposition & Content Nuance (Table 22)**:  
   Reduced completion (omissions and not-reached items) accounts for approximately **23.3%** of the multiple-choice decline and **26.2%** of the constructed-response decline. The remaining ~74–77% occurred among attempted responses. While this confirms that examinees did not simply stop answering questions, an attempted incorrect response cannot automatically be equated with pure mathematical learning loss rather than interface or expression friction. Furthermore, content domains diverge: Number (40 items) is completely format-neutral ($-1.87$ pp MC vs. $-1.72$ pp CR), while Measurement and Geometry shows a substantial CR drop ($-4.34$ pp, $-4.10$ pp attempted). The apparent divergence in Data (+1.11 pp MC vs. $-3.29$ pp CR) relies on only 3 multiple-choice items and is strictly exploratory.
3. **Historical Mode Sensitivity Linkage across 31 Anchor Items (Table 23)**:  
   Linking the 31 items shared between Study A's 2019 mode bridge and Study D's longitudinal panel, an orthogonal split-sample regression revealed no detectable relationship between 2019 digital vulnerability and subsequent longitudinal trend ($\gamma_1 = -0.169$, $SE = 0.159$, $p = 0.297$, $R^2 = 0.037$). However, given $N = 31$ items, statistical power to detect small associations is limited.
4. **Screen-Level Process Timing Panel (Table 24)**:  
   Analyzing $N = 190,058$ examinee-screen interactions across 77 pure screens, time spent on multiple-choice screens remained unchanged ($+0.06$ seconds, $SE = 0.80$, $p = 0.94$). In contrast, time spent on constructed-response screens dropped by **$-2.71$ seconds** ($SE = 0.60$, $p < 0.0001$) relative to multiple choice. While this shows students were not spending more time struggling with response tools, it does not prove that input difficulty vanished.
5. **Exploratory Synthetic IRT Sensitivity Demonstration (Table 25)**:  
   Theoretical IRT simulations demonstrate how multiple-choice guessing floors ($c > 0$) naturally cause constructed responses to decline more under uniform latent ability loss. However, this demonstration uses illustrative 3PL/2PL curves rather than calibrated TIMSS item parameters, and the sign of the excess format divergence depends on the assumed parameter grid (ranging from $-0.23$ pp to $+0.82$ pp). Consequently, it illustrates theoretical mechanics but cannot support a numerical scale-score attribution.
6. **Overall Conclusion**:  
   We reject the hypothesis that an exploding constructed-response keyboarding penalty drove the national mathematics decline. At the same time, we do **not** claim that digital testing caused "0%" of the score drop: format-neutral interface effects, assessment design shifts, and student engagement factors cannot be ruled out without an empirical paper counterfactual in 2023.
"""))

    # ==============================================================================
    # Setup & Environment
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""### Setup and Data Loading
We load the pre-computed Study D analytical tables, processed microdata panels, and item inventories.
"""))

    cells.append(nbf.v4.new_code_cell(r"""import sys
from pathlib import Path
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

# Configure repository paths
NOTEBOOK_DIR = Path.cwd()
PROJECT_ROOT = NOTEBOOK_DIR.parent if NOTEBOOK_DIR.name == "notebooks" else NOTEBOOK_DIR
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

pd.set_option("display.max_columns", 25)
pd.set_option("display.width", 1000)
pd.set_option("display.float_format", lambda x: f"{x:.4f}" if abs(x) < 1e-2 else f"{x:.2f}")

print(f"[OK] Environment configured. Root: {PROJECT_ROOT}")
"""))

    # ==============================================================================
    # Section 1: Difference-in-Differences Format Divergence (Table 21)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 1. Difference-in-Differences Format Divergence (Table 21)

### Econometric Formulation & Inference
To test whether constructed-response mathematics questions deteriorated faster than multiple-choice questions between 2019 and 2023, we estimate the student-by-item stacked linear probability model:
$$Y_{ist} = \alpha_i + \beta_1 \, \text{Year2023}_t + \beta_2 \, (\text{CR}_i \times \text{Year2023}_t) + X_{ist}'\theta + \varepsilon_{ist}$$
where:
- $Y_{ist} \in [0, 100]$ is the percentage score of student $s$ on item $i$ in year $t \in \{2019, 2023\}$.
- $\alpha_i$ are individual item fixed effects (controlling for baseline item difficulty).
- $\beta_1$ represents the longitudinal baseline trend on multiple-choice items.
- $\beta_2$ is the parameter of interest: the differential longitudinal change on constructed-response items relative to multiple choice.
- Standard errors are clustered at the school sampling unit ($\text{IDSCHOOL}$).

#### Methodological Note on Sampling Variance
Our current models estimate weighted least squares regressions with school-clustered standard errors. In TIMSS's official scaling methodology, sampling uncertainty is evaluated via jackknife repeated replication (JK2), and achievement estimates incorporate five plausible values. School clustering captures intra-cluster correlation across students and items within schools, but does not implement full replicate-weight re-estimation.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_t21 = pd.read_csv(TABLES_DIR / "table21_timss_longitudinal_did_models.csv")
df_t21[["model_specification", "sample_tier", "n_items", "mc_baseline_trend_pp", "did_format_interaction_pp", "did_format_interaction_se", "ci_95_lower_pp", "ci_95_upper_pp", "p_value"]]
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Key Empirical Findings: Table 21
1. **Stability of Point Estimates**:
   - Across all seven specifications, the estimated format interaction $\beta_2$ is consistently negative and narrow in magnitude, ranging between **$-0.89$ pp and $-1.19$ pp**.
   - In the primary pre-registered model (Model 2: Item Fixed Effects on the 84 standard scaling items), the multiple-choice baseline dropped by **$-1.92$ pp** ($SE = 1.02$, $p = 0.058$), while the constructed-response differential interaction was **$-0.97$ pp** ($SE = 0.49$, $p = 0.047$).
2. **Inferential Sensitivity**:
   - While point estimates are stable, statistical significance is sensitive to modeling choices:
     - Model 1 (Raw Unadjusted): $\beta_2 = -0.95$ pp ($p = 0.054$).
     - Model 2 (Primary Item FE): $\beta_2 = -0.97$ pp ($p = 0.047$).
     - Model 3 (Content Domain $\times$ Year): $\beta_2 = -0.99$ pp ($p = 0.067$, 95% CI: $[-2.06, +0.07]$ pp).
     - Model 4 (Cognitive Domain $\times$ Year): $\beta_2 = -0.97$ pp ($p = 0.047$).
     - Model 5 (Student-Normalized Weights): $\beta_2 = -0.89$ pp ($p = 0.078$).
     - Model 6 (PSI Inclusive Standard Scoring): $\beta_2 = -1.19$ pp ($p = 0.017$).
     - Model 7 (PSI Alternate Non-Response): $\beta_2 = -0.96$ pp ($p = 0.054$).
   - Several reasonable specifications straddle the $p = 0.05$ threshold, and the content-adjusted confidence interval extends below $-2.0$ pp.
3. **Substantive Interpretation**:
   - The estimated format interaction is small, consistently negative, and inferentially sensitive.
   - This provides useful evidence against a very large, easily detectable constructed-response collapse (such as an expanding $\ge -3.0$ pp penalty), while showing that the format gap shifted by about one percentage point.
"""))

    # ==============================================================================
    # Section 2: Non-Response Accounting Decomposition (Table 22)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 2. Non-Response Accounting Decomposition (Table 22)

### Methodological Decomposition
We decompose the total change in unconditioned item percentage score $\Delta \bar{Y}$ into completion versus attempted performance components:
$$\Delta \bar{Y} = \underbrace{\Delta A \cdot \bar{S}}_{\text{Completion Component}} + \underbrace{\bar{A} \cdot \Delta S}_{\text{Attempted Performance Component}}$$
where:
- $A \in [0, 1]$ is item attempt status (1 if answered, 0 if omitted or not-reached).
- $S \in [0, 100]$ is accuracy conditional on attempting the item.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_t22 = pd.read_csv(TABLES_DIR / "table22_timss_longitudinal_nonresponse_decomposition.csv")
print("--- Primary 84 Pool Summary ---")
print(df_t22[df_t22["subgroup"] == "Primary 84 Pool"][["format", "n_items", "total_change_pp", "completion_component_pp", "performance_component_pp", "share_due_to_noncompletion_pct"]])

print("\n--- Content Domain Subgroups ---")
print(df_t22[df_t22["subgroup"].str.contains("Content")][["subgroup", "format", "n_items", "total_change_pp", "completion_component_pp", "performance_component_pp"]])
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Key Empirical Findings: Table 22
1. **Primary Accounting Decomposition**:
   - **Multiple Choice**: Total drop $-1.94$ pp = $-0.57$ pp completion (**23.3%**) + $-1.37$ pp attempted score decline (**76.7%**).
   - **Constructed Response**: Total drop $-2.89$ pp = $-0.78$ pp completion (**26.2%**) + $-2.11$ pp attempted score decline (**73.8%**).
   - The non-completion difference between formats is narrow ($-0.21$ pp). Most score deterioration occurred among attempted items.
2. **Epistemic Qualification on Attempted Errors**:
   - An attempted answer that receives zero points is an attempted response. However, an incorrect attempted answer does not definitively isolate lack of mathematical knowledge from expression, transcription, or interface friction (e.g., student understands the concept but enters the answer in an unexpected format).
3. **Content-Domain Nuance**:
   - **Number (40 items: 18 MC, 22 CR)**: Completely format-neutral. MC fell by $-1.87$ pp; CR fell by $-1.72$ pp ($\Delta = +0.15$ pp).
   - **Measurement and Geometry (23 items: 11 MC, 12 CR)**: Substantial constructed-response decline. MC fell by $-2.92$ pp, while CR fell by $-4.34$ pp ($\Delta = -1.42$ pp), almost entirely driven by attempted errors ($-4.10$ pp).
   - **Data (21 items: 3 MC, 18 CR)**: Apparent large divergence (MC $+1.11$ pp vs. CR $-3.29$ pp, $\Delta = -4.40$ pp). However, because only **3 multiple-choice items** represent this domain, this contrast is strictly exploratory.
"""))

    # ==============================================================================
    # Section 3: Historical 31-Item Mode Sensitivity Linkage (Table 23)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 3. Historical 31-Item Mode Sensitivity Linkage (Table 23)

### Mechanism Test: Did Mode-Sensitive Items Deteriorate Faster?
In Study A, we measured the exact item-level paper-versus-digital performance contrast in 2019. Exactly **31 items** (14 Multiple Choice, 17 Constructed Response) appear in both Study A's 2019 mode bridge and Study D's 2019–2023 longitudinal panel.

To eliminate mechanical correlation, we employ a split-sample estimator:
- Split 1 (Odd Student IDs in 2019): Measures 2019 digital vulnerability: $\Delta_{\text{mode}, i}^{(1)} = \bar{Y}_{\text{dig}, i}^{(1)} - \bar{Y}_{\text{paper}, i}$.
- Split 2 (Even Student IDs in 2019): Measures 2019–2023 longitudinal trend: $\Delta_{\text{trend}, i}^{(2)} = \bar{Y}_{2023, i} - \bar{Y}_{\text{dig}, i}^{(2)}$.

We estimate the regression:
$$\Delta_{\text{trend}, i}^{(2)} = \gamma_0 + \gamma_1 \, \Delta_{\text{mode}, i}^{(1)} + u_i$$
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_t23 = pd.read_csv(TABLES_DIR / "table23_timss_historical_mode_sensitivity_31items.csv")
print(f"Total overlapping items: {len(df_t23)} ({df_t23['format'].value_counts().to_dict()})")

X = sm.add_constant(df_t23["mode_diff_split1"])
y = df_t23["trend_split2"]
mod_split = sm.OLS(y, X).fit()
print(mod_split.summary().tables[1])
print(f"R-squared: {mod_split.rsquared:.4f}, p-value: {mod_split.pvalues.iloc[1]:.4f}")
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Key Empirical Findings: Table 23
1. **Baseline Mode Vulnerability (2019 Study A)**:
   - On this 31-item subset, the 2019 mode difference was **$-1.62$ pp** on Multiple Choice vs. **$-5.00$ pp** on Constructed Response, yielding a format gap of **$-3.38$ pp** (consistent with Study A's national findings).
2. **Longitudinal Sensitivity Test**:
   - The split-sample slope is $\gamma_1 = -0.169$ ($SE = 0.159$, $p = 0.297$, $R^2 = 0.037$).
   - There is no statistically detectable relationship between 2019 mode vulnerability and post-2019 decline. However, with $N = 31$ items, this test has limited statistical power to rule out modest associations.
"""))

    # ==============================================================================
    # Section 4: Screen-Level Process Timing Panel (Table 24)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 4. Screen-Level Process Timing Panel (Table 24)

### Dwell Time on Screen
We evaluate whether students spent additional time on constructed-response screens in 2023, estimating screen-level fixed effects models across $N = 190,058$ interactions on 77 pure screens:
$$\text{Duration}_{ist} = \alpha_i + \delta_1 \, \text{Year2023}_t + \delta_2 \, (\text{CR}_i \times \text{Year2023}_t) + \varepsilon_{ist}$$
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_t24 = pd.read_csv(TABLES_DIR / "table24_timss_screen_behavioral_panel.csv")
df_t24
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Key Empirical Findings: Table 24
1. **Timing Changes**:
   - Multiple-choice screen duration was unchanged: **$+0.06$ seconds** ($SE = 0.80$, $p = 0.94$).
   - Constructed-response screen duration declined by **$-2.71$ seconds** ($SE = 0.60$, $p < 0.0001$, 95% CI: $[-3.89, -1.54]$s; log scale $-4.58\%$).
2. **Behavioral Interpretation**:
   - Fourth graders spent slightly less time on constructed-response screens in 2023 than in 2019.
   - This provides evidence against prolonged tool disorientation or keyboarding struggle. However, spending less time does not prove that input difficulty disappeared; students could be giving up faster or writing shorter responses.
"""))

    # ==============================================================================
    # Section 5: Exploratory Synthetic IRT Sensitivity Demonstration (Table 25)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 5. Exploratory Synthetic IRT Sensitivity Demonstration (Table 25)

### Psychometric Mechanics: The Non-Linear Guessing Floor
In item response theory, multiple-choice items include a pseudo-guessing floor ($c > 0$, typically $c \approx 0.25$), whereas constructed-response items do not ($c = 0.0$):
$$P_{\text{MC}}(\theta) = c + \frac{1 - c}{1 + e^{-a_{\text{MC}}(\theta - b_{\text{MC}})}}, \quad P_{\text{CR}}(\theta) = \frac{1}{1 + e^{-a_{\text{CR}}(\theta - b_{\text{CR}})}}$$
Because the multiple-choice curve is bounded below by $c$, an across-the-board drop in latent student ability ($\Delta\theta < 0$) mathematically compresses the multiple-choice drop, producing a larger percentage-point drop on constructed responses even when learning loss is completely format-neutral.

#### Methodological Limits of Synthetic Demonstrations
The official TIMSS reporting scale was established with a reference standard deviation of 100 points (sample SD $\approx 80$ points). More importantly, mapping the observed 17.8 scale score point decline to a latent $\theta$ shift requires the calibrated linear scale transformation ($S = A\theta + B$) and empirical item parameters ($a_i, b_i, c_i$).

Below, we simulate illustrative 3PL/2PL curves across 200,000 students to demonstrate the theoretical mechanics and highlight how parameter choices affect the expected format gap:
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_t25 = pd.read_csv(TABLES_DIR / "table25_timss_longitudinal_irt_counterfactuals.csv")
df_t25
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Key Methodological Insights: Table 25
1. **Mechanical Format Divergence**:
   - Across all five synthetic scenarios, uniform ability loss produces an expected format divergence ($\beta_{\text{expected}}$) between **$-0.74$ pp and $-1.79$ pp**, purely from the mathematical curvature of the guessing floor and discrimination parameters.
2. **Sensitivity to Illustrative Parameters**:
   - In Scenario 1 (Scale SD 100, Canonical parameters), $\beta_{\text{expected}} = -1.34$ pp, making the observed $-0.97$ pp gap look smaller than expected (+0.37 pp).
   - In Scenario 3 (Balanced discrimination: $a_{\text{CR}} = 1.05, a_{\text{MC}} = 1.00$), $\beta_{\text{expected}} = -0.99$ pp, almost exactly matching the observed $-0.97$ pp gap (+0.02 pp).
   - In Scenario 5 (Lower guessing floor: $c = 0.15$), $\beta_{\text{expected}} = -0.74$ pp, making the observed $-0.97$ pp gap look like additional constructed-response decline ($-0.23$ pp).
3. **No Empirical Attribution Estimate**:
   - Because the sign and magnitude of the difference depend directly on the assumed parameters, this simulation cannot support an empirical scale-point attribution. We postpone numerical attribution until calibrated TIMSS item parameters are fitted.
"""))

    # ==============================================================================
    # Section 6: Comprehensive Scientific Synthesis
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 6. Comprehensive Scientific Synthesis & Track Separation

### Synthesis of the Two Research Tracks
This investigation establishes a critical distinction between two separate empirical questions:

| Research Domain | Core Empirical Findings | Calibrated Scientific Conclusion |
| :--- | :--- | :--- |
| **Track 1: Interface Mechanism**<br>*(Does digital test delivery create a penalty for constructed-response math?)* | **Robust negative level effect**:<br>$\bullet$ Study A within-school FE: **$-2.73$ pp** ($p = 0.003$)<br>$\bullet$ Study A mode-invariant items: **$-2.58$ pp** ($p = 0.007$)<br>$\bullet$ Study B process timing: **$2.6\times$ duration** multiplier on CR | **Supported.** Fourth graders face real cognitive and mechanical friction when entering mathematical responses on screens (keypads, drawing, equation entry). |
| **Track 2: Trend Attribution**<br>*(Did digital testing explain the 18-point score decline between 2019 and 2023?)* | **Narrow, format-stable trend**:<br>$\bullet$ DiD format interaction: **$-0.89$ to $-1.19$ pp** (inferentially sensitive, $p = 0.016$ to $0.078$)<br>$\bullet$ Non-response: ~74–77% attempted error<br>$\bullet$ Historical sensitivity: $\gamma_1 = -0.169$ ($p = 0.297$, limited power)<br>$\bullet$ Screen timing: **$-2.71$s** dwell on CR screens ($p < 0.0001$)<br>$\bullet$ Synthetic IRT: non-linear guessing floors can generate $-0.7$ to $-1.8$ pp format gaps | **Partially Constrained, Causal Attribution Unproven.** The evidence argues against an expanding, severe constructed-response interface penalty. However, claiming digital testing caused "0%" of the decline is unsupported: format-neutral interface effects or general measurement shifts cannot be ruled out without an empirical paper counterfactual in 2023. |

---

### Methodological Recommendations for Future Research
1. **Do Not Conflate a Level Mode Penalty with a Longitudinal Trend**:
   A stable mode penalty drops out of longitudinal first differences. To explain a score decline, interface friction must have worsened, assessment format composition must have shifted, or adaptive routing must have amplified barriers.
2. **Postpone Numerical Scale Attribution Pending IRT Calibrations**:
   Avoid dividing raw percentage differences by scale point declines or applying uncalibrated IRT multipliers. Fitting actual TIMSS 2019 and 2023 item calibrations is necessary before estimating how many scale points relate to format differences.
3. **Execute Causal Laboratory Trials**:
   To decompose the Study A mechanism into screen presentation vs. response entry vs. typing/tool fluency, we have specified a pre-trial randomized crossover protocol in [`docs/experimental_design_protocol.md`](../docs/experimental_design_protocol.md).
"""))

    nb.cells = cells
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[OK] Notebook written -> {NOTEBOOK_PATH.name} ({len(cells)} cells)")
    return NOTEBOOK_PATH


if __name__ == "__main__":
    build_longitudinal_notebook()
