"""
KC Job Intelligence Harvester v2
================================
Broader queries, multiple search passes, direct job board targeting.
"""

import asyncio
import json
import sys
from datetime import datetime, UTC
from ddgs import DDGS

sys.stdout.reconfigure(encoding='utf-8')

KC_EMPLOYERS = [
    "Cerner", "Oracle Health", "Oracle", "Garmin", "T-Mobile",
    "Burns McDonnell", "Black Veatch", "Hallmark", "H&R Block",
    "Commerce Bank", "Lockton", "VML", "Populous",
    "Netsmart", "C2FO", "Barkley", "DST Systems",
    "SS&C", "Federal Reserve Bank", "AMC Theatres",
    "USAA", "Fishtech", "Torch.AI", "Terracon",
    "Blue Cross Blue Shield", "Children's Mercy",
    "KU Health System", "KUMC", "Honeywell",
    "Panasonic", "EquipmentShare", "Paylocity",
    "Accenture", "Deloitte", "KPMG", "PwC",
    "Peraton", "Leidos", "Carvana", "SelectQuote",
    "Sprint", "Waddell Reed", "Mariner Wealth",
    "Epic", "Euronet", "SkillPath", "DEG Digital",
    "Bestow", "Cobalt Speech", "Spire", "Evergy",
]


def search_ddgs(query, max_results=12):
    """Run a single DDGS search and return results."""
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


def classify_source(url):
    if "linkedin.com" in url: return "linkedin"
    if "indeed.com" in url: return "indeed"
    if "glassdoor.com" in url: return "glassdoor"
    if "handshake" in url: return "handshake"
    if "ziprecruiter" in url: return "ziprecruiter"
    if "lever.co" in url or "greenhouse.io" in url: return "ats_direct"
    if "builtin.com" in url: return "builtin"
    if "reddit.com" in url: return "reddit"
    if "careers" in url or "jobs" in url: return "company_careers"
    return "other"


def identify_company(title, body):
    text = (title + " " + body).lower()
    for emp in KC_EMPLOYERS:
        if emp.lower() in text:
            return emp
    return "Unknown"


def main():
    print("KC COMPUTER SCIENCE JOB INTELLIGENCE OBSERVATORY v2")
    print(f"Run Time: {datetime.now(UTC).isoformat()}")
    print("=" * 70)

    # ─── PHASE 1: JOB POSTING DISCOVERY ──────────────────────────────
    print("\n" + "=" * 70)
    print("PHASE 1: DISCOVERING ACTIVE JOB POSTINGS")
    print("=" * 70)

    posting_queries = [
        # Broad job board searches
        "software intern Kansas City 2026",
        "software intern Kansas City 2027",
        "computer science internship Kansas City",
        "software engineer internship Kansas City",
        "data science intern Kansas City",
        "cybersecurity intern Kansas City",
        "IT internship Kansas City",
        "entry level software developer Kansas City",
        "junior software engineer Kansas City",
        "entry level developer Kansas City",
        "new grad software Kansas City",
        # Company-specific
        "Garmin intern software Olathe",
        "Cerner intern software Kansas City",
        "Oracle Health intern Kansas City",
        "Burns McDonnell intern technology Kansas City",
        "Hallmark intern technology Kansas City",
        "H&R Block intern technology Kansas City",
        "T-Mobile intern software Kansas City",
        "Federal Reserve Bank Kansas City intern technology",
        "Black Veatch intern technology",
        "Commerce Bank intern technology Kansas City",
        # Job boards
        "Kansas City software intern indeed",
        "Kansas City software intern linkedin",
        "Kansas City tech internships builtin",
        "Kansas City computer science jobs entry level",
    ]

    all_postings = []
    seen_urls = set()

    for q in posting_queries:
        print(f"\n  Searching: {q}")
        try:
            results = search_ddgs(q, max_results=10)
            count = 0
            for r in results:
                url = r.get("href", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title = r.get("title", "")
                body = r.get("body", "")
                source = classify_source(url)
                company = identify_company(title, body)

                posting = {
                    "title": title,
                    "company": company,
                    "url": url,
                    "source": source,
                    "snippet": body[:350],
                }
                all_postings.append(posting)
                count += 1
                print(f"    [{source}] {company}: {title[:70]}")

            if count == 0:
                print(f"    (no new results)")

        except Exception as e:
            print(f"    Error: {e}")

    print(f"\n  TOTAL UNIQUE RESULTS: {len(all_postings)}")

    # ─── PHASE 2: COMPANY INTELLIGENCE ───────────────────────────────
    print("\n" + "=" * 70)
    print("PHASE 2: GATHERING COMPANY & INTERVIEW INTELLIGENCE")
    print("=" * 70)

    companies_found = list(set(p["company"] for p in all_postings if p["company"] != "Unknown"))
    print(f"  Companies to investigate: {companies_found}")

    intel = {}

    # General KC tech scene intel
    general_queries = [
        "Kansas City tech internship experience reddit",
        "Kansas City software engineer interview reddit",
        "best companies to intern at Kansas City tech",
        "Kansas City tech companies hiring interns glassdoor",
        "Cerner Oracle Health internship interview experience",
        "Garmin internship review intern experience",
        "Kansas City junior developer salary reddit",
        "ghost job posting Kansas City tech",
        "Kansas City tech jobs actually hiring reddit",
        "r/cscareerquestions Kansas City",
        "Kansas City software developer Glassdoor reviews",
        "Hallmark technology internship review",
        "Burns McDonnell technology intern review",
        "H&R Block technology internship review",
        "Federal Reserve Kansas City intern experience",
    ]

    general_intel = []
    seen_intel_urls = set()

    for q in general_queries:
        print(f"\n  Searching: {q}")
        try:
            results = search_ddgs(q, max_results=8)
            count = 0
            for r in results:
                url = r.get("href", "")
                if url in seen_intel_urls:
                    continue
                seen_intel_urls.add(url)

                title = r.get("title", "")
                body = r.get("body", "")
                source = classify_source(url)
                company = identify_company(title, body)

                item = {
                    "title": title,
                    "company": company,
                    "url": url,
                    "source": source,
                    "snippet": body[:400],
                }
                general_intel.append(item)
                count += 1
                print(f"    [{source}] {company}: {title[:65]}")

            if count == 0:
                print(f"    (no new results)")

        except Exception as e:
            print(f"    Error: {e}")

    print(f"\n  TOTAL INTEL ITEMS: {len(general_intel)}")

    # ─── PHASE 3: ANALYSIS ───────────────────────────────────────────
    print("\n" + "=" * 70)
    print("PHASE 3: ANALYSIS & SYNTHESIS")
    print("=" * 70)

    # Company frequency in postings
    company_counts = {}
    for p in all_postings:
        c = p["company"]
        company_counts[c] = company_counts.get(c, 0) + 1

    print("\n  TOP COMPANIES BY POSTING VOLUME:")
    for c, n in sorted(company_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"    {c}: {n} postings")

    # Source distribution
    source_counts = {}
    for p in all_postings:
        s = p["source"]
        source_counts[s] = source_counts.get(s, 0) + 1

    print("\n  POSTING SOURCE DISTRIBUTION:")
    for s, n in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"    {s}: {n}")

    # Intel by company
    intel_by_company = {}
    for item in general_intel:
        c = item["company"]
        if c not in intel_by_company:
            intel_by_company[c] = []
        intel_by_company[c].append(item)

    print("\n  COMPANIES WITH INTERVIEW/CULTURE INTELLIGENCE:")
    for c, items in sorted(intel_by_company.items(), key=lambda x: -len(x[1])):
        sources = {}
        for i in items:
            s = i["source"]
            sources[s] = sources.get(s, 0) + 1
        breakdown = ", ".join(f"{k}:{v}" for k, v in sources.items())
        print(f"    {c}: {len(items)} items ({breakdown})")

    # Intel source distribution
    intel_source_counts = {}
    for item in general_intel:
        s = item["source"]
        intel_source_counts[s] = intel_source_counts.get(s, 0) + 1

    print("\n  INTEL SOURCE DISTRIBUTION:")
    for s, n in sorted(intel_source_counts.items(), key=lambda x: -x[1]):
        print(f"    {s}: {n}")

    # ─── SAVE ────────────────────────────────────────────────────────
    output = {
        "run_id": "kc-cs-jobs-intel-v2-2026-10",
        "timestamp": datetime.now(UTC).isoformat(),
        "total_postings": len(all_postings),
        "total_intel": len(general_intel),
        "postings": all_postings,
        "intel": general_intel,
    }

    with open("scratch/kc_cs_jobs_intel_v2.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  Raw data saved to scratch/kc_cs_jobs_intel_v2.json")
    print("=" * 70)
    print("HARVEST COMPLETE")


if __name__ == "__main__":
    main()
