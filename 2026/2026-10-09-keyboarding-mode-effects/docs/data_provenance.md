# Data Provenance & Primary Source Registry (`2026-10-09-keyboarding-mode-effects`)

This document provides complete provenance, extraction citations, and table references for all empirical datasets utilized in the Keyboarding & Digital Assessment Mode Effects Observatory.

---

## 1. Primary Source Registry

| Source ID | Institution / Source | Collection Year(s) | Table / Publication Reference | Access Status | File Path in Repository |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `SRC-01` | NCES NAEP High School Transcript Study (HSTS) | 2000, 2005, 2009, 2019 | [HSTS 2019 Tables, Table 1](https://nces.ed.gov/nationsreportcard/hsts/2019_tables/2019_table1.aspx) | Public Excel/HTML | `data/raw/nces_hsts_2019_table1.csv` |
| `SRC-02` | NCES School Pulse Panel | 2024–2025 | NCES School Pulse Panel Technology Report (2025) | Public NCES Report | `data/raw/nces_pulse_device_access.csv` |
| `SRC-03` | Education Week Research Center | November 2024 | Survey of 404 School and District Leaders | Public Report & Articles | `data/raw/edweek_keyboarding_survey_2024.csv`, `data/raw/edweek_equity_breakdown_2024.csv` |
| `SRC-04` | Empirical Mode Effects Meta-Analytic Benchmark | 2015–2020 | Backes & Cowan (2019, JPAM); Egalite & Rapp (2020, Fordham); NCES (2017 DBA Whitepaper) | Public Peer-Reviewed / Reports | `data/raw/mode_effects_literature_meta.csv` |
| `SRC-05` | IEA / NCES ICILS Assessment | 2018, 2023 | International Computer and Information Literacy Study, U.S. National Report | Public Microdata & Summary Tables | `data/raw/icils_cil_trends_2018_2023.csv` |
| `SRC-06` | NAEP Grade 4 Teacher Questionnaire | 2017 | NAEP 2017 Grade 4 Background Questionnaire (SQ Teacher G4) | Public Survey Instrument & Items | `data/raw/naep_g4_teacher_keyboarding_2017.csv` |

---

## 2. Granular Data Field Specifications

### `SRC-01`: NCES NAEP HSTS Table 1 (High School Graduates Coursework)
- **Metric**: Percentage of high school graduates earning credits in business/office and computer-related courses.
- **Fields**:
  - `course_title`: Keyboarding, Word Processing, Computer Applications.
  - `year`: 2000, 2005, 2009, 2019.
  - `pct_graduates`: Percentage of high school graduates who completed at least one course credit.
  - `stat_diff_from_2019`: Binary flag indicating whether the earlier year estimate is statistically significantly different from 2019 at $p < 0.05$.
- **Key Verified Value**: Keyboarding credit collapsed from $44.1\%$ in 2000 to $2.5\%$ in 2019 ($p < 0.05$).

### `SRC-02`: NCES School Pulse Panel (1:1 Student Device Programs)
- **Metric**: Percentage of public elementary and secondary schools reporting a 1-to-1 computing program (providing an individual computing device to each enrolled student).
- **Key Verified Value**: $88.0\%$ of public schools reported 1-to-1 programs in the 2024–25 school year.

### `SRC-03`: Education Week Research Center 2024 Keyboarding Survey
- **Sample**: Nationally representative survey of $N = 404$ school and district leaders conducted in late 2024.
- **Key Delivery Values**:
  - Standalone keyboarding class only: $8.0\%$.
  - Combined (standalone + integrated): $11.0\%$.
  - Integrated within regular classroom instruction: $50.0\%$.
  - No formal keyboarding instruction: $31.0\%$.
- **Key Equity Values (Grades K–2)**:
  - Lower-poverty school systems: $36.0\%$ report keyboarding instruction.
  - Higher-poverty school systems: $18.0\%$ report keyboarding instruction.
  - Equity disparity ratio: $2.0\times$ higher in low-poverty districts.

### `SRC-04`: Meta-Analytic Benchmark Studies
- **Fields**: `study_id`, `study_citation`, `jurisdiction`, `year`, `grades`, `sample_size`, `subject`, `item_format`, `device_mode`, `effect_size_sd`, `ci_lower`, `ci_upper`, `wwc_rating`.
- **Key Effect Sizes**:
  - Backes & Cowan (2019) Year 1 ELA: $-0.25$ SD (WWC with reservations).
  - Backes & Cowan (2019) Year 1 Math: $-0.10$ SD.
  - NAEP 2017 Grade 4 Reading Multiple Choice: $-0.01$ SD.
  - NAEP 2017 Grade 4 Reading Constructed Response: $-0.18$ SD.
  - Tennessee Middle School Keyboarding Study (NBEA): $+0.04$ SD ($p = 0.48$).

### `SRC-05`: IEA ICILS (U.S. Eighth-Grade Digital Literacy)
- **Scale**: Mean 500, Standard Deviation 100.
- **U.S. Score 2018**: $519$ points ($\text{SE} = 3.2$).
- **U.S. Score 2023**: $482$ points ($\text{SE} = 4.1$).
- **Statistically Significant Drop**: $-37.0$ scale score points ($-0.37$ SD, $p < 0.001$).
- **Proficiency Level**: $43.0\%$ of U.S. 8th graders scored at Level 1 or below (basic deficiency).
