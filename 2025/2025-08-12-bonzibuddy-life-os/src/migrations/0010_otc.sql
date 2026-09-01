BEGIN;

-- Add OTC fields to med
ALTER TABLE med ADD COLUMN is_otc INTEGER DEFAULT 0; -- 0/1
ALTER TABLE med ADD COLUMN on_hand_qty REAL DEFAULT 0;
ALTER TABLE med ADD COLUMN unit TEXT; -- e.g., tabs, mL
ALTER TABLE med ADD COLUMN low_threshold REAL DEFAULT 0;

INSERT INTO schema_version(version, applied_at) VALUES (10, CURRENT_TIMESTAMP);

COMMIT;

