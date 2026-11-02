"""Export utilities for the 2020 review/research queue and Step 0 audit summary."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any


QUEUE_EXPORT_COLUMNS = (
    "task_id",
    "candidate_incident_id",
    "dataset_year",
    "report_number",
    "queue_stage",
    "scope_review_flag",
    "source_offense_codes",
    "source_classification",
    "has_excluded_09d_rows",
    "excluded_09d_row_count",
    "earliest_incident_date",
    "latest_incident_date",
    "earliest_from_time",
    "latest_to_time",
    "incident_date_precision",
    "reported_date",
    "earliest_reported_time",
    "reported_block_or_intersection",
    "city_as_reported",
    "zip_as_reported",
    "reporting_district",
    "patrol_division",
    "beats_as_reported",
    "latitude",
    "longitude",
    "coordinate_precision",
    "firearm_flag_values_normalized",
    "domestic_flag_values_raw",
    "domestic_flag_values_normalized",
    "linked_source_rows",
    "involvement_roles_summary",
    "inclusion_decision",
    "victim_verification_state",
    "medical_cause_state",
    "police_clearance_state",
    "prosecutor_action_state",
    "court_outcome_state",
    "attempt_count",
    "latest_search_date",
    "blockers",
    "sources_checked_json",
    "outstanding_questions_json",
)


def export_research_queue(
    db_path: Path,
    csv_path: Path,
    jsonl_path: Path | None = None,
    dataset_year: int = 2020,
) -> dict[str, Any]:
    """Export the research queue for a given dataset_year (default 2020) to CSV and JSONL."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if jsonl_path is not None:
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT
                t.task_id,
                c.candidate_incident_id,
                c.dataset_year,
                c.report_number,
                t.queue_stage,
                c.scope_review_flag,
                c.source_offense_codes,
                c.source_classification,
                c.has_excluded_09d_rows,
                c.excluded_09d_row_count,
                c.earliest_incident_date,
                c.latest_incident_date,
                c.earliest_from_time,
                c.latest_to_time,
                c.incident_date_precision,
                c.reported_date,
                c.earliest_reported_time,
                c.reported_block_or_intersection,
                c.city_as_reported,
                c.zip_as_reported,
                c.reporting_district,
                c.patrol_division,
                c.beats_as_reported,
                c.latitude,
                c.longitude,
                c.coordinate_precision,
                c.firearm_flag_values_normalized,
                c.domestic_flag_values_raw,
                c.domestic_flag_values_normalized,
                c.linked_source_rows,
                c.involvement_roles_summary,
                c.inclusion_decision,
                c.victim_verification_state,
                c.medical_cause_state,
                c.police_clearance_state,
                c.prosecutor_action_state,
                c.court_outcome_state,
                t.attempt_count,
                t.latest_search_date,
                t.blockers,
                t.sources_checked_json,
                t.outstanding_questions_json
            FROM incident_candidates c
            JOIN research_tasks t
              ON t.candidate_incident_id = c.candidate_incident_id
            WHERE c.dataset_year = ?
            ORDER BY c.earliest_incident_date ASC, c.report_number ASC
            """,
            (dataset_year,),
        ).fetchall()

        records: list[dict[str, Any]] = [dict(r) for r in rows]

        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(QUEUE_EXPORT_COLUMNS))
            writer.writeheader()
            for rec in records:
                writer.writerow(rec)

        if jsonl_path is not None:
            with jsonl_path.open("w", encoding="utf-8") as jf:
                for rec in records:
                    rich = dict(rec)
                    rich["sources_checked"] = json.loads(rec["sources_checked_json"])
                    rich["outstanding_questions"] = json.loads(rec["outstanding_questions_json"])
                    jf.write(json.dumps(rich) + "\n")

        return {
            "dataset_year": dataset_year,
            "exported_rows": len(records),
            "csv_path": str(csv_path),
            "jsonl_path": str(jsonl_path) if jsonl_path else None,
        }
    finally:
        conn.close()
