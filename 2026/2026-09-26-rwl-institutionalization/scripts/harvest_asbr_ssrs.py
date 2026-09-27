"""Harvest official DESE ASBR financial reports for Grandview C-4 directly from SSRS ReportViewer.

Automates selection of Grandview C-4 (048074) across all school years (2018-19 to 2023-24),
triggers direct SSRS CSV and Excel exports, and stores pristine state filings in
data/raw/grandview-c4/finance/asbr/.
"""

import os
import time
from playwright.sync_api import sync_playwright

YEARS = [
    ('2024|GENERAL', '2023-2024', '2023_2024'),
    ('2023|GENERAL', '2022-2023', '2022_2023'),
    ('2022|GENERAL', '2021-2022', '2021_2022'),
    ('2021|GENERAL', '2020-2021', '2020_2021'),
    ('2020|GENERAL', '2019-2020', '2019_2020'),
    ('2019|GENERAL', '2018-2019', '2018_2019'),
]

RAW_DIR = os.path.abspath('2026/2026-09-26-rwl-institutionalization/data/raw/grandview-c4/finance/asbr')

def harvest_ssrs_exports():
    os.makedirs(RAW_DIR, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        for ddl_val, display_year, slug in YEARS:
            csv_path = os.path.join(RAW_DIR, f'asbr_{slug}.csv')
            xlsx_path = os.path.join(RAW_DIR, f'asbr_{slug}.xlsx')

            if os.path.exists(csv_path) and os.path.getsize(csv_path) > 1000:
                print(f'[{display_year}] Already cached: {csv_path}', flush=True)
                continue

            print(f'[{display_year}] Navigating to DESE OrgSelect...', flush=True)
            try:
                page.goto('https://apps.dese.mo.gov/DESEApplicationsSignin/OrgSelect?appId=6514&sort=0&appType=Public', timeout=45000)
                page.wait_for_load_state('networkidle')

                page.select_option('#CONTENT_VERSION_HEADER_ctlPublicVersionSelection_ddlDistrict', '48074')
                time.sleep(2)
                page.wait_for_load_state('networkidle')

                page.select_option('#CONTENT_VERSION_HEADER_ctlPublicVersionSelection_ddlYear', ddl_val)
                time.sleep(3)
                page.wait_for_load_state('networkidle')

                print(f'[{display_year}] Launching SSRS ReportViewer popup...', flush=True)
                with page.expect_popup(timeout=30000) as popup_info:
                    page.click('#MainContent_lkbASBRReport')
                popup = popup_info.value
                popup.wait_for_load_state('networkidle')
                time.sleep(4)

                # Export CSV
                print(f'[{display_year}] Triggering SSRS CSV export...', flush=True)
                with popup.expect_download(timeout=30000) as dl_info:
                    popup.evaluate("$find('rvCert1').exportReport('CSV');")
                dl = dl_info.value
                dl.save_as(csv_path)
                print(f'[{display_year}] Saved CSV ({os.path.getsize(csv_path)} bytes) -> {csv_path}', flush=True)

                # Export Excel
                print(f'[{display_year}] Triggering SSRS Excel export...', flush=True)
                with popup.expect_download(timeout=30000) as dl_info_xl:
                    popup.evaluate("$find('rvCert1').exportReport('EXCELOPENXML');")
                dl_xl = dl_info_xl.value
                dl_xl.save_as(xlsx_path)
                print(f'[{display_year}] Saved Excel ({os.path.getsize(xlsx_path)} bytes) -> {xlsx_path}', flush=True)

                popup.close()
                time.sleep(1)
            except Exception as e:
                print(f'[{display_year}] Error fetching SSRS report: {e}', flush=True)

        browser.close()

if __name__ == '__main__':
    harvest_ssrs_exports()
