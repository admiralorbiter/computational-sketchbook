"""
KC Job Intelligence Harvester — Prototype
==========================================
Combines live job posting discovery with ground-truth interview/culture
intelligence from Reddit, Glassdoor snippets, and community forums.

Phase 1: Discover actual open CS internship & entry-level postings in KC
Phase 2: Cross-reference companies with employee/interview reviews
Phase 3: Surface authentic voices on what the process actually looks like
"""

import asyncio
import json
import sys
from datetime import datetime, UTC
from ddgs import DDGS

sys.stdout.reconfigure(encoding='utf-8')

# ─── KC Tech Employer Universe ───────────────────────────────────────
KC_EMPLOYERS = [
    "Cerner", "Oracle Health", "Garmin", "T-Mobile", "Sprint",
    "Burns & McDonnell", "Black & Veatch", "Hallmark", "H&R Block",
    "Commerce Bank", "Lockton Companies", "VML", "Populous",
    "Netsmart Technologies", "C2FO", "Barkley", "DST Systems",
    "SS&C Technologies", "Federal Reserve Bank of Kansas City",
    "AMC Theatres", "Waddell & Reed", "USAA", "Fishtech Group",
    "Mariner Wealth Advisors", "SelectQuote", "Torch.AI",
    "Terracon", "Blue Cross Blue Shield of Kansas City",
    "Children's Mercy Hospital", "University of Kansas Health System",
    "Honeywell Federal Manufacturing", "Panasonic Energy",
    "EquipmentShare", "Paylocity", "Accenture", "Deloitte",
    "KPMG", "PwC", "Perspecta / Peraton", "Leidos",
]

# ─── Phase 1: Discover Active Job Postings ───────────────────────────
async def discover_postings():
    """Search for actual CS internship and entry-level postings in KC."""
    print("=" * 70)
    print("PHASE 1: DISCOVERING ACTIVE JOB POSTINGS")
    print("=" * 70)

    posting_queries = [
        '"computer science" internship "Kansas City" 2026 OR 2027',
        '"software engineer" intern "Kansas City" site:linkedin.com',
        '"software engineer" intern "Kansas City" site:indeed.com',
        '"software developer" intern OR "entry level" "Kansas City"',
        '"data science" intern OR "entry level" "Kansas City" 2026',
        '"IT" intern "Kansas City" summer 2027',
        '"cybersecurity" intern "Kansas City"',
        'entry level "software" OR "developer" OR "engineer" "Kansas City" junior',
        '"machine learning" OR "AI" intern OR junior "Kansas City"',
        '"full stack" OR "backend" OR "frontend" junior OR intern "Kansas City"',
    ]

    all_postings = []
    seen_urls = set()

    with DDGS() as ddgs:
        for q in posting_queries:
            print(f"\n  Searching: {q}")
            try:
                results = list(ddgs.text(q, max_results=10))
                for r in results:
                    url = r.get("href", "")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = r.get("title", "")
                    body = r.get("body", "")

                    # Classify posting source
                    source = "other"
                    if "linkedin.com" in url: source = "linkedin"
                    elif "indeed.com" in url: source = "indeed"
                    elif "glassdoor.com" in url: source = "glassdoor"
                    elif "handshake" in url: source = "handshake"
                    elif "ziprecruiter" in url: source = "ziprecruiter"
                    elif "lever.co" in url or "greenhouse.io" in url: source = "ats_direct"
                    elif "careers" in url or "jobs" in url: source = "company_careers"

                    # Try to identify company
                    company = "Unknown"
                    for emp in KC_EMPLOYERS:
                        if emp.lower() in title.lower() or emp.lower() in body.lower():
                            company = emp
                            break

                    posting = {
                        "title": title,
                        "company": company,
                        "url": url,
                        "source": source,
                        "snippet": body[:300],
                        "discovered_at": datetime.now(UTC).isoformat(),
                    }
                    all_postings.append(posting)
                    print(f"    [{source}] {company}: {title[:70]}")

            except Exception as e:
                print(f"    Error: {e}")

    print(f"\n  TOTAL UNIQUE POSTINGS DISCOVERED: {len(all_postings)}")
    return all_postings


# ─── Phase 2: Gather Company Intelligence ────────────────────────────
async def gather_company_intel(companies: list[str]):
    """For each company found in postings, gather interview/culture intel."""
    print("\n" + "=" * 70)
    print("PHASE 2: GATHERING COMPANY INTELLIGENCE")
    print("=" * 70)

    intel = {}

    with DDGS() as ddgs:
        for company in companies:
            if company == "Unknown":
                continue
            print(f"\n  --- {company} ---")
            intel[company] = {"glassdoor": [], "reddit": [], "blind": [], "other": []}

            intel_queries = [
                f'"{company}" "Kansas City" internship OR intern interview experience site:reddit.com',
                f'"{company}" "Kansas City" OR KC interview process glassdoor',
                f'"{company}" intern OR "entry level" review OR experience reddit',
                f'"{company}" "Kansas City" culture OR work environment OR "work life balance"',
            ]

            for iq in intel_queries:
                try:
                    results = list(ddgs.text(iq, max_results=5))
                    for r in results:
                        url = r.get("href", "")
                        title = r.get("title", "")
                        body = r.get("body", "")

                        cat = "other"
                        if "reddit.com" in url: cat = "reddit"
                        elif "glassdoor.com" in url: cat = "glassdoor"
                        elif "blind" in url.lower(): cat = "blind"

                        intel[company][cat].append({
                            "title": title,
                            "url": url,
                            "snippet": body[:400],
                        })
                        print(f"    [{cat}] {title[:65]}")

                except Exception as e:
                    print(f"    Error: {e}")

    return intel


# ─── Phase 3: Ghost Posting & Freshness Analysis ────────────────────
def analyze_postings(postings: list[dict], intel: dict):
    """Analyze posting freshness, ghost posting indicators, and intel coverage."""
    print("\n" + "=" * 70)
    print("PHASE 3: ANALYSIS & SYNTHESIS")
    print("=" * 70)

    # Company frequency
    company_counts = {}
    for p in postings:
        c = p["company"]
        company_counts[c] = company_counts.get(c, 0) + 1

    print("\n  TOP COMPANIES BY POSTING VOLUME:")
    for c, n in sorted(company_counts.items(), key=lambda x: -x[1])[:15]:
        has_intel = "✓ intel" if c in intel and any(intel[c].values()) else "✗ no intel"
        print(f"    {c}: {n} postings ({has_intel})")

    # Source distribution
    source_counts = {}
    for p in postings:
        s = p["source"]
        source_counts[s] = source_counts.get(s, 0) + 1

    print("\n  POSTING SOURCE DISTRIBUTION:")
    for s, n in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"    {s}: {n}")

    # Companies with intel but maybe ghost postings (lots of reviews saying "never heard back")
    print("\n  COMPANIES WITH INTERVIEW INTELLIGENCE:")
    for company, data in intel.items():
        total = sum(len(v) for v in data.values())
        if total > 0:
            breakdown = ", ".join(f"{k}:{len(v)}" for k, v in data.items() if v)
            print(f"    {company}: {total} items ({breakdown})")

    return company_counts


# ─── Main ────────────────────────────────────────────────────────────
async def main():
    print("KC COMPUTER SCIENCE JOB INTELLIGENCE OBSERVATORY")
    print(f"Run Time: {datetime.now(UTC).isoformat()}")
    print("=" * 70)

    # Phase 1: Discover postings
    postings = await discover_postings()

    # Extract unique companies
    companies = list(set(p["company"] for p in postings))
    print(f"\n  Unique companies identified: {len(companies)}")

    # Phase 2: Gather intel on discovered companies
    intel = await gather_company_intel(companies)

    # Phase 3: Analyze
    analyze_postings(postings, intel)

    # Save raw data
    output = {
        "run_id": "kc-cs-jobs-intel-2026-10",
        "timestamp": datetime.now(UTC).isoformat(),
        "total_postings": len(postings),
        "postings": postings,
        "company_intel": {k: {cat: items for cat, items in v.items()} for k, v in intel.items()},
    }

    with open("scratch/kc_cs_jobs_intel.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  Raw data saved to scratch/kc_cs_jobs_intel.json")
    print("=" * 70)
    print("HARVEST COMPLETE")


if __name__ == "__main__":
    asyncio.run(main())
