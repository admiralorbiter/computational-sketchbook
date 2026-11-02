"""SQLite schema and data contract definitions for the KCMO Homicide Research Project.

Follows the Data Contract in KCMO_Homicide_Antigravity_Handoff.txt:
- Source snapshots
- Raw rows (preserving original API JSON, field aliases, date precision, text IDs, distinct false vs NULL)
- Incident candidates
- Deceased victims (supporting unnamed victims, separating medical cause, manner, weapon, circumstances)
- Court cases, defendants, and charges (supporting multiple defendants/victims without double counting)
- Status events (dated history across police clearance, prosecutor action, court disposition, appeals)
- Claims and evidence links (atomic assertions with review state: proposed / verified / rejected / unresolved)
- Research tasks (queue tracking, sources checked, blockers, attempt count, outstanding questions)
"""

from __future__ import annotations

import sqlite3

EXPECTED_STARTER_SHA256 = "6221d85597ca6b747098278b07816d9a7e70e9acb53548899273d6fe61751717"

VALID_REVIEW_STATES = ("proposed", "verified", "rejected", "unresolved")

VALID_RESEARCH_STATES = (
    "not_researched",
    "searched_no_result",
    "inaccessible",
    "unknown",
    "in_progress",
    "proposed",
    "verified",
    "unresolved",
)

SCHEMA_DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    dataset_year INTEGER,
    dataset_id TEXT,
    source_name TEXT NOT NULL,
    publisher TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT,
    extraction_url TEXT,
    period TEXT,
    published_or_updated_at TEXT,
    retrieved_at TEXT,
    access_status TEXT NOT NULL,
    dataset_version TEXT,
    content_hash TEXT,
    limit_or_followup_note TEXT
);

CREATE TABLE IF NOT EXISTS raw_rows (
    raw_row_id TEXT PRIMARY KEY,
    snapshot_id TEXT NOT NULL REFERENCES source_snapshots(snapshot_id),
    dataset_year INTEGER NOT NULL,
    dataset_id TEXT NOT NULL,
    snapshot_row INTEGER NOT NULL,
    report_no_raw TEXT NOT NULL,
    report_no_field TEXT NOT NULL,
    ibrs_raw TEXT,
    offense_raw TEXT,
    source_description TEXT,
    extraction_decision TEXT NOT NULL,
    is_candidate_offense INTEGER NOT NULL CHECK (is_candidate_offense IN (0, 1)),
    reported_date_raw TEXT,
    reported_date_calendar TEXT,
    reported_time_raw TEXT,
    reported_date_precision TEXT NOT NULL,
    reported_date_field TEXT,
    reported_time_field TEXT,
    from_date_raw TEXT,
    from_date_calendar TEXT,
    from_time_raw TEXT,
    from_date_precision TEXT NOT NULL,
    to_date_raw TEXT,
    to_date_calendar TEXT,
    to_time_raw TEXT,
    to_date_precision TEXT NOT NULL,
    address_raw TEXT,
    city_raw TEXT,
    zip_code_raw TEXT,
    zip_code_field TEXT,
    rep_dist_raw TEXT,
    beat_raw TEXT,
    area_raw TEXT,
    involvement_raw TEXT,
    race_raw TEXT,
    sex_raw TEXT,
    age_raw TEXT,
    age_range_raw TEXT,
    firearm_flag_raw TEXT,
    firearm_flag_bool INTEGER CHECK (firearm_flag_bool IN (0, 1) OR firearm_flag_bool IS NULL),
    firearm_flag_field TEXT,
    dv_flag_raw TEXT,
    dv_flag_normalized TEXT CHECK (dv_flag_normalized IN ('true', 'false', 'unknown') OR dv_flag_normalized IS NULL),
    latitude REAL,
    longitude REAL,
    location_format TEXT,
    original_json TEXT NOT NULL,
    row_hash TEXT NOT NULL,
    UNIQUE (snapshot_id, snapshot_row)
);

CREATE INDEX IF NOT EXISTS idx_raw_rows_report ON raw_rows(dataset_year, report_no_raw);
CREATE INDEX IF NOT EXISTS idx_raw_rows_ibrs ON raw_rows(ibrs_raw, is_candidate_offense);

CREATE TABLE IF NOT EXISTS incident_candidates (
    candidate_incident_id TEXT PRIMARY KEY,
    agency TEXT NOT NULL,
    report_number TEXT NOT NULL,
    dataset_year INTEGER NOT NULL,
    dataset_id TEXT NOT NULL,
    snapshot_id TEXT NOT NULL REFERENCES source_snapshots(snapshot_id),
    source_offense_codes TEXT NOT NULL,
    source_classification TEXT NOT NULL,
    has_excluded_09d_rows INTEGER NOT NULL DEFAULT 0 CHECK (has_excluded_09d_rows IN (0, 1)),
    excluded_09d_row_count INTEGER NOT NULL DEFAULT 0,
    earliest_incident_date TEXT,
    latest_incident_date TEXT,
    earliest_from_raw TEXT,
    earliest_from_time TEXT,
    latest_to_raw TEXT,
    latest_to_time TEXT,
    incident_date_precision TEXT NOT NULL,
    to_date_note TEXT,
    reported_date TEXT,
    earliest_reported_raw TEXT,
    earliest_reported_time TEXT,
    reported_date_precision TEXT NOT NULL,
    reported_block_or_intersection TEXT,
    city_as_reported TEXT,
    zip_as_reported TEXT,
    reporting_district TEXT,
    patrol_division TEXT,
    beats_as_reported TEXT,
    latitude REAL,
    longitude REAL,
    coordinate_precision TEXT NOT NULL,
    firearm_flag_values_workbook TEXT,
    firearm_flag_values_normalized TEXT,
    domestic_flag_values_raw TEXT,
    domestic_flag_values_normalized TEXT,
    linked_source_rows INTEGER NOT NULL,
    involvement_roles_summary TEXT,
    scope_review_flag TEXT NOT NULL,
    inclusion_decision TEXT NOT NULL DEFAULT 'unreviewed_candidate',
    victim_verification_state TEXT NOT NULL DEFAULT 'not_researched',
    medical_cause_state TEXT NOT NULL DEFAULT 'not_researched',
    police_clearance_state TEXT NOT NULL DEFAULT 'not_researched',
    prosecutor_action_state TEXT NOT NULL DEFAULT 'not_researched',
    court_outcome_state TEXT NOT NULL DEFAULT 'not_researched',
    status_last_checked_at TEXT,
    source_updated_utc TEXT,
    dataset_url TEXT,
    research_notes TEXT,
    UNIQUE (agency, report_number)
);

CREATE INDEX IF NOT EXISTS idx_candidates_year ON incident_candidates(dataset_year);
CREATE INDEX IF NOT EXISTS idx_candidates_scope ON incident_candidates(scope_review_flag);

CREATE TABLE IF NOT EXISTS deceased_victims (
    victim_id TEXT PRIMARY KEY,
    candidate_incident_id TEXT NOT NULL REFERENCES incident_candidates(candidate_incident_id),
    victim_sequence INTEGER NOT NULL,
    publicly_confirmed_name TEXT,
    name_status TEXT NOT NULL DEFAULT 'not_researched'
        CHECK (name_status IN ('confirmed_named', 'confirmed_unnamed', 'not_researched', 'searched_no_result', 'inaccessible', 'unresolved')),
    age_reported TEXT,
    sex_reported TEXT,
    race_reported TEXT,
    injury_date TEXT,
    injury_date_precision TEXT,
    death_date TEXT,
    death_date_precision TEXT,
    discovery_date TEXT,
    ruling_date TEXT,
    medical_cause_of_death TEXT,
    manner_of_death TEXT,
    weapon_or_force_reported TEXT,
    reported_circumstances TEXT,
    verification_state TEXT NOT NULL DEFAULT 'proposed'
        CHECK (verification_state IN ('proposed', 'verified', 'rejected', 'unresolved')),
    supporting_claim_ids_json TEXT NOT NULL DEFAULT '[]',
    notes TEXT,
    UNIQUE (candidate_incident_id, victim_sequence)
);

CREATE TABLE IF NOT EXISTS court_cases (
    court_case_id TEXT PRIMARY KEY,
    candidate_incident_id TEXT NOT NULL REFERENCES incident_candidates(candidate_incident_id),
    court_docket_number TEXT,
    court_jurisdiction TEXT,
    prosecutor_office TEXT,
    referral_date TEXT,
    filing_date TEXT,
    case_stage TEXT NOT NULL DEFAULT 'not_researched',
    verification_state TEXT NOT NULL DEFAULT 'proposed'
        CHECK (verification_state IN ('proposed', 'verified', 'rejected', 'unresolved')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS case_defendants (
    defendant_id TEXT PRIMARY KEY,
    candidate_incident_id TEXT NOT NULL REFERENCES incident_candidates(candidate_incident_id),
    court_case_id TEXT REFERENCES court_cases(court_case_id),
    defendant_sequence INTEGER NOT NULL,
    defendant_name TEXT,
    name_status TEXT NOT NULL DEFAULT 'not_researched'
        CHECK (name_status IN ('confirmed_named', 'withheld_or_juvenile', 'unknown', 'not_researched', 'unresolved')),
    police_clearance_status TEXT NOT NULL DEFAULT 'not_researched',
    police_clearance_wording_raw TEXT,
    police_clearance_date TEXT,
    prosecutor_action_status TEXT NOT NULL DEFAULT 'not_researched',
    prosecutor_wording_raw TEXT,
    prosecutor_action_date TEXT,
    court_disposition_status TEXT NOT NULL DEFAULT 'not_researched',
    court_disposition_wording_raw TEXT,
    disposition_date TEXT,
    sentence_summary TEXT,
    postconviction_or_appeal_status TEXT,
    verification_state TEXT NOT NULL DEFAULT 'proposed'
        CHECK (verification_state IN ('proposed', 'verified', 'rejected', 'unresolved')),
    supporting_claim_ids_json TEXT NOT NULL DEFAULT '[]',
    notes TEXT,
    UNIQUE (candidate_incident_id, defendant_sequence)
);

CREATE TABLE IF NOT EXISTS defendant_charges (
    charge_id TEXT PRIMARY KEY,
    defendant_id TEXT NOT NULL REFERENCES case_defendants(defendant_id),
    court_case_id TEXT REFERENCES court_cases(court_case_id),
    victim_id TEXT REFERENCES deceased_victims(victim_id),
    charge_count_number INTEGER,
    charge_code_raw TEXT,
    charge_description_raw TEXT NOT NULL,
    normalized_charge_category TEXT,
    charge_disposition_status TEXT NOT NULL DEFAULT 'pending_or_unknown',
    charge_disposition_wording_raw TEXT,
    disposition_date TEXT,
    sentence_text TEXT,
    verification_state TEXT NOT NULL DEFAULT 'proposed'
        CHECK (verification_state IN ('proposed', 'verified', 'rejected', 'unresolved'))
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    candidate_incident_id TEXT NOT NULL REFERENCES incident_candidates(candidate_incident_id),
    entity_type TEXT NOT NULL,
    entity_id TEXT,
    field_name TEXT NOT NULL,
    proposed_value TEXT,
    source_id TEXT NOT NULL,
    source_url TEXT,
    evidence_locator TEXT NOT NULL,
    brief_supporting_paraphrase TEXT NOT NULL,
    event_date TEXT,
    date_precision TEXT,
    source_published_at TEXT,
    observed_at TEXT NOT NULL,
    match_basis TEXT NOT NULL,
    review_state TEXT NOT NULL CHECK (review_state IN ('proposed', 'verified', 'rejected', 'unresolved')),
    review_note TEXT,
    competing_claim_id TEXT REFERENCES claims(claim_id),
    created_by_role TEXT
);

CREATE INDEX IF NOT EXISTS idx_claims_incident ON claims(candidate_incident_id, review_state);

CREATE TABLE IF NOT EXISTS status_events (
    status_event_id TEXT PRIMARY KEY,
    candidate_incident_id TEXT NOT NULL REFERENCES incident_candidates(candidate_incident_id),
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    status_domain TEXT NOT NULL
        CHECK (status_domain IN (
            'inclusion',
            'victim_verification',
            'medical_cause',
            'police_clearance',
            'prosecutor_action',
            'court_disposition',
            'appeal_or_postconviction'
        )),
    agency_original_wording TEXT,
    normalized_status TEXT NOT NULL,
    effective_date_start TEXT,
    effective_date_end TEXT,
    date_precision TEXT,
    source_published_at TEXT,
    observed_at TEXT NOT NULL,
    source_id TEXT,
    source_url TEXT,
    claim_id TEXT REFERENCES claims(claim_id),
    review_state TEXT NOT NULL CHECK (review_state IN ('proposed', 'verified', 'rejected', 'unresolved')),
    review_note TEXT
);

CREATE INDEX IF NOT EXISTS idx_status_events_entity ON status_events(candidate_incident_id, entity_type, entity_id);

CREATE TABLE IF NOT EXISTS research_tasks (
    task_id TEXT PRIMARY KEY,
    candidate_incident_id TEXT NOT NULL UNIQUE REFERENCES incident_candidates(candidate_incident_id),
    dataset_year INTEGER NOT NULL,
    report_number TEXT NOT NULL,
    queue_stage TEXT NOT NULL DEFAULT 'step0_queued',
    priority_rank INTEGER,
    selection_stratum TEXT,
    assigned_role TEXT,
    sources_checked_json TEXT NOT NULL DEFAULT '[]',
    progress_summary TEXT NOT NULL DEFAULT 'not_researched',
    blockers TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    latest_search_date TEXT,
    outstanding_questions_json TEXT NOT NULL DEFAULT '[]',
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_year_stage ON research_tasks(dataset_year, queue_stage);
"""


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize all Data Contract tables in SQLite with foreign keys enabled."""
    conn.executescript(SCHEMA_DDL)
    conn.commit()
