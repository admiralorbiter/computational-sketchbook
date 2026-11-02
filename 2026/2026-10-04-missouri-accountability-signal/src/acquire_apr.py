"""
src/acquire_apr.py

Acquires official DESE/MCDS building-level Annual Performance Report (APR)
Summary and Supporting Excel workbooks for MSIP 6 years: 2022, 2023, 2024, 2025.
Computes SHA-256 hashes and logs provenance to sources/source_registry.csv.
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
RAW_DIR = BASE_DIR / "data" / "raw" / "apr"
RAW_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_PATH = BASE_DIR / "sources" / "source_registry.csv"

# Official MCDS file download endpoints identified from MCDS School Performance portal
APR_FILES = [
    {
        "source_id": "APR_SUMM_2025_BLD",
        "source_name": "Missouri 2025 APR Summary by Buildings",
        "school_year": 2025,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=6a4b1e79-c0e3Summary Building Report.xlsx",
        "file_name": "mo_apr_summary_2025_building.xlsx",
        "level": "building",
    },
    {
        "source_id": "APR_SUPP_2025_BLD",
        "source_name": "Missouri 2025 APR Supporting by Buildings",
        "school_year": 2025,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=d07d9e08-a6f1Supporting Building Report.xlsx",
        "file_name": "mo_apr_supporting_2025_building.xlsx",
        "level": "building",
    },
    {
        "source_id": "APR_SUMM_2024_BLD",
        "source_name": "Missouri 2024 APR Summary by Buildings",
        "school_year": 2024,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=fb7fd144-df2fSummary Building Report.xlsx",
        "file_name": "mo_apr_summary_2024_building.xlsx",
        "level": "building",
    },
    {
        "source_id": "APR_SUPP_2024_BLD",
        "source_name": "Missouri 2024 APR Supporting by Buildings",
        "school_year": 2024,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=9c55ae75-b6bbSupporting Building Report.xlsx",
        "file_name": "mo_apr_supporting_2024_building.xlsx",
        "level": "building",
    },
    {
        "source_id": "APR_SUMM_2023_BLD",
        "source_name": "Missouri 2023 APR Summary by Buildings",
        "school_year": 2023,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=d32adf43-9d6bSummary Building Report.xlsx",
        "file_name": "mo_apr_summary_2023_building.xlsx",
        "level": "building",
    },
    {
        "source_id": "APR_SUPP_2023_BLD",
        "source_name": "Missouri 2023 APR Supporting by Buildings",
        "school_year": 2023,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=4f33fdaf-e9f2Supporting Building Report.xlsx",
        "file_name": "mo_apr_supporting_2023_building.xlsx",
        "level": "building",
    },
    {
        "source_id": "APR_SUMM_2022_BLD",
        "source_name": "Missouri 2022 APR Summary by Buildings",
        "school_year": 2022,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=027ef54a-4975Summary Building Report.xlsx",
        "file_name": "mo_apr_summary_2022_building.xlsx",
        "level": "building",
    },
    {
        "source_id": "APR_SUPP_2022_BLD",
        "source_name": "Missouri 2022 APR Supporting by Buildings",
        "school_year": 2022,
        "rel_url": "/MCDS/FileDownloadWebHandler.ashx?filename=99b7236c-0514Supporting Building Report.xlsx",
        "file_name": "mo_apr_supporting_2022_building.xlsx",
        "level": "building",
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
    print("[*] Successfully initialized MCDS public session.")
    return s


def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def update_registry(records):
    cols = [
        "source_id", "source_name", "agency", "url", "school_year",
        "download_date", "file_name", "file_format", "level", "raw_hash",
        "public_or_restricted", "notes"
    ]
    if REGISTRY_PATH.exists():
        df_existing = pd.read_csv(REGISTRY_PATH)
        # remove records being updated
        existing_ids = {r["source_id"] for r in records}
        df_filtered = df_existing[~df_existing["source_id"].isin(existing_ids)]
        df_new = pd.DataFrame(records)
        df_out = pd.concat([df_filtered, df_new], ignore_index=True)
    else:
        df_out = pd.DataFrame(records)
    
    df_out.to_csv(REGISTRY_PATH, index=False)
    print(f"[*] Updated source registry at {REGISTRY_PATH} ({len(df_out)} total records).")


def acquire_apr_data():
    session = establish_mcds_session()
    registry_records = []
    now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for item in APR_FILES:
        out_path = RAW_DIR / item["file_name"]
        full_url = urljoin("https://apps.dese.mo.gov", item["rel_url"])
        print(f"\n[*] Downloading: {item['source_name']}")
        print(f"    URL: {full_url}")
        print(f"    Target: {out_path}")

        res = session.get(full_url, stream=True, timeout=60)
        if res.status_code != 200:
            raise RuntimeError(f"HTTP error {res.status_code} fetching {full_url}")
        
        with open(out_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=65536):
                f.write(chunk)

        file_size = out_path.stat().st_size
        sha256 = compute_sha256(out_path)
        print(f"    Saved: {file_size:,} bytes | SHA256: {sha256[:12]}...")

        # Sanity check: Ensure valid excel file > 50KB
        if file_size < 50000:
            raise ValueError(f"Downloaded file {out_path} is unexpectedly small ({file_size} bytes).")

        registry_records.append({
            "source_id": item["source_id"],
            "source_name": item["source_name"],
            "agency": "Missouri DESE / MCDS",
            "url": full_url,
            "school_year": item["school_year"],
            "download_date": now_date,
            "file_name": item["file_name"],
            "file_format": "xlsx",
            "level": item["level"],
            "raw_hash": sha256,
            "public_or_restricted": "public",
            "notes": f"Official MSIP 6 Building-Level APR workbook. File size: {file_size} bytes."
        })

    update_registry(registry_records)
    print("\n[SUCCESS] Phase 1: All 8 building-level APR Summary and Supporting workbooks acquired.")


if __name__ == "__main__":
    acquire_apr_data()
