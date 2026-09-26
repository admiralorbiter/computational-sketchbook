# Source Dossier: National Center for Education Statistics — National Teacher and Principal Survey (NTPS)

> **Observatory Standard:** In the Education Data Observatory, data sources have dossiers, measures have dossiers, and analyses consume measures. An analysis never "owns" raw data.
>
> *Principle: Preserve raw source provenance. A raw download is an immutable artifact.*

---

## 1. Identity & Provenance Metadata

| Attribute | Specification |
| :--- | :--- |
| **Source ID** | `ntps` |
| **Official Dataset Name** | National Teacher and Principal Survey (NTPS), formerly Schools and Staffing Survey (SASS) |
| **Governing Agency** | National Center for Education Statistics (NCES), Institute of Education Sciences (IES), U.S. Department of Education |
| **Product / Sub-Collection** | Public School Teacher Questionnaire, Principal Questionnaire, School Questionnaire |
| **Status** | `active` |
| **First Release Year** | 1987–88 (as SASS); redesigned as NTPS in 2015–16 |
| **Latest Release Year** | 2023–24 |

---

## 2. Authoritative Links & Reference Documentation

- **Authoritative Landing Page:** [https://nces.ed.gov/surveys/ntps/](https://nces.ed.gov/surveys/ntps/)
- **Direct Documentation / Methodology:** [https://nces.ed.gov/surveys/ntps/methods.asp](https://nces.ed.gov/surveys/ntps/methods.asp)
- **Data Query Tool:** NCES DataLab / PowerStats ([https://nces.ed.gov/datalab/](https://nces.ed.gov/datalab/))
- **Citation Recommendation:** National Center for Education Statistics. (Year). *National Teacher and Principal Survey (NTPS)*. U.S. Department of Education. Washington, D.C.: Institute of Education Sciences.

---

## 3. Collection Methodology & Legal Authority

### 3.1 Statutory Authority & Collection Mandate
Authorized by the Education Sciences Reform Act of 2002 (ESRA 2002, 20 U.S.C. 9543). Participation by sampled public schools, principals, and teachers is voluntary under federal law, though state and local district policies may encourage or require response.

### 3.2 Collection Methodology & Respondent
- **Collection Type:** Stratified Probability Sample Survey.
- **Respondent Entity:** Sampled individual classroom teachers, school principals, and school administrative offices.
- **Collection Instrument:** Self-administered web surveys and paper questionnaires.
- **Reference Date / Snapshot:** Mid-school year (typically administered between December and May of the survey year).

---

## 4. Release Cadence & Revision Policy

### 4.1 Publication Schedule & Release Lag
- **Cadence:** Quadrennial (every 4 years; e.g., 2015–16, 2017–18, 2020–21, 2023–24).
- **Typical Publication Lag:** 18 to 24 months post-survey completion.

### 4.2 Revision Policy & File Staging
- Public-use microdata files are subjected to statistical disclosure limitation (data perturbation, categorization of continuous variables). Full microdata requires a formal IES Restricted-Use Data License.

---

## 5. Scope & Coverage Boundaries

| Dimension | Scope |
| :--- | :--- |
| **Geographic Coverage** | National and state-representative for public elementary and secondary education. |
| **Entity Types Covered** | Sampled regular public schools, public charter schools, and private schools. |
| **Grade Levels Covered** | Kindergarten through Grade 12. |
| **Historical Continuity** | Periodic quadrennial cross-sections; SASS (1987–88 to 2011–12) transitioned to NTPS in 2015–16 with methodological redesign. |

---

## 6. Access Methods & Ingestion Pipeline

### 6.1 Access Mechanism
NCES DataLab PowerStats online query tool for aggregate tabular estimations; licensed secure transfer for restricted microdata.

### 6.2 Raw Artifact Storage & Checksumming
- **Raw Path:** `data/raw/ntps/<survey-year>/`
- Tracked in [`../../data/upstream_artifacts.csv`](../../data/upstream_artifacts.csv).

---

## 7. Privacy, Suppression & Missing Value Rules

### 7.1 Suppression Rules (FERPA / Small Cells)
NCES applies strict statistical disclosure control: cells with unweighted respondent counts $<30$ or with coefficients of variation $>50\%$ are suppressed or flagged as unstable.

---

## 8. Known Longitudinal Traps & Historical Anomalies

1. **Sample Survey, NOT a Universal Census:** NTPS cannot be linked deterministically to every Kansas City campus or LEA. It cannot be used to measure campus-level headcount or year-over-year district staffing trends.
2. **Self-Reported vs. Administrative Measures:** NTPS measures **teacher self-reported class size** (e.g., "How many students were enrolled in your first period class?"), whereas CCD measures macro pupil/teacher ratio and CRDC measures derived school-course mean class size.
3. **Epistemic Role in the Observatory:** NTPS provides empirical benchmarks on teacher daily schedules (number of instructional periods taught per day, prep/planning periods per day, and specialized coaching duties). These empirical distributions are critical for parameterizing the schedule waterfall conversion between macro PTR (`EDU-001`) and true classroom roster load (`EDU-012`).

---

## 9. Downstream Measures & Model Dependencies

| Measure ID / Model | Role in Measurement Graph | Key Parameters Extracted |
| :--- | :--- | :--- |
| `EDU-007` | Teacher-Reported Average Class Size | Survey questionnaire Table 7 benchmark distributions |
| `REL-002 (EDU-001 -> EDU-012)` | Structural empirical conversion model | Mean secondary teacher teaching fraction ($\lambda = 0.75$ to $0.80$), planning period allocations |
| `REL-003 (EDU-003 -> EDU-004)` | FTE to headcount conversion | Part-time teacher share and itinerant teacher adjustments |
