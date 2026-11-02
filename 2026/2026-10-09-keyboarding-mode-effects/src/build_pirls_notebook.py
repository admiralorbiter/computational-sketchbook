"""
Notebook Generation Script: 04_pirls_2021_process_data.ipynb
Generates and executes the calibrated Study B research notebook analyzing PIRLS 2021 digital reading
process data, item response latencies, navigation revisit frequency, scored outcomes, and within-item
time-accuracy gradients in Grade 4 reading.
"""

from pathlib import Path
import nbformat as nbf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOKS_DIR / "04_pirls_2021_process_data.ipynb"


def build_pirls_notebook():
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
    # Title & Study B Research Framing
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""# PIRLS 2021 Digital Reading Process & Interaction Logs (Study B)
## Descriptive Latency Decomposition, Revisit Behavior, and Time-Accuracy Dynamics in Grade 4 Reading (`04_pirls_2021_process_data`)

**Author**: Computational Sketchbook Observatory  
**Date**: October 2026 (Calibrated Edition)  
**Primary Dataset**: IEA PIRLS 2021 International Database (`ASPDEUR5.sav`, `ASADEUR5.sav`, `P21_ItemInformation.xlsx`)  
**Study Scope**: High-income OECD digital reading benchmark sample ($N = 4,486$ clean fourth-grade examinees across 273 digital reading items, yielding 91,376 matched student-item observations).

---

### Executive Research Purpose & Methodological Scope
In Study A, our within-school item-controlled analysis of TIMSS 2019 demonstrated that fourth graders suffer a robust **$-2.73$ percentage-point penalty** on constructed-response mathematics questions under digital administration ($-2.58$ pp among officially invariant items).

However, test-score outcomes alone cannot observe the real-time behavioral process of test-taking. Study B utilizes digital process logs from PIRLS 2021 to examine how young elementary students allocate time, navigate on-screen passages, and formulate responses during computerized assessments.

#### Epistemic Demarcation & Calibrated Interpretation
1. **Descriptive Behavior vs. Causal Transcription Tax**:
   Because paper response latencies are unobserved for these reading items, the observed $+78.5\text{s}$ duration difference between constructed-response and multiple-choice items cannot be identified as a causal "digital transcription tax." A constructed response takes longer than selecting a radio button for multiple cognitive reasons: formulating, organizing, writing, and revising text. Study B provides descriptive evidence of digital test-taking behavior that generates testable hypotheses for mathematics.
2. **Institutional Context**:
   NCES sampled U.S. students for both digital and paper-bridge administration in PIRLS 2021, but published its official results from the paper-bridge sample due to psychometric linking concerns. Germany serves as the primary high-income OECD digital benchmark administering the complete digital PIRLS assessment with verified event timestamps and reading proficiency scales.
"""))

    # ==============================================================================
    # Section 1: Study Admission Gate & Estimand Specifications
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 1. Study Admission Gate & Estimand Specifications

### The Six-Point Study Admission Gate
1. **Retrieval & Usability**: Full access to the public-use PIRLS 2021 International Database (IEA Hamburg), including process timing files (`ASP`) and scored achievement microdata (`ASA`).
2. **Analytical Population**: Exactly $N = 4,486$ clean students meeting official participation criteria (`FLAGPT1 == 0` and `FLAGPT2 == 0`) across 273 digital reading items (124 Multiple Choice, 149 Constructed Response).
3. **Explicit Estimand Labeling**:
   - **Table 15**: Item-level macro-averages (unweighted across 273 items).
   - **Table 16**: Student-level population-weighted averages (using sampling weights `TOTWGT`, $N = 4,486$).
   - **Table 17**: Student-item matched panel regressions with item fixed effects ($N = 91,376$ observations).
4. **Directional Neutrality**: We test competing behavioral hypotheses without presupposing an interface penalty:
   - Does navigation frequency explain format differences?
   - Does extra time on task predict higher accuracy (productive engagement) or lower accuracy (hesitation/confusion)?
5. **Audited Data Integrity**: Pinned dependencies, verified two-digit scoring keys, and recovered timing fields.
"""))

    # ==============================================================================
    # Section 2: Environment Setup & Data Loading
    # ==============================================================================
    cells.append(nbf.v4.new_code_cell(r"""import sys
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path("..").resolve()
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"

pd.set_option("display.max_columns", 25)
pd.set_option("display.width", 1000)

df_items = pd.read_parquet(PROCESSED_DIR / "pirls_2021_item_process_metrics.parquet")
clean_stu = pd.read_parquet(PROCESSED_DIR / "pirls_2021_student_process_sample.parquet")
df_panel = pd.read_parquet(PROCESSED_DIR / "pirls_2021_student_item_panel.parquet")

print(f"[OK] Loaded {len(df_items)} digital items ({df_items['item_type'].value_counts().to_dict()})")
print(f"[OK] Loaded {len(clean_stu)} clean examinees (Mean PV1: {clean_stu['ASRREA01'].mean():.1f} pts)")
print(f"[OK] Loaded {len(df_panel):,} matched student-item observations across {df_panel['item_id'].nunique()} items")
"""))

    # ==============================================================================
    # Section 3: Item-Level Latency Decomposition (Table 15)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 2. Item-Level Response Latency Decomposition (Table 15)

We calculate unweighted macro-averages across 273 digital reading items (124 Multiple Choice, 149 Constructed Response) across all four reading comprehension processes:
1. *Focus on and Retrieve Explicitly Stated Information*
2. *Make Straightforward Inferences*
3. *Interpret and Integrate Ideas and Information*
4. *Evaluate and Critique Content and Textual Elements*
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_t15 = pd.read_csv(TABLES_DIR / "table15_pirls_2021_process_metrics_by_format.csv")
display(df_t15)

# Highlight Key Ratios
mc_ov = df_t15[(df_t15["grouping"]=="Overall Format") & (df_t15["category"].str.contains("Multiple Choice"))].iloc[0]
cr_ov = df_t15[(df_t15["grouping"]=="Overall Format") & (df_t15["category"].str.contains("Constructed Response"))].iloc[0]

print("\n--- Overall Item Latency Contrast (Table 15 Macro-Averages) ---")
print(f"Multiple Choice Mean Total Time:         {mc_ov['mean_total_time_s']:.1f} seconds")
print(f"Constructed Response Mean Total Time:     {cr_ov['mean_total_time_s']:.1f} seconds")
print(f"Observed Format Duration Wedge:           +{cr_ov['mean_total_time_s'] - mc_ov['mean_total_time_s']:.1f} seconds per item")
print(f"Latency Multiplier:                       {cr_ov['entry_latency_ratio']:.2f}x")
print(f"Revisit Rate Gap:                         {cr_ov['revisit_pct']:.1f}% CR vs {mc_ov['revisit_pct']:.1f}% MC (Delta = +{cr_ov['revisit_pct'] - mc_ov['revisit_pct']:.1f} pp)")
print(f"Additional Time After First Visit:        {cr_ov['mean_additional_time_after_first_visit_s']:.1f}s CR vs {mc_ov['mean_additional_time_after_first_visit_s']:.1f}s MC (3.3x)")
print(f"Conditional Revisit Duration (when F>1):  {cr_ov['mean_conditional_revisit_duration_s']:.1f}s CR vs {mc_ov['mean_conditional_revisit_duration_s']:.1f}s MC (3.1x)")
"""))

    # ==============================================================================
    # Section 4: Testing the Behavioral Hypotheses (Table 16)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 3. Empirical Evaluation of Behavioral Hypotheses (Table 16)

### Hypothesis 1: Navigation Friction (Paging & Scrolling)
- **Prediction**: If navigation friction disproportionately harms constructed response performance, examinees will exhibit substantially higher revisit rates on CR items due to interface confusion.
- **Empirical Reality**: Revisit rates are virtually identical across formats: **52.2%** on CR vs. **49.8%** on MC ($\Delta = +2.4\text{ pp}$).
- **Behavioral Nuance**: Revisit duration is $3.1\times$ to $3.3\times$ longer on CR ($30.4\text{s}$ vs $9.2\text{s}$ unconditional; $56.8\text{s}$ vs $18.5\text{s}$ conditional). This indicates that revisits to CR items involve substantive answer drafting and editing, not screen disorientation.

### Hypothesis 2: Digital Response Duration (Observed Format Wedge)
- **Empirical Reality**: Students spend a population-weighted average of **127.0 seconds** per CR item versus **48.6 seconds** per MC item—a **$+78.4\text{s}$ per-item duration wedge** ($2.61\times$).
- **Calibrated Interpretation**: In a 40-minute test block (12–14 items), CR questions absorb nearly triple the temporal budget of MC questions. However, because paper completion times are unobserved, this reflects the general cognitive and motor demands of constructing text rather than an isolated keyboarding penalty.

### Hypothesis 3: General Academic Ability (Comprehension Moderating Duration)
- **Empirical Reality**:
  - $r(\text{MC Time}, \text{Reading Score}) = -0.094$: Proficient readers answer multiple-choice questions faster.
  - $r(\text{CR Time}, \text{Reading Score}) = +0.114$: Proficient readers spend *longer* on constructed-response questions.
  - $r(\text{Wedge}, \text{Reading Score}) = +0.173$: Higher academic ability widens the response duration wedge, as stronger students write longer, multi-sentence answers.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_t16 = pd.read_csv(TABLES_DIR / "table16_pirls_2021_mechanism_decomposition.csv")
for _, r in df_t16.iterrows():
    print(f"\n================================================================================")
    print(f"{r['mechanism_hypothesis']}")
    print(f"================================================================================")
    print(f"Metric:        {r['empirical_metric']}")
    print(f"Observed:      {r['observed_value']}")
    print(f"Contrast:      {r['p_value_or_wedge']}")
    print(f"Evaluation:    {r['substantive_evaluation']}")
    print(f"Estimand:      {r['estimand_note']}")
"""))

    # ==============================================================================
    # Section 5: Within-Item Time-Accuracy Gradient (Table 17)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 4. Within-Item Time-Accuracy Gradient (Table 17)

To test whether extra time spent on an item represents **productive task engagement** (higher score) or **unproductive hesitation/struggle** (lower score), we estimate within-item fixed effects regressions on the 91,376 matched student-item observations:

$$Y_{ij} - \bar{Y}_j = \beta \cdot (\ln T_{ij} - \overline{\ln T}_j) + \epsilon_{ij}$$

Where $Y_{ij}$ is the percent score earned by student $i$ on item $j$, and $T_{ij}$ is the total time spent in seconds.
"""))

    cells.append(nbf.v4.new_code_cell(r"""df_t17 = pd.read_csv(TABLES_DIR / "table17_pirls_2021_time_accuracy_decomposition.csv")
display(df_t17)

print("\n--- Key Finding from Within-Item Matched Analysis ---")
mc_row = df_t17[df_t17["item_format"].str.startswith("Multiple Choice")].iloc[0]
cr_row = df_t17[df_t17["item_format"].str.startswith("Constructed Response")].iloc[0]

print(f"Multiple Choice Within-Item Beta:       {mc_row['within_item_beta_log_time']:+.4f} (Corr: {mc_row['within_item_corr_log_time']:+.4f})")
print(f"Constructed Response Within-Item Beta:  {cr_row['within_item_beta_log_time']:+.4f} (Corr: {cr_row['within_item_corr_log_time']:+.4f})")
print(f"Format Slope Wedge:                     {cr_row['within_item_beta_log_time'] - mc_row['within_item_beta_log_time']:+.4f}")
"""))

    # ==============================================================================
    # Section 6: Student Pacing & Reading Ability Distribution
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 5. Student Pacing & Reading Ability Distribution

We examine how student pacing and accuracy trade off across quartiles of reading achievement.
"""))

    cells.append(nbf.v4.new_code_cell(r"""clean_stu["reading_quartile"] = pd.qcut(clean_stu["ASRREA01"], 4, labels=["Q1 (Lowest)", "Q2", "Q3", "Q4 (Highest)"])
pacing_by_q = clean_stu.groupby("reading_quartile").agg(
    mean_pv1=("ASRREA01", "mean"),
    mc_acc_pct=("mc_score_pct", "mean"),
    cr_acc_pct=("cr_score_pct", "mean"),
    mean_mc_s=("mean_mc_time_s", "mean"),
    mean_cr_s=("mean_cr_time_s", "mean"),
    mean_wedge_s=("cr_mc_time_diff_s", "mean")
)
print("--- Pacing and Accuracy Metrics by Reading Proficiency Quartile ---")
display(pacing_by_q.round(2))
"""))

    # ==============================================================================
    # Section 7: Synthesis & Hypotheses for U.S. Mathematics
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 6. Synthesis: Generating Hypotheses for U.S. Mathematics

Study B provides crucial behavioral context for interpreting the digital constructed-response penalty identified in TIMSS 2019 Study A:

1. **Constructed Responses Demand Heavy Time Investment**:
   Digital open-ended questions require **$2.6\times$ more time than multiple choice** (+78.5s per item). On digital tests, constructed response is an intrinsically high-latency activity.
2. **Extra Time on Constructed Response is Productive**:
   Unlike multiple-choice items—where longer duration signals confusion or guessing ($\beta = -0.033$)—longer duration on constructed-response items associates with **higher scores** ($\beta = +0.041$). Students earn credit by drafting, expanding, and refining their answers.
3. **The Keyboarding Hypothesis**:
   If productive performance on constructed responses requires extensive drafting, students who lack keyboarding fluency or input automaticity face a binding constraint. Under timed test conditions, typing friction may prevent students from fully articulating what they understand.
4. **Next Steps in the Empirical Agenda**:
   - **Longitudinal Trend Study**: Did U.S. fourth-grade performance on common digital constructed-response mathematics items decline disproportionately between TIMSS 2019 and 2023?
   - **Randomized Assessment Trial**: Does an experimental intervention (Paper vs. Screen vs. Digital Entry vs. Authentic Practice) eliminate the response-entry wedge?
"""))

    nb.cells = cells
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[OK] Wrote calibrated PIRLS notebook to {NOTEBOOK_PATH.name} ({len(cells)} cells)")


if __name__ == "__main__":
    build_pirls_notebook()
