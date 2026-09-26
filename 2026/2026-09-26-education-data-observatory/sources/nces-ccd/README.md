# Source Dossier: National Center for Education Statistics — Common Core of Data (CCD)

> **Observatory Standard:** In the Education Data Observatory, data sources have dossiers, measures have dossiers, and analyses consume measures. An analysis never "owns" raw data.
>
> *Principle: Preserve raw source provenance. A raw download is an immutable artifact.*

---

## 1. Identity & Provenance Metadata

| Attribute | Specification |
| :--- | :--- |
| **Source ID** | `nces-ccd` |
| **Official Dataset Name** | Common Core of Data (CCD) Non-Fiscal Public Elementary/Secondary School and LEA Universe Surveys |
| **Governing Agency** | National Center for Education Statistics (NCES), Institute of Education Sciences (IES), U.S. Department of Education |
| **Product / Sub-Collection** | Directory Survey, School Universe Survey, Local Education Agency (LEA) Universe Survey, State Nonfiscal Public Survey |
| **Status** | `active` |
| **First Release Year** | 1986–87 |
| **Latest Release Year** | 2024–25 (Provisional) |

---

## 2. Authoritative Links & Reference Documentation

- **Authoritative Landing Page:** [https://nces.ed.gov/ccd/](https://nces.ed.gov/ccd/)
- **Direct Documentation / Codebook URL:** [https://nces.ed.gov/ccd/doc/nonfiscal/](https://nces.ed.gov/ccd/doc/nonfiscal/)
- **API Endpoint / Data Tool:** Urban Institute Education Data Portal API ([https://educationdata.urban.org/](https://educationdata.urban.org/)) & NCES Elementary/Secondary Information System (ElSi).
- **Citation Recommendation:** National Center for Education Statistics. (Year). *Common Core of Data (CCD): Public Elementary/Secondary School and Local Education Agency Universe Surveys*. U.S. Department of Education. Washington, D.C.: Institute of Education Sciences.

---

## 3. Collection Methodology & Legal Authority

### 3.1 Statutory Authority & Collection Mandate
Collected under the authority of the Education Sciences Reform Act of 2002 (ESRA 2002, 20 U.S.C. 9543), which mandates that the National Center for Education Statistics collect, collate, analyze, and report complete statistics on the condition and progress of education in the United States.

### 3.2 Collection Methodology & Respondent
- **Collection Type:** Administrative Census.
- **Respondent Entity:** State Education Agency (SEA) data coordinators and state longitudinal data system (SLDS) administrators, who compile and validate submissions from local school districts.
- **Collection Instrument:** EDFacts reporting system (governed by the EDFacts Data Governance System), transmitting standardized federal file specifications (e.g., FS029 Directory, FS052 Membership, FS059 Staff).
- **Reference Date / Snapshot:** **October 1** of each academic year (or the closest operating school day within the first two weeks of October).

---

## 4. Release Cadence & Revision Policy

### 4.1 Publication Schedule & Release Lag
- **Cadence:** Annual.
- **Typical Publication Lag:** 12 to 18 months post-snapshot for Provisional releases; 24 to 30 months for Final releases.

### 4.2 Revision Policy & File Staging
- `Preliminary`: Unedited early-release state aggregates; subject to non-reporting and uncorrected errors.
- `Provisional`: Microdata files released following standard NCES edit checks, partner-state verification cycles, and basic imputation of select non-response items.
- `Final`: Fully edited, longitudinal-harmonized data files with comprehensive imputation documentation.

---

## 5. Scope & Coverage Boundaries

| Dimension | Scope |
| :--- | :--- |
| **Geographic Coverage** | National (50 states, District of Columbia, Puerto Rico, Bureau of Indian Education, and outlying territories). |
| **Entity Types Covered** | Operating regular public school districts, independent charter LEAs, regional supervisory unions, county educational service agencies, state-operated specialized agencies, and individual operating campus facilities. |
| **Grade Levels Covered** | Pre-Kindergarten (PK), Kindergarten (KG), Grades 1 through 12, Ungraded (UG), and Adult/Continuing Education. |
| **Historical Continuity** | Annual continuous series since 1986–87; modern LEAID and NCESSCH 12-digit coding system standardized since the late 1990s. |

---

## 6. Access Methods & Ingestion Pipeline

### 6.1 Access Mechanism
Acquired via direct bulk HTTP downloads from NCES data directories or programmatically queried through the Urban Institute Education Data Portal REST API.

### 6.2 Raw Artifact Storage & Checksumming
- **Raw Path:** `data/raw/nces-ccd/<academic-year>/`
- **Integrity Rule:** Raw source files are immutable. Checksums and source URLs are tracked in [`../../data/upstream_artifacts.csv`](../../data/upstream_artifacts.csv).

### 6.3 File Formats & Technical Encodings
- **Format:** Comma-Separated Values (`CSV`) and fixed-width flat files (`DAT`).
- **Text Encoding:** `UTF-8` (modern releases) / `ASCII` / `CP-1252` (historical files).
- **Header Quirks:** Historical files used capitalized 8-character field names (e.g., `MEMBER`, `TEACH`), while modern EDFacts/Urban Institute pipelines standardize to lowercase snake_case (e.g., `enrollment`, `teachers_fte`).

---

## 7. Privacy, Suppression & Missing Value Rules

### 7.1 Suppression Rules (FERPA / Small Cells)
In standard public non-fiscal universe files, aggregate membership and total FTEs are unsuppressed. Demographic or grade-level sub-cells with counts between 1 and 4 are subject to state-specific primary suppression in select reporting years.

### 7.2 Native Missing & Exception Codes
| Source Code | Official Definition | Pipeline Handling Rule |
| :--- | :--- | :--- |
| `-1` or `M` | Missing / Not reported | Map to `NaN`; record data quality flag |
| `-2` or `N` | Not applicable (entity does not offer grade/role) | Map to `0.0` or structural `NaN` depending on measure definition |
| `-9` or `S` | Suppressed for student privacy | Map to `NaN`; flag privacy suppression |
| `0` | Zero count confirmed | Preserve as `0.0` (differentiate from missing) |

---

## 8. Known Longitudinal Traps & Historical Anomalies

1. **The 2015–16 Kansas Staff Non-Reporting Break:** In the SY 2015–16 federal CCD LEA and School Non-Fiscal files, Kansas failed to submit teacher counts for major districts including Olathe USD 233 (`2010140`) and Gardner Edgerton USD 231 (`2006420`), causing an artificial regional undercount of $-2,311$ FTE. Pipeline interpolation via continuous KSDE records is required.
2. **Variable Renaming (`TOTENR` $\to$ `MEMBER`):** In SY 2014–15, NCES transitioned core variable names, moving total school enrollment from `TOTENR` to `MEMBER`.
3. **Zero-Membership Operating Schools:** Legitimate operating public schools (particularly technical/vocational centers and specialized shared-time programs) report $0$ official October 1 membership because students are enrolled and counted primarily at their home comprehensive campus.
4. **Campus-Sum vs. LEA Membership Gap:** Across the Kansas City 9-county metropolitan area, LEA-reported enrollment exceeds the sum of campus enrollment by $+1,472$ students across regular districts (primarily Pre-K and centralized special education programs) plus $+973$ students in non-traditional regional/statewide LEAs.
5. **Support Staff Historical Unavailability:** Non-teaching staff roles (e.g., `psychologists_fte`, `school_admin_support_fte`) were unpopulated in older CCD files (2014–15/2015–16) and `student_support_staff_fte` was zeroed out between 2016–17 and 2018–19. Longitudinal analysis of support staff must avoid naive aggregation across inconsistent categories.

---

## 9. Downstream Measures

| Measure ID | Measure Name | Observation Level | Primary Fields Ingested |
| :--- | :--- | :--- | :--- |
| `EDU-001` | Pupil/Teacher Ratio (PTR) | School / LEA | `enrollment`, `teachers_fte` |
| `EDU-002` | Student Enrollment (Headcount) | School / LEA | `enrollment`, `grade_level` |
| `EDU-003` | Reported Classroom Teacher FTE | School / LEA | `teachers_fte` |
| `EDU-005` | Paraprofessional / Aide FTE | LEA | `paraprofessionals_fte` |
| `EDU-006` | School Administrator FTE | LEA / School | `school_administrators_fte`, `lea_administrators_fte` |
