# Center School District 58: Priority Board Governance Corpus (Gate 2 Standard)

**District**: Center School District 58 (`048-080`)  
**E-Governance Platform**: Simbli by eBOARDsolutions (`SchoolID = 229`)  
**Corpus Scope**: Focal Transition Board Meetings spanning the Kauffman Real World Learning Grant Transition Boundary (FY25: October 2024 through June 2025)  
**Total Meetings Harvested**: 7  
**Total Priority Items Indexed**: 364  
**Total Governance Artifacts Manifested**: 21  

---

## 1. Corpus Architecture & Epistemic Standards

This governance corpus adheres strictly to the epistemic separation standards established in Gate 2:
1. **Observable Governance Facts**:
   - `item_title`, `action_requested`, `board_action`, `vote_result`, `motion_made_by`, `motion_seconded_by` are derived directly from primary meeting minutes JSON (`GetMeetingMinutes`) and agenda item records (`GetItemContents`).
   - Procedural items without votes (e.g., Call to Order, Pledge of Allegiance, Informational Presentations) are recorded factually as `no_vote_taken`. No synthetic unanimous defaults are introduced.
   - Presenter names are recorded only when explicitly stated in Simbli contact records.
2. **Derived Semantic Classifications**:
   - `explicit_rwl`, `explicit_mva`, `career_connected_semantic`, `money_mentioned`, `partner_mentioned` are flagged via explicit rule-based string matching and labeled `coding_method = 'rule_based_derived'`.

---

## 2. Ingested Focal Meetings Panel

| Meeting Date | Simbli MID | Title | Total Items | Explicit Career/CTE Items | Key Governance Actions |
| :--- | :--- | :--- | :---: | :---: | :--- |
| 2024-10-28 | `16288` | Regular Session Meeting | 53 | 0 | Standard Consent & Operations |
| 2024-11-25 | `16532` | Regular Session Meeting | 55 | 0 | A. No Tax Rate Increase Bond/Levy Transf |
| 2024-12-16 | `16561` | Regular Session Meeting | 43 | 1 | C. 15th Annual Prep-KC Regional Math Rel; B. New Reflections MOU; A. Grant Writing RFP |
| 2025-01-27 | `16754` | Regular Session Meeting | 45 | 3 | A. 15th Annual Prep-KC Regional Math Rel; 2. MARC Head Start Services Agreement (G; 1. GEAR UP |
| 2025-02-24 | `17110` | Regular Session Meeting | 53 | 0 | A. Reece Nichols Real Estate Rising Star |
| 2025-03-17 | `17383` | Regular Session Meeting | 50 | 0 | D. Be Great Together Grant Recipient |
| 2025-06-23 | `18452` | Regular Session Meeting | 65 | 2 | 1. Herndon Career Center - Renewal; 2. Summit Tech Academy - Renewal; 3. T & L Welding - Renewal |

---

## 3. Key Empirical Findings Across the December 31, 2024 Transition Boundary

### 3.1 Pre-Sunset Institutional Positioning (Oct–Dec 2024)
- **Grant Writing RFP Action (2024-12-16, MID 16561)**: In the final board meeting prior to the December 31, 2024 expiration of the Kauffman RWL grant, Superintendent administration presented a **Grant Writing RFP**, signaling formal administrative recognition that external philanthropic grant funding was terminating and alternative competitive grant mechanisms were required.
- **Regional Workforce Partnerships**: Continued recognition and participation in regional STEM/workforce pipelines (Prep-KC Regional Math Relays).

### 3.2 Post-Sunset Administrative Realignment (Jan–Jun 2025)
- **Summit Technology Academy (STA) Expansion (2025-01-27, MID 16754)**: Immediately following the expiration of the Kauffman grant, the Board approved a two-year extension agreement to ensure high school student transportation and enrollment in advanced career pathways at Summit Technology Academy.
- **GEAR UP Partnership MOU (2025-01-27, MID 16754)**: The district established an active Memorandum of Understanding with GEAR UP for postsecondary access and career counseling. Notably, this item was pulled from the Consent Agenda for explicit discussion before approval.
- **Operational Realignment (2025-01-27, MID 16754)**: The board approved administrative restructuring (*Alignment of Resources/Responsibilities*) to absorb operational duties under core district staffing.

---

## 4. Summary Corpus Metrics

| Metric | Count | Percentage of Corpus |
| :--- | :---: | :---: |
| **Total Ingested Agenda Items** | `364` | 100.0% |
| **Explicit Real World Learning (RWL) Items** | `6` | `1.6%` |
| **Explicit Market Value Asset (MVA) Items** | `0` | `0.0%` |
| **Career & Technical Education (CTE) / Workforce Connected Items** | `6` | `1.6%` |
| **Items Involving Direct Financial/Budgetary Amounts** | `28` | `7.7%` |

---

## 5. Artifact Directory Layout

```
data/raw/center-58/governance/
├── meetings/
│   ├── 2024-10-28_mid-16288/
│   │   ├── agenda/
│   │   ├── minutes/
│   │   └── packet/
│   ├── 2024-11-25_mid-16532/
│   ├── 2024-12-16_mid-16561/
│   ├── 2025-01-27_mid-16754/
│   ├── 2025-02-24_mid-17110/
│   ├── 2025-03-17_mid-17383/
│   └── 2025-06-23_mid-18452/
districts/center-58/governance/
├── simbli_meetings_index.csv
├── priority_meeting_items.csv
├── priority_meeting_artifacts.csv
└── GATE_2_GOVERNANCE_CORPUS.md
```
