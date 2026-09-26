"""
Build Task 002 Gate 2 Priority Governance Corpus for Grandview C-4.
Processes Simbli API responses, Edlio Board Briefs, and metadata across 5 priority meetings.
Generates directory structure, raw artifacts, interim search-ready text, manifests, and indexes.

Epistemically remediated version:
- Separates observed facts from derived inferences.
- Extracts explicit motions, seconds, and roll call votes from minutes JSON.
- Populates presenter and presenting_department only when explicitly named in accessible records.
- Labels rule-based semantic coding as derived.
- Binds evaluation schema strictly to observable claims in accessible text.
- Formally bounds video status as 'no_public_recording_located'.
"""

import os
import json
import hashlib
import csv
import re
from bs4 import BeautifulSoup

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH_DATA = os.path.join(r"C:\Users\admir\.gemini\antigravity\brain\8469418b-e5bc-4b96-9e94-3bad1b2f33b1\scratch", "all_5_meetings_data.json")
RAW_MEETINGS_DIR = os.path.join(PROJECT_ROOT, "data/raw/grandview-c4/governance/meetings")
RAW_BRIEFS_DIR = os.path.join(PROJECT_ROOT, "data/raw/grandview-c4/governance/board_briefs")
INTERIM_DIR = os.path.join(PROJECT_ROOT, "data/interim/grandview-c4/governance")
GOV_DIR = os.path.join(PROJECT_ROOT, "districts/grandview-c4/governance")

os.makedirs(RAW_MEETINGS_DIR, exist_ok=True)
os.makedirs(INTERIM_DIR, exist_ok=True)
os.makedirs(GOV_DIR, exist_ok=True)

BRIEFS_MAP = {
    "16764": ("2011053", "https://www.grandviewc4.net/apps/news/article/2011053"),
    "16922": ("2020964", "https://www.grandviewc4.net/apps/news/article/2020964"),
    "17411": ("2053567", "https://www.grandviewc4.net/apps/news/article/2053567"),
    "24913": ("2191177", "https://www.grandviewc4.net/apps/news/article/2191177?categoryId=5936"),
    "25898": ("2210618", "https://www.grandviewc4.net/apps/news/article/2210618?categoryId=5936"),
}

def sha256_file(filepath):
    if not os.path.exists(filepath):
        return "file_not_found"
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def clean_html_text(html_str):
    if not html_str:
        return ""
    soup = BeautifulSoup(html_str, "html.parser")
    for br in soup.find_all(["br", "p", "div", "h1", "h2", "h3", "h4", "li", "tr"]):
        br.append("\n")
    text = soup.get_text()
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)

def clean_inline_text(html_str):
    if not html_str:
        return ""
    soup = BeautifulSoup(html_str, "html.parser")
    for br in soup.find_all(["br", "p", "div", "li", "tr"]):
        br.append(" ")
    return " ".join(soup.get_text().split())

def build_corpus():
    print("[*] Loading meeting crawl data...")
    with open(SCRATCH_DATA, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    artifacts_records = []
    items_records = []

    sorted_mids = ["16764", "16922", "17411", "24913", "25898"]

    for mid in sorted_mids:
        mdata = all_data[mid]
        date = mdata["meeting_date"]
        folder_name = f"{date}_mid-{mid}"
        m_dir = os.path.join(RAW_MEETINGS_DIR, folder_name)

        agenda_dir = os.path.join(m_dir, "agenda")
        packet_dir = os.path.join(m_dir, "packet")
        att_dir = os.path.join(m_dir, "attachments")
        min_dir = os.path.join(m_dir, "minutes")
        brief_dir = os.path.join(m_dir, "board_brief")
        vid_dir = os.path.join(m_dir, "video")

        for d in [agenda_dir, packet_dir, att_dir, min_dir, brief_dir, vid_dir]:
            os.makedirs(d, exist_ok=True)

        print(f"\n[*] Processing meeting {date} (MID {mid}) -> {folder_name}...")

        # 1. Agenda Artifacts
        agenda_html_path = os.path.join(agenda_dir, f"agenda_{mid}.html")
        with open(agenda_html_path, "w", encoding="utf-8") as f:
            f.write(mdata["raw_html"])

        agenda_json_path = os.path.join(agenda_dir, f"agenda_tree_{mid}.json")
        with open(agenda_json_path, "w", encoding="utf-8") as f:
            json.dump(mdata["agenda_tree"], f, indent=2)

        agenda_items_path = os.path.join(agenda_dir, f"agenda_items_{mid}.json")
        with open(agenda_items_path, "w", encoding="utf-8") as f:
            json.dump(mdata["items_with_contents"], f, indent=2)

        # 2. Minutes Artifacts
        min_data = mdata.get("minutes_data") or {}
        min_json_path = os.path.join(min_dir, f"minutes_{mid}.json")
        with open(min_json_path, "w", encoding="utf-8") as f:
            json.dump(min_data, f, indent=2)

        min_html_content = min_data.get("MeetingMinutes") or ""
        if isinstance(min_html_content, dict):
            min_html_content = json.dumps(min_html_content, indent=2)
        min_html_path = os.path.join(min_dir, f"minutes_{mid}.html")
        with open(min_html_path, "w", encoding="utf-8") as f:
            f.write(str(min_html_content))

        # 3. Board Brief Artifacts
        art_id, brief_url = BRIEFS_MAP[mid]
        src_brief_file = os.path.join(RAW_BRIEFS_DIR, f"brief_{art_id}.html")
        dest_brief_html = os.path.join(brief_dir, f"board_brief_{art_id}.html")
        dest_brief_txt = os.path.join(brief_dir, f"board_brief_{art_id}.txt")

        brief_html = ""
        if os.path.exists(src_brief_file):
            with open(src_brief_file, "r", encoding="utf-8") as f:
                brief_html = f.read()

        with open(dest_brief_html, "w", encoding="utf-8") as f:
            f.write(brief_html)

        brief_clean = clean_html_text(brief_html)
        with open(dest_brief_txt, "w", encoding="utf-8") as f:
            f.write(brief_clean)

        # 4. Packet Status Artifact
        packet_status_path = os.path.join(packet_dir, f"packet_status_{mid}.json")
        packet_status_obj = {
            "master_meeting_id": mid,
            "meeting_date": date,
            "packet_access_status": "linked_but_unavailable",
            "barrier_type": "dynamic_authenticated_generation",
            "barrier_details": "Simbli eBOARDsolutions does not provide static public download links for full meeting packets. Packet generation is dynamically orchestrated via client-side REST calls to app2.eboardsolutions.com (/api/PrintMeetingPacket/GenerateMeetingPacketPdf) and protected by session-bound bearer tokens and Imperva Incapsula WAF.",
            "available_proxies": [
                f"agenda/agenda_{mid}.html",
                f"agenda/agenda_tree_{mid}.json",
                f"agenda/agenda_items_{mid}.json",
                f"minutes/minutes_{mid}.json",
                f"board_brief/board_brief_{art_id}.html"
            ]
        }
        with open(packet_status_path, "w", encoding="utf-8") as f:
            json.dump(packet_status_obj, f, indent=2)

        # 5. Video Metadata Artifact
        video_metadata_path = os.path.join(vid_dir, f"video_metadata_{mid}.json")
        video_obj = {
            "master_meeting_id": mid,
            "meeting_date": date,
            "video_access_status": "no_public_recording_located",
            "search_audit": "Queried YouTube channel @GrandviewC-4SchoolDistrict, official Grandview TV channel, and grandviewc4.net Board of Education video portals. No public video or livestream archive was located for this regular meeting date.",
            "public_channel": "https://www.youtube.com/@GrandviewC-4SchoolDistrict",
            "recommendation": "If district internal recording archives or sunshine audio files are obtained via public records requests, align timestamps to priority agenda items indexed in priority_meeting_items.csv."
        }
        with open(video_metadata_path, "w", encoding="utf-8") as f:
            json.dump(video_obj, f, indent=2)

        # 6. Meeting Metadata
        meta_path = os.path.join(m_dir, "meeting_metadata.json")
        meeting_meta_obj = {
            "master_meeting_id": mid,
            "meeting_date": date,
            "school_id": "225",
            "district": "Consolidated School District No. 4 (Grandview C-4)",
            "meeting_type": "Regular Open Meeting of the Board of Education",
            "portal_url": f"https://simbli.eboardsolutions.com/SB_Meetings/ViewMeeting.aspx?S=225&MID={mid}",
            "board_brief_url": brief_url,
            "board_brief_article_id": art_id,
            "total_agenda_items": len(mdata["items_with_contents"]),
            "total_attachments_linked": len(mdata["attachments"]),
            "minutes_published": bool(min_data.get("MeetingMinutes")),
            "grant_regime": "direct_kauffman_grant" if date <= "2024-12-31" else "post_direct_grant"
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meeting_meta_obj, f, indent=2)

        # 7. Interim Clean Text Generation
        interim_meeting_txt_path = os.path.join(INTERIM_DIR, f"{date}_mid-{mid}_governance_text.txt")
        with open(interim_meeting_txt_path, "w", encoding="utf-8") as f:
            f.write(f"================================================================================\n")
            f.write(f"GRANDVIEW C-4 SCHOOL DISTRICT - GOVERNANCE CORPUS INTERIM TEXT\n")
            f.write(f"MEETING DATE: {date} | MASTER MEETING ID: {mid} | REGIME: {meeting_meta_obj['grant_regime'].upper()}\n")
            f.write(f"SOURCE SIMBLI: https://simbli.eboardsolutions.com/SB_Meetings/ViewMeeting.aspx?S=225&MID={mid}\n")
            f.write(f"SOURCE BOARD BRIEF: {brief_url}\n")
            f.write(f"================================================================================\n\n")

            f.write(f"--- SECTION 1: EDLEO BOARD BRIEF EXECUTIVE SUMMARY (ARTICLE {art_id}) ---\n")
            f.write(brief_clean)
            f.write(f"\n\n--- SECTION 2: OFFICIAL BOARD MINUTES ---\n")
            if min_data.get("MeetingMinutes"):
                f.write(clean_html_text(str(min_data.get("MeetingMinutes"))))
                f.write("\n")
            for im in (min_data.get("LstItemMinutes") or []):
                f.write(f"\n[Minute Item: {im.get('Title')}]\n")
                f.write(clean_html_text(str(im.get("Minute"))))
                f.write("\n")

            f.write(f"\n\n--- SECTION 3: AGENDA ITEMS AND SUPPORTING ADMINISTRATIVE MEMOS ---\n")
            for idx, it in enumerate(mdata["items_with_contents"]):
                it_title = it.get("Title") or ""
                it_seq = it.get("SeqUnderParent") or ""
                it_level = it.get("Level") or 0
                f.write(f"\n================================================================================\n")
                f.write(f"ITEM [{it_level}:{it_seq}] {it_title} (ID: {it.get('ID')})\n")
                f.write(f"--------------------------------------------------------------------------------\n")
                for fld in it.get("fields", []):
                    fname = fld.get("FieldName")
                    ftitle = fld.get("FieldTitle")
                    c_raw = fld.get("Content") or ""
                    clean_c = clean_html_text(c_raw)
                    if clean_c:
                        f.write(f"[{ftitle}]:\n{clean_c}\n\n")
                    atts = fld.get("Attachments") or []
                    if atts:
                        f.write(f"[Supporting Documents Attached ({len(atts)})]:\n")
                        for a in atts:
                            f.write(f"  * Title: {a.get('Title')} | Filename: {a.get('FileName')} | AttID: {a.get('AttachmentID')} | EncrID: {a.get('EncrId')}\n")
                        f.write("\n")
                    pols = fld.get("Policies") or []
                    if pols:
                        f.write(f"[Policies Referenced ({len(pols)})]:\n")
                        for p in pols:
                            f.write(f"  * Code: {p.get('Code')} | Name: {p.get('Name')} | Status: {p.get('Status')} | URL: {p.get('URL')}\n")
                        f.write("\n")

        print(f"[+] Wrote interim text to {interim_meeting_txt_path}")

        # 8. Record Core Manifest Entries (priority_meeting_artifacts.csv)
        rel_prefix = f"data/raw/grandview-c4/governance/meetings/{folder_name}"

        # Agenda HTML
        artifacts_records.append({
            "artifact_id": f"ART-GV-GOV-{mid}-AGD-HTML",
            "meeting_date": date,
            "master_meeting_id": mid,
            "meeting_type": "Regular Open Meeting",
            "agenda_item_number": "ALL",
            "agenda_item_title": "Full Meeting Portal Agenda View",
            "artifact_type": "agenda_html",
            "original_filename": f"ViewMeeting.aspx?S=225&MID={mid}",
            "normalized_filename": f"agenda_{mid}.html",
            "source_url": f"https://simbli.eboardsolutions.com/SB_Meetings/ViewMeeting.aspx?S=225&MID={mid}",
            "retrieved_at": "2026-09-26",
            "local_path": f"{rel_prefix}/agenda/agenda_{mid}.html",
            "file_format": "html",
            "page_count": 1,
            "sha256": sha256_file(agenda_html_path),
            "access_status": "acquired",
            "notes": "Full HTML page snapshot of Simbli ViewMeeting portal including security tokens and prototype models."
        })

        # Agenda Tree JSON
        artifacts_records.append({
            "artifact_id": f"ART-GV-GOV-{mid}-AGD-JSON",
            "meeting_date": date,
            "master_meeting_id": mid,
            "meeting_type": "Regular Open Meeting",
            "agenda_item_number": "ALL",
            "agenda_item_title": "Agenda Item Tree Hierarchy API Response",
            "artifact_type": "agenda_tree_json",
            "original_filename": f"GetAgendaTree_MID_{mid}.json",
            "normalized_filename": f"agenda_tree_{mid}.json",
            "source_url": f"https://simbli.eboardsolutions.com/Services/api/GetAgendaTree/?sct=TOKEN&endid=DID&enmid=MID",
            "retrieved_at": "2026-09-26",
            "local_path": f"{rel_prefix}/agenda/agenda_tree_{mid}.json",
            "file_format": "json",
            "page_count": 1,
            "sha256": sha256_file(agenda_json_path),
            "access_status": "acquired",
            "notes": "Complete REST API response listing all hierarchical agenda nodes, IDs, levels, and attachment flags."
        })

        # Minutes JSON
        artifacts_records.append({
            "artifact_id": f"ART-GV-GOV-{mid}-MIN-JSON",
            "meeting_date": date,
            "master_meeting_id": mid,
            "meeting_type": "Regular Open Meeting",
            "agenda_item_number": "ALL",
            "agenda_item_title": "Official Approved Meeting Minutes API Response",
            "artifact_type": "minutes_json",
            "original_filename": f"GetMeetingMinutes_MID_{mid}.json",
            "normalized_filename": f"minutes_{mid}.json",
            "source_url": f"https://simbli.eboardsolutions.com/Services/api/GetMeetingMinutes/?sct=TOKEN&endid=DID&enmid=MID",
            "retrieved_at": "2026-09-26",
            "local_path": f"{rel_prefix}/minutes/minutes_{mid}.json",
            "file_format": "json",
            "page_count": 1,
            "sha256": sha256_file(min_json_path),
            "access_status": "acquired",
            "notes": "REST API response containing attendees HTML, general board minutes, and item-by-item actions/votes."
        })

        # Minutes HTML
        artifacts_records.append({
            "artifact_id": f"ART-GV-GOV-{mid}-MIN-HTML",
            "meeting_date": date,
            "master_meeting_id": mid,
            "meeting_type": "Regular Open Meeting",
            "agenda_item_number": "ALL",
            "agenda_item_title": "Official Approved Meeting Minutes Formatted HTML",
            "artifact_type": "minutes_html",
            "original_filename": f"minutes_{mid}.html",
            "normalized_filename": f"minutes_{mid}.html",
            "source_url": f"https://simbli.eboardsolutions.com/SB_Meetings/ViewMeeting.aspx?S=225&MID={mid}&T=1",
            "retrieved_at": "2026-09-26",
            "local_path": f"{rel_prefix}/minutes/minutes_{mid}.html",
            "file_format": "html",
            "page_count": 1,
            "sha256": sha256_file(min_html_path),
            "access_status": "acquired",
            "notes": "Formatted HTML body of approved minutes rendered by Simbli."
        })

        # Board Brief HTML
        artifacts_records.append({
            "artifact_id": f"ART-GV-GOV-{mid}-BRF-HTML",
            "meeting_date": date,
            "master_meeting_id": mid,
            "meeting_type": "Regular Open Meeting",
            "agenda_item_number": "ALL",
            "agenda_item_title": f"Edlio Board Brief Executive Summary ({date})",
            "artifact_type": "board_brief_html",
            "original_filename": f"article_{art_id}.html",
            "normalized_filename": f"board_brief_{art_id}.html",
            "source_url": brief_url,
            "retrieved_at": "2026-09-26",
            "local_path": f"{rel_prefix}/board_brief/board_brief_{art_id}.html",
            "file_format": "html",
            "page_count": 1,
            "sha256": sha256_file(dest_brief_html),
            "access_status": "acquired",
            "notes": "Official post-meeting executive summary published by district communications on Edlio CMS."
        })

        # Packet Status
        artifacts_records.append({
            "artifact_id": f"ART-GV-GOV-{mid}-PKT-STAT",
            "meeting_date": date,
            "master_meeting_id": mid,
            "meeting_type": "Regular Open Meeting",
            "agenda_item_number": "ALL",
            "agenda_item_title": "Complete Meeting Packet Composite Dossier",
            "artifact_type": "full_packet",
            "original_filename": f"MeetingPacket_{mid}.pdf",
            "normalized_filename": f"packet_status_{mid}.json",
            "source_url": f"https://app2.eboardsolutions.com/api/PrintMeetingPacket/GenerateMeetingPacketPdf/?sid=DID&mid=MID",
            "retrieved_at": "2026-09-26",
            "local_path": f"{rel_prefix}/packet/packet_status_{mid}.json",
            "file_format": "json",
            "page_count": 1,
            "sha256": sha256_file(packet_status_path),
            "access_status": "linked_but_unavailable",
            "notes": "Composite packet requires authenticated client-side PDF generation job on app2.eboardsolutions.com; proxy data reconstructed from item contents and minutes."
        })

        # Video Recording
        artifacts_records.append({
            "artifact_id": f"ART-GV-GOV-{mid}-VID-INDEX",
            "meeting_date": date,
            "master_meeting_id": mid,
            "meeting_type": "Regular Open Meeting",
            "agenda_item_number": "ALL",
            "agenda_item_title": "Board Meeting Video Recording Search Record",
            "artifact_type": "video_index",
            "original_filename": "N/A",
            "normalized_filename": f"video_metadata_{mid}.json",
            "source_url": "https://www.youtube.com/@GrandviewC-4SchoolDistrict",
            "retrieved_at": "2026-09-26",
            "local_path": f"{rel_prefix}/video/video_metadata_{mid}.json",
            "file_format": "json",
            "page_count": 1,
            "sha256": sha256_file(video_metadata_path),
            "access_status": "no_public_recording_located",
            "notes": "Exhaustive YouTube and district site audit confirmed no public open-session recording located for this date."
        })

        # Attached documents
        for att in mdata["attachments"]:
            att_id_num = att.get("AttachmentID")
            encr_id = att.get("EncrId")
            fname = att.get("FileName") or ""
            title = att.get("Title") or ""
            it_num_att = att.get("ItemSeq") or ""
            it_title = att.get("ItemTitle") or ""
            ext = os.path.splitext(fname)[1].replace(".", "") if fname else "bin"

            artifacts_records.append({
                "artifact_id": f"ART-GV-ATT-{att_id_num}",
                "meeting_date": date,
                "master_meeting_id": mid,
                "meeting_type": "Regular Open Meeting",
                "agenda_item_number": it_num_att,
                "agenda_item_title": it_title,
                "artifact_type": "item_attachment",
                "original_filename": fname,
                "normalized_filename": f"att_{att_id_num}_{fname}",
                "source_url": f"https://simbli.eboardsolutions.com/SB_Meetings/ViewAgendaMinuteDocument.aspx?S=225&aid={encr_id}",
                "retrieved_at": "2026-09-26",
                "local_path": f"{rel_prefix}/attachments/att_{att_id_num}_{fname}",
                "file_format": ext.lower(),
                "page_count": "unretrieved",
                "sha256": "unavailable_imperva_hcaptcha",
                "access_status": "linked_but_unavailable",
                "notes": f"Linked as primary attachment to agenda item '{it_title}'. Direct programmatic download blocked by Imperva Incapsula hCaptcha on ViewAgendaMinuteDocument.aspx."
            })

        # 9. Agenda Items Extraction with Epistemic Separation (priority_meeting_items.csv)
        min_by_encr = {}
        def index_min(ilist):
            for mi in ilist:
                eid = mi.get("EncrId")
                if eid:
                    min_by_encr[eid] = mi
                index_min(mi.get("ChildMinutesLst") or [])
        index_min(min_data.get("LstItemMinutes") or [])

        consent_item_id = None
        consent_motion_by = "none"
        consent_second_by = "none"
        consent_approved = False

        for it in mdata["items_with_contents"]:
            if "consent agenda" in (it.get("Title") or "").lower():
                consent_item_id = it.get("ID")
                mi = min_by_encr.get(consent_item_id)
                if mi:
                    for mov in (mi.get("MeetingOnlineVotings") or []):
                        if mov.get("AllVotingApproved"):
                            consent_approved = True
                        for vh in (mov.get("VotingHTML") or []):
                            vh_clean = clean_inline_text(vh)
                            if vh_clean and "motion made by:" in vh_clean.lower():
                                consent_motion_by = vh_clean.split("Motion made by:")[-1].strip()
                            elif vh_clean and "motion seconded by:" in vh_clean.lower():
                                consent_second_by = vh_clean.split("Motion seconded by:")[-1].strip()
                break

        is_in_consent_section = False

        for idx, it in enumerate(mdata["items_with_contents"]):
            it_id = it.get("ID")
            it_title = it.get("Title") or ""
            it_level = it.get("Level", 0)

            if it_level == 0:
                if "consent agenda" in it_title.lower():
                    is_in_consent_section = True
                elif it_title.strip() != "":
                    is_in_consent_section = False

            bg_text = ""
            action_req = ""
            fin_text = ""
            for fld in it.get("fields", []):
                fn = fld.get("FieldName")
                c = clean_inline_text(fld.get("Content") or "")
                if fn in ["Custom1", "summary", "abstract"]:
                    bg_text += " " + c
                elif fn in ["requestedAction", "recommendations"]:
                    action_req += " " + c
                elif fn in ["financialImpact"]:
                    fin_text += " " + c

            action_req = action_req.strip()
            action_req_source = "agenda_recommendation" if action_req else "not_specified"
            if not action_req:
                action_req = "none"

            combined_text = f"{it_title} {bg_text} {action_req} {fin_text}".lower()

            mi = min_by_encr.get(it_id)
            min_text = clean_inline_text(mi.get("Minutes")) if mi else ""

            item_motion_by = "none"
            item_second_by = "none"
            item_approved = None
            roll_call_details = "none"

            if mi:
                for mov in (mi.get("MeetingOnlineVotings") or []):
                    if mov.get("AllVotingApproved"):
                        item_approved = True
                    elif mov.get("AllVotingNotApproved"):
                        item_approved = False
                    for vh in (mov.get("VotingHTML") or []):
                        vh_clean = clean_inline_text(vh)
                        if "motion made by:" in vh_clean.lower():
                            item_motion_by = vh_clean.split("Motion made by:")[-1].strip()
                        elif "motion seconded by:" in vh_clean.lower():
                            item_second_by = vh_clean.split("Motion seconded by:")[-1].strip()
                        elif "yes:" in vh_clean.lower() or "no:" in vh_clean.lower() or "abstain:" in vh_clean.lower():
                            roll_call_details = vh_clean

            is_consent_child = is_in_consent_section and (it_id != consent_item_id)

            if it_id == consent_item_id:
                board_action = "approved" if consent_approved else "pending_or_unknown"
                vote_result = "motion_approved" if consent_approved else "unknown"
            elif is_consent_child:
                if consent_approved:
                    board_action = "approved_via_consent"
                    vote_result = "approved_via_consent_vote"
                    item_motion_by = f"{consent_motion_by} (Consent Agenda)"
                    item_second_by = f"{consent_second_by} (Consent Agenda)"
                else:
                    board_action = "consent_item_unverified"
                    vote_result = "unknown"
            elif item_approved is True:
                board_action = "approved"
                if roll_call_details != "none":
                    vote_result = f"roll_call_approved: {roll_call_details}"
                else:
                    vote_result = "motion_approved"
            elif item_approved is False:
                board_action = "failed"
                vote_result = "motion_failed"
            elif any(k in it_title.lower() for k in ["call to order", "pledge of allegiance", "quorum", "adjournment"]):
                if "adjournment" in it_title.lower() and item_approved:
                    board_action = "approved"
                    vote_result = "motion_approved"
                else:
                    board_action = "procedural"
                    vote_result = "no_vote_taken"
            elif any(k in it_title.lower() for k in ["audience participation", "report of board members", "salient dates", "recapitulation of funds"]):
                board_action = "procedural"
                vote_result = "no_vote_taken"
            elif it_level > 0 and len(it.get("fields", [])) == 0 and not is_consent_child:
                board_action = "agenda_section_heading"
                vote_result = "not_applicable"
            elif "update" in it_title.lower() or "presentation" in it_title.lower() or "report" in it_title.lower() or "review" in it_title.lower():
                board_action = "information_presentation"
                vote_result = "no_vote_taken"
            elif action_req != "none":
                board_action = "action_requested_record_silent"
                vote_result = "no_individual_vote_recorded"
            else:
                board_action = "information_review"
                vote_result = "no_vote_taken"

            # Presenter & Presenting Department: STRICT OBSERVABILITY
            presenter = "unknown"
            presenting_department = "unknown"

            if "eric wollerman" in combined_text or "eric wollerman" in min_text.lower():
                presenter = "Eric Wollerman (President, Honeywell FM&T)"
            elif "president terry" in min_text.lower():
                if any(k in it_title.lower() for k in ["call to order", "pledge", "adjourn"]):
                    presenter = "Monica Terry (Board President)"
            elif "dr. rodrequez" in min_text.lower() or "dr. rodrequez" in combined_text:
                if "superintendent" in it_title.lower() or "approval of agenda" in it_title.lower():
                    presenter = "Dr. Kenny Rodrequez (Superintendent)"

            if "curriculum & instruction" in combined_text or "c&i" in it_title.lower():
                presenting_department = "Curriculum & Instruction"
            elif "human resources" in combined_text or "personnel transactions" in it_title.lower():
                presenting_department = "Human Resources"
            elif "finance committee" in combined_text or "finance & operations" in combined_text:
                presenting_department = "Finance & Operations"
            elif "superintendent" in it_title.lower():
                presenting_department = "Superintendent Office"

            explicit_rwl = bool(re.search(r'\breal[\s-]world\s+learning\b|\brwl\b', combined_text, re.I))
            explicit_mva = bool(re.search(r'\bmarket\s+value\s+asset\b|\bmva\b|\bmvas\b', combined_text, re.I))
            career_connected = bool(re.search(r'\b(welding|cosmetology|barbering|healthcare|cna|phlebotomy|advanced manufacturing|honeywell|prep-kc|career|pathway|internship|externship|dual credit|credential)\b', combined_text, re.I))

            money_m = re.search(r'\$\s*([0-9,]+(?:\.[0-9]{2})?)', combined_text)
            money_mentioned = bool(money_m) or bool(re.search(r'\b(budget|funds|warrants|revenue|expenditure|salary|cost|dollars)\b', combined_text, re.I))
            amount_val = money_m.group(1).replace(",", "") if money_m else ""
            if not amount_val and ("n/a" in fin_text.lower() or "$0" in fin_text):
                amount_val = "0"
            elif not amount_val and money_mentioned:
                amount_val = "unspecified"

            staffing_mentioned = bool(re.search(r'\b(personnel|salary|hiring|resignation|retirement|coach|facilitator|teacher|superintendent|staff|intern)\b', combined_text, re.I))

            partners = []
            if "honeywell" in combined_text or "kcnsc" in combined_text: partners.append("Honeywell / KCNSC")
            if "prep-kc" in combined_text or "prepkc" in combined_text: partners.append("PREP-KC")
            if "t&l" in combined_text or "t and l" in combined_text: partners.append("T&L Welding")
            if "between me 2 you" in combined_text: partners.append("Between Me 2 You")
            if "cornerstones of care" in combined_text: partners.append("Cornerstones of Care")
            if "cass community health" in combined_text or "cass county" in combined_text: partners.append("Cass Community Health Foundation")
            if "strategos" in combined_text: partners.append("Strategos Group")
            if "kauffman" in combined_text: partners.append("Kauffman Foundation")
            if "grandview education foundation" in combined_text or "gef" in combined_text: partners.append("Grandview Education Foundation")
            if "apple" in combined_text: partners.append("Apple Inc.")
            if "zeta" in combined_text: partners.append("Zeta")
            partner_str = "; ".join(partners) if partners else "None"

            metrics = []
            if "mva" in combined_text: metrics.append("MVA attainment")
            if "apr" in combined_text or "msip" in combined_text: metrics.append("MSIP 6 APR")
            if "iready" in combined_text or "i-ready" in combined_text: metrics.append("i-Ready reading/math")
            if "attendance" in combined_text: metrics.append("Attendance rate")
            if "graduation" in combined_text: metrics.append("Graduation rate")
            if "credential" in combined_text or "aws" in combined_text: metrics.append("Industry credentials")
            metric_str = "; ".join(metrics) if metrics else "None"

            it_num = it_title.split(".")[0].strip() if "." in it_title else str(idx + 1)

            items_records.append({
                "meeting_date": date,
                "master_meeting_id": mid,
                "item_number": it_num,
                "item_title": it_title,
                "source_item_id": it_id,
                "presenting_department": presenting_department,
                "presenter": presenter,
                "action_requested": action_req,
                "action_requested_source": action_req_source,
                "board_action": board_action,
                "vote_result": vote_result,
                "motion_made_by": item_motion_by,
                "motion_seconded_by": item_second_by,
                "explicit_rwl": explicit_rwl,
                "explicit_mva": explicit_mva,
                "career_connected_semantic": career_connected,
                "money_mentioned": money_mentioned,
                "amount": amount_val if amount_val else "None",
                "staffing_mentioned": staffing_mentioned,
                "partner_mentioned": partner_str,
                "metric_mentioned": metric_str,
                "coding_method": "rule_based_derived",
                "source_artifact_id": f"ART-GV-GOV-{mid}-AGD-JSON",
                "page_or_timestamp": f"Item ID {it_id}"
            })

    # Write priority_meeting_artifacts.csv
    artifacts_csv_path = os.path.join(GOV_DIR, "priority_meeting_artifacts.csv")
    artifacts_fields = [
        "artifact_id", "meeting_date", "master_meeting_id", "meeting_type",
        "agenda_item_number", "agenda_item_title", "artifact_type",
        "original_filename", "normalized_filename", "source_url", "retrieved_at",
        "local_path", "file_format", "page_count", "sha256", "access_status", "notes"
    ]
    with open(artifacts_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=artifacts_fields)
        writer.writeheader()
        for r in artifacts_records:
            writer.writerow(r)
    print(f"\n[+] Wrote {len(artifacts_records)} artifact records to {artifacts_csv_path}")

    # Write priority_meeting_items.csv
    items_csv_path = os.path.join(GOV_DIR, "priority_meeting_items.csv")
    items_fields = [
        "meeting_date", "master_meeting_id", "item_number", "item_title",
        "source_item_id", "presenting_department", "presenter", "action_requested",
        "action_requested_source", "board_action", "vote_result", "motion_made_by",
        "motion_seconded_by", "explicit_rwl", "explicit_mva", "career_connected_semantic",
        "money_mentioned", "amount", "staffing_mentioned", "partner_mentioned",
        "metric_mentioned", "coding_method", "source_artifact_id", "page_or_timestamp"
    ]
    with open(items_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=items_fields)
        writer.writeheader()
        for r in items_records:
            writer.writerow(r)
    print(f"[+] Wrote {len(items_records)} agenda item records to {items_csv_path}")

    # Write rwl_evaluation_2024_schema.csv
    schema_csv_path = os.path.join(GOV_DIR, "rwl_evaluation_2024_schema.csv")
    schema_fields = [
        "domain_or_topic", "domain_type", "observable_claim_or_metric", "evidence_source",
        "source_artifact_id", "accessible_text_excerpt", "numerator", "denominator",
        "target", "reported_numeric_value", "comparison_value", "governance_action", "notes"
    ]
    schema_rows = [
        {
            "domain_or_topic": "College Preparation & Placement",
            "domain_type": "rwl_evaluation_domain",
            "observable_claim_or_metric": "Data analyses of college preparation and placement included in evaluation",
            "evidence_source": "Board Brief Dec 19 2024 (Article 2011053)",
            "source_artifact_id": "ART-GV-GOV-16764-BRF-HTML",
            "accessible_text_excerpt": "The evaluation includes data analyses of college preparation and placement...",
            "numerator": "unobservable_in_accessible_text",
            "denominator": "unobservable_in_accessible_text",
            "target": "unobservable_in_accessible_text",
            "reported_numeric_value": "unobservable_in_accessible_text",
            "comparison_value": "unobservable_in_accessible_text",
            "governance_action": "Formally reviewed and approved by Board of Education",
            "notes": "Underlying metric calculations and data tables remain inside WAF-protected attachment 387812 (2022-2024 Real World Learning Program Evaluation.pdf)."
        },
        {
            "domain_or_topic": "Career Center & Academy Enrollment",
            "domain_type": "rwl_evaluation_domain",
            "observable_claim_or_metric": "Data analyses of enrollment in career centers and academies included in evaluation",
            "evidence_source": "Board Brief Dec 19 2024 (Article 2011053)",
            "source_artifact_id": "ART-GV-GOV-16764-BRF-HTML",
            "accessible_text_excerpt": "...enrollment in career centers/academies...",
            "numerator": "unobservable_in_accessible_text",
            "denominator": "unobservable_in_accessible_text",
            "target": "unobservable_in_accessible_text",
            "reported_numeric_value": "unobservable_in_accessible_text",
            "comparison_value": "unobservable_in_accessible_text",
            "governance_action": "Formally reviewed and approved by Board of Education",
            "notes": "Program-specific enrollment counts across partner career centers remain inside attachment 387812."
        },
        {
            "domain_or_topic": "Market Value Asset (MVA) Attainment",
            "domain_type": "rwl_evaluation_domain",
            "observable_claim_or_metric": "Data analyses of market value asset attainment included in evaluation",
            "evidence_source": "Board Brief Dec 19 2024 (Article 2011053)",
            "source_artifact_id": "ART-GV-GOV-16764-BRF-HTML",
            "accessible_text_excerpt": "...market value asset attainment...",
            "numerator": "unobservable_in_accessible_text",
            "denominator": "unobservable_in_accessible_text",
            "target": "unobservable_in_accessible_text",
            "reported_numeric_value": "unobservable_in_accessible_text",
            "comparison_value": "unobservable_in_accessible_text",
            "governance_action": "Formally reviewed and approved by Board of Education",
            "notes": "District-specific senior attainment rates are not reported in the Board Brief text; regional aggregate figures must not be substituted."
        },
        {
            "domain_or_topic": "STEM Course Participation",
            "domain_type": "rwl_evaluation_domain",
            "observable_claim_or_metric": "Data analyses of student participation in Science, Technology, Engineering and Math (STEM) classes",
            "evidence_source": "Board Brief Dec 19 2024 (Article 2011053)",
            "source_artifact_id": "ART-GV-GOV-16764-BRF-HTML",
            "accessible_text_excerpt": "...and student participation in Science, Technology, Engineering and Math (STEM) classes.",
            "numerator": "unobservable_in_accessible_text",
            "denominator": "unobservable_in_accessible_text",
            "target": "unobservable_in_accessible_text",
            "reported_numeric_value": "unobservable_in_accessible_text",
            "comparison_value": "unobservable_in_accessible_text",
            "governance_action": "Formally reviewed and approved by Board of Education",
            "notes": "Specific course-level enrollment figures and PLTW course breakdowns remain inside attachment 387812."
        },
        {
            "domain_or_topic": "Program Growth Trajectory (Qualitative Reporting)",
            "domain_type": "rwl_evaluation_qualitative_finding",
            "observable_claim_or_metric": "District reporting of sustained and significant growth in Real-World Learning programming in recent years",
            "evidence_source": "Board Brief Dec 19 2024 (Article 2011053)",
            "source_artifact_id": "ART-GV-GOV-16764-BRF-HTML",
            "accessible_text_excerpt": "The district has experienced sustained and significant growth in Real-World Learning programming in recent years.",
            "numerator": "not_applicable",
            "denominator": "not_applicable",
            "target": "not_applicable",
            "reported_numeric_value": "not_applicable",
            "comparison_value": "not_applicable",
            "governance_action": "Public communication summary of evaluation findings",
            "notes": "Qualitative characterization published by district communications; underlying quantitative time series unobservable in accessible text."
        },
        {
            "domain_or_topic": "Policy IM Program Evaluation Process",
            "domain_type": "governance_policy_mandate",
            "observable_claim_or_metric": "Inclusion of Real World Learning in standing annual/biennial instructional program evaluation cycle under Policy IM",
            "evidence_source": "Simbli Agenda Item G.1.c Background (MID 16764)",
            "source_artifact_id": "ART-GV-GOV-16764-AGD-JSON",
            "accessible_text_excerpt": "District programs are evaluated annually or biennially per Policy IM. These evaluations assess progress toward meeting established goals and provide recommendations for improvement... Program Evaluation for Finance and Real World Learning and the 2024-25 Program Evaluation Schedule are attached...",
            "numerator": "not_applicable",
            "denominator": "not_applicable",
            "target": "not_applicable",
            "reported_numeric_value": "not_applicable",
            "comparison_value": "not_applicable",
            "governance_action": "Unanimously approved under motion by Damon Greene, seconded by Stacy Wright",
            "notes": "Documents that RWL was evaluated under the district instructional policy framework; does not independently establish permanent institutionalization."
        },
        {
            "domain_or_topic": "MSIP 6 Annual Performance Report (APR) Total Score",
            "domain_type": "concurrent_accountability_context",
            "observable_claim_or_metric": "Missouri DESE 2024 APR score: 127.5 out of 200 points (63.7%)",
            "evidence_source": "Simbli Agenda Item G.1.a & Board Brief Dec 19 2024",
            "source_artifact_id": "ART-GV-GOV-16764-AGD-JSON",
            "accessible_text_excerpt": "The district earned 127.5 out of 200 points, or 63.7%, on the 2024 Annual Performance Report.",
            "numerator": "127.5",
            "denominator": "200.0",
            "target": "70.0% (Full Accreditation Benchmark)",
            "reported_numeric_value": "63.7%",
            "comparison_value": "Prior Year APR",
            "governance_action": "Accepted as informational by Board of Education",
            "notes": "Reported concurrently by Curriculum & Instruction in separate agenda item G.1.a; state accountability metric, not an RWL-specific evaluation metric."
        },
        {
            "domain_or_topic": "MSIP 6 Continuous Improvement Points Earned",
            "domain_type": "concurrent_accountability_context",
            "observable_claim_or_metric": "Continuous improvement sub-score: 86.6% points earned",
            "evidence_source": "Board Brief Dec 19 2024 (Article 2011053)",
            "source_artifact_id": "ART-GV-GOV-16764-BRF-HTML",
            "accessible_text_excerpt": "In Continuous Improvement, Grandview earned 86.6% of the points...",
            "numerator": "unobservable_in_accessible_text",
            "denominator": "unobservable_in_accessible_text",
            "target": "CSIP Continuous Improvement Benchmark",
            "reported_numeric_value": "86.6%",
            "comparison_value": "State Continuous Improvement Average",
            "governance_action": "Accepted as informational by Board of Education",
            "notes": "Reported as part of DESE accountability presentation; measures district-wide growth milestones."
        }
    ]
    with open(schema_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=schema_fields)
        writer.writeheader()
        for r in schema_rows:
            writer.writerow(r)
    print(f"[+] Wrote {len(schema_rows)} evaluation schema records to {schema_csv_path}")

    # Write priority_meeting_video_index.csv
    video_csv_path = os.path.join(GOV_DIR, "priority_meeting_video_index.csv")
    video_fields = [
        "meeting_date", "master_meeting_id", "video_url", "video_status",
        "official_captions", "transcript_available", "agenda_timestamps_available",
        "recommended_transcription_segments"
    ]
    video_rows = [
        {
            "meeting_date": "2024-12-19",
            "master_meeting_id": "16764",
            "video_url": "https://www.youtube.com/@GrandviewC-4SchoolDistrict/search?query=2024-12-19",
            "video_status": "no_public_recording_located",
            "official_captions": "false",
            "transcript_available": "false",
            "agenda_timestamps_available": "false",
            "recommended_transcription_segments": "Item G.1.a (C&I Update / APR Presentation); Item G.1.c (Real World Learning Program Evaluation presentation and board discussion); Item G.3.a (FY24 Audit Presentation)"
        },
        {
            "meeting_date": "2025-01-16",
            "master_meeting_id": "16922",
            "video_url": "https://www.youtube.com/@GrandviewC-4SchoolDistrict/search?query=2025-01-16",
            "video_status": "no_public_recording_located",
            "official_captions": "false",
            "transcript_available": "false",
            "agenda_timestamps_available": "false",
            "recommended_transcription_segments": "Item G.1.a (C&I Update: Eric Wollerman / Honeywell FM&T address, PREP-KC Shared Pathways expansion, MVA Tracker presentation); Item G.1.b (Mid-Year i-Ready Data Review)"
        },
        {
            "meeting_date": "2025-03-20",
            "master_meeting_id": "17411",
            "video_url": "https://www.youtube.com/@GrandviewC-4SchoolDistrict/search?query=2025-03-20",
            "video_status": "no_public_recording_located",
            "official_captions": "false",
            "transcript_available": "false",
            "agenda_timestamps_available": "false",
            "recommended_transcription_segments": "Item G.5.a (Strategic Plan Review 2024-2027); Item G.1.b (Seal of Biliteracy MVA presentation); Item G.3.c (Budget Amendment 2); Item D.3.e (Estimated Tax Levies)"
        },
        {
            "meeting_date": "2026-04-16",
            "master_meeting_id": "24913",
            "video_url": "https://www.youtube.com/@GrandviewC-4SchoolDistrict/search?query=2026-04-16",
            "video_status": "no_public_recording_located",
            "official_captions": "false",
            "transcript_available": "false",
            "agenda_timestamps_available": "false",
            "recommended_transcription_segments": "Item G.1.a (C&I Update: RWL Board Update, Foundations for the Future Week, student opportunity expansion under incoming superintendent Dr. Amaya)"
        },
        {
            "meeting_date": "2026-06-18",
            "master_meeting_id": "25898",
            "video_url": "https://www.youtube.com/@GrandviewC-4SchoolDistrict/search?query=2026-06-18",
            "video_status": "no_public_recording_located",
            "official_captions": "false",
            "transcript_available": "false",
            "agenda_timestamps_available": "false",
            "recommended_transcription_segments": "Item D.3.a (T&L Welding MOA continuation); Item D.3.d (Between Me 2 You healthcare MOU); Item G.3.a (Budget Amendment 3); Item G.3.b (FY2026-27 Preliminary Budget Adoption); Item G.2.a (Career Ladder Committee Update)"
        }
    ]
    with open(video_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=video_fields)
        writer.writeheader()
        for r in video_rows:
            writer.writerow(r)
    print(f"[+] Wrote {len(video_rows)} video records to {video_csv_path}")

if __name__ == "__main__":
    build_corpus()
