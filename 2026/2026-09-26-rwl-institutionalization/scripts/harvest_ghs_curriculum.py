"""Harvest curriculum, course selection, and CTE/pathway planning documents for Grandview High School.

Downloads course selection planning guides and tools from GHS counseling portal and Google Drive,
and scans Simbli governance corpus for formal CTE agreements, MOUs, and dual-credit programs.
Outputs to data/raw/grandview-c4/operations/ and districts/grandview-c4/operations/pathway_and_cte_agreements.csv.
"""

import os
import re
import csv
import json
import urllib.request

RAW_OPS_DIR = os.path.abspath('2026/2026-09-26-rwl-institutionalization/data/raw/grandview-c4/operations')
OUT_CSV = os.path.abspath('2026/2026-09-26-rwl-institutionalization/districts/grandview-c4/operations/pathway_and_cte_agreements.csv')
PRIORITY_ITEMS_CSV = os.path.abspath('2026/2026-09-26-rwl-institutionalization/districts/grandview-c4/governance/priority_meeting_items.csv')
SIMBLI_RAW = os.path.abspath('2026/2026-09-26-rwl-institutionalization/data/raw/grandview-c4/governance/simbli/simbli_meetings_raw.json')

DRIVE_FILES = [
    ('Focus Directions for Course Selection', '1vaqnAb_j35QkR0T5-EaWoZgdQ1BAeO0p', 'ghs_course_selection_focus_directions.pdf'),
    ('Credit Check Planner', '1SxNaqBApKP83IePqWHf7TPBzTUT_CMhg', 'ghs_credit_check_planner.png'),
    ('Transcript Review Tutorial', '138d06xRpwKpNw5yZplg3riT_4qyMJbL3', 'ghs_transcript_review_tutorial.pdf'),
    ('NAIA NCAA Course Eligibility', '1A5Ba25ti930ZAFUKTTThvUXDu2DX4v61', 'ghs_ncaa_course_eligibility.pdf'),
]

def download_counseling_assets():
    os.makedirs(RAW_OPS_DIR, exist_ok=True)
    saved = []
    for title, file_id, filename in DRIVE_FILES:
        out_path = os.path.join(RAW_OPS_DIR, filename)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            print(f'[Cached] {filename} ({os.path.getsize(out_path)} bytes)')
            saved.append((title, out_path))
            continue

        dl_url = f'https://drive.google.com/uc?export=download&id={file_id}'
        print(f'Downloading {title} from {dl_url}...')
        req = urllib.request.Request(dl_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                with open(out_path, 'wb') as f:
                    f.write(content)
                print(f'Saved {out_path} ({len(content)} bytes)')
                saved.append((title, out_path))
        except Exception as e:
            print(f'Failed to download {title}: {e}')
    return saved

def scan_governance_agreements():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    agreements = []

    # 1. First scan priority meeting items
    if os.path.exists(PRIORITY_ITEMS_CSV):
        with open(PRIORITY_ITEMS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('item_title', '')
                desc = row.get('item_text_snippet', '')
                combined = f'{title} {desc}'.lower()

                # Look for CTE, pathway, MOU, partnership, college/career keywords
                if any(k in combined for k in [
                    'mou', 'moa', 'agreement', 'pathway', 'career', 'technical education',
                    'welding', 'healthcare', 'herndon', 'caps', 'prep-kc', 'honeywell',
                    'metropolitan community college', 'mcc', 'kauffman', 'real world learning',
                    'stem', 'aviation', 'apprenticeship', 'internship', 'hvac'
                ]):
                    agreements.append({
                        'source_type': 'simbli_priority_meeting',
                        'meeting_date': row.get('meeting_date', ''),
                        'meeting_id': row.get('meeting_id', ''),
                        'item_title': title,
                        'agreement_or_pathway_entity': extract_partner_entity(title),
                        'action_type': row.get('action_type', ''),
                        'vote_result': row.get('vote_result', ''),
                        'item_description_snippet': desc[:250].replace('\n', ' '),
                        'grant_regime': 'direct_grant' if row.get('meeting_date', '') < '2025-01-01' else 'post_direct_grant',
                        'coding_method': 'primary_board_record'
                    })

    # 2. Scan broad Simbli meeting titles for historical agreements
    if os.path.exists(SIMBLI_RAW):
        with open(SIMBLI_RAW, 'r', encoding='utf-8') as f:
            meetings = json.load(f)
        for m in meetings:
            title = m.get('MM_MeetingTitle', '')
            date_time = m.get('MM_DateTime', '')
            date = date_time.split('T')[0] if date_time else ''
            # Check if any special meeting or title specifically mentions CTE/Pathways
            if any(k in title.lower() for k in ['career', 'pathway', 'vocational', 'real world learning']):
                agreements.append({
                    'source_type': 'simbli_meeting_listing',
                    'meeting_date': date,
                    'meeting_id': str(m.get('Master_MeetingID', '')),
                    'item_title': title,
                    'agreement_or_pathway_entity': extract_partner_entity(title),
                    'action_type': 'Meeting Held',
                    'vote_result': 'N/A',
                    'item_description_snippet': f"Meeting type: {m.get('ML_TypeTitle', '')}",
                    'grant_regime': 'direct_grant' if date < '2025-01-01' else 'post_direct_grant',
                    'coding_method': 'primary_board_record'
                })

    # Sort by meeting date
    agreements.sort(key=lambda x: x.get('meeting_date', ''))

    if agreements:
        headers = list(agreements[0].keys())
        with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(agreements)
        print(f'Wrote {len(agreements)} pathway/CTE agreement records to {OUT_CSV}')

def extract_partner_entity(title):
    t_lower = title.lower()
    if 'honeywell' in t_lower:
        return 'Honeywell FM&T'
    if 't&l' in t_lower or 'welding' in t_lower:
        return 'T&L Welding Academy'
    if 'between me 2 you' in t_lower:
        return 'Between Me 2 You (Healthcare)'
    if 'herndon' in t_lower:
        return 'Herndon Career Center'
    if 'caps' in t_lower:
        return 'Southland CAPS / STA'
    if 'prep-kc' in t_lower or 'prepkc' in t_lower:
        return 'PREP-KC'
    if 'metropolitan community college' in t_lower or 'mcc' in t_lower:
        return 'Metropolitan Community College (MCC)'
    if 'kauffman' in t_lower or 'real world learning' in t_lower:
        return 'Ewing Marion Kauffman Foundation'
    return 'District Program / Unspecified'

if __name__ == '__main__':
    download_counseling_assets()
    scan_governance_agreements()
