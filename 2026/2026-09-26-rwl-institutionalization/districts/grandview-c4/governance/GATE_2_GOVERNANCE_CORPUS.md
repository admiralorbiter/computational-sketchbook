# Task 002 Gate 2 Dossier: Grandview C-4 Priority Governance Corpus

**Corpus Scope**: Five Priority Board of Education Meetings Spanning Direct-Grant to Post-Direct-Grant Governance  
**District**: Consolidated School District No. 4 (Grandview C-4), Jackson County, Missouri (DESE Code: 048-074)  
**Execution Date**: September 26, 2026  
**Branch**: `task-002-gate-2-priority-governance`  
**Methodological Scope**: Primary Corpus Acquisition, Provenance Registration, and Observable-Only Schema Mapping  

---

## 1. Executive Summary & Corpus Boundaries

Task 002 Gate 2 establishes the **complete API-accessible governance corpus for the five focal meetings** of the Grandview C-4 Board of Education, spanning the transition from direct Kauffman Foundation grant support (2019–2024, concluding December 31, 2024 per IRS Form 990-PF grant records) into the subsequent post-direct-grant observation period (January 2025 through June 2026).

```
Direct Kauffman Grant Regime                     Post-Direct-Kauffman-Grant Regime
================================== | =================================================================
2024-12-19 (MID 16764)             | 2025-01-16 (MID 16922)      2025-03-20 (MID 17411)
* RWL Program Evaluation           | * Shared Pathways Expansion * CSIP 2024-27 Review
* Policy IM Evaluation Process     | * Honeywell FM&T Address    * Seal of Biliteracy MVA
* 2024 MSIP 6 APR (127.5 / 200)    | * MVA Tracking Workflows    * FY25 Budget Amendment 2
                                   |
                                   | 2026-04-16 (MID 24913)      2026-06-18 (MID 25898)
                                   | * RWL Progress Update       * T&L Welding MOA Renewal
                                   | * Superintendent Transition * Between Me 2 You Healthcare MOU
                                   | * Foundations for Future    * FY27 Preliminary Budget Adoption
```

### Epistemic Boundaries & Access Limitations
1. **Separation of Observations and Inferences**: Field-level coding strictly differentiates primary source disclosures from derived classifications:
   - Presenters and departments are coded only when explicitly declared in the primary text; otherwise marked `unknown`.
   - Motions, seconds, and vote outcomes derive directly from official published minute structures (`LstItemMinutes`), distinguishing direct roll-call/voice votes from consent agenda omnibus approvals.
   - Heuristic flags (`career_connected_semantic`, `money_mentioned`, `staffing_mentioned`) are explicitly designated with `coding_method=rule_based_derived`.
2. **Binary Attachment Barrier**: While all 237 discoverable binary attachment references are cataloged in the artifact registry with complete metadata, the PDF/DOCX files themselves remain **unavailable behind the Simbli/Imperva Incapsula access boundary** (bot-detection hCaptcha).
3. **No Interpretive Verdicts**: In accordance with the study design, this dossier makes **no claims of institutionalization, rebranding, or decay**. It records documented administrative actions, motions, and public communications.
4. **Governing Terminology**: The observational period starting January 1, 2025 is classified as `post_direct_grant` (or `post-direct-Kauffman-grant`), **not** `post_grant`, because non-Kauffman capital streams (e.g., KCNSC / Honeywell FM&T, PREP-KC) continue to fund specific pathways.

---

## 2. Five-Meeting Coverage Matrix

The corpus covers **199 distinct agenda items**, **237 cataloged attachment references**, **5 sets of official approved minutes** obtained via the Simbli REST API, and **5 companion Edlio Board Brief summaries**.

| Meeting Date | Simbli MID | Edlio Brief ID | Governance Regime | Total Agenda Items | Attachments Linked | Minutes Status | Board Brief Status | Interim Text Path |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **2024-12-19** | `16764` | `2011053` | `direct_kauffman_grant` | 33 | 43 | Acquired via API | Acquired / Preserved | `data/interim/grandview-c4/governance/2024-12-19_mid-16764_governance_text.txt` |
| **2025-01-16** | `16922` | `2020964` | `post_direct_grant` | 38 | 39 | Acquired via API | Acquired / Preserved | `data/interim/grandview-c4/governance/2025-01-16_mid-16922_governance_text.txt` |
| **2025-03-20** | `17411` | `2053567` | `post_direct_grant` | 42 | 48 | Acquired via API | Acquired / Preserved | `data/interim/grandview-c4/governance/2025-03-20_mid-17411_governance_text.txt` |
| **2026-04-16** | `24913` | `2191177` | `post_direct_grant` | 41 | 51 | Acquired via API | Acquired / Preserved | `data/interim/grandview-c4/governance/2026-04-16_mid-24913_governance_text.txt` |
| **2026-06-18** | `25898` | `2210618` | `post_direct_grant` | 45 | 56 | Acquired via API | Acquired / Preserved | `data/interim/grandview-c4/governance/2026-06-18_mid-25898_governance_text.txt` |
| **Total** | — | — | — | **199** | **237** | **5 / 5 Acquired** | **5 / 5 Acquired** | **5 Search Text Files** |

---

## 3. Technical Platform Architecture: Simbli eBOARDsolutions

### API Access Capabilities
The Grandview C-4 Board of Education governance portal is hosted on **Simbli by eBOARDsolutions** (`SchoolID / S = 225`). Programmatic access to Simbli's REST APIs succeeded across all five meetings:
- `Services/api/GetMeeting`: Shell metadata, date, time, and site context.
- `Services/api/GetAgendaTree`: Hierarchical outline, node sequencing, and nesting levels.
- `Services/api/GetItemContents`: Administrative background text, requested recommendations, and attachment lists.
- `Services/api/GetMeetingMinutes`: Official approved minutes, attendance records, item-by-item minute texts, and formal voting structures (`MeetingOnlineVotings`).

### Document Download Barrier
Direct downloads of attached binary files (e.g., `ViewAgendaMinuteDocument.aspx?S=225&aid=...`) and on-demand packet PDF generation (`app2.eboardsolutions.com/api/PrintMeetingPacket/GenerateMeetingPacketPdf`) are protected by an **Imperva Incapsula Web Application Firewall (WAF)** that serves an interactive hCaptcha challenge.
- Because automated bypass of access controls was not performed, the binary files remain unretrieved.
- All 237 attachments are cataloged in [`priority_meeting_artifacts.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-rwl-institutionalization/districts/grandview-c4/governance/priority_meeting_artifacts.csv) with status `linked_but_unavailable`.
- The primary textual proxy for attachment content consists of the administrative narrative preserved in `agenda_items_{mid}.json` and the public executive summaries published in the Edlio Board Briefs.

---

## 4. Focal Meeting Observations & Documented Actions

### Meeting 1: December 19, 2024 (`MID 16764`) — Final Direct-Grant Month
- **RWL Governance Action**:
  - **Item G.1.c**: *Program Evaluation - Real World Learning*
  - **Agenda Recommendation**: "Approve the Real World Learning Program Evaluation as presented in Supporting Documents."
  - **Board Action**: Approved under motion by Damon Greene, seconded by Stacy Wright (`vote_result: motion_approved`).
  - **Governance Context**: Background narrative states that RWL was included in the district's standing program-evaluation process pursuant to **District Policy IM** (*Evaluation of Instructional Programs*).
  - **Underlying Attachments (Cataloged, WAF-Protected)**:
    - `2022-2024 Real World Learning Program Evaluation.pdf` (`AttachmentID: 387812`)
    - `Program Evaluation Schedule 24-25.docx - Google Docs (2).pdf` (`AttachmentID: 387813`)
  - **Board Brief Disclosures (Article 2011053)**: Confirms the evaluation covered four specific domains: college preparation/placement, career-center/academy enrollment, Market Value Asset (MVA) attainment, and STEM course participation. It added the qualitative assessment: *"The district has experienced sustained and significant growth in Real-World Learning programming in recent years."*
- **Concurrent Accountability Reporting**:
  - **Item G.1.a**: *C&I Update*. Curriculum & Instruction presented the 2024 Missouri DESE Annual Performance Report (APR). Total score: **127.5 out of 200 points (63.7%)**, with Continuous Improvement earning **86.6%** of available points.

### Meeting 2: January 16, 2025 (`MID 16922`) — First Post-Direct-Grant Meeting
- **Key Real-World Learning Items**:
  - **Item G.1.a**: *C&I Update*. Addressed by guest speaker **Eric Wollerman, President of Honeywell FM&T** (Kansas City National Security Campus).
  - **Programmatic Disclosures**: Administration outlined shared regional pathways in partnership with neighboring districts (Center, Hickman Mills) and PREP-KC, highlighting Graphic Design, Barbering/Cosmetology, Welding, Healthcare, and Advanced Manufacturing. Internal district MVA tracking systems were reviewed.

### Meeting 3: March 20, 2025 (`MID 17411`) — Strategic Plan & MVA Credential Alignment
- **Key Actions**:
  - **Item G.5.a**: *Strategic Plan Review*. Administrative review of the Comprehensive School Improvement Plan approved June 20, 2024, confirming standing operational focus on Pillar 1 (Success-Ready Students).
  - **Item G.1.b**: *Seal of Biliteracy Award & Resolution*. Approved under motion by Dawn Foy, seconded by Helen Ransom (`vote_result: motion_approved`), formally recognizing language biliteracy credentials aligned with Market Value Asset definitions.

### Meeting 4: April 16, 2026 (`MID 24913`) — Administrative Transition Period
- **Key Actions**:
  - **Item G.1.a**: *C&I Update*. Executive reporting documenting student participation in Foundations for the Future Week and ongoing Real World Learning opportunities during the superintendent transition period.

### Meeting 5: June 18, 2026 (`MID 25898`) — Fiscal & Operational Continuity Evidence
- **Key Actions**:
  - **Item D.3.a**: *Approval of Memorandum of Agreement with T&L Welding*. Approved via Consent Agenda (`approved_via_consent`), renewing vocational welding instruction allowing students to complete up to 200 hours of coursework toward industry credentials.
  - **Item D.3.d**: *Approval of Healthcare Training Partnership with Between Me 2 You*. Approved via Consent Agenda (`approved_via_consent`), establishing clinical instruction partnerships for CNA, Phlebotomy, and medical assisting.
  - **Item G.3.b**: *Preliminary Operating Budget Adoption FY2026-27*. Operational budget adoption approving preliminary expenditures for the fiscal year under incoming Superintendent Dr. Stephanie Amaya.

---

## 5. Observable-Only RWL Program Evaluation Schema

The schema below records **only what is directly observable** from the accessible text of Simbli Agenda Item `G.1.c` and Board Brief Article `2011053`. Numeric fields and calculations located inside WAF-protected attachment 387812 are strictly designated as `unobservable_in_accessible_text`.

| Domain / Topic | Domain Type | Observable Claim / Metric | Evidence Source | Reported Numeric Value | Governance Action | Epistemic Note |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **College Preparation & Placement** | `rwl_evaluation_domain` | Data analyses of college prep and placement included in evaluation | Board Brief 2011053 | *unobservable* | Formally approved | Metric values and denominators remain inside attachment 387812. |
| **Career Center & Academy Enrollment** | `rwl_evaluation_domain` | Data analyses of enrollment in career centers and academies | Board Brief 2011053 | *unobservable* | Formally approved | Specific program-level enrollment counts remain inside attachment 387812. |
| **Market Value Asset (MVA) Attainment** | `rwl_evaluation_domain` | Data analyses of MVA attainment included in evaluation | Board Brief 2011053 | *unobservable* | Formally approved | District senior attainment percentages not disclosed in brief; regional aggregate must not be substituted. |
| **STEM Course Participation** | `rwl_evaluation_domain` | Data analyses of student participation in STEM classes | Board Brief 2011053 | *unobservable* | Formally approved | Course enrollment numbers and PLTW breakdowns remain inside attachment 387812. |
| **Program Growth Trajectory** | `rwl_evaluation_qualitative_finding` | "Sustained and significant growth in Real-World Learning programming in recent years" | Board Brief 2011053 | *not_applicable* | Public reporting | Qualitative characterization published by district communications; underlying time series unobservable. |
| **Policy IM Review Process** | `governance_policy_mandate` | Inclusion of RWL in standing instructional evaluation cycle under Policy IM | Agenda Item G.1.c | *not_applicable* | Unanimously approved | Documents inclusion in district policy evaluation schedule; does not prove permanent institutionalization. |
| **MSIP 6 APR Total Score** | `concurrent_accountability_context` | District earned 127.5 out of 200 points (63.7%) on 2024 APR | Agenda Item G.1.a | 63.7% (127.5/200) | Accepted as info | Reported concurrently in separate item G.1.a; state accountability metric, not direct RWL outcome. |
| **MSIP 6 Continuous Improvement** | `concurrent_accountability_context` | Grandview earned 86.6% of points in Continuous Improvement | Board Brief 2011053 | 86.6% | Accepted as info | Measures district-wide accountability growth milestones under MSIP 6. |

---

## 6. Video & Audio Archive Audit

An audit of public media repositories was conducted across official Grandview C-4 channels:
- **YouTube Channel**: `@GrandviewC-4SchoolDistrict`
- **District Stream Portals**: Grandview TV / `grandviewc4.net` Board of Education page.

### Audit Result
Status: `no_public_recording_located`.  
The district does not publicly broadcast or archive video recordings of its regular open board meetings. Public communication relies on published agendas, official minutes, and Edlio Board Briefs. This does not preclude the existence of internal audio recordings retained by the district secretary.

### Priority Segments for Potential Public Records Requests
Should audio recordings or Sunshine Law (RSMo Chapter 610) tapes be requested, the following segments are prioritized in [`priority_meeting_video_index.csv`](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-26-rwl-institutionalization/districts/grandview-c4/governance/priority_meeting_video_index.csv):
1. **2024-12-19 (`MID 16764`)**: Item `G.1.c` (Real World Learning Program Evaluation discussion and vote); Item `G.1.a` (MSIP 6 APR presentation).
2. **2025-01-16 (`MID 16922`)**: Item `G.1.a` (Eric Wollerman / Honeywell FM&T address and shared pathways expansion).
3. **2025-03-20 (`MID 17411`)**: Item `G.5.a` (Strategic Plan Review 2024–2027); Item `G.1.b` (Seal of Biliteracy presentation).
4. **2026-04-16 (`MID 24913`)**: Item `G.1.a` (RWL update during superintendent transition).
5. **2026-06-18 (`MID 25898`)**: Item `D.3.a` (T&L Welding MOA); Item `D.3.d` (Between Me 2 You healthcare MOU); Item `G.3.b` (Preliminary Budget FY27).

---

## 7. Next Steps for Research Continuation

1. **Course Guide & Catalog Integration (Gate 3)**: Analyze the Grandview High School Course Description & Planning Guide (`SRC-GV-OPS-001`) to assess whether the shared pathways observed in board discussions appear as formal course offerings.
2. **Financial Ledger Alignment (Gate 3)**: Cross-reference MOAs and programs against the adopted operating budgets (`SRC-GV-FIN-002`) to investigate local account code substitution following the expiration of direct Kauffman funding.
3. **Public Records Request Contingency**: If quantitative metrics for Item `G.1.c` (Dec 2024) are required, submit a targeted Sunshine Law request for Attachment 387812 (`2022-2024 Real World Learning Program Evaluation.pdf`).
