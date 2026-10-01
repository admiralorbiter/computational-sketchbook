import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

print("=== DEEP AUDIT OF SNAPCHAT, YOUTUBE COMMENTS, FACEBOOK, AND TIKTOK ===\n")

platforms = ['snapchat', 'facebook', 'tiktok']

for plat in platforms:
    print(f"==================================================")
    print(f"PLATFORM: {plat.upper()}")
    print(f"==================================================")
    query = f"""
        SELECT author_handle, published_at, text, canonical_url
        FROM 'data/normalized/artifacts.parquet'
        WHERE platform = '{plat}'
          AND (
              text ILIKE '%school%' OR text ILIKE '%student%' OR text ILIKE '%teacher%' 
              OR text ILIKE '%parent%' OR text ILIKE '%fight%' OR text ILIKE '%olathe%'
              OR text ILIKE '%blue valley%' OR text ILIKE '%kansas%' OR text ILIKE '%kcps%'
          )
        LIMIT 10
    """
    rows = con.execute(query).fetchall()
    print(f"Found {len(rows)} items:")
    for a, dt, t, u in rows:
        cleaned = ' '.join(t.split())[:300]
        print(f"  * @{a} ({dt}):")
        print(f"    \"{cleaned}\"")
        print(f"    -> {u}\n")

# Now print the newly harvested YouTube comments on Olathe closures and Blue Valley cuts!
print(f"==================================================")
print(f"YOUTUBE COMMENTS ON OLATHE CLOSURES & BLUE VALLEY CUTS")
print(f"==================================================")
query = """
    SELECT author_handle, published_at, text, canonical_url
    FROM 'data/normalized/artifacts.parquet'
    WHERE run_id = 'run_2026-10-kc-social-voices' AND platform = 'youtube'
    LIMIT 20
"""
rows = con.execute(query).fetchall()
print(f"Found {len(rows)} comments:")
for a, dt, t, u in rows:
    cleaned = ' '.join(t.split())
    print(f"  * @{a}: \"{cleaned}\"")
    print(f"    Link: {u}\n")
