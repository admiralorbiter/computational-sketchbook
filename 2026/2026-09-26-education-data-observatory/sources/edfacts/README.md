# Source Dossier: U.S. Department of Education — EDFacts Reporting System

> **Observatory Standard:** In the Education Data Observatory, data sources have dossiers, measures have dossiers, and analyses consume measures. An analysis never "owns" raw data.
>
> *Principle: Preserve raw source provenance. A raw download is an immutable artifact.*

---

## 1. Identity & Provenance Metadata

| Attribute | Specification |
| :--- | :--- |
| **Source ID** | `edfacts` |
| **Official Dataset Name** | EDFacts Data Governance System Public Data Files |
| **Governing Agency** | U.S. Department of Education (US ED), National Center for Education Statistics (NCES) |
| **Product / Sub-Collection** | Federal EDFacts Public Reporting Files (Chronic Absenteeism, Special Education / IDEA Part B, School Assessments) |
| **Status** | `active` |
| **First Release Year** | 2004–05 (System inception); 2010–11 (Standardized public data files) |
| **Latest Release Year** | 2023–24 |

---

## 2. Authoritative Links & Reference Documentation

- **Authoritative Landing Page:** [https://www2.ed.gov/about/inits/ed/edfacts/index.html](https://www2.ed.gov/about/inits/ed/edfacts/index.html)
- **Direct Documentation / File Specifications:** [https://www2.ed.gov/about/inits/ed/edfacts/file-specifications.html](https://www2.ed.gov/about/inits/ed/edfacts/file-specifications.html)
- **Public Data Files Hub:** [https://www2.ed.gov/about/inits/ed/edfacts/data-files/index.html](https://www2.ed.gov/about/inits/ed/edfacts/data-files/index.html)
- **Citation Recommendation:** U.S. Department of Education. (Year). *EDFacts Data Files: School and Local Education Agency Public Reporting*. Washington, D.C.: U.S. Department of Education.

---

## 3. Collection Methodology & Legal Authority

### 3.1 Statutory Authority & Collection Mandate
Authorized under the Elementary and Secondary Education Act of 1965 (ESEA), as amended by the Every Student Succeeds Act (ESSA, 20 U.S.C. 6301 et seq.), and the Individuals with Disabilities Education Act (IDEA, 20 U.S.C. 1400 et seq.). State participation in EDFacts is mandatory for all state education agencies receiving federal elementary and secondary education funding.

### 3.2 Collection Methodology & Respondent
- **Collection Type:** Administrative State Reporting and Federal Compliance Census.
- **Respondent Entity:** State Education Agency (SEA) EDFacts coordinators compiling verified LEA submissions.
- **Collection Instrument:** EDFacts Submission System (ESS) using structured standardized file specifications (e.g., FS195 Chronic Absenteeism, FS002 Children with Disabilities).
- **Reference Date / Snapshot:** Cumulative school year (e.g., absenteeism) and December 1 child count snapshot (IDEA).

---

## 4. Release Cadence & Revision Policy

### 4.1 Publication Schedule & Release Lag
- **Cadence:** Annual.
- **Typical Publication Lag:** 12 to 18 months post-school year.

### 4.2 Revision Policy & File Staging
- State submissions undergo federal business rule checks and resubmission windows prior to publication of standardized public files.

---

## 5. Scope & Coverage Boundaries

| Dimension | Scope |
| :--- | :--- |
| **Geographic Coverage** | National (50 states, District of Columbia, Puerto Rico, Bureau of Indian Education). |
| **Entity Types Covered** | Operating regular public school districts, charter schools, and individual campuses. |
| **Grade Levels Covered** | Pre-K through Grade 12. |
| **Historical Continuity** | Annual continuous series for core federal accountability indicators. |

---

## 6. Access Methods & Ingestion Pipeline

### 6.1 Access Mechanism
Direct HTTP bulk download from US ED EDFacts public data file repositories or via the Urban Institute Education Data Portal.

### 6.2 Raw Artifact Storage & Checksumming
- **Raw Path:** `data/raw/edfacts/<academic-year>/`
- Tracked in [`../../data/upstream_artifacts.csv`](../../data/upstream_artifacts.csv).

---

## 7. Privacy, Suppression & Missing Value Rules

### 7.1 Suppression Rules (FERPA / Small Cells)
EDFacts public data files apply federal privacy protection algorithms: percentage ranges (e.g., `50-54%`, `GE80%`, `LE20%`) and count top/bottom-coding are utilized for small cell populations.

---

## 8. Known Longitudinal Traps & Historical Anomalies

1. **State Definition Variance in Chronic Absenteeism:** Under ESSA, each state defines chronic absenteeism in its consolidated state plan (most commonly missing $\ge 10\%$ of enrolled days, typically 15–18 days), but minimum enrollment day thresholds (e.g., enrolled for at least 10 days vs. 90 days) vary slightly across states.
2. **Pandemic Wave Gaps:** Accountability testing and absenteeism reporting requirements were federally waived for SY 2019–20 under emergency COVID-19 waivers.

---

## 9. Downstream Measures

| Measure ID | Measure Name | Observation Level | Primary Fields Ingested |
| :--- | :--- | :--- | :--- |
| `EDU-008` | Chronic Absenteeism Rate | School / LEA | `chronic_absenteeism_pct`, `enrolled_students` |
| `EDU-009` | IDEA Special Education Enrollment | School / LEA | `idea_count`, `disability_type` |
