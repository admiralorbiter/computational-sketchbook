# BonziBuddy v2 — Product Philosophy & System Playbook (v0.1)

> A scalable, extensible, private-by-default life OS that helps Future You win.

---

## 0) TL;DR

* **Promise:** One assistant, many domains; add new capabilities like Lego bricks without rewiring the house.
* **Approach:** Opinionated *primitives* + a small set of *engines* (capture, schedule, rules, review, dashboards) + *domain packs* composed from those primitives.
* **Guardrails:** Local-first, explicit permissions, full audit log, portable data. Human-in-the-loop for anything consequential.
* **North Star:** “Did this reduce cognitive load and increase follow‑through?”

---

## 1) Design Tenets

1. **Capture is sacred.** Zero‑friction inboxes everywhere (voice/text/clip), fast fuzzy search, and later triage.
2. **One truth, many views.** There’s a single underlying graph; domains are just curated views + workflows.
3. **Small primitives, big compositions.** Trackers, checklists, schedules, inventories, ledgers, CRMs, and workflows are the atoms. Everything else is a molecule.
4. **Local-first, cloud‑optional.** Works offline, syncs opportunistically, end‑to‑end encryption for anything sensitive.
5. **Explainable automation.** Every action lists the rule that fired, inputs used, and how to undo.
6. **Progress over perfection.** Ship thin slices; default templates make good decisions easy.
7. **Accessibility by design.** Keyboard first, readable defaults, and assistive modes.
8. **Composable integrations.** Calendars, health, banks, tasks, storage—treat external systems as sources of truth with reconciliation.
9. **Safety modes.** Travel / Sick‑day / Focus change priorities, notifications, and automations globally.
10. **Portability.** Export everything, including rules, templates, and audit logs, in open formats.

---

## 2) System Architecture (conceptual)

**Primitives (data types)**

* `Entity` (person, account, vehicle, pet, plant, device, document, location)
* `Metric` (time‑series values: BP, A1C, weight, K/D, budget balances)
* `Log` (timestamped notes / events / symptoms / workouts)
* `Checklist` (steps with states; supports templates)
* `Schedule` (one‑off or recurring events with reminders)
* `InventoryItem` (qty, unit, par level, expiry, location)
* `LedgerItem` (amount, currency, category, counterparty, receipt)
* `Task` (status, priority, estimate, context tags)
* `Project` (goal, milestones, dependencies)
* `Document` (files/links, versioning)
* `IntegrationAccount` (scopes & tokens)

**Engines (services)**

* **Capture Engine:** quick add; OCR/ASR; schema suggestion.
* **Rules Engine:** `when` (event) + `if` (conditions) + `then` (actions). All rules are versioned and testable.
* **Scheduler:** calendars, reminders, time‑blocking; respects safety modes.
* **Review Engine:** daily/weekly/monthly rituals with checklists and surfaced insights.
* **Reconciliation:** two‑way sync with sources (calendars, health, bank); de‑dupe + conflict resolution.
* **Insight Engine:** simple stats → trends → anomalies; explain assumptions.
* **Dashboard Builder:** tiles from metrics, logs, tasks, and projections.
* **Audit Log:** immutable event store of reads/writes/rules fired.

**Data Model:** property graph (`Entity --[relationship]--> Entity`) + append‑only events + time‑series for `Metric`.

**Interfaces:**

* Command palette ("Add meds", "Log BP 122/78", "Next best task").
* Domain views (Health, Home, Money, etc.).
* Rule editor (blocks now, text later).
* Integrations hub.

---

## 3) Privacy, Security, and Governance

* **Default privacy:** private/local by default. Opt‑in per integration and per rule.
* **Data minimization:** store only what’s needed; allow redaction.
* **Strong boundaries:** PHI/financial data isolated at rest; separate encryption keys.
* **Explainability:** every insight links to inputs; click‑through to raw events.
* **Permissions:** shareable spaces (e.g., family, care team) with role‑based access.
* **Portability:** one‑click export (JSON + attachments + rules + dashboards). Importers for re‑hydration.
* **Auditability:** all actions recorded with timestamp, actor, and reason.

---

## 4) Extensibility Model

**Domain Pack = Primitives + Views + Workflows + Rules + Integrations**

* Pack folder includes: `/schema`, `/templates`, `/rules`, `/dashboards`, `/tests`.
* Versioned; semantic versioning; migration scripts for breaking changes.
* Packs can be enabled/disabled without affecting core data.

**Capability Spec (sketch)**

```yaml
name: meds-and-supplements
version: 0.1.0
entities:
  - Medication: {name, dose, unit, route, schedule_ref, prescriber_ref}
checklists:
  - RefillChecklist: [Check remaining, Request refill, Pick up]
schedules:
  - DoseSchedule: {times: [08:00, 20:00], ruleset: adherence-nudges}
rules:
  - when: missed_dose > 30m
    if: user.not_in(FocusMode)
    then: notify("You’re 30m late for Metformin"), create_task("Take dose now")
integrations:
  - apple_health, google_fit
```

**Rule DSL (concepts)**

* Events: `task.completed`, `metric.logged`, `calendar.event.start`, `integration.sync`, `location.entered`, `bg.reading.updated`.
* Conditions: time windows, modes, tags, thresholds, streaks.
* Actions: notify, schedule, create/update entities, append log, change mode, call integration, request confirmation.
* Always allow **dry‑run** and **why‑run** (explain what would fire and why).

---

## 5) UX Principles

* **Start from templates.** Every domain ships with a thin useful default.
* **One‑screen decisions.** No wizard rabbit holes; show key info + default next step.
* **Keyboard and voice first.** Command palette, global hotkeys; voice capture.
* **State is visible.** Badges for overdue/blocked; streaks for habits.
* **Undo is cheap.** Every action is reversible; deletions are soft by default.
* **Focus windows.** Deep‑work blocks shield notifications and rule firings unless explicitly whitelisted.

---

## 6) Patterns Library (reusable feature shapes)

1. **Tracker** → Inputs (manual/import) → Time‑series → Trend/targets → Alerts.
2. **Checklist** → Template → Instance → Progress → Archive.
3. **Schedule** → Recurrence → Reminder windows → Snooze/Skip → Compliance.
4. **Inventory** → Par levels → Low‑stock → Reorder list.
5. **Ledger** → Import (CSV/API) → Categorize → Reconcile → Reports.
6. **Project/Task Graph** → Dependencies → Critical path → Review.
7. **CRM** → Contacts → Touch cadence → Notes → Introductions.
8. **Library** → Items → Tags → Queues → Highlights/Quotes.
9. **Plan** → Scope → Constraints → Budget → Milestones → Risks.
10. **Dashboard** → Tiles → Targets → Anomalies → Drill‑down.

These ten shapes cover \~95% of your domain list by composition.

---

## 7) Domain Blueprints (starter mappings)

Below are concise blueprints showing how the domain maps to primitives + engines. Each includes **Key Entities**, **Core Workflows**, **Rules**, and **Dashboard Tiles**.

### 7.1 Self & Health

* **Meds & Supplements**

  * Entities: `Medication`, `DoseSchedule`, `Refill`, `Allergy`, `Provider`.
  * Workflows: start med → adherence tracking → refill runway → interaction check.
  * Rules: missed dose nudge; low‑refill runway (<7 days) → add to errands; travel time‑shift; sick‑day mode auto‑snooze.
  * Tiles: adherence %, next dose, refill runway, last labs.
* **Conditions & Symptoms**

  * Entities: `Condition`, `SymptomLog`, `Trigger`.
  * Rules: flare frequency ↑ → suggest trigger review; correlate with sleep/activity.
* **Vitals & Labs**

  * Entities: `Metric`(BP, A1C, lipids), `LabOrder`/`Result`.
  * Rules: due date approaching; anomaly alerts with soften‑edges (confirm before alarming).
* **Emergency Profile**

  * Entities: `EmergencyCard` (allergies, meds, ICE).
  * Rules: printable/exportable card updated on change; shareable with QR + access controls.

**Kidney transplant + diabetes (special pack)**

* Sick‑day mode; clinic pack checklist; CGM + meals + steps juxtaposed; infection‑risk radar (season + event density) → pre‑trip packing preset.

### 7.2 Home & Property

* Entities: `Asset`(appliances), `MaintenanceSchedule`, `Warranty`, `Manual`, `Contractor`.
* Rules: seasonal checklists; warranty nearing end → test/claim; battery/filters cycle; outage alerts.

### 7.3 Food & Shopping

* Entities: `InventoryItem`, `Recipe`, `MealPlan`, `Store`.
* Rules: smart grocery list = meal plan + staples + low stock; location‑aware reminders; return deadlines.

### 7.4 Money & Admin

* Entities: `Account`, `Bill`, `Subscription`, `Policy`, `Claim`, `Document`.
* Rules: due dates; price‑hike detection; renewal windows; fraud alerts; export tax packet.

### 7.5 Mobility & Travel

* Entities: `Vehicle`, `Service`, `Recall`, `Trip`, `Itinerary`, `Visa`.
* Rules: maintenance by mileage/time; visa lead times; points nearing expiry; travel health schedule shift.

### 7.6 Work & Career

* Entities: `Goal`, `OKR`, `Project`, `Task`, `Meeting`, `Note`, `Expense`, `Certification`.
* Rules: weekly review prompts; stuck‑card detector (idle > N days); CEU renewals.

### 7.7 Family, Relationships & Care

* Entities: `Contact`, `Preference`, `Gift`, `Event`, `Pet`, `Plant`, `CarePlan`.
* Rules: touch‑base cadence; feeding/meds schedules; licenses/IEP/504 renewals.

### 7.8 Learning, Hobbies & Creativity

* Entities: `Course`, `PracticeLog`, `Highlight`, `Draft`, `Showcase`.
* Rules: spaced review; publish‑one‑thing‑per‑week cadence; competition deadlines.

### 7.9 Digital Life & Security

* Entities: `Device`, `Backup`, `PasswordManagerRef`, `Domain`, `StorageQuota`.
* Rules: backup/restore fire‑drill; permission audits; domain/SSL renewals.

### 7.10 Time, Focus & Planning

* Entities: `CalendarBlock`, `Routine`, `Habit`, `Template`, `Availability`.
* Rules: energy‑based scheduling; “next best task” ranks by urgency×importance×context; mode flips.

### 7.11 Community & Civic Life

* Entities: `Membership`, `Donation`, `VolunteerEvent`, `Ballot`.
* Rules: receipts archive; registration/ballot dates; recurring giving.

### 7.12 Media, Comms & Fun

* Entities: `Event`, `Draft`, `Album`, `FocusProfile`.
* Rules: content pipeline scaffolds; focus modes.

### 7.13 Transitions & Special Situations

* Entities: `Transition`, `Checklist`, `AddressChange`, `Claim`, `EstateTask`.
* Rules: moving/offboarding cascades; bereavement estate task sequence; disaster playbooks.

### 7.14 Piano (Practice System)

* Entities: `Piece`, `TechniqueDeck`, `TroubleBar`, `PracticeSession`, `Recording`.
* Rules: SRS for trouble bars; tempo ladders; recital prep timeline.

### 7.15 Call of Duty (Gaming Hub)

* Entities: `Loadout`, `SensitivityProfile`, `MapNote`, `KPI`.
* Rules: warm‑up sequence; VOD review checklist; KPI anomaly nudges.

### 7.16 Writing a Book

* Entities: `Idea`, `Outline`, `Scene`, `Character`, `WorldNote`, `Draft`, `RevisionPass`, `BetaReader`, `Submission`.
* Rules: daily word‑count sprints; burndown; beta reader deadlines.

### 7.17 Skill Management & Learning

* Entities: `Skill`, `Level`, `Reps`, `Exam`, `CEU`.
* Rules: deliberate practice loops; mock exam cadence; 12‑week planning.

### 7.18 Creativity & Content Studio

* Entities: `Idea`, `Asset`, `Post`, `Release`, `PortfolioItem`.
* Rules: make‑one‑thing/week; repurpose pipeline.

### 7.19 Relationships & Community Extras

* Entities: `Contact`, `Nudge`, `ThankYou`, `Intro`.
* Rules: gratitude queue; connector log prompts.

### 7.20 Life UX & Experiments

* Entities: `Friction`, `Experiment`, `EnergyEntry`, `FocusScene`.
* Rules: 1% fixes; energy diary insights; phone‑drawer schedules.

### 7.21 Money & Assets (Nerdy)

* Entities: `PriceBookItem`, `UsageLog`, `Warranty`, `SparePart`.
* Rules: cost‑per‑use dashboards; renewal pings.

### 7.22 Digital Workshop

* Entities: `Snippet`, `Hotkey`, `AutomationIdea`, `BackupDrill`, `ArchiveBatch`.
* Rules: ROI estimate; fire‑drill schedules; quarterly archive festival.

### 7.23 Safety & Resilience

* Entities: `ICEPacket`, `RecoveryCodes`, `Risk`, `DisasterPlaybook`.
* Rules: recovery code verification cadence; top‑10 risk review.

### 7.24 Travel & Adventure Extras

* Entities: `MicroTrip`, `EatListItem`, `PackPreset`, `RemoteWorkKit`.
* Rules: radius/budget generator; climate × activity pack layers.

### 7.25 Meta: Coaching & Feedback

* Entities: `Review`, `Decision`, `HabitHealth`.
* Rules: weekly review script; anomaly alerts (bills/sleep/output dips).

### 7.26 Work Output Accelerator

* Entities: `DeepWorkBlock`, `ShipLog`, `Sprint`, `Contract`.
* Rules: auto‑shield deep work; stuck‑card prompts; demo day cadence.

### 7.27 Photography & Film Lab

* Entities: `ShotList`, `Preset`, `Location`, `EditPair`, `PortfolioSet`.
* Rules: weekly theme; speed‑edit time trials; quarterly curation.

### 7.28 YouTube Series & Blog Engine

* Entities: `Pillar`, `Script`, `Recording`, `Thumbnail`, `PublishEvent`.
* Rules: scaffold pipelines; title A/B tests.

### 7.29 Portfolio + Presence

* Entities: `Portfolio`, `Badge`, `Showcase`, `Metric`.
* Rules: auto‑pull from repos/kanban; proof‑of‑impact section.

### 7.30 Software & Game‑Dev Factory

* Entities: `Prototype`, `Playtest`, `Kit`, `ReleaseChecklist`.
* Rules: weekly micro‑ship treadmill; telemetry basic checks.

### 7.31 Student Work & CS Programs

* Entities: `Challenge`, `Mentor`, `ShowcaseEvent`, `Artifact`.
* Rules: monthly demo day; mentor CRM nudges.

### 7.32 Research & Data Hub

* Entities: `Question`, `Scan`, `Dataset`, `Experiment`, `Result`.
* Rules: 2‑hour lit scans; reproducible lab pipeline.

### 7.33 Pairing Engine

* Entities: `Pairing`, `FocusLevel`, `Preset`.
* Rules: suggest ready pairings; block conflicts.

### 7.34 Routines & Cadences

* Entities: `Routine` (daily/weekly/monthly), `Review`.
* Rules: AM/PM routines, weekly publish, monthly ship audit.

### 7.35 Dashboards & KPIs

* Tiles defined per domain; global board shows Health, Creation, Code, Photo/Film, Impact.

### 7.36 Safety/Guardrails Modes

* **Travel:** shift med times, lighter publishing, pack kits prompts.
* **Sick‑day:** hydrate + meds + rest; snooze nonessential; low‑focus tasks surface.
* **Focus:** block distractors; queue low‑focus tasks.

---

## 8) “Next Best Task” (NBT) Engine (detail)

* **Inputs:** deadlines, importance, estimated value, effort, energy match, context availability, streaks, modes.
* **Score:** `priority = f(urgency, importance, energy_fit, context_fit, expected_value / effort)`.
* **Output:** top 3 tasks + rationale; show alternatives for variety.
* **Controls:** sliders for “today’s energy” and “time available”.
* **Ethics:** never nag; offer silent mode; respect do‑not‑disturb windows.

---

## 9) AI/LLM Usage Policy

* Retrieval‑augmented generation for summaries and drafting; never fabricate structured data.
* Deterministic first for calculations, reminders, and rules; LLMs for synthesis and suggestions.
* **Human confirmation** for med advice, money moves, or privacy‑affecting actions.
* Prefer on‑device/in‑LAN models when feasible; otherwise, redact or hash sensitive fields.
* Keep prompts, outputs, and source pointers in the audit log for reproducibility.

---

## 10) Integrations & Sources of Truth

* Calendars (primary truth for events) • Health (Apple Health/Google Fit/CGM) • Finance (bank/credit CSV/API) • Storage (Drive/Dropbox/Local) • Task managers (two‑way with tags) • Email (parse bills/travel).
* **Reconciliation rules:** idempotent imports; duplicate detection; user‑visible conflict resolution.

---

## 11) Modes & Global State

* `FocusMode(on/off, whitelist_rules)`
* `TravelMode(start/end, timezone_shifts)`
* `SickDayMode(level)`
* Mode transitions log cause and revert steps.

---

## 12) Failure Modes & Resilience

* **Network loss:** queue writes; show offline banner.
* **Clock skew/timezone jumps:** store in UTC + local; rebase schedules safely.
* **Duplicate items:** hash‑based de‑dupe; merge UI.
* **Bad rule:** sandbox + dry‑run + rate limits + global kill‑switch.
* **Data corruption:** append‑only event store + verified backups + restore drills.

---

## 13) Shipping Heuristics & Roadmap Skeleton (30‑day starter)

* **Week 1:** capture everywhere, command palette, basic tasks, audit log.
* **Week 2:** schedules + reminders; NBT v0; Health: meds + vitals basics.
* **Week 3:** Money: bills/subscriptions; Home maintenance cycles; Review engine.
* **Week 4:** Integrations hub; export everything; modes; first dashboards.

---

## 14) Feature Brief Template (for any new capability)

Use this for every new feature or domain pack.

```markdown
# <Feature Name>
**Problem** — Why this matters now; jobs to be done.
**Outcomes** — 2–4 measurable results.
**User Stories** — “As a <role>, I want <goal> so <benefit>.”
**Data Model** — Entities, relationships, metrics.
**Workflows** — Capture → Organize → Act → Review.
**Rules** — Events, conditions, actions, with examples.
**Integrations** — Systems of record & sync policy.
**Dashboards** — Tiles and drill‑downs.
**Safety/Privacy** — Risks, mitigations, consent points.
**Edge Cases** — Failure modes and fallbacks.
**MVP Slice** — What ships first (2 weeks max).
**Next Iterations** — v0.1 → v0.2 → v0.3.
**Test Plan** — Unit, scenario, rule dry‑runs; acceptance.
**Telemetry** — What we log and why.
```

---

## 15) Example Filled Briefs (abridged)

### A) Meds & Supplements (Health)

* **Outcomes:** ≥95% adherence; zero surprise runouts; travel shifts error‑free.
* **Data Model:** `Medication`↔`DoseSchedule`↔`Refill`; `Interaction` list; `Provider`.
* **Rules:** missed dose (+30m) → nudge; refill runway <7d → add to Grocery/Pharmacy list; TravelMode shift times; Sick‑day snoozes nonessential.
* **MVP (2 weeks):** add meds + dose times; reminders; adherence log; manual refill counter.

### B) Home Maintenance

* **Outcomes:** on‑time seasonal tasks; no lapsed smoke alarms.
* **Data Model:** `Asset` with `MaintenanceSchedule`, `Warranty`, `Manual`.
* **Rules:** filters/batteries cadence; warranty expiring → test; storm alerts → gutter check.
* **MVP:** template checklists (quarterly/seasonal); reminders; completion log.

### C) Next Best Task Engine

* **Outcomes:** daily plan in 30s; increased completion rate.
* **Data Model:** `Task` with context (place/tools/energy), `Availability`.
* **Rules:** ranker using urgency×importance×context; do‑not‑disturb respect.
* **MVP:** score + top 3 with rationale; sliders for energy/time.

### D) Trip Planning

* **Outcomes:** zero missed documents; smart pack list; time‑shifted meds.
* **Data Model:** `Trip`, `Itinerary`, `Visa`, `PackPreset`, `Reservation`.
* **Rules:** visa lead‑time alerts; pack presets by climate/activity; points expiry nudges.
* **MVP:** import itinerary emails; packing checklist; calendar overlay.

### E) Personal CRM

* **Outcomes:** remember birthdays and last chats; natural nudge cadence.
* **Data Model:** `Contact`, `Preference`, `NudgeSchedule`, `Gift`.
* **Rules:** quarterly touch for key contacts; thank‑you queue; intro tracking.
* **MVP:** contact cards; tags; simple cadences; birthday reminders.

---

## 16) Naming, Voice, and Interaction Style

* **Tone:** direct, encouraging, non‑judgmental.
* **Microcopy:** “Nice ship.” “Want a lighter day?” “Sick‑day mode is shielding noise.”
* **Commands:** short verbs (add/log/plan/pack/snooze/review).
* **Colors & Status:** green (on track), amber (watch), red (action), gray (snoozed).

---

## 17) Observability & Telemetry

* Redacted, purpose‑limited logs.
* Metrics: capture success rate, rule firings (accepted/rejected), task completion latency, export/restore success, crash reports.
* User‑visible **System Journal**: “what the system did and why”.

---

## 18) Quality Bars & Checklists

* **Privacy review:** data needed? consent obtained? exportable?
* **Security review:** authz on every route; key handling; backup tested.
* **UX review:** one‑screen decision; undo path; keyboard path.
* **Resilience:** offline flow; retries; idempotency; migrations.
* **Docs:** brief filled; runbook updated; audit log entries verified.

---

## 19) Portability & Backup/Restore

* Nightly encrypted snapshots (local + optional cloud). Monthly restore drills.
* Export bundles contain data, rules, templates, dashboards, and mode states.

---

## 20) Governance & Ethics

* No dark patterns, no unlimited nagging, no hidden data sharing.
* Clear “power‑down” that halts all automations.
* User owns their data, forever.

---

## 21) Appendices

* **A. Glossary** (Entity, Event, Rule, Mode, Pack, Tile, etc.)
* **B. Example Rule Tests** (Given/When/Then style).
* **C. Example JSON Schemas** for common entities (Medication, Task, Asset).
* **D. Migration Notes** (versioning strategy, rollback).

---

**End of v0.1.**
