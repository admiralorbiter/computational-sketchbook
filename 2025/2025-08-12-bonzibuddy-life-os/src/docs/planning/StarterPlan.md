# 30‑Day Starter Plan (source of truth)

## Success criteria (v0)
- CRUD for Health, Hobbies, Research
- Manual migration pipeline working
- Basic dashboards & lists
- Tests running in CI; pre‑commit passing

## Sprint 1 (Week 1)
- Repo scaffolding & venv; Bootstrap/Alpine wired
- Core data layer (`db.py`), app factory, blueprint stubs
- Migration 0001_init.sql: schema_version, profile, tag, attachment
- Smoke tests, CI stub, pre‑commit

## Sprint 2 (Week 2)
- Health v0: meds, symptoms, vitals; forms + list/detail
- Migration 0002_health_basics.sql
- ADRs for Health decisions

## Sprint 3 (Week 3)
- Hobbies v0: projects, sessions (generic practice sessions)
- Migration 0003_hobbies_basics.sql
- Dashboards: recent sessions, streaks

## Sprint 4 (Week 4)
- Research v0: questions, sources, notes, highlights
- Migration 0004_research_basics.sql
- Import/export (CSV/JSON) basics; backup/restore runbook
- Cut a v0 tag (optional)

## Cadence & rituals
- Daily: 10‑min standup note; Evening quick review
- Weekly: Sprint review + retro; Update Starter Plan
