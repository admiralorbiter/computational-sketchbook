BEGIN;

CREATE TABLE IF NOT EXISTS lab_order (
  id INTEGER PRIMARY KEY,
  appointment_id INTEGER,
  label TEXT NOT NULL,
  kind TEXT,
  provider TEXT,
  location TEXT,
  instructions TEXT,
  status TEXT DEFAULT 'ordered', -- ordered|scheduled|completed|canceled
  ordered_ts TEXT DEFAULT (datetime('now')),
  scheduled_ts TEXT,
  due_ts TEXT,
  completed_ts TEXT,
  reminder_days INTEGER,
  result_note TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(appointment_id) REFERENCES appointment(id) ON DELETE SET NULL
);

INSERT INTO schema_version(version, applied_at) VALUES (8, CURRENT_TIMESTAMP);

COMMIT;

