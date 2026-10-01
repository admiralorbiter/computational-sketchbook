import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

print("=== INVESTIGATING SURPRISING / RED FLAG / WEIRD STORIES IN CORPUS ===\n")

queries = [
    ("Guns, Weapons & Police Coverups in Schools", 
     "(text ILIKE '%gun%' OR text ILIKE '%glock%' OR text ILIKE '%police%' OR text ILIKE '%internal affairs%' OR text ILIKE '%protection order%') AND (text ILIKE '%school%' OR text ILIKE '%district%' OR text ILIKE '%high%')"),
    ("Bizarre Board Moments, Threats & Culture Clashes", 
     "text ILIKE '%flag%' OR text ILIKE '%lynch%' OR text ILIKE '%redneck%' OR text ILIKE '%turning point%' OR text ILIKE '%sticker%' OR text ILIKE '%book ban%'"),
    ("Busing & Logistics Meltdowns (Zum & Shifts)", 
     "text ILIKE '%zum%' OR text ILIKE '%bus route%' OR text ILIKE '%7 am%' OR text ILIKE '%crossing guard%'"),
    ("Vendor & Classified Staff Cuts (Kokua, Subs, Classified)", 
     "text ILIKE '%kokua%' OR text ILIKE '%classified%' OR text ILIKE '%holiday pay%' OR text ILIKE '%substitute%'"),
    ("Weird / High-Friction Local Incidents & Scandals", 
     "(text ILIKE '%scandal%' OR text ILIKE '%retaliat%' OR text ILIKE '%investigat%' OR text ILIKE '%walkout%') AND (text ILIKE '%school%' OR text ILIKE '%teacher%')")
]

for title, cond in queries:
    print(f"*** {title} ***")
    rows = con.execute(f"""
        SELECT artifact_id, platform, author_handle, text, canonical_url 
        FROM 'data/normalized/artifacts.parquet' 
        WHERE ({cond}) AND (run_id ILIKE '%education%' OR run_id ILIKE '%kcps%' OR run_id ILIKE '%kckps%')
        LIMIT 4
    """).fetchall()
    for aid, p, author, text, url in rows:
        cleaned = ' '.join(text.split())[:280]
        print(f"  * [{aid[:8]}] [{p}] @{author}:")
        print(f"    \"{cleaned}\"")
        print(f"    -> {url}")
    print()
