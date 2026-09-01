# Student Projects — Software Apprenticeship & Simulated Engineering Hub (October 2025)

> **Category:** `[SKETCHBOOK EXPERIMENT / CS EDTECH & APPRENTICESHIP DESIGN]`  
> **Date:** October 6, 2025  
> **Stack:** Static HTML5, CSS3, JavaScript (Classroom Microsite), JSON, Markdown  
> **Original Origin:** `admiralorbiter/student-projects` (HEAD: `0ac15cc`)  

---

## 1. Project Purpose & Scope

*Student Projects* is an educational curriculum design blueprint and project scaffolding hub created to simulate professional software engineering team workflows for student developers.

> [!IMPORTANT]
> **Curriculum & Project Hub Specification (Not Target Application Code):**  
> This artifact contains the **instructional scaffolding environment**—sprint guides, API contracts, Architecture Decision Records (ADRs), database schemas, role matrices, and risk registers. It does *not* contain the GradeBridge application source code.

---

## 2. The Two Instructional Models Preserved

```text
THE INSTRUCTIONAL PROGRESSION
================================================================================
Model A: Bounded Browser Projects (`other-projects/`)
   "4 students × 4 weeks × small browser application (Grade Calculator, Countdown Timer)."
   ├── Role breakdown: Frontend, Core Logic, Data Manager, Polish
   └── Focus: LocalStorage, DOM manipulation, code standards, demo rubrics
                       │
                       ▼
Model B: Simulated Software Organization (GradeBridge Hub)
   "3–4 students × 6 sprints (18 weeks) × full-stack multi-school grade management platform."
   ├── Organizational Artifacts: ADRs, API Contracts, Risk Register, Test Plans, Sprint Gates
   └── Engineering Scope: Node/Express, SQLite/Postgres parity, RBAC, session auth, migrations
```

---

## 3. Core Pedagogical Breakthrough: Software as Decisions, Not Just Code

1. **Exposing Invisible Professional Artifacts:** Students engage with real engineering decision artifacts:
   - **Architectural Decision Records (ADRs):** Explicitly weighing trade-offs (e.g., Node/Express with vanilla templates to avoid SPA state complexity at the cost of manual DOM rendering).
   - **Risk Registers:** Identifying real operational vulnerabilities (scope creep, RBAC multi-tenant data leakage, database migration drift).
   - **API Contracts & Test Scenarios:** Pre-specifying expected HTTP responses and authorization failure states before writing code.
2. **The Lineage Bridge to Synthetic Practice Environments:**
   - *Observation:* Over-scripting ticket implementations risks turning students into passive ticket-completers.
   - *Evolution:* Serves as a direct conceptual ancestor to modern **synthetic workplace / rehearsal environments**—moving from static instruction toward *simulation by consequence* (responsive stakeholder feedback, PR reviews, and dynamic runtime constraints).
