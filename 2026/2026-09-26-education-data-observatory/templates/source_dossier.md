# Source Dossier Template

> **Observatory Standard:** In the Education Data Observatory, data sources have dossiers, measures have dossiers, and analyses consume measures. An analysis never "owns" raw data.
>
> *Principle: Preserve raw source provenance. A raw download is an immutable artifact.*

---

## 1. Identity & Provenance Metadata

| Attribute | Specification |
| :--- | :--- |
| **Source ID** | `lowercase-slug` (e.g., `nces-ccd`, `crdc`, `mo-dese`, `ksde`) |
| **Official Dataset Name** | Full legal / published title of the data collection |
| **Governing Agency** | Parent department, bureau, or division (e.g., NCES, US ED OCR, MO DESE) |
| **Product / Sub-Collection** | Specific survey or data product within the agency |
| **Status** | `active` \| `legacy` \| `deprecated` \| `pilot` |
| **First Release Year** | Earliest year published |
| **Latest Release Year** | Most recent public release |

---

## 2. Authoritative Links & Reference Documentation

- **Authoritative Landing Page:** [URL to agency data home]
- **Direct Documentation / Codebook URL:** [URL to data dictionary / PDF layout]
- **API Endpoint / Data Tool:** [URL if programmatically accessible]
- **Citation Recommendation:** Standard academic / public citation format for this source.

---

## 3. Collection Methodology & Legal Authority

### 3.1 Statutory Authority & Collection Mandate
*Under what legal authority is this data collected? (e.g., Every Student Succeeds Act [ESSA], Title VI Civil Rights Act of 1964, Individuals with Disabilities Education Act [IDEA], State Revised Statutes).*

### 3.2 Collection Methodology & Respondent
- **Collection Type:** `Administrative Census` \| `Sample Survey` \| `Compliance Filing` \| `Fiscal Audit`
- **Respondent Entity:** (e.g., State Education Agency [SEA] data coordinators, LEA central office administrators, campus principals).
- **Collection Instrument:** (e.g., EDFacts submission system, online web portal, bulk XML/CSV upload from State Longitudinal Data Systems [SLDS]).
- **Reference Date / Snapshot:** (e.g., "On or near October 1 of the school year", "Cumulative end-of-year spring record").

---

## 4. Release Cadence & Revision Policy

### 4.1 Publication Schedule & Release Lag
- **Cadence:** `Annual` \| `Biennial` \| `Periodic (every 4 years)` \| `Continuous`
- **Typical Publication Lag:** Time elapsed between reference date and public data file release (e.g., 12–18 months for provisional, 24 months for final).

### 4.2 Revision Policy & File Staging
*Does the agency publish multiple stages of data (e.g., Preliminary $\to$ Provisional $\to$ Final)? How are corrections handled?*
- `Preliminary / Unedited`: Initial raw dump; high risk of non-reporting.
- `Provisional`: Imputed or cleaned release with state coordinator sign-off.
- `Final`: Audited multi-year harmonized release.

---

## 5. Scope & Coverage Boundaries

| Dimension | Scope |
| :--- | :--- |
| **Geographic Coverage** | `National (50 states + DC + territories)` \| `Statewide (single state)` \| `Regional` |
| **Entity Types Covered** | Local education agencies (LEAs), regular schools, charter schools, vocational schools, state-operated schools, specialized educational facilities. |
| **Grade Levels Covered** | Pre-Kindergarten, Kindergarten through 12, Adult Education. |
| **Historical Continuity** | Continuous uninterrupted series vs. periodic waves. |

---

## 6. Access Methods & Ingestion Pipeline

### 6.1 Access Mechanism
*How does the Observatory acquire this source?*
- [ ] Direct bulk HTTP / FTP download (automated script).
- [ ] Public REST API (e.g., Urban Institute Education Data Portal, Census API).
- [ ] Interactive query export tool (manual or semi-automated download).
- [ ] Formal state records request (FOIA, Missouri Sunshine Law, Kansas Open Records Act [KORA]).

### 6.2 Raw Artifact Storage & Checksumming
*Where are immutable raw files stored, and how is cryptographic provenance maintained?*
- **Raw Path:** `data/raw/<source-id>/<year>/`
- **Integrity Rule:** Raw files are NEVER modified in place. Every downloaded file must be logged in a manifest with source URL, timestamp, file size, and SHA-256 hash.

### 6.3 File Formats & Technical Encodings
- **Format:** `CSV` \| `TSV` \| `Fixed-width ASCII` \| `Excel (.xlsx)` \| `SAS (.sas7bdat)` \| `JSON`
- **Text Encoding:** `UTF-8` \| `Windows-1252 (CP-1252)` \| `ISO-8859-1`
- **Header Quirks:** (e.g., All uppercase headers, varying column names across historical years, trailing empty columns).

---

## 7. Privacy, Suppression & Missing Value Rules

### 7.1 Suppression Rules (FERPA / Small Cells)
*How does the source protect student privacy in small cells?*
- Top-coding / Bottom-coding (e.g., CRDC reporting `<3` or `>=95%`).
- Cell suppression (e.g., suppression of enrollment when count is between 1 and 4).
- Perturbation / Data swapping (e.g., intentional noise injected into public files).

### 7.2 Native Missing & Exception Codes
| Source Code | Official Definition | Pipeline Handling Rule |
| :--- | :--- | :--- |
| `-1` | Missing | Map to `NaN`; flag data quality exception |
| `-2` | Not applicable | Map to `NaN`; record structural non-applicability |
| `-9` | Suppressed | Map to `NaN`; record suppression flag |
| `N/A` | Text missing | Map to `NaN` |

---

## 8. Known Longitudinal Traps & Historical Anomalies

*Document known historical disruptions in this source (e.g., federal reporting platform migrations, state non-reporting years, sudden changes in variable naming conventions).*

- **Case 1 (e.g., Kansas 2015–16):** Staff suppression in select large LEAs resulting in partial state undercounting.
- **Case 2 (e.g., CRDC 2019–20):** Wave skipped / altered due to the COVID-19 pandemic.
- **Case 3 (e.g., Variable Renaming):** Field `MEMBER` renamed from `TOTENR` in SY 2014–15.

---

## 9. Downstream Measures

*List of all Observatory measures derived or extracted from this source:*

| Measure ID | Measure Name | Observation Level | Primary Fields Ingested |
| :--- | :--- | :--- | :--- |
| `EDU-001` | Pupil/Teacher Ratio | School / LEA | `MEMBER`, `TEACHERS_FTE` |
| `EDU-002` | Student Enrollment | School / LEA | `MEMBER` |
| `EDU-003` | Teacher FTE (Total) | School / LEA | `TEACHERS_FTE` |
