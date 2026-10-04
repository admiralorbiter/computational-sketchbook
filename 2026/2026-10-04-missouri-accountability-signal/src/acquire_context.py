"""
src/acquire_context.py

Acquires official DESE/MCDS building-level student and school context files:
1. Free and Reduced Price Lunch Percentage by Building (longitudinal 2009-10 to 2025-26 with CEP flag)
2. Building Demographic Data (race/ethnicity, LEP/ELL, etc.)
3. Building Enrollment (longitudinal 1991 to 2025)
4. Building Proportional Attendance Rate
5. Building Mobility Rates
6. Part B Special Education School Assessment Participation (IEP)
7. Missouri Growth Model Technical Documentation (2024 & 2025 Procedures and Results, Primer)
8. Executive Order 26-01 (A-F Accountability Foundation)

Computes SHA-256 hashes and updates sources/source_registry.csv.
"""

import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CONTEXT_DIR = BASE_DIR / "data" / "raw" / "context"
RAW_DOCS_DIR = BASE_DIR / "data" / "raw" / "growth_model_docs"
RAW_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_PATH = BASE_DIR / "sources" / "source_registry.csv"

MCDS_CONTEXT_FILES = [
    {
        "source_id": "SES_FRPL_LONGITUDINAL",
        "source_name": "Free and Reduced Price Lunch Percentage by Building 2009-10 to 2025-26",
        "school_year": "2010-2026",
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=fb61ee1c-5613Free and Reduced Priced Lunch Percentage by Building 2009-10 to 2025-26 (1).xlsx",
        "file_name": "mo_frpl_building_2009_2026.xlsx",
        "format": "xlsx",
        "target_dir": RAW_CONTEXT_DIR,
        "notes": "Official DESE longitudinal building FRPL counts, membership, percentages, and CEP participating building flags.",
    },
    {
        "source_id": "STUDENT_DEMOGRAPHICS_LONGITUDINAL",
        "source_name": "Building Demographic Data 2006 to Current",
        "school_year": "2006-2025",
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=e3b40c5a-cc9bBuilding Demographic Data 2006 to Current.xlsx",
        "file_name": "mo_building_demographics_2006_2025.xlsx",
        "format": "xlsx",
        "target_dir": RAW_CONTEXT_DIR,
        "notes": "Official DESE building student racial/ethnic composition and subgroup counts/percentages.",
    },
    {
        "source_id": "SCHOOL_ENROLLMENT_LONGITUDINAL",
        "source_name": "Building Enrollment 1991-2025",
        "school_year": "1991-2025",
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=419d81bf-4a37Building Enrollment.xlsx",
        "file_name": "mo_building_enrollment_1991_2025.xlsx",
        "format": "xlsx",
        "target_dir": RAW_CONTEXT_DIR,
        "notes": "Official DESE longitudinal building enrollment by grade and total.",
    },
    {
        "source_id": "ATTENDANCE_PROPORTIONAL_BUILDING",
        "source_name": "Building Proportional Attendance Rates",
        "school_year": "2018-2025",
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=8c3d8d67-a5b4Building Proportional Attendance Rates.xlsx",
        "file_name": "mo_building_attendance_rates.xlsx",
        "format": "xlsx",
        "target_dir": RAW_CONTEXT_DIR,
        "notes": "Official DESE building proportional attendance rates (students attending >= 90% of time).",
    },
    {
        "source_id": "STUDENT_MOBILITY_BUILDING",
        "source_name": "Building Mobility Rates",
        "school_year": "2018-2025",
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=cb1c1f0a-7cedBuilding Mobility Rates.xlsx",
        "file_name": "mo_building_mobility_rates.xlsx",
        "format": "xlsx",
        "target_dir": RAW_CONTEXT_DIR,
        "notes": "Official DESE building student mobility rates (inbound/outbound/net).",
    },
    {
        "source_id": "SPED_PART_B_SCHOOL_2025",
        "source_name": "Part B Special Education Assessment Participation School 2024-25",
        "school_year": 2025,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=54dfc2b8-97e8PartB_AssessParticipation_school_2024-25.xlsx",
        "file_name": "mo_part_b_special_ed_school_2025.xlsx",
        "format": "xlsx",
        "target_dir": RAW_CONTEXT_DIR,
        "notes": "Official DESE building-level Part B special education assessment participation rates and IEP demographics.",
    },
    {
        "source_id": "SPED_PART_B_SCHOOL_2024",
        "source_name": "Part B Special Education Assessment Participation School 2023-24",
        "school_year": 2024,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=ceafbd35-2db6PartB_AssessParticipation_school_2023-24.xlsx",
        "file_name": "mo_part_b_special_ed_school_2024.xlsx",
        "format": "xlsx",
        "target_dir": RAW_CONTEXT_DIR,
        "notes": "Official DESE building-level Part B special education assessment participation rates 2023-24.",
    },
    {
        "source_id": "SPED_PART_B_SCHOOL_2023",
        "source_name": "Part B Special Education Assessment Participation School 2022-23",
        "school_year": 2023,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=081f75bb-db25PartB_AssessParticipation_school_2022-23.xlsx",
        "file_name": "mo_part_b_special_ed_school_2023.xlsx",
        "format": "xlsx",
        "target_dir": RAW_CONTEXT_DIR,
        "notes": "Official DESE building-level Part B special education assessment participation rates 2022-23.",
    },
]

EXTERNAL_DOCS = [
    {
        "source_id": "GROWTH_MODEL_DOC_2025",
        "source_name": "2025 Missouri Growth Model Procedures and Results",
        "school_year": 2025,
        "direct_url": "https://dese.mo.gov/sites/g/files/zuston521/files/media/pdf/2026/04/2025%20Growth%20Model%20Procedures%20and%20Results_AOD.pdf",
        "file_name": "mo_growth_model_procedures_results_2025.pdf",
        "format": "pdf",
        "target_dir": RAW_DOCS_DIR,
        "notes": "Technical documentation on Missouri value-added growth model estimation, parameters, and demographic correlation diagnostics.",
    },
    {
        "source_id": "GROWTH_MODEL_DOC_2024",
        "source_name": "2024 Missouri Growth Model Procedures and Results",
        "school_year": 2024,
        "direct_url": "https://dese.mo.gov/sites/g/files/zuston521/files/media/pdf/2026/04/2024%20Growth%20Model%20Procedures%20and%20Results_AOD.pdf",
        "file_name": "mo_growth_model_procedures_results_2024.pdf",
        "format": "pdf",
        "target_dir": RAW_DOCS_DIR,
        "notes": "Technical documentation on 2024 growth model procedures and direct certification correlation diagnostics.",
    },
    {
        "source_id": "GROWTH_MODEL_PRIMER",
        "source_name": "Missouri Growth Model Primer",
        "school_year": "General",
        "direct_url": "https://dese.mo.gov/sites/g/files/zuston521/files/media/pdf/2026/04/Missouri%20Growth%20Model%20Primer%20-%20101123_AOD.pdf",
        "file_name": "mo_growth_model_primer.pdf",
        "format": "pdf",
        "target_dir": RAW_DOCS_DIR,
        "notes": "DESE technical primer explaining value-added residuals, conditioning variables, and MSIP 6 integration.",
    },
]


def establish_mcds_session():
    """Establishes an authenticated public session on DESE MCDS portal."""
    s = requests.Session()
    s.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    })
    login_url = "https://apps.dese.mo.gov/WebLogin/Login.aspx?ReturnUrl=%2fMCDS%2fhome.aspx"
    r = s.get(login_url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form")
    form_data = {
        inp.get("name"): inp.get("value", "")
        for inp in form.find_all("input")
        if inp.get("name")
    }
    form_data["ctl00$ContentPlaceHolder1$btnPublic"] = "View Public Applications"
    if "ctl00$ContentPlaceHolder1$Login1$LoginButton" in form_data:
        del form_data["ctl00$ContentPlaceHolder1$Login1$LoginButton"]

    post_url = urljoin(login_url, form.get("action"))
    r_post = s.post(post_url, data=form_data, timeout=20)
    if r_post.status_code != 200:
        raise RuntimeError(f"Failed to enter MCDS public portal: status {r_post.status_code}")
    print("[*] Successfully initialized MCDS public session for context harvesting.")
    return s


def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def update_registry(records):
    if REGISTRY_PATH.exists():
        df_existing = pd.read_csv(REGISTRY_PATH)
        existing_ids = {r["source_id"] for r in records}
        df_filtered = df_existing[~df_existing["source_id"].isin(existing_ids)]
        df_new = pd.DataFrame(records)
        df_out = pd.concat([df_filtered, df_new], ignore_index=True)
    else:
        df_out = pd.DataFrame(records)
    
    df_out.to_csv(REGISTRY_PATH, index=False)
    print(f"[*] Updated source registry at {REGISTRY_PATH} ({len(df_out)} total records).")


def acquire_context_data():
    session = establish_mcds_session()
    registry_records = []
    now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 1. Download MCDS context files
    for item in MCDS_CONTEXT_FILES:
        out_path = item["target_dir"] / item["file_name"]
        full_url = urljoin("https://apps.dese.mo.gov", item["rel_url"])
        print(f"\n[*] Downloading context: {item['source_name']}")
        print(f"    URL: {full_url}")
        print(f"    Target: {out_path}")

        res = session.get(full_url, stream=True, timeout=90)
        if res.status_code != 200:
            raise RuntimeError(f"HTTP error {res.status_code} fetching {full_url}")
        
        with open(out_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=65536):
                f.write(chunk)

        file_size = out_path.stat().st_size
        sha256 = compute_sha256(out_path)
        print(f"    Saved: {file_size:,} bytes | SHA256: {sha256[:12]}...")

        registry_records.append({
            "source_id": item["source_id"],
            "source_name": item["source_name"],
            "agency": "Missouri DESE / MCDS",
            "url": full_url,
            "school_year": item["school_year"],
            "download_date": now_date,
            "file_name": item["file_name"],
            "file_format": item["format"],
            "level": "building",
            "raw_hash": sha256,
            "public_or_restricted": "public",
            "notes": item["notes"] + f" File size: {file_size} bytes."
        })

    # 2. Download Growth Model technical documents
    doc_session = requests.Session()
    doc_session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    })
    for doc in EXTERNAL_DOCS:
        out_path = doc["target_dir"] / doc["file_name"]
        print(f"\n[*] Downloading technical doc: {doc['source_name']}")
        print(f"    URL: {doc['direct_url']}")
        print(f"    Target: {out_path}")

        res = doc_session.get(doc["direct_url"], stream=True, timeout=60)
        if res.status_code != 200:
            raise RuntimeError(f"HTTP error {res.status_code} fetching {doc['direct_url']}")

        with open(out_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=65536):
                f.write(chunk)

        file_size = out_path.stat().st_size
        sha256 = compute_sha256(out_path)
        print(f"    Saved: {file_size:,} bytes | SHA256: {sha256[:12]}...")

        registry_records.append({
            "source_id": doc["source_id"],
            "source_name": doc["source_name"],
            "agency": "Missouri DESE / University of Missouri",
            "url": doc["direct_url"],
            "school_year": doc["school_year"],
            "download_date": now_date,
            "file_name": doc["file_name"],
            "file_format": doc["format"],
            "level": "statewide_technical_model",
            "raw_hash": sha256,
            "public_or_restricted": "public",
            "notes": doc["notes"] + f" File size: {file_size} bytes."
        })

    update_registry(registry_records)
    print("\n[SUCCESS] Phase 3: All context datasets and Growth Model documents acquired.")


if __name__ == "__main__":
    acquire_context_data()
