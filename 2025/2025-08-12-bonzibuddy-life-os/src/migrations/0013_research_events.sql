BEGIN;

-- Research v0 additions: events, evidence links, tagging bridge; extend source/note/highlight

-- Current events/news
CREATE TABLE IF NOT EXISTS news_event (
  id INTEGER PRIMARY KEY,
  date_ts TEXT,
  headline TEXT NOT NULL,
  outlet TEXT,
  summary TEXT,
  url TEXT,
  added_ts TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_news_event_date ON news_event(date_ts);
CREATE INDEX IF NOT EXISTS idx_news_event_url ON news_event(url);

-- Evidence link between question and source with stance
CREATE TABLE IF NOT EXISTS evidence_link (
  id INTEGER PRIMARY KEY,
  question_id INTEGER NOT NULL,
  source_id INTEGER NOT NULL,
  stance TEXT DEFAULT 'neutral', -- supports|refutes|neutral
  note TEXT,
  FOREIGN KEY(question_id) REFERENCES question(id),
  FOREIGN KEY(source_id) REFERENCES source(id)
);

CREATE INDEX IF NOT EXISTS idx_evidence_question ON evidence_link(question_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence_link(source_id);

-- Shared tagging bridge
CREATE TABLE IF NOT EXISTS tag_map (
  id INTEGER PRIMARY KEY,
  entity_type TEXT NOT NULL, -- e.g., 'source','news_event','note','highlight','question'
  entity_id INTEGER NOT NULL,
  tag_id INTEGER NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(entity_type, entity_id, tag_id),
  FOREIGN KEY(tag_id) REFERENCES tag(id)
);

CREATE INDEX IF NOT EXISTS idx_tag_map_entity ON tag_map(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_tag_map_tag ON tag_map(tag_id);

-- Extend source with richer metadata
ALTER TABLE source ADD COLUMN venue TEXT;
ALTER TABLE source ADD COLUMN publisher TEXT;
ALTER TABLE source ADD COLUMN published_date TEXT;
ALTER TABLE source ADD COLUMN language TEXT;
ALTER TABLE source ADD COLUMN abstract TEXT;
ALTER TABLE source ADD COLUMN doi TEXT;
ALTER TABLE source ADD COLUMN arxiv_id TEXT;
ALTER TABLE source ADD COLUMN via_url TEXT;
ALTER TABLE source ADD COLUMN added_ts TEXT DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX IF NOT EXISTS idx_source_doi ON source(doi);
CREATE INDEX IF NOT EXISTS idx_source_arxiv ON source(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_source_url ON source(url);

-- Extend note/highlight
ALTER TABLE note ADD COLUMN kind TEXT; -- note|summary
ALTER TABLE note ADD COLUMN pinned INTEGER DEFAULT 0; -- bool
ALTER TABLE highlight ADD COLUMN comment TEXT;

INSERT INTO schema_version(version, applied_at) VALUES (13, CURRENT_TIMESTAMP);

COMMIT;


