"""
Script to build and execute the Missouri CRDC Educational Opportunity Measurement Notebook:
notebooks/01_measuring_educational_opportunity.ipynb
"""

import subprocess
from pathlib import Path
import nbformat as nbf

PROJECT_DIR = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_DIR / "notebooks" / "01_measuring_educational_opportunity.ipynb"

nb = nbf.v4.new_notebook()
cells = []

# ==============================================================================
# 1. Title & Executive Abstract
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""# Measuring Educational Opportunity: Proxy Definitions, Subject Concealment, and Denominator Wedges
### A Disciplined Empirical Measurement Study of Missouri High Schools (2021–22 CRDC & NCES CCD)
**Computational Sketchbook: Education Policy & Measurement Observatory**  
*Data Sources: U.S. Department of Education Office for Civil Rights (OCR) Civil Rights Data Collection (CRDC 2021–22) and National Center for Education Statistics (NCES) Common Core of Data (CCD 2021–22 Directory).*

---

## Executive Summary & Problem Formulation

When policymakers and researchers evaluate educational opportunity, they rely on administrative proxies:
- *"Does a school offer Advanced Placement (AP)?"*
- *"Do students have access to foundational STEM coursework like Physics or Computer Science?"*

However, empirical measurement routinely breaks down across three distinct vulnerabilities:
1. **Indicator Misinterpretation**: Survey indicators often measure reported *student participation* rather than institutional *course availability*, altering what research questions can be credibly answered.
2. **Proxy Blind Spots**: Relying on a single canonical advanced course pathway (such as the College Board's AP program) blinds researchers to parallel institutional pathways (such as Dual Enrollment and college-in-the-high-school partnerships).
3. **Denominator Divergence**: Reporting unweighted institutional counts (*"a third of high schools lack physics"*) describes a fundamentally different social reality than reporting student exposure (*"less than a fifth of students lack physics"*), because course offerings scale systematically with school enrollment.

This notebook establishes an auditable, six-point admission rule for measurement studies and executes three strictly bounded empirical analyses across Missouri's 2021–22 public high schools.
"""))

# ==============================================================================
# 2. Epistemic Philosophy & The Six-Point Admission Gate
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 1. Epistemic Philosophy: The Six-Point Study Admission Gate

Before specifying regressions or estimating causal parameters, empirical inquiry requires disciplined measurement. We enforce the following **Six-Point Study Admission Gate**:

1. **Retrieval & Usability**: The underlying administrative records are retrieved, and the required fields contain audited, usable values.
2. **Fixed Population & Denominator**: The population boundaries, exclusions, and denominators are fixed in code and narrative prior to analysis.
3. **Written Mathematical Model**: The calculation or statistical estimator is written down explicitly.
4. **Directional Neutrality**: A result of any direction—including no difference or an unexpected null—substantively answers the question.
5. **Audited Sensitivity Check**: Remaining structural uncertainty (such as conflicting inter-agency reporting) is bounded by a specified sensitivity check.
6. **Scholarly & Survey Integrity**: The exact contribution is checked against prior literature and official survey documentation.

### Research Stage Demarcation

| Stage | Goal | Machinery | Role of Regressions / CIs |
| :--- | :--- | :--- | :--- |
| **Stage 1: Measurement Study** *(This Work)* | Measure how proxy definitions, exclusions, and denominators alter reality | Direct counts, cross-tabulations, conditional rates, percentage-point difference wedges | **None needed.** Uncertainty stems from reporting accuracy, exclusions, and survey definitions—not sampling error. |
| **Stage 2: Association Study** | Measure demographic sorting and institutional correlates | Stratified tabulations, multivariate regressions, Shapley decompositions | Requires explicit pre-registration of comparison groups and model controls. |
| **Stage 3: Causal Effect Study** | Estimate policy impacts on student learning or adult wages | Quasi-experimental designs, regression discontinuities, lottery controls | Feasible only when a credible exogenous identification strategy exists. |
"""))

# ==============================================================================
# 3. Setup & Data Loading
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 2. Environment Setup & Data Ingestion

We load the standardized Missouri High School CRDC Measurement Panel constructed by `src/build_panel.py`.
"""))

cells.append(nbf.v4.new_code_cell("""import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import IPython.display as display

# Setup project directories
NOTEBOOK_DIR = Path.cwd()
PROJECT_DIR = NOTEBOOK_DIR.parent if NOTEBOOK_DIR.name == "notebooks" else NOTEBOOK_DIR
DATA_PROCESSED = PROJECT_DIR / "data" / "processed"
ARTIFACTS_DIR = PROJECT_DIR / "artifacts"

# Load master panel and funnel
panel = pd.read_parquet(DATA_PROCESSED / "mo_high_school_crdc_measurement_panel_2021_22.parquet")
funnel = pd.read_csv(DATA_PROCESSED / "population_exclusion_funnel.csv")

print(f"Loaded master panel: {len(panel)} school records")
funnel
"""))

# ==============================================================================
# 4. Population Accounting & Exclusions Funnel
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 3. Population Accounting & Bounded Cohort Derivation

Our target population is **regular public high schools serving exactly grades 9–12 in Missouri during SY 2021–22**.

### The Derivation Funnel:
1. **Initial Selection (CCD)**: Starting with the NCES CCD Directory (SY 2021–22), filtering for `ST == 'MO'`, `SCH_TYPE_TEXT == 'Regular School'`, `GSLO == '09'`, `GSHI == '12'`, and `SY_STATUS_TEXT == 'Open'` yields exactly **318 schools**. This excludes vocational/technical centers, special education facilities, alternative schools, closed/future schools, and combined-grade schools (such as grades 7–12).
2. **CRDC Record Linkage**: Merging against the 2021–22 CRDC School Characteristics file via 12-digit NCES school IDs (`COMBOKEY`) matches **317 schools** (99.7% linkage). Exactly one school—*Hawthorn High School* in Kansas City (`290060803317`)—is present in CCD but absent in the CRDC collection.
3. **Grade-Span Reporting Consistency**: Examining the 15 grade indicators in CRDC (`SCH_GRADE_PS` through `SCH_GRADE_UG`), **307 schools** report consistent grades 9–12 configurations (all four high school grades reported as "Yes", and all other grades reported as "No").
4. **Quarantined Sensitivity Group**: Exactly **10 schools** report conflicting grade spans in CRDC (e.g., reporting preschool, elementary grades, or ungraded students alongside secondary grades). These 10 schools are quarantined and evaluated in sensitivity checks.
"""))

cells.append(nbf.v4.new_code_cell("""# Inspect the 10 schools with conflicting grade-span reporting
conflicting_10 = panel[panel['flag_conflicting_span']][['school_name', 'district_name', 'crdc_reported_grades', 'ap_indicator_raw', 'dual_indicator_raw']]
print(f"Conflicting Grade-Span Schools (N={len(conflicting_10)}):")
conflicting_10
"""))

# ==============================================================================
# 5. Study 1 (Pilot): AP vs. Dual Enrollment
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 4. Study 1 (Pilot): AP vs. Dual-Enrollment Participation

### The Survey Documentation Correction
In official CRDC survey documentation ([OCR School Form, Items 10 & 11](https://www.ed.gov/sites/ed/files/about/offices/list/ocr/docs/2021-22-crdc-school-form.pdf)):
- `SCH_APENR_IND`: *"Are students enrolled in Advanced Placement (AP) courses?"*
- `SCH_DUAL_IND`: *"Are students enrolled in dual enrollment or dual credit programs?"*

Both items measure **reported student participation/enrollment**, not mere catalog offerings.

### Narrow Question
> **Among Missouri high schools reporting no AP participation, how many reported dual-enrollment participation?**

### Statistical Path & Calculation
We construct a four-cell contingency table crossing `SCH_APENR_IND` and `SCH_DUAL_IND`. We calculate the conditional rate:
$$\\text{Rate}_{\\text{Dual} | \\text{No AP}} = \\frac{N(\\text{No AP} \\land \\text{Yes Dual})}{N(\\text{No AP})}$$
"""))

cells.append(nbf.v4.new_code_cell("""# 1. Filter to baseline 307 consistent schools
df_307 = panel[panel['flag_consistent_9_12']].copy()

# 2. Four-cell contingency table (Counts)
ct_counts = pd.crosstab(
    df_307['ap_indicator_raw'],
    df_307['dual_indicator_raw'],
    margins=True,
    margins_name="Total"
)
print("=== STUDY 1: FOUR-CELL CONTINGENCY TABLE (COUNTS) ===")
display.display(ct_counts)

# 3. Four-cell table (Percentages of total 307)
ct_pct = (pd.crosstab(
    df_307['ap_indicator_raw'],
    df_307['dual_indicator_raw'],
    margins=True,
    margins_name="Total",
    normalize='all'
) * 100).round(2)
print("\\n=== STUDY 1: CONTINGENCY TABLE (% OF TOTAL 307 SCHOOLS) ===")
display.display(ct_pct)

# 4. Conditional rate
no_ap_307 = df_307[df_307['ap_indicator_raw'] == 'No']
n_no_ap = len(no_ap_307)
n_dual_in_no_ap = (no_ap_307['dual_indicator_raw'] == 'Yes').sum()
rate_307 = (n_dual_in_no_ap / n_no_ap) * 100

print(f"\\nKey Conditional Metric (Baseline 307):")
print(f"Schools reporting No AP participation: {n_no_ap} of 307 ({n_no_ap / len(df_307) * 100:.1f}%)")
print(f"Dual-Enrollment participation among No-AP schools: {n_dual_in_no_ap} of {n_no_ap} = {rate_307:.1f}% ({rate_307:.3f}%)")
"""))

cells.append(nbf.v4.new_markdown_cell("""### Sensitivity Check: Broad Sample (N=317)
We repeat the calculation including the 10 schools with conflicting grade-span reporting.
"""))

cells.append(nbf.v4.new_code_cell("""# Sensitivity calculation across all 317 matched schools
df_317 = panel[panel['flag_matched_crdc']].copy()
no_ap_317 = df_317[df_317['ap_indicator_raw'] == 'No']
n_no_ap_317 = len(no_ap_317)
n_dual_317 = (no_ap_317['dual_indicator_raw'] == 'Yes').sum()
rate_317 = (n_dual_317 / n_no_ap_317) * 100

print("=== STUDY 1: SENSITIVITY COMPARISON ===")
print(f"Baseline (307 Consistent): {n_dual_in_no_ap} of {n_no_ap} = {rate_307:.2f}%")
print(f"Sensitivity (317 Matched): {n_dual_317} of {n_no_ap_317} = {rate_317:.2f}%")
print(f"Difference: {rate_317 - rate_307:+.2f} percentage points")
"""))

cells.append(nbf.v4.new_markdown_cell("""### Visualization: Figure 1
The four-cell matrix and conditional non-AP breakdown:
"""))

cells.append(nbf.v4.new_code_cell("""display.Image(filename=str(ARTIFACTS_DIR / "fig1_ap_dual_contingency.png"), width=850)
"""))

cells.append(nbf.v4.new_markdown_cell("""### Scholarly Interpretation & Epistemic Boundaries
- **Claim Supported**: An AP-only measure misses **92.9%** (105 of 113) of Missouri high schools reporting advanced coursework participation through dual enrollment. Across all 307 schools, only **8 schools (2.6%)** report neither AP nor Dual Enrollment.
- **Boundaries**: This study answers a small, highly specific measurement question. It does **not** establish program quality, whether credits successfully transfer, how many students enroll per school, or whether participants experience long-term earnings benefits. Those require distinct studies.
"""))

# ==============================================================================
# 6. Study 2: Curricular Concealment in AP (Computer Science)
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 5. Study 2: Curricular Concealment in AP (The Case of Computer Science)

### Motivation
School accountability dashboards and real estate aggregators frequently award binary credit for "AP Programs". But does a general AP indicator ensure subject breadth, or does it conceal the complete absence of foundational modern coursework?

### Narrow Question
> **Among schools reporting AP participation, what percentage reported no AP Computer Science participation?**

### Statistical Path & Calculation
We restrict the sample to high schools reporting `SCH_APENR_IND == 'Yes'` (N=194 in the baseline 307 cohort), and calculate the proportion reporting `SCH_APCOMPENR_IND == 'No'`:
$$\\text{Concealment Rate}_{\\text{AP CS}} = \\frac{N(\\text{Yes AP} \\land \\text{No AP CS})}{N(\\text{Yes AP})}$$
"""))

cells.append(nbf.v4.new_code_cell("""# Restrict to AP-participating schools
ap_schools_307 = df_307[df_307['ap_participating']].copy()
n_ap_307 = len(ap_schools_307)

cs_counts_307 = ap_schools_307['ap_cs_indicator_raw'].value_counts()
n_no_cs_307 = (ap_schools_307['ap_cs_indicator_raw'] == 'No').sum()
n_yes_cs_307 = (ap_schools_307['ap_cs_indicator_raw'] == 'Yes').sum()
pct_no_cs_307 = (n_no_cs_307 / n_ap_307) * 100

print(f"=== STUDY 2: AP COMPUTER SCIENCE CONCEALMENT (N={n_ap_307}) ===")
print(f"Schools reporting NO AP Computer Science: {n_no_cs_307} ({pct_no_cs_307:.2f}%)")
print(f"Schools reporting YES AP Computer Science: {n_yes_cs_307} ({n_yes_cs_307 / n_ap_307 * 100:.2f}%)")

# Sensitivity check on 317
ap_schools_317 = df_317[df_317['ap_participating']].copy()
n_ap_317 = len(ap_schools_317)
n_no_cs_317 = (ap_schools_317['ap_cs_indicator_raw'] == 'No').sum()
pct_no_cs_317 = (n_no_cs_317 / n_ap_317) * 100

print(f"\\nSensitivity (317 Sample, N_AP={n_ap_317}):")
print(f"Schools reporting NO AP CS: {n_no_cs_317} ({pct_no_cs_317:.2f}%)")
print(f"Difference: {pct_no_cs_317 - pct_no_cs_307:+.2f} percentage points")
"""))

cells.append(nbf.v4.new_markdown_cell("""### Visualization: Figure 2
The curricular concealment breakdown among AP-participating schools:
"""))

cells.append(nbf.v4.new_code_cell("""display.Image(filename=str(ARTIFACTS_DIR / "fig2_ap_cs_concealment.png"), width=750)
"""))

cells.append(nbf.v4.new_markdown_cell("""### Scholarly Interpretation & Epistemic Boundaries
- **Claim Supported**: Among Missouri public high schools actively participating in the AP program, **65.5%** report zero students enrolled in AP Computer Science. An umbrella AP label conceals that nearly two-thirds of AP schools offer no advanced computer science pathway.
- **Boundaries**: This does not measure teacher supply constraints, student interest, or whether introductory non-AP computing is offered. It specifically bounds the epistemic loss of using aggregate program indicators.
"""))

# ==============================================================================
# 7. Study 3: The Denominator Wedge (Physics Provision)
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 6. Study 3: The Denominator Wedge (Schools vs. Students in Physics Provision)

### Motivation
A central measurement vulnerability in education policy is the confusion between **institutional availability** (school-weighted) and **student exposure** (enrollment-weighted). Headlining that *"a third of schools lack physics"* suggests a vastly different crisis than discovering *"less than a fifth of students attend a school without physics"*.

### Narrow Question
> **Does the percentage of schools reporting zero physics classes differ from the percentage of students attending those schools?**

### Statistical Path & Calculation
1. **School-Level Unweighted Percentage ($P_{\\text{school}}$)**:
   $$P_{\\text{school}} = \\frac{1}{N} \\sum_{i=1}^N \\mathbf{1}(\\text{Physics}_i = 0)$$
2. **Student-Level Enrollment-Weighted Percentage ($P_{\\text{student}}$)**:
   $$P_{\\text{student}} = \\frac{\\sum_{i=1}^N \\text{Enrollment}_i \\cdot \\mathbf{1}(\\text{Physics}_i = 0)}{\\sum_{i=1}^N \\text{Enrollment}_i}$$
3. **Denominator Wedge**:
   $$\\Delta = P_{\\text{school}} - P_{\\text{student}}$$
"""))

cells.append(nbf.v4.new_code_cell("""# 1. School-level percentage
zero_phys_307 = df_307['physics_classes'] == 0
n_zero_schools_307 = zero_phys_307.sum()
school_pct_307 = (n_zero_schools_307 / len(df_307)) * 100

# 2. Student-level percentage
total_enr_307 = df_307['crdc_total_enrollment'].sum()
zero_enr_307 = df_307.loc[zero_phys_307, 'crdc_total_enrollment'].sum()
student_pct_307 = (zero_enr_307 / total_enr_307) * 100

wedge_307 = school_pct_307 - student_pct_307

print("=== STUDY 3: DENOMINATOR WEDGE (BASELINE 307) ===")
print(f"Total High Schools: {len(df_307)}")
print(f"Schools reporting 0 Physics classes: {n_zero_schools_307} ({school_pct_307:.2f}%)")
print(f"Total High School Students: {total_enr_307:,.0f}")
print(f"Students attending Zero-Physics schools: {zero_enr_307:,.0f} ({student_pct_307:.2f}%)")
print(f"Denominator Wedge: {wedge_307:.2f} percentage points")

# Enrollment scale decomposition
mean_enr_zero = df_307.loc[zero_phys_307, 'crdc_total_enrollment'].mean()
mean_enr_has = df_307.loc[~zero_phys_307, 'crdc_total_enrollment'].mean()
med_enr_zero = df_307.loc[zero_phys_307, 'crdc_total_enrollment'].median()
med_enr_has = df_307.loc[~zero_phys_307, 'crdc_total_enrollment'].median()

print(f"\\nInstitutional Scale Decomposition:")
print(f"Zero-Physics Schools: Mean enrollment = {mean_enr_zero:.1f}, Median = {med_enr_zero:.0f}")
print(f"Physics-Offering Schools: Mean enrollment = {mean_enr_has:.1f}, Median = {med_enr_has:.0f}")
"""))

cells.append(nbf.v4.new_markdown_cell("""### Sensitivity Check: Broad Sample (N=317)
"""))

cells.append(nbf.v4.new_code_cell("""zero_phys_317 = df_317['physics_classes'] == 0
school_pct_317 = zero_phys_317.mean() * 100

total_enr_317 = df_317['crdc_total_enrollment'].sum()
zero_enr_317 = df_317.loc[zero_phys_317, 'crdc_total_enrollment'].sum()
student_pct_317 = (zero_enr_317 / total_enr_317) * 100
wedge_317 = school_pct_317 - student_pct_317

print("=== STUDY 3: SENSITIVITY COMPARISON ===")
print(f"Baseline Wedge: {wedge_307:.2f} pp (32.90% school vs. 18.02% student)")
print(f"Sensitivity Wedge: {wedge_317:.2f} pp (33.12% school vs. 17.67% student)")
print(f"Difference: {wedge_317 - wedge_307:+.2f} percentage points")
"""))

cells.append(nbf.v4.new_markdown_cell("""### Visualization: Figure 3
The denominator wedge and institutional scale distribution:
"""))

cells.append(nbf.v4.new_code_cell("""display.Image(filename=str(ARTIFACTS_DIR / "fig3_physics_denominator_wedge.png"), width=900)
"""))

cells.append(nbf.v4.new_markdown_cell("""### Scholarly Interpretation & Epistemic Boundaries
- **Claim Supported**: The choice of denominator generates a **14.9 percentage-point wedge**. In Missouri, 32.9% of regular high schools report zero physics classes, but those schools enroll only 18.0% of the state's secondary student body. Zero-physics schools are systematically smaller (mean enrollment 403 vs. 899).
- **Boundaries**: This does not prove that large schools provide superior instruction, nor that students in physics-offering schools actually enroll in physics. It establishes that institutional counts systematically overstate the proportion of students who lack access to specialized teachers.
"""))

# ==============================================================================
# 8. Synthesis & Methodological Scorecard
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 7. Synthesis & Scorecard of Findings

### Master Findings Scorecard

| Study | Core Question | Baseline (N=307) | Sensitivity (N=317) | Delta | Substantive Conclusion |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Study 1 (Pilot)** | Dual Enrollment rate among schools reporting No AP | **92.9%** (105 / 113) | **93.1%** (108 / 116) | +0.18 pp | AP-only opportunity metrics miss 93% of non-AP schools that offer college-level pathways through dual credit. |
| **Study 2** | Curricular concealment: No AP Computer Science among AP schools | **65.5%** (127 / 194) | **64.2%** (129 / 201) | -1.28 pp | An umbrella "AP" label conceals that nearly two-thirds of AP high schools offer zero AP Computer Science. |
| **Study 3** | Denominator wedge: Schools vs. Students reporting Zero Physics | **14.88 pp** (32.9% school vs 18.0% student) | **15.46 pp** (33.1% school vs 17.7% student) | +0.58 pp | Institutional counts overstate student-level absence by ~15 pp because zero-physics schools are small rural/community schools. |

---

## 8. Epistemic Verdict & Agenda for Future Inquiries

By adhering to the **Six-Point Admission Gate**, we answered three concrete measurement questions with zero regression scaffolding, zero target leakage, and zero reliance on unverifiable causal claims.

Each study stands independently:
1. **Pilot Complete**: The AP / Dual Enrollment question is fully resolved for Missouri SY 2021–22.
2. **Next Natural Extension (Study 1B)**: Move from binary participation indicators to **participation rates** (percentage of 11th and 12th graders enrolled).
3. **Subject Breadth Extension (Study 1C)**: Examine the specific subject taxonomy of dual credit offerings relative to state university general education cores.

Together, these bounded studies construct an evidence-first foundation for understanding how educational opportunity is truly distributed and measured.
"""))

nb.cells = cells

# Save unexecuted notebook
with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Generated notebook structure at: {NOTEBOOK_PATH}")

# Execute notebook to render outputs
print("Executing notebook with jupyter nbconvert...")
cmd = [
    "jupyter", "nbconvert", "--to", "notebook", "--execute",
    str(NOTEBOOK_PATH), "--output", "01_measuring_educational_opportunity.ipynb",
    "--output-dir", str(NOTEBOOK_PATH.parent)
]
subprocess.run(cmd, check=True)
print("Notebook executed successfully with all tables and figures pre-rendered!")
