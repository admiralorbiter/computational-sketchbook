BEGIN;

-- Extend appointments table with richer fields
ALTER TABLE appointment ADD COLUMN specialty TEXT;
ALTER TABLE appointment ADD COLUMN is_virtual INTEGER DEFAULT 0; -- 0/1
ALTER TABLE appointment ADD COLUMN status TEXT DEFAULT 'planned'; -- planned|completed|canceled|rescheduled
ALTER TABLE appointment ADD COLUMN reminder_days INTEGER; -- days before to remind
ALTER TABLE appointment ADD COLUMN follow_up_ts TEXT; -- ISO text
ALTER TABLE appointment ADD COLUMN lab_due_ts TEXT; -- ISO text

-- Tasks for appointments
CREATE TABLE IF NOT EXISTS appointment_task (
  id INTEGER PRIMARY KEY,
  appointment_id INTEGER NOT NULL,
  label TEXT NOT NULL,
  due_ts TEXT,
  done INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(appointment_id) REFERENCES appointment(id) ON DELETE CASCADE
);

INSERT INTO schema_version(version, applied_at) VALUES (7, CURRENT_TIMESTAMP);

COMMIT;

