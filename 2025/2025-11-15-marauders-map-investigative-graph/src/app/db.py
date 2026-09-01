from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, g


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        db_path = g.app.config["DATABASE_PATH"]  # type: ignore[attr-defined]
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db  # type: ignore[return-value]


def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app: Flask) -> None:
    @app.before_request
    def attach_app_to_g() -> None:  # type: ignore[override]
        g.app = app

    @app.teardown_appcontext
    def teardown(exception: Exception | None) -> None:  # type: ignore[override]
        close_db(exception)

    db_path = Path(app.config["DATABASE_PATH"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        _initialize_schema(db_path)
    else:
        _migrate_schema(db_path)


def _initialize_schema(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                is_deleted INTEGER NOT NULL DEFAULT 0,
                lat REAL,
                lng REAL,
                location_label TEXT
            );

            -- Reserve a place for FTS5; Slice 1 can flesh this out.
            CREATE VIRTUAL TABLE IF NOT EXISTS entities_fts
            USING fts5(name, content='entities', content_rowid='id');

            CREATE TRIGGER IF NOT EXISTS entities_ai
            AFTER INSERT ON entities
            WHEN new.is_deleted = 0
            BEGIN
                INSERT INTO entities_fts(rowid, name)
                VALUES (new.id, new.name);
            END;

            CREATE TRIGGER IF NOT EXISTS entities_au
            AFTER UPDATE OF name, is_deleted ON entities
            BEGIN
                DELETE FROM entities_fts WHERE rowid = new.id;
                INSERT INTO entities_fts(rowid, name)
                SELECT new.id, new.name WHERE new.is_deleted = 0;
            END;

            CREATE TABLE relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                role TEXT,
                start_date TEXT,
                end_date TEXT,
                is_current INTEGER NOT NULL DEFAULT 1,
                strength INTEGER,
                confidence INTEGER,
                provenance_json TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                is_deleted INTEGER NOT NULL DEFAULT 0,
                CHECK (source_id != target_id),
                FOREIGN KEY (source_id) REFERENCES entities(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES entities(id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def _migrate_schema(db_path: Path) -> None:
    """Best-effort migration for dev/test.

    Adds new columns for entities and creates the relationships table
    if they are missing, then (re)creates the FTS triggers.
    """
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(entities);")
        cols = {row[1] for row in cur.fetchall()}

        if "updated_at" not in cols:
            cur.execute("ALTER TABLE entities ADD COLUMN updated_at TEXT;")
        if "is_deleted" not in cols:
            cur.execute(
                "ALTER TABLE entities ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0;"
            )
        if "lat" not in cols:
            cur.execute("ALTER TABLE entities ADD COLUMN lat REAL;")
        if "lng" not in cols:
            cur.execute("ALTER TABLE entities ADD COLUMN lng REAL;")
        if "location_label" not in cols:
            cur.execute("ALTER TABLE entities ADD COLUMN location_label TEXT;")

        # Ensure relationships table exists
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                target_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                role TEXT,
                start_date TEXT,
                end_date TEXT,
                is_current INTEGER NOT NULL DEFAULT 1,
                strength INTEGER,
                confidence INTEGER,
                provenance_json TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                is_deleted INTEGER NOT NULL DEFAULT 0,
                CHECK (source_id != target_id),
                FOREIGN KEY (source_id) REFERENCES entities(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES entities(id) ON DELETE CASCADE
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS entities_fts
            USING fts5(name, content='entities', content_rowid='id');

            DROP TRIGGER IF EXISTS entities_ai;
            DROP TRIGGER IF EXISTS entities_au;

            CREATE TRIGGER entities_ai
            AFTER INSERT ON entities
            WHEN new.is_deleted = 0
            BEGIN
                INSERT INTO entities_fts(rowid, name)
                VALUES (new.id, new.name);
            END;

            CREATE TRIGGER entities_au
            AFTER UPDATE OF name, is_deleted ON entities
            BEGIN
                DELETE FROM entities_fts WHERE rowid = new.id;
                INSERT INTO entities_fts(rowid, name)
                SELECT new.id, new.name WHERE new.is_deleted = 0;
            END;
            """
        )
        conn.commit()
    finally:
        conn.close()

