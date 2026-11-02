"""Reproducible Step 0 importer for Kansas_City_Homicide_Project_Starter.xlsx.

Reads the immutable starter workbook, reconstructs normalized records from the
Original API row JSON in the 'Source rows' sheet, cross-checks against the
'Candidate cases' sheet, and populates SQLite without overwriting reviewed work.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import openpyxl

from .schema import EXPECTED_STARTER_SHA256, init_db

FIREARM_FIELD_ALIASES = (
    "firearm_used_flag",   # 2020
    "firearmused_flag",    # 2021
    "firearmusedflag",     # 2022, 2023, 2025, 2026
    "fire_arm_used_flag",  # 2024 (missed by starter workbook's 3-alias formula)
)

WORKBOOK_THREE_FIREARM_ALIASES = (
    "firearm_used_flag",
    "firearmused_flag",
    "firearmusedflag",
)


def compute_file_sha256(path: Path) -> str:
    """Return lowercase hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_text_id(val: Any) -> str | None:
    """Preserve identifiers (report numbers, ZIP codes, beats, districts) as text."""
    if val is None:
        return None
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    s = str(val).strip()
    return s if s != "" else None


def classify_date_precision(iso_val: str | None, time_val: str | None, is_2022_dup_to_date: bool = False) -> str:
    """Determine date precision without turning date-only Socrata strings into midnight claims."""
    if not iso_val:
        return "missing"
    if is_2022_dup_to_date:
        return "date_and_time_duplicated_from_start_without_to_time"
    if "T" in iso_val:
        _, time_part = iso_val.split("T", 1)
        if time_part.startswith("00:00:00"):
            if time_val and time_val.strip() not in ("", "00:00", "00:00:00"):
                return "date_only_with_separate_time"
            elif time_val and time_val.strip() in ("00:00", "00:00:00"):
                return "date_only_with_midnight_time_string"
            return "date_only"
        return "timestamp_with_separate_time" if time_val else "timestamp"
    return "date_only_with_separate_time" if time_val else "date_only"


def extract_firearm_flag(obj: dict[str, Any], aliases: tuple[str, ...] = FIREARM_FIELD_ALIASES) -> tuple[str | None, int | None, str | None]:
    """Extract firearm flag keeping false and missing (NULL) strictly distinct."""
    for field in aliases:
        if field in obj:
            raw_val = obj[field]
            if raw_val is None:
                return None, None, field
            if isinstance(raw_val, bool):
                return ("true" if raw_val else "false"), (1 if raw_val else 0), field
            s = str(raw_val).strip().lower()
            if s in ("true", "y", "yes", "1"):
                return "true", 1, field
            if s in ("false", "n", "no", "0"):
                return "false", 0, field
            return str(raw_val).strip(), None, field
    return None, None, None


def extract_dv_flag(obj: dict[str, Any]) -> tuple[str | None, str | None]:
    """Extract domestic violence flag preserving raw ('Y'/'N' or 'true'/'false') and normalized values."""
    if "dvflag" not in obj or obj["dvflag"] is None:
        return None, None
    val = obj["dvflag"]
    if isinstance(val, bool):
        s = "true" if val else "false"
        return s, s
    raw_s = str(val).strip()
    if not raw_s:
        return None, None
    low = raw_s.lower()
    if low in ("y", "yes", "true", "1"):
        return raw_s, "true"
    if low in ("n", "no", "false", "0"):
        return raw_s, "false"
    return raw_s, "unknown"


def extract_coordinates(obj: dict[str, Any]) -> tuple[float | None, float | None, str]:
    """Extract (latitude, longitude, location_format) from Socrata JSON location object."""
    loc = obj.get("location")
    if not isinstance(loc, dict):
        return None, None, "missing"
    if "latitude" in loc and "longitude" in loc and loc["latitude"] is not None and loc["longitude"] is not None:
        return float(loc["latitude"]), float(loc["longitude"]), "socrata_human_address_dict"
    if loc.get("type") == "Point" and isinstance(loc.get("coordinates"), list) and len(loc["coordinates"]) == 2:
        lon, lat = loc["coordinates"]
        if lat is not None and lon is not None:
            return float(lat), float(lon), "geojson_point"
    return None, None, "unrecognized_location_dict"


def join_distinct(values: list[ str | None ]) -> str | None:
    """Join distinct non-empty text values sorted alphabetically with '; '."""
    cleaned = sorted({v.strip() for v in values if v is not None and v.strip() != ""})
    return "; ".join(cleaned) if cleaned else None


def compute_scope_review_flag(
    earliest_incident_date: str | None,
    cities: set[str],
    zips: set[str],
    beats: set[str],
    areas: set[str],
) -> str:
    """Reproduce and explain the starter workbook's scope review flag from raw JSON fields."""
    if earliest_incident_date and earliest_incident_date < "2020-01-01":
        return "Incident date before 2020"
    non_kcmo_city = any(c.upper() != "KANSAS CITY" for c in cities if c)
    ks_zip = any(z.startswith("66") for z in zips if z)
    beat_9 = any(b.startswith("9") for b in beats if b)
    ospd_area = any(a.upper() == "OSPD" for a in areas if a)
    if non_kcmo_city or ks_zip or beat_9 or ospd_area:
        return "Check jurisdiction"
    return "Candidate - verify inclusion"


def build_default_questions(
    scope_review_flag: str,
    source_offense_codes: str,
    has_coords: bool,
    has_excluded_09d: bool,
    linked_rows: int,
) -> list[str]:
    """Generate explicit research questions for a candidate incident task."""
    questions = [
        "Did this incident occur inside Kansas City, Missouri municipal boundaries?",
        "How many deceased homicide victims are confirmed for this report, and what are their publicly confirmed identities and death dates?",
        "What are the medical cause and manner of death (distinct from police firearm flag)?",
        "What is the police clearance status and date, preserving agency wording?",
        "Were charges referred or filed by the responsible prosecutor, and what are the court case numbers, defendants, and dated dispositions?",
    ]
    if scope_review_flag == "Check jurisdiction":
        questions.insert(
            0,
            "PRIORITY SCOPE CHECK: Source row has OSPD/beat-999, non-KCMO city label, or KS ZIP — verify whether incident scene was inside KCMO.",
        )
    elif scope_review_flag == "Incident date before 2020":
        questions.insert(
            0,
            "PRIORITY CARRYOVER CHECK: Source from_date precedes 2020 — verify injury date vs. death/ruling date and whether this is a pre-2020 carryover death.",
        )
    if source_offense_codes != "09A":
        questions.append(
            f"CLASSIFICATION CHECK: Source offense code is {source_offense_codes} (not 09A) — verify official classification and inclusion rule."
        )
    if not has_coords:
        questions.append(
            "GEOCODING CHECK: Published source row lacks coordinates — verify block/intersection location against KCMO place boundary."
        )
    if has_excluded_09d:
        questions.append(
            "MURDER-SUICIDE / 09D AUDIT: Report also has excluded 09D (DV Related Suicide) source rows — separate homicide victim(s) from perpetrator suicide."
        )
    if linked_rows >= 5:
        questions.append(
            f"MULTI-ROW AUDIT: Report has {linked_rows} candidate involvement rows — verify distinct victims vs. suspects/witnesses to prevent double counting."
        )
    return questions


def backup_existing_research(conn: sqlite3.Connection, research_backup_path: Path | None = None) -> dict[str, Any]:
    """Snapshot any non-default reviewed work so a full rebuild never destroys research."""
    tables_exist = {
        r[0]
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    backup: dict[str, Any] = {
        "candidate_progress": {},
        "task_progress": {},
        "deceased_victims": [],
        "court_cases": [],
        "case_defendants": [],
        "defendant_charges": [],
        "claims": [],
        "status_events": [],
    }
    if "incident_candidates" in tables_exist:
        cur = conn.execute(
            """
            SELECT candidate_incident_id, inclusion_decision, victim_verification_state,
                   medical_cause_state, police_clearance_state, prosecutor_action_state,
                   court_outcome_state, status_last_checked_at, research_notes
            FROM incident_candidates
            WHERE inclusion_decision != 'unreviewed_candidate'
               OR victim_verification_state != 'not_researched'
               OR medical_cause_state != 'not_researched'
               OR police_clearance_state != 'not_researched'
               OR prosecutor_action_state != 'not_researched'
               OR court_outcome_state != 'not_researched'
               OR status_last_checked_at IS NOT NULL
               OR research_notes IS NOT NULL
            """
        )
        cols = [d[0] for d in cur.description]
        for row in cur.fetchall():
            d = dict(zip(cols, row))
            backup["candidate_progress"][d["candidate_incident_id"]] = d

    if "research_tasks" in tables_exist:
        cur = conn.execute(
            """
            SELECT task_id, candidate_incident_id, queue_stage, priority_rank,
                   selection_stratum, assigned_role, sources_checked_json,
                   progress_summary, blockers, attempt_count, latest_search_date,
                   outstanding_questions_json, updated_at
            FROM research_tasks
            WHERE queue_stage != 'step0_queued'
               OR progress_summary != 'not_researched'
               OR attempt_count > 0
               OR blockers IS NOT NULL
               OR latest_search_date IS NOT NULL
               OR sources_checked_json != '[]'
            """
        )
        cols = [d[0] for d in cur.description]
        for row in cur.fetchall():
            d = dict(zip(cols, row))
            backup["task_progress"][d["candidate_incident_id"]] = d

    for tbl in ("deceased_victims", "court_cases", "case_defendants", "defendant_charges", "claims", "status_events"):
        if tbl in tables_exist:
            cur = conn.execute(f"SELECT * FROM {tbl}")
            cols = [d[0] for d in cur.description]
            backup[tbl] = [dict(zip(cols, r)) for r in cur.fetchall()]

    if research_backup_path is not None:
        has_any = any(
            bool(backup[k]) for k in backup
        )
        if has_any:
            research_backup_path.parent.mkdir(parents=True, exist_ok=True)
            research_backup_path.write_text(json.dumps(backup, indent=2), encoding="utf-8")
        elif research_backup_path.exists():
            backup = json.loads(research_backup_path.read_text(encoding="utf-8"))

    return backup


def restore_existing_research(conn: sqlite3.Connection, backup: dict[str, Any]) -> None:
    """Re-apply backed-up research state after rebuilding import tables."""
    for cid, cprog in backup.get("candidate_progress", {}).items():
        conn.execute(
            """
            UPDATE incident_candidates
               SET inclusion_decision = ?,
                   victim_verification_state = ?,
                   medical_cause_state = ?,
                   police_clearance_state = ?,
                   prosecutor_action_state = ?,
                   court_outcome_state = ?,
                   status_last_checked_at = ?,
                   research_notes = ?
             WHERE candidate_incident_id = ?
            """,
            (
                cprog["inclusion_decision"],
                cprog["victim_verification_state"],
                cprog["medical_cause_state"],
                cprog["police_clearance_state"],
                cprog["prosecutor_action_state"],
                cprog["court_outcome_state"],
                cprog["status_last_checked_at"],
                cprog["research_notes"],
                cid,
            ),
        )

    for cid, tprog in backup.get("task_progress", {}).items():
        conn.execute(
            """
            UPDATE research_tasks
               SET queue_stage = ?,
                   priority_rank = ?,
                   selection_stratum = ?,
                   assigned_role = ?,
                   sources_checked_json = ?,
                   progress_summary = ?,
                   blockers = ?,
                   attempt_count = ?,
                   latest_search_date = ?,
                   outstanding_questions_json = ?,
                   updated_at = ?
             WHERE candidate_incident_id = ?
            """,
            (
                tprog["queue_stage"],
                tprog["priority_rank"],
                tprog["selection_stratum"],
                tprog["assigned_role"],
                tprog["sources_checked_json"],
                tprog["progress_summary"],
                tprog["blockers"],
                tprog["attempt_count"],
                tprog["latest_search_date"],
                tprog["outstanding_questions_json"],
                tprog["updated_at"],
                cid,
            ),
        )

    for tbl in ("deceased_victims", "court_cases", "case_defendants", "defendant_charges", "claims", "status_events"):
        rows = backup.get(tbl, [])
        for r in rows:
            cols = list(r.keys())
            placeholders = ", ".join("?" for _ in cols)
            col_names = ", ".join(cols)
            conn.execute(
                f"INSERT OR REPLACE INTO {tbl} ({col_names}) VALUES ({placeholders})",
                tuple(r[c] for c in cols),
            )
    conn.commit()


def import_starter_workbook(
    workbook_path: Path,
    db_path: Path,
    rebuild: bool = False,
    research_backup_path: Path | None = None,
) -> dict[str, Any]:
    """Import Kansas_City_Homicide_Project_Starter.xlsx into SQLite.

    Preserves the workbook untouched, parses all 3,146 raw JSON records,
    reconstructs the 974 candidate incidents, cross-checks against the
    workbook's 'Candidate cases' sheet, and initializes empty evidence tables.
    """
    if not workbook_path.exists():
        raise FileNotFoundError(f"Starter workbook not found: {workbook_path}")

    sha_before = compute_file_sha256(workbook_path)
    if sha_before != EXPECTED_STARTER_SHA256:
        raise ValueError(
            f"Starter workbook SHA-256 mismatch: expected {EXPECTED_STARTER_SHA256}, got {sha_before}"
        )

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        backup = backup_existing_research(conn, research_backup_path=research_backup_path)
        if rebuild:
            for tbl in (
                "status_events",
                "claims",
                "defendant_charges",
                "case_defendants",
                "court_cases",
                "deceased_victims",
                "research_tasks",
                "incident_candidates",
                "raw_rows",
                "source_snapshots",
            ):
                conn.execute(f"DROP TABLE IF EXISTS {tbl};")
            conn.commit()

        init_db(conn)

        wb = openpyxl.load_workbook(str(workbook_path), read_only=True, data_only=True)
        try:
            ws_sources = wb["Sources"]
            sources_rows = list(ws_sources.iter_rows(values_only=True))[1:]

            ws_raw = wb["Source rows"]
            raw_sheet_rows = list(ws_raw.iter_rows(values_only=True))[1:]

            ws_cand = wb["Candidate cases"]
            cand_sheet_rows = list(ws_cand.iter_rows(values_only=True))
            cand_headers = cand_sheet_rows[0]
            wb_candidates_by_rep: dict[str, dict[str, Any]] = {}
            for r in cand_sheet_rows[1:]:
                d = dict(zip(cand_headers, r))
                wb_candidates_by_rep[clean_text_id(d["Police report number"])] = d
        finally:
            wb.close()

        # Compute deterministic content hashes per dataset_id from raw rows JSON
        dataset_hashers: dict[str, hashlib._Hash] = defaultdict(hashlib.sha256)
        for r in raw_sheet_rows:
            yr, dsid, snap_row, rep_no, ibrs, desc, dec, raw_json = r
            if dsid and raw_json:
                dataset_hashers[str(dsid)].update(f"{snap_row}:{raw_json}\n".encode("utf-8"))

        # 1. Upsert source_snapshots from 'Sources' sheet
        dataset_id_to_snapshot_id: dict[str, str] = {}
        dataset_id_to_updated_utc: dict[str, str | None] = {}
        dataset_id_to_url: dict[str, str | None] = {}

        for idx, r in enumerate(sources_rows, start=1):
            if not any(x is not None for x in r):
                continue
            src_name, url, period, access_checked, useful_content, limit_note, dsid, ext_url, retrieved = r
            dsid_str = clean_text_id(dsid)
            if dsid_str:
                snapshot_id = f"SOCRATA:{dsid_str}"
                dataset_id_to_snapshot_id[dsid_str] = snapshot_id
                dataset_year = int(period) if str(period).isdigit() else None
                publisher = "KCPD / Open Data KC (data.kcmo.org)"
                content_hash = dataset_hashers[dsid_str].hexdigest() if dsid_str in dataset_hashers else sha_before
            else:
                slug = "".join(ch if ch.isalnum() else "_" for ch in str(src_name).upper()).strip("_")
                snapshot_id = f"REF:{idx:02d}:{slug[:32]}"
                dataset_year = None
                publisher = str(src_name)
                content_hash = None

            updated_at = None
            if useful_content and "Last data update (UTC):" in str(useful_content):
                updated_at = str(useful_content).split("Last data update (UTC):", 1)[1].strip()
            if dsid_str:
                dataset_id_to_updated_utc[dsid_str] = updated_at[:10] if updated_at else None
                dataset_id_to_url[dsid_str] = str(url) if url else None

            retrieved_str = (
                retrieved.isoformat() + "Z"
                if hasattr(retrieved, "isoformat")
                else (str(retrieved) if retrieved is not None else None)
            )

            conn.execute(
                """
                INSERT INTO source_snapshots (
                    snapshot_id, dataset_year, dataset_id, source_name, publisher, title,
                    url, extraction_url, period, published_or_updated_at, retrieved_at,
                    access_status, dataset_version, content_hash, limit_or_followup_note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(snapshot_id) DO UPDATE SET
                    published_or_updated_at = excluded.published_or_updated_at,
                    retrieved_at = excluded.retrieved_at,
                    access_status = excluded.access_status,
                    content_hash = excluded.content_hash,
                    limit_or_followup_note = excluded.limit_or_followup_note
                """,
                (
                    snapshot_id,
                    dataset_year,
                    dsid_str,
                    str(src_name),
                    publisher,
                    str(src_name),
                    str(url) if url else None,
                    str(ext_url) if ext_url else None,
                    str(period) if period is not None else None,
                    updated_at,
                    retrieved_str,
                    str(access_checked) if access_checked else "unknown",
                    updated_at[:10] if updated_at else "2026-11-01-starter",
                    content_hash,
                    str(limit_note) if limit_note else None,
                ),
            )

        # 2. Parse and upsert all 3,146 raw_rows
        parsed_rows_by_report: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
        raw_row_count = 0
        candidate_row_count = 0
        excluded_09d_row_count = 0

        for r in raw_sheet_rows:
            yr, dsid, snap_row, rep_no_cell, ibrs_cell, desc_cell, dec_cell, raw_json_str = r
            dataset_year = int(yr)
            dataset_id = clean_text_id(dsid)
            assert dataset_id is not None
            snapshot_row = int(snap_row)
            snapshot_id = dataset_id_to_snapshot_id[dataset_id]
            raw_row_id = f"{dataset_id}:{snapshot_row}"

            obj = json.loads(raw_json_str)
            row_hash = hashlib.sha256(raw_json_str.encode("utf-8")).hexdigest()

            if "report_no" in obj:
                report_no_field = "report_no"
                report_no_raw = clean_text_id(obj["report_no"])
            elif "report" in obj:
                report_no_field = "report"
                report_no_raw = clean_text_id(obj["report"])
            else:
                report_no_field = "sheet_fallback"
                report_no_raw = clean_text_id(rep_no_cell)
            assert report_no_raw is not None

            ibrs_raw = clean_text_id(obj.get("ibrs") or ibrs_cell)
            offense_raw = clean_text_id(obj.get("offense"))
            source_description = clean_text_id(obj.get("description") or desc_cell)
            extraction_decision = str(dec_cell).strip()
            is_candidate = 1 if extraction_decision == "Candidate offense row" else 0

            if is_candidate:
                candidate_row_count += 1
            else:
                excluded_09d_row_count += 1

            # Reported date & time
            if "reported_date" in obj:
                reported_date_field = "reported_date"
                reported_date_raw = clean_text_id(obj["reported_date"])
            elif "report_date" in obj:
                reported_date_field = "report_date"
                reported_date_raw = clean_text_id(obj["report_date"])
            else:
                reported_date_field = None
                reported_date_raw = None

            if "reported_time" in obj:
                reported_time_field = "reported_time"
                reported_time_raw = clean_text_id(obj["reported_time"])
            elif "report_time" in obj:
                reported_time_field = "report_time"
                reported_time_raw = clean_text_id(obj["report_time"])
            else:
                reported_time_field = None
                reported_time_raw = None

            reported_date_calendar = reported_date_raw[:10] if reported_date_raw else None
            reported_date_precision = classify_date_precision(reported_date_raw, reported_time_raw)

            # From date & time
            from_date_raw = clean_text_id(obj.get("from_date"))
            from_time_raw = clean_text_id(obj.get("from_time"))
            from_date_calendar = from_date_raw[:10] if from_date_raw else None
            from_date_precision = classify_date_precision(from_date_raw, from_time_raw)

            # To date & time
            to_date_raw = clean_text_id(obj.get("to_date"))
            to_time_raw = clean_text_id(obj.get("to_time"))
            to_date_calendar = to_date_raw[:10] if to_date_raw else None
            is_2022_dup = (
                dataset_year == 2022
                and to_date_raw is not None
                and to_time_raw is None
                and to_date_raw == from_date_raw
            )
            to_date_precision = classify_date_precision(to_date_raw, to_time_raw, is_2022_dup_to_date=is_2022_dup)

            # Geography & identifiers (all preserved as text)
            address_raw = clean_text_id(obj.get("address"))
            city_raw = clean_text_id(obj.get("city"))
            if "zip_code" in obj:
                zip_code_field = "zip_code"
                zip_code_raw = clean_text_id(obj["zip_code"])
            elif "zipcode" in obj:
                zip_code_field = "zipcode"
                zip_code_raw = clean_text_id(obj["zipcode"])
            else:
                zip_code_field = None
                zip_code_raw = None

            rep_dist_raw = clean_text_id(obj.get("rep_dist"))
            beat_raw = clean_text_id(obj.get("beat"))
            area_raw = clean_text_id(obj.get("area"))
            involvement_raw = clean_text_id(obj.get("involvement"))
            race_raw = clean_text_id(obj.get("race"))
            sex_raw = clean_text_id(obj.get("sex"))
            age_raw = clean_text_id(obj.get("age"))
            age_range_raw = clean_text_id(obj.get("age_range"))

            firearm_flag_raw, firearm_flag_bool, firearm_flag_field = extract_firearm_flag(obj, FIREARM_FIELD_ALIASES)
            wb_firearm_raw, _, _ = extract_firearm_flag(obj, WORKBOOK_THREE_FIREARM_ALIASES)
            dv_flag_raw, dv_flag_normalized = extract_dv_flag(obj)
            lat, lon, loc_fmt = extract_coordinates(obj)

            conn.execute(
                """
                INSERT INTO raw_rows (
                    raw_row_id, snapshot_id, dataset_year, dataset_id, snapshot_row,
                    report_no_raw, report_no_field, ibrs_raw, offense_raw, source_description,
                    extraction_decision, is_candidate_offense,
                    reported_date_raw, reported_date_calendar, reported_time_raw,
                    reported_date_precision, reported_date_field, reported_time_field,
                    from_date_raw, from_date_calendar, from_time_raw, from_date_precision,
                    to_date_raw, to_date_calendar, to_time_raw, to_date_precision,
                    address_raw, city_raw, zip_code_raw, zip_code_field,
                    rep_dist_raw, beat_raw, area_raw, involvement_raw,
                    race_raw, sex_raw, age_raw, age_range_raw,
                    firearm_flag_raw, firearm_flag_bool, firearm_flag_field,
                    dv_flag_raw, dv_flag_normalized,
                    latitude, longitude, location_format,
                    original_json, row_hash
                ) VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?,
                    ?, ?
                )
                ON CONFLICT(raw_row_id) DO UPDATE SET
                    row_hash = excluded.row_hash,
                    original_json = excluded.original_json,
                    firearm_flag_raw = excluded.firearm_flag_raw,
                    firearm_flag_bool = excluded.firearm_flag_bool,
                    firearm_flag_field = excluded.firearm_flag_field
                """,
                (
                    raw_row_id, snapshot_id, dataset_year, dataset_id, snapshot_row,
                    report_no_raw, report_no_field, ibrs_raw, offense_raw, source_description,
                    extraction_decision, is_candidate,
                    reported_date_raw, reported_date_calendar, reported_time_raw,
                    reported_date_precision, reported_date_field, reported_time_field,
                    from_date_raw, from_date_calendar, from_time_raw, from_date_precision,
                    to_date_raw, to_date_calendar, to_time_raw, to_date_precision,
                    address_raw, city_raw, zip_code_raw, zip_code_field,
                    rep_dist_raw, beat_raw, area_raw, involvement_raw,
                    race_raw, sex_raw, age_raw, age_range_raw,
                    firearm_flag_raw, firearm_flag_bool, firearm_flag_field,
                    dv_flag_raw, dv_flag_normalized,
                    lat, lon, loc_fmt,
                    raw_json_str, row_hash,
                ),
            )

            parsed_rows_by_report[(dataset_year, report_no_raw)].append(
                {
                    "raw_row_id": raw_row_id,
                    "snapshot_id": snapshot_id,
                    "dataset_year": dataset_year,
                    "dataset_id": dataset_id,
                    "report_no_raw": report_no_raw,
                    "ibrs_raw": ibrs_raw,
                    "source_description": source_description,
                    "is_candidate": is_candidate,
                    "reported_date_raw": reported_date_raw,
                    "reported_date_calendar": reported_date_calendar,
                    "reported_time_raw": reported_time_raw,
                    "reported_date_precision": reported_date_precision,
                    "from_date_raw": from_date_raw,
                    "from_date_calendar": from_date_calendar,
                    "from_time_raw": from_time_raw,
                    "from_date_precision": from_date_precision,
                    "to_date_raw": to_date_raw,
                    "to_date_calendar": to_date_calendar,
                    "to_time_raw": to_time_raw,
                    "to_date_precision": to_date_precision,
                    "is_2022_dup": is_2022_dup,
                    "address_raw": address_raw,
                    "city_raw": city_raw,
                    "zip_code_raw": zip_code_raw,
                    "rep_dist_raw": rep_dist_raw,
                    "beat_raw": beat_raw,
                    "area_raw": area_raw,
                    "involvement_raw": involvement_raw,
                    "firearm_flag_raw": firearm_flag_raw,
                    "wb_firearm_raw": wb_firearm_raw,
                    "dv_flag_raw": dv_flag_raw,
                    "dv_flag_normalized": dv_flag_normalized,
                    "lat": lat,
                    "lon": lon,
                }
            )
            raw_row_count += 1

        # 3. Construct incident_candidates from candidate rows (09A, 09B, 09C)
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        candidate_count = 0
        candidates_by_year: Counter[int] = Counter()
        scope_flag_counts: Counter[str] = Counter()
        mixed_09d_reports: list[str] = []
        only_09d_reports: list[str] = []
        discrepancies_vs_workbook: list[dict[str, Any]] = []

        for (dataset_year, report_number), all_rows in sorted(parsed_rows_by_report.items()):
            cand_rows = [r for r in all_rows if r["is_candidate"] == 1]
            excl_rows = [r for r in all_rows if r["is_candidate"] == 0]

            if not cand_rows:
                only_09d_reports.append(f"{dataset_year}:{report_number}")
                continue

            if excl_rows:
                mixed_09d_reports.append(f"{dataset_year}:{report_number}")

            candidate_count += 1
            candidates_by_year[dataset_year] += 1

            agency = "KCPD"
            candidate_incident_id = f"{agency}:{report_number}"
            dataset_id = cand_rows[0]["dataset_id"]
            snapshot_id = cand_rows[0]["snapshot_id"]

            source_offense_codes = join_distinct([r["ibrs_raw"] for r in cand_rows]) or ""
            source_classification = join_distinct([r["source_description"] for r in cand_rows]) or ""

            from_calendars = sorted({r["from_date_calendar"] for r in cand_rows if r["from_date_calendar"]})
            to_calendars = sorted({r["to_date_calendar"] for r in cand_rows if r["to_date_calendar"]})
            earliest_incident_date = from_calendars[0] if from_calendars else None
            latest_incident_date = (
                to_calendars[-1]
                if to_calendars
                else (from_calendars[-1] if len(from_calendars) > 1 else None)
            )

            from_raws = sorted({r["from_date_raw"] for r in cand_rows if r["from_date_raw"]})
            from_times = sorted({r["from_time_raw"] for r in cand_rows if r["from_time_raw"]})
            to_raws = sorted({r["to_date_raw"] for r in cand_rows if r["to_date_raw"]})
            to_times = sorted({r["to_time_raw"] for r in cand_rows if r["to_time_raw"]})

            earliest_from_raw = from_raws[0] if from_raws else None
            earliest_from_time = from_times[0] if from_times else None
            latest_to_raw = to_raws[-1] if to_raws else None
            latest_to_time = to_times[-1] if to_times else None

            inc_precisions = sorted({r["from_date_precision"] for r in cand_rows})
            incident_date_precision = "; ".join(inc_precisions)

            if any(r["is_2022_dup"] for r in cand_rows) and not to_times:
                to_date_note = "2022 Socrata export repeats from_date in to_date even when to_time is absent"
            elif latest_to_raw:
                to_date_note = "Explicit to_date present in source"
            else:
                to_date_note = None

            rep_calendars = sorted({r["reported_date_calendar"] for r in cand_rows if r["reported_date_calendar"]})
            reported_date = rep_calendars[0] if rep_calendars else None
            rep_raws = sorted({r["reported_date_raw"] for r in cand_rows if r["reported_date_raw"]})
            rep_times = sorted({r["reported_time_raw"] for r in cand_rows if r["reported_time_raw"]})
            earliest_reported_raw = rep_raws[0] if rep_raws else None
            earliest_reported_time = rep_times[0] if rep_times else None
            reported_date_precision = "; ".join(sorted({r["reported_date_precision"] for r in cand_rows}))

            reported_block = join_distinct([r["address_raw"] for r in cand_rows])
            city_as_reported = join_distinct([r["city_raw"] for r in cand_rows])
            zip_as_reported = join_distinct([r["zip_code_raw"] for r in cand_rows])
            reporting_district = join_distinct([r["rep_dist_raw"] for r in cand_rows])
            patrol_division = join_distinct([r["area_raw"] for r in cand_rows])
            beats_as_reported = join_distinct([r["beat_raw"] for r in cand_rows])

            coords = {(r["lat"], r["lon"]) for r in cand_rows if r["lat"] is not None and r["lon"] is not None}
            if len(coords) == 1:
                latitude, longitude = next(iter(coords))
                coordinate_precision = "block_or_intersection_point"
            elif len(coords) > 1:
                latitude, longitude = None, None
                coordinate_precision = "conflicting_coordinates_across_rows"
            else:
                latitude, longitude = None, None
                coordinate_precision = "missing"

            firearm_flag_values_workbook = join_distinct([r["wb_firearm_raw"] for r in cand_rows])
            firearm_flag_values_normalized = join_distinct([r["firearm_flag_raw"] for r in cand_rows])
            domestic_flag_values_raw = join_distinct([r["dv_flag_raw"] for r in cand_rows])
            domestic_flag_values_normalized = join_distinct([r["dv_flag_normalized"] for r in cand_rows])

            linked_source_rows = len(cand_rows)
            inv_counter = Counter(r["involvement_raw"] for r in cand_rows if r["involvement_raw"])
            involvement_roles_summary = "; ".join(f"{k} ({v})" for k, v in sorted(inv_counter.items()))

            scope_review_flag = compute_scope_review_flag(
                earliest_incident_date=earliest_incident_date,
                cities={r["city_raw"] for r in cand_rows if r["city_raw"]},
                zips={r["zip_code_raw"] for r in cand_rows if r["zip_code_raw"]},
                beats={r["beat_raw"] for r in cand_rows if r["beat_raw"]},
                areas={r["area_raw"] for r in cand_rows if r["area_raw"]},
            )
            scope_flag_counts[scope_review_flag] += 1

            # Verify against workbook 'Candidate cases' sheet
            wb_row = wb_candidates_by_rep.get(report_number)
            if wb_row is None:
                discrepancies_vs_workbook.append(
                    {"report_number": report_number, "issue": "Missing from workbook Candidate cases sheet"}
                )
            else:
                if wb_row["Scope review"] != scope_review_flag:
                    discrepancies_vs_workbook.append(
                        {
                            "report_number": report_number,
                            "issue": f"Scope review mismatch: workbook={wb_row['Scope review']!r} vs computed={scope_review_flag!r}",
                        }
                    )
                if wb_row["Firearm flag values"] != firearm_flag_values_normalized:
                    discrepancies_vs_workbook.append(
                        {
                            "dataset_year": dataset_year,
                            "report_number": report_number,
                            "issue": "2024_fire_arm_used_flag_alias_recovered",
                            "workbook_value": wb_row["Firearm flag values"],
                            "normalized_json_value": firearm_flag_values_normalized,
                        }
                    )

            source_updated_utc = dataset_id_to_updated_utc.get(dataset_id)
            dataset_url = dataset_id_to_url.get(dataset_id)

            conn.execute(
                """
                INSERT INTO incident_candidates (
                    candidate_incident_id, agency, report_number, dataset_year, dataset_id, snapshot_id,
                    source_offense_codes, source_classification,
                    has_excluded_09d_rows, excluded_09d_row_count,
                    earliest_incident_date, latest_incident_date,
                    earliest_from_raw, earliest_from_time, latest_to_raw, latest_to_time,
                    incident_date_precision, to_date_note,
                    reported_date, earliest_reported_raw, earliest_reported_time, reported_date_precision,
                    reported_block_or_intersection, city_as_reported, zip_as_reported,
                    reporting_district, patrol_division, beats_as_reported,
                    latitude, longitude, coordinate_precision,
                    firearm_flag_values_workbook, firearm_flag_values_normalized,
                    domestic_flag_values_raw, domestic_flag_values_normalized,
                    linked_source_rows, involvement_roles_summary,
                    scope_review_flag, source_updated_utc, dataset_url
                ) VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?, ?, ?,
                    ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?, ?
                )
                ON CONFLICT(candidate_incident_id) DO UPDATE SET
                    source_offense_codes = excluded.source_offense_codes,
                    source_classification = excluded.source_classification,
                    has_excluded_09d_rows = excluded.has_excluded_09d_rows,
                    excluded_09d_row_count = excluded.excluded_09d_row_count,
                    earliest_incident_date = excluded.earliest_incident_date,
                    latest_incident_date = excluded.latest_incident_date,
                    earliest_from_raw = excluded.earliest_from_raw,
                    earliest_from_time = excluded.earliest_from_time,
                    latest_to_raw = excluded.latest_to_raw,
                    latest_to_time = excluded.latest_to_time,
                    incident_date_precision = excluded.incident_date_precision,
                    to_date_note = excluded.to_date_note,
                    reported_date = excluded.reported_date,
                    earliest_reported_raw = excluded.earliest_reported_raw,
                    earliest_reported_time = excluded.earliest_reported_time,
                    reported_date_precision = excluded.reported_date_precision,
                    reported_block_or_intersection = excluded.reported_block_or_intersection,
                    city_as_reported = excluded.city_as_reported,
                    zip_as_reported = excluded.zip_as_reported,
                    reporting_district = excluded.reporting_district,
                    patrol_division = excluded.patrol_division,
                    beats_as_reported = excluded.beats_as_reported,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    coordinate_precision = excluded.coordinate_precision,
                    firearm_flag_values_workbook = excluded.firearm_flag_values_workbook,
                    firearm_flag_values_normalized = excluded.firearm_flag_values_normalized,
                    domestic_flag_values_raw = excluded.domestic_flag_values_raw,
                    domestic_flag_values_normalized = excluded.domestic_flag_values_normalized,
                    linked_source_rows = excluded.linked_source_rows,
                    involvement_roles_summary = excluded.involvement_roles_summary,
                    scope_review_flag = excluded.scope_review_flag,
                    source_updated_utc = excluded.source_updated_utc,
                    dataset_url = excluded.dataset_url
                """,
                (
                    candidate_incident_id, agency, report_number, dataset_year, dataset_id, snapshot_id,
                    source_offense_codes, source_classification,
                    1 if excl_rows else 0, len(excl_rows),
                    earliest_incident_date, latest_incident_date,
                    earliest_from_raw, earliest_from_time, latest_to_raw, latest_to_time,
                    incident_date_precision, to_date_note,
                    reported_date, earliest_reported_raw, earliest_reported_time, reported_date_precision,
                    reported_block, city_as_reported, zip_as_reported,
                    reporting_district, patrol_division, beats_as_reported,
                    latitude, longitude, coordinate_precision,
                    firearm_flag_values_workbook, firearm_flag_values_normalized,
                    domestic_flag_values_raw, domestic_flag_values_normalized,
                    linked_source_rows, involvement_roles_summary,
                    scope_review_flag, source_updated_utc, dataset_url,
                ),
            )

            # 4. Initialize research_tasks without overwriting existing progress
            task_id = f"TASK:{dataset_year}:{report_number}"
            default_questions = build_default_questions(
                scope_review_flag=scope_review_flag,
                source_offense_codes=source_offense_codes,
                has_coords=(latitude is not None and longitude is not None),
                has_excluded_09d=bool(excl_rows),
                linked_rows=linked_source_rows,
            )
            conn.execute(
                """
                INSERT INTO research_tasks (
                    task_id, candidate_incident_id, dataset_year, report_number,
                    queue_stage, outstanding_questions_json, updated_at
                ) VALUES (?, ?, ?, ?, 'step0_queued', ?, ?)
                ON CONFLICT(candidate_incident_id) DO NOTHING
                """,
                (
                    task_id,
                    candidate_incident_id,
                    dataset_year,
                    report_number,
                    json.dumps(default_questions),
                    now_utc,
                ),
            )

        if rebuild:
            restore_existing_research(conn, backup)

        conn.commit()
    finally:
        conn.close()

    sha_after = compute_file_sha256(workbook_path)
    if sha_after != sha_before:
        raise RuntimeError("Workbook SHA-256 changed during import!")

    return {
        "workbook_path": str(workbook_path),
        "workbook_sha256": sha_after,
        "db_path": str(db_path),
        "raw_rows_imported": raw_row_count,
        "candidate_offense_rows": candidate_row_count,
        "excluded_09d_rows": excluded_09d_row_count,
        "candidate_incidents": candidate_count,
        "candidates_by_year": dict(sorted(candidates_by_year.items())),
        "scope_flag_counts": dict(scope_flag_counts),
        "only_09d_reports": only_09d_reports,
        "mixed_09a_and_09d_reports": mixed_09d_reports,
        "recovered_2024_firearm_flags_count": sum(
            1 for d in discrepancies_vs_workbook if d.get("issue") == "2024_fire_arm_used_flag_alias_recovered"
        ),
    }
