import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

print("=== CHECKING WEIRD / SURPRISING ANOMALIES ACROSS ALL RUNS ===\n")

topics = [
    ("Dodge City KS / Garden City Meatpacking ICE Raid Whispers", "text ILIKE '%ice%' AND (text ILIKE '%dodge city%' OR text ILIKE '%meatpacking%' OR text ILIKE '%plant%')"),
    ("Westport Gun War & Private Security Drone Perimeter", "text ILIKE '%westport%' AND (text ILIKE '%gun%' OR text ILIKE '%security%' OR text ILIKE '%checkpoint%' OR text ILIKE '%perimeter%')"),
    ("KC Underground DIY Raves & Industrial Caves", "text ILIKE '%cave%' OR (text ILIKE '%rave%' AND text ILIKE '%warehouse%') OR text ILIKE '%subtropolis%'"),
    ("Restaurant Surcharges & Downhill Canaries (In-A-Tub, Westport)", "text ILIKE '%surcharge%' OR (text ILIKE '%in-a-tub%' AND (text ILIKE '%powder%' OR text ILIKE '%cheese%'))")
]

for label, cond in topics:
    print(f"*** TOPIC: {label} ***")
    rows = con.execute(f"""
        SELECT artifact_id, platform, author_handle, text, canonical_url 
        FROM 'data/normalized/artifacts.parquet' 
        WHERE ({cond})
        LIMIT 3
    """).fetchall()
    for aid, p, author, text, url in rows:
        cleaned = ' '.join(text.split())[:260]
        print(f"  * [{aid[:8]}] [{p}] @{author}: \"{cleaned}\"")
        print(f"    -> {url}")
    print()
