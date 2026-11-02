# Source Dossier: Missouri Department of Elementary and Secondary Education (MO DESE)

> **Observatory Standard:** In the Education Data Observatory, data sources have dossiers, measures have dossiers, and analyses consume measures. An analysis never "owns" raw data.
>
> *Principle: Preserve raw source provenance. A raw download is an immutable artifact.*

---

## 1. Identity & Provenance Metadata

| Attribute | Specification |
| :--- | :--- |
| **Source ID** | `mo-dese` |
| **Official Dataset Name** | Missouri Comprehensive Data System (MCDS) & Missouri Student Information System (MOSIS) |
| **Governing Agency** | Missouri Department of Elementary and Secondary Education (DESE), Office of Data System Management |
| **Product / Sub-Collection** | Annual School Data Portal, MOSIS Core Data (Personnel, Enrollment, Building, and Course Assignment Files) |
| **Status** | `active` |
| **First Release Year** | 1991–92 (Core Data); 2006–07 (MOSIS modern longitudinal SLDS) |
| **Latest Release Year** | 2024–25 |

---

## 2. Authoritative Links & Reference Documentation

- **Authoritative Landing Page:** [https://dese.mo.gov/](https://dese.mo.gov/)
- **Direct Documentation / Codebook URL:** [https://dese.mo.gov/data-system-management/mosis/code-sets](https://dese.mo.gov/data-system-management/mosis/code-sets)
- **Data Portal & Reporting Engine:** Missouri Comprehensive Data System (MCDS) Reports ([https://apps.dese.mo.gov/MCDS/Reports/](https://apps.dese.mo.gov/MCDS/Reports/))
- **Citation Recommendation:** Missouri Department of Elementary and Secondary Education. (Year). *Missouri Comprehensive Data System (MCDS) Administrative Records*. Jefferson City, MO: MO DESE.

---

## 3. Collection Methodology & Legal Authority

### 3.1 Statutory Authority & Collection Mandate
Mandated under the Revised Statutes of Missouri (RSMo Chapter 160, 161, and 163). In particular, RSMo § 163.021 governs eligibility for state foundation formula aid, mandating precise reporting of student enrollment, daily attendance, and certified instructional personnel.

### 3.2 Collection Methodology & Respondent
- **Collection Type:** Administrative Census and Statutory Compliance Filing.
- **Respondent Entity:** LEA Core Data / MOSIS coordinators, certified district payroll clerks, and campus registrars.
- **Collection Instrument:** MOSIS web transmission application (Cycle 1 October, Cycle 2 December, Cycle 3 February, Cycle 4 June).
- **Reference Date / Snapshot:** 
  - **October 1:** Official state and federal membership snapshot.
  - **Last Wednesday of September:** Historical state aid enrollment reference date.
  - **June 30:** Cumulative Average Daily Attendance (ADA) and certified staff service credit.

---

## 4. Release Cadence & Revision Policy

### 4.1 Publication Schedule & Release Lag
- **Cadence:** Annual (with multiple reporting cycles during the school year).
- **Typical Publication Lag:** 6 to 9 months post-school year for validated portal exports.

### 4.2 Revision Policy & File Staging
- Preliminary cycle reports are audited and reconciled against school district financial audits before final determination of foundation formula funding allocations.

---

## 5. Scope & Coverage Boundaries

| Dimension | Scope |
| :--- | :--- |
| **Geographic Coverage** | Statewide (all 114 Missouri counties plus the City of St. Louis; 56 public LEAs in the 9-county KC metro area). |
| **Entity Types Covered** | Public school districts (K–12 and K–8), independent public charter LEAs (statutorily authorized in Kansas City and St. Louis), and state-operated schools. |
| **Grade Levels Covered** | Pre-Kindergarten through Grade 12. |
| **Historical Continuity** | Modern MOSIS individual student/staff identifiers established 2006–07; aggregate district reporting continuous since 1991. |

---

## 6. Access Methods & Ingestion Pipeline

### 6.1 Access Mechanism
Direct export from MCDS Public Portal query tools, published state tabular Excel/CSV releases, and formal Missouri Sunshine Law (RSMo Chapter 610) open records requests.

### 6.2 Raw Artifact Storage & Checksumming
- **Raw Path:** `data/raw/mo-dese/<academic-year>/`
- Tracked in [`../../data/upstream_artifacts.csv`](../../data/upstream_artifacts.csv).

---

## 7. Privacy, Suppression & Missing Value Rules

### 7.1 Suppression Rules (FERPA / Small Cells)
MO DESE suppresses student counts $<5$ in public reporting to prevent disclosure of personally identifiable information.

---

## 8. Known Longitudinal Traps & Historical Anomalies

1. **Pre-K Teacher Allocation in Building Totals:** In Missouri MOSIS reporting, campus-level certified classroom teacher FTE counts include early-childhood and Pre-K teachers stationed in elementary school facilities. In the Kansas City regional audit, LEA total reported teachers ($13,806.08$ FTE across 56 Missouri LEAs) reconciled with campus sums ($13,742.85$ FTE) within $+63.23$ FTE (+0.46%), while LEA K–12 reported teachers ($13,350.66$ FTE) excluded $455.42$ FTE of Pre-K educators.
2. **Membership vs. Average Daily Attendance (ADA):** In Missouri, state foundation formula funding is allocated based on Average Daily Attendance (weighted ADA), **NOT** on October 1 student membership. Enrollment shifts do not translate into funding shifts at a 1:1 instantaneous rate due to statutory attendance weighting and three-year funding lookback provisions.
3. **Independent Charter District Coding:** Missouri charter schools operate as autonomous LEAs with separate 6-digit county-district codes (e.g., Jackson County code `048-XXX`), independent of the KCPS traditional district (`048-078`).

---

## 9. Downstream Measures

| Measure ID | Measure Name | Observation Level | Primary Fields Ingested |
| :--- | :--- | :--- | :--- |
| `EDU-001` | Pupil / Teacher Ratio | School / LEA | Building membership, building teacher FTE |
| `EDU-002` | Student Headcount Enrollment | School / LEA | October membership, September headcount |
| `EDU-003` | Reported Classroom Teacher FTE | School / LEA | Certified teacher assignment FTE |
| `EDU-013` | Individual Section Enrollment | Section | MOSIS Screen 21 Course Assignment file |
| `EDU-014` | Student-Weighted Class Size Exposure | School / Grade | Derived from section roster microdata |
| `EDU-015` | Average Daily Attendance (ADA) | LEA / School | Core Data Attendance Hours / Calendar Hours |
