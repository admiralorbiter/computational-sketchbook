"""Harvest and parse historical and current staff directory rosters for Grandview C-4.

Uses Wayback Machine captures (2018-2024) and Playwright for live 2026 directory to construct
a longitudinal staff directory panel in districts/grandview-c4/organization/staff_directory_longitudinal.csv.
"""

import os
import json
import urllib.request
import re
import csv
import time
from bs4 import BeautifulSoup

RAW_DIR = os.path.abspath('2026/2026-09-26-rwl-institutionalization/data/raw/grandview-c4/organization/snapshots')
CDX_FILE = os.path.abspath('2026/2026-09-26-rwl-institutionalization/data/raw/grandview-c4/communications/wayback_cdx_index.json')
OUT_CSV = os.path.abspath('2026/2026-09-26-rwl-institutionalization/districts/grandview-c4/organization/staff_directory_longitudinal.csv')

def fetch_wayback_snapshots():
    os.makedirs(RAW_DIR, exist_ok=True)
    if not os.path.exists(CDX_FILE):
        print(f'CDX index not found at {CDX_FILE}')
        return []

    with open(CDX_FILE, 'r', encoding='utf-8') as f:
        cdx = json.load(f)

    staff_captures = [c for c in cdx.get('staff_captures', []) if c.get('statuscode') == '200']
    print(f'Found {len(staff_captures)} 200-OK staff directory captures in CDX.')

    # Group by year-month to avoid redundant daily duplicate snapshots
    unique_periods = {}
    for c in staff_captures:
        ts = c['timestamp']
        period = ts[:6] # YYYYMM
        if period not in unique_periods:
            unique_periods[period] = c

    print(f'Targeting {len(unique_periods)} monthly/periodic snapshots across 2018-2024.')

    saved_files = []
    for period, capture in sorted(unique_periods.items()):
        ts = capture['timestamp']
        orig = capture['original']
        out_file = os.path.join(RAW_DIR, f'staff_snapshot_{ts}.html')

        if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
            print(f'[{ts}] Cached: {out_file}')
            saved_files.append((ts, out_file))
            continue

        wb_url = f'http://web.archive.org/web/{ts}id_/{orig}'
        print(f'[{ts}] Downloading from Wayback: {wb_url}...')
        req = urllib.request.Request(wb_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                content = resp.read().decode('utf-8', errors='ignore')
                with open(out_file, 'w', encoding='utf-8') as out:
                    out.write(content)
                print(f'[{ts}] Saved {out_file} ({len(content)} bytes)')
                saved_files.append((ts, out_file))
                time.sleep(1) # respectful pacing
        except Exception as e:
            print(f'[{ts}] Failed to fetch: {e}')

    return saved_files

def fetch_live_staff_directory():
    out_file = os.path.join(RAW_DIR, 'staff_snapshot_2026_live.html')
    if os.path.exists(out_file) and os.path.getsize(out_file) > 5000:
        print(f'[Live 2026] Cached: {out_file}')
        return ('20260927000000', out_file)

    print('[Live 2026] Fetching live staff directory with Playwright...')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        try:
            page.goto('https://www.grandviewc4.net/apps/staff/', timeout=45000)
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            content = page.content()
            with open(out_file, 'w', encoding='utf-8') as out:
                out.write(content)
            print(f'[Live 2026] Saved {out_file} ({len(content)} bytes)')
            browser.close()
            return ('20260927000000', out_file)
        except Exception as e:
            print(f'[Live 2026] Error: {e}')
            browser.close()
            return None

def parse_staff_snapshot(ts, html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    date_str = f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}' if len(ts) >= 8 else ts
    school_year = f'{int(ts[:4])-1}-{ts[:4]}' if int(ts[4:6]) < 7 else f'{ts[:4]}-{int(ts[:4])+1}'

    records = []

    # Edlio staff item container variations
    # 1. Standard edlio staff-directory groups
    staff_items = soup.find_all(class_=re.compile(r'staff-item|user-item|staff-card|user-card'))
    
    if not staff_items:
        # Fallback to user-data spans within directory container
        container = soup.find(class_=re.compile(r'staff-directory'))
        if container:
            # Look for blocks with user-name and user-position
            blocks = container.find_all(['li', 'div', 'tr'], class_=re.compile(r'user|staff|member|item'))
            if blocks:
                staff_items = blocks

    if staff_items:
        for item in staff_items:
            name_el = item.find('a', class_=re.compile(r'\bname\b')) or item.find(class_='user-name') or item.find(class_='staff-name')
            pos_el = item.find('span', class_='user-position') or item.find(class_='job-title') or item.find(class_='staff-title')
            dept_el = item.find(class_='user-department') or item.find(class_='staff-department')
            email_el = item.find('a', href=re.compile(r'mailto:'))

            name = name_el.get_text(strip=True) if name_el else ''
            position = pos_el.get_text(strip=True) if pos_el else ''
            dept = dept_el.get_text(strip=True) if dept_el else ''
            email = email_el.get('href').replace('mailto:', '').strip() if email_el else ''

            if name and position:
                records.append({
                    'snapshot_timestamp': ts,
                    'snapshot_date': date_str,
                    'school_year': school_year,
                    'staff_name': name,
                    'job_title': position,
                    'department': dept,
                    'email': email,
                    'source_file': os.path.relpath(html_path, '2026/2026-09-26-rwl-institutionalization').replace('\\', '/'),
                    'is_rwl_or_career_related': 'true' if any(k in f'{position} {dept}'.lower() for k in ['real world', 'rwl', 'career', 'pathway', 'mva', 'workforce', 'internship', 'curriculum', 'counselor']) else 'false',
                    'coding_method': 'primary_directory_snapshot'
                })
    else:
        # Generic span extraction if structured blocks were not matched
        user_infos = soup.find_all(class_='user-info')
        if user_infos:
            for info in user_infos:
                name_el = info.find('a', class_=re.compile(r'\bname\b')) or info.find(class_='user-name')
                pos_el = info.find('span', class_='user-position')
                email_el = info.find('a', href=re.compile(r'mailto:'))
                name = name_el.get_text(strip=True) if name_el else ''
                position = pos_el.get_text(strip=True) if pos_el else ''
                email = email_el.get('href').replace('mailto:', '').strip() if email_el else ''
                if name and position:
                    records.append({
                        'snapshot_timestamp': ts,
                        'snapshot_date': date_str,
                        'school_year': school_year,
                        'staff_name': name,
                        'job_title': position,
                        'department': '',
                        'email': email,
                        'source_file': os.path.relpath(html_path, '2026/2026-09-26-rwl-institutionalization').replace('\\', '/'),
                        'is_rwl_or_career_related': 'true' if any(k in position.lower() for k in ['real world', 'rwl', 'career', 'pathway', 'mva', 'workforce', 'internship', 'curriculum', 'counselor']) else 'false',
                        'coding_method': 'primary_directory_snapshot'
                    })

    return records

def build_longitudinal_staff_panel():
    snapshots = fetch_wayback_snapshots()
    live = fetch_live_staff_directory()
    if live:
        snapshots.append(live)

    all_records = []
    for ts, path in snapshots:
        recs = parse_staff_snapshot(ts, path)
        print(f'[{ts}] Extracted {len(recs)} staff members.')
        all_records.extend(recs)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    if all_records:
        headers = list(all_records[0].keys())
        with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_records)
        print(f'Wrote {len(all_records)} longitudinal staff records to {OUT_CSV}')
    else:
        print('No staff records extracted.')

if __name__ == '__main__':
    build_longitudinal_staff_panel()
