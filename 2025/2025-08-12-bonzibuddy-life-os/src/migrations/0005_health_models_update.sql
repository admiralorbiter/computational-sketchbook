BEGIN;

-- Add missing columns to med table
ALTER TABLE med ADD COLUMN created_at TEXT DEFAULT (datetime('now'));

-- Add missing columns to med_event table  
ALTER TABLE med_event ADD COLUMN created_at TEXT DEFAULT (datetime('now'));

-- Add missing columns to symptom_log table
ALTER TABLE symptom_log ADD COLUMN created_at TEXT DEFAULT (datetime('now'));

-- Add missing columns to vital table
ALTER TABLE vital ADD COLUMN created_at TEXT DEFAULT (datetime('now'));

-- Add missing columns to appointment table
ALTER TABLE appointment ADD COLUMN created_at TEXT DEFAULT (datetime('now'));

-- Update schema version
INSERT INTO schema_version(version, applied_at) VALUES (5, CURRENT_TIMESTAMP);

COMMIT;
