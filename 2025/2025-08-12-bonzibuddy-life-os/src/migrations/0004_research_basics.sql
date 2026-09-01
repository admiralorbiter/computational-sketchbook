BEGIN;
CREATE TABLE question (id INTEGER PRIMARY KEY, text TEXT NOT NULL, area TEXT, status TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE source (id INTEGER PRIMARY KEY, kind TEXT, title TEXT, author TEXT, year INTEGER, url TEXT, citation TEXT);
CREATE TABLE note (id INTEGER PRIMARY KEY, source_id INTEGER, question_id INTEGER, ts TEXT DEFAULT CURRENT_TIMESTAMP, body TEXT,
  FOREIGN KEY(source_id) REFERENCES source(id),
  FOREIGN KEY(question_id) REFERENCES question(id));
CREATE TABLE highlight (id INTEGER PRIMARY KEY, source_id INTEGER NOT NULL, location TEXT, text TEXT,
  FOREIGN KEY(source_id) REFERENCES source(id));
INSERT INTO schema_version(version, applied_at) VALUES (4, CURRENT_TIMESTAMP);
COMMIT;
