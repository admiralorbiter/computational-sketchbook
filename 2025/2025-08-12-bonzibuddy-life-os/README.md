# BonziBuddy — Multi-Domain Life OS & State Externalization Prototype (August 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / MAJOR COGNITIVE ANCESTOR]`  
> **Date:** August 12–16, 2025 (~4 days, 24 commits)  
> **Stack:** Python 3, Flask, SQLAlchemy, SQLite, Manual Migrations (20+ slices), Bootstrap / Jinja2, Pytest  
> **Original Origin:** `admiralorbiter/bonzibuddy`  

---

## 1. The Core Thesis & Historical Significance

*BonziBuddy* is the seminal ancestor in your engineering lineage for **externalizing the recurring state of a life**.

Defined in [`phil_and_playbook.md`](src/docs/phil_and_playbook.md) as:
> *"A scalable, extensible, private-by-default life OS that helps Future You win."*

### The North Star:
> *"Did this reduce cognitive load and increase follow-through?"*

```text
LIVED ACTIVITY / RECURRING OBLIGATION
                 │
                 ▼
SACRED LOW-FRICTION CAPTURE
                 │
                 ▼
NORMALIZED DATABASE SUBSTRATE ("One Truth, Many Views")
                 │
                 ▼
DOMAIN ENGINES (Health, Research Evidence, Household Maintenance)
                 │
                 ▼
FUTURE YOU OPERATIONAL ADVANTAGE (Zero Reconstructive Cognitive Tax)
```

---

## 2. Implemented Functional Domains vs. Revealed Preference

| Domain | Implementation Scope | Evolutionary Reality |
| :--- | :--- | :--- |
| **Health** | **Substantial functional prototype:** Appointments, lab tracking, OTC/prescriptions, CGM, Oura API schema, time-series dashboards, unit tests. | First operational proof of utility. |
| **Research** | **Substantial functional prototype:** Questions ◄► sources ◄► notes/highlights with supporting/refuting/neutral evidence links, CSV ingestion/rollback. | Direct precursor to evidence-grounded research memory graphs. |
| **Home / Property** | **Substantial functional prototype:** Assets, warranties, maintenance schedules, contractors, and visual chore state machines (clean/dirty/hidden toggles). | Designed to eliminate "house brain" load. |
| **Hobbies** | **Blueprint Stub Only:** Planned for Week 3 in the 30-day charter, but never implemented. | **Revealed Preference:** Domains where forgetting carries expensive failure modes commanded all developmental momentum. |

---

## 3. The Architecture vs. Implementation Frontier

- **Conceived Architecture:** A universal graph composed of generic primitives (*Entity, Metric, Log, Task, Project*) powered by shared engines (*Capture, Rules, Review, Reconciliation*).
- **Actual Implementation:** A robust Flask modular monolith sharing an SQLite database and manual migration pipeline across three domain services.
- **Security Boundary:** Designed as a single-user local prototype (unencrypted SQLite, debug server binding `0.0.0.0`, plaintext OAuth token schemas in migrations). Explicitly marked as **unhardened prototype**.
