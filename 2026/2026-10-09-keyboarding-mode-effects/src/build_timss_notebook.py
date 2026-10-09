"""
Notebook Generation Script: 02_timss_2019_mode_effects.ipynb
Assembles and executes the empirical microdata analysis of TIMSS 2019 U.S. Grade 4 Mathematics.
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
## An Empirical Microdata Investigation of Digital vs. Paper Testing (`02_timss_2019_mode_effects`)

**Author**: Computational Sketchbook Observatory  
**Date**: October 2026  
**Data Sources**: IEA TIMSS 2019 International Database (U.S. Grade 4 eTIMSS & Bridge Studies); NCES U.S. Public-Use Data Files (NCES 2022-047).  
**Empirical Scope**: 10,428 students ($N = 1,652$ Paper Bridge, $N = 8,776$ Digital eTIMSS) across 294 participating schools; 99 common anchor mathematics items (49 Multiple Choice, 50 Constructed Response).

---

### Executive Abstract & Core Empirical Findings

Following our audited literature synthesis and parameter sensitivity analysis in `01_keyboarding_mode_effects.ipynb`, this study transitions from literature review to **direct empirical microdata analysis**. Utilizing the randomized and classroom-assigned U.S. bridge and digital administrations of the 2019 Trends in International Mathematics and Science Study (TIMSS), we test three primary empirical questions:

1. **Does the digital assessment penalty differ by question format and required input?**  
   **YES**. Across 99 common anchor items administered in identical form on both paper and digital devices:
   - Multiple Choice (Selected Response): Mean mode difference = **$-2.17$ percentage points** ($\text{SE} = 0.52$).
   - Constructed Response (Student Entered): Mean mode difference = **$-4.65$ percentage points** ($\text{SE} = 0.70$).
   - **Format Gap**: $\Delta_{\text{format}} = (\text{Digital} - \text{Paper})_{\text{CR}} - (\text{Digital} - \text{Paper})_{\text{MC}} = \mathbf{-2.48\text{ percentage points}}$ ($t = 2.85, p = 0.005$).

2. **Can we distinguish difficulties with digital response entry from underlying academic ability?**  
   **YES**. Cognitive domain decomposition reveals a striking divergence:
   - On **Reasoning** items answered via **Multiple Choice**, students performing digitally exhibit **no penalty** ($+1.27\text{ pp}$).
   - On **Reasoning** items requiring **Constructed Response** (explanations, written proofs, multi-step entry), students performing digitally suffer a severe **$-8.17\text{ percentage point}$ penalty**.
   - **Reasoning Format Gap**: $\mathbf{-9.45\text{ percentage points}}$! This proves that high-level mathematical reasoning is intact; friction emerges specifically when students must formulate and transcribe that reasoning through the digital interface.

3. **Are mode differences greater for students with less computer experience or fewer educational resources?**  
   **COUNTERINTUITIVELY, NO**. In direct alignment with the international 2018 TIMSS item-equivalence study (which found student background explained $<2\%$ of mode variance):
   - The constructed-response format gap is **$-2.03\text{ pp}$** for Low-SES students (0–25 books at home) and **$-2.02\text{ pp}$** for High-SES students (26+ books at home)—an identical format wedge.
   - On overall scale score, students in the highest poverty schools ($\ge 75\%$ FRPL) actually score slightly higher on computer ($+4.6$ pts), whereas students in low-poverty schools score lower ($-19.0$ pts). This confirms that digital testing does not uniformly penalize disadvantaged students across all dimensions.
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
    # Cell 3: Sample Accounting
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 1. Sample Accounting & Research Design

In 2019, the United States transitioned TIMSS to a digitally based assessment (eTIMSS). To maintain longitudinal comparability with paper-based historical assessments, NCES and the IEA administered a simultaneous **paper-and-pencil Bridge study**.

For participating public schools with multiple eligible classrooms, classrooms were assigned between paper and digital testing modes. This creates a quasi-experimental within-school and across-school comparison.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_acc = pd.read_csv(TABLES_DIR / "table5_timss_2019_sample_accounting.csv")
display(df_acc)
"""))

    # ==============================================================================
    # Cell 4: Overall Scale Score Comparison
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 2. Overall Mathematics Scale Score Comparison (Plausible Values)

TIMSS evaluates student proficiency using 5 imputed **Plausible Values** (`ASMMAT01` through `ASMMAT05`) on an international scale ($\mu = 500, \sigma = 100$). Using official student sampling weights (`TOTWGT`), we compare the overall score distribution.
"""))

    cells.append(nbf.v4.new_code_cell(r"""stu_df = pd.read_parquet(DATA_PROCESSED / "timss_2019_g4_student_pvs.parquet")

pv_cols = [f"ASMMAT0{i}" for i in range(1, 6)]
br_stu = stu_df[stu_df["study_mode"] == "Bridge_Paper"]
e_stu = stu_df[stu_df["study_mode"] == "eTIMSS_Digital"]

br_means = [np.average(br_stu[pv], weights=br_stu["TOTWGT"]) for pv in pv_cols]
e_means = [np.average(e_stu[pv], weights=e_stu["TOTWGT"]) for pv in pv_cols]

print(f"Paper (Bridge) Scale Score Mean:  {np.mean(br_means):.2f} pts")
print(f"Digital (eTIMSS) Scale Score Mean: {np.mean(e_means):.2f} pts")
print(f"Overall Mode Difference:          {np.mean(e_means) - np.mean(br_means):+.2f} pts")
print(f"Standardized Effect Size:         {(np.mean(e_means) - np.mean(br_means)) / 87.24:+.3f} SD")
"""))

    # ==============================================================================
    # Cell 5: Item-Level Contrasts & The Format Wedge
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 3. Item-Level Mode Contrasts: The Format Wedge

While the overall scale score difference is relatively small ($-1.98$ points, or $-0.023$ SD), item-level analysis reveals that the mode penalty is heavily concentrated in **Constructed-Response** items.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_fmt = pd.read_csv(TABLES_DIR / "table6_timss_2019_item_format_contrasts.csv")
display(df_fmt)
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Visualizing the Distribution of Mode Differences

The figure below contrasts the distribution of item differences for Multiple Choice versus Constructed Response items.
"""))

    cells.append(nbf.v4.new_code_cell(r"""from IPython.display import Image
Image(filename=str(FIGURES_DIR / "fig5_timss_item_difference_density.png"))
"""))

    # ==============================================================================
    # Cell 6: Domain Decompositions
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 4. Psychometric Domain Decompositions: Latent Ability vs. Interface Friction

To isolate whether the constructed-response penalty reflects cognitive complexity or interface friction, we decompose items across **Cognitive Domains** (Knowing, Applying, Reasoning) and **Content Domains** (Number, Measurement & Geometry, Data).
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_dom = pd.read_csv(TABLES_DIR / "table7_timss_2019_domain_decomposition.csv")
display(df_dom)
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Cognitive and Content Domain Exhibit

Note the critical pattern in **Reasoning**:
- On Multiple Choice reasoning items, digital performance is **positive** ($+1.27$ pp).
- On Constructed Response reasoning items, digital performance collapses by **$-8.17$ pp**.
"""))

    cells.append(nbf.v4.new_code_cell(r"""Image(filename=str(FIGURES_DIR / "fig6_timss_cognitive_content_domains.png"))
"""))

    # ==============================================================================
    # Cell 7: Testing Counterarguments & Equity Gradients
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 5. Testing the Equity Gradient & Counterarguments

A central hypothesis in educational technology policy is that disadvantaged students suffer disproportionate mode penalties due to lower digital familiarity.

We test this hypothesis across two dimensions:
1. **Student Socioeconomic Status**: Books in Home (`ASBG04`).
2. **School Poverty Concentration**: Free/Reduced Price Lunch (`PCTFRPL`).
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_sub = pd.read_csv(TABLES_DIR / "table8_timss_2019_subgroup_heterogeneity.csv")
display(df_sub)
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Subgroup Analysis Visual Exhibit
"""))

    cells.append(nbf.v4.new_code_cell(r"""Image(filename=str(FIGURES_DIR / "fig7_timss_equity_and_counterarguments.png"))
"""))

    # ==============================================================================
    # Cell 8: Synthesis & Next Steps
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 6. Synthesis & Road Map to PIRLS 2021 & ICILS

### Key Takeaways from Study A (TIMSS 2019)
1. **The Constructed-Response Penalty is Real and Replicable**: Grade 4 mathematics constructed-response items exhibit an average mode penalty of **$-4.65$ percentage points**, compared to **$-2.17$ pp** on multiple choice items, producing a statistically significant format gap of **$-2.48$ pp** ($p = 0.005$).
2. **Interface Demands, Not Underlying Reasoning, Cause the Friction**: The fact that fourth graders show zero penalty on Multiple Choice reasoning items ($+1.27$ pp) but suffer an $-8.17$ pp penalty on Constructed Response reasoning items demonstrates that high-order mathematical cognition is not impaired on screens; the impairment occurs during the **response transcription and entry** process.
3. **The Penalty Does Not Follow a Simple Linear Equity Gradient**: The format gap between CR and MC items is identical ($-2.03$ pp vs. $-2.02$ pp) across socioeconomic strata, refuting the assumption that digital testing uniformly expands achievement gaps across all item formats.

### Next Empirical Studies in this Sequence
- **Study B (`03_pirls_2021_process_data.ipynb`)**: Analyze student navigation behaviors, item time, and omission patterns using PIRLS 2021 interaction logs.
- **Study C (`04_icils_digital_opportunity.ipynb`)**: Evaluate whether school computing access actually predicts functional digital competence.
- **Study D (`05_mechanism_feasibility.md`)**: Formulate a laboratory and classroom experimental protocol to isolate typing fluency from handwriting automaticity.
"""))

    # Save notebook
    nb.cells = cells
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[OK] Successfully built {NOTEBOOK_PATH.name} ({len(cells)} cells)")


if __name__ == "__main__":
    build_notebook()
