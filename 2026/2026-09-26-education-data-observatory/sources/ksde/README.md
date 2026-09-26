# Source Dossier: Kansas State Department of Education (KSDE)

> **Observatory Standard:** In the Education Data Observatory, data sources have dossiers, measures have dossiers, and analyses consume measures. An analysis never "owns" raw data.
>
> *Principle: Preserve raw source provenance. A raw download is an immutable artifact.*

---

## 1. Identity & Provenance Metadata

| Attribute | Specification |
| :--- | :--- |
| **Source ID** | `ksde` |
| **Official Dataset Name** | KSDE Data Central, Comparative Performance & Fiscal System (CPFS), and Licensed Personnel Reports (KPTEN) |
| **Governing Agency** | Kansas State Department of Education (KSDE), Division of Fiscal & Administrative Services |
| **Product / Sub-Collection** | Audited September 20 Headcount & FTE Reports, Licensed Personnel Reports, School Finance Budget Files |
| **Status** | `active` |
| **First Release Year** | 2000–01 |
| **Latest Release Year** | 2024–25 |

---

## 2. Authoritative Links & Reference Documentation

- **Authoritative Landing Page:** [https://datacentral.ksde.org/](https://datacentral.ksde.org/)
- **Direct Documentation / Finance Reports:** [https://www.ksde.org/Agency/Fiscal-and-Administrative-Services/School-Finance/Reports-and-Publications](https://www.ksde.org/Agency/Fiscal-and-Administrative-Services/School-Finance/Reports-and-Publications)
- **Data Portal:** KSDE Data Central Reports Warehouse ([https://datacentral.ksde.org/cpfs.aspx](https://datacentral.ksde.org/cpfs.aspx))
- **Citation Recommendation:** Kansas State Department of Education. (Year). *Comparative Performance & Fiscal System (CPFS) and Licensed Personnel Data*. Topeka, KS: KSDE School Finance.

---

## 3. Collection Methodology & Legal Authority

### 3.1 Statutory Authority & Collection Mandate
Mandated under the Kansas Statutes Annotated (K.S.A. 72-5131 et seq., the Kansas School Equity and Enhancement Act [KSEEA]). K.S.A. 72-5132 establishes statutory guidelines for determining school district state foundation aid based on audited enrollment.

### 3.2 Collection Methodology & Respondent
- **Collection Type:** Audited Administrative Census and Statutory Compliance Filing.
- **Respondent Entity:** Unified School District (USD) superintendents, district business managers, and licensed personnel administrators.
- **Collection Instrument:** Kansas Individual Data on Students (KIDS) and Licensed Personnel Report (LPR/KPTEN) web applications.
- **Reference Date / Snapshot:** 
  - **September 20:** Statutory snapshot date for state aid enrollment audit (or the first following school day if September 20 falls on a weekend).
  - **October 1:** Federal snapshot date for EDFacts and CCD submissions.

---

## 4. Release Cadence & Revision Policy

### 4.1 Publication Schedule & Release Lag
- **Cadence:** Annual.
- **Typical Publication Lag:** 4 to 6 months post-school year for audited finance and certified personnel reports.

### 4.2 Revision Policy & File Staging
- Preliminary fall counts are audited by KSDE field auditors during the winter and finalized in the spring prior to conclusive state foundation aid reconciliation.

---

## 5. Scope & Coverage Boundaries

| Dimension | Scope |
| :--- | :--- |
| **Geographic Coverage** | Statewide (all 286 Unified School Districts in Kansas; 21 public USDs in the 9-county KC metro area). |
| **Entity Types Covered** | Unified School Districts (USDs), interlocals, service centers, and public school attendance centers. |
| **Grade Levels Covered** | Pre-Kindergarten through Grade 12. |
| **Historical Continuity** | Annual audited series continuous from 2000–01 to present. |

---

## 6. Access Methods & Ingestion Pipeline

### 6.1 Access Mechanism
Direct download from KSDE Data Central reports warehouse, public school finance Excel releases, and formal records requests under the Kansas Open Records Act (KORA, K.S.A. 45-215 et seq.).

### 6.2 Raw Artifact Storage & Checksumming
- **Raw Path:** `data/raw/ksde/<academic-year>/`
- Tracked in [`../../data/upstream_artifacts.csv`](../../data/upstream_artifacts.csv).

---

## 7. Privacy, Suppression & Missing Value Rules

### 7.1 Suppression Rules (FERPA / Small Cells)
Student demographic cells $<10$ are suppressed in public reporting to maintain student confidentiality.

---

## 8. Known Longitudinal Traps & Historical Anomalies

1. **The 2015–16 Federal Non-Reporting Repair:** In SY 2015–16, the federal NCES CCD failed to capture teacher counts for Olathe USD 233 (`2010140`) and Gardner Edgerton USD 231 (`2006420`), creating an artificial $-2,311$ regional teacher drop. Audited KSDE Licensed Personnel Reports confirm the actual certified teacher stocks ($1,940.3$ FTE in Olathe and $370.8$ FTE in Gardner Edgerton), enabling the Observatory to repair this federal data break.
2. **Centralized / Itinerant Instructional Staff:** In Kansas USDs, central district rosters carry substantial itinerant teaching personnel (special education itinerants, traveling art/music/PE specialists, curriculum coaches) who are not assigned to individual school building codes. Across the 21 Kansas regional districts, LEA Total Reported teacher FTE exceeds the campus sum by $+455.26$ FTE (+4.32%).
3. **Headcount vs. FTE Enrollment:** Kansas state foundation aid uses audited FTE student counts (where half-day kindergarten students historically counted as $0.5$ FTE), which is lower than the full headcount reported to federal CCD.

---

## 9. Downstream Measures

| Measure ID | Measure Name | Observation Level | Primary Fields Ingested |
| :--- | :--- | :--- | :--- |
| `EDU-001` | Pupil/Teacher Ratio | School / LEA | Building membership, licensed teacher FTE |
| `EDU-002` | Student Enrollment | School / LEA | Audited September 20 headcount, building enrollment |
| `EDU-003` | Reported Classroom Teacher FTE | School / LEA | KPTEN certified classroom teacher FTE |
