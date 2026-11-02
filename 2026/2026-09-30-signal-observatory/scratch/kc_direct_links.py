"""
KC Job Intel — Phase 2.5: Direct Application Link Harvester
============================================================
Targets actual ATS/career page postings, not job board search result pages.
"""
import sys
from datetime import datetime, UTC
from ddgs import DDGS

sys.stdout.reconfigure(encoding='utf-8')

def search(query, max_results=10):
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))

# Company-specific ATS / careers page searches
company_queries = {
    "Garmin": [
        "site:careers.garmin.com software intern",
        "site:careers.garmin.com engineer intern 2027",
    ],
    "T-Mobile": [
        "site:careers.t-mobile.com software intern",
        "site:careers.t-mobile.com engineering intern 2027",
    ],
    "Commerce Bank": [
        "site:commercebank.com careers intern IT",
        "Commerce Bank IT intern summer 2027 workday",
    ],
    "Federal Reserve KC": [
        "site:kansascityfed.org intern",
        "site:kansascityfed.org TechEdge",
    ],
    "Burns & McDonnell": [
        "site:burnsmcd.com intern technology",
        "Burns McDonnell information technology intern Kansas City",
    ],
    "Hallmark": [
        "site:hallmark.com careers intern",
        "Hallmark technology intern 2027 Kansas City",
    ],
    "Netsmart": [
        "site:ntst.wd1.myworkdayjobs.com software intern",
        "Netsmart Technologies software engineer intern",
    ],
    "Black & Veatch": [
        "site:bv.com careers intern technology",
        "Black Veatch technology intern 2027",
    ],
    "KCNSC / Honeywell": [
        "site:kcnsc.doe.gov intern",
        "Kansas City National Security Campus intern software",
    ],
    "Lockton": [
        "site:careers.lockton.com intern technology",
        "Lockton intern Kansas City technology 2027",
    ],
    "H&R Block": [
        "H&R Block technology intern Kansas City 2027",
        "H&R Block software engineer intern",
    ],
    "Cerner / Oracle Health": [
        "Oracle Health intern software 2027 Kansas City",
        "Cerner Oracle software development intern",
    ],
    "Evergy": [
        "Evergy intern technology Kansas City 2027",
    ],
    "Blue KC (BCBS)": [
        "Blue Cross Blue Shield Kansas City intern technology",
    ],
    "Children's Mercy": [
        "Children's Mercy Kansas City intern IT technology",
    ],
    "C2FO": [
        "C2FO intern software engineer Kansas City",
    ],
    "Torch.AI": [
        "Torch.AI Kansas City intern software",
    ],
    "EquipmentShare": [
        "EquipmentShare intern software engineer Kansas City",
    ],
}

print("KC DIRECT APPLICATION LINK HARVESTER")
print(f"Run: {datetime.now(UTC).isoformat()}")
print("=" * 80)

all_direct = []
for company, queries in company_queries.items():
    print(f"\n{'─' * 60}")
    print(f"  {company}")
    print(f"{'─' * 60}")
    
    for q in queries:
        try:
            results = search(q, max_results=8)
            for r in results:
                url = r.get("href", "")
                title = r.get("title", "")
                body = r.get("body", "")
                
                # Flag direct application vs search page
                is_direct = any(x in url for x in [
                    "careers.", "jobs.", "workday", "lever.co",
                    "greenhouse.io", "icims", "taleo", "wd1.", "wd5.",
                    "kcnsc.doe.gov", "kansascityfed.org",
                ])
                
                tag = "DIRECT" if is_direct else "search"
                print(f"    [{tag}] {title[:70]}")
                print(f"           {url[:90]}")
                
                all_direct.append({
                    "company": company,
                    "title": title,
                    "url": url,
                    "snippet": body[:300],
                    "is_direct_application": is_direct,
                })
                
        except Exception as e:
            print(f"    Error: {e}")

print(f"\n{'=' * 80}")
print(f"TOTAL RESULTS: {len(all_direct)}")
direct_count = sum(1 for d in all_direct if d["is_direct_application"])
print(f"DIRECT APPLICATION LINKS: {direct_count}")
print(f"SEARCH/LISTING PAGES: {len(all_direct) - direct_count}")

# Save
import json
with open("scratch/kc_direct_application_links.json", "w", encoding="utf-8") as f:
    json.dump(all_direct, f, indent=2, ensure_ascii=False)
print(f"\nSaved to scratch/kc_direct_application_links.json")
