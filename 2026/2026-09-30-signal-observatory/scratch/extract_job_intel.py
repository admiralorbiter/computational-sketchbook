import json, sys
sys.stdout.reconfigure(encoding='utf-8')

d = json.load(open('scratch/kc_cs_jobs_intel_v2.json', 'r', encoding='utf-8'))
postings = d['postings']
intel = d['intel']

print("=" * 80)
print("POSTINGS WITH IDENTIFIED COMPANIES")
print("=" * 80)
for p in postings:
    if p['company'] != 'Unknown':
        print(f"  {p['company']:22s} | {p['source']:15s} | {p['title'][:65]}")
        print(f"  {'':22s}   {p['url'][:90]}")
        print()

print()
print("=" * 80)
print("KEY INTEL — REDDIT & GLASSDOOR SNIPPETS")
print("=" * 80)
for i in intel:
    if i['source'] in ('reddit', 'glassdoor'):
        print(f"\n  [{i['source'].upper()}] Company: {i['company']}")
        print(f"  Title: {i['title'][:80]}")
        print(f"  URL: {i['url'][:90]}")
        print(f"  Snippet: {i['snippet'][:350]}")
        print("  " + "-" * 70)

print()
print("=" * 80)
print("ALL POSTINGS — SOURCE BREAKDOWN")
print("=" * 80)
by_source = {}
for p in postings:
    s = p['source']
    if s not in by_source:
        by_source[s] = []
    by_source[s].append(p)

for source, items in sorted(by_source.items(), key=lambda x: -len(x[1])):
    print(f"\n  --- {source} ({len(items)} results) ---")
    for p in items[:5]:
        print(f"    {p['company']:20s} | {p['title'][:65]}")
        print(f"    {'':20s}   {p['url'][:90]}")
