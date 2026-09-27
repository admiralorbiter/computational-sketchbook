"""
Harvest curriculum, course pathways, and RWL documents for Center 58 from Apptegy Thrillshare.
Folders & Pages:
1. Real World Learning documents: https://www.center.k12.mo.us/documents/academic-services/real-world-learning/330874
2. RWL Slides folder: https://www.center.k12.mo.us/documents/academic-services/real-world-learning/rwl--slides/23169840
3. High School Curriculum 9-12: https://www.center.k12.mo.us/page/curriculum-9-12/
4. CHS Graduation Requirements: https://www.center.k12.mo.us/o/chs/page/graduationrequirements/
5. CHS Student Services Documents: https://www.center.k12.mo.us/o/chs/documents/student-services/723384
"""

import os
import re
import csv
import json
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path("2026/2026-09-26-rwl-institutionalization")
DIST_ID = "center-58"
RAW_OPS = BASE_DIR / "data" / "raw" / DIST_ID / "operations"
DIST_OPS = BASE_DIR / "districts" / DIST_ID / "operations"

RAW_OPS.mkdir(parents=True, exist_ok=True)
DIST_OPS.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def harvest_center_curriculum():
    print("[*] Starting Center 58 Curriculum & Pathway Harvester...")
    downloaded_files = []
    text_data = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)

        # 1. Scrape Curriculum 9-12
        print("  [*] Fetching Curriculum 9-12...")
        try:
            page.goto("https://www.center.k12.mo.us/page/curriculum-9-12/", wait_until="domcontentloaded", timeout=25000)
            time.sleep(3)
            c912_text = page.inner_text("body")
            text_data["curriculum_9_12"] = c912_text
            with open(RAW_OPS / "center_curriculum_9_12.txt", "w", encoding="utf-8") as f:
                f.write(c912_text)
        except Exception as e:
            print("  Failed on curriculum 9-12:", e)

        # 2. Scrape Real World Learning page
        print("  [*] Fetching Real World Learning page...")
        try:
            page.goto("https://www.center.k12.mo.us/page/real-world-learning/", wait_until="domcontentloaded", timeout=25000)
            time.sleep(3)
            rwl_text = page.inner_text("body")
            text_data["real_world_learning"] = rwl_text
            with open(RAW_OPS / "center_real_world_learning.txt", "w", encoding="utf-8") as f:
                f.write(rwl_text)
        except Exception as e:
            print("  Failed on rwl page:", e)

        # 3. Scrape RWL Document Folder
        print("  [*] Fetching RWL Document Folder (330874)...")
        doc_urls = [
            "https://www.center.k12.mo.us/documents/academic-services/real-world-learning/330874",
            "https://www.center.k12.mo.us/documents/academic-services/real-world-learning/rwl--slides/23169840",
            "https://www.center.k12.mo.us/o/chs/documents/student-services/723384"
        ]

        found_links = []
        for durl in doc_urls:
            try:
                page.goto(durl, wait_until="domcontentloaded", timeout=25000)
                time.sleep(4)
                links = page.eval_on_selector_all("a", """
                els => els.map(e => ({
                    text: e.innerText.trim(),
                    href: e.href
                }))
                """)
                for l in links:
                    href = l["href"]
                    text = l["text"]
                    if any(k in href.lower() for k in ["thrillshare.com", ".pdf", ".docx", ".pptx", ".xlsx", "drive.google"]):
                        found_links.append((text, href))
                        print(f"    Found file: {text} -> {href}")
            except Exception as e:
                print(f"  Failed on doc url {durl}:", e)

        browser.close()

    # Download discovered files
    print(f"\n[*] Downloading {len(found_links)} discovered curriculum documents...")
    headers = {"User-Agent": USER_AGENT}
    for title, url in found_links:
        # Generate safe filename
        safe_name = re.sub(r'[^a-zA-Z0-9_\.-]', '_', title)
        if not any(safe_name.lower().endswith(ext) for ext in ['.pdf', '.docx', '.pptx', '.xlsx']):
            if '.pdf' in url.lower():
                safe_name += '.pdf'
            elif '.docx' in url.lower():
                safe_name += '.docx'
            elif '.pptx' in url.lower():
                safe_name += '.pptx'
            else:
                safe_name += '.bin'
        
        dest = RAW_OPS / safe_name
        if dest.exists() and dest.stat().st_size > 500:
            print(f"  [Cached] {safe_name}")
            downloaded_files.append((title, dest))
            continue

        print(f"  Downloading {safe_name} from {url}...")
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                with open(dest, "wb") as f:
                    f.write(data)
                print(f"  Saved {safe_name} ({len(data)} bytes)")
                downloaded_files.append((title, dest))
        except Exception as e:
            print(f"  Failed download: {e}")

    print(f"[+] Downloaded {len(downloaded_files)} files to {RAW_OPS}")

if __name__ == "__main__":
    harvest_center_curriculum()
