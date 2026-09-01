# Architecture

## Overview
Modular monolith in Flask. Domains (Health, Hobbies, Research) live in `app/domains/<name>` with `models.py`, `services.py`, `views.py`, `forms.py`. Single‑user, local‑first.

## App factory & Blueprints
- `create_app()` wires config, db, blueprints under `/` and `/api/v1/*`.
- Templating with Jinja; Bootstrap components; Alpine.js for interactivity.

## Data access
- SQLAlchemy Core/ORM for models and queries.
- **Manual migrations**: SQL files in `/migrations`, applied by `scripts/db_apply.py`. Track version in `schema_version` table.

## Authentication
- Local session cookie only (optional). No external auth.

## API
- Internal JSON endpoints under `/api/v1` for dynamic pages. No public auth yet.

## Observability & audit
- Structured logs to file; lightweight `audit` table for key actions.

## Extensibility
- New domain = new folder with the four files; register blueprint.
- Integrations (e.g., Oura, diabetes CGM) later via ETL jobs or CSV import.
- Research domain mirrors Health structure with v0 minimal HTML + JSON API, expanding to FTS and importers. Shared components: `tag/tag_map`, `attachment/attachment_map`, audit logging.

### Home & Property Domain
- Scaffolded with `app/domains/home/` providing `views.py`, `services.py`, `models.py` (placeholder) and UI at `app/ui/templates/home/*`.
- Routes mounted under `/home` with a dashboard HTML and JSON endpoint, plus placeholder CRUD for assets and maintenance plans. Backed by in-memory structures temporarily; to be replaced with SQLAlchemy models per `planning/HomePropImplementationPlan.md`.