"""
src/acquire_nces_ccd.py

Acquires official NCES Common Core of Data (CCD) school directory data for Missouri:
- Years: 2022, 2023, 2024
- Fields:
  - ncessch (NCES School ID)
  - state_leaid (Missouri County-District Code)
  - seasch (Missouri Building Code)
  - school_type (1=Regular, 2=Special Ed, 3=Vocational/CTE, 4=Alternative)
  - virtual (0=No, 1=Virtual)
  - direct_certification (Headcount of directly certified students)
  - free_lunch, reduced_price_lunch, free_or_reduced_price_lunch
  - enrollment

Saves to data/raw/context/mo_nces_ccd_directory_{yr}.csv and updates sources/source_registry.csv.
"""

from pathlib import Path
import hashlib
from datetime import date
import requests
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_CONTEXT_DIR = BASE_DIR / "data" / "raw" / "context"
RAW_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_PATH = BASE_DIR / "sources" / "source_registry.csv"


def acquire_ccd_directory():
    print("[*] Acquiring NCES CCD School Directory & Direct Certification data for Missouri...")
    years = [2022, 2023, 2024]
    
    downloaded_entries = []

    for yr in years:
        url = f"https://educationdata.urban.org/api/v1/schools/ccd/directory/{yr}/?fips=29"
        print(f"[*] Fetching CCD directory for {yr} from {url}...")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        print(f"    Received {len(results):,} school records for {yr}.")

        df = pd.DataFrame(results)
        
        # Standardize key columns
        df["district_code"] = df["state_leaid"].astype(str).str.replace("MO-", "", regex=False).str.strip().str.zfill(6)
        df["building_code"] = df["seasch"].astype(str).str.slice(7, 11)
        
        # Output file
        out_name = f"mo_nces_ccd_directory_{yr}.csv"
        out_path = RAW_CONTEXT_DIR / out_name
        df.to_csv(out_path, index=False)

        with open(out_path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()

        downloaded_entries.append({
            "source_id": f"NCES_CCD_DIRECTORY_{yr}",
            "source_name": f"NCES Common Core of Data School Directory Missouri {yr}",
            "agency": "National Center for Education Statistics / Urban Institute Education Data",
            "url": url,
            "school_year": str(yr),
            "download_date": str(date.today()),
            "file_name": out_name,
            "file_format": "csv",
            "level": "building",
            "raw_hash": h,
            "public_or_restricted": "public",
            "notes": f"Official NCES CCD directory containing school_type, virtual flag, direct_certification count, and NCES IDs. Records: {len(df):,}."
        })

    # Update source registry
    df_reg = pd.read_csv(REGISTRY_PATH)
    # Remove existing CCD entries if any
    existing_ids = set(df_reg["source_id"])
    new_rows = [e for e in downloaded_entries if e["source_id"] not in existing_ids]
    if new_rows:
        df_updated = pd.concat([df_reg, pd.DataFrame(new_rows)], ignore_index=True)
        df_updated.to_csv(REGISTRY_PATH, index=False)
        print(f"[SUCCESS] Added {len(new_rows)} NCES CCD entries to {REGISTRY_PATH}")
    else:
        print("[*] NCES CCD entries already present in registry.")


if __name__ == "__main__":
    acquire_ccd_directory()
