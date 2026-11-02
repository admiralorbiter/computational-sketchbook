import sys
from ddgs import DDGS

sys.stdout.reconfigure(encoding='utf-8')

queries = [
    "site:reddit.com/r/kansascity olathe school closures",
    "site:reddit.com/r/kansascity independence 4 day school week",
    "site:reddit.com/r/kansascity kansas city cell phone ban school",
    "site:reddit.com/r/Teachers kansas city school district admin",
    "site:reddit.com/r/kansascity shawnee mission teachers"
]

print("=== HARVESTING RECENT FIRSTHAND REDDIT VOICES VIA DDGS ===\n")

ddgs = DDGS()
for q in queries:
    print(f"QUERY: {q}")
    try:
        results = list(ddgs.text(q, max_results=5))
        for r in results:
            print(f"  * Title: {r.get('title')}")
            print(f"    Snippet: {r.get('body')}")
            print(f"    URL: {r.get('href')}\n")
    except Exception as e:
        print(f"Error: {e}")
    print("=" * 60)
