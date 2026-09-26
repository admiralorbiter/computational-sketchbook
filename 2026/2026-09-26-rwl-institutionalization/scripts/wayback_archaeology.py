"""
Wayback Machine archaeology for Grandview C-4.

This script creates an inventory of historical captures. It does NOT treat hitting a
CDX query limit as proof that the full archive has been enumerated.
"""

import os
import json
import subprocess
import urllib.parse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data/raw/grandview-c4/communications")
SUMMARY_OUT = os.path.join(PROJECT_ROOT, "districts/grandview-c4/communications/wayback_cdx_summary.json")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def query_cdx(url_pattern, from_year=2018, to_year=2026, limit=5000):
    params = {
        "url": url_pattern,
        "output": "json",
        "from": str(from_year),
        "to": str(to_year),
        "limit": str(limit),
        "filter": "statuscode:200",
    }
    cdx_url = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode(params)
    cmd = ["curl.exe", "-s", "-L", "-A", USER_AGENT, cdx_url]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"curl failed for CDX query {url_pattern}: {res.stderr[:300]}")
    try:
        data = json.loads(res.stdout)
    except Exception as exc:
        raise RuntimeError(f"CDX parse error for {url_pattern}: {exc}") from exc
    if len(data) <= 1:
        return []
    headers = data[0]
    return [dict(zip(headers, row)) for row in data[1:]]

def query_variants(path_pattern, limit=5000):
    """Query both apex and www hostnames and deduplicate captures."""
    rows = []
    for host in ("grandviewc4.net", "www.grandviewc4.net"):
        rows.extend(query_cdx(f"{host}{path_pattern}", limit=limit))
    deduped = {}
    for row in rows:
        key = (row.get("timestamp"), row.get("original"), row.get("digest"))
        deduped[key] = row
    return sorted(deduped.values(), key=lambda r: (r.get("timestamp", ""), r.get("original", "")))

def summarize_years(rows):
    out = {}
    for row in rows:
        year = row.get("timestamp", "")[:4]
        if year:
            out[year] = out.get(year, 0) + 1
    return out

def run_archaeology():
    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    # A wildcard root/site query is intentionally separate from targeted staff/news
    # queries. Large counts are inventories, not evidence that every capture was retrieved.
    site_limit = 10000
    targeted_limit = 5000
    site_captures = query_variants("/*", limit=site_limit)
    staff_captures = query_variants("/apps/staff/*", limit=targeted_limit)
    news_captures = query_variants("/apps/news/*", limit=targeted_limit)

    raw_file = os.path.join(DATA_RAW_DIR, "wayback_cdx_index.json")
    payload = {
        "site_captures": site_captures,
        "staff_captures": staff_captures,
        "news_captures": news_captures,
        "query_limits": {"site": site_limit, "staff": targeted_limit, "news": targeted_limit},
    }
    with open(raw_file, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    summary = {
        "total_site_snapshots_returned": len(site_captures),
        "total_staff_snapshots_returned": len(staff_captures),
        "total_news_snapshots_returned": len(news_captures),
        "site_by_year": summarize_years(site_captures),
        "staff_by_year": summarize_years(staff_captures),
        "news_by_year": summarize_years(news_captures),
        "earliest_staff_snapshot": staff_captures[0]["timestamp"] if staff_captures else None,
        "latest_staff_snapshot": staff_captures[-1]["timestamp"] if staff_captures else None,
        "site_query_may_be_truncated": len(site_captures) >= site_limit,
        "staff_query_may_be_truncated": len(staff_captures) >= targeted_limit,
        "news_query_may_be_truncated": len(news_captures) >= targeted_limit,
        "interpretation": "Returned capture counts are inventory counts, not proof of complete Internet Archive coverage.",
    }
    with open(SUMMARY_OUT, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    run_archaeology()
