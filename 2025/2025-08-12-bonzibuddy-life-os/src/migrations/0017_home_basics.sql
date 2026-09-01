BEGIN;

-- Locations (rooms/zones)
CREATE TABLE IF NOT EXISTS location (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  parent_id INTEGER,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(parent_id) REFERENCES location(id)
);

-- Assets (appliances/tools/fixtures)
CREATE TABLE IF NOT EXISTS asset (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT,
  brand TEXT,
  model TEXT,
  serial TEXT,
  purchase_date TEXT,
  purchase_price REAL,
  location_id INTEGER,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(location_id) REFERENCES location(id)
);
CREATE INDEX IF NOT EXISTS idx_asset_location ON asset(location_id);

-- Manuals (file or URL)
CREATE TABLE IF NOT EXISTS manual (
  id INTEGER PRIMARY KEY,
  asset_id INTEGER NOT NULL,
  file_path TEXT,
  url TEXT,
  note TEXT,
  FOREIGN KEY(asset_id) REFERENCES asset(id)
);
CREATE INDEX IF NOT EXISTS idx_manual_asset ON manual(asset_id);

-- Warranties
CREATE TABLE IF NOT EXISTS warranty (
  id INTEGER PRIMARY KEY,
  asset_id INTEGER NOT NULL,
  provider TEXT,
  policy_no TEXT,
  start_date TEXT,
  end_date TEXT,
  coverage_note TEXT,
  claim_steps TEXT,
  FOREIGN KEY(asset_id) REFERENCES asset(id)
);
CREATE INDEX IF NOT EXISTS idx_warranty_asset ON warranty(asset_id);

-- Maintenance planning
CREATE TABLE IF NOT EXISTS maintenance_plan (
  id INTEGER PRIMARY KEY,
  asset_id INTEGER,
  title TEXT NOT NULL,
  cadence TEXT NOT NULL,
  next_due TEXT,
  last_done TEXT,
  checklist_json TEXT,
  FOREIGN KEY(asset_id) REFERENCES asset(id)
);
CREATE INDEX IF NOT EXISTS idx_maint_plan_asset ON maintenance_plan(asset_id);

CREATE TABLE IF NOT EXISTS maintenance_event (
  id INTEGER PRIMARY KEY,
  plan_id INTEGER NOT NULL,
  ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,
  cost REAL,
  FOREIGN KEY(plan_id) REFERENCES maintenance_plan(id)
);
CREATE INDEX IF NOT EXISTS idx_maint_event_plan_ts ON maintenance_event(plan_id, ts);

-- Chores planning
CREATE TABLE IF NOT EXISTS chore_plan (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  cadence TEXT NOT NULL,
  location_id INTEGER,
  next_due TEXT,
  last_done TEXT,
  checklist_json TEXT,
  FOREIGN KEY(location_id) REFERENCES location(id)
);
CREATE INDEX IF NOT EXISTS idx_chore_plan_location ON chore_plan(location_id);

CREATE TABLE IF NOT EXISTS chore_event (
  id INTEGER PRIMARY KEY,
  plan_id INTEGER NOT NULL,
  ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  who TEXT,
  notes TEXT,
  FOREIGN KEY(plan_id) REFERENCES chore_plan(id)
);
CREATE INDEX IF NOT EXISTS idx_chore_event_plan_ts ON chore_event(plan_id, ts);

-- Safety devices
CREATE TABLE IF NOT EXISTS safety_device (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL,
  location_id INTEGER,
  model TEXT,
  purchase_date TEXT,
  expiry_date TEXT,
  test_cadence TEXT,
  next_test_due TEXT,
  last_test TEXT,
  FOREIGN KEY(location_id) REFERENCES location(id)
);
CREATE INDEX IF NOT EXISTS idx_safety_device_location ON safety_device(location_id);

INSERT INTO schema_version(version, applied_at) VALUES (17, CURRENT_TIMESTAMP);

COMMIT;


