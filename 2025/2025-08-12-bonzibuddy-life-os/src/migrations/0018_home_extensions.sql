BEGIN;

-- Utilities & services
CREATE TABLE IF NOT EXISTS utility_account (
  id INTEGER PRIMARY KEY,
  provider TEXT NOT NULL,
  service_type TEXT NOT NULL,
  account_no TEXT,
  start_date TEXT,
  renewal_date TEXT,
  website TEXT,
  support_phone TEXT,
  address TEXT
);

CREATE TABLE IF NOT EXISTS rate_snapshot (
  id INTEGER PRIMARY KEY,
  utility_account_id INTEGER NOT NULL,
  effective_date TEXT NOT NULL,
  unit_price REAL,
  unit_name TEXT,
  base_fee REAL,
  FOREIGN KEY(utility_account_id) REFERENCES utility_account(id)
);
CREATE INDEX IF NOT EXISTS idx_rate_snapshot_account_date ON rate_snapshot(utility_account_id, effective_date);

CREATE TABLE IF NOT EXISTS outage_report (
  id INTEGER PRIMARY KEY,
  utility_account_id INTEGER NOT NULL,
  start_ts TEXT NOT NULL,
  end_ts TEXT,
  ticket_no TEXT,
  notes TEXT,
  FOREIGN KEY(utility_account_id) REFERENCES utility_account(id)
);

-- Projects & contractors
CREATE TABLE IF NOT EXISTS project (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  scope_md TEXT,
  status TEXT,
  start_date TEXT,
  due_date TEXT,
  budget_estimate REAL,
  budget_actual REAL
);

CREATE TABLE IF NOT EXISTS contractor (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  license_no TEXT,
  insurance_expires TEXT,
  rating REAL
);

CREATE TABLE IF NOT EXISTS bid (
  id INTEGER PRIMARY KEY,
  project_id INTEGER NOT NULL,
  contractor_id INTEGER NOT NULL,
  amount REAL,
  notes TEXT,
  selected INTEGER DEFAULT 0,
  FOREIGN KEY(project_id) REFERENCES project(id),
  FOREIGN KEY(contractor_id) REFERENCES contractor(id)
);
CREATE INDEX IF NOT EXISTS idx_bid_project ON bid(project_id);

-- Inventory
CREATE TABLE IF NOT EXISTS inventory_item (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  location_id INTEGER,
  qty REAL,
  unit TEXT,
  par_level REAL,
  expiry_date TEXT,
  photo_path TEXT,
  notes TEXT,
  FOREIGN KEY(location_id) REFERENCES location(id)
);
CREATE INDEX IF NOT EXISTS idx_inventory_location ON inventory_item(location_id);

-- Pest & Lawn
CREATE TABLE IF NOT EXISTS pestlawn_plan (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  service_type TEXT,
  cadence TEXT,
  provider TEXT,
  next_due TEXT,
  last_done TEXT
);

CREATE TABLE IF NOT EXISTS pestlawn_event (
  id INTEGER PRIMARY KEY,
  plan_id INTEGER NOT NULL,
  ts TEXT NOT NULL,
  product_used TEXT,
  notes TEXT,
  cost REAL,
  FOREIGN KEY(plan_id) REFERENCES pestlawn_plan(id)
);
CREATE INDEX IF NOT EXISTS idx_pestlawn_event_plan_ts ON pestlawn_event(plan_id, ts);

-- Safety drills & emergency kits
CREATE TABLE IF NOT EXISTS safety_drill (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  cadence TEXT,
  next_due TEXT,
  last_done TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS emergency_kit (
  id INTEGER PRIMARY KEY,
  location_id INTEGER,
  contents_json TEXT,
  last_audited TEXT,
  next_audit_due TEXT,
  FOREIGN KEY(location_id) REFERENCES location(id)
);

INSERT INTO schema_version(version, applied_at) VALUES (18, CURRENT_TIMESTAMP);

COMMIT;


