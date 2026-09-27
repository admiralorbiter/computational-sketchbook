"""
Harvest Board of Education document catalogs for Center 58 from Apptegy Thrillshare portal.
Folders:
1. Agendas / Packets (Folder ID: 23169941)
2. Board Minutes (Folder ID: 23169957)
3. Board Meeting Attachments (Folder ID: 23169977)
"""

import os
import csv
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("2026/2026-09-26-rwl-institutionalization")
GOV_DIR = BASE_DIR / "districts" / "center-58" / "governance"
RAW_DIR = BASE_DIR / "data" / "raw" / "center-58" / "governance"
GOV_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR.mkdir(parents=True, exist_ok=True)

FOLDERS = [
    {
        "category": "agendas_packets",
        "url": "https://www.center.k12.mo.us/documents/board-of-education/agendas%2Fpackets/23169941"
    },
    {
        "category": "board_minutes",
        "url": "https://www.center.k12.mo.us/documents/board-of-education/board-minutes/23169957"
    },
    {
        "category": "board_attachments",
        "url": "https://www.center.k12.mo.us/documents/board-of-education/board-meeting-attachments/23169977"
    }
]

def harvest_center_documents():
    all_docs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        for f_info in FOLDERS:
            cat = f_info["category"]
            furl = f_info["url"]
            print(f"\n[*] Navigating to {cat}: {furl}")
            page.goto(furl, wait_until="domcontentloaded", timeout=45000)
            time.sleep(5)

            # Check subfolders and files
            # In Apptegy, links pointing to files-backend.assets.thrillshare.com or subfolders
            elements = page.eval_on_selector_all("a", """
            els => els.map(e => ({
                text: e.innerText.trim(),
                href: e.href,
                is_file: e.href.includes('thrillshare.com') || e.href.endsWith('.pdf') || e.href.endsWith('.docx'),
                is_subfolder: e.href.includes('/documents/') && !e.href.endsWith('/documents')
            }))
            """)

            cat_docs = [e for e in elements if e["is_file"] or e["is_subfolder"]]
            print(f"[+] Found {len(cat_docs)} items in {cat}")

            for item in cat_docs:
                if not item["text"]:
                    continue
                doc_record = {
                    "category": cat,
                    "title": item["text"],
                    "url": item["href"],
                    "is_file": item["is_file"],
                    "is_subfolder": item["is_subfolder"]
                }
                all_docs.append(doc_record)
                print(f"  [{'FILE' if item['is_file'] else 'FOLDER'}] {item['text']} -> {item['href']}")

                # If subfolder, let's explore it if it's a year folder (e.g. 2024-2025, 2023-2024, etc.)
                if item["is_subfolder"] and any(yr in item["text"] for yr in ["2023", "2024", "2025", "2026", "23-24", "24-25", "25-26"]):
                    print(f"    --> Exploring subfolder: {item['text']}")
                    sub_page = browser.new_page(user_agent="Mozilla/5.0")
                    try:
                        sub_page.goto(item["href"], wait_until="domcontentloaded", timeout=30000)
                        time.sleep(4)
                        sub_items = sub_page.eval_on_selector_all("a", """
                        els => els.map(e => ({
                            text: e.innerText.trim(),
                            href: e.href,
                            is_file: e.href.includes('thrillshare.com') || e.href.endsWith('.pdf')
                        }))
                        """)
                        for s in sub_items:
                            if s["is_file"] and s["text"]:
                                sub_rec = {
                                    "category": f"{cat}_{item['text']}",
                                    "title": s["text"],
                                    "url": s["href"],
                                    "is_file": True,
                                    "is_subfolder": False
                                }
                                all_docs.append(sub_rec)
                                print(f"      [SUB-FILE] {s['text']} -> {s['href']}")
                    except Exception as err:
                        print(f"      Error in subfolder: {err}")
                    finally:
                        sub_page.close()

        browser.close()

    # Save to JSON and CSV
    raw_path = RAW_DIR / "center58_board_documents_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, indent=2)
    print(f"\n[+] Saved {len(all_docs)} raw document records to {raw_path}")

    csv_path = GOV_DIR / "center58_board_documents_index.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "title", "url", "is_file", "is_subfolder"])
        writer.writeheader()
        writer.writerows(all_docs)
    print(f"[+] Saved CSV index to {csv_path}")

if __name__ == "__main__":
    harvest_center_documents()
