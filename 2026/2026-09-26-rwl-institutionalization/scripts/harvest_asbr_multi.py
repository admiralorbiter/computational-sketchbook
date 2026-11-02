"""
Multi-District DESE ASBR Harvester via SSRS ReportViewer.
Harvests official ASBR reports for:
- Center 58 (DESE dropdown: 48080, Code: 048-080)
- Hickman Mills C-1 (DESE dropdown: 48072, Code: 048-072)
Across school years 2018-19 through 2023-24 (both CSV and Excel).
"""

import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

DISTRICTS = [
    {
        "slug": "center-58",
        "code_dese": "048-080",
        "ddl_val": "48080",
        "name": "Center 58"
    },
    {
        "slug": "hickman-mills",
        "code_dese": "048-072",
        "ddl_val": "48072",
        "name": "Hickman Mills C-1"
    }
]

YEARS = [
    ('2024|GENERAL', '2023-2024', '2023_2024'),
    ('2023|GENERAL', '2022-2023', '2022_2023'),
    ('2022|GENERAL', '2021-2022', '2021_2022'),
    ('2021|GENERAL', '2020-2021', '2020_2021'),
    ('2020|GENERAL', '2019-2020', '2019_2020'),
    ('2019|GENERAL', '2018-2019', '2018_2019'),
]

BASE_DIR = Path("2026/2026-09-26-rwl-institutionalization")

def harvest_districts():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for d in DISTRICTS:
            slug = d["slug"]
            ddl_district = d["ddl_val"]
            dname = d["name"]
            raw_dir = BASE_DIR / "data" / "raw" / slug / "finance" / "asbr"
            raw_dir.mkdir(parents=True, exist_ok=True)
            print(f"\n========================================================")
            print(f"[*] Harvesting {dname} (DDL: {ddl_district}) -> {raw_dir}")

            for ddl_val, display_year, year_slug in YEARS:
                csv_path = raw_dir / f"asbr_{year_slug}.csv"
                xlsx_path = raw_dir / f"asbr_{year_slug}.xlsx"

                if csv_path.exists() and csv_path.stat().st_size > 1000 and xlsx_path.exists() and xlsx_path.stat().st_size > 1000:
                    print(f"[{slug} - {display_year}] Already cached: {csv_path.name}, {xlsx_path.name}")
                    continue

                print(f"[{slug} - {display_year}] Navigating to DESE OrgSelect...")
                try:
                    page.goto("https://apps.dese.mo.gov/DESEApplicationsSignin/OrgSelect?appId=6514&sort=0&appType=Public", timeout=45000)
                    page.wait_for_load_state("networkidle")

                    page.select_option("#CONTENT_VERSION_HEADER_ctlPublicVersionSelection_ddlDistrict", ddl_district)
                    time.sleep(2)
                    page.wait_for_load_state("networkidle")

                    page.select_option("#CONTENT_VERSION_HEADER_ctlPublicVersionSelection_ddlYear", ddl_val)
                    time.sleep(3)
                    page.wait_for_load_state("networkidle")

                    print(f"[{slug} - {display_year}] Launching SSRS ReportViewer popup...")
                    with page.expect_popup(timeout=30000) as popup_info:
                        page.click("#MainContent_lkbASBRReport")
                    popup = popup_info.value
                    popup.wait_for_load_state("networkidle")
                    time.sleep(4)

                    # Export CSV
                    print(f"[{slug} - {display_year}] Triggering SSRS CSV export...")
                    with popup.expect_download(timeout=30000) as dl_info:
                        popup.evaluate("$find('rvCert1').exportReport('CSV');")
                    dl = dl_info.value
                    dl.save_as(str(csv_path))
                    print(f"[{slug} - {display_year}] Saved CSV ({csv_path.stat().st_size} bytes)")

                    # Export Excel
                    print(f"[{slug} - {display_year}] Triggering SSRS Excel export...")
                    with popup.expect_download(timeout=30000) as dl_info_xl:
                        popup.evaluate("$find('rvCert1').exportReport('EXCELOPENXML');")
                    dl_xl = dl_info_xl.value
                    dl_xl.save_as(str(xlsx_path))
                    print(f"[{slug} - {display_year}] Saved Excel ({xlsx_path.stat().st_size} bytes)")

                    popup.close()
                    time.sleep(1)
                except Exception as e:
                    print(f"[{slug} - {display_year}] Error fetching SSRS report: {e}")

        browser.close()
        print("\n[+] Multi-district ASBR harvest finished.")

if __name__ == "__main__":
    harvest_districts()
