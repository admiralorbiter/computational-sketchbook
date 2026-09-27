"""
Simbli eBOARDsolutions Client for Hickman Mills C-1 (S=223).
Extracts meeting listings, agenda metadata, and packet attachments from the Simbli e-governance API.
"""

import os
import re
import json
import time
import subprocess
from pathlib import Path

BASE_DIR = Path("2026/2026-09-26-rwl-institutionalization")
SCHOOL_ID = "223"
BASE_URL = "https://simbli.eboardsolutions.com"
LISTING_PAGE_URL = f"{BASE_URL}/SB_Meetings/SB_MeetingListing.aspx?S={SCHOOL_ID}"
API_URL = f"{BASE_URL}/Services/api/GetMeetingListing"
OUTPUT_DIR = BASE_DIR / "districts" / "hickman-mills" / "governance"
RAW_OUT_DIR = BASE_DIR / "data" / "raw" / "hickman-mills" / "governance" / "simbli"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def fetch_page_html(url):
    cmd = ["curl.exe", "-s", "-L", "-A", USER_AGENT, url]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.stdout

def get_simbli_tokens():
    html = fetch_page_html(LISTING_PAGE_URL)
    m_grd = re.search(r'var meetingCustGrd = JSON\.parse\(\'([^\']+)\'\);', html)
    m_constr = re.search(r'var constr = \'([^\']+)\';', html)

    if not m_grd or not m_constr:
        m_grd = re.search(r'var meetingCustGrd = JSON\.parse\("([^"]+)"\);', html)
        m_constr = re.search(r'var constr = "([^"]+)";', html)

    if m_grd and m_constr:
        payload = json.loads(m_grd.group(1).replace("\\'", "'"))
        constr = m_constr.group(1)
        payload["ConnectionString"] = constr
        payload["SchoolID"] = SCHOOL_ID
        return payload
    return None

def query_meeting_listing(payload, record_start=1, record_count=100, listing_type=2):
    payload["RecordStart"] = record_start
    payload["RecordCount"] = record_count
    payload["ListingType"] = listing_type
    payload["SortColName"] = "MeetingDate"
    payload["IsSortDesc"] = True

    cmd = [
        "curl.exe", "-s", "-X", "POST",
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/json",
        "-H", f"Referer: {LISTING_PAGE_URL}",
        "-A", USER_AGENT,
        "-d", json.dumps(payload),
        API_URL
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        data = json.loads(res.stdout)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get("MeetingListing", [])
        return []
    except Exception as e:
        print(f"[!] Error parsing API response: {e}")
        return []

def harvest_hickman_meetings():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[*] Retrieving Simbli session tokens for Hickman Mills (S=223)...")
    payload = get_simbli_tokens()
    if not payload:
        print("[!] Could not parse Simbli connection tokens from listing page.")
        return []

    print("[*] Successfully extracted Simbli connection string and security token.")
    print("[*] Querying prior meetings...")

    first_page = query_meeting_listing(payload, record_start=1, record_count=100, listing_type=2)
    if not first_page:
        print("[!] No meetings returned.")
        return []

    total_records = first_page[0].get("MeetingsCount", 383) if first_page else 383
    all_meetings = list(first_page)
    print(f"[+] Total Hickman Mills meetings reported: {total_records}")
    print(f"[+] Page 1: {len(all_meetings)} meetings")

    start = 101
    while start <= total_records:
        print(f"[*] Fetching records {start} to {start+99}...")
        pdata = query_meeting_listing(payload, record_start=start, record_count=100, listing_type=2)
        if not pdata:
            break
        all_meetings.extend(pdata)
        start += 100
        time.sleep(0.3)

    print(f"[+] Total meetings harvested: {len(all_meetings)}")
    raw_path = RAW_OUT_DIR / "hickman_simbli_meetings_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_meetings, f, indent=2)
    print(f"[+] Saved raw meetings listing to {raw_path}")

    # Build CSV index
    import csv
    csv_path = OUTPUT_DIR / "simbli_meetings_index.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "meeting_id", "meeting_date", "meeting_type", "meeting_name",
            "published_date", "minutes_status", "encr_meeting_id", "encr_site_id", "encr_timezone"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in all_meetings:
            writer.writerow({
                "meeting_id": m.get("Master_MeetingID"),
                "meeting_date": m.get("MM_DateTime", "")[:10],
                "meeting_type": m.get("ML_TypeTitle"),
                "meeting_name": m.get("MM_MeetingTitle"),
                "published_date": m.get("MM_PublishedDate"),
                "minutes_status": m.get("MinutesStatus"),
                "encr_meeting_id": m.get("EncrMeetingId"),
                "encr_site_id": m.get("EncrSiteId"),
                "encr_timezone": m.get("EncrTimeZone")
            })
    print(f"[+] Saved CSV index to {csv_path}")
    return all_meetings

if __name__ == "__main__":
    harvest_hickman_meetings()
