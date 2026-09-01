# Home & Property — Features Implementation Plan (v0→v2)

**Status:** ✅ Scaffold running (v0 WIP)
**Created:** August 2025
**Scope:** Implementation roadmap for Home & Property domain (v0 → v2) within the BonziBuddy v2 stack (Flask + SQLAlchemy + Bootstrap 5.3 + Alpine.js + SQLite).

---

## 🎯 Goals & Outcomes

* Reduce "house brain" load; make maintenance timely and visible.
* Maintain a reliable record of assets, warranties, manuals, and inventory.
* Provide safety readiness (detectors, drills, kits) with clear check cadence.
* Keep utilities/services details handy: rates, renewals, outages, support paths.
* Track projects from scope → budget → contractors → completion with receipts.

**North‑star metrics (targets by v1):**

* ✅ On‑time completion of recurring maintenance ≥ 85%
* ✅ 0 missed warranty expirations in last 12 months
* ✅ Safety checks coverage (smoke/CO/extinguishers) ≥ 90%
* ✅ Inventory completeness for big‑ticket items ≥ 95% (serial + photo)
* ✅ Average time to log a maintenance event ≤ 20s

---

## 🗺️ Scope (feature groups)

* **Chores & cleaning cycles** (weekly/monthly/seasonal)
* **Home maintenance** (HVAC filters, gutters, smoke alarms)
* **Appliances, manuals & warranties** (serials, claim steps)
* **Utilities & services** (rates, outages, renewal dates)
* **Home improvement projects** (scope, budget, contractors)
* **Home inventory** (for insurance; big items + photos)
* **Pest & lawn care schedules**
* **Home security & safety checks** (detectors, drills, kits)

---

## 🧱 Architecture & Conventions

* **Framework:** Flask 3.x domain blueprint `home`
* **DB:** SQLAlchemy 2.x on SQLite (prod‑ready to swap to Postgres)
* **UI:** Bootstrap 5.3 + Alpine.js 3.x (keyboard‑first, mobile‑friendly)
* **Migrations:** Manual SQL files with version tracking (matching health)
  - Applied: `0017_home_basics.sql`, `0018_home_extensions.sql`
* **Audit:** Reuse core `audit` table for create/update/delete + rule firings
* **Files:** Store uploads in `/uploads/home/` with hashed filenames + metadata

**New/Optional deps:**

* `Pillow` (image resizing/EXIF for photos)
* `python-dateutil` (recurrence parsing, already in health plan)
* *(Optional, web)* QuaggaJS in UI for barcode/serial capture; ExifReader for orientation.

---

## 🗃️ Data Model (SQLAlchemy sketch)

> Keep it modular—"atoms" that compose workflows. Add `created_at/updated_at`, soft‑delete flags, and indexes on foreign keys / timestamps.

**Core:**

* `Location` (room/zone) — id, name, parent\_id
* `Asset` (appliance/tool/fixture) — id, name, type, brand, model, serial, purchase\_date, purchase\_price, location\_id, notes
* `Manual` — id, asset\_id, file\_id, url, note
* `Warranty` — id, asset\_id, provider, policy\_no, start\_date, end\_date, coverage\_note, claim\_steps
* `MaintenancePlan` — id, asset\_id (nullable), title, cadence (cron/rrule-ish), next\_due, last\_done, checklist\_json
* `MaintenanceEvent` — id, plan\_id, ts, who, notes, cost
* `ChorePlan` — id, title, cadence, location\_id (nullable), next\_due, last\_done, checklist\_json
* `ChoreEvent` — id, plan\_id, ts, who, notes
* `UtilityAccount` — id, provider, service\_type (power/gas/water/internet/trash), account\_no, start\_date, renewal\_date, website, support\_phone, address
* `RateSnapshot` — id, utility\_account\_id, effective\_date, unit\_price, unit\_name, base\_fee
* `OutageReport` — id, utility\_account\_id, start\_ts, end\_ts (nullable), ticket\_no, notes
* `Project` — id, title, scope\_md, status (idea/planning/active/blocked/done), start\_date, due\_date, budget\_estimate, budget\_actual
* `Contractor` — id, name, phone, email, license\_no, insurance\_expires, rating
* `Bid` — id, project\_id, contractor\_id, amount, notes, selected (bool)
* `InventoryItem` — id, name, category, location\_id, qty, unit, par\_level, expiry\_date, photo\_file\_id, notes
* `PestLawnPlan` — id, title, service\_type (pest/lawn/tree), cadence, provider (nullable), next\_due, last\_done
* `PestLawnEvent` — id, plan\_id, ts, product\_used, notes, cost
* `SafetyDevice` — id, type (smoke/CO/extinguisher/first\_aid), location\_id, model, purchase\_date, expiry\_date (e.g., extinguisher), test\_cadence, next\_test\_due, last\_test
* `SafetyDrill` — id, title, cadence, next\_due, last\_done, notes
* `EmergencyKit` — id, location\_id, contents\_json, last\_audited, next\_audit\_due

**Relationships & indices:**

* Index `(plan_id, ts)` on event tables; `(asset_id)` on plan/warranty/manual; `(utility_account_id, effective_date)` on rates.

---

## 🧠 Service Layer

`HomeService(db)` encapsulates business logic:

* Plans: `create_plan`, `schedule_next_due`, `log_event`, `complete_checklist` (validates steps)
* Assets: `register_asset`, `attach_manual`, `add_warranty`, `flag_expiring_warranties`
* Utilities: `add_utility_account`, `snapshot_rate`, `log_outage`
* Projects: `create_project`, `add_bid`, `select_bid`, `log_expense`
* Inventory: `low_stock_list`, `reorder_suggest`
* Safety: `test_due_devices`, `record_safety_test`, `kit_audit`
* Common: `upcoming_due(range)`, `overdue()`, `search(q)`

---

## 🔌 API Blueprint (v0 → v1)

**Base path:** `/home`

**v0 (CRUD essentials + due logic)**

* `GET /dashboard` → tiles data (today/this week due; overdue counts)
* Assets: `GET/POST /assets`, `GET/PUT/DELETE /assets/{id}`
* Manuals & warranties: `POST /assets/{id}/manuals`, `POST /assets/{id}/warranties`
* Maintenance: `GET/POST /maintenance/plans`, `POST /maintenance/plans/{id}/events`, `POST /maintenance/plans/{id}/schedule_next`
* Chores: `GET/POST /chores/plans`, `POST /chores/plans/{id}/events`
* Utilities: `GET/POST /utilities/accounts`, `POST /utilities/{id}/rates`, `POST /utilities/{id}/outages`
* Safety: `GET/POST /safety/devices`, `POST /safety/devices/{id}/test`

**v1 (projects, inventory, pest/lawn, exports)**

* Projects: `GET/POST /projects`, `POST /projects/{id}/bids`, `POST /projects/{id}/select_bid`, `POST /projects/{id}/events`
* Inventory: `GET/POST /inventory/items`, `GET /inventory/low_stock`
* Pest/Lawn: `GET/POST /pestlawn/plans`, `POST /pestlawn/plans/{id}/events`
* Export: `GET /export/csv?scope=<assets|maintenance|inventory|...>`

**v2 (nice‑to‑have)**

* Attach photos from camera; barcode/serial scan; recall lookup stubs; calendar webhooks.

---

## 🧩 UI / UX

**Dashboard layout**

```
┌─────────────────────────────────────────────────────────┐
│ Home Dashboard                                          │
├───────────────┬───────────────────────┬─────────────────┤
│ Due This Week │ Overdue               │ Safety Readiness │
│ (plans+chores)│ (count + quick actions)│ (tests/expiries)│
├───────────────┼───────────────────────┼─────────────────┤
│ Assets &      │ Utilities             │ Projects        │
│ Warranties    │ (rates, renewals)     │ (budget status) │
├───────────────┴───────────────────────┴─────────────────┤
│ Inventory (low stock) • Pest/Lawn schedule • Activity log│
└─────────────────────────────────────────────────────────┘
```

**Key screens**

* **Assets**: table (name, type, location, serial, warranty end), detail pane with manuals & plans; quick photo attach.
* **Maintenance & Chores**: calendar + list views; complete with checklist; snooze/skip with reason.
* **Utilities**: provider cards (account, rate snapshots, renewal date, support links), outage log.
* **Projects**: kanban (idea/planning/active/blocked/done); budget vs actual; contractors & bids.
* **Inventory**: location grid (garage/kitchen/etc.), low‑stock list → add to errands.
* **Safety**: detectors/drills/kits with next‑due; “Run drill” flow generates checklist and log.

**Micro‑interactions**

* Quick Add (`q`) opens omnibox: “log filter change for HVAC”, “add asset Washer model WFW9620”, “test bedroom smoke alarm”.
* Keyboard shortcuts: `n` new asset; `.` quick log; `/` search.
* Inline toasts with undo; badges for overdue.

---

## ✅ Phased Delivery

### Phase 1 — Core Infra & Essentials (Week 1–2)

**DB & Models**

* [x] Create core models: `Location`, `Asset`, `Manual`, `Warranty`, `MaintenancePlan`, `MaintenanceEvent`, `ChorePlan`, `ChoreEvent`, `SafetyDevice`
* [x] Add indices; timestamps; soft‑delete (migrations 0017, 0018 applied)
* [ ] Add missing timestamps to models (updated_at, archived_at)

**Service Layer**

* [x] `HomeService` scaffold with placeholder CRUD endpoints (in-memory)
* [x] **SLICE 1**: Switch `HomeService` to SQLAlchemy models + DB (assets CRUD first) ✅ **COMPLETED**
* [x] **SLICE 2**: Maintenance plans CRUD + basic scheduling ✅ **COMPLETED**
* [x] **SLICE 3**: Chores CRUD + basic scheduling ✅ **COMPLETED**
* [x] **SLICE 4**: Safety devices CRUD + test recording ✅ **COMPLETED**
* [x] **SLICE 5**: Manuals & warranties CRUD ✅ **COMPLETED**
* [x] Warranty expiry detection ✅ **COMPLETED**

**API (v0)**

* [x] CRUD for assets, plans (maintenance + chores) — placeholder in-memory
* [x] Dashboard tiles endpoint (HTML + JSON)
* [x] Safety device test endpoint (scaffold)
* [x] **SLICE 1**: Assets CRUD endpoints fully DB-backed ✅ **COMPLETED**
* [x] **SLICE 2**: Maintenance plans CRUD endpoints fully DB-backed ✅ **COMPLETED**
* [x] **SLICE 3**: Chores CRUD endpoints fully DB-backed ✅ **COMPLETED**
* [x] **SLICE 4**: Safety devices CRUD endpoints fully DB-backed ✅ **COMPLETED**
* [x] **SLICE 5**: Manuals & warranties CRUD endpoints fully DB-backed ✅ **COMPLETED**

**UI**

* [x] Home Dashboard (Due This Week, Overdue, Safety Readiness) — basic tiles
* [x] **SLICE 1**: Assets table + detail forms (CRUD working) ✅ **COMPLETED**
* [x] **SLICE 2**: Maintenance plans list + forms (CRUD working) ✅ **COMPLETED**
* [x] **SLICE 3**: Chores list + forms (CRUD working) ✅ **COMPLETED**
* [x] **SLICE 4**: Safety devices list + forms (CRUD working) ✅ **COMPLETED**
* [x] **SLICE 5**: Manuals & warranties forms (CRUD working) ✅ **COMPLETED**

**Testing**

* [x] **SLICE 1**: Unit tests for Asset model & CRUD operations ✅ **COMPLETED** (models updated with timestamps)
* [x] **SLICE 2**: Unit tests for Maintenance models & CRUD operations ✅ **COMPLETED** (models updated with timestamps)
* [x] **SLICE 3**: Unit tests for Chore models & CRUD operations ✅ **COMPLETED** (models updated with timestamps)
* [x] **SLICE 4**: Unit tests for Safety models & CRUD operations ✅ **COMPLETED** (models updated with timestamps)
* [x] **SLICE 5**: Unit tests for Manual/Warranty models & CRUD operations ✅ **COMPLETED** (models updated with timestamps)

### Phase 2 — Utilities, Inventory, Safety (Week 3)

**DB**

* [x] `UtilityAccount`, `RateSnapshot`, `OutageReport` (schema)
* [x] `InventoryItem`, `EmergencyKit`, `SafetyDrill` (schema)

**API/UI**

* [x] **SLICE 1**: Utilities cards (rates, renewals, outages) ✅ **COMPLETED**
* [x] **SLICE 2**: Inventory location grid + low‑stock tile ✅ **COMPLETED**
* [x] **SLICE 3**: Safety drills flow + kit audit ✅ **COMPLETED**

**Dashboard Integration**
* [x] Safety drills & emergency kits counts in main dashboard ✅ **COMPLETED**

**Exports**

* [x] **SLICE 4**: CSV export for assets, maintenance events, inventory ✅ **COMPLETED**

**Testing**

* [ ] **SLICE 5**: Integration tests (end‑to‑end logging, export)

### Phase 3 — Projects & Pest/Lawn (Week 4)

**DB**

* [x] `Project`, `Contractor`, `Bid`, `PestLawnPlan`, `PestLawnEvent` (schema)

**API/UI**

* [ ] Projects kanban + budgets + bids
* [ ] Pest & lawn schedule (seasonal presets); provider log
* [ ] Search & filters; mobile optimizations

**Nice‑to‑haves**

* [ ] Camera capture for serials/photos; barcode scan (JS)
* [ ] Chart tiles (Chart.js) for spend, task trends

---

## 🧪 Testing Strategy

**Unit** — Model validations, schedule calculations (next\_due, overdue), warranty expiry logic, low‑stock detector.
**API** — CRUD, list filters, pagination, exports.
**UI** — Form validation, keyboard shortcuts, quick‑log flows.
**Fixtures** — Example assets (HVAC, Washer, Fridge), plans (filters, gutters), utilities (power/internet), safety devices (smoke/CO), inventory (filters, batteries).

**Coverage targets:** overall ≥ 70% by v0; ≥ 85% for home domain by v1.

---

## 🔐 Security & Privacy

* Local‑first storage; PII minimized (contractor contacts).
* Audit logging for data changes and file downloads.
* CSRF protection; XSS‑safe rendering; input sanitization.
* Role‑ready for shared household later (v2).

---

## ⚙️ Performance

* Index on `(next_due)`, `(location_id)`, `(asset_id)`; paginate tables.
* Debounced search; lazy‑load images; image resize on upload.
* Cache dashboard tiles for 30–60s.

---

## 📦 Migrations & Data Hygiene

* Add `created_at/updated_at/archived_at` to all tables.
* Backfill `next_due` on import; denormalize a `due_status` for fast dashboards.
* Validation scripts for serial formats, date ranges.

---

## 📈 Success Metrics (by v1)

* On‑time maintenance ≥ 85%; overdue tasks cleared within 72h.
* 0 missed warranty expirations; 100% of big assets have manuals attached.
* Safety devices all tested within cadence month.
* Inventory low‑stock → errands list within 24h.

---

## 🧨 Risks & Mitigations

* **Image bloat** → Resize + webp; disk quota; background cleanup.
* **Schedule drift/timezones** → store UTC + local; rrule tests.
* **Over‑complexity** → ship presets: seasonal packs; common assets starter set.
* **Data entry friction** → quick‑log, defaults, templates, keyboard paths.

---

## 🧭 Next Steps (this month)

1. Assets: convert manuals/warranties to DB-backed; add UI controls on Assets page; add warranty expiry flag on dashboard tile.
2. Safety: make device Create/Test fully DB-backed; show due/overdue counts in dashboard; add simple devices list UI.
3. Utilities: endpoints and UI for accounts, rate snapshots, and outages; show renewal date and most recent rate on dashboard.
4. Inventory: endpoints and UI; compute low‑stock list; add low‑stock tile.
5. Maintenance & Chores: add quick-complete in list pages; optional snooze; compute upcoming/overdue ranges for dashboard.
6. Projects: minimal CRUD with bids and selection; basic kanban view.
7. Pest/Lawn: CRUD and events; seasonal presets.
8. Exports: CSV for assets and maintenance events.
9. Tests: unit tests for scheduling and warranty expiry; API tests for Home CRUD; fixtures for demo data.

---

## ❓ Open Questions

1. Single vs multi‑home support? (schema: add `home_id` now?)
2. Project budgets: multi‑currency needed? tax handling?
3. Inventory: track cost‑per‑use or just qty/expiry?
4. Utilities: pull outages via integration later, or manual only?
5. Attachments: store in DB (BLOB) vs filesystem (path)?
6. Should maintenance completion auto‑shift next\_due or use fixed calendar cadence? (support both)

---

## 🧩 Example Model Snippets

```python
# app/domains/home/models.py
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Float, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Location(Base):
    __tablename__ = 'location'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    parent_id = Column(Integer, ForeignKey('location.id'))
    created_at = Column(DateTime, server_default=func.now())

class Asset(Base):
    __tablename__ = 'asset'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(80))
    brand = Column(String(120))
    model = Column(String(120))
    serial = Column(String(120))
    purchase_date = Column(Date)
    purchase_price = Column(Float)
    location_id = Column(Integer, ForeignKey('location.id'))
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class MaintenancePlan(Base):
    __tablename__ = 'maintenance_plan'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    asset_id = Column(Integer, ForeignKey('asset.id'))
    cadence = Column(String(120), nullable=False)  # e.g., "RRULE:FREQ=MONTHLY;BYDAY=1SU"
    next_due = Column(Date)
    last_done = Column(Date)
    checklist_json = Column(Text)

class MaintenanceEvent(Base):
    __tablename__ = 'maintenance_event'
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('maintenance_plan.id'), nullable=False)
    ts = Column(DateTime, server_default=func.now())
    notes = Column(Text)
    cost = Column(Float)
```

---

**End of plan.**
