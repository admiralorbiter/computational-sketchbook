BEGIN;
CREATE TABLE project (id INTEGER PRIMARY KEY, domain TEXT, title TEXT NOT NULL, status TEXT, started_at TEXT, note TEXT);
CREATE TABLE session (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, ts_start TEXT NOT NULL, ts_end TEXT, focus TEXT, quality INTEGER, note TEXT,
  FOREIGN KEY(project_id) REFERENCES project(id));
CREATE TABLE milestone (id INTEGER PRIMARY KEY, project_id INTEGER NOT NULL, title TEXT NOT NULL, due_date TEXT, done INTEGER DEFAULT 0,
  FOREIGN KEY(project_id) REFERENCES project(id));
INSERT INTO schema_version(version, applied_at) VALUES (3, CURRENT_TIMESTAMP);
COMMIT;
