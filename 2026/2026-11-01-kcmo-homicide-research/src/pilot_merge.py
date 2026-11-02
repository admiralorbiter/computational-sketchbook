"""Coordinator validation, merge, and export pipeline for Step 1 (10-case 2020 pilot).

Only the Engineer/Coordinator runs this module to merge verifier-audited claims
into data/kcmo_homicide.sqlite while preserving proposed, verified, rejected,
and unresolved claims for audit.
"""

from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .importer import backup_existing_research
from .schema import VALID_REVIEW_STATES

CLAIM_EXPORT_COLUMNS = (
    "claim_id",
    "candidate_incident_id",
    "entity_type",
    "entity_id",
    "field_name",
    "proposed_value",
    "source_id",
    "source_url",
    "evidence_locator",
    "brief_supporting_paraphrase",
    "event_date",
    "date_precision",
    "source_published_at",
    "observed_at",
    "match_basis",
    "review_state",
    "review_note",
    "competing_claim_id",
    "created_by_role",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                records.append(json.loads(s))
    return records


def merge_and_export_pilot(
    db_path: Path,
    pilot_dir: Path,
    exports_dir: Path,
    research_backup_path: Path,
) -> dict[str, Any]:
    """Validate researcher + verifier JSONL outputs, merge into SQLite, and export deliverables."""
    input_packets = {
        p["candidate_incident_id"]: p
        for p in load_jsonl(pilot_dir / "pilot_tasks_input.jsonl")
    }
    res_a = load_jsonl(pilot_dir / "researcher_batch_a_output.jsonl")
    res_b = load_jsonl(pilot_dir / "researcher_batch_b_output.jsonl")
    research_by_cid = {r["candidate_incident_id"]: r for r in (res_a + res_b)}

    verifier_records = load_jsonl(pilot_dir / "verifier_review.jsonl")
    verifier_by_cid = {v["candidate_incident_id"]: v for v in verifier_records}

    if len(research_by_cid) != 10 or len(verifier_by_cid) != 10:
        raise ValueError(
            f"Expected 10 researcher packets and 10 verifier reviews; got {len(research_by_cid)} and {len(verifier_by_cid)}"
        )

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    merged_case_packets: list[dict[str, Any]] = []
    all_claims_for_export: list[dict[str, Any]] = []
    unresolved_rows: list[dict[str, Any]] = []

    total_research_seconds = 0
    total_verification_seconds = 0
    total_corrections = 0
    claim_state_counts: Counter[str] = Counter()

    try:
        # Clear any prior pilot claims/entities for these 10 cases before clean merge
        for cid in input_packets:
            for tbl in (
                "status_events",
                "claims",
                "defendant_charges",
                "case_defendants",
                "court_cases",
                "deceased_victims",
            ):
                conn.execute(f"DELETE FROM {tbl} WHERE candidate_incident_id = ?" if tbl != "defendant_charges" else
                             "DELETE FROM defendant_charges WHERE defendant_id IN (SELECT defendant_id FROM case_defendants WHERE candidate_incident_id = ?)", (cid,))

        for cid, in_pkt in sorted(input_packets.items(), key=lambda x: x[1]["pilot_rank"]):
            res = research_by_cid[cid]
            ver = verifier_by_cid[cid]

            res_sec = int(res.get("research_duration_seconds") or res.get("search_duration_seconds") or 180)
            ver_sec = int(ver.get("verification_duration_seconds") or 90)
            corr_cnt = int(ver.get("corrections_or_downgrades_count") or 0)
            total_research_seconds += res_sec
            total_verification_seconds += ver_sec
            total_corrections += corr_cnt

            narrative_summary = (
                res.get("case_narrative_summary")
                or res.get("proposed_incident_summary")
                or ver.get("verifier_summary")
            )

            # Map verifier claim decisions by claim_id
            ver_claim_map = {
                vc["claim_id"]: vc for vc in ver.get("verified_claims", [])
            }

            # Merge claims (researcher claims updated by verifier + any verifier-added claims)
            case_claims: list[dict[str, Any]] = []
            seen_claim_ids: set[str] = set()

            for raw_clm in res.get("proposed_claims", []):
                clm = dict(raw_clm)
                cid_clm = clm["claim_id"]
                seen_claim_ids.add(cid_clm)
                if cid_clm in ver_claim_map:
                    vdec = ver_claim_map[cid_clm]
                    clm["review_state"] = vdec["review_state"]
                    clm["review_note"] = vdec.get("verifier_note") or clm.get("review_note")
                    if "corrected_proposed_value" in vdec and vdec["corrected_proposed_value"] is not None:
                        clm["proposed_value"] = vdec["corrected_proposed_value"]
                    if "competing_claim_id" in vdec:
                        clm["competing_claim_id"] = vdec["competing_claim_id"]
                else:
                    clm["review_state"] = clm.get("review_state", "proposed")

                if clm["review_state"] not in VALID_REVIEW_STATES:
                    raise ValueError(f"Invalid review_state on {cid_clm}: {clm['review_state']}")
                if not clm.get("source_id") or not clm.get("evidence_locator") or not clm.get("brief_supporting_paraphrase"):
                    raise ValueError(f"Claim {cid_clm} missing required evidence pointer or paraphrase")

                claim_state_counts[clm["review_state"]] += 1
                case_claims.append(clm)

            # Include any additional claims created directly by verifier (e.g. competing claims)
            for vc in ver.get("verified_claims", []):
                if vc["claim_id"] not in seen_claim_ids and vc.get("field_name"):
                    clm = {
                        "claim_id": vc["claim_id"],
                        "candidate_incident_id": cid,
                        "entity_type": vc.get("entity_type", "incident"),
                        "entity_id": vc.get("entity_id", cid),
                        "field_name": vc["field_name"],
                        "proposed_value": vc.get("corrected_proposed_value") or vc.get("proposed_value"),
                        "source_id": vc.get("source_id", "VERIFIER_AUDIT"),
                        "source_url": vc.get("source_url"),
                        "evidence_locator": vc.get("evidence_locator", "Verifier source check"),
                        "brief_supporting_paraphrase": vc.get("brief_supporting_paraphrase", vc.get("verifier_note", "")),
                        "event_date": vc.get("event_date"),
                        "date_precision": vc.get("date_precision"),
                        "source_published_at": vc.get("source_published_at"),
                        "observed_at": vc.get("observed_at", now_utc),
                        "match_basis": vc.get("match_basis", "verifier_audit"),
                        "review_state": vc["review_state"],
                        "review_note": vc.get("verifier_note"),
                        "competing_claim_id": vc.get("competing_claim_id"),
                        "created_by_role": "evidence_verifier",
                    }
                    claim_state_counts[clm["review_state"]] += 1
                    case_claims.append(clm)

            for clm in case_claims:
                conn.execute(
                    """
                    INSERT INTO claims (
                        claim_id, candidate_incident_id, entity_type, entity_id,
                        field_name, proposed_value, source_id, source_url,
                        evidence_locator, brief_supporting_paraphrase,
                        event_date, date_precision, source_published_at,
                        observed_at, match_basis, review_state, review_note,
                        competing_claim_id, created_by_role
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        clm["claim_id"],
                        cid,
                        clm["entity_type"],
                        clm.get("entity_id"),
                        clm["field_name"],
                        str(clm["proposed_value"]) if clm.get("proposed_value") is not None else None,
                        clm["source_id"],
                        clm.get("source_url"),
                        clm["evidence_locator"],
                        clm["brief_supporting_paraphrase"],
                        clm.get("event_date"),
                        clm.get("date_precision"),
                        clm.get("source_published_at"),
                        clm["observed_at"],
                        clm["match_basis"],
                        clm["review_state"],
                        clm.get("review_note"),
                        clm.get("competing_claim_id"),
                        clm.get("created_by_role", "incident_and_outcome_researcher"),
                    ),
                )
                all_claims_for_export.append(clm)

            # Insert deceased_victims
            final_victims = ver.get("reviewed_victims") if "reviewed_victims" in ver else res.get("proposed_victims", [])
            for idx, v in enumerate(final_victims, start=1):
                v_state = v.get("verification_state") or ver.get("final_victim_verification_state", "verified")
                if v_state not in VALID_REVIEW_STATES:
                    v_state = "unresolved"
                name_status = v.get("name_status", "confirmed_named" if v.get("publicly_confirmed_name") else "unresolved")
                if name_status not in ("confirmed_named", "confirmed_unnamed", "not_researched", "searched_no_result", "inaccessible", "unresolved"):
                    name_status = "unresolved"
                conn.execute(
                    """
                    INSERT INTO deceased_victims (
                        victim_id, candidate_incident_id, victim_sequence,
                        publicly_confirmed_name, name_status,
                        age_reported, sex_reported, race_reported,
                        injury_date, injury_date_precision,
                        death_date, death_date_precision,
                        medical_cause_of_death, manner_of_death,
                        weapon_or_force_reported, reported_circumstances,
                        verification_state, supporting_claim_ids_json, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        v.get("victim_id", f"VIC:{cid}:{idx}"),
                        cid,
                        int(v.get("victim_sequence", idx)),
                        v.get("publicly_confirmed_name"),
                        name_status,
                        str(v["age_reported"]) if v.get("age_reported") is not None else None,
                        v.get("sex_reported"),
                        v.get("race_reported"),
                        v.get("injury_date"),
                        v.get("injury_date_precision"),
                        v.get("death_date"),
                        v.get("death_date_precision"),
                        v.get("medical_cause_of_death"),
                        v.get("manner_of_death"),
                        v.get("weapon_or_force_reported"),
                        v.get("reported_circumstances"),
                        v_state,
                        json.dumps(v.get("supporting_claim_ids", [])),
                        v.get("notes"),
                    ),
                )

            # Insert court_cases
            final_cases = ver.get("reviewed_court_cases") if "reviewed_court_cases" in ver else res.get("proposed_court_cases", [])
            valid_court_case_ids: set[str] = set()
            for idx, cc in enumerate(final_cases, start=1):
                cc_id = cc.get("court_case_id", f"CASE:{cid}:{idx}")
                valid_court_case_ids.add(cc_id)
                cc_state = cc.get("verification_state", "verified")
                if cc_state not in VALID_REVIEW_STATES:
                    cc_state = "unresolved"
                conn.execute(
                    """
                    INSERT INTO court_cases (
                        court_case_id, candidate_incident_id, court_docket_number,
                        court_jurisdiction, prosecutor_office, filing_date,
                        case_stage, verification_state, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cc_id,
                        cid,
                        cc.get("court_docket_number"),
                        cc.get("court_jurisdiction"),
                        cc.get("prosecutor_office"),
                        cc.get("filing_date"),
                        cc.get("case_stage", "unknown"),
                        cc_state,
                        cc.get("notes"),
                    ),
                )

            # Insert case_defendants
            final_defs = ver.get("reviewed_defendants") if "reviewed_defendants" in ver else res.get("proposed_defendants", [])
            for idx, df in enumerate(final_defs, start=1):
                df_id = df.get("defendant_id", f"DEF:{cid}:{idx}")
                cc_link = df.get("court_case_id") if df.get("court_case_id") in valid_court_case_ids else None
                d_state = df.get("verification_state", "verified")
                if d_state not in VALID_REVIEW_STATES:
                    d_state = "unresolved"
                d_name_status = df.get("name_status", "confirmed_named" if df.get("defendant_name") else "unknown")
                if d_name_status not in ("confirmed_named", "withheld_or_juvenile", "unknown", "not_researched", "unresolved"):
                    d_name_status = "unresolved"
                conn.execute(
                    """
                    INSERT INTO case_defendants (
                        defendant_id, candidate_incident_id, court_case_id,
                        defendant_sequence, defendant_name, name_status,
                        police_clearance_status, police_clearance_wording_raw, police_clearance_date,
                        prosecutor_action_status, prosecutor_wording_raw, prosecutor_action_date,
                        court_disposition_status, court_disposition_wording_raw,
                        disposition_date, sentence_summary, verification_state,
                        supporting_claim_ids_json, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        df_id,
                        cid,
                        cc_link,
                        int(df.get("defendant_sequence", idx)),
                        df.get("defendant_name"),
                        d_name_status,
                        df.get("police_clearance_status", "unknown"),
                        df.get("police_clearance_wording_raw"),
                        df.get("police_clearance_date"),
                        df.get("prosecutor_action_status", "unknown"),
                        df.get("prosecutor_wording_raw"),
                        df.get("prosecutor_action_date"),
                        df.get("court_disposition_status", "unknown"),
                        df.get("court_disposition_wording_raw"),
                        df.get("disposition_date"),
                        df.get("sentence_summary"),
                        d_state,
                        json.dumps(df.get("supporting_claim_ids", [])),
                        df.get("notes"),
                    ),
                )

            # Create dated status_events from verified/unresolved claims on status domains
            domain_map = {
                "inclusion_decision": "inclusion",
                "publicly_confirmed_name": "victim_verification",
                "medical_cause_of_death": "medical_cause",
                "police_clearance_status": "police_clearance",
                "prosecutor_action_status": "prosecutor_action",
                "court_disposition_status": "court_disposition",
            }
            for idx_se, clm in enumerate(case_claims, start=1):
                if clm["field_name"] in domain_map:
                    conn.execute(
                        """
                        INSERT INTO status_events (
                            status_event_id, candidate_incident_id, entity_type, entity_id,
                            status_domain, agency_original_wording, normalized_status,
                            effective_date_start, date_precision, source_published_at,
                            observed_at, source_id, source_url, claim_id,
                            review_state, review_note
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            f"SE:{in_pkt['report_number']}:{idx_se:02d}",
                            cid,
                            clm["entity_type"],
                            clm.get("entity_id") or cid,
                            domain_map[clm["field_name"]],
                            clm.get("evidence_locator"),
                            str(clm["proposed_value"]) if clm.get("proposed_value") is not None else "unknown",
                            clm.get("event_date"),
                            clm.get("date_precision"),
                            clm.get("source_published_at"),
                            clm["observed_at"],
                            clm["source_id"],
                            clm.get("source_url"),
                            clm["claim_id"],
                            clm["review_state"],
                            clm.get("review_note"),
                        ),
                    )

            # Update incident_candidates and research_tasks with verifier-approved states
            inc_dec = ver.get("final_inclusion_decision") or res.get("proposed_inclusion_decision", "unreviewed_candidate")
            vic_st = ver.get("final_victim_verification_state") or res.get("proposed_victim_verification_state", "unresolved")
            med_st = ver.get("final_medical_cause_state") or res.get("proposed_medical_cause_state", "unknown")
            pol_st = ver.get("final_police_clearance_state") or res.get("proposed_police_clearance_state", "unresolved")
            pro_st = ver.get("final_prosecutor_action_state") or res.get("proposed_prosecutor_action_state", "unresolved")
            crt_st = ver.get("final_court_outcome_state") or res.get("proposed_court_outcome_state", "unresolved")

            res_blockers = res.get("blockers") or []
            res_unres = res.get("unresolved_questions") or res.get("unresolved_questions_or_blockers") or []
            combined_blockers = list(dict.fromkeys(res_blockers + (ver.get("verifier_blockers") or [])))
            combined_unresolved = list(dict.fromkeys(res_unres + (ver.get("verifier_unresolved_questions") or [])))

            for uq in combined_unresolved:
                unresolved_rows.append(
                    {
                        "pilot_rank": in_pkt["pilot_rank"],
                        "candidate_incident_id": cid,
                        "report_number": in_pkt["report_number"],
                        "selection_stratum": in_pkt["selection_stratum"],
                        "inclusion_decision": inc_dec,
                        "unresolved_question": uq,
                        "blockers": "; ".join(combined_blockers),
                    }
                )

            conn.execute(
                """
                UPDATE incident_candidates
                   SET inclusion_decision = ?,
                       victim_verification_state = ?,
                       medical_cause_state = ?,
                       police_clearance_state = ?,
                       prosecutor_action_state = ?,
                       court_outcome_state = ?,
                       status_last_checked_at = '2026-11-01',
                       research_notes = ?
                 WHERE candidate_incident_id = ?
                """,
                (
                    inc_dec,
                    vic_st,
                    med_st,
                    pol_st,
                    pro_st,
                    crt_st,
                    ver.get("verifier_summary") or narrative_summary,
                    cid,
                ),
            )

            q_stage = "pilot_verified" if not combined_unresolved else "pilot_reviewed_with_open_questions"
            conn.execute(
                """
                UPDATE research_tasks
                   SET queue_stage = ?,
                       assigned_role = 'kcmo-case-researcher + kcmo-evidence-verifier',
                       sources_checked_json = ?,
                       progress_summary = ?,
                       blockers = ?,
                       attempt_count = 1,
                       latest_search_date = '2026-11-01',
                       outstanding_questions_json = ?,
                       updated_at = ?
                 WHERE candidate_incident_id = ?
                """,
                (
                    q_stage,
                    json.dumps(res.get("sources_checked", [])),
                    ver.get("verifier_summary") or narrative_summary,
                    "; ".join(combined_blockers) if combined_blockers else None,
                    json.dumps(combined_unresolved),
                    now_utc,
                    cid,
                ),
            )

            merged_case_packets.append(
                {
                    "pilot_rank": in_pkt["pilot_rank"],
                    "candidate_incident_id": cid,
                    "report_number": in_pkt["report_number"],
                    "selection_stratum": in_pkt["selection_stratum"],
                    "date_bounds": in_pkt["date_bounds"],
                    "location": in_pkt["location"],
                    "source_offense_codes": in_pkt["source_offense_codes"],
                    "scope_review_flag": in_pkt["scope_review_flag"],
                    "linked_source_rows_count": in_pkt["linked_source_rows_count"],
                    "involvement_roles_summary": in_pkt["involvement_roles_summary"],
                    "final_states": {
                        "inclusion_decision": inc_dec,
                        "victim_verification_state": vic_st,
                        "medical_cause_state": med_st,
                        "police_clearance_state": pol_st,
                        "prosecutor_action_state": pro_st,
                        "court_outcome_state": crt_st,
                    },
                    "case_narrative_summary": narrative_summary,
                    "verifier_summary": ver.get("verifier_summary"),
                    "effort_and_quality_metrics": {
                        "research_duration_seconds": res_sec,
                        "verification_duration_seconds": ver_sec,
                        "total_case_seconds": res_sec + ver_sec,
                        "verifier_corrections_or_downgrades": corr_cnt,
                        "claims_total": len(case_claims),
                        "claims_by_review_state": dict(Counter(c["review_state"] for c in case_claims)),
                    },
                    "sources_checked": res.get("sources_checked", []),
                    "victims": final_victims,
                    "court_cases": final_cases,
                    "defendants": final_defs,
                    "claims": case_claims,
                    "blockers": combined_blockers,
                    "unresolved_questions": combined_unresolved,
                }
            )

        conn.commit()
        backup_existing_research(conn, research_backup_path=research_backup_path)
    finally:
        conn.close()

    # Export deliverables
    exports_dir.mkdir(parents=True, exist_ok=True)
    packets_json_path = exports_dir / "pilot_2020_case_packets.json"
    packets_md_path = exports_dir / "pilot_2020_case_packets.md"
    claims_csv_path = exports_dir / "pilot_2020_claims_evidence.csv"
    claims_jsonl_path = exports_dir / "pilot_2020_claims_evidence.jsonl"
    unresolved_csv_path = exports_dir / "pilot_2020_unresolved_questions.csv"
    unresolved_md_path = exports_dir / "pilot_2020_unresolved_questions.md"

    summary_payload = {
        "pilot_batch": "pilot_batch_1_2020",
        "selection_rule": merged_case_packets[0]["selection_stratum"] if merged_case_packets else "",
        "cases_count": len(merged_case_packets),
        "total_claims": len(all_claims_for_export),
        "claims_by_review_state": dict(claim_state_counts),
        "total_research_seconds": total_research_seconds,
        "total_verification_seconds": total_verification_seconds,
        "mean_seconds_per_case": round((total_research_seconds + total_verification_seconds) / len(merged_case_packets), 1),
        "total_verifier_corrections_or_downgrades": total_corrections,
        "mean_corrections_per_case": round(total_corrections / len(merged_case_packets), 2),
        "estimated_hours_for_remaining_152_cases_2020": round(
            152 * ((total_research_seconds + total_verification_seconds) / len(merged_case_packets)) / 3600.0, 2
        ),
        "case_packets": merged_case_packets,
    }
    packets_json_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    # Write human-readable Markdown case packets
    md_lines = [
        "# Step 1 — Ten-Case 2020 Pilot Case Packets",
        "",
        f"- **Total Cases:** {len(merged_case_packets)}",
        f"- **Total Claims Extracted & Audited:** {len(all_claims_for_export)} (`{dict(claim_state_counts)}`)",
        f"- **Total Research + Verification Time:** {total_research_seconds + total_verification_seconds}s ({summary_payload['mean_seconds_per_case']}s / case)",
        f"- **Verifier Corrections / Downgrades:** {total_corrections} ({summary_payload['mean_corrections_per_case']} / case)",
        f"- **Estimated Effort for Remaining 152 Cases in 2020:** ~{summary_payload['estimated_hours_for_remaining_152_cases_2020']} agent-hours",
        "",
        "---",
        "",
    ]
    for pkt in merged_case_packets:
        fs = pkt["final_states"]
        em = pkt["effort_and_quality_metrics"]
        md_lines.extend([
            f"## Case {pkt['pilot_rank']}: `{pkt['candidate_incident_id']}` ({pkt['selection_stratum']})",
            f"- **Incident Date / Time:** `{pkt['date_bounds']['earliest_incident_date']}` (`{pkt['date_bounds']['earliest_from_time']}`)",
            f"- **Reported Location:** `{pkt['location']['reported_block_or_intersection']}` (`{pkt['location']['city_as_reported']}`, `{pkt['location']['zip_as_reported']}`, Div `{pkt['location']['patrol_division']}`, Beat `{pkt['location']['beats_as_reported']}`)",
            f"- **Source Code & Scope Flag:** `{pkt['source_offense_codes']}` | `{pkt['scope_review_flag']}` | `{pkt['linked_source_rows_count']}` rows (`{pkt['involvement_roles_summary']}`)",
            f"- **Reviewed States:** Inclusion=`{fs['inclusion_decision']}` | Victim=`{fs['victim_verification_state']}` | Medical=`{fs['medical_cause_state']}` | Police=`{fs['police_clearance_state']}` | Prosecutor=`{fs['prosecutor_action_state']}` | Court=`{fs['court_outcome_state']}`",
            f"- **Effort & Verification:** Research `{em['research_duration_seconds']}s` + Verifier `{em['verification_duration_seconds']}s` | Corrections/Downgrades=`{em['verifier_corrections_or_downgrades']}` | Claims=`{em['claims_by_review_state']}`",
            "",
            f"**Case Narrative Summary:** {pkt['case_narrative_summary']}",
            "",
            f"**Verifier Audit Summary:** {pkt['verifier_summary']}",
            "",
            "### Deceased Victims",
        ])
        if pkt["victims"]:
            for v in pkt["victims"]:
                md_lines.append(
                    f"- `{v.get('victim_id')}`: **{v.get('publicly_confirmed_name') or 'Unnamed / Unconfirmed'}** (`{v.get('name_status')}`) | {v.get('race_reported')}/{v.get('sex_reported')}/age {v.get('age_reported')} | Death: `{v.get('death_date')}` | Cause: `{v.get('medical_cause_of_death') or 'Not publicly released (ME restricted)'}` | Weapon: `{v.get('weapon_or_force_reported')}`"
                )
        else:
            md_lines.append("- None confirmed as KCMO homicide victim (see inclusion decision / notes).")
        md_lines.append("")
        md_lines.append("### Defendants & Court Outcomes")
        if pkt["defendants"]:
            for d in pkt["defendants"]:
                md_lines.append(
                    f"- `{d.get('defendant_id')}`: **{d.get('defendant_name') or 'Unidentified / Uncharged'}** | Police: `{d.get('police_clearance_status')}` (`{d.get('police_clearance_wording_raw')}`) | Prosecutor: `{d.get('prosecutor_action_status')}` (`{d.get('prosecutor_action_date') or 'n/a'}`) | Court: `{d.get('court_disposition_status')}` (`{d.get('disposition_date') or 'n/a'}`) — {d.get('sentence_summary') or d.get('court_disposition_wording_raw') or 'n/a'}"
                )
        else:
            md_lines.append("- No charged defendant record.")
        md_lines.append("")
        md_lines.append("### Unresolved Questions & Blockers")
        for uq in pkt["unresolved_questions"]:
            md_lines.append(f"- {uq}")
        md_lines.extend(["", "---", ""])

    packets_md_path.write_text("\n".join(md_lines), encoding="utf-8")

    # Write human-readable Unresolved Questions Markdown
    uq_md = [
        "# Step 1 — Unresolved Questions & Source Limitations (10-Case 2020 Pilot)",
        "",
        "| Rank | Report ID | Stratum | Inclusion Decision | Unresolved Question | Blockers |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ]
    for ur in unresolved_rows:
        uq_md.append(
            f"| {ur['pilot_rank']} | `{ur['report_number']}` | `{ur['selection_stratum']}` | `{ur['inclusion_decision']}` | {ur['unresolved_question']} | {ur['blockers']} |"
        )
    unresolved_md_path.write_text("\n".join(uq_md) + "\n", encoding="utf-8")

    with claims_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(CLAIM_EXPORT_COLUMNS))
        writer.writeheader()
        for clm in all_claims_for_export:
            writer.writerow({k: clm.get(k) for k in CLAIM_EXPORT_COLUMNS})

    with claims_jsonl_path.open("w", encoding="utf-8") as f:
        for clm in all_claims_for_export:
            f.write(json.dumps(clm) + "\n")

    with unresolved_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "pilot_rank",
                "candidate_incident_id",
                "report_number",
                "selection_stratum",
                "inclusion_decision",
                "unresolved_question",
                "blockers",
            ],
        )
        writer.writeheader()
        for ur in unresolved_rows:
            writer.writerow(ur)

    return {
        "cases_merged": len(merged_case_packets),
        "total_claims": len(all_claims_for_export),
        "claims_by_review_state": dict(claim_state_counts),
        "unresolved_questions_count": len(unresolved_rows),
        "total_research_seconds": total_research_seconds,
        "total_verification_seconds": total_verification_seconds,
        "total_verifier_corrections": total_corrections,
        "packets_json_path": str(packets_json_path),
        "packets_md_path": str(packets_md_path),
        "claims_csv_path": str(claims_csv_path),
        "claims_jsonl_path": str(claims_jsonl_path),
        "unresolved_csv_path": str(unresolved_csv_path),
        "unresolved_md_path": str(unresolved_md_path),
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    result = merge_and_export_pilot(
        db_path=root / "data" / "kcmo_homicide.sqlite",
        pilot_dir=root / "data" / "research" / "pilot_batch_1",
        exports_dir=root / "exports",
        research_backup_path=root / "data" / "research" / "reviewed_bundle.json",
    )
    print(json.dumps(result, indent=2))

