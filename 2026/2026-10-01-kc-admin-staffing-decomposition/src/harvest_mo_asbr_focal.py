"""
Harvest Missouri DESE ASBR statutory Excel workbooks for focal archetypes:
- Lee's Summit R-VII (48071)
- North Kansas City 74 (24093)
- Raytown C-2 (48073)
Across benchmark years 2014-15, 2018-19, and 2022-23 (and all intervening years).
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "missouri_asbr"
RAW_DIR.mkdir(parents=True, exist_ok=True)

DISTRICTS = [
    {"slug": "lees_summit", "ddl_val": "48071", "code": "048-071", "name": "Lee's Summit R-VII"},
    {"slug": "north_kansas_city", "ddl_val": "24093", "code": "024-093", "name": "North Kansas City 74"},
    {"slug": "raytown", "ddl_val": "48073", "code": "048-073", "name": "Raytown C-2"},
]

YEARS = [
    ("2023|GENERAL", "2022-2023", "2022_2023"),
    ("2019|GENERAL", "2018-2019", "2018_2019"),
    ("2015|GENERAL", "2014-2015", "2014_2015"),
]

def harvest_asbr():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for d in DISTRICTS:
            slug = d["slug"]
            ddl_val = d["ddl_val"]
            dname = d["name"]
            dist_dir = RAW_DIR / slug
            dist_dir.mkdir(parents=True, exist_ok=True)

            print(f"\n========================================================")
            print(f"[*] Harvesting {dname} (DDL: {ddl_val}) -> {dist_dir}")

            for ddl_year, display_year, year_slug in YEARS:
                xlsx_path = dist_dir / f"asbr_{year_slug}.xlsx"
                if xlsx_path.exists() and xlsx_path.stat().st_size > 10000:
                    print(f"[{slug} - {display_year}] Cached: {xlsx_path.name}")
                    continue

                print(f"[{slug} - {display_year}] Navigating to DESE OrgSelect...")
                page.goto("https://apps.dese.mo.gov/DESEApplicationsSignin/OrgSelect?appId=6514&sort=0&appType=Public", timeout=45000)
                page.wait_for_load_state("networkidle")

                page.select_option("#CONTENT_VERSION_HEADER_ctlPublicVersionSelection_ddlDistrict", ddl_val)
                time.sleep(2)
                page.wait_for_load_state("networkidle")

                page.select_option("#CONTENT_VERSION_HEADER_ctlPublicVersionSelection_ddlYear", ddl_year)
                time.sleep(2)
                page.wait_for_load_state("networkidle")

                print(f"[{slug} - {display_year}] Launching SSRS ReportViewer popup...")
                with page.expect_popup(timeout=30000) as popup_info:
                    page.click("#MainContent_lkbASBRReport")
                popup = popup_info.value
                popup.wait_for_load_state("networkidle")
                time.sleep(4)

                print(f"[{slug} - {display_year}] Triggering SSRS Excel export...")
                with popup.expect_download(timeout=30000) as dl_info_xl:
                    popup.evaluate("$find('rvCert1').exportReport('EXCELOPENXML');")
                dl_xl = dl_info_xl.value
                dl_xl.save_as(str(xlsx_path))
                print(f"[{slug} - {display_year}] Saved Excel ({xlsx_path.stat().st_size} bytes)")
                popup.close()

        browser.close()
    print("\n[SUCCESS] Completed Missouri ASBR harvesting.")

if __name__ == "__main__":
    harvest_asbr()
