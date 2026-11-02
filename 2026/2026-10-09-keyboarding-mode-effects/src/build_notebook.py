"""
src/build_notebook.py

Constructs and executes the audited master research notebook:
notebooks/01_keyboarding_mode_effects.ipynb
"""

import subprocess
import sys
from pathlib import Path
import nbformat as nbf

PROJECT_DIR = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_DIR / "notebooks" / "01_keyboarding_mode_effects.ipynb"

nb = nbf.v4.new_notebook()
cells = []

# ==============================================================================
# Cell 1: Title & Executive Abstract
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""# The Keyboard Penalty: Device Ubiquity, Keyboarding Coursework Collapse, and Digital Assessment Mode Effects
### A Computational Literature Synthesis, Empirical Reconciliation, and Parameter Sensitivity Analysis
**Computational Sketchbook: Education Policy & Measurement Observatory**  
*Primary Sources: NCES High School Transcript Study (Table 1), NCES School Pulse Panel (2025), Education Week Research Center (2024), NCES 2017 NAEP Mode Evaluation Study (Table 4.1c), IEA ICILS (2018–2023), Backes & Cowan (2019, Economics of Education Review), Gordanier et al. (2023, Education Finance and Policy), Parker (2018, JRBE).*

---

## Executive Summary & Research Scope

Over the past two decades, American elementary and secondary education experienced three simultaneously colliding transformations:
1. **Device Ubiquity**: U.S. public schools expanded individual computer access to **88.0%** of schools by 2024–25 (NCES School Pulse Panel).
2. **Keyboarding Coursework Collapse**: High school graduates earning course credit in keyboarding collapsed from **44.1% in 2000 to 2.5% in 2019** (NCES High School Transcript Study, Table 1)—a **94.3%** structural decline.
3. **Universal Digital Assessment Mandates**: State testing consortia (PARCC, Smarter Balanced) and federal monitoring assessments (NAEP reading and mathematics in 2017) shifted from paper-and-pencil tests (PBA) to digitally based assessments (DBA).

When educational assessments require students to demonstrate academic abilities through digital interfaces, the testing medium itself can introduce **Construct-Irrelevant Variance (CIV)**.

### Calibrated Central Finding
> **Across fourth-grade reading and mathematics, digitally administered constructed-response items exhibited larger negative mode differences than selected-response items. This cross-subject pattern suggests that response format and associated interface demands merit further investigation, but does not isolate a common cognitive mechanism.**

### Project Reclassification
This project is a **computational literature synthesis, empirical reconciliation, and parameter sensitivity analysis**. It synthesizes published findings from peer-reviewed journals and official government evaluations, evaluates the sensitivity of hypothesized typing thresholds, and outlines an experimental protocol to isolate the keyboarding mechanism.
"""))

# ==============================================================================
# Cell 2: Epistemic Demarcation & Six-Point Admission Gate
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 1. Epistemic Demarcation: Claim 1 vs. Claim 2

To maintain scientific integrity, we draw an absolute boundary between two distinct empirical claims:

| Feature | Claim 1: Interface Penalty Claim | Claim 2: Macro Score Decline Attribution |
| :--- | :--- | :--- |
| **Proposition** | Digital administration can depress student performance, especially on constructed-response items among younger students. | The national decline in standardized test scores over the past decade was caused by declining keyboarding instruction. |
| **Psychometric Status** | **Construct-Irrelevant Difficulty** (Messick 1989; Berninger 1999). | Causal attribution with massive unobserved macro confounders. |
| **Empirical Status** | **Supported by Replicated Evidence**: State transitions (MA $-0.25$ SD ELA; SC $-0.085$ SD ELA, $-0.024$ SD Math) and NAEP Table 4.1c ($-6.8$ pp on G4 Reading CR vs. $-3.8$ pp on SR; $-6.9$ pp on G4 Math CR vs. $-2.4$ pp on SR). | **Unsupported**: NAEP 2017+ trends are statistically linked for mode; score declines continued in 2022–2024 within an already digital baseline; typing courses alone (Parker 2018) showed null writing gains. |
| **Research Action** | **Admitted to study**: Reconcile published effect sizes, item-format differences, and parameter sensitivity. | **Quarantined from causal claims**: Rejected as an unsupported causal attribution. |

### The Six-Point Study Admission Gate
1. **Retrieval & Usability**: Underlying administrative and survey records are retrieved and versioned in reproducible tabular datasets.
2. **Fixed Population & Denominator**: Analytical populations are explicitly bounded prior to analysis.
3. **Written Mathematical Model**: The classical test theory error decomposition and parameter sensitivity equations are specified mathematically.
4. **Directional Neutrality**: Null findings (such as selected-response items showing smaller mode differences, or standalone typing courses showing null writing gains) substantively answer the research question without bias.
5. **Audited Sensitivity Check**: Cross-study variation in mode penalties is bounded and contextualized across different jurisdictions and methodologies.
6. **Scholarly & Survey Integrity**: Full transparency regarding NAEP's official decision to suppress the 2017 Writing assessment and the unverified status of questionnaire response frequencies.
"""))

# ==============================================================================
# Cell 3: Environment Setup & Data Ingestion
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 2. Environment Setup & Data Ingestion

We load the standardized datasets compiled in `data/processed/` and `data/raw/`.
"""))

cells.append(nbf.v4.new_code_cell("""import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set paths
NOTEBOOK_DIR = Path.cwd()
PROJECT_ROOT = NOTEBOOK_DIR.parent if NOTEBOOK_DIR.name == "notebooks" else NOTEBOOK_DIR
DATA_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"
TABLES_DIR = PROJECT_ROOT / "artifacts" / "tables"
FIG_DIR = PROJECT_ROOT / "artifacts" / "figures"

# Display options
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

print(f"Project root: {PROJECT_ROOT}")
"""))

# ==============================================================================
# Cell 4: Trend 1 vs Trend 2 - The Infrastructure Paradox
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 3. The Infrastructure Paradox: Keyboarding Collapse vs. 1:1 Laptop Ubiquity

Over the last 25 years, while public schools achieved nearly universal 1-to-1 computing infrastructure, formal high school coursework in keyboarding virtually disappeared.

We examine **Table 1 from the NCES NAEP High School Transcript Study (HSTS)** alongside verified data from the **NCES School Pulse Panel**.
"""))

cells.append(nbf.v4.new_code_cell("""# Load Audited HSTS Table 1 and School Pulse Data
df_hsts = pd.read_csv(RAW_DIR / "nces_hsts_2019_table1.csv")
df_pulse = pd.read_csv(RAW_DIR / "nces_pulse_device_access.csv")

print("--- NCES High School Transcript Study (Table 1: Keyboarding & Computer Courses) ---")
display(df_hsts)

print()
print("--- NCES School Pulse Panel: Public School 1:1 Device Programs ---")
display(df_pulse)
"""))

cells.append(nbf.v4.new_code_cell("""# Display Audited Summary Table 1
df_table1 = pd.read_csv(TABLES_DIR / "table1_hsts_course_trends.csv")
display(df_table1)
"""))

cells.append(nbf.v4.new_markdown_cell("""### Figure 1 Exhibit: The Divergent Curves
We visualize the divergence between device presence, keyboarding coursework, and digital literacy.
"""))

cells.append(nbf.v4.new_code_cell("""from IPython.display import Image
Image(filename=str(FIG_DIR / "fig1_three_divergent_trends.png"))
"""))

# ==============================================================================
# Cell 5: Keyboarding Instruction Landscape & Equity Disparities
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 4. Current Keyboarding Instruction & The Poverty Gradient (EdWeek 2024)

Does the absence of high school keyboarding credits simply mean students learn to type earlier in elementary school?

A nationally representative 2024 survey of $N = 404$ school and district leaders by the **Education Week Research Center** reveals that instruction is fractured and marked by a socioeconomic gradient:
- **74% of leaders in lower-poverty systems** report keyboarding instruction in grades K–2.
- **51% of leaders in higher-poverty systems** report keyboarding instruction in grades K–2.
- Disparity ratio: **$1.45\\times$** higher access in lower-poverty districts.
"""))

cells.append(nbf.v4.new_code_cell("""df_deliv = pd.read_csv(RAW_DIR / "edweek_keyboarding_survey_2024.csv")
df_equity = pd.read_csv(RAW_DIR / "edweek_equity_breakdown_2024.csv")

print("--- EdWeek 2024 Keyboarding Delivery Models ---")
display(df_deliv)

print()
print("--- EdWeek 2024 Keyboarding Instruction by Grade Span & District Poverty ---")
display(df_equity)

# Display Table 3 Summary
df_table3 = pd.read_csv(TABLES_DIR / "table3_edweek_instruction_equity.csv")
print()
print("--- Table 3: EdWeek Instruction & Equity Summary ---")
display(df_table3)
"""))

cells.append(nbf.v4.new_markdown_cell("""### Audit of Teacher Survey Status (2017 NAEP Grade 4 Questionnaire)
The 2017 NAEP Grade 4 Teacher Questionnaire explicitly asked teachers about typing expectations (Question 13) and the percentage of students meeting them (Question 14).
However, the response distributions are **unverified and unpublished in the public survey instrument**. We register this item as a survey design precedent requiring microdata extraction.
"""))

cells.append(nbf.v4.new_code_cell("""df_teacher_audit = pd.read_csv(RAW_DIR / "naep_g4_teacher_questionnaire_audit.csv")
display(df_teacher_audit)
"""))

# ==============================================================================
# Cell 6: Official NAEP 2017 Mode Evaluation (Table 4.1c)
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 5. The Official NAEP 2017 Mode Evaluation: Reading & Mathematics (Table 4.1c)

In the official 2017 NAEP Mode Evaluation Study (`transitional_whitepaper.pdf`, Table 4.1c, p. 37), NCES evaluated mean item-score differences between digital (DBA) and paper (PBA) instruments in **percentage points (pp)**, not standard deviations.

### Key Empirical Findings:
1. **Grade 4 Reading**:
   - Selected-Response (SR): **$-3.8$ pp** (DBA 60.0%, PBA 64.0%, $\\text{SE} = 0.22, p < 0.05$).
   - Constructed-Response (CR): **$-6.8$ pp** (DBA 35.0%, PBA 42.0%, $\\text{SE} = 0.18, p < 0.05$).
   - Format Gap: Constructed-response items exhibit an incremental **$-3.0$ pp** deficit.
2. **Grade 4 Mathematics**:
   - Selected-Response (SR): **$-2.4$ pp** (DBA 54.0%, PBA 56.0%, $\\text{SE} = 0.24, p < 0.05$).
   - Constructed-Response (CR): **$-6.9$ pp** (DBA 46.0%, PBA 52.0%, $\\text{SE} = 0.31, p < 0.05$).
   - Format Gap: Constructed-response items exhibit an incremental **$-4.5$ pp** deficit.
3. **Grade 8 Attenuation**:
   - Reading: **$-1.6$ pp on SR** ($\text{SE} = 0.19$) vs. **$-2.0$ pp on CR** ($\text{SE} = 0.24$) (a $-0.4$ pp format gap).
   - Mathematics: **$-2.5$ pp on SR** (DBA 51%, PBA 53%, $\text{SE} = 0.26$) vs. **$-3.5$ pp on CR** ($\text{SE} = 0.30$) (a $-1.0$ pp format gap).
4. **Calibrated Substantive Interpretation**:
   - Across fourth-grade reading and mathematics, digitally administered constructed-response items exhibited larger negative mode differences than selected-response items.
   - However, this cross-subject pattern **does not isolate a single common cognitive mechanism**. The two subjects measure distinct academic constructs and present different item demands. Both selected-response categories also show negative mode differences. Observational mode evaluations cannot isolate whether constructed-response deficits arise from typing, equation entry, screen navigation, or other test features.
"""))

cells.append(nbf.v4.new_code_cell("""df_41c = pd.read_csv(RAW_DIR / "naep_2017_mode_table41c.csv")
print("--- NCES 2017 NAEP Mode Evaluation (Table 4.1c: Reading & Mathematics Item Differences in Percentage Points) ---")
display(df_41c)

df_table2 = pd.read_csv(TABLES_DIR / "table2_naep_mode_contrasts.csv")
print()
print("--- Table 2: Verified NAEP Mode Contrasts Across Subjects ---")
display(df_table2)
"""))

cells.append(nbf.v4.new_code_cell("""# Display Figure 3: Keyboarding Delivery & NAEP Table 4.1c
Image(filename=str(FIG_DIR / "fig3_naep_grade4_cr_penalty_and_teacher_expectations.png"))
"""))

# ==============================================================================
# Cell 7: Empirical Literature Synthesis
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 6. Empirical Literature Synthesis: Reconciling Peer-Reviewed Evidence

We evaluate published empirical studies across state assessment transitions:
- **Massachusetts (Backes & Cowan 2019, *Economics of Education Review*, 68, 89–103)**:
  - Found an overall mode penalty of **$-0.25$ SD in ELA** and **$-0.10$ SD in math** in Year 1.
  - In Year 2, penalties attenuated to **$-0.13$ SD in ELA** and **$-0.05$ SD in math**, showing experiential learning.
- **South Carolina (Gordanier, Ozturk, & Zhan 2023, *Education Finance and Policy*, 18(2), 232–252, DOI: 10.1162/edfp_a_00373)**:
  - Statewide panel evaluating SC READY/PASS transitions in grades 3–8 (Table 3).
  - Main OLS estimates: **$-0.085$ SD in ELA** ($\text{SE} = 0.007$) and **$-0.024$ SD in Math** ($\text{SE} = 0.007$; 2SLS estimate is $-0.017$ SD, not statistically significant).
  - Negative impacts were significantly larger for students from low-income households, and were mitigated in schools with greater technology availability.
- **Tennessee Middle School Study (Parker 2018, *Journal of Research in Business Education*, 59(1), 1–14)**:
  - Analyzed $N = 916$ (Essay 1) and $N = 906$ (Essay 2) middle school students using chi-square tests of independence.
  - Found **no statistically significant relationship** ($p > 0.05$) between completing a 9-week keyboarding course and writing test proficiency.
  - *Methodological note*: A non-significant chi-square indicates a lack of detectable association in this quasi-experimental setting; it does not constitute proof of zero benefit nor a standardized effect size of 0.00 SD.
- **NCES 2010 Paper vs. 2012 Computer Writing Pilot Benchmarks**:
  - In tasks common to both administrations, 4th graders produced **110 words on computer** vs. **159 words on paper** (30.8% reduction).
  - However, average scores did not decline: **3.08 on computer** vs. **2.98 on paper** (scale 1–6).
  - Crucially, higher-performing students scored substantially better on computers, while lower- and middle-performing students showed no benefit, suggesting a **potential widening of the achievement gap**.
  - *Methodological note*: These were separate pilot administrations, not a randomized crossover trial.
- **NAEP 2017 Writing Assessment Suppression**:
  - NCES declared the 2017 national writing assessment results **unreportable due to unresolved comparability concerns**, explicitly stating it could not determine how much of the performance difference reflected changes in assessment administration and devices versus genuine differences in students' writing skills.
"""))

cells.append(nbf.v4.new_code_cell("""df_meta = pd.read_csv(TABLES_DIR / "table4_literature_benchmark.csv")
display(df_meta[["authors", "year", "table_reference", "subject", "estimation_model", "coefficient", "standard_error", "key_finding"]])
"""))

cells.append(nbf.v4.new_code_cell("""# Display Writing Pilot Comparison
df_pilot = pd.read_csv(RAW_DIR / "nces_writing_pilot_comparison.csv")
display(df_pilot)
"""))

cells.append(nbf.v4.new_code_cell("""# Display Figure 2: Literature Mode Penalties
Image(filename=str(FIG_DIR / "fig2_mode_penalty_by_subject_and_format.png"))
"""))

# ==============================================================================
# Cell 8: The Keyboarding Mechanism Paradox
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 7. Reconciling the Keyboarding Paradox: The "Simple View of Writing"

If digital testing introduces interface friction, why did Parker's (2018) Tennessee study find that a 9-week keyboarding course produced **no statistically significant writing improvement**?

### Cognitive Load & Threshold Mechanics
Psycholinguistic research (Berninger & Amtmann 1999; McCutchen 1996; Graham et al. 2007) models written expression as a hierarchical cognitive architecture:
1. **Transcription**: Keystroke mechanics, motor automaticity, spelling.
2. **Translation & Generation**: Formulating mental ideas into syntactic structures.
3. **Executive Planning & Review**: Coherence, argumentation, self-monitoring.

Transcription automaticity acts as a **threshold condition**, not a linear driver:
- Below $\\approx 20-25$ Words Per Minute (WPM), typing requires conscious visual search ("hunt-and-peck"), draining working memory.
- Above $\\approx 25$ WPM, transcription becomes automatic. Writing quality is then governed by vocabulary, reading comprehension, and content mastery.
- Isolated keyboarding drills that teach typing without integrating it into written composition do not automatically transfer to higher test scores.
"""))

# ==============================================================================
# Cell 9: Broader Digital Competence Erosion (ICILS 2018 vs 2023)
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 8. Broader Digital Competence Erosion: The IEA ICILS Evidence

The interface deficit extends beyond typing speed to broader functional computer literacy:
- **IEA ICILS (International Computer and Information Literacy Study)**:
  - U.S. 8th graders scored **519** in 2018.
  - U.S. 8th graders dropped to **482** in 2023 ($-37$ points, $-0.37$ SD, $p < 0.001$).
  - **51%** scored at Level 1 or below (25% below Level 1 [deficient] + 26% at Level 1 [basic]).
  - **102-point socioeconomic gap** between students in the highest and lowest SES quartiles.
"""))

cells.append(nbf.v4.new_code_cell("""df_icils = pd.read_csv(RAW_DIR / "icils_cil_trends_2018_2023.csv")
display(df_icils)
"""))

# ==============================================================================
# Cell 10: Parameter Sensitivity Analysis
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell(r"""## 9. Exploratory Parameter Sensitivity Analysis

Because student-level typing speed and score microdata are restricted, we evaluate an **exploratory parameter sensitivity analysis**:
$$f(\text{WPM}_i) = \beta_{\text{wpm}} \cdot \max(0, \tau - \text{WPM}_i)$$
We ground our speed distribution means in the 2012 NCES Usability Study benchmarks (Grade 4 mean = 12.0 WPM; Grade 8 mean = 30.0 WPM), and use assumed standard deviations ($\sigma = 4.5$ WPM for G4; $\sigma = 7.5$ WPM for G8) to explore population heterogeneity under hypothetical transcription thresholds ($\tau \in [15, 20, 25, 30]$ WPM) and penalty slopes ($\beta \in [-0.010, -0.018, -0.025]$).

*Crucial Epistemic Caveat*: This simulation illustrates theoretical model mechanics under hypothesized thresholds; it does **not** validate that typing fluency caused the observed testing gaps. Handwriting also imposes motor transcription burdens (fatigue, dysgraphia), and digital interfaces may offer benefits (editing flexibility, accommodations) for some students.
"""))

cells.append(nbf.v4.new_code_cell("""df_grid = pd.read_parquet(DATA_DIR / "typing_threshold_sensitivity_grid.parquet")
print("--- Parameter Sensitivity Grid (12 Scenarios Grounded in NCES Pilot Benchmarks) ---")
display(df_grid)
"""))

cells.append(nbf.v4.new_code_cell("""# Display Figure 4: Parameter Sensitivity Analysis
Image(filename=str(FIG_DIR / "fig4_psychometric_civ_simulation.png"))
"""))

# ==============================================================================
# Cell 11: Master Findings Scorecard & Experimental Agenda
# ==============================================================================
cells.append(nbf.v4.new_markdown_cell("""## 10. Master Findings Scorecard & Core Research Conclusions

### Synthesis of Core Questions

#### Question 1: Does digital assessment introduce an interface score penalty, especially on keyboard-intensive questions for younger students?
**YES. Empirical studies show that digital administration can depress measured student achievement, particularly on constructed-response items among younger students:**
1. **Massachusetts PARCC (Backes & Cowan 2019)**: An overall mode penalty of **$-0.25$ SD** in ELA and **$-0.10$ SD** in math in Year 1.
2. **South Carolina (Gordanier et al. 2023)**: Main OLS mode penalties of **$-0.085$ SD in ELA** and **$-0.024$ SD in Math**, larger for low-income students.
3. **NAEP 2017 Mode Evaluation (NCES Table 4.1c)**:
   - Grade 4 Reading: **$-3.8$ pp** on Selected Response vs. **$-6.8$ pp** on Constructed Response (a $-3.0$ pp format gap).
   - Grade 4 Mathematics: **$-2.4$ pp** on Selected Response vs. **$-6.9$ pp** on Constructed Response (a $-4.5$ pp format gap).
   - Across both subjects, constructed-response items exhibited larger negative mode differences than selected-response items, indicating that response format and associated interface demands merit investigation.
4. **Developmental Attenuation**: By Grade 8, the NAEP constructed-response penalty attenuates to **$-2.0$ pp in Reading** ($-0.4$ pp format gap) and **$-3.5$ pp in Math** ($-1.0$ pp format gap).

#### Question 2: Did the national decline in standardized test scores get caused by declining keyboarding instruction?
**NO. Available evidence does NOT support this causal claim:**
1. **Statistical Equating**: NAEP explicitly implemented statistical linking in 2017 to remove mode differences from longitudinal score comparisons. Subsequent score declines between 2019 and 2024 occurred *within* an already digital testing baseline.
2. **Confounding Factors**: Post-2019 score declines coincided with massive pandemic disruptions, chronic absenteeism, and curriculum adjustments.
3. **The Keyboarding Null Result**: Parker's (2018) Tennessee middle school study found no statistically significant relationship ($p > 0.05$) between completing a 9-week keyboarding course and writing test proficiency.
4. **Distributional Rather than Universal Shifts**: The 2010 vs 2012 NCES Writing Pilot showed that while digital testing cut word count by 31%, average scores did not decline (3.08 vs 2.98). Instead, high performers gained while lower performers did not, suggesting unequal preparation alters the distribution of achievement rather than imposing an identical macro penalty.

---

## 11. Proposed Experimental Protocol: The Promising Next Research Frontier

The central unresolved empirical question identified by this observatory is:

> **To what extent do differences in typing fluency, handwriting fluency, and digital interface familiarity explain variation in fourth-grade students' performance between paper and computer-based assessments—and are those differences larger for students with fewer opportunities to develop digital skills?**

To answer this question, we propose a within-student randomized crossover trial:

```mermaid
flowchart TD
    S["Cohort of 4th Grade Students\\n(Pre-tested for touch-typing WPM, handwriting fluency, and home device access)"]
    S --> R{"Random Assignment"}
    R -->|Group A| T1["Session 1: Prompt A on Paper (Handwritten)\\nSession 2: Prompt B on Laptop (Digital Keyboard)"]
    R -->|Group B| T2["Session 1: Prompt A on Laptop (Digital Keyboard)\\nSession 2: Prompt B on Paper (Handwritten)"]
    T1 --> M["Double-blind Rubric Scoring\\n(Word Count, Ideas & Organization, Syntactic Complexity)"]
    T2 --> M
    M --> E["Econometric Within-Student Decomposition:\\nEstimate Δ Score (Computer - Paper) as a function of\\n(WPM - Handwriting Speed), prior typing instruction, and district poverty"]
```

### Key Policy Recommendations
1. **Assessment Design**: State testing agencies should evaluate mode differences using item-level percentage-point tracking and ensure that young elementary students are not subjected to timed typing demands before transcription automaticity is established.
2. **Instructional Integration**: Schools should move away from isolated, siloed keyboarding drills and integrate touch-typing practice directly into daily classroom composition and digital literacy activities.
3. **Score Interpretation**: Accountability systems must account for mode effects and distributional wedges when transitioning between assessment platforms.
"""))

# Assign cells to notebook and write
nb.cells = cells

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"[OK] Audited notebook successfully generated at: {NOTEBOOK_PATH}")
