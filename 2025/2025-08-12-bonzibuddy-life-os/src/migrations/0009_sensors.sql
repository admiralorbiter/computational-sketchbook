BEGIN;

CREATE TABLE IF NOT EXISTS sensor_type (
  id INTEGER PRIMARY KEY,
  key TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  wear_days INTEGER NOT NULL DEFAULT 15,
  pack_size INTEGER NOT NULL DEFAULT 2,
  default_lead_time_days INTEGER NOT NULL DEFAULT 7,
  default_reminder_days INTEGER NOT NULL DEFAULT 3,
  safety_stock INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS sensor_use (
  id INTEGER PRIMARY KEY,
  type_key TEXT NOT NULL,
  start_ts TEXT NOT NULL,
  end_ts_expected TEXT,
  end_ts_actual TEXT,
  note TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(type_key) REFERENCES sensor_type(key)
);

CREATE TABLE IF NOT EXISTS sensor_inventory (
  id INTEGER PRIMARY KEY,
  type_key TEXT NOT NULL,
  ts TEXT NOT NULL DEFAULT (datetime('now')),
  delta_sensors INTEGER NOT NULL,
  source TEXT NOT NULL,
  note TEXT,
  FOREIGN KEY(type_key) REFERENCES sensor_type(key)
);

-- Seed Stelo CGM sensor type
INSERT OR IGNORE INTO sensor_type(key, label, wear_days, pack_size, default_lead_time_days, default_reminder_days, safety_stock)
VALUES ('stelo_cgm', 'Stelo CGM', 15, 2, 7, 3, 1);

INSERT INTO schema_version(version, applied_at) VALUES (9, CURRENT_TIMESTAMP);

COMMIT;

