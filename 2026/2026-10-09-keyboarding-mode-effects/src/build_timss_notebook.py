"""
Notebook Generation Script: 02_timss_2019_mode_effects.ipynb
Assembles and executes the empirical microdata analysis of TIMSS 2019 U.S. Grade 4 Mathematics.
Includes audited two-digit diagnostic scoring, omission recovery, input modality hierarchy,
within-school randomized classroom comparisons (72 schools), and econometric DiD models.
"""

from pathlib import Path
import nbformat as nbf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOKS_DIR / "02_timss_2019_mode_effects.ipynb"


def build_notebook():
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
    # Cell 1: Title & Executive Summary
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""# TIMSS 2019 U.S. Grade 4 Mathematics: Item-Level Mode Effects & Interface Friction
## An Audited Empirical Microdata Investigation of Digital vs. Paper Testing (`02_timss_2019_mode_effects`)

**Author**: Computational Sketchbook Observatory  
**Date**: October 2026 (Audited & Reconciled Release)  
**Data Sources**: IEA TIMSS 2019 International Database (U.S. Grade 4 eTIMSS & Bridge Studies); NCES U.S. Public-Use Data Files (NCES 2022-047).  
**Empirical Scope**: 10,428 students ($N = 1,652$ Paper Bridge, $N = 8,776$ Digital eTIMSS) across 294 participating schools; 99 common anchor mathematics items (49 Multiple Choice, 50 Constructed Response); 72 schools with within-school randomized classroom administration ($N=2,728$).

---

### Executive Abstract & Core Empirical Findings

Following our audited literature synthesis and parameter sensitivity analysis in `01_keyboarding_mode_effects.ipynb`, this study transitions to **direct empirical microdata analysis**. Utilizing the randomized and classroom-assigned U.S. bridge and digital administrations of the 2019 Trends in International Mathematics and Science Study (TIMSS), we address the three core research questions using verified two-digit diagnostic scoring, recovered user-missing codes, within-school fixed effects, and survey-weighted econometric estimation:

```
========================================================================================================================
TIMSS 2019 U.S. GRADE 4 MATHEMATICS AUDITED EMPIRICAL SCORECARD
========================================================================================================================
Core Research Question               Audited Empirical Finding                   Statistical Evidence
------------------------------------------------------------------------------------------------------------------------
1. Does the mode penalty differ      YES: Constructed Response experiences       Multiple Choice: -0.47 pp (SE 0.53)
   by item format & required input?  a 3.4 pp larger penalty than MC.            Constructed Response: -3.90 pp (SE 0.73)
                                     Robust to booklet item composition          Descriptive Format Gap: -3.42 pp (t = -3.80)
                                     and school selection.                       Survey-Weighted DiD: beta = -3.10 pp (p < 0.0001)
                                                                                 Item Fixed Effects WLS: beta = -3.42 pp (p < 0.00001)
                                                                                 Within-School Student FE: beta = -2.36 pp (p = 0.0065)
                                                                                 Item + School FE (Class Clustered): beta = -2.73 pp (p = 0.0034)
                                                                                 Randomization Permutation: p = 0.0380

2. Is the penalty driven by          INTERFACE FRICTION & REASONING WEDGE:       Reasoning MC: +2.61 pp
   cognitive ability or entry?       Reasoning MC holds positive (+2.6 pp),      Reasoning CR: -7.54 pp
                                     but Reasoning CR collapses (-7.5 pp).       Reasoning Format Gap: -10.14 pp!
                                     Provisional input gradient:                 Text / Explanation CR: -7.13 pp
                                     MC (-0.47 pp) -> Drawing (-3.10 pp) ->     Keypad / Numeric: -3.80 pp
                                     Keypad (-3.80 pp) -> Text (-7.13 pp).       Note: Text items belong to Reasoning domain;
                                                                                 entry mode is confounded with cognitive complexity.

3. Are penalties larger for low-SES  NO DETECTABLE MODERATION: Subgroup gaps     Low SES Format Penalty: -3.17 pp
   or under-resourced students?      are near-identical across home books;       High SES Format Penalty: -3.07 pp
                                     econometric interaction term is null.       Interaction beta = -0.10 pp (p = 0.934)
                                     However, 95% CI [-2.35, +2.16] pp does      95% CI: [-2.35, +2.16] pp
                                     not rule out +-2.2 pp heterogeneity.        Reflects lack of detectable moderation,
                                                                                 not established statistical equivalence.
========================================================================================================================
```
"""))

    # ==============================================================================
    # Cell 2: Setup & Environment
    # ==============================================================================
    cells.append(nbf.v4.new_code_cell(r"""import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set paths
PROJECT_ROOT = Path("..").resolve()
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"
FIGURES_DIR = PROJECT_ROOT / "artifacts" / "figures"

pd.set_option("display.max_columns", 25)
pd.set_option("display.width", 1000)

print(f"[OK] Python {sys.version}")
print(f"[OK] Project Root: {PROJECT_ROOT}")
"""))

    # ==============================================================================
    # Cell 3: Sample Accounting & Research Design
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 1. Sample Accounting & Research Design

In 2019, the United States transitioned TIMSS to a digitally based assessment (eTIMSS). To maintain longitudinal comparability with paper-based historical assessments, NCES and the IEA administered a simultaneous **paper-and-pencil Bridge study**.

Crucially, in 72 participating public schools with multiple sampled classrooms, classrooms were assigned between paper and digital testing modes through **within-school randomized assignment**. This provides both:
1. A **National Probability Sample** ($N = 10,428$ students across 294 schools) evaluated with survey sampling weights (`TOTWGT`) and cluster-robust standard errors.
2. A **Within-School Quasi-Experimental Sample** ($N = 2,728$ students across 72 schools) evaluated with school fixed effects, completely controlling for school selection and neighborhood composition.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_acc = pd.read_csv(TABLES_DIR / "table5_timss_2019_sample_accounting.csv")
display(df_acc)
"""))

    # ==============================================================================
    # Cell 4: Scoring Methodology & Response Status Recovery
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 2. Two-Digit Diagnostic Scoring & Response Status Recovery

TIMSS constructed-response items utilize a **two-digit diagnostic coding scheme**:
- **First Digit**: Score point value (e.g., `10`–`19` award 1 point; `20`–`29` award 2 points; `70`–`79` award 0 points).
- **Second Digit**: Diagnostic response strategy or error type.

In naive parsers, checking only `code == 10.0` or `code == 20.0` erroneously zeros out valid partial or full credit strategies (such as `11.0` or `12.0`). Furthermore, SPSS user-missing codes (`99.0` for omitted items, `96.0` for not reached items) must be explicitly preserved via `user_missing=True` to compute accurate non-response rates.
"""))

    cells.append(nbf.v4.new_code_cell(r"""item_df = pd.read_parquet(DATA_PROCESSED / "timss_2019_g4_item_contrasts.parquet")
print(f"Total Common Anchor Items: {len(item_df)}")
print(f"Multiple Choice (MC): {(item_df['item_type'] == 'MC').sum()} items")
print(f"Constructed Response (CR): {(item_df['item_type'] == 'CR').sum()} items")

# Display items with diagnostic correct codes
print("\nItems with special diagnostic coding or multi-point rubrics:")
display(item_df[item_df["maximum_points"] > 1][["item_id", "maximum_points", "item_type", "cognitive_domain", "label", "diff_pp"]])
"""))

    # ==============================================================================
    # Cell 5: Item Format Contrasts & Omission Patterns
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 3. Item Format Contrasts & Omission Patterns

Table 6 reports the survey-weighted item performance across formats, omission rates, and sensitivity under answered-only denominators.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_fmt = pd.read_csv(TABLES_DIR / "table6_timss_2019_item_format_contrasts.csv")
display(df_fmt)
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Figure 5: Item-Level Mode Difference Distribution & Paired Scatter
*Panel A illustrates the kernel density of item mode differences, showing the leftward shift of Constructed Response relative to Multiple Choice. Panel B plots digital vs. paper percent correct against the 45-degree parity line.*
"""))

    cells.append(nbf.v4.new_code_cell(r"""from IPython.display import Image
Image(filename=str(FIGURES_DIR / "fig5_timss_item_difference_density.png"))
"""))

    # ==============================================================================
    # Cell 6: Cognitive Domain Decomposition & The Reasoning Wedge
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 4. Cognitive Domain Decomposition: Isolating the Reasoning Wedge

To determine whether the constructed-response deficit reflects high-order cognitive failure on screens or interface entry friction, we decompose items across TIMSS cognitive domains: **Knowing**, **Applying**, and **Reasoning**.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_dom = pd.read_csv(TABLES_DIR / "table7_timss_2019_domain_decomposition.csv")
display(df_dom)
"""))

    # ==============================================================================
    # Cell 7: Input Modality Hierarchy
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 5. Digital Input Modality Hierarchy

Grounding our analysis in the TIMSS Item Equivalence taxonomy (Fishbein, Foy, & Yin / Mullis et al.), we categorize the 50 constructed-response items by their required digital input modality:
1. **Multiple Choice** (Click/tap radio button, $N=49$)
2. **CR: Drawing / Graphing** (Drawing lines, plotting points, shading bars, $N=10$)
3. **CR: Interactive / Table** (Classifying items into table cells or toggling checkboxes, $N=8$)
4. **CR: Number-pad / Numeric** (Entering numbers, decimals, or fractions via on-screen keypad, $N=27$)
5. **CR: Text / Explanation** (Typing multi-step mathematical explanations, $N=5$)

> **Important Methodological Note on Confounding**: This input classification is provisional and exploratory. Crucially, all 5 items requiring typed text explanations (`MP51008`, `MP61228`, `MP61248`, `MP61255`, `MP61256`) belong to the **Reasoning** cognitive domain. Consequently, input modality is confounded with underlying cognitive complexity in the TIMSS anchor item pool; the $-7.13$ pp penalty reflects both typing friction and cognitive reasoning demand.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_mod = pd.read_csv(TABLES_DIR / "table9_timss_2019_input_modality.csv")
display(df_mod)
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Figure 6: Cognitive Decompositions and Input Modality Gradient
*Panel A demonstrates that Reasoning MC performance is positive (+2.6 pp) while Reasoning CR collapses (-7.5 pp). Panel B displays the provisional progression of digital penalties as input transcription demands increase, noting the Reasoning domain confounding on text items.*
"""))

    cells.append(nbf.v4.new_code_cell(r"""Image(filename=str(FIGURES_DIR / "fig6_timss_cognitive_content_domains.png"))
"""))

    # ==============================================================================
    # Cell 8: Subgroup Heterogeneity & Within-School Randomization
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 6. Socioeconomic Heterogeneity & Within-School Randomization

We test whether the digital format penalty compounds among students with fewer home resources or attending higher-poverty schools.

Table 8 reports scale scores and individual student format gaps ($CR\% - MC\%$) computed dynamically across subgroups.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_sub = pd.read_csv(TABLES_DIR / "table8_timss_2019_subgroup_heterogeneity.csv")
display(df_sub)
"""))

    # ==============================================================================
    # Cell 9: Econometric Estimation & Hypothesis Testing
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 7. Econometric Estimation: Clustered Survey DiD, Item Fixed Effects, and Booklet Sensitivity

To account for TIMSS's complex sampling design, matrix-sampled booklet composition, clustering within schools, and within-school classroom assignment, we estimate formal econometric models and sensitivity checks:

1. **Model 1 (National Survey-Weighted Student DiD)**: Full national sample ($N = 10,417$) with survey sampling weights (`TOTWGT`) clustered at the school level ($\beta = -3.102$ pp, $p < 0.0001$).
2. **Model 2 (National Item Fixed-Effects Panel WLS)**: Stacked student-by-item panel ($N = 164,653$ responses across 99 items and 294 schools) with 99 item baseline difficulty fixed effects ($\alpha_j$), fully controlling for booklet item composition ($\beta_2 = -3.422$ pp, $p = 3.0 \times 10^{-7}$).
3. **Model 3 (Within-School Student DiD)**: 72 schools with randomized classroom assignment ($N = 2,726$), controlling for school selection and neighborhood composition via school fixed effects ($\beta = -2.364$ pp, $p = 0.0065$).
4. **Model 4a (Within-School Item FE + School FE Panel, Classroom Clustered)**: Stacked panel on 72 randomized schools ($N = 53,837$ responses) simultaneously absorbing 99 item fixed effects AND 72 school fixed effects, clustered by 147 classrooms ($\beta_2 = -2.734$ pp, $SE = 0.932, p = 0.00335$, 95% CI: $[-4.56, -0.91]$ pp).
5. **Model 4b (Within-School Item FE + School FE Panel, School Clustered)**: Clustered conservatively at the school level across the 72 schools ($\beta_2 = -2.734$ pp, $SE = 0.843, p = 0.00119$, 95% CI: $[-4.39, -1.08]$ pp).
6. **Model 5 (SES Interaction Test)**: Testing whether mode effects compound among lower-SES students ($\beta = -0.096$ pp, $p = 0.934$, 95% CI: $[-2.35, +2.16]$ pp).

### Design-Based Inference & Randomization Inference
Table 11 reports survey-design uncertainty estimated via TIMSS Jackknife Repeated Replication (JK2 using official two-sided complementary replicates per zone with factor 0.5), yielding an independent JK2 DiD standard error of $0.668$ pp. Cluster linearization accounting for positive within-school covariance across all 294 schools yields $SE = 0.663$ pp ($t = -4.68, p < 0.00001$). Within the 72 schools, Monte Carlo randomization inference across 2,000 permutations confirms that the within-school classroom contrast is statistically significant ($p = 0.0400$ two-tailed, finite-sample corrected).
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_reg = pd.read_csv(TABLES_DIR / "table10_timss_2019_econometric_models.csv")
display(df_reg)

df_jk = pd.read_csv(TABLES_DIR / "table11_timss_2019_survey_inference_jk2.csv")
print("\n--- TIMSS Jackknife Repeated Replication (JK2 Design-Based Standard Errors) ---")
display(df_jk)

df_sens = pd.read_csv(TABLES_DIR / "table13_timss_2019_booklet_exposure_sensitivity.csv")
print("\n--- Matrix-Sampling Booklet Exposure & Weighting Sensitivity (Table 13) ---")
display(df_sens)
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Figure 7: Testing the Equity Gradient and Within-School Randomization
*Panel A shows that scale score differences are near-parallel across home book strata. Panel B shows that the constructed-response mode penalty is indistinguishable between Low SES (-3.17 pp) and High SES (-3.07 pp) with a null interaction (p=0.934, 95% CI [-2.35, +2.16] pp). Panel C displays the unweighted descriptive differences across the 72 schools with descriptive gap (-2.36 pp), student FE model (beta = -2.36 pp), stacked item+school FE model (beta = -2.73 pp, p=0.0034), and Monte Carlo classroom permutation test (p=0.0400).*
"""))

    cells.append(nbf.v4.new_code_cell(r"""Image(filename=str(FIGURES_DIR / "fig7_timss_equity_and_counterarguments.png"))
"""))

    # ==============================================================================
    # Cell 10: Discussion & Conclusions
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 8. Discussion & Synthesis: Answering the Three Research Questions

### Calibrated Synthesis
> **Defensible Empirical Conclusion**: Using U.S. fourth-grade TIMSS 2019 paper-bridge and digital assessment data, we find larger negative digital-versus-paper performance differences on constructed-response mathematics items than on multiple-choice items. The difference remains negative when controlling for item and school characteristics within schools represented in both modes ($-2.73$ pp, $p = 0.00335$ classroom-clustered; $p = 0.00119$ school-clustered; Monte Carlo classroom permutation $p = 0.0400$). The results are consistent with additional digital response-format demands, although their mechanism, precise magnitude, and nationally representative uncertainty require further validation.

### Question 1: Does the digital assessment penalty differ by question format?
**Confirmed.** Across 99 common items, Multiple Choice items exhibit near-parity ($-0.47\text{ pp}$), while Constructed Response items suffer a statistically significant and substantial penalty ($-3.90\text{ pp}$), yielding a **$-3.42\text{ pp}$ format gap** ($t = -3.80$). Crucially, **booklet matrix sampling does not explain this gap**: in student-by-item regressions absorbing 99 item fixed effects, the interaction is **$-3.42\text{ pp}$** ($p < 0.00001$), and remains **$-3.30$ to $-3.68\text{ pp}$** whether using row-level or student-normalized weights. Controlling for school fixed effects across 72 randomized schools, the penalty remains **$-2.36\text{ pp}$** ($p = 0.0065$). Absorbing both 99 item fixed effects and 72 school fixed effects simultaneously, the penalty is **$-2.73\text{ pp}$** ($p = 0.00335$ clustered by classroom, $p = 0.00119$ clustered by school; student-normalized $\beta = -2.68$ pp to $-2.83$ pp).

### Question 2: Is the penalty driven by cognitive ability or interface friction?
**Interface Friction & Reasoning Confounding.** When fourth graders answer higher-order **Reasoning** items via multiple-choice radio buttons, their performance is $+2.61\text{ pp}$ higher on computer than on paper. But when answering Reasoning items requiring constructed explanations, their performance collapses by $-7.54\text{ pp}$, producing an acute **$-10.14\text{ pp}$ Reasoning wedge**. Across input modalities, the penalty appears monotonic: Multiple Choice ($-0.47$ pp) $\to$ Drawing ($-3.10$ pp) $\to$ Keypad ($-3.80$ pp) $\to$ Typed Text ($-7.13$ pp). However, because all 5 text items belong to the Reasoning domain (`MP51008`, `MP61228`, `MP61248`, `MP61255`, `MP61256`), input modality is confounded with cognitive difficulty, and this taxonomy should be interpreted as provisional and exploratory.

### Question 3: Are penalties larger for low-SES or under-resourced students?
**No Detectable Moderation.** The mode penalty on constructed response is statistically indistinguishable across socioeconomic status: **$-3.17\text{ pp}$** for Low-SES students vs. **$-3.07\text{ pp}$** for High-SES students. The interaction coefficient in Model 5 is $\beta = -0.096\text{ pp}$ ($p = 0.934$). However, the 95% confidence interval ($[-2.35, +2.16]$ pp) does not rule out educationally meaningful heterogeneity up to $\pm 2.2$ pp. Rather than proving complete invariance, the empirical evidence demonstrates a lack of detectable moderation by home SES.
"""))

    nb.cells = cells
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[OK] Wrote notebook to {NOTEBOOK_PATH.name} ({len(cells)} cells)")


if __name__ == "__main__":
    build_notebook()
