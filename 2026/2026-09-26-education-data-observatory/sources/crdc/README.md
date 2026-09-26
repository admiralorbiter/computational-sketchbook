# Source Dossier: U.S. Department of Education — Civil Rights Data Collection (CRDC)

> **Observatory Standard:** In the Education Data Observatory, data sources have dossiers, measures have dossiers, and analyses consume measures. An analysis never "owns" raw data.
>
> *Principle: Preserve raw source provenance. A raw download is an immutable artifact.*

---

## 1. Identity & Provenance Metadata

| Attribute | Specification |
| :--- | :--- |
| **Source ID** | `crdc` |
| **Official Dataset Name** | Civil Rights Data Collection (CRDC) School and District Survey Files |
| **Governing Agency** | Office for Civil Rights (OCR), U.S. Department of Education |
| **Product / Sub-Collection** | School-Level Course Offerings, Section Counts, Student Course Enrollment, and Advanced Placement Files |
| **Status** | `active` |
| **First Release Year** | 1968 (Sample survey); 2011–12 (Universal Census) |
| **Latest Release Year** | 2023–24 (Released 2025–26) |

---

## 2. Authoritative Links & Reference Documentation

- **Authoritative Landing Page:** [https://ocrdata.ed.gov/](https://ocrdata.ed.gov/)
- **Direct Documentation / Codebook URL:** [https://www2.ed.gov/about/offices/list/ocr/data.html](https://www2.ed.gov/about/offices/list/ocr/data.html)
- **Data Download Hub:** [https://civilrightsdata.ed.gov/data](https://civilrightsdata.ed.gov/data)
- **Citation Recommendation:** U.S. Department of Education, Office for Civil Rights. (Year). *Civil Rights Data Collection (CRDC)*. Washington, D.C.: Office for Civil Rights.

---

## 3. Collection Methodology & Legal Authority

### 3.1 Statutory Authority & Collection Mandate
Collected under the legal authority of:
- Title VI of the Civil Rights Act of 1964 (prohibiting discrimination on the basis of race, color, and national origin);
- Title IX of the Education Amendments of 1972 (prohibiting discrimination on the basis of sex);
- Section 504 of the Rehabilitation Act of 1973 (prohibiting discrimination on the basis of disability);
- Department of Education Organization Act (20 U.S.C. 3413(c)(1)), which authorizes OCR to collect data necessary to ensure compliance with civil rights laws.

### 3.2 Collection Methodology & Respondent
- **Collection Type:** Mandatory Compliance Census of all public school districts, charter schools, juvenile justice facilities, and alternative education campuses.
- **Respondent Entity:** Local Education Agency (LEA) compliance coordinators, central district data managers, and high school master scheduling administrators.
- **Collection Instrument:** CRDC Data Submission System (electronic portal ingesting bulk CSV extracts from local student information systems [SIS]).
- **Reference Date / Snapshot:** Course enrollment snapshot counts typically referenced as of the district's official fall reporting date or winter scheduling census.

---

## 4. Release Cadence & Revision Policy

### 4.1 Publication Schedule & Release Lag
- **Cadence:** Historically Biennial (every two years).
- **Typical Publication Lag:** 18 to 24 months post-collection.

### 4.2 Revision Policy & File Staging
- OCR releases provisional school and district files followed by final public-use data files. Public-use files include privacy perturbation in small demographic cells.

---

## 5. Scope & Coverage Boundaries

| Dimension | Scope |
| :--- | :--- |
| **Geographic Coverage** | National (all 50 states, DC, and Puerto Rico). |
| **Entity Types Covered** | Public elementary and secondary schools, public charter schools, vocational/technical schools, and alternative programs. |
| **Grade Levels Covered** | Pre-K through Grade 12 (with secondary course offerings specific to Grades 7–12 and 9–12). |
| **Historical Continuity** | Universal biennial census starting 2011–12 (2011–12, 2013–14, 2015–16, 2017–18). The 2019–20 wave was postponed due to COVID-19, followed by back-to-back collections in 2020–21, 2021–22, and 2023–24. |

---

## 6. Access Methods & Ingestion Pipeline

### 6.1 Access Mechanism
Direct bulk HTTP download of zipped CSV datasets from the OCR Civil Rights Data portal.

### 6.2 Raw Artifact Storage & Checksumming
- **Raw Path:** `data/raw/crdc/<academic-year>/`
- Checksums and download timestamps logged in [`../../data/upstream_artifacts.csv`](../../data/upstream_artifacts.csv).

### 6.3 File Formats & Technical Encodings
- **Format:** Comma-Separated Values (`CSV`).
- **Text Encoding:** `UTF-8` or `Windows-1252`.
- **Header Quirks:** Column names utilize OCR-specific prefixes that change across waves (e.g., `SCH_MATHCLASSES_CALC`, `SCH_MATHENR_CALC_M`, `SCH_MATHENR_CALC_F`).

---

## 7. Privacy, Suppression & Missing Value Rules

### 7.1 Suppression Rules (FERPA / Small Cells)
CRDC public data files apply small-cell protection. When demographic cell counts are between 1 and 4, counts may be top-coded, bottom-coded, or perturbed. Course section counts and total course enrollment counts are generally preserved as exact integers.

### 7.2 Native Missing & Exception Codes
| Source Code | Official Definition | Pipeline Handling Rule |
| :--- | :--- | :--- |
| `-9` | Data not reported / Missing | Map to `NaN`; flag reporting non-compliance |
| `-5` | Not applicable (school does not offer course/grade) | Map to `0` or structural `NaN` |
| `-7` | Data not certified | Map to `NaN`; review district certification status |

---

## 8. Known Longitudinal Traps & Historical Anomalies

1. **Course Class Size is NOT Collected Directly:** CRDC does not collect student section rosters or direct classroom headcount. Derived class size must be operationalized as:
   $$\text{Derived Class Size (EDU-012)} = \frac{\text{Course Student Enrollment (EDU-011)}}{\text{Course Section Count (EDU-007)}}$$
2. **Pandemic Scheduling Disruption:** The 2019–20 collection was cancelled due to nationwide school closures. The subsequent 2020–21 wave was collected during peak hybrid/remote instruction, creating anomalous section counts and enrollment structures.
3. **Singleton Course Sections:** In small high schools (<800 enrollment), courses such as Calculus or Physics are frequently offered as a single section ($\text{EDU-007} = 1$). A change from 1 section to 0 sections represents complete cancellation of the curriculum.

---

## 9. Downstream Measures

| Measure ID | Measure Name | Observation Level | Primary Fields Ingested |
| :--- | :--- | :--- | :--- |
| `EDU-007` | Course Section Count | School / Course | `SCH_MATHCLASSES_CALC`, `SCH_SCICLASSES_PHYS`, etc. |
| `EDU-011` | Course Student Enrollment | School / Course | `SCH_MATHENR_CALC_TOT`, `SCH_SCIENR_PHYS_TOT`, etc. |
| `EDU-012` | Derived School-Course Mean Class Size | School / Course | Ratio of `EDU-011` to `EDU-007` |
| `EDU-013` | Advanced Course Availability (Indicator) | School / Course | Boolean indicator ($\text{EDU-007} > 0$) |
| `EDU-014` | Advanced STEM Pipeline Participation Rate | School / Course | Ratio of `EDU-011` to Grade 11–12 enrollment |
