import sys
sys.stdout.reconfigure(encoding="utf-8")
from ddgs import DDGS
import json

queries = [
    'site:snapchat.com/spotlight "Kansas City"',
    'site:snapchat.com/spotlight Westport Kansas',
    'site:snapchat.com/spotlight "West Bottoms"',
    'site:snapchat.com/spotlight "Crossroads" "Kansas City"',
    'site:snapchat.com "Kansas City" spotlight'
]

ddgs = DDGS()
found_links = {}

for q in queries:
    print(f"\nQuerying: {q}")
    try:
        results = list(ddgs.text(q, max_results=10))
        print(f"  Got {len(results)} results")
        for r in results:
            url = r.get("href") or ""
            title = r.get("title") or ""
            body = r.get("body") or ""
            if "snapchat.com" in url:
                found_links[url] = {"title": title, "snippet": body}
                print(f"    -> [{title}] {url}")
    except Exception as e:
        print(f"  Error: {e}")

print(f"\nTotal unique Snapchat links discovered: {len(found_links)}")
for u, info in found_links.items():
    print(f"- {info['title']}: {u}")
