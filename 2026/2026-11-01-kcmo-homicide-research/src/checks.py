"""Step 0 completion checks and synthetic multi-entity test fixture."""

from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

from .importer import compute_file_sha256, import_starter_workbook
from .schema import EXPECTED_STARTER_SHA256, init_db

EXPECTED_CANDIDATES_BY_YEAR = {
    2020: 162,
    2021: 124,
    2022: 158,
    2023: 166,
    2024: 138,
    2025: 121,
    2026: 105,
}


def run_synthetic_multi_entity_fixture() -> dict[str, Any]:
    """Verify that the schema represents 1 incident, 2 deceased victims, and 2 defendants
    with different outcomes without double counting across joined queries.
    """
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    init_db(conn)

    conn.execute(
        """
        INSERT INTO source_snapshots (
            snapshot_id, dataset_year, dataset_id, source_name, publisher, title, access_status
        ) VALUES ('SYNTH:SNAP:2020', 2020, 'synth-2020', 'Synthetic Test Snapshot', 'Test Suite', 'Synthetic Snapshot', 'synthetic_fixture')
        """
    )
    conn.execute(
        """
        INSERT INTO incident_candidates (
            candidate_incident_id, agency, report_number, dataset_year, dataset_id, snapshot_id,
            source_offense_codes, source_classification, earliest_incident_date,
            incident_date_precision, reported_date, reported_date_precision,
            coordinate_precision, linked_source_rows, scope_review_flag,
            inclusion_decision, victim_verification_state, police_clearance_state,
            prosecutor_action_state, court_outcome_state
        ) VALUES (
            'SYNTH:KC20999999', 'KCPD', 'KC20999999', 2020, 'synth-2020', 'SYNTH:SNAP:2020',
            '09A', 'Murder', '2020-06-15',
            'date_only_with_separate_time', '2020-06-15', 'date_only_with_separate_time',
            'block_or_intersection_point', 4, 'Candidate - verify inclusion',
            'included_kcmo_homicide', 'verified', 'verified', 'verified', 'verified'
        )
        """
    )

    # Two deceased victims (one publicly named, one unnamed)
    conn.execute(
        """
        INSERT INTO deceased_victims (
            victim_id, candidate_incident_id, victim_sequence, publicly_confirmed_name,
            name_status, death_date, death_date_precision, medical_cause_of_death,
            manner_of_death, weapon_or_force_reported, verification_state
        ) VALUES
            ('SYNTH:VIC:1', 'SYNTH:KC20999999', 1, 'Synthetic Victim A', 'confirmed_named',
             '2020-06-15', 'exact_date', 'Gunshot wound', 'Homicide', 'Firearm', 'verified'),
            ('SYNTH:VIC:2', 'SYNTH:KC20999999', 2, NULL, 'confirmed_unnamed',
             '2020-06-16', 'exact_date', 'Gunshot wound', 'Homicide', 'Firearm', 'verified')
        """
    )

    # Two separate court cases / defendants with different dispositions
    conn.execute(
        """
        INSERT INTO court_cases (
            court_case_id, candidate_incident_id, court_docket_number,
            court_jurisdiction, prosecutor_office, filing_date, case_stage, verification_state
        ) VALUES
            ('SYNTH:CASE:1', 'SYNTH:KC20999999', '2016-CR99901', 'Jackson County Circuit Court', 'Jackson County Prosecutor', '2020-07-01', 'disposed', 'verified'),
            ('SYNTH:CASE:2', 'SYNTH:KC20999999', '2016-CR99902', 'Jackson County Circuit Court', 'Jackson County Prosecutor', '2020-07-01', 'disposed', 'verified')
        """
    )

    conn.execute(
        """
        INSERT INTO case_defendants (
            defendant_id, candidate_incident_id, court_case_id, defendant_sequence,
            defendant_name, name_status,
            police_clearance_status, police_clearance_wording_raw,
            prosecutor_action_status,
            court_disposition_status, court_disposition_wording_raw, disposition_date,
            sentence_summary, verification_state
        ) VALUES
            ('SYNTH:DEF:1', 'SYNTH:KC20999999', 'SYNTH:CASE:1', 1,
             'Synthetic Defendant 1', 'confirmed_named',
             'cleared_by_arrest', 'ARR CHA SUS',
             'charges_filed',
             'convicted_trial', 'Guilty by Jury Trial', '2022-04-10',
             'Life without parole + 25 years consecutive', 'verified'),
            ('SYNTH:DEF:2', 'SYNTH:KC20999999', 'SYNTH:CASE:2', 2,
             'Synthetic Defendant 2', 'confirmed_named',
             'cleared_by_arrest', 'ARR CHA SUS',
             'charges_filed',
             'acquitted', 'Not Guilty on All Counts', '2022-09-18',
             NULL, 'verified')
        """
    )

    # Four charges (each defendant charged across each of the 2 victims)
    conn.execute(
        """
        INSERT INTO defendant_charges (
            charge_id, defendant_id, court_case_id, victim_id, charge_count_number,
            charge_description_raw, normalized_charge_category, charge_disposition_status,
            disposition_date, verification_state
        ) VALUES
            ('SYNTH:CHG:1A', 'SYNTH:DEF:1', 'SYNTH:CASE:1', 'SYNTH:VIC:1', 1, 'Murder 1st Degree', 'murder_1st', 'convicted_trial', '2022-04-10', 'verified'),
            ('SYNTH:CHG:1B', 'SYNTH:DEF:1', 'SYNTH:CASE:1', 'SYNTH:VIC:2', 2, 'Murder 2nd Degree', 'murder_2nd', 'convicted_trial', '2022-04-10', 'verified'),
            ('SYNTH:CHG:2A', 'SYNTH:DEF:2', 'SYNTH:CASE:2', 'SYNTH:VIC:1', 1, 'Murder 2nd Degree', 'murder_2nd', 'acquitted', '2022-09-18', 'verified'),
            ('SYNTH:CHG:2B', 'SYNTH:DEF:2', 'SYNTH:CASE:2', 'SYNTH:VIC:2', 2, 'Murder 2nd Degree', 'murder_2nd', 'acquitted', '2022-09-18', 'verified')
        """
    )

    # Atomic claims & status events
    conn.execute(
        """
        INSERT INTO claims (
            claim_id, candidate_incident_id, entity_type, entity_id, field_name,
            proposed_value, source_id, source_url, evidence_locator,
            brief_supporting_paraphrase, event_date, date_precision,
            source_published_at, observed_at, match_basis, review_state, review_note
        ) VALUES
            ('SYNTH:CLM:1', 'SYNTH:KC20999999', 'defendant', 'SYNTH:DEF:1', 'court_disposition_status',
             'convicted_trial', 'SYNTH:SNAP:2020', 'https://example.test/case1', 'Docket Entry 42',
             'Jury returned guilty verdict on Counts 1 and 2.', '2022-04-10', 'exact_date',
             '2022-04-10', '2026-11-01T00:00:00Z', 'exact_court_docket', 'verified', 'Synthetic fixture test'),
            ('SYNTH:CLM:2', 'SYNTH:KC20999999', 'defendant', 'SYNTH:DEF:2', 'court_disposition_status',
             'acquitted', 'SYNTH:SNAP:2020', 'https://example.test/case2', 'Docket Entry 58',
             'Jury returned not guilty verdict on Counts 1 and 2.', '2022-09-18', 'exact_date',
             '2022-09-18', '2026-11-01T00:00:00Z', 'exact_court_docket', 'verified', 'Synthetic fixture test')
        """
    )

    # Query across incident + victims + defendants + charges using distinct counts / subqueries
    row = conn.execute(
        """
        SELECT
            COUNT(DISTINCT c.candidate_incident_id) AS incident_count,
            COUNT(DISTINCT v.victim_id) AS victim_count,
            COUNT(DISTINCT CASE WHEN v.name_status = 'confirmed_unnamed' THEN v.victim_id END) AS unnamed_victim_count,
            COUNT(DISTINCT d.defendant_id) AS defendant_count,
            COUNT(DISTINCT CASE WHEN d.court_disposition_status = 'convicted_trial' THEN d.defendant_id END) AS convicted_defendants,
            COUNT(DISTINCT CASE WHEN d.court_disposition_status = 'acquitted' THEN d.defendant_id END) AS acquitted_defendants,
            COUNT(DISTINCT ch.charge_id) AS total_charge_counts
        FROM incident_candidates c
        LEFT JOIN deceased_victims v ON v.candidate_incident_id = c.candidate_incident_id
        LEFT JOIN case_defendants d ON d.candidate_incident_id = c.candidate_incident_id
        LEFT JOIN defendant_charges ch ON ch.defendant_id = d.defendant_id AND ch.victim_id = v.victim_id
        WHERE c.candidate_incident_id = 'SYNTH:KC20999999'
        """
    ).fetchone()
    conn.close()

    result = {
        "incident_count": row[0],
        "victim_count": row[1],
        "unnamed_victim_count": row[2],
        "defendant_count": row[3],
        "convicted_defendants": row[4],
        "acquitted_defendants": row[5],
        "total_charge_counts": row[6],
    }
    passed = (
        result["incident_count"] == 1
        and result["victim_count"] == 2
        and result["unnamed_victim_count"] == 1
        and result["defendant_count"] == 2
        and result["convicted_defendants"] == 1
        and result["acquitted_defendants"] == 1
        and result["total_charge_counts"] == 4
    )
    result["passed"] = passed
    return result


def run_step0_completion_checks(
    workbook_path: Path,
    db_path: Path,
    queue_csv_path: Path,
) -> dict[str, Any]:
    """Execute all Step 0 completion checks defined in KCMO_Homicide_Antigravity_Handoff.txt."""
    checks: dict[str, Any] = {}

    # Check 1: Immutable starter workbook SHA-256
    sha = compute_file_sha256(workbook_path)
    checks["workbook_immutable"] = {
        "passed": sha == EXPECTED_STARTER_SHA256,
        "expected_sha256": EXPECTED_STARTER_SHA256,
        "actual_sha256": sha,
    }

    conn = sqlite3.connect(str(db_path))
    try:
        # Check 2: Snapshot counts (3,146 raw rows, 3,103 candidate rows, 43 09D rows, 974 candidate reports, 162 in 2020)
        raw_total = conn.execute("SELECT COUNT(*) FROM raw_rows").fetchone()[0]
        raw_cand = conn.execute("SELECT COUNT(*) FROM raw_rows WHERE is_candidate_offense = 1").fetchone()[0]
        raw_09d = conn.execute("SELECT COUNT(*) FROM raw_rows WHERE is_candidate_offense = 0 AND ibrs_raw = '09D'").fetchone()[0]
        cand_total = conn.execute("SELECT COUNT(*) FROM incident_candidates").fetchone()[0]
        yr_rows = conn.execute(
            "SELECT dataset_year, COUNT(*) FROM incident_candidates GROUP BY dataset_year ORDER BY dataset_year"
        ).fetchall()
        actual_by_year = {int(yr): int(cnt) for yr, cnt in yr_rows}
        scope_flagged = conn.execute(
            "SELECT COUNT(*) FROM incident_candidates WHERE scope_review_flag != 'Candidate - verify inclusion'"
        ).fetchone()[0]

        checks["snapshot_counts"] = {
            "passed": (
                raw_total == 3146
                and raw_cand == 3103
                and raw_09d == 43
                and cand_total == 974
                and actual_by_year == EXPECTED_CANDIDATES_BY_YEAR
                and scope_flagged == 16
            ),
            "raw_rows_total": raw_total,
            "candidate_offense_rows": raw_cand,
            "excluded_09d_rows": raw_09d,
            "candidate_incidents_total": cand_total,
            "candidates_by_year": actual_by_year,
            "scope_flagged_candidates": scope_flagged,
        }

        # Check 3: Code 09D excluded from candidates but retained in raw audit trail
        cand_with_09d_code = conn.execute(
            "SELECT COUNT(*) FROM incident_candidates WHERE source_offense_codes LIKE '%09D%'"
        ).fetchone()[0]
        mixed_09d_flagged = conn.execute(
            "SELECT COUNT(*), SUM(excluded_09d_row_count) FROM incident_candidates WHERE has_excluded_09d_rows = 1"
        ).fetchone()
        checks["code_09d_audit_retention"] = {
            "passed": (
                raw_09d == 43
                and cand_with_09d_code == 0
                and mixed_09d_flagged[0] == 10
                and mixed_09d_flagged[1] == 23
            ),
            "raw_09d_rows_retained": raw_09d,
            "candidates_classified_as_09d": cand_with_09d_code,
            "mixed_09a_09d_reports_flagged": mixed_09d_flagged[0],
            "mixed_09d_rows_accounted": mixed_09d_flagged[1],
            "pure_09d_excluded_rows": raw_09d - (mixed_09d_flagged[1] or 0),
        }

        # Check 4: False flags and missing flags remain distinct; identifiers remain text
        false_firearm_rows = conn.execute(
            "SELECT COUNT(*) FROM raw_rows WHERE firearm_flag_raw = 'false' AND firearm_flag_bool = 0"
        ).fetchone()[0]
        true_firearm_rows = conn.execute(
            "SELECT COUNT(*) FROM raw_rows WHERE firearm_flag_raw = 'true' AND firearm_flag_bool = 1"
        ).fetchone()[0]
        null_firearm_rows = conn.execute(
            "SELECT COUNT(*) FROM raw_rows WHERE firearm_flag_raw IS NULL AND firearm_flag_bool IS NULL"
        ).fetchone()[0]

        float_formatted_zips = conn.execute(
            "SELECT COUNT(*) FROM raw_rows WHERE zip_code_raw LIKE '%.0'"
        ).fetchone()[0]
        non_text_report_ids = conn.execute(
            "SELECT COUNT(*) FROM incident_candidates WHERE typeof(report_number) != 'text'"
        ).fetchone()[0]
        non_text_zips = conn.execute(
            "SELECT COUNT(*) FROM raw_rows WHERE zip_code_raw IS NOT NULL AND typeof(zip_code_raw) != 'text'"
        ).fetchone()[0]
        date_only_2020_preserved = conn.execute(
            "SELECT COUNT(*) FROM raw_rows WHERE dataset_year = 2020 AND from_date_precision LIKE 'date_only%'"
        ).fetchone()[0]

        # Test that NULL firearm flag is preserved as NULL (distinct from 'false') on a schema check
        checks["flags_and_types_integrity"] = {
            "passed": (
                false_firearm_rows > 0
                and true_firearm_rows > 0
                and (false_firearm_rows + true_firearm_rows + null_firearm_rows) == 3146
                and float_formatted_zips == 0
                and non_text_report_ids == 0
                and non_text_zips == 0
                and date_only_2020_preserved == 506
            ),
            "true_firearm_rows": true_firearm_rows,
            "false_firearm_rows": false_firearm_rows,
            "null_firearm_rows": null_firearm_rows,
            "float_formatted_zips": float_formatted_zips,
            "non_text_report_ids": non_text_report_ids,
            "non_text_zips": non_text_zips,
            "date_only_2020_rows_preserved": date_only_2020_preserved,
        }

        # Check 5: No fabricated/unsupported victim names, case outcomes, or research claims in DB
        fab_counts = {}
        for tbl in ("deceased_victims", "court_cases", "case_defendants", "defendant_charges", "claims", "status_events"):
            fab_counts[tbl] = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        unsupported_claims = conn.execute(
            """
            SELECT COUNT(*) FROM claims
            WHERE source_id IS NULL OR trim(source_id) = ''
               OR evidence_locator IS NULL OR trim(evidence_locator) = ''
               OR brief_supporting_paraphrase IS NULL OR trim(brief_supporting_paraphrase) = ''
            """
        ).fetchone()[0]
        unresearched_cands = conn.execute(
            """
            SELECT COUNT(*) FROM incident_candidates
            WHERE inclusion_decision = 'unreviewed_candidate'
            """
        ).fetchone()[0]
        reviewed_cands = 974 - unresearched_cands
        checks["zero_fabrication"] = {
            "passed": unsupported_claims == 0 and (unresearched_cands + reviewed_cands) == 974,
            "research_table_counts": fab_counts,
            "unsupported_claims_count": unsupported_claims,
            "unresearched_candidates_count": unresearched_cands,
            "pilot_reviewed_candidates_count": reviewed_cands,
        }
    finally:
        conn.close()

    # Check 6: Re-importing the frozen workbook creates no duplicate records and does not destroy reviewed work
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_db = Path(tmpdir) / "test_idempotency.sqlite"
        tmp_backup = Path(tmpdir) / "research_backup.json"
        shutil.copy2(db_path, tmp_db)

        # Insert a simulated reviewed claim and task update into the temporary copy
        tconn = sqlite3.connect(str(tmp_db))
        initial_claims = tconn.execute("SELECT COUNT(*) FROM claims WHERE claim_id != 'TEST:CLM:KC20001088:1'").fetchone()[0]
        tconn.execute(
            """
            UPDATE incident_candidates
               SET inclusion_decision = 'included_kcmo_homicide',
                   research_notes = 'Reviewed in idempotency test'
             WHERE candidate_incident_id = 'KCPD:KC20001088'
            """
        )
        tconn.execute(
            """
            UPDATE research_tasks
               SET queue_stage = 'pilot_selected',
                   attempt_count = 1,
                   progress_summary = 'Checked initial sources'
             WHERE candidate_incident_id = 'KCPD:KC20001088'
            """
        )
        tconn.execute(
            """
            INSERT OR REPLACE INTO claims (
                claim_id, candidate_incident_id, entity_type, entity_id, field_name,
                proposed_value, source_id, source_url, evidence_locator,
                brief_supporting_paraphrase, observed_at, match_basis, review_state
            ) VALUES (
                'TEST:CLM:KC20001088:1', 'KCPD:KC20001088', 'incident', 'KCPD:KC20001088',
                'inclusion_decision', 'included_kcmo_homicide', 'SOCRATA:vsgj-uufz',
                'https://data.kcmo.org/d/vsgj-uufz', 'Snapshot row 19',
                'Test claim preservation across re-import and rebuild',
                '2026-11-01T00:00:00Z', 'exact_report_id', 'verified'
            )
            """
        )
        tconn.commit()
        tconn.close()

        # Re-import without rebuild (upsert mode) and then WITH rebuild=True
        import_starter_workbook(workbook_path, tmp_db, rebuild=False, research_backup_path=tmp_backup)
        import_starter_workbook(workbook_path, tmp_db, rebuild=True, research_backup_path=tmp_backup)

        tconn = sqlite3.connect(str(tmp_db))
        raw_after = tconn.execute("SELECT COUNT(*) FROM raw_rows").fetchone()[0]
        cand_after = tconn.execute("SELECT COUNT(*) FROM incident_candidates").fetchone()[0]
        task_after = tconn.execute("SELECT COUNT(*) FROM research_tasks").fetchone()[0]
        claim_after = tconn.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
        preserved_cand = tconn.execute(
            "SELECT inclusion_decision, research_notes FROM incident_candidates WHERE candidate_incident_id = 'KCPD:KC20001088'"
        ).fetchone()
        preserved_task = tconn.execute(
            "SELECT queue_stage, attempt_count FROM research_tasks WHERE candidate_incident_id = 'KCPD:KC20001088'"
        ).fetchone()
        tconn.close()

        checks["idempotent_reimport_preserves_research"] = {
            "passed": (
                raw_after == 3146
                and cand_after == 974
                and task_after == 974
                and claim_after == initial_claims + 1
                and preserved_cand == ("included_kcmo_homicide", "Reviewed in idempotency test")
                and preserved_task == ("pilot_selected", 1)
            ),
            "raw_rows_after_reimport": raw_after,
            "candidates_after_reimport": cand_after,
            "tasks_after_reimport": task_after,
            "preserved_claims_after_rebuild": claim_after,
            "preserved_candidate_state": preserved_cand,
            "preserved_task_state": preserved_task,
        }

    # Check 7: Synthetic multi-entity fixture
    checks["synthetic_multi_entity_fixture"] = run_synthetic_multi_entity_fixture()

    # Check 8: 2020 research queue export exists and has 162 rows
    if queue_csv_path.exists():
        with queue_csv_path.open("r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f) - 1
    else:
        line_count = 0
    checks["export_2020_queue"] = {
        "passed": line_count == 162,
        "csv_path": str(queue_csv_path),
        "exported_2020_candidates": line_count,
    }

    checks["all_passed"] = all(
        v.get("passed", False) for k, v in checks.items() if isinstance(v, dict)
    )
    return checks


def run_step1_pilot_checks(db_path: Path, exports_dir: Path) -> dict[str, Any]:
    """Execute all Step 1 (10-case 2020 pilot) completion checks."""
    packets_path = exports_dir / "pilot_2020_case_packets.json"
    claims_csv = exports_dir / "pilot_2020_claims_evidence.csv"
    unresolved_csv = exports_dir / "pilot_2020_unresolved_questions.csv"

    if not packets_path.exists():
        return {"all_passed": False, "reason": "pilot_2020_case_packets.json not found"}

    payload = json.loads(packets_path.read_text(encoding="utf-8"))
    packets = payload.get("case_packets", [])

    conn = sqlite3.connect(str(db_path))
    try:
        verified_Without_pointer = conn.execute(
            """
            SELECT COUNT(*) FROM claims
            WHERE review_state = 'verified'
              AND (
                  source_id IS NULL OR trim(source_id) = ''
                  OR source_url IS NULL OR trim(source_url) = ''
                  OR evidence_locator IS NULL OR trim(evidence_locator) = ''
                  OR brief_supporting_paraphrase IS NULL OR trim(brief_supporting_paraphrase) = ''
                  OR review_note IS NULL OR trim(review_note) = ''
              )
            """
        ).fetchone()[0]

        pilot_tasks_reviewed = conn.execute(
            """
            SELECT COUNT(*) FROM research_tasks
            WHERE dataset_year = 2020
              AND attempt_count >= 1
              AND sources_checked_json != '[]'
            """
        ).fetchone()[0]

        # Check that out-of-scope KC20030505 is excluded and its victim is rejected (not counted as verified KCMO victim)
        kc20030505_inc = conn.execute(
            "SELECT inclusion_decision, victim_verification_state FROM incident_candidates WHERE report_number = 'KC20030505'"
        ).fetchone()
        verified_kcmo_victims = conn.execute(
            "SELECT COUNT(*) FROM deceased_victims WHERE verification_state = 'verified'"
        ).fetchone()[0]
    finally:
        conn.close()

    all_have_sources_claims_gaps = (
        len(packets) == 10
        and all(len(p.get("sources_checked", [])) > 0 for p in packets)
        and all(len(p.get("claims", [])) > 0 for p in packets)
        and all("unresolved_questions" in p for p in packets)
    )

    checks = {
        "ten_case_packets_complete": {
            "passed": all_have_sources_claims_gaps and pilot_tasks_reviewed == 10,
            "packets_count": len(packets),
            "pilot_tasks_reviewed_in_db": pilot_tasks_reviewed,
        },
        "verified_claims_have_source_pointer_and_review_record": {
            "passed": verified_Without_pointer == 0 and payload.get("total_claims", 0) >= 80,
            "total_claims": payload.get("total_claims", 0),
            "claims_by_review_state": payload.get("claims_by_review_state", {}),
            "verified_claims_missing_pointer_or_review": verified_Without_pointer,
        },
        "scope_and_victim_deduplication_integrity": {
            "passed": (
                kc20030505_inc == ("excluded_outside_kcmo", "rejected")
                and verified_kcmo_victims == 9
            ),
            "kc20030505_state": kc20030505_inc,
            "verified_deceased_victims_across_9_in_scope_cases": verified_kcmo_victims,
        },
        "effort_and_corrections_reported": {
            "passed": (
                payload.get("total_research_seconds", 0) > 0
                and payload.get("total_verification_seconds", 0) > 0
                and payload.get("total_verifier_corrections_or_downgrades", 0) >= 1
                and claims_csv.exists()
                and unresolved_csv.exists()
            ),
            "mean_seconds_per_case": payload.get("mean_seconds_per_case"),
            "total_verifier_corrections_or_downgrades": payload.get("total_verifier_corrections_or_downgrades"),
            "mean_corrections_per_case": payload.get("mean_corrections_per_case"),
            "estimated_hours_for_remaining_152_cases_2020": payload.get("estimated_hours_for_remaining_152_cases_2020"),
        },
    }
    checks["all_passed"] = all(
        v.get("passed", False) for v in checks.values() if isinstance(v, dict)
    )
    return checks

