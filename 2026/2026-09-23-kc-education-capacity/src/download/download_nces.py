"""
Download official NCES CCD and EDGE Geocode datasets for School Year 2024-2025.
Saves raw zip archives immutably into data/raw/nces/ and records checksums in data/manifest.csv.
"""

import os
import sys
import hashlib
import datetime
import pathlib
import requests
import pandas as pd

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
RAW_NCES_DIR = BASE_DIR / "data" / "raw" / "nces"
MANIFEST_FILE = BASE_DIR / "data" / "manifest.csv"

DOWNLOAD_TARGETS = [
    {
        "source": "NCES CCD",
        "source_url": "https://nces.ed.gov/ccd/Data/zip/ccd_sch_029_2425_w_1a_073025.zip",
        "filename": "ccd_sch_029_2425_w_1a_073025.zip",
        "school_year": "2024-2025",
        "description": "NCES CCD Public Elementary/Secondary School Universe Survey Directory Data SY 2024-2025 (v.1a)",
        "notes": "Contains school names, LEA IDs, address, grade span (GSLO/GSHI), operational status, school type, and charter text"
    },
    {
        "source": "NCES CCD",
        "source_url": "https://nces.ed.gov/ccd/Data/zip/ccd_sch_129_2425_w_1a_073025.zip",
        "filename": "ccd_sch_129_2425_w_1a_073025.zip",
        "school_year": "2024-2025",
        "description": "NCES CCD School Characteristics Data SY 2024-2025 (v.1a)",
        "notes": "Contains virtual school status indicators (VIRTUAL, VIRTUAL_TEXT) and shared time indicators"
    },
    {
        "source": "NCES EDGE",
        "source_url": "https://nces.ed.gov/programs/edge/data/EDGE_GEOCODE_PUBLICSCH_2425.zip",
        "filename": "EDGE_GEOCODE_PUBLICSCH_2425.zip",
        "school_year": "2024-2025",
        "description": "NCES EDGE Public School Geocodes and Locale Assignments SY 2024-2025",
        "notes": "Contains building physical location, coordinates (LAT, LON), county name (NMCNTY), county FIPS (CNTY), and NCES locale code (LOCALE)"
    }
]

def compute_sha256(filepath: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def download_file(url: str, dest_path: pathlib.Path):
    print(f"Downloading {url} -> {dest_path.name}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=512 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        pct = downloaded / total_size * 100
                        print(f"\r  Downloaded {downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB ({pct:.1f}%)", end="", flush=True)
                    else:
                        print(f"\r  Downloaded {downloaded / 1024 / 1024:.1f} MB", end="", flush=True)
    print("\n  Download complete.")

def update_manifest(records):
    if MANIFEST_FILE.exists() and MANIFEST_FILE.stat().st_size > 0:
        manifest_df = pd.read_csv(MANIFEST_FILE)
    else:
        manifest_df = pd.DataFrame(columns=[
            "source", "source_url", "filename", "school_year",
            "download_date", "sha256", "description", "notes"
        ])
    
    for rec in records:
        # Check if already present by filename and school_year
        mask = (manifest_df["filename"] == rec["filename"]) & (manifest_df["school_year"] == rec["school_year"])
        if mask.any():
            manifest_df.loc[mask, list(rec.keys())] = list(rec.values())
        else:
            manifest_df = pd.concat([manifest_df, pd.DataFrame([rec])], ignore_index=True)
            
    manifest_df.to_csv(MANIFEST_FILE, index=False)
    print(f"Updated {MANIFEST_FILE}")

def main():
    RAW_NCES_DIR.mkdir(parents=True, exist_ok=True)
    manifest_records = []
    
    for target in DOWNLOAD_TARGETS:
        dest_path = RAW_NCES_DIR / target["filename"]
        if not dest_path.exists():
            download_file(target["source_url"], dest_path)
        else:
            print(f"File {dest_path.name} already exists. Skipping download.")
            
        sha256 = compute_sha256(dest_path)
        print(f"  SHA-256 ({dest_path.name}): {sha256}")
        
        manifest_records.append({
            "source": target["source"],
            "source_url": target["source_url"],
            "filename": target["filename"],
            "school_year": target["school_year"],
            "download_date": datetime.date.today().isoformat(),
            "sha256": sha256,
            "description": target["description"],
            "notes": target["notes"]
        })
        
    update_manifest(manifest_records)
    print("All NCES raw files downloaded and recorded in manifest.")

if __name__ == "__main__":
    main()
