BEGIN;

-- Extend medications to support prescriptions data
ALTER TABLE med ADD COLUMN dosage TEXT;                 -- e.g., "50 mg"
ALTER TABLE med ADD COLUMN qty INTEGER;                 -- total quantity dispensed
ALTER TABLE med ADD COLUMN refills_left INTEGER;        -- remaining refills
ALTER TABLE med ADD COLUMN last_refilled TEXT;          -- ISO timestamp (or DATE stored as TEXT)
ALTER TABLE med ADD COLUMN qty_per_day REAL;            -- doses per day (for adherence)
ALTER TABLE med ADD COLUMN condition TEXT;              -- condition treated
ALTER TABLE med ADD COLUMN pharmacy TEXT;               -- dispensing pharmacy

-- Update schema version
INSERT INTO schema_version(version, applied_at) VALUES (6, CURRENT_TIMESTAMP);

COMMIT;

