"""
Simbli eBOARDsolutions Client for Grandview C-4 School District (S=225).
Extracts meeting listings, agenda metadata, and packet attachments from the Simbli e-governance API.
"""

import os
import re
import json
import time
import subprocess
import urllib.request

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHOOL_ID = "225"
BASE_URL = "https://simbli.eboardsolutions.com"
LISTING_PAGE_URL = f"{BASE_URL}/SB_Meetings/SB_MeetingListing.aspx?S={SCHOOL_ID}"
API_URL = f"{BASE_URL}/Services/api/GetMeetingListing"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "districts/grandview-c4/governance")
RAW_OUT_DIR = os.path.join(PROJECT_ROOT, "data/raw/grandview-c4/governance/simbli")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def fetch_page_html(url):
    cmd = ["curl.exe", "-s", "-L", "-A", USER_AGENT, url]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.stdout

def get_simbli_tokens():
    """Extract meetingCustGrd prototype and encrypted ConnectionString from listing HTML."""
    html = fetch_page_html(LISTING_PAGE_URL)
    m_grd = re.search(r'var meetingCustGrd = JSON\.parse\(\'([^\']+)\'\);', html)
    m_constr = re.search(r'var constr = \'([^\']+)\';', html)
    
    if not m_grd or not m_constr:
        # Fallback search for double quotes
        m_grd = re.search(r'var meetingCustGrd = JSON\.parse\("([^"]+)"\);', html)
        m_constr = re.search(r'var constr = "([^"]+)";', html)
        
    if m_grd and m_constr:
        payload = json.loads(m_grd.group(1).replace("\\'", "'"))
        constr = m_constr.group(1)
        payload["ConnectionString"] = constr
        payload["SchoolID"] = SCHOOL_ID
        return payload
    return None

def query_meeting_listing(payload, record_start=1, record_count=50, listing_type=0):
    """
    Query GetMeetingListing endpoint.
    listing_type: 0 = All Meetings, 1 = Upcoming, 2 = Prior
    """
    payload["RecordStart"] = record_start
    payload["RecordCount"] = record_count
    payload["ListingType"] = listing_type
    payload["SortColName"] = "MeetingDate"
    payload["IsSortDesc"] = True
    
    data_bytes = json.dumps(payload).encode("utf-8")
    
    # Use curl to post JSON payload with proper headers
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
        return json.loads(res.stdout)
    except Exception as e:
        print(f"[!] Error parsing API response: {e}")
        return None

def harvest_meetings():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(RAW_OUT_DIR, exist_ok=True)
    
    print("[*] Retrieving Simbli session tokens...")
    payload = get_simbli_tokens()
    if not payload:
        print("[!] Could not parse Simbli connection tokens from listing page.")
        return []
        
    print("[*] Successfully extracted Simbli connection string and security token.")
    print("[*] Querying prior meetings...")
    
    meetings = query_meeting_listing(payload, record_start=1, record_count=100, listing_type=2)
    if meetings:
        out_path = os.path.join(RAW_OUT_DIR, "simbli_meetings_raw.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(meetings, f, indent=2)
        print(f"[+] Saved raw meetings listing to {out_path}")
        return meetings
    else:
        print("[!] No meetings returned or request failed.")
        return []

if __name__ == "__main__":
    harvest_meetings()
