# Data Provenance & Source Audit Registry (`2026-10-09-keyboarding-mode-effects`)

This document provides complete provenance, extraction citations, table references, and verification audits for all empirical datasets utilized in the Keyboarding & Digital Assessment Mode Effects Observatory.

---

## 1. Primary Source Audit Registry

| Source ID | Institution / Authors | Collection Year(s) | Original Publication Reference | Exact Table / Page | Metric Unit | Verification Status | Repository Location |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :--- |
| `SRC-01` | NCES High School Transcript Study (HSTS) | 2000, 2005, 2009, 2019 | [HSTS 2019 Tables](https://nces.ed.gov/nationsreportcard/hsts/2019_tables/2019_table1.aspx) | Table 1 | Percentage of graduates (%) | **Verified Primary Table** | `data/raw/nces_hsts_2019_table1.csv` |
| `SRC-02` | NCES School Pulse Panel | 2021–2025 | [NCES School Pulse Panel Technology Reports](https://ies.ed.gov/schoolpulse/) | 2024–25 Report | Percentage of public schools (%) | **Verified Primary Report** | `data/raw/nces_pulse_device_access.csv` |
| `SRC-03` | Education Week Research Center | Nov 2024 | [Education Week Keyboarding Survey](https://www.edweek.org) | Survey of $N = 404$ leaders | Percentage (%) | **Verified Primary Article** | `data/raw/edweek_keyboarding_survey_2024.csv`, `data/raw/edweek_equity_breakdown_2024.csv` |
| `SRC-04` | NCES NAEP Mode Evaluation | 2017 | [*2017 NAEP Transition to Digitally Based Assessments*](https://nces.ed.gov/nationsreportcard/subject/publications/main2020/pdf/transitional_whitepaper.pdf) | Table 4.1c | **Percentage Points (pp)** | **Verified Primary Table** | `data/raw/naep_2017_mode_table41c.csv` |
| `SRC-05` | Ben Backes & James Cowan | 2015–2016 | [*Economics of Education Review*, Vol. 68, pp. 89–103 (2019)](https://doi.org/10.1016/j.econedurev.2018.12.003) | Tables 2–4 | Standard Deviations (SD) | **Verified Peer-Reviewed** | `data/raw/mode_effects_literature_meta.csv` |
| `SRC-06` | John Gordanier, Orgul Ozturk, & Crystal Zhan | 2015–2018 | [*Education Finance and Policy*, Vol. 18(3), pp. 411–437 (2023)](https://doi.org/10.1162/edfp_a_00366) | Full Paper | Standard Deviations (SD) | **Verified Peer-Reviewed** | `data/raw/mode_effects_literature_meta.csv` |
| `SRC-07` | Carol Parker | 2018 | [*Journal of Research in Business Education*, Vol. 59(1), pp. 1–14](https://jrbe.nbea.org) | Tables 1–3 ($N = 916 / 906$) | Chi-Square Test ($p > 0.05$) | **Verified Peer-Reviewed** | `data/raw/mode_effects_literature_meta.csv` |
| `SRC-08` | IEA / NCES ICILS | 2018, 2023 | [*U.S. Results from the 2023 International Computer and Information Literacy Study*](https://nces.ed.gov/surveys/icils/) | National Summary Report | Scale Score (Mean 500, SD 100) | **Verified Primary Report** | `data/raw/icils_cil_trends_2018_2023.csv` |
| `SRC-09` | NAEP Grade 4 Teacher Questionnaire | 2017 | [2017 NAEP SQ Teacher G4](https://nces.ed.gov/nationsreportcard/subject/about/pdf/bgq/teacher/2017_sq_teacher_g4.pdf) | Questions 13 & 14 | Survey Questions | **Instrument Verified / Frequencies Unverified** | `data/raw/naep_g4_teacher_questionnaire_audit.csv` |

---

## 2. Granular Extraction Audits & Field Discrepancy Corrections

### `SRC-01`: NCES NAEP HSTS Table 1 (High School Graduates Coursework)
- **Original Source**: National Center for Education Statistics, High School Transcript Study, Table 1.
- **Population**: Nationally representative sample of high school graduates.
- **Audited Fields**:
  - *Keyboarding*: $44.1\%$ in 2000 ($\text{SE} = 1.25$), $26.6\%$ in 2005 ($\text{SE} = 1.11$), $15.0\%$ in 2009 ($\text{SE} = 0.88$), $2.5\%$ in 2019 ($\text{SE} = 0.28$). Drop from 2000 to 2019 is statistically significant ($p < 0.05$).
  - *Computer Applications*: $3.1\%$ in 2000 ($\text{SE} = 0.35$), $26.8\%$ in 2005 ($\text{SE} = 1.14$), $31.4\%$ in 2009 ($\text{SE} = 1.18$), $10.4\%$ in 2019 ($\text{SE} = 0.58$).
  - *Word Processing*: $12.8\%$ in 2000 ($\text{SE} = 0.74$), $5.0\%$ in 2005 ($\text{SE} = 0.51$), $3.8\%$ in 2009 ($\text{SE} = 0.41$), $1.2\%$ in 2019 ($\text{SE} = 0.17$).
  - *Business Computer Applications*: $6.2\%$ in 2000, $7.1\%$ in 2005, $3.4\%$ in 2009, $8.8\%$ in 2019.
- **Correction Applied**: Earlier draft mistakenly transcribed Computer Applications as starting at 18.2% and ending at 12.4%. Reconciled to exact published values: $3.1\%$ (2000) $\to$ $31.4\%$ (2009 peak) $\to$ $10.4\%$ (2019).

### `SRC-02`: NCES School Pulse Panel (1:1 Student Device Programs)
- **Original Source**: NCES School Pulse Panel, 2024–25 School Year Technology Report.
- **Methodological Scope**: The School Pulse Panel began monthly collections in 2021.
- **Audited Value**: $88.0\%$ of U.S. public schools reported having a 1-to-1 computing program for the 2024–25 school year (up from $83.0\%$ in 2021–22).
- **Correction Applied**: Removed the synthetic continuous 2013–2025 time-series line, which conflated disparate historical surveys (FRSS and Pew) with the School Pulse Panel.

### `SRC-03`: Education Week Research Center 2024 Keyboarding Survey
- **Sample**: Nationally representative survey of $N = 404$ school and district leaders conducted in late 2024.
- **Delivery Models**:
  - Standalone keyboarding class only: $8.0\%$.
  - Combined standalone and integrated: $11.0\%$.
  - Integrated within regular classroom instruction: $50.0\%$.
  - No formal keyboarding instruction: $31.0\%$.
- **Socioeconomic Breakdown in Grades K–2**:
  - Lower-poverty school systems: **$74.0\%$** report keyboarding instruction.
  - Higher-poverty school systems: **$51.0\%$** report keyboarding instruction.
  - Disparity Ratio: **$1.45\times$** ($74\% / 51\%$).
- **Correction Applied**: Corrected an earlier transcription error that erroneously recorded 36% vs. 18% (claiming a 2.0x gap). The actual published disparity is 74% vs. 51% (1.45x gap).

### `SRC-04`: NCES 2017 NAEP Mode Evaluation Study (Table 4.1c)
- **Publication**: *2017 NAEP Transition to Digitally Based Assessments in Mathematics and Reading at Grades 4 and 8: Mode Evaluation Study* (`transitional_whitepaper.pdf`), Table 4.1c.
- **Measurement Unit**: **Mean item score differences in PERCENTAGE POINTS (pp)**, NOT standard deviations!
- **Audited Values (Reading)**:
  - **Grade 4 Selected-Response (SR)**: Digital $56\%$ vs. Paper $60\%$ $\to$ Difference = **$-3.8$ pp** ($\text{SE} = 0.24, p < 0.05$).
  - **Grade 4 Constructed-Response (CR)**: Digital $33\%$ vs. Paper $40\%$ $\to$ Difference = **$-6.8$ pp** ($\text{SE} = 0.27, p < 0.05$).
  - **Grade 4 Format Gap (CR vs. SR)**: **$-3.0$ pp** (both differences are negative and statistically significant).
  - **Grade 8 Selected-Response (SR)**: Digital $74\%$ vs. Paper $76\%$ $\to$ Difference = **$-1.6$ pp** ($\text{SE} = 0.19, p < 0.05$).
  - **Grade 8 Constructed-Response (CR)**: Digital $53\%$ vs. Paper $55\%$ $\to$ Difference = **$-2.0$ pp** ($\text{SE} = 0.24, p < 0.05$).
  - **Grade 8 Format Gap (CR vs. SR)**: **$-0.4$ pp**.
- **Correction Applied**: Corrected the metric unit from standard deviations to percentage points. Acknowledged that both SR and CR items exhibited statistically significant negative mode differences in Grade 4, and that reading presentation, scrolling, interface layout, and cognitive load are plausible mechanisms alongside typing.

### `SRC-05` to `SRC-07`: Empirical Benchmark Literature
- **Backes & Cowan (2019)**: Corrected journal citation to *Economics of Education Review* (Vol. 68, pp. 89–103). Verified Year 1 PARCC mode penalty of $-0.25$ SD in ELA and $-0.10$ SD in math.
- **Gordanier, Ozturk, & Zhan (2023)**: Corrected citation to *Education Finance and Policy* (Vol. 18(3), pp. 411–437), replacing the previous placeholder. Verified significant negative CBT penalties in South Carolina, more severe for students from poor households.
- **Carol Parker (2018)**: *Journal of Research in Business Education* (Vol. 59(1), pp. 1–14). Removed fabricated effect size (+0.04 SD) and normal confidence intervals. Reconciled to the study's actual methodology: a chi-square test of independence on $N = 916$ (Essay 1) and $N = 906$ (Essay 2) middle school students, reporting no statistically significant relationship ($p > 0.05$) between completing a 9-week keyboarding course and writing test proficiency.

### `SRC-09`: NAEP Grade 4 Teacher Questionnaire Status
- **Audit Findings**: The public background questionnaire instrument (`2017_sq_teacher_g4.pdf`) confirms that teachers were asked about their typing expectations (Question 13) and the percentage of students meeting them (Question 14).
- **Correction Applied**: Removed previously fabricated response distributions (e.g. "67% of teachers report half or fewer students meet expectations"). Formally registered this item as **Instrument Verified / Response Frequencies Unverified (Awaiting Microdata Extraction)**.
