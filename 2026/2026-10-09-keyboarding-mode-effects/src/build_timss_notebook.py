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
                                                                                 Descriptive Format Gap: -3.42 pp (t = -3.80)
                                                                                 Survey-Weighted DiD: beta = -3.10 pp (p < 0.0001)

2. Is the penalty driven by          INTERFACE FRICTION: Reasoning MC holds      Reasoning MC: +2.61 pp
   cognitive ability or entry?       positive, but Reasoning CR collapses.      Reasoning CR: -7.54 pp
                                     Penalty scales monotonically with entry:    Reasoning Format Gap: -10.14 pp!
                                     MC (-0.47 pp) -> Drawing (-3.10 pp) ->     Text / Explanation CR: -7.13 pp
                                     Keypad (-3.80 pp) -> Text (-7.13 pp).

3. Are penalties larger for low-SES  NO: Invariant across home resources         Low SES Format Penalty: -3.17 pp
   or under-resourced students?      and school poverty; confirmed null          High SES Format Penalty: -3.07 pp
                                     econometric interaction term.               Interaction beta = -0.10 pp (p = 0.93)
                                     Survives within-school randomization.       72 School Fixed Effects: beta = -2.36 pp (p = 0.0065)
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
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_mod = pd.read_csv(TABLES_DIR / "table9_timss_2019_input_modality.csv")
display(df_mod)
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Figure 6: Cognitive Decompositions and Input Modality Gradient
*Panel A demonstrates that Reasoning MC performance is positive (+2.6 pp) while Reasoning CR collapses (-7.5 pp). Panel B displays the monotonic progression of digital penalties as input transcription demands increase.*
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
    cells.append(nbf.v4.new_markdown_cell(r"""## 7. Econometric Estimation: Clustered Survey DiD & School Fixed Effects

To account for TIMSS's complex sampling design, clustering within schools, and within-school classroom assignment, we estimate three formal student-level econometric models:

$$\text{FormatGap}_{ij} = \beta_0 + \beta_1 \text{Digital}_{ij} + \epsilon_{ij}$$

1. **Model 1**: Full national sample with survey weights (`TOTWGT`) and cluster-robust standard errors clustered at the school level.
2. **Model 2**: Within-school fixed effects on the 72 overlapping schools where classrooms were randomly assigned to paper vs. digital.
3. **Model 3**: National sample interacting mode with student socioeconomic status (`Digital` $\times$ `Low SES`).
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_reg = pd.read_csv(TABLES_DIR / "table10_timss_2019_econometric_models.csv")
display(df_reg)
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Figure 7: Testing the Equity Gradient and Within-School Randomization
*Panel A shows that scale score differences are near-parallel across home book strata. Panel B confirms that the constructed-response mode penalty is identical between Low SES (-3.17 pp) and High SES (-3.07 pp). Panel C displays the within-school randomized classroom contrast across the 72 schools ($\beta = -2.36$ pp, $p = 0.0065$).*
"""))

    cells.append(nbf.v4.new_code_cell(r"""Image(filename=str(FIGURES_DIR / "fig7_timss_equity_and_counterarguments.png"))
"""))

    # ==============================================================================
    # Cell 10: Discussion & Conclusions
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 8. Discussion & Synthesis: Answering the Three Research Questions

### Question 1: Does the digital assessment penalty differ by question format?
**Confirmed.** Across 99 common items, Multiple Choice items exhibit near-parity ($-0.47\text{ pp}$), while Constructed Response items suffer a statistically significant and substantial penalty ($-3.90\text{ pp}$), yielding a **$-3.42\text{ pp}$ format gap** ($t = -3.80$). In survey-weighted student regressions clustered by school, the difference-in-differences penalty is **$-3.10\text{ pp}$** ($p < 0.0001$). Controlling for school fixed effects across 72 randomized schools, the penalty remains **$-2.36\text{ pp}$** ($p = 0.0065$).

### Question 2: Is the penalty driven by cognitive ability or interface friction?
**Interface Friction.** When fourth graders answer higher-order **Reasoning** items via multiple-choice radio buttons, their performance is $+2.61\text{ pp}$ higher on computer than on paper. But when answering Reasoning items requiring constructed explanations, their performance collapses by $-7.54\text{ pp}$, producing an acute **$-10.14\text{ pp}$ Reasoning wedge**. Furthermore, the penalty follows a strict monotonic hierarchy corresponding to interface complexity:
- Multiple Choice: $-0.47\text{ pp}$
- Drawing / Graphing: $-3.10\text{ pp}$
- Interactive Tables: $-3.18\text{ pp}$
- Keypad / Fractions: $-3.80\text{ pp}$
- Typed Text / Explanations: **$-7.13\text{ pp}$**

### Question 3: Are penalties larger for low-SES or under-resourced students?
**Rejected.** The mode penalty on constructed response is invariant across socioeconomic status: **$-3.17\text{ pp}$** for Low-SES students vs. **$-3.07\text{ pp}$** for High-SES students. The interaction coefficient in Model 3 is $\beta = -0.096\text{ pp}$ ($p = 0.93$). Furthermore, high-poverty schools ($\ge 75\%$ FRPL) actually score $+4.6$ scale points higher on computer. Interface friction affects fourth graders universally regardless of home socioeconomic resources.
"""))

    nb.cells = cells
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[OK] Wrote notebook to {NOTEBOOK_PATH.name} ({len(cells)} cells)")


if __name__ == "__main__":
    build_notebook()
