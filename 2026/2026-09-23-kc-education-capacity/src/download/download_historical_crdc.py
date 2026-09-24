"""
Download and extract official Civil Rights Data Collection (CRDC) public-use files
across 6 collection waves: 2013-14, 2015-16, 2017-18, 2020-21, 2021-22, and 2023-24.

Target course files extracted:
- Algebra I
- Geometry
- Algebra II
- Advanced Mathematics
- Calculus
- Biology
- Chemistry
- Physics
- School Characteristics / Directory

Maintains exact provenance and updates data/manifest.csv.
"""

import os
import sys
import io
import csv
import zipfile
import hashlib
import struct
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_CRDC_DIR = PROJECT_ROOT / "data" / "raw" / "crdc"
RESEARCH_DIR = PROJECT_ROOT / "research"
MANIFEST_CSV = PROJECT_ROOT / "data" / "manifest.csv"
SOURCE_MATRIX = RESEARCH_DIR / "crdc_source_matrix.csv"

COURSE_KEYWORDS = [
    "algebra", "geometry", "math", "calculus",
    "biology", "chemistry", "physics", "characteristic", "school data"
]

CRDC_ARCHIVES = [
    {
        "school_year": "2013-2014",
        "wave": "2013-14",
        "url": "https://civilrightsdata.ed.gov/assets/ocr/docs/2013-14-crdc-data.zip",
        "zip_name": "2013-14-crdc-data.zip",
        "mode": "selective_extract",
        "target_prefix": "2013-14 CRDC/School/CRDC-collected data file for Schools/",
        "target_files": [
            "01 School Characteristics.xlsx",
            "05-1 Algebra I Courses and Classes.xlsx",
            "05-2 Geometry Courses and Classes.xlsx",
            "05-3 Other Math Courses and Classes.xlsx",
            "05-4 Biology Courses and Classes.xlsx",
            "05-5 Chemistry Courses and Classes.xlsx",
            "05-6 Physics Courses and Classes.xlsx",
        ]
    },
    {
        "school_year": "2015-2016",
        "wave": "2015-16",
        "url": "https://civilrightsdata.ed.gov/assets/ocr/docs/2015-16-crdc-data.zip",
        "zip_name": "2015-16-crdc-data.zip",
        "mode": "full_download",
        "target_files": [
            "Data Files and Layouts/CRDC 2015-16 School Data.csv",
            "Data Files and Layouts/CRDC 2015-16 School Data Record Layout.csv",
        ]
    },
    {
        "school_year": "2017-2018",
        "wave": "2017-18",
        "url": "https://civilrightsdata.ed.gov/assets/ocr/docs/2017-18-crdc-data.zip",
        "zip_name": "2017-18-crdc-data.zip",
        "mode": "full_download",
        "target_files": [
            "Algebra I.csv",
            "Algebra II.csv",
            "Geometry.csv",
            "Advanced Mathematics.csv",
            "Calculus.csv",
            "Biology.csv",
            "Chemistry.csv",
            "Physics.csv",
            "School Characteristics.csv",
        ]
    },
    {
        "school_year": "2020-2021",
        "wave": "2020-21",
        "url": "https://civilrightsdata.ed.gov/assets/ocr/docs/2020-21-crdc-data.zip",
        "zip_name": "2020-21-crdc-data.zip",
        "mode": "full_download",
        "target_files": [
            "Algebra I.csv",
            "Algebra II.csv",
            "Geometry.csv",
            "Advanced Mathematics.csv",
            "Calculus.csv",
            "Biology.csv",
            "Chemistry.csv",
            "Physics.csv",
            "School Characteristics.csv",
        ]
    },
    {
        "school_year": "2021-2022",
        "wave": "2021-22",
        "url": "https://civilrightsdata.ed.gov/assets/ocr/docs/2021-22-crdc-data.zip",
        "zip_name": "2021-22-crdc-data.zip",
        "mode": "selective_extract",
        "target_prefix": "SCH/",
        "target_files": [
            "SCH/Algebra I.csv",
            "SCH/Algebra II.csv",
            "SCH/Geometry.csv",
            "SCH/Advanced Mathematics.csv",
            "SCH/Calculus.csv",
            "SCH/Biology.csv",
            "SCH/Chemistry.csv",
            "SCH/Physics.csv",
            "SCH/School Characteristics.csv",
        ]
    },
    {
        "school_year": "2023-2024",
        "wave": "2023-24",
        "url": "https://civilrightsdata.ed.gov/assets/ocr/docs/2023-24-crdc-data.zip",
        "zip_name": "2023-24-crdc-data.zip",
        "mode": "full_download",
        "target_files": [
            "Algebra I.csv",
            "Algebra II.csv",
            "Geometry.csv",
            "Advanced Mathematics.csv",
            "Calculus.csv",
            "Biology.csv",
            "Chemistry.csv",
            "Physics.csv",
            "School Characteristics.csv",
        ]
    }
]


def extract_selective_range(url, target_files, dest_dir):
    """
    Extract specific files from a remote zip using HTTP range requests
    without downloading the entire multi-hundred megabyte zip.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
    with urllib.request.urlopen(req) as resp:
        total_size = int(resp.headers.get("Content-Length", 0))

    # Read tail to get central directory
    range_start = max(0, total_size - 2 * 1024 * 1024)
    req_tail = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={range_start}-{total_size-1}"})
    with urllib.request.urlopen(req_tail) as resp_tail:
        tail = resp_tail.read()

    eocd_pos = tail.rfind(b"\x50\x4b\x05\x06")
    cd_size, cd_offset = struct.unpack("<II", tail[eocd_pos+12:eocd_pos+20])
    cd_start_in_tail = cd_offset - range_start

    mini_zip = tail[cd_start_in_tail:cd_start_in_tail+cd_size] + tail[eocd_pos:eocd_pos+22]
    mini_zip = mini_zip[:cd_size+16] + struct.pack("<I", 0) + mini_zip[cd_size+20:]

    with zipfile.ZipFile(io.BytesIO(mini_zip)) as zf:
        namelist = zf.namelist()
        for tf in target_files:
            matches = [n for n in namelist if tf.lower() == n.lower() or n.lower().endswith(tf.lower())]
            if not matches:
                print(f"  Warning: {tf} not found in zip")
                continue
            matched_name = matches[0]
            info = zf.getinfo(matched_name)
            out_name = Path(matched_name).name
            out_path = dest_dir / out_name
            if out_path.exists() and out_path.stat().st_size == info.file_size:
                print(f"  [Exists] {out_name} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
                continue

            print(f"  Fetching {out_name} (compressed {info.compress_size / (1024*1024):.2f} MB)...")
            header_offset = info.header_offset
            fetch_len = info.compress_size + 1024  # include local header padding
            req_file = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Range": f"bytes={header_offset}-{header_offset+fetch_len}"})
            with urllib.request.urlopen(req_file) as resp_f:
                chunk = resp_f.read()

            # Parse local header to get exact data start
            # Local header format: 4 signature, 2 version, 2 flags, 2 compression, 2 mod time, 2 mod date, 4 crc, 4 comp size, 4 uncomp size, 2 fname len, 2 extra len
            if chunk[:4] == b"\x50\x4b\x03\x04":
                fname_len, extra_len = struct.unpack("<HH", chunk[26:30])
                data_start = 30 + fname_len + extra_len
                raw_data = chunk[data_start:data_start+info.compress_size]
                if info.compress_type == zipfile.ZIP_DEFLATED:
                    import zlib
                    decompressed = zlib.decompress(raw_data, -15)
                elif info.compress_type == zipfile.ZIP_STORED:
                    decompressed = raw_data
                else:
                    raise ValueError(f"Unsupported compression type: {info.compress_type}")

                with open(out_path, "wb") as out_f:
                    out_f.write(decompressed)
                print(f"  Saved {out_name} ({len(decompressed) / (1024*1024):.2f} MB)")


def download_and_extract_full(url, target_files, dest_dir, zip_dest):
    """
    Download zip file directly, compute sha256, and extract target course files.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    RAW_CRDC_DIR.mkdir(parents=True, exist_ok=True)

    if not zip_dest.exists():
        print(f"  Downloading {url} to {zip_dest.name}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(zip_dest, "wb") as out_f:
            while True:
                buf = resp.read(1024 * 1024)
                if not buf:
                    break
                out_f.write(buf)
        print(f"  Download complete: {zip_dest.stat().st_size / (1024*1024):.2f} MB")
    else:
        print(f"  [Exists] {zip_dest.name} ({zip_dest.stat().st_size / (1024*1024):.2f} MB)")

    # Compute sha256
    h = hashlib.sha256()
    with open(zip_dest, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    sha256_hash = h.hexdigest()

    # Extract target files
    with zipfile.ZipFile(zip_dest) as zf:
        namelist = zf.namelist()
        for tf in target_files:
            matches = [n for n in namelist if tf.lower() == n.lower() or n.lower().endswith(tf.lower())]
            if not matches:
                print(f"  Warning: {tf} not found in {zip_dest.name}")
                continue
            matched_name = matches[0]
            out_name = Path(matched_name).name
            out_path = dest_dir / out_name
            if out_path.exists():
                print(f"  [Extracted exists] {out_name}")
                continue
            with zf.open(matched_name) as src, open(out_path, "wb") as dst:
                dst.write(src.read())
            print(f"  Extracted {out_name} ({out_path.stat().st_size / (1024*1024):.2f} MB)")

    return sha256_hash


def update_manifest(records):
    """
    Append or update manifest.csv with downloaded CRDC entries.
    """
    if MANIFEST_CSV.exists():
        manifest_df = pd.read_csv(MANIFEST_CSV)
    else:
        manifest_df = pd.DataFrame(columns=["source", "source_url", "filename", "school_year", "download_date", "sha256", "description", "notes"])

    existing_filenames = set(manifest_df["filename"].astype(str))
    new_rows = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for rec in records:
        fn = rec["filename"]
        if fn not in existing_filenames:
            new_rows.append({
                "source": "CRDC / OCR",
                "source_url": rec["source_url"],
                "filename": fn,
                "school_year": rec["school_year"],
                "download_date": today,
                "sha256": rec["sha256"],
                "description": rec["description"],
                "notes": rec["notes"]
            })
            existing_filenames.add(fn)

    if new_rows:
        updated_df = pd.concat([manifest_df, pd.DataFrame(new_rows)], ignore_index=True)
        updated_df.to_csv(MANIFEST_CSV, index=False)
        print(f"\nUpdated manifest.csv with {len(new_rows)} new entries.")


def main():
    RAW_CRDC_DIR.mkdir(parents=True, exist_ok=True)
    manifest_entries = []

    print("=" * 70)
    print("CRDC HISTORICAL DATA ACQUISITION PIPELINE")
    print("=" * 70)

    for arch in CRDC_ARCHIVES:
        sy = arch["school_year"]
        wave = arch["wave"]
        url = arch["url"]
        zip_name = arch["zip_name"]
        mode = arch["mode"]
        dest_year_dir = RAW_CRDC_DIR / sy
        dest_zip = RAW_CRDC_DIR / zip_name

        print(f"\nProcessing CRDC Wave {wave} (School Year {sy})...")
        if mode == "full_download":
            sha256 = download_and_extract_full(url, arch["target_files"], dest_year_dir, dest_zip)
            manifest_entries.append({
                "filename": zip_name,
                "source_url": url,
                "school_year": sy,
                "sha256": sha256,
                "description": f"Civil Rights Data Collection (CRDC) Public-Use Data Archive SY {sy} ({wave})",
                "notes": f"Contains courses and classes data: Algebra I, Geometry, Algebra II, Biology, Chemistry, Physics"
            })
        elif mode == "selective_extract":
            print(f"  Using selective range extraction for {zip_name}...")
            extract_selective_range(url, arch["target_files"], dest_year_dir)
            manifest_entries.append({
                "filename": zip_name,
                "source_url": url,
                "school_year": sy,
                "sha256": "remote_selective_extract",
                "description": f"Civil Rights Data Collection (CRDC) Course Extracts SY {sy} ({wave})",
                "notes": f"Selectively extracted course files: Algebra I, Geometry, Algebra II, Biology, Chemistry, Physics"
            })

    update_manifest(manifest_entries)
    print("\nAll CRDC data downloads and extractions completed successfully!")


if __name__ == "__main__":
    main()
