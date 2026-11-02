"""
Harvest and parse historical and current staff directory rosters for Hickman Mills C-1 School District.
Ingests:
1. Historical Wayback Machine directory snapshots (2024-2025).
2. Complete live 2026 staff directory across all 56 pages (835 personnel records, including 54 RWL Center staff).

Generates districts/hickman-mills/organization/staff_directory_longitudinal.csv.
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
DISTRICT_ID = "hickman-mills"
RAW_DIR = BASE_DIR / "data" / "raw" / DISTRICT_ID / "organization" / "snapshots"
OUT_DIR = BASE_DIR / "districts" / DISTRICT_ID / "organization"

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

YEARLY_WAYBACK_TIMESTAMPS = [
    ("20240913115326", "2024-2025", "https://www.hickmanmills.org/directory"),
    ("20241107224701", "2024-2025", "https://www.hickmanmills.org/directory"),
    ("20250321170616", "2024-2025", "https://www.hickmanmills.org/directory"),
    ("20250717091809", "2025-2026", "https://www.hickmanmills.org/directory"),
]

def fetch_wayback_snapshots():
    print("[*] Fetching historical Wayback snapshots for Hickman Mills...")
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
    print("\n[*] Harvesting live 2026 staff directory for Hickman Mills (56 pages)...")
    live_records = []
    live_html_dir = RAW_DIR / "live_2026_pages"
    live_html_dir.mkdir(parents=True, exist_ok=True)
    total_pages = 56

    for p in range(1, total_pages + 1):
        url = f"https://www.hickmanmills.org/directory?const_page={p}&const_search_group_ids=&const_search_role_ids=1"
        page_file = live_html_dir / f"page_{p:02d}.html"

        html = ""
        if page_file.exists() and page_file.stat().st_size > 2000:
            with open(page_file, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')
                    with open(page_file, "w", encoding="utf-8") as f:
                        f.write(html)
                    time.sleep(0.2)
            except Exception as e:
                print(f"  [!] Error on live page {p}: {e}")
                continue

        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all(class_=lambda c: c and "fsConstituentItem" in c)

        for it in items:
            name_tag = it.find(class_=lambda c: c and any(k in c.lower() for k in ["name", "title"]))
            raw_name = ""
            if name_tag:
                raw_name = name_tag.get_text().strip()
            else:
                t_lines = [l.strip() for l in it.get_text().split("\n") if l.strip()]
                if t_lines:
                    raw_name = t_lines[0]

            titles = []
            t_block = it.find(class_=lambda c: c and "fsTitles" in c)
            if t_block:
                titles = [l.strip() for l in t_block.get_text().split("\n") if l.strip() and l.strip().lower() != "titles:"]
            elif "Titles:" in it.get_text():
                m_t = re.search(r"Titles:\s*([^\n]+)", it.get_text())
                if m_t:
                    titles.append(m_t.group(1).strip())

            locations = []
            loc_block = it.find(class_=lambda c: c and "fsLocations" in c)
            if loc_block:
                locations = [l.strip() for l in loc_block.get_text().split("\n") if l.strip() and l.strip().lower() != "locations:"]
            elif "Locations:" in it.get_text():
                m_l = re.search(r"Locations:\s*([^\n]+)", it.get_text())
                if m_l:
                    locations.append(m_l.group(1).strip())

            email = ""
            email_tag = it.find("a", href=lambda h: h and "mailto:" in h)
            if email_tag:
                email = email_tag.get("href", "").replace("mailto:", "").strip()

            title_str = "; ".join(titles) if titles else ""
            loc_str = "; ".join(locations) if locations else ""

            live_records.append({
                "snapshot_timestamp": "20260927000000",
                "snapshot_date": "2026-09-27",
                "school_year": "2026-2027",
                "staff_name": raw_name,
                "job_title": title_str,
                "department": loc_str,
                "email": email,
                "source_file": str(page_file.relative_to(BASE_DIR)),
                "source_type": "live_finalsite_directory"
            })

    print(f"  [+] Harvested {len(live_records)} live personnel records.")
    return live_records

def parse_snapshot_records(ts, sy, html_file):
    records = []
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all(class_=lambda c: c and "fsConstituentItem" in c)
    date_str = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 else ts

    for it in items:
        name_tag = it.find(class_=lambda c: c and any(k in c.lower() for k in ["name", "title"]))
        raw_name = name_tag.get_text().strip() if name_tag else ""
        if not raw_name:
            t_lines = [l.strip() for l in it.get_text().split("\n") if l.strip()]
            if t_lines:
                raw_name = t_lines[0]

        titles = []
        t_block = it.find(class_=lambda c: c and "fsTitles" in c)
        if t_block:
            titles = [l.strip() for l in t_block.get_text().split("\n") if l.strip() and l.strip().lower() != "titles:"]
        elif "Titles:" in it.get_text():
            m_t = re.search(r"Titles:\s*([^\n]+)", it.get_text())
            if m_t:
                titles.append(m_t.group(1).strip())

        locations = []
        loc_block = it.find(class_=lambda c: c and "fsLocations" in c)
        if loc_block:
            locations = [l.strip() for l in loc_block.get_text().split("\n") if l.strip() and l.strip().lower() != "locations:"]
        elif "Locations:" in it.get_text():
            m_l = re.search(r"Locations:\s*([^\n]+)", it.get_text())
            if m_l:
                locations.append(m_l.group(1).strip())

        email = ""
        email_tag = it.find("a", href=lambda h: h and "mailto:" in h)
        if email_tag:
            email = email_tag.get("href", "").replace("mailto:", "").strip()

        title_str = "; ".join(titles) if titles else ""
        loc_str = "; ".join(locations) if locations else ""

        records.append({
            "snapshot_timestamp": ts,
            "snapshot_date": date_str,
            "school_year": sy,
            "staff_name": raw_name,
            "job_title": title_str,
            "department": loc_str,
            "email": email,
            "source_file": str(html_file.relative_to(BASE_DIR)),
            "source_type": "wayback_snapshot"
        })

    return records

def build_hickman_staff_panel():
    historical_snapshots = fetch_wayback_snapshots()
    all_records = []

    for ts, sy, html_file in historical_snapshots:
        recs = parse_snapshot_records(ts, sy, html_file)
        print(f"  [+] Parsed {len(recs)} records from snapshot {ts} ({sy})")
        all_records.extend(recs)

    live_recs = harvest_live_staff_directory()
    all_records.extend(live_recs)

    career_keywords = [
        "real world learning", "rwl", "career", "cte", "vocational", "intern",
        "skilled trades", "entrepreneurial", "counselor", "project lead the way",
        "pltw", "superintendent", "principal", "secondary programs", "curriculum"
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
    build_hickman_staff_panel()
