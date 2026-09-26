"""
Wayback Machine Archaeology Script for Grandview C-4 School District.
Queries Internet Archive CDX API for snapshots of grandviewc4.net from 2018 through 2026.
Catalogs archived pages across staff directories, board policies, news, and strategic planning.
"""

import os
import json
import subprocess
import urllib.parse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data/raw/grandview-c4/communications")
SUMMARY_OUT = os.path.join(PROJECT_ROOT, "districts/grandview-c4/communications/wayback_cdx_summary.json")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

KEY_PATTERNS = [
    "/apps/staff/",
    "/apps/news/",
    "/apps/pages/",
    "strategic",
    "budget",
    "board",
    "career",
    "pathways"
]

def query_cdx(url_pattern, from_year=2018, to_year=2026, limit=1000):
    """Query Internet Archive CDX server."""
    cdx_url = (
        f"http://web.archive.org/cdx/search/cdx"
        f"?url={urllib.parse.quote(url_pattern)}"
        f"&output=json&from={from_year}&to={to_year}&limit={limit}"
    )
    cmd = ["curl.exe", "-s", "-L", "-A", USER_AGENT, cdx_url]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        data = json.loads(res.stdout)
        if len(data) > 1:
            headers = data[0]
            rows = [dict(zip(headers, row)) for row in data[1:]]
            return rows
        return []
    except Exception as e:
        print(f"[!] CDX parse error for {url_pattern}: {e}")
        return []

def run_archaeology():
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(SUMMARY_OUT), exist_ok=True)
    
    print("[*] Starting Wayback Machine archaeology for grandviewc4.net...")
    
    # 1. Broad site captures
    print("[*] Querying homepage and root captures (2018-2026)...")
    root_captures = query_cdx("grandviewc4.net/", from_year=2018, to_year=2026, limit=500)
    print(f"[+] Found {len(root_captures)} root homepage snapshots.")
    
    # 2. Staff directory captures
    print("[*] Querying staff directory captures...")
    staff_captures = query_cdx("grandviewc4.net/apps/staff/*", from_year=2018, to_year=2026, limit=500)
    print(f"[+] Found {len(staff_captures)} staff directory snapshots.")
    
    # 3. News / Board Briefs captures
    print("[*] Querying news and board briefs captures...")
    news_captures = query_cdx("grandviewc4.net/apps/news/*", from_year=2018, to_year=2026, limit=500)
    print(f"[+] Found {len(news_captures)} news archive snapshots.")
    
    # Save raw records
    raw_file = os.path.join(DATA_RAW_DIR, "wayback_cdx_index.json")
    all_records = {
        "root_captures": root_captures,
        "staff_captures": staff_captures,
        "news_captures": news_captures
    }
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2)
    print(f"[+] Saved raw CDX records to {raw_file}")
    
    # Produce summary analysis
    summary = {
        "total_root_snapshots": len(root_captures),
        "total_staff_snapshots": len(staff_captures),
        "total_news_snapshots": len(news_captures),
        "root_by_year": {},
        "staff_by_year": {},
        "earliest_staff_snapshot": staff_captures[0]["timestamp"] if staff_captures else None,
        "latest_staff_snapshot": staff_captures[-1]["timestamp"] if staff_captures else None,
    }
    for c in root_captures:
        yr = c.get("timestamp", "")[:4]
        summary["root_by_year"][yr] = summary["root_by_year"].get(yr, 0) + 1
        
    for c in staff_captures:
        yr = c.get("timestamp", "")[:4]
        summary["staff_by_year"][yr] = summary["staff_by_year"].get(yr, 0) + 1
        
    with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[+] Saved summary to {SUMMARY_OUT}")
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    run_archaeology()
