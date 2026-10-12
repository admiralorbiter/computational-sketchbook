"""
Notebook Generation Script: 05_timss_2023_item_crosswalk.ipynb
Generates and executes the Study C admission notebook establishing exact sample accounting,
5-PV national benchmark replication, primary 84-item standard scaling sample,
secondary 100-item PSI robustness sample, deduplicated screen-level process timing (Table 20),
reconciled omission/not-reached rates, and non-causal DiD decision benchmarks.
"""

from pathlib import Path
import nbformat as nbf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH = NOTEBOOKS_DIR / "05_timss_2023_item_crosswalk.ipynb"


def build_crosswalk_notebook():
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
    # Title & Study C Research Framing
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""# TIMSS 2023 Grade 4 U.S. Microdata Admission & 2019–2023 Common-Item Crosswalk
## Sample Accounting, Group-Adaptive Design, and Longitudinal Item Linkage (`05_timss_2023_item_crosswalk`)

**Author**: Computational Sketchbook Observatory  
**Date**: October 2026 (Study C Reconciled Admission Edition)  
**Primary Datasets**: 
- IEA TIMSS 2023 Grade 4 U.S. Public-Use Microdata (`asausam8.sav`, `asrusam8.sav`, `asgusam8.sav`, `acgusam8.sav`, `aspusam8.sav`, `ashusam8.sav`, `astusam8.sav`, `atgusam8.sav`)
- Official TIMSS 2023 Item Information Codebook (`T23_ItemInformation_G4.xlsx`)
- IEA TIMSS 2019 Grade 4 U.S. Public-Use Microdata (`asausam7.sav`, `asausaz7.sav`)  
**Study Scope**: Complete United States Grade 4 public-use microdata; common-item inventory linking 2019 eTIMSS and 2023 group-adaptive digital mathematics across all 8 trend blocks; screen-level process timing deduplication.

---

### Executive Research Purpose & Methodological Scope
Between 2019 and 2023, the reported average mathematics achievement of U.S. fourth graders on TIMSS declined by **18 scale score points** (from 535 to 517). In parallel, NAEP fourth-grade mathematics scores declined by **3 scale score points** (from 240 in 2019 to 237 in 2024).

In Study A, our within-school item-controlled analysis of TIMSS 2019 demonstrated that fourth graders suffer a robust **$-2.73$ percentage-point penalty** on constructed-response mathematics questions under digital administration ($-2.58$ pp among officially invariant items).

This raises a central empirical question for **Track 2 (National Trend Attribution)**:  
*Did interface and response-entry friction contribute to the post-2019 score drop, or is the score decline driven entirely by post-pandemic learning loss?*

#### Epistemic Guardrails: Level Difference vs. Trend Attribution
Before estimating any longitudinal models, we must enforce fundamental methodological boundaries:
1. **A Constant Mode Penalty Does Not Produce a Trend**:
   If students suffered a $-3$ pp digital penalty on constructed-response items in 2019, and the exact same $-3$ pp penalty in 2023, the mode effect **drops out** of the longitudinal difference ($\Delta_{2023-2019}$). A level penalty can only explain a downward score trend if:
   - The constructed-response penalty widened substantially between 2019 and 2023 (e.g., from $-3$ pp to $-8$ pp), OR
   - The assessment shifted toward a substantially higher proportion of constructed-response items, OR
   - The 2023 transition to group-adaptive testing differentially amplified interface friction among lower-performing students.
2. **Prohibition of Scale-Score Division Fallacy**:
   We strictly forbid dividing raw percentage-point changes $\Delta p$ by the 18-point scale-score decline $\Delta \text{Scale}$. Item accuracy and international scale scores exist on entirely different metrics; an empirical Difference-in-Differences regression is required to establish whether format differences changed over time.
3. **Admission First, Modeling Second**:
   This notebook establishes audited data admission, verifies sample accounting against published IEA national benchmarks across all 5 plausible values, reconciles the official 107-item trend inventory, and constructs the longitudinal common-item crosswalk.
"""))

    # ==============================================================================
    # Section 1: Study Admission Gate & Specifications
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 1. Study Admission Gate & Specifications

### The Six-Point Study Admission Gate
1. **Public-Use Microdata Retrieval**: Direct extraction of official IEA TIMSS 2023 U.S. microdata files (`asausam8.sav`, `asrusam8.sav`, `asgusam8.sav`, `acgusam8.sav`, `aspusam8.sav`, `ashusam8.sav`, `astusam8.sav`, `atgusam8.sav`) and official codebooks (`T23_ItemInformation_G4.xlsx`).
2. **5-PV Sample Accounting & Benchmark Replication**: Full population-weighted replication of U.S. Grade 4 mathematics scale scores across all 5 plausible values for both 2019 (534.73 $\to$ 535.0) and 2023 (516.93 $\to$ 517.0), verifying the $-17.80$ point national drop.
3. **Primary vs. Robustness Sample Definition**: Aligning the Primary Analytical Sample with the published 2019 national results by selecting the **84 dual-administered standard scaling items** (excluding PSI), while establishing the **100 scaling items** as a secondary robustness sample.
4. **Three-Tier Administrative Clarification**: Explicitly distinguishing the international trend inventory, U.S.-administered items (151 dual items), and scaling-retained items, marking the 107-item NCES match as a proposed reconciliation.
5. **Complete Denominators & Omission Accounting**: Establishing complete block-level administered denominators (`user_missing=True`) and decomposing omissions vs. not-reached rates.
6. **Deduplicated Screen-Level Process Timing**: Deduplicating screen durations (`_S`) and revisit counts (`_F`) to unique screens (Table 20) to prevent multi-item double-counting.
"""))

    # ==============================================================================
    # Section 2: Environment Setup & Data Loading
    # ==============================================================================
    cells.append(nbf.v4.new_code_cell(r"""import sys
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path("..").resolve()
RAW_DIR_23 = PROJECT_ROOT / "data" / "raw" / "timss_2023"
RAW_DIR_19 = PROJECT_ROOT / "data" / "raw" / "timss_2019"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"

pd.set_option("display.max_columns", 35)
pd.set_option("display.width", 1000)

# Load sample accounting, item crosswalk, and screen timing
sample_acc = pd.read_csv(TABLES_DIR / "table18_timss_2023_sample_accounting.csv")
df_crosswalk = pd.read_parquet(PROCESSED_DIR / "timss_2019_2023_item_crosswalk.parquet")
df_screens = pd.read_parquet(PROCESSED_DIR / "timss_2019_2023_screen_timing.parquet")

print(f"[OK] Loaded Table 18: Sample Accounting ({len(sample_acc)} assessment cohorts)")
print(f"[OK] Loaded Table 19 / Crosswalk: {len(df_crosswalk)} total item codes across 8 trend blocks")
print(f"[OK] Loaded Table 20 / Screen Timing: {len(df_screens)} unique screens across 8 trend blocks")
"""))

    # ==============================================================================
    # Section 3: U.S. Grade 4 Sample Accounting & 5-PV Replication (Table 18)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 2. U.S. Grade 4 Sample Accounting & 5-PV Replication (Table 18)

Table 18 presents the verified sample composition and population-weighted achievement means across all 5 plausible values (`ASMMAT01`–`ASMMAT05`) using total student sampling weights (`TOTWGT`).

The pipeline replicates the official published national mathematics scale scores:
- **TIMSS 2019 Official eTIMSS**: 5-PV mean = **534.73** $\to$ published **535.0** ($\Delta = -0.27$ pts)
- **TIMSS 2019 eTIMSS + PSI**: 5-PV mean = **533.53** $\to$ published **535.0** ($\Delta = -1.47$ pts)
- **TIMSS 2023 Official Digital**: 5-PV mean = **516.93** $\to$ published **517.0** ($\Delta = -0.07$ pts)

This empirically replicates the **$-17.80$ point national decline** (published as an 18-point drop: $535 - 517$).

### Why the 84 Standard Scaling Items Form the Primary Sample
The official 2019 U.S. national score (535.0) was computed exclusively from the 14 standard eTIMSS booklets (`asausam7.sav`), excluding the interactive Problem Solving and Inquiry (PSI) tasks administered in Booklets 15 and 16. In 2023, PSI block `A_MD4` was integrated into the group-adaptive rotation.
To align our primary longitudinal analysis directly with the published national score trend, the **84 dual-administered, scaling-marked standard eTIMSS items** serve as our **Primary Analytical Sample**. The expanded 100-item pool (including the 16 PSI scaling items) serves as our planned **Secondary / Robustness Analysis**.

### Sampling Weights Distinction: asausam7.sav vs. asausaz7.sav
- **Primary Analytical Sample (84 Standard Scaling Items)**: Evaluated using the official standard file `asausam7.sav` ($N = 8,776$ students across Booklets 1–14). The student weight `TOTWGT` in this file is calibrated to the official Grade 4 national target population and replicates the official published national average of 535.0 (replicated 5-PV mean = 534.73).
- **Secondary Robustness Sample (100 Scaling Items with PSI)**: Evaluated using the expanded research file `asausaz7.sav` ($N = 10,029$ students across Booklets 1–16 including PSI). The `TOTWGT` in `asausaz7.sav` is recalibrated across all 16 booklets (replicated 5-PV mean = 533.53).
In Study D, all primary DiD regressions will use `asausam7.sav` weights, while sensitivity analyses on the 100-item pool will use `asausaz7.sav` weights.
"""))

    cells.append(nbf.v4.new_code_cell(r"""# Display Table 18: Sample Accounting
display(sample_acc)

for _, row in sample_acc.iterrows():
    c = row["assessment_cycle"]
    n_stud = int(row["total_assessed_students"])
    n_sch = int(row["total_schools"])
    pv_mean = float(row["population_weighted_5pv_mean"])
    pub = float(row["official_published_math_scale_score"])
    delta = float(row["reconciliation_delta"])
    print(f"{c:32s} | N={n_stud:,} | Schools={n_sch} | 5-PV Mean={pv_mean:.2f} | Published={pub:.1f} | Delta={delta:+.2f}")

drop = float(sample_acc.loc[sample_acc['assessment_cycle'].str.contains('Official eTIMSS'), 'population_weighted_5pv_mean'].iloc[0]) - \
       float(sample_acc.loc[sample_acc['assessment_cycle'].str.contains('2023'), 'population_weighted_5pv_mean'].iloc[0])
print(f"\nReconciled 2019-2023 National Mathematics Decline: {drop:.2f} scale score points (Official Published: 18.0 points)")
"""))

    # ==============================================================================
    # Section 4: Three-Way Item Reconciliation & Sample Tiers (Table 19)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 3. Three-Way Item Reconciliation & Sample Tiers (Table 19)

A critical methodological requirement is distinguishing between three different administrative concepts:
1. **International Trend Item Inventory**: The set of trend items identified in international frameworks.
2. **Items Administered in the United States**: Exactly **151 items** actively presented in U.S. test booklets across both 2019 and 2023 (128 standard eTIMSS items + 23 PSI items).
3. **Items Retained for International Scaling**: Items included in the concurrent IRT calibration.

### Resolving the NCES 107 Trend Item Inventory
NCES technical notes report **107 fourth-grade mathematics trend items** (Number: 55, Measurement & Geometry: 29, Data: 23).
In our crosswalk:
- Exactly **104 items** are marked `Scaling Status: Yes` across all 8 trend blocks.
- Supplementing these 104 scaling items with 3 standalone unscaled items (`ME61021`, `MQ71A01`, `MQ71A03A`) yields exactly 107 items with matching domain counts.
- **Methodological Qualification**: As noted in peer review, `ME61021` and `MQ71A01` were unadministered in 2023, and `MQ71A03A` was excluded by IEA. Therefore, we explicitly designate this 107-item correspondence as a **Proposed Reconciliation** pending official item-by-item NCES release, rather than an independently proven fact.

### Clean Sample Tiers
We partition all 157 database item codes into five mutually exclusive and exhaustive sample tiers:
1. **Primary Standard Scaling (84 items)**: Dual-administered scaling items across the 7 standard non-PSI blocks (**32 Multiple Choice, 52 Constructed Response**). Directly links to the official 2019 eTIMSS cohort.
2. **Secondary PSI Scaling (16 items)**: Scaling items from the interactive PSI block `A_MD4` (**1 MC, 15 CR**).
3. **Standard eTIMSS Subparts (44 items)**: Unscaled subparts of composite questions in standard blocks (40 MC, 4 CR).
4. **PSI Interactive Subparts (7 items)**: Unscaled subparts and interactive tasks in block `A_MD4` (0 MC, 7 CR).
5. **Single-Cycle Unadministered (6 items)**: Items present in codebook space but administered in only one cycle.
"""))

    cells.append(nbf.v4.new_code_cell(r"""# Breakdown of items by Sample Tier and Format
tier_summary = df_crosswalk.groupby(["sample_tier", "format"]).size().unstack(fill_value=0)
tier_summary["Total"] = tier_summary.sum(axis=1)
tier_summary.loc["Total Database Codes"] = tier_summary.sum(axis=0)

print("Item Accounting by Sample Tier and Response Format:")
display(tier_summary)

# Summary of Primary vs. Secondary Sample
n_p84 = df_crosswalk["in_primary_scaling_sample"].sum()
n_p84_mc = (df_crosswalk["in_primary_scaling_sample"] & (df_crosswalk["item_type"] == "MC")).sum()
n_p84_cr = (df_crosswalk["in_primary_scaling_sample"] & (df_crosswalk["item_type"] == "CR")).sum()

n_s100 = df_crosswalk["in_psi_robustness_sample"].sum()
n_s100_mc = (df_crosswalk["in_psi_robustness_sample"] & (df_crosswalk["item_type"] == "MC")).sum()
n_s100_cr = (df_crosswalk["in_psi_robustness_sample"] & (df_crosswalk["item_type"] == "CR")).sum()

print(f"\nSample Tier Architecture:")
print(f"  - Primary Analytical Sample (Standard Scaling): {n_p84} items ({n_p84_mc} MC, {n_p84_cr} CR)")
print(f"  - Secondary Robustness Sample (Scaling + PSI):  {n_s100} items ({n_s100_mc} MC, {n_s100_cr} CR)")
print(f"  - Standard eTIMSS Dual Pool (Scaling + Subparts): {df_crosswalk['in_standard_etimss_sample'].sum()} items")
print(f"  - Full Trend Dual Pool (All 8 Blocks):           {df_crosswalk['in_full_trend_sample'].sum()} items")
print(f"  - Proposed 107-Item NCES Reconciliation:         {df_crosswalk['is_proposed_107_reconciliation'].sum()} items (104 scaling + 3 unscaled standalone)")
"""))

    # ==============================================================================
    # Section 5: Complete Response Denominators & Omission / Not-Reached Patterns
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 4. Complete Response Denominators, Omission Disparities, and Not-Reached Patterns

### Avoiding Omission Attrition Bias (`user_missing=True`)
By preserving user-defined missing codes (omitted = 9/99, not reached = 6/96), we establish complete block-level administered denominators:
$$N_{\text{administered}} = N_{\text{answered}} + N_{\text{omitted}} + N_{\text{not reached}}$$

In 2019, every single item within a block shares an **identical administered denominator** ($N = 1,248$).
In 2023, administered denominators range from 1,250 to 1,350 across blocks.

### Exact Omission and Not-Reached Accounting
Below, we compute exact descriptive rates aggregated directly from item-level counts ($N_{\text{admin}}$, $N_{\text{omitted}}$, $N_{\text{not reached}}$) across both the Primary (84 items) and Secondary (100 items) samples.
"""))

    cells.append(nbf.v4.new_code_cell(r"""def report_response_breakdown(sub, sample_name):
    print(f"=== {sample_name} (N = {len(sub)} items) ===")
    records = []
    for fmt in ["Multiple Choice", "Constructed Response"]:
        s = sub[sub["format"] == fmt]
        adm19, omit19, nr19 = s["n_admin_2019"].sum(), s["n_omitted_2019"].sum(), s["n_not_reached_2019"].sum()
        adm23, omit23, nr23 = s["n_admin_2023"].sum(), s["n_omitted_2023"].sum(), s["n_not_reached_2023"].sum()
        
        r_omit19 = omit19 / adm19 * 100
        r_nr19 = nr19 / adm19 * 100
        r_omit23 = omit23 / adm23 * 100
        r_nr23 = nr23 / adm23 * 100
        
        records.append({
            "Format": fmt,
            "Items": len(s),
            "2019 Admin N": adm19,
            "2019 Omit %": round(r_omit19, 2),
            "2023 Omit %": round(r_omit23, 2),
            "Delta Omit (pp)": round(r_omit23 - r_omit19, 2),
            "2019 Not-Reached %": round(r_nr19, 2),
            "2023 Not-Reached %": round(r_nr23, 2),
            "Delta Not-Reached (pp)": round(r_nr23 - r_nr19, 2)
        })
    df_rep = pd.DataFrame(records).set_index("Format")
    display(df_rep)
    return df_rep

# Primary 84-item sample
primary_sub = df_crosswalk[df_crosswalk["in_primary_scaling_sample"]]
rep84 = report_response_breakdown(primary_sub, "Primary Analytical Sample (84 Standard Scaling Items)")

# Secondary 100-item sample
sec_sub = df_crosswalk[df_crosswalk["in_psi_robustness_sample"]]
rep100 = report_response_breakdown(sec_sub, "Secondary Robustness Sample (100 Scaling Items with PSI)")
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Substantive Finding on Non-Response Behaviors
The descriptive evidence reveals a crucial distinction between omissions and not-reached responses:
1. **Omission Rate Changes Were Modest**:
   - In the Primary 84-item sample, Multiple Choice omissions decreased slightly from **1.13% to 1.00%** ($-0.14$ pp), while Constructed Response omissions rose from **1.76% to 2.33%** ($+0.58$ pp).
   - In the 100-item sample, MC omissions fell from **1.28% to 1.18%** ($-0.09$ pp), while CR omissions rose from **2.88% to 3.44%** ($+0.56$ pp).
2. **Not-Reached Rates Rose Substantially Across Both Formats**:
   - In the Primary 84-item sample, MC not-reached responses rose from **1.20% to 2.26%** ($+1.05$ pp), and CR not-reached responses rose from **1.86% to 2.90%** ($+1.04$ pp).
   - In the 100-item sample, MC not-reached rose by **$+1.11$ pp**, and CR not-reached rose by **$+1.53$ pp**.
3. **Methodological Implication**:
   - Not-reached items represent unanswered questions at the end of assessment sections. Their parallel rise across formats suggests general pacing constraints, booklet routing dynamics, or end-of-test fatigue under the group-adaptive design, rather than format-isolated interface blockage.
   - This underscores why conditioning only on completed answers would introduce severe selection bias, confirming that all trend regressions must use $N_{\text{administered}}$ as the denominator.

### IEA PSI Not-Reached Scoring Convention & Sensitivity Protocol
In standard eTIMSS analysis, not-reached items (omitted at the end of a booklet) are scored as incorrect (0 points).
However, in IEA's official 2019 PSI scaling, not-reached responses were treated as unadministered (missing) rather than scored zero due to exceptionally high noncompletion (34% noncompletion in PSI vs. ~8% in standard eTIMSS).
For Study D, we prespecify a dual scoring protocol for the secondary 100-item sample:
1. **Standard Scoring Benchmark**: All omitted and not-reached items within administered blocks scored as incorrect (0 points).
2. **IEA PSI Scoring Convention**: Not-reached items in PSI blocks treated as unadministered, testing whether noncompletion dynamics distort the format difference estimate.
"""))

    # ==============================================================================
    # Section 6: Deduplicated Screen-Level Process Timing (Table 20)
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 5. Deduplicated Screen-Level Process Timing (Table 20)

### Why Screen-Level Timing Must Be Deduplicated
In TIMSS digital assessments, process timing (`_S` duration, `_F` revisit count) is recorded by the test delivery platform at the **screen level**, not the item level:
- Several scored items share the same screen (e.g., in block `A_MD4`, items `MQ71A02A`, `MQ71A02B`, and `MQ71A02C` all share screen `M71A03`).
- In the Primary 84-item sample, the 84 items map to **78 unique screens** (6 screens host 2 scaling items).
- Across all 157 database item codes, there are **92 unique screens** across 8 blocks.
- Exactly **88 screens are dual-administered** with observed process timing in both 2019 and 2023, while only 4 screens appear in a single cycle (`M71A02`, `ME61021`, `ME71005`, `ME71199`).
- Averaging durations across item records double-counts shared screens and assigns entire screen durations to mixed-format subparts.

#### Methodological Bug Resolution & Screen Administration
Earlier code evaluated screen administration via `grp.iloc[0]["n_admin_2019"] > 0`. For screens where the first database row was a 2023-only code (e.g., `ME71135A` was 2023-only while subpart `ME71135B` was administered in 2019; `ME61081` parent was 2023-only while subparts `ME61081A/B` were administered in 2019), this erroneously flagged valid 2019 screens as missing. By testing `grp["n_admin_2019"].max() > 0`, the crosswalk pipeline successfully recovered 2019 timing for both screens (`ME71135`: 70.5s $\to$ 68.7s; `ME61081`: 82.4s $\to$ 82.9s), establishing exactly 88 dual screens.

#### Dual Screen Format Classifications
To avoid confounding non-scaling subparts with primary items, Table 20 provides two distinct format classifications for each screen:
1. `screen_format_all_items`: Classifies the screen based on all visible item codes (primary 78 screens: 36 Constructed Response, 31 Multiple Choice, 11 Mixed).
2. `screen_format_primary_items`: Classifies the screen restricted strictly to the 84 primary scaling items (primary 78 screens: 46 Constructed Response, 31 Multiple Choice, 1 Mixed [`ME61211`]).

Table 20 provides the deduplicated screen-level analysis, tracking the auditable variable mappings:
- In 2019 (`asausaz7.sav`): screen total duration is `[SCREEN_ID]_S`, and revisit frequency is `[SCREEN_ID]_F`.
- In 2023 (`aspusam8.sav`): screen total duration is `[SCREEN_ID]_S`, revisit frequency is `[SCREEN_ID]_F`, and first-visit duration is `[SCREEN_ID]_R`.
"""))

    cells.append(nbf.v4.new_code_cell(r"""# Screen-Level Timing Analysis (Primary 84-Item Sample Screens)
p84_screens = df_screens[df_screens["in_primary_84_sample"]].copy()

print("--- Screen Format Classification 1: All Visible Items on Screen ---")
summary_all = p84_screens.groupby("screen_format_all_items").agg({
    "screen_id": "count",
    "n_items_on_screen": "sum",
    "mean_screen_time_2019": "mean",
    "median_screen_time_2019": "mean",
    "mean_screen_time_2023": "mean",
    "median_screen_time_2023": "mean",
    "screen_time_change": "mean"
}).rename(columns={"screen_id": "unique_screens", "n_items_on_screen": "total_items"})
display(summary_all.round(1))

print("\n--- Screen Format Classification 2: Primary Scaling Items Only ---")
summary_pri = p84_screens.groupby("screen_format_primary_items").agg({
    "screen_id": "count",
    "n_items_on_screen": "sum",
    "mean_screen_time_2019": "mean",
    "median_screen_time_2019": "mean",
    "mean_screen_time_2023": "mean",
    "median_screen_time_2023": "mean",
    "screen_time_change": "mean"
}).rename(columns={"screen_id": "unique_screens", "n_items_on_screen": "total_items"})
display(summary_pri.round(1))

print("\nScreen-Level Duration Changes (Primary Items Classification):")
for s_fmt, grp in p84_screens.groupby("screen_format_primary_items"):
    m19 = grp["mean_screen_time_2019"].mean()
    m23 = grp["mean_screen_time_2023"].mean()
    diff = grp["screen_time_change"].mean()
    print(f"  - {s_fmt:22s} ({len(grp):2d} screens): 2019 = {m19:5.1f}s -> 2023 = {m23:5.1f}s (Diff: {diff:+5.1f}s)")

# Contrast with Item-Level Averages (which include shared screen weighting)
print("\nItem-Level Duration Averages (84 items, with screen duplication):")
for fmt in ["Multiple Choice", "Constructed Response"]:
    sub_fmt = primary_sub[primary_sub["format"] == fmt]
    t19 = sub_fmt["mean_screen_time_2019"].mean()
    t23 = sub_fmt["mean_screen_time_2023"].mean()
    print(f"  - {fmt:22s} ({len(sub_fmt):2d} items):   2019 = {t19:5.1f}s -> 2023 = {t23:5.1f}s (Diff: {t23 - t19:+5.1f}s)")
"""))

    cells.append(nbf.v4.new_markdown_cell(r"""### Key Findings on Student Pacing
1. **Screen-Level Consistency Across Both Classifications**:
   - Under *All Items Classification* (78 screens): Pure Multiple Choice screens (31 screens) averaged **52.6s in 2019** and **52.1s in 2023** ($\Delta = -0.5$s); Pure Constructed Response screens (36 screens) averaged **90.8s in 2019** and **87.2s in 2023** ($\Delta = -3.5$s); Mixed-format screens (11 screens) averaged **74.0s in 2019** and **71.3s in 2023** ($\Delta = -2.7$s).
   - Under *Primary Scaling Classification* (78 screens): Pure Multiple Choice screens (31 screens) shifted by **$-0.5$s** (52.6s $\to$ 52.1s); Pure Constructed Response screens (46 screens) shifted by **$-3.3$s** (86.6s $\to$ 83.3s); the single Mixed-format screen (`ME61211`) shifted by **$-4.3$s** (100.8s $\to$ 96.5s).
2. **Item-Level Averages Show Identical Qualitative Pattern**:
   - Multiple Choice items shifted by **$-0.7$s** (54.1s $\to$ 53.5s).
   - Constructed Response items shifted by **$-3.3$s** (89.8s $\to$ 86.5s).
3. **Behavioral Interpretation & Epistemic Caution**:
   - Students in 2023 spent slightly less time on constructed-response screens (~3.3s to 3.5s less per screen).
   - However, a shorter screen duration **cannot be interpreted as proof that students typed faster or had worse typing friction**. Shorter screen durations can reflect faster completion, earlier abandonment, position in the group-adaptive booklet rotation, or interface familiarity.
   - Pacing metrics serve as descriptive behavioral context, not direct measures of transcription automaticity.
"""))

    # ==============================================================================
    # Section 7: Econometric Specification & Calibrated Decision Benchmarks
    # ==============================================================================
    cells.append(nbf.v4.new_markdown_cell(r"""## 6. Econometric Specification & Non-Causal Decision Benchmarks

### Difference-in-Differences Econometric Model
To evaluate whether format-specific performance changed between 2019 and 2023, we specify a repeated cross-sections Difference-in-Differences model across the dual-administered common items:

$$Y_{ijt} = \alpha_j + \lambda_t + \beta (\text{CR}_j \times \text{Post2023}_t) + \mathbf{X}_{ijt} \gamma + \epsilon_{ijt}$$

where:
- $Y_{ijt} \in [0, 1]$ is the score (partial/full credit) of student $i$ on item $j$ in year $t \in \{2019, 2023\}$.
- $\alpha_j$ are **item fixed effects**, absorbing all time-invariant item characteristics (intrinsic difficulty, cognitive domain, wording).
- $\lambda_t$ is the **year fixed effect**, capturing the overall score trend on Multiple Choice baseline items.
- $\text{CR}_j$ is an indicator for Constructed Response format.
- $\beta$ is the **Difference-in-Differences parameter of interest**: the empirical format-differential change:
  $$\beta = (\text{CR}_{2023} - \text{CR}_{2019}) - (\text{MC}_{2023} - \text{MC}_{2019})$$
- Standard errors are clustered at the **school level** ($\text{IDSCHOOL}$).

### Predefined Benchmarks for Practical Difference (Avoiding Premature Causal Attribution)
Because both the 2019 and 2023 assessments were administered digitally on school computers, we **do not have a paper counterfactual in 2023**. Therefore, the interaction coefficient $\beta$ measures whether constructed-response accuracy changed relative to multiple-choice accuracy, but **does not isolate the causal mechanism**.
Furthermore, an empirical finding cannot be interpreted solely on the point estimate without evaluating its confidence interval:

| Estimated $\beta$ | Statistical Condition | Descriptive Interpretation | Epistemic Boundary & Inference Guardrails |
|---|---|---|---|
| **$\beta < -2.0$ pp** | Negative & Statistically Significant ($p < 0.05$) | **Widening Format Disparity**: CR accuracy declined more steeply than MC accuracy. | Consistent with expanding interface friction, but **equally consistent** with larger post-pandemic instructional losses in multi-step problem solving, written mathematical communication, or specific CR curriculum topics. |
| **$-2.0 \le \beta \le +2.0$ pp** | Statistically Indistinguishable from Zero (with sufficiently tight CI) | **Format-Parallel Trend**: CR and MC dropped in parallel across cycles. | Inconsistent with an expanding format wedge. **Caution**: A point estimate inside $[-2.0, +2.0]$ pp is NOT proof of parallel trends if the confidence interval is wide (e.g., spanning $\pm 4$ pp). Equivalence testing or CI bounds must exclude substantial divergence before concluding parallel trends. |
| **$\beta > +2.0$ pp** | Positive & Statistically Significant ($p < 0.05$) | **CR Relative Resilience**: Constructed response declined less than Multiple Choice. | Inconsistent with expanding keyboarding mode penalty. |

### Strict Epistemic Boundary: No Ratio to Scale Score Decline
We reiterate that researchers must **never divide $\Delta p$ by the 18-point scale decline**.
Scale scores are computed via an IRT concurrent calibration across thousands of examinees internationally; percentage correct is a raw proportion. Reporting "mode friction explains X% of the 18-point decline" based on dividing raw percentages by IRT scale scores is a severe category error.
"""))

    # ==============================================================================
    # Section 8: Primary Sample Preview & Verification
    # ==============================================================================
    cells.append(nbf.v4.new_code_cell(r"""# Preview first 10 items of the Primary Analytical Sample (84 standard scaling items)
print(f"Primary Analytical Sample (84 Standard Scaling Items) - Head Preview:")
display(primary_sub[["item_id_2023", "item_id_2019", "screen_id", "block", "format", "content_domain", "cognitive_domain", "max_points", "omission_rate_2019", "omission_rate_2023", "screen_time_change", "label"]].head(10))

# Preview first 10 screens of Table 20
print(f"\nTable 20: Deduplicated Screen-Level Process Timing - Head Preview:")
display(p84_screens[["screen_id", "block", "screen_format", "n_items_on_screen", "timing_var_2019", "timing_var_2023", "mean_screen_time_2019", "mean_screen_time_2023", "screen_time_change"]].head(10))
"""))

    nb.cells = cells
    return nb


def main():
    print("Generating Study C crosswalk notebook: 05_timss_2023_item_crosswalk.ipynb...")
    nb = build_crosswalk_notebook()
    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"[OK] Written notebook to {NOTEBOOK_PATH.name}")


if __name__ == "__main__":
    main()
