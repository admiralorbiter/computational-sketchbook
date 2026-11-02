"""
Harvest and parse curriculum, course pathways, and RWL programming guides for Hickman Mills C-1.
Downloads:
1. 2025-2026 HMC-1 Real-World Learning Programming Guide (PDF)
2. 2025-2026 Ruskin High School Student Handbook (PDF)
Extracts pathway structures, course offerings, credentials, and dual credit partnerships.
Outputs:
- data/raw/hickman-mills/operations/hmc1_rwl_programming_2025_26.pdf
- data/raw/hickman-mills/operations/ruskin_student_handbook_2025_26.pdf
- districts/hickman-mills/operations/course_catalog_and_pathways.csv
- districts/hickman-mills/operations/CURRICULUM_AND_PATHWAYS_PROFILE.md
"""

import os
import re
import csv
import urllib.request
from pathlib import Path
import fitz  # PyMuPDF

BASE_DIR = Path("2026/2026-09-26-rwl-institutionalization")
DISTRICT_ID = "hickman-mills"
RAW_OPS = BASE_DIR / "data" / "raw" / DISTRICT_ID / "operations"
DIST_OPS = BASE_DIR / "districts" / DISTRICT_ID / "operations"

RAW_OPS.mkdir(parents=True, exist_ok=True)
DIST_OPS.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

FILES_TO_DOWNLOAD = [
    (
        "hmc1_rwl_programming_2025_26.pdf",
        "https://resources.finalsite.net/images/v1738697035/hickmanmillsorg/p8ytjfi2dppyvgzuydnb/25-26HMC-1RWLProgramming.pdf"
    ),
    (
        "ruskin_student_handbook_2025_26.pdf",
        "https://resources.finalsite.net/images/v1756151662/hickmanmillsorg/am0roh0lqemaq3fivb7y/STUDENT_HANDBOOKS_2025_26_Ruskin_FINAL.pdf"
    )
]

def download_assets():
    print("[*] Downloading Hickman Mills curriculum and programming assets...")
    downloaded = {}
    for filename, url in FILES_TO_DOWNLOAD:
        dest = RAW_OPS / filename
        if dest.exists() and dest.stat().st_size > 10000:
            print(f"  [Cached] {filename} ({dest.stat().st_size} bytes)")
        else:
            print(f"  Downloading {filename} from {url}...")
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read()
                    with open(dest, "wb") as f:
                        f.write(data)
                    print(f"  Saved {dest.name} ({len(data)} bytes)")
            except Exception as e:
                print(f"  [!] Failed to download {filename}: {e}")
        if dest.exists():
            downloaded[filename] = dest
    return downloaded

def parse_rwl_guide(pdf_path):
    print(f"\n[*] Parsing RWL Programming Guide: {pdf_path.name}...")
    doc = fitz.open(pdf_path)
    print(f"  Total pages: {len(doc)}")
    
    pages_text = []
    for i, page in enumerate(doc):
        text = page.get_text()
        pages_text.append((i + 1, text))

    full_text = "\n\n".join([f"--- PAGE {p} ---\n{t}" for p, t in pages_text])
    out_txt = RAW_OPS / f"{pdf_path.stem}_text.txt"
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"  [+] Extracted full text to {out_txt.name}")

    # Extract distinct programs, courses, academies, certifications
    # Search for patterns: Programs, pathways, partners, requirements
    programs = []
    
    # Analyze text sections
    lines = full_text.split("\n")
    current_section = "General"
    
    for page_num, text in pages_text:
        # Check headings and keywords
        p_lines = [l.strip() for l in text.split("\n") if l.strip()]
        for idx, line in enumerate(p_lines):
            line_l = line.lower()
            if any(k in line_l for k in [
                "pathway", "academy", "program", "institute", "course", "internship",
                "credential", "certification", "dual credit", "market value asset", "mva"
            ]):
                # Capture context
                context = " ".join(p_lines[max(0, idx-1):min(len(p_lines), idx+3)])
                programs.append({
                    "page_number": page_num,
                    "matched_line": line,
                    "context_snippet": context[:250],
                    "source_doc": pdf_path.name
                })

    return programs, full_text

def main():
    assets = download_assets()
    if "hmc1_rwl_programming_2025_26.pdf" in assets:
        programs, full_text = parse_rwl_guide(assets["hmc1_rwl_programming_2025_26.pdf"])
        print(f"  Found {len(programs)} pathway/course mentions.")

if __name__ == "__main__":
    main()
