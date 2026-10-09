# The Keyboard Penalty: Device Ubiquity, Keyboarding Coursework Collapse, and Digital Assessment Mode Effects (`2026-10-09-keyboarding-mode-effects`)

A computational literature synthesis, empirical reconciliation, and parameter sensitivity analysis examining assessment mode effects, keyboarding coursework trends, and construct-irrelevant variance across standardized testing.

---

## 1. Project Overview & Calibrated Finding

Over the past two decades, primary and secondary education in the United States underwent three simultaneous transformations:
1. **Device Ubiquity**: U.S. public schools expanded individual computer access to **88.0%** of schools by 2024–25 (NCES School Pulse Panel).
2. **Keyboarding Coursework Collapse**: The proportion of high school graduates earning course credit in keyboarding collapsed from **44.1% in 2000 to 2.5% in 2019** (NCES High School Transcript Study, Table 1)—a **94.3%** structural decline.
3. **Universal Digital Assessment Mandates**: State testing consortia (PARCC, Smarter Balanced) and federal monitoring assessments (NAEP reading and mathematics in 2017) transitioned from paper-and-pencil assessments (PBA) to digitally based assessments (DBA).

### Calibrated Central Finding
> **Digital administration can affect measured student performance, and the differences appear particularly pronounced on constructed-response items among younger students. The degree to which typing fluency explains those differences remains unresolved.**

### Project Scope Demarcation
- **Nature of the Work**: A **computational literature synthesis, empirical reconciliation, and parameter sensitivity analysis**. It synthesizes published findings from peer-reviewed journals and official government evaluations, evaluates the sensitivity of hypothesized typing thresholds, and outlines an experimental protocol to isolate the keyboarding mechanism.
- **Boundary**: This project is **not** a student-level microdata replication or a formal meta-regression. It does not claim that keyboarding declines caused national test-score trends.

---

## 2. Epistemic Demarcation: Claim 1 vs. Claim 2

```mermaid
flowchart TD
    subgraph Claim1["Claim 1: The Interface Penalty Claim (EMPIRICALLY SUPPORTED)"]
        C1["Digital test administration can depress student performance,\nespecially on constructed-response items among younger students."]
        E1["Empirical Evidence:\n• Backes & Cowan (2019, EER): -0.25 SD in ELA, -0.10 SD in Math\n• Gordanier et al. (2023, EFP): Significant negative CBT penalty, larger for poor students\n• NAEP 2017 Table 4.1c: -3.8 pp on SR vs. -6.8 pp on CR in G4 Reading\n• 2017 NAEP Writing: Results suppressed due to typing speed & device disparity"]
        C1 --> E1
    end

    subgraph Claim2["Claim 2: The Macro Score Decline Claim (UNSUPPORTED)"]
        C2["The national decline in standardized test scores over the past decade\nwas caused by declining keyboarding instruction."]
        E2["Empirical Contradictions:\n• NAEP 2017+ trends are statistically linked/equated for mode\n• Declines deepened post-2020 within an already-digital testing baseline\n• Keyboarding coursework alone (Parker 2018) did not boost computerized writing"]
        C2 --> E2
    end
```

### The Six-Point Study Admission Gate
1. **Retrieval & Usability**: Primary records from NCES HSTS Table 1, NCES School Pulse Panel, EdWeek 2024, ICILS 2018/2023, and NAEP 2017 Table 4.1c are retrieved and audited in reproducible tabular datasets.
2. **Fixed Population & Denominator**: Analytical populations are explicitly bounded prior to analysis.
3. **Written Mathematical Model**: The classical test theory error decomposition ($X = T + E_{\text{interface}} + \epsilon$) is explicitly specified.
4. **Directional Neutrality**: Null findings (such as selected-response items showing smaller mode differences, or standalone typing courses showing null writing gains) substantively answer the research question without bias.
5. **Audited Sensitivity Check**: Cross-study variation in mode penalties is bounded and contextualized across different jurisdictions and methodologies.
6. **Scholarly & Survey Integrity**: Full transparency regarding NAEP's official decision to suppress the 2017 Writing assessment and the unverified status of questionnaire response frequencies.

---

## 3. Audited Findings Scorecard

| Research Domain | Specific Question | Empirical Estimate | Primary Source Citation | Verification Status | Substantive Conclusion |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **High School Keyboarding** | Did high school keyboarding credits decline? | **44.1% $\to$ 2.5%**<br>($-94.3\%$ relative) | NCES HSTS 2019, Table 1 | **Verified Primary Table** | Dedicated high school typing coursework has collapsed. |
| **Computer Applications** | Did software applications replace typing? | **3.1% (2000) $\to$ 31.4% (2009) $\to$ 10.4% (2019)** | NCES HSTS 2019, Table 1 | **Verified Primary Table** | Peaked in 2009, then receded as applications shifted to earlier grades. |
| **Device Access** | Did school computing device access expand? | **88.0% (2024–25)**<br>(83.0% in 2021–22) | NCES School Pulse Panel (2021–2025) | **Verified Primary Report** | Near-universal 1:1 student device penetration achieved in public schools. |
| **Digital Literacy** | Did student digital competence improve? | **519 $\to$ 482 pts**<br>($-37$ pts, $-0.37$ SD) | IEA / NCES ICILS (2018–2023) | **Verified Primary Report** | Touchscreen ubiquity did not produce functional computer problem-solving skills. |
| **State Mode Penalty** | How large was the initial online penalty? | **$-0.25$ SD (ELA)**<br>**$-0.10$ SD (Math)** | Backes & Cowan (2019, *EER*) | **Verified Peer-Reviewed** | Substantial initial penalty in Year 1; attenuated to $-0.13$ SD and $-0.05$ SD in Year 2. |
| **South Carolina Transition** | Did mode penalties affect students equitably? | **Statistically Significant Negative** | Gordanier et al. (2023, *EFP*) | **Verified Peer-Reviewed** | Negative CBT impact was significantly larger for students from poor households. |
| **NAEP G4 Format Gap** | Does question format drive the penalty? | **$-3.8$ pp (SR)** vs.<br>**$-6.8$ pp (CR)** | NCES 2017 Mode Evaluation, Table 4.1c | **Verified Primary Table** | Both item types show negative differences; CR is $-3.0$ pp larger. Keyboarding is one plausible factor among several. |
| **NAEP Age Attenuation** | Does age attenuate the penalty? | **$-1.6$ pp (SR)** vs.<br>**$-2.0$ pp (CR)** | NCES 2017 Mode Evaluation, Table 4.1c | **Verified Primary Table** | Mode differences attenuate at Grade 8, leaving a narrow $-0.4$ pp format gap. |
| **Early Instruction Equity** | Do low-income systems teach typing early? | **74% (Low-Poverty)** vs.<br>**51% (High-Poverty)** | EdWeek Research Center (2024) | **Verified Primary Survey** | Lower-poverty systems are $1.45\times$ more likely to report K–2 keyboarding instruction. |
| **Keyboarding Intervention** | Does a typing course raise test scores? | **Chi-Square $p > 0.05$**<br>(Null Association) | Parker (2018, *JRBE*, $N=916/906$) | **Verified Peer-Reviewed** | 9-week standalone typing class showed no statistically significant relationship with writing scores. |
| **NAEP Writing 2017** | Was the federal digital writing test valid? | **UNREPORTABLE / SUPPRESSED** | NAGB / NCES Technical Summary | **Verified Administrative Fact** | Suppressed due to severe typing speed, response length (30-40% drop), and device incomparability. |

---

## 4. Key Visual Exhibits

### Figure 1: The Infrastructure Paradox (2000–2025)
*Contrasts the collapse in keyboarding credits (44.1% to 2.5%) against universal 1:1 device penetration (88%) and declining ICILS digital literacy (519 to 482).*  
![Figure 1](artifacts/figures/fig1_three_divergent_trends.png)

### Figure 2: Empirical Mode Penalties from Published Studies
*Synthesizes effect sizes across Backes & Cowan (2019, Economics of Education Review), Gordanier et al. (2023, Education Finance and Policy), and Parker (2018, JRBE).*  
![Figure 2](artifacts/figures/fig2_mode_penalty_by_subject_and_format.png)

### Figure 3: Keyboarding Delivery (EdWeek 74% vs 51%) & NAEP Table 4.1c Item Differences
*Visualizes delivery models (EdWeek 2024), the 1.45x K–2 poverty gap, and the official NAEP Table 4.1c item differences in percentage points ($-3.8$ pp SR vs. $-6.8$ pp CR at Grade 4).*  
![Figure 3](artifacts/figures/fig3_naep_grade4_cr_penalty_and_teacher_expectations.png)

### Figure 4: Parameter Sensitivity Analysis
*Explores how simulated score penalties vary across hypothetical transcription thresholds ($\tau \in [15, 20, 25, 30]$ WPM) and penalty slopes, acknowledging handwriting transcription burdens.*  
![Figure 4](artifacts/figures/fig4_psychometric_civ_simulation.png)

---

## 5. Directory Architecture

```text
2026-10-09-keyboarding-mode-effects/
├── README.md                           # Master investigation overview & scorecard
├── docs/
│   ├── research_design.md              # Theoretical model, 6-point gate, hypotheses
│   ├── literature_synthesis.md         # Audited synthesis of mode effects & typing literature
│   └── data_provenance.md              # Primary source registry, citations, and table references
├── data/
│   ├── raw/
│   │   ├── nces_hsts_2019_table1.csv   # Audited HSTS 2000-2019 coursework credits
│   │   ├── nces_pulse_device_access.csv # School Pulse 1:1 device penetration & survey context
│   │   ├── edweek_keyboarding_survey_2024.csv # EdWeek 2024 delivery models (N=404)
│   │   ├── edweek_equity_breakdown_2024.csv   # Audited EdWeek 2024 K-2 poverty gradient (74% vs 51%)
│   │   ├── naep_2017_mode_table41c.csv # Official NAEP Mode Evaluation Table 4.1c (in pp)
│   │   ├── mode_effects_literature_meta.csv   # Audited empirical literature panel
│   │   ├── icils_cil_trends_2018_2023.csv     # IEA ICILS 8th grade scores & SES gap
│   │   └── naep_g4_teacher_questionnaire_audit.csv # Teacher questionnaire audit status
│   └── processed/
│       ├── typing_threshold_sensitivity_grid.parquet
│       ├── typing_threshold_sensitivity_grid.csv
│       ├── master_mode_effects_benchmark.csv
│       └── keyboarding_longitudinal_panel.csv
├── src/
│   ├── acquire_datasets.py             # Audited data acquisition and validation
│   ├── analyze_mode_effects.py         # Statistical analysis, Table 4.1c contrasts, sensitivity
│   ├── generate_figures.py             # Publication-quality multi-panel visualization suite
│   └── build_notebook.py               # Generates and executes the research notebook
├── notebooks/
│   └── 01_keyboarding_mode_effects.ipynb # Fully executed, interactive 2.4MB research notebook
├── tests/
│   └── test_data_integrity.py          # Pytest verification suite (6 passing tests)
└── artifacts/
    ├── figures/
    │   ├── fig1_three_divergent_trends.png
    │   ├── fig2_mode_penalty_by_subject_and_format.png
    │   ├── fig3_naep_grade4_cr_penalty_and_teacher_expectations.png
    │   └── fig4_psychometric_civ_simulation.png
    └── tables/
        ├── table1_hsts_course_trends.csv
        ├── table2_naep_mode_contrasts.csv
        ├── table3_edweek_instruction_equity.csv
        └── table4_literature_benchmark.csv
```

---

## 6. How to Reproduce

All data pipelines, test suites, figures, and executed notebooks can be fully reproduced using Python 3.12:

```bash
# 1. Acquire and audit raw datasets
python src/acquire_datasets.py

# 2. Run automated verification test suite
pytest tests/test_data_integrity.py -v

# 3. Perform statistical analysis and generate summary tables
python src/analyze_mode_effects.py

# 4. Generate audited publication figures
python src/generate_figures.py

# 5. Build and execute the Jupyter notebook
python src/build_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebooks/01_keyboarding_mode_effects.ipynb
```
