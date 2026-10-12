# KC Pathways — Vertical Slice 01 Specification

**Working Title:** Kansas City — Paths Not Taken  
**Scenario:** Mission 01 — *A Future in Healthcare*  
**Focal Geography:** South Kansas City (Hickman Mills C-1 School District) & Midtown KC  
**Focal Institutions:** Ruskin High School, Hickman Mills Real-World Learning Center, MCC–Penn Valley Health Science Institute  
**Target Environments:** Jupyter Computational Notebook (`01_kc_paths_not_taken.ipynb`) and Standalone Browser UI  
**Design Reference:** Oliver (@Olliesiin) SF Housing Game model adapted to urban educational & career mobility  

---

## 1. Project Premise & Pedagogical Philosophy

Most educational dashboards present static school report cards: graduation rates, standardized test scores, demographic breakdown. These tools present outcomes as faits accomplis and risk reinforcing the **ecological fallacy**—the erroneous inference that an individual student's likelihood of becoming a nurse or engineer is determined by their census tract or school demographic average.

*KC Pathways* rejects both fatalistic demographic prediction and decontextualized optimism. It models educational and career progression as a **navigable constraint puzzle grounded in verified institutional rules, real geography, and scarce personal resources**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       THE PATHWAYS PROGRESSION CHAIN                        │
│                                                                             │
│   [ PLACE ]  ──►  [ SCHOOL ]  ──►  [ PROGRAM ]  ──►  [ CREDENTIAL ] ──► [ CAREER ]
│   Hickman          Ruskin HS        Health Start       CNA / Pharm Tech    Healthcare
│   Mills            (Grades 9-12)    (MCC-Penn Valley)  AAS Nursing         Allied Health
│                                                                             │
│   Each transition is governed by:                                          │
│   - Verified Institutional Rules (GPA, test cutoffs, dual credit)           │
│   - Physical Geography & Transit (commute, bus lines, schedules)           │
│   - Fictional Resource Budgets (Action points, time, coordination)          │
└─────────────────────────────────────────────────────────────────────────────┘
```

The player is not told what their future will be. The player explores **what becomes feasible, difficult, expensive, or blocked** when specific circumstances, policies, or decisions change.

---

## 2. Mission 01 Scope: "A Future in Healthcare"

### Character & Setting
- **Persona:** Fictional Grade 10 student attending Ruskin High School (7000 E 111th St, Kansas City, MO).
- **Goal:** Explore viable routes into healthcare before high school ends, balancing district off-campus academies against postsecondary community college routes.
- **Duration:** 3 Planning Rounds (representing planning periods during the sophomore school year).
- **Resource Budget:** 2 Action Points (AP) per round = 6 AP maximum across the mission. Unused AP expires at round end.

### Physical Locations
1. **Ruskin High School** (`38.923090, -94.506760`): Home campus and advising base.
2. **Hickman Mills Real-World Learning Center** (`38.939400, -94.532954`): District career-learning hub coordinating Health Start Academy.
3. **MCC–Penn Valley Health Science Institute** (`39.064955, -94.590989`): Midtown facility discovered in Round 2 for postsecondary exploration.

### Transportation Profiles (Counterfactual Replay Mechanism)
The player selects one of two starting transportation conditions:
- **Profile A (`reliable`):** Student has dependable family or personal transportation.
- **Profile B (`needs-coordination`):** Student relies on public transit or district shuttles. Preparing a Health Start inquiry requires an additional 1-AP transportation investigation before submitting.

---

## 3. Action Catalog & Resource Economy

| Action ID | Action Title | Cost | Available | Location | Prerequisites | Result Flag |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `speak_counselor` | Speak with a Counselor | 1 AP | Round 1 | Ruskin High | None | `counselor_consulted` |
| `investigate_health_start` | Investigate Health Start | 1 AP | Round 1 | RWL Center | None | `health_start_researched` |
| `investigate_transport` | Investigate Transportation | 1 AP | Round 1 | Ruskin High | `needs-coordination` profile | `transport_documented` |
| `prepare_health_start_inquiry` | Prepare Health Start Inquiry | 2 AP | Round 1 | RWL Center | Counselor + Health Start + Transport (if profile B) | `health_start_prepared` |
| `explore_mcc_health` | Explore MCC Health Programs | 1 AP | Round 2 | MCC–Penn Valley | Round $\ge 2$ | `mcc_explored` |
| `compare_college_options` | Compare College Options | 1 AP | Round 2 | MCC–Penn Valley | `mcc_explored` | `college_compared` |
| `draft_postgrad_plan` | Draft Postgraduation Plan | 1 AP | Round 2 | MCC–Penn Valley | `college_compared` | `postgrad_plan_prepared` |

---

## 4. Possible Endings & Evaluative Reflection

1. **Health Start Inquiry Prepared:**  
   The player completes the high-school career academy route. Achievable with 4 AP under reliable transport (leaving 2 AP for college exploration) or 5 AP under coordinated transport (leaving 1 AP).
2. **Postsecondary College Exploration Plan Drafted:**  
   The player explores MCC–Penn Valley, compares stackable credentials vs. AAS nursing/allied health degrees, and drafts a postsecondary plan (3 AP required in Rounds 2–3).
3. **Still Exploring (Partial Progress):**  
   The player spent action points across disparate investigations without assembling a coherent terminal plan. The debrief emphasizes the opportunity cost of uncoordinated exploration and invites a replay.

---

## 5. Epistemic Demarcation Rules

Every piece of information displayed in the UI or notebook must carry one of three explicit labels:
1. `verified_fact`: Backed by official district, state, or institutional documentation (with URL and checked date).
2. `simulation_assumption`: A declared scenario rule or resource parameter (e.g., 2 AP per round, transportation condition).
3. `unknown`: An empirical or institutional unknown that requires inquiry rather than algorithmic hallucination (e.g., cohort seat limits, exact future deadlines).

No demographic causal determinism, synthetic test-score penalties, or fabricated wage figures may be introduced.
