BEGIN;

-- External links (Google Docs/Sheets and other providers)
CREATE TABLE IF NOT EXISTS external_link (
  id INTEGER PRIMARY KEY,
  entity_type TEXT NOT NULL, -- e.g., 'source','news_event','question'
  entity_id INTEGER NOT NULL,
  provider TEXT NOT NULL,    -- 'google_docs','google_sheets','web'
  kind TEXT,                 -- 'doc','sheet','web'
  title TEXT,
  url TEXT,
  external_id TEXT,          -- doc ID, spreadsheet ID, etc.
  note TEXT,
  added_ts TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_external_link_entity ON external_link(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_external_link_provider ON external_link(provider);
CREATE INDEX IF NOT EXISTS idx_external_link_external_id ON external_link(external_id);

INSERT INTO schema_version(version, applied_at) VALUES (16, CURRENT_TIMESTAMP);

COMMIT;


