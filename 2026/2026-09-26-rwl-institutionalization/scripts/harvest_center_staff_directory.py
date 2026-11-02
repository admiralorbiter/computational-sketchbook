"""
Harvest and parse historical and current staff directory rosters for Center School District 58.
Ingests:
1. Historical Wayback Machine snapshots of center.k12.mo.us/staff (2018-2025).
2. Complete live 2026 staff directory across all 23 pages (450 personnel records).

Generates districts/center-58/organization/staff_directory_longitudinal.csv.
"""

import os
import re
import csv
import time
import json
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path("2026/2026-09-26-rwl-institutionalization")
DISTRICT_ID = "center-58"
RAW_DIR = BASE_DIR / "data" / "raw" / DISTRICT_ID / "organization" / "snapshots"
OUT_DIR = BASE_DIR / "districts" / DISTRICT_ID / "organization"

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Representative yearly snapshots from CDX
YEARLY_WAYBACK_TIMESTAMPS = [
    ("20181020200511", "2018-2019", "http://www.center.k12.mo.us/staff"),
    ("20190817163904", "2019-2020", "https://www.center.k12.mo.us/staff"),
    ("20201026042456", "2020-2021", "https://www.center.k12.mo.us/staff"),
    ("20210418084530", "2021-2022", "https://www.center.k12.mo.us/staff"),
    ("20220302170321", "2022-2023", "https://www.center.k12.mo.us/staff"),
    ("20230328124233", "2023-2024", "https://www.center.k12.mo.us/staff"),
    ("20240315104230", "2024-2025", "https://www.center.k12.mo.us/staff"),
]

def fetch_wayback_snapshots():
    print("[*] Fetching historical Wayback snapshots for Center 58...")
    snapshots_data = []

    for ts, sy, orig in YEARLY_WAYBACK_TIMESTAMPS:
        out_file = RAW_DIR / f"staff_snapshot_{ts}.html"
        if out_file.exists() and out_file.stat().st_size > 5000:
            print(f"  [{ts}] Cached: {out_file.name}")
        else:
            wb_url = f"https://web.archive.org/web/{ts}id_/{orig}"
            print(f"  [{ts}] Downloading {wb_url}...")
            req = urllib.request.Request(wb_url, headers={'User-Agent': USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    content = resp.read().decode('utf-8', errors='ignore')
                    with open(out_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"  [{ts}] Saved {out_file.name} ({len(content)} bytes)")
                    time.sleep(1)
            except Exception as e:
                print(f"  [{ts}] Failed to fetch: {e}")

        if out_file.exists():
            snapshots_data.append((ts, sy, out_file))

    return snapshots_data

def harvest_live_staff_directory():
    print("\n[*] Harvesting live 2026 staff directory for Center 58 (23 pages)...")
    live_records = []
    live_html_dir = RAW_DIR / "live_2026_pages"
    live_html_dir.mkdir(parents=True, exist_ok=True)

    for p in range(1, 24):
        url = f"https://www.center.k12.mo.us/staff?page_no={p}"
        page_file = live_html_dir / f"page_{p:02d}.html"
        
        html = ""
        if page_file.exists() and page_file.stat().st_size > 5000:
            with open(page_file, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')
                    with open(page_file, "w", encoding="utf-8") as f:
                        f.write(html)
                    time.sleep(0.3)
            except Exception as e:
                print(f"  [!] Error on live page {p}: {e}")
                continue

        soup = BeautifulSoup(html, "html.parser")
        boxes = soup.find_all(class_="contact-box")
        for b in boxes:
            info = b.find(class_="staff-info")
            btn = b.find(class_="contact-button") or b.find("a")
            email = btn.get_text().strip() if btn else ""
            lines = info.get_text("\n").split("\n") if info else []
            lines = [l.strip() for l in lines if l.strip()]

            name = lines[0] if lines else "Unknown"
            title = lines[1] if len(lines) > 1 else ""
            dept = lines[2] if len(lines) > 2 else ""
            if "@" in dept and not email:
                email = dept
                dept = ""

            live_records.append({
                "snapshot_timestamp": "20260927000000",
                "snapshot_date": "2026-09-27",
                "school_year": "2026-2027",
                "staff_name": name,
                "job_title": title,
                "department": dept,
                "email": email,
                "source_file": str(page_file.relative_to(BASE_DIR)),
                "source_type": "live_apptegy_directory"
            })

    print(f"  [+] Harvested {len(live_records)} live personnel records.")
    return live_records

def parse_snapshot_records(ts, sy, html_file):
    records = []
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    boxes = soup.find_all(class_="contact-box")

    date_str = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 else ts

    for b in boxes:
        info = b.find(class_="staff-info")
        btn = b.find(class_="contact-button") or b.find("a")
        email = btn.get_text().strip() if btn else ""
        lines = info.get_text("\n").split("\n") if info else []
        lines = [l.strip() for l in lines if l.strip()]

        if not lines:
            continue

        name = lines[0]
        title = lines[1] if len(lines) > 1 else ""
        dept = lines[2] if len(lines) > 2 else ""
        if "@" in dept and not email:
            email = dept
            dept = ""

        records.append({
            "snapshot_timestamp": ts,
            "snapshot_date": date_str,
            "school_year": sy,
            "staff_name": name,
            "job_title": title,
            "department": dept,
            "email": email,
            "source_file": str(html_file.relative_to(BASE_DIR)),
            "source_type": "wayback_snapshot"
        })

    return records

def build_center_staff_panel():
    historical_snapshots = fetch_wayback_snapshots()
    all_records = []

    for ts, sy, html_file in historical_snapshots:
        recs = parse_snapshot_records(ts, sy, html_file)
        print(f"  [+] Parsed {len(recs)} records from snapshot {ts} ({sy})")
        all_records.extend(recs)

    live_recs = harvest_live_staff_directory()
    all_records.extend(live_recs)

    # Classify RWL / Career / Leadership roles
    career_keywords = [
        "career", "cte", "vocational", "counselor", "industrial technology",
        "business technology", "summit tech", "herndon", "prep-kc", "gear up",
        "superintendent", "assistant superintendent", "director of operations", "curriculum"
    ]

    for r in all_records:
        t_str = f"{r['job_title']} {r['department']}".lower()
        r["is_rwl_or_career_related"] = any(k in t_str for k in career_keywords)
        r["coding_method"] = "primary_directory_snapshot"

    out_csv = OUT_DIR / "staff_directory_longitudinal.csv"
    fieldnames = [
        "snapshot_timestamp", "snapshot_date", "school_year", "staff_name",
        "job_title", "department", "email", "source_file",
        "is_rwl_or_career_related", "coding_method"
    ]

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_records:
            row = {k: r.get(k, "") for k in fieldnames}
            writer.writerow(row)

    print(f"\n[+] Successfully saved {len(all_records)} longitudinal staff records to {out_csv}")

if __name__ == "__main__":
    build_center_staff_panel()
