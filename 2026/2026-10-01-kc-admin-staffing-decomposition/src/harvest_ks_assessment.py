"""
src/harvest_ks_assessment.py

Harvest official KSDE KAP assessment performance levels and participation data
for the 19 Kansas balanced panel districts across 2018-19 through 2023-24.

Source:
- KSDE Performance Level Reports: https://ksreportcard.ksde.gov/assessment_results.aspx
- KSDE Participation Summary Reports: https://ksreportcard.ksde.gov/part_details.aspx
"""

import os
import time
import pandas as pd
from playwright.sync_api import sync_playwright

KS_USD_MAP = {
    "202": {"nces_id": 2012360, "name": "Turner-Kansas City"},
    "203": {"nces_id": 2010680, "name": "Piper-Kansas City"},
    "204": {"nces_id": 2004050, "name": "Bonner Springs"},
    "207": {"nces_id": 2006330, "name": "Fort Leavenworth"},
    "229": {"nces_id": 2012000, "name": "Blue Valley"},
    "230": {"nces_id": 2011850, "name": "Spring Hill"},
    "231": {"nces_id": 2006420, "name": "Gardner Edgerton"},
    "232": {"nces_id": 2005490, "name": "De Soto"},
    "233": {"nces_id": 2010140, "name": "Olathe"},
    "367": {"nces_id": 2010260, "name": "Osawatomie"},
    "368": {"nces_id": 2010500, "name": "Paola"},
    "416": {"nces_id": 2008970, "name": "Louisburg"},
    "449": {"nces_id": 2005640, "name": "Easton"},
    "453": {"nces_id": 2008430, "name": "Leavenworth"},
    "458": {"nces_id": 2003780, "name": "Basehor-Linwood"},
    "464": {"nces_id": 2012210, "name": "Tonganoxie"},
    "469": {"nces_id": 2008340, "name": "Lansing"},
    "500": {"nces_id": 2007950, "name": "Kansas City"},
    "512": {"nces_id": 2011640, "name": "Shawnee Mission Pub Sch"},
}


def harvest_ks_performance(browser, usd_list):
    print("=== Harvesting Kansas Assessment Performance ===")
    page = browser.new_page()
    records = []
    
    subjects = [("ELA", "0"), ("Math", "1")]
    # Query year options on KSDE: 
    # 2019 yields (2018, 2019)
    # 2022 yields (2021, 2022)
    # 2024 yields (2023, 2024)
    year_opts = ["2019", "2022", "2024"]

    for idx, usd in enumerate(usd_list):
        nces_id = KS_USD_MAP[usd]["nces_id"]
        dist_name = KS_USD_MAP[usd]["name"]
        org_val = f"D0{usd}" if len(usd) == 3 else f"D{usd}"
        url = f"https://ksreportcard.ksde.gov/assessment_results.aspx?org_no={org_val}&rptType=2"
        print(f"[{idx+1}/{len(usd_list)}] Navigating to {dist_name} (USD {usd}, {org_val})...")
        
        try:
            page.goto(url, timeout=45000)
            page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"  Error loading {url}: {e}")
            continue

        for subj_name, subj_val in subjects:
            try:
                curr_subj = page.query_selector("#ddlSubject").input_value()
                if curr_subj != subj_val:
                    with page.expect_navigation(timeout=30000):
                        page.select_option("#ddlSubject", subj_val)
                    page.wait_for_load_state("networkidle")
                    time.sleep(0.3)
            except Exception as e:
                print(f"  Error selecting subject {subj_name}: {e}")
                continue

            for y_opt in year_opts:
                try:
                    curr_yr = page.query_selector("#ddlSchoolYear").input_value()
                    if curr_yr != y_opt:
                        with page.expect_navigation(timeout=30000):
                            page.select_option("#ddlSchoolYear", y_opt)
                        page.wait_for_load_state("networkidle")
                        time.sleep(0.3)

                    tables = page.query_selector_all("table")
                    if len(tables) > 1:
                        t1 = tables[1]
                        rows = t1.query_selector_all("tr")
                        for r in rows[1:]:
                            cells = [c.inner_text().strip() for c in r.query_selector_all("td")]
                            if len(cells) >= 7:
                                org_lvl = cells[0]
                                prog_yr = cells[1]
                                records.append({
                                    "usd_code": usd,
                                    "nces_lea_id": nces_id,
                                    "district_name": dist_name,
                                    "subject": subj_name,
                                    "query_year_opt": y_opt,
                                    "org_level": org_lvl,
                                    "program_year": int(prog_yr) if prog_yr.isdigit() else prog_yr,
                                    "pct_level_1": cells[2],
                                    "pct_level_2": cells[3],
                                    "pct_level_3": cells[4],
                                    "pct_level_4": cells[5],
                                    "pct_not_tested": cells[6],
                                })
                except Exception as e:
                    print(f"  Error processing USD {usd} {subj_name} {y_opt}: {e}")

    page.close()
    return pd.DataFrame(records)


def harvest_ks_participation(browser, usd_list):
    print("=== Harvesting Kansas Assessment Participation ===")
    page = browser.new_page()
    records = []
    
    # We want years 2019, 2021, 2022, 2023, 2024
    years = ["2019", "2021", "2022", "2023", "2024"]

    for idx, usd in enumerate(usd_list):
        nces_id = KS_USD_MAP[usd]["nces_id"]
        dist_name = KS_USD_MAP[usd]["name"]
        org_val = f"D0{usd}" if len(usd) == 3 else f"D{usd}"
        url = f"https://ksreportcard.ksde.gov/part_details.aspx?org_no={org_val}&rptType=2"
        print(f"[{idx+1}/{len(usd_list)}] Navigating to participation {dist_name} (USD {usd})...")

        try:
            page.goto(url, timeout=45000)
            page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"  Error loading {url}: {e}")
            continue

        subj_map = {}
        for o in page.query_selector("#ddlSubject").query_selector_all("option"):
            txt = o.inner_text().strip()
            val = o.get_attribute("value")
            if "Math" in txt and "All" in txt:
                subj_map["Math"] = val
            elif "ELA" in txt and "All" in txt:
                subj_map["ELA"] = val

        for subj_name, subj_val in subj_map.items():
            try:
                curr_subj = page.query_selector("#ddlSubject").input_value()
                if curr_subj != subj_val:
                    with page.expect_navigation(timeout=30000):
                        page.select_option("#ddlSubject", subj_val)
                    page.wait_for_load_state("networkidle")
                    time.sleep(0.3)
            except Exception as e:
                print(f"  Error selecting subject {subj_name}: {e}")
                continue

            for yr in years:
                try:
                    curr_yr = page.query_selector("#ddlSchoolYear").input_value()
                    if curr_yr != yr:
                        with page.expect_navigation(timeout=30000):
                            page.select_option("#ddlSchoolYear", yr)
                        page.wait_for_load_state("networkidle")
                        time.sleep(0.3)

                    tables = page.query_selector_all("table")
                    if len(tables) > 1:
                        t = tables[1]
                        for r in t.query_selector_all("tr")[1:]:
                            cells = [c.inner_text().strip() for c in r.query_selector_all("td")]
                            if len(cells) >= 5 and "All Students" in cells[0]:
                                records.append({
                                    "usd_code": usd,
                                    "nces_lea_id": nces_id,
                                    "district_name": dist_name,
                                    "subject": subj_name,
                                    "school_year": yr,
                                    "group_name": cells[0],
                                    "test_pool": cells[1],
                                    "total_tested_n": cells[2],
                                    "part_rate_pct": cells[3],
                                    "not_tested_pct": cells[4],
                                })
                                break
                except Exception as e:
                    print(f"  Error processing participation USD {usd} {subj_name} {yr}: {e}")

    page.close()
    return pd.DataFrame(records)


def main():
    os.makedirs("data/raw/ks_assessment", exist_ok=True)
    usd_list = sorted(list(KS_USD_MAP.keys()))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        df_perf = harvest_ks_performance(browser, usd_list)
        perf_path = "data/raw/ks_assessment/ks_assessment_performance.csv"
        df_perf.to_csv(perf_path, index=False)
        print(f"Saved {len(df_perf)} performance records to {perf_path}")
        
        df_part = harvest_ks_participation(browser, usd_list)
        part_path = "data/raw/ks_assessment/ks_assessment_participation.csv"
        df_part.to_csv(part_path, index=False)
        print(f"Saved {len(df_part)} participation records to {part_path}")
        
        browser.close()


if __name__ == "__main__":
    main()
