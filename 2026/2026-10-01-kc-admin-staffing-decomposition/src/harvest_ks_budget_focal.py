"""
Harvest official Kansas KSDE USD Budget Codes Documents (Form USD-E)
for the three Kansas focal archetypes:
- Shawnee Mission USD 512
- Olathe USD 233
- Kansas City USD 500
Harvesting both the contemporaneous budget files and the subsequent year's actuals files:
- 2014-15 Actuals: from 2015-16 Codes (Codes2016.pdf, Col 2: 2014-15 Actual)
- 2018-19 Actuals: from 2019-20 Codes (Codes2020.pdf, Col 2: 2018-19 Actual)
- 2022-23 Actuals: from 2023-24 Codes (Codes2024.pdf, Col 2: 2022-23 Actual)
"""

import ssl
import hashlib
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "kansas_budget"
RAW_DIR.mkdir(parents=True, exist_ok=True)

DISTRICTS = [
    {"usd": "512", "slug": "shawnee_mission", "name": "Shawnee Mission USD 512"},
    {"usd": "233", "slug": "olathe", "name": "Olathe USD 233"},
    {"usd": "500", "slug": "kansas_city", "name": "Kansas City USD 500"},
]

FILES_TO_HARVEST = [
    # (Contemporaneous school year, codes year, url folder, target filename, role)
    ("2014-2015", "2016", "15-16_Summary", "Codes2016_Actuals2015.pdf", "audited_actuals_source"),
    ("2018-2019", "2020", "19-20_Summary", "Codes2020_Actuals2019.pdf", "audited_actuals_source"),
    ("2022-2023", "2024", "23-24_Summary", "Codes2024_Actuals2023.pdf", "audited_actuals_source"),
]

def harvest_ks_actuals():
    ctx = ssl._create_unverified_context()
    manifest_records = []

    for d in DISTRICTS:
        usd = d["usd"]
        slug = d["slug"]
        dname = d["name"]
        dist_dir = RAW_DIR / slug
        dist_dir.mkdir(parents=True, exist_ok=True)

        for sy, codes_yr, ypath, out_fname, role in FILES_TO_HARVEST:
            remote_fname = f"{usd}Codes{codes_yr}.pdf"
            fpath = dist_dir / f"{usd}_{out_fname}"
            url = f"https://www.ksde.org/Portals/0/School%20Finance/budget/Budget_at_a_Glance/{ypath}/{remote_fname}"

            if fpath.exists() and fpath.stat().st_size > 500000:
                print(f"[{dname} - {sy}] Cached: {fpath.name} ({fpath.stat().st_size} bytes)")
                data = fpath.read_bytes()
            else:
                print(f"[{dname} - {sy}] Downloading {remote_fname} from {url}...")
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
                    data = resp.read()
                fpath.write_bytes(data)
                print(f"[{dname} - {sy}] Saved {fpath.name} ({len(data)} bytes)")

            sha = hashlib.sha256(data).hexdigest()
            manifest_records.append({
                "district_name": dname,
                "usd": usd,
                "target_school_year": sy,
                "source_codes_year": codes_yr,
                "file_name": f"{usd}_{out_fname}",
                "file_size_bytes": len(data),
                "sha256": sha,
                "source_url": url,
            })

    print(f"\n[SUCCESS] Successfully harvested {len(manifest_records)} Kansas budget actuals files.")
    for rec in manifest_records:
        print(f"  {rec['district_name']} | {rec['target_school_year']} | {rec['file_name']} | {rec['file_size_bytes']} bytes")

if __name__ == "__main__":
    harvest_ks_actuals()
