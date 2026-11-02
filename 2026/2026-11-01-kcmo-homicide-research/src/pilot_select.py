"""Deterministic Step 1 selection rule and task-packet builder for the 10-case 2020 pilot."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PILOT_SELECTION_RULE = (
    "Deterministic 6-stratum workflow test sample from 2020 candidates (ordered by earliest_incident_date, report_number within each stratum): "
    "(A) first 3 ordinary 09A records with coordinates, 2-3 rows, and no scope/09D flags (KC20001088, KC20001607, KC20002513); "
    "(B) 2 location/jurisdiction ambiguity records with 'Check jurisdiction' flag — first KCMO-labeled beat-999 record (KC20001881) and first non-KCMO postal city OSPD record (KC20030505); "
    "(C) first 2 high-multiplicity (8+ row) 09A records (KC20004297 with 9 rows, KC20004714 with 20 rows); "
    "(D) first missing-coordinate non-firearm (firearm=false) intersection record (KC20008191); "
    "(E) first non-09A classification record (KC20009618, 09C Justifiable Homicide); "
    "(F) first mixed 09A + excluded 09D (DV Related Suicide) record (KC20041259)."
)

PILOT_CASES_SPEC = [
    ("KC20001088", "A1_ordinary_09A_baseline"),
    ("KC20001607", "A2_ordinary_09A_baseline"),
    ("KC20002513", "A3_ordinary_09A_dv_flag"),
    ("KC20001881", "B1_jurisdiction_beat999_missing_coords"),
    ("KC20030505", "B2_jurisdiction_ospd_independence_postal_city"),
    ("KC20004297", "C1_multi_row_9_involvements"),
    ("KC20004714", "C2_multi_row_20_involvements_mass_event"),
    ("KC20008191", "D1_missing_coords_non_firearm_intersection"),
    ("KC20009618", "E1_non_09A_justifiable_homicide_09C"),
    ("KC20041259", "F1_mixed_09A_and_excluded_09D_murder_suicide"),
]


def select_and_export_pilot_tasks(db_path: Path, output_dir: Path) -> list[dict[str, Any]]:
    """Select the 10 pilot cases in SQLite and write explicit input task packets as JSONL."""
    output_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    packets: list[dict[str, Any]] = []
    try:
        for rank, (rep_no, stratum) in enumerate(PILOT_CASES_SPEC, start=1):
            cid = f"KCPD:{rep_no}"
            conn.execute(
                """
                UPDATE research_tasks
                   SET queue_stage = 'pilot_selected',
                       priority_rank = ?,
                       selection_stratum = ?,
                       updated_at = ?
                 WHERE candidate_incident_id = ?
                """,
                (rank, stratum, now_utc, cid),
            )
            cand = dict(
                conn.execute(
                    "SELECT * FROM incident_candidates WHERE candidate_incident_id = ?",
                    (cid,),
                ).fetchone()
            )
            task = dict(
                conn.execute(
                    "SELECT * FROM research_tasks WHERE candidate_incident_id = ?",
                    (cid,),
                ).fetchone()
            )
            raw_rows = [
                dict(r)
                for r in conn.execute(
                    """
                    SELECT raw_row_id, snapshot_row, ibrs_raw, offense_raw, source_description,
                           extraction_decision, is_candidate_offense,
                           from_date_raw, from_time_raw, to_date_raw, to_time_raw,
                           reported_date_raw, reported_time_raw,
                           address_raw, city_raw, zip_code_raw, rep_dist_raw, beat_raw, area_raw,
                           involvement_raw, race_raw, sex_raw, age_raw,
                           firearm_flag_raw, dv_flag_raw, latitude, longitude
                    FROM raw_rows
                    WHERE dataset_year = 2020 AND report_no_raw = ?
                    ORDER BY snapshot_row ASC
                    """,
                    (rep_no,),
                ).fetchall()
            ]
            packet = {
                "pilot_rank": rank,
                "selection_stratum": stratum,
                "selection_rule": PILOT_SELECTION_RULE,
                "task_id": task["task_id"],
                "candidate_incident_id": cid,
                "report_number": rep_no,
                "dataset_year": cand["dataset_year"],
                "dataset_id": cand["dataset_id"],
                "snapshot_id": cand["snapshot_id"],
                "source_offense_codes": cand["source_offense_codes"],
                "source_classification": cand["source_classification"],
                "scope_review_flag": cand["scope_review_flag"],
                "has_excluded_09d_rows": bool(cand["has_excluded_09d_rows"]),
                "excluded_09d_row_count": cand["excluded_09d_row_count"],
                "date_bounds": {
                    "earliest_incident_date": cand["earliest_incident_date"],
                    "latest_incident_date": cand["latest_incident_date"],
                    "earliest_from_time": cand["earliest_from_time"],
                    "latest_to_time": cand["latest_to_time"],
                    "reported_date": cand["reported_date"],
                    "earliest_reported_time": cand["earliest_reported_time"],
                    "incident_date_precision": cand["incident_date_precision"],
                },
                "location": {
                    "reported_block_or_intersection": cand["reported_block_or_intersection"],
                    "city_as_reported": cand["city_as_reported"],
                    "zip_as_reported": cand["zip_as_reported"],
                    "reporting_district": cand["reporting_district"],
                    "patrol_division": cand["patrol_division"],
                    "beats_as_reported": cand["beats_as_reported"],
                    "latitude": cand["latitude"],
                    "longitude": cand["longitude"],
                    "coordinate_precision": cand["coordinate_precision"],
                },
                "flags": {
                    "firearm_flag_values_normalized": cand["firearm_flag_values_normalized"],
                    "domestic_flag_values_raw": cand["domestic_flag_values_raw"],
                    "domestic_flag_values_normalized": cand["domestic_flag_values_normalized"],
                },
                "linked_source_rows_count": cand["linked_source_rows"],
                "involvement_roles_summary": cand["involvement_roles_summary"],
                "source_rows": raw_rows,
                "questions": json.loads(task["outstanding_questions_json"]),
            }
            packets.append(packet)

        conn.commit()
    finally:
        conn.close()

    all_path = output_dir / "pilot_tasks_input.jsonl"
    batch_a_path = output_dir / "pilot_tasks_batch_a.jsonl"
    batch_b_path = output_dir / "pilot_tasks_batch_b.jsonl"

    with all_path.open("w", encoding="utf-8") as f:
        for p in packets:
            f.write(json.dumps(p) + "\n")
    with batch_a_path.open("w", encoding="utf-8") as f:
        for p in packets[:5]:
            f.write(json.dumps(p) + "\n")
    with batch_b_path.open("w", encoding="utf-8") as f:
        for p in packets[5:]:
            f.write(json.dumps(p) + "\n")

    return packets


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    pkts = select_and_export_pilot_tasks(
        db_path=root / "data" / "kcmo_homicide.sqlite",
        output_dir=root / "data" / "research" / "pilot_batch_1",
    )
    print(f"Exported {len(pkts)} pilot task packets.")
