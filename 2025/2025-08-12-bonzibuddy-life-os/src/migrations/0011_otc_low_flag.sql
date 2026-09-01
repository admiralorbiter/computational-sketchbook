BEGIN;

ALTER TABLE med ADD COLUMN is_low INTEGER DEFAULT 0; -- boolean flag for OTC low reminder

INSERT INTO schema_version(version, applied_at) VALUES (11, CURRENT_TIMESTAMP);

COMMIT;

