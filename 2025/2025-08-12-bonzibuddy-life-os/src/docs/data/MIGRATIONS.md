# Manual Migrations

## Strategy
- SQL files in `/migrations/NNNN_desc.sql`
- `schema_version(version)` tracks last applied number
- `scripts/db_apply.py` applies files > current version inside a transaction

## 0001_init.sql
- Create schema_version, profile, tag, attachment, audit

## 0002_health_basics.sql
- med, med_event, symptom_log, vital, appointment

## 0003_hobbies_basics.sql
- project, session, milestone

## 0004_research_basics.sql
- question, source, note, highlight
