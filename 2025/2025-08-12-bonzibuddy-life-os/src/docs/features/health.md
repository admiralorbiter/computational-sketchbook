# Health Feature Spec (v0 → v2)

**Status:** ✅ **IMPLEMENTED (v0 Complete)**
**Scope:** Everything under **Self & Health** for a local, single‑user Flask app (SQLite, manual migrations). This doc is the canonical spec for the Health feature. If any section outgrows this page, see **Split Candidates** below.

## 🎯 **Implementation Status**

### ✅ **v0 Features - COMPLETED**
- **Database Schema**: All v0 tables created and migrated
- **SQLAlchemy Models**: Full ORM implementation with relationships
- **Service Layer**: Business logic for all CRUD operations
- **REST API**: Complete API endpoints for all health entities
- **Dashboard UI**: Interactive health dashboard with Bootstrap + Alpine.js
- **Testing**: 12/12 tests passing (100% success rate)

### 🚧 **v1+ Features - PLANNED**
- Enhanced medication scheduling and interactions
- Condition and flare tracking
- Preventive care rules and reminders
- Mental health tracking tools
- Fitness and workout logging
- Sleep and recovery monitoring
- Nutrition and hydration tracking
- Lab results management

### 🔗 **Quick Links**
- **[Health Dashboard](http://localhost:5000/health/)** - Live application
- **[Implementation Plan](planning/HealthImplementationPlan.md)** - Technical details
- **[API Endpoints](api/ENDPOINTS.md)** - REST API documentation

---

## 1) Goals & Non‑Goals

### Goals

* Track **meds & supplements**: doses, refills, adherence; optionally interactions.
* Log **conditions & symptoms** with flare tracking and triggers.
* Surface **preventive care & screenings** using age/sex‑based schedules (local rules table first; later external sources).
* Manage **appointments & care team** (prep checklists, follow‑ups, contact info).
* Support **mental health** tracking: therapy plans, mood & sleep logs, coping tools.
* Track **fitness & training**: programs, workouts, PRs, recovery notes.
* Track **sleep & recovery**: sleep debt, wind‑down routine; optional import from Oura.
* Track **nutrition & hydration**: meal notes, macros, water goals (lightweight in v0).
* Record **vitals & labs**: BP, A1C, lipid panels, trends, custom labs (e.g., transplant labs).
* Record **accessibility & accommodations** notes for workplaces/venues.
* Maintain an **Emergency medical profile** (allergies, meds, ICE contacts).
* **Integrations (later):** Oura Ring, diabetes CGM/reader imports.

### Non‑Goals (v0)

* No medical advice or dosing recommendations.
* No automated reminders (no scheduler yet) — but show **computed "due" lists** in UI.
* No online EHR sync; CSV/JSON imports only.

---

## 2) Data Model (manual SQL)

Tables marked **(v0)** exist in initial migrations; **(v1+)** are planned expansions.

### Core

* **schema\_version** (existing).
* **profile** (existing): display\_name, timezone.
* **tag** / **tag\_map** (v1): lightweight tagging across entities.
* **attachment** (existing): file path, mime, bytes, note.
* **audit** (existing): action log.

### Meds & Supplements

* **med** **(v0)**: `id, name, dose_text, notes`
  *Optional v1 fields:* `form (tablet/capsule/injection), strength, unit`
* **med\_event** **(v0)**: `id, med_id, ts, amount, note` (adherence log)
* **med\_schedule** **(v1)**: `med_id, time_of_day, days_mask, with_food BOOL`
* **med\_refill** **(v1)**: `med_id, qty, refills_left, pharmacy, last_filled_ts`
* **med\_interaction** **(v1)**: `a_med_id, b_med_id, severity, note` *(local list; import later)*

### Conditions & Symptoms

* **condition** **(v1)**: `id, name, dx_date, status, note`
* **symptom\_log** **(v0)**: `id, ts, label, severity INT, trigger, note`
* **flare** **(v1)**: `id, condition_id, start_ts, end_ts NULL, trigger, notes`

### Preventive Care & Screenings

* **preventive\_rule** **(v1)**: `id, name, sex, min_age, max_age, interval_months, note`
* **preventive\_due** **(v1, computed table or view)**: derived from rules + last completion.
* **preventive\_event** **(v1)**: `id, rule_id, ts, result, next_due_ts`

### Appointments & Care Team

* **provider** **(v1)**: `id, name, specialty, location, phone, portal_url`
* **appointment** **(v0)**: `id, ts, provider, location, purpose, note`
  *Option (v1):* `provider_id FK`, `status`, `followup_ts`.
* **appointment\_checklist** **(v1)**: `id, appointment_id, item, done BOOL`

### Mental Health

* **therapy\_plan** **(v1)**: `id, goals TEXT, techniques TEXT, owner`
* **mood\_log** **(v1)**: `id, ts, mood INT(1–5), anxiety INT, sleep_quality INT, note`
* **coping\_tool** **(v1)**: library of strategies/templates

### Fitness & Training

* **workout** **(v1)**: `id, ts, kind, duration_min, rpe INT, notes`
* **set\_log** **(v1)**: `workout_id, exercise, sets, reps, weight`
* **pr** **(v1)**: `exercise, value, unit, ts`

### Sleep & Recovery

* **sleep\_log** **(v1)**: `ts_start, ts_end, efficiency, stages_json, notes` (manual or imported)

### Nutrition & Hydration

* **meal** **(v1)**: `ts, name, kcal, protein_g, carbs_g, fat_g, notes`
* **water\_log** **(v1)**: `ts, amount_ml`

### Vitals & Labs

* **vital** **(v0)**: `id, ts, kind, value_num, unit, note`
  *Examples:* BP(S/D as two rows or in `note`), HR, weight, temp.
* **lab\_result** **(v1)**: `id, ts, name, value_num, unit, ref_low, ref_high, note`
* **lab\_panel** **(v1)**: `id, name (e.g., Lipid Panel)`, with join table to results.

### Accessibility & Accommodations

* **accommodation\_note** **(v1)**: `id, context, org, note, last_used_ts`

### Emergency Medical Profile

* **emergency\_profile** **(v1)**: `id, allergies TEXT, conditions TEXT, meds_summary TEXT, ice_name, ice_phone, org_id_cards TEXT`

### Diabetes‑specific (extension)

* **glucose\_log** **(v1)**: `ts, mg_dl, source (CGM|fingerstick), note`
* **insulin\_dose** **(v1)**: `ts, kind (bolus|basal), units, note`
* **carb\_log** **(v1)**: `ts, grams, note`

### Transplant‑specific (extension)

* **transplant\_profile** **(v1)**: `id, organ, tx_date, center, care_team JSON`
* **immunosuppressant** **(v1)**: `id, med_id FK, target_trough_min, target_trough_max`
* **transplant\_lab** **(v1)**: `ts, name (creatinine|eGFR|tacro), value_num, unit, note`

**Indexes & retention:**

* Add indexes on time (`ts`) and foreign keys. No auto‑purge yet; exports via CSV/JSON.

---

## 3) Views & Flows

### Health Home (dashboard)

Cards for: **Today’s meds**, **Upcoming appointments (30d)**, **Due preventive items**, **Recent symptoms**, **Recent vitals**, **Sleep summary (last 7d)**, **Glucose trend (if imported)**.

### Meds & Supplements

* **List**: name, dose, adherence % (last 14d), refill status.
* **Detail**: dose instructions, events timeline, notes.
* **Quick log**: add `med_event` with now/amount.
* **Refill aide** (v1): editable `refills_left`, pharmacy.
* **Interactions** (v1): surface known pairs from local table; manual notes.

### Conditions & Symptoms

* **Symptom logger**: label, severity 1–5, trigger, note (+ tags).
* **Flare tracker** (v1): start/stop flare windows; list triggers.
* **Trends**: bar/line by label & severity over time.

### Preventive Care

* **Rules list** (local): colonoscopy, A1C cadence, flu shot, etc.
* **Due view**: compute next‑due from last completion & rule interval.
* **Complete**: add `preventive_event`.

### Appointments & Care Team

* **Calendar list**: past/future.
* **Prep checklist** per appointment.
* **Provider directory** (v1): contacts, portal links, notes.

### Mental Health

* **Mood/sleep check‑in** (v1): single form; charts.
* **Therapy plan** (v1): goals & techniques; session notes.
* **Coping tools** (v1): quick reference.

### Fitness & Training

* **Workout logger** (v1): kind, duration, RPE; PR detection; session history.

### Sleep & Recovery

* **Sleep log** (manual or Oura import).
* **Wind‑down checklist** (v1): customizable.

### Nutrition & Hydration

* **Meal quick‑add** (v1): free‑text parse to macros (optional later).
* **Water tracker** (v1).

### Vitals & Labs

* **Quick‑add vitals** (BP, HR, weight, temp).
* **Labs** (v1): table, reference ranges, out‑of‑range highlights.

### Accessibility & Accommodations

* **Notes**: reusable blurbs by workplace/venue.
* **Share/print** (local export) (v1).

### Emergency Medical Profile

* **ICE card** editor + **print/export** (PDF/PNG) (v1).

---

## 4) Integrations & Imports (later)

### Oura Ring

* **Import path:** manual CSV/JSON export → map to `sleep_log`, `vital` (HR/HRV), `workout` (activity).
* **Mapping:** readiness, sleep stages, total sleep, HRV, RHR.
* **Future:** token‑based API sync (local cache only).

### Diabetes (CGM/reader)

* **Import path:** CSV from reader app → `glucose_log` (ts, mg/dL), optional `carb_log`, `insulin_dose`.
* **Derived views:** time‑in‑range %, low/high counts/day, post‑meal deltas.
* **Nudges (future):** show “walk 10 min” suggestion when post‑meal BG > threshold (no auto scheduling yet).

### Transplant

* **Focus:** immunosuppressant adherence view; transplant‑specific labs (creatinine/eGFR/tacrolimus).
* **Rules:** configurable target ranges; highlight out‑of‑range.

**Import UI:** dropzone (CSV/JSON), parser preview, dry‑run, then commit.

---

## 5) Business Rules (initial)

* **Adherence %** = med\_events taken ÷ scheduled (if schedule defined) for window (7/14/30d). Without schedules, compute vs. target times/day.
* **Preventive due** = last\_event + interval ≤ today (based on rule).
* **Severity scales:** 1–5 for symptom, 1–10 optional in settings.
* **Out‑of‑range lab** = value < ref\_low or > ref\_high → highlight.

---

## 6) UI/UX Notes

* Bootstrap forms; Alpine.js for quick‑add, inline editors.
* Keyboard shortcuts: `n` new entry, `/` focus search, `.` quick‑log now.
* Mobile‑first layouts for logging tasks.

---

## 7) Privacy & Risk

* Local‑only data; no uploads.
* Sensitive health data (HIPAA‑like); recommend full‑disk encryption at OS level.
* Exports stored under `/backups` — encourage external drive sync.

---

## 8) Metrics & Dashboards

* **Tiles:** meds taken %, next appointment, due screenings count, last A1C, time‑in‑range (if CGM), weekly symptom severity avg, sleep avg (hrs), weight trend.
* **Trends:** line charts per metric (later).

---

## 9) API (internal only)

*(v1 endpoints extend v0)*

* `GET /health/meds` | `POST /health/meds`
* `POST /health/meds/{id}/log`
* `GET/POST /health/symptoms`
* `GET/POST /health/vitals`
* `GET/POST /health/appointments`
* Imports: `POST /health/import/{oura|cgm}` (later)

---

## 10) Testing

* **Unit:** model helpers (adherence calc, due rules).
* **Feature:** create/log flows, import parser dry‑runs.
* **Fixtures:** sample CSVs (Oura, CGM), tiny DB snapshots.
* **Coverage target:** ≥80% for domain services.

---

## 11) Backlog

### v0 (already planned)

* Tables: `med`, `med_event`, `symptom_log`, `vital`, `appointment`
* Views: meds list/detail + quick‑log; symptom logger; vitals quick‑add; appointments list
* Dashboard cards (basic)
* Export CSV/JSON

### v1

* Preventive rules + due view
* Provider directory + prep checklists
* Mood log & therapy plan
* Workout logger & PRs
* Sleep log + Oura CSV import
* Nutrition (meal/water) basics
* Labs with ref ranges
* Tagging; attachments
* CSV importers (CGM, Oura) with dry‑run

### v2

* Interaction table + warnings
* Refill tracking + stock runway
* Transplant module (targets, labs)
* Diabetes module (time‑in‑range, bolus/carb analysis)
* ICE card printable/exportable
* Charts & trend analytics

---

## 12) Split Candidates (consider separate feature docs)

| Area                     | Complexity | Data Volume | UX Surface | Recommend Split? | Notes                                           |
| ------------------------ | ---------: | ----------: | ---------: | ---------------- | ----------------------------------------------- |
| Meds & Adherence         |       High |        High |     Medium | **Yes**          | Schedules, refills, interactions can grow fast. |
| Preventive Care          |     Medium |         Low |     Medium | Maybe            | Rule table + due logic is self‑contained.       |
| Appointments & Care Team |     Medium |      Medium |     Medium | Maybe            | Checklists & directory are reusable.            |
| Mental Health            |     Medium |      Medium |     Medium | Maybe            | Mood, therapy plans, coping tools.              |
| Fitness & Training       |     Medium |      Medium |     Medium | Maybe            | Workout/logger & PR logic.                      |
| Sleep & Recovery (Oura)  |     Medium |      Medium |     Medium | **Yes**          | Import parsers, sleep staging visuals.          |
| Nutrition & Hydration    |     Medium |        High |     Medium | Maybe            | Parsing, macros can balloon.                    |
| Labs & Panels            |     Medium |      Medium |     Medium | Maybe            | Panels, ranges, highlights.                     |
| Diabetes Module (CGM)    |       High |        High |       High | **Yes**          | Import, analytics, safety edge cases.           |
| Transplant Module        |       High |      Medium |     Medium | **Yes**          | Targets, critical labs, adherence focus.        |
| Emergency Profile        |        Low |         Low |        Low | No               | Fits here with print/export.                    |

---

## 13) Migrations (proposed adds)

* `0005_preventive_and_mood.sql` — preventive\_rule/event, mood\_log, therapy\_plan
* `0006_workout_sleep_meal.sql` — workout, sleep\_log, meal, water\_log
* `0007_labs_and_tagging.sql` — lab\_result, lab\_panel, tag\_map
* `0008_diabetes_transplant.sql` — glucose\_log, insulin\_dose, carb\_log, transplant\_\*

Each file uses `BEGIN; ... INSERT INTO schema_version(...); COMMIT;`.

---

## 14) Open Questions

1. Which **preventive rules** do you want preloaded (flu shot, A1C every 3 months, eye exam, etc.)?
2. For **med interactions**, OK to start with **manual notes only** and add a local list later?
3. Do you want **BP** stored as two values (Systolic/Diastolic) or one row each with `kind=BP_S/BP_D`?
4. Minimum viable import fields for **CGM** and **Oura**? (attach sample CSVs when ready.)
5. Any **must‑have charts** for v1 (e.g., A1C trend, time‑in‑range, sleep stages)?

---

## 15) ADR Hooks

* ADR‑H‑0001 — Health v0 entities & flows (this doc)
* ADR‑H‑0002 — Preventive care rules strategy
* ADR‑H‑0003 — Import mapping for Oura/CGM
* ADR‑H‑0004 — Transplant targets & lab ranges
