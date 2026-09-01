BEGIN;
CREATE TABLE med (id INTEGER PRIMARY KEY, name TEXT NOT NULL, dose_text TEXT, notes TEXT);
CREATE TABLE med_event (id INTEGER PRIMARY KEY, med_id INTEGER NOT NULL, ts TEXT NOT NULL, amount REAL, note TEXT,
  FOREIGN KEY(med_id) REFERENCES med(id));
CREATE TABLE symptom_log (id INTEGER PRIMARY KEY, ts TEXT NOT NULL, label TEXT NOT NULL, severity INTEGER, trigger TEXT, note TEXT);
CREATE TABLE vital (id INTEGER PRIMARY KEY, ts TEXT NOT NULL, kind TEXT NOT NULL, value_num REAL, unit TEXT, note TEXT);
CREATE TABLE appointment (id INTEGER PRIMARY KEY, ts TEXT NOT NULL, provider TEXT, location TEXT, purpose TEXT, note TEXT);
INSERT INTO schema_version(version, applied_at) VALUES (2, CURRENT_TIMESTAMP);
COMMIT;
