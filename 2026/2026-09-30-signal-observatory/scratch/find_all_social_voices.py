import duckdb
import sys

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

print("=== SEARCHING ALL NON-REDDIT/NON-NEWS ARTIFACTS FOR KC EDUCATION VOICES ===\n")

platforms = ['youtube', 'facebook', 'tiktok', 'reviews']

for plat in platforms:
    print(f"--- PLATFORM: {plat.upper()} ---")
    query = f"""
        SELECT author_handle, published_at, text, canonical_url
        FROM 'data/normalized/artifacts.parquet'
        WHERE platform = '{plat}'
          AND (
            text ILIKE '%teacher%' OR text ILIKE '%student%' OR text ILIKE '%school%' 
            OR text ILIKE '%district%' OR text ILIKE '%parent%' OR text ILIKE '%substitute%'
            OR text ILIKE '%olathe%' OR text ILIKE '%blue valley%' OR text ILIKE '%shawnee mission%'
            OR text ILIKE '%kcps%' OR text ILIKE '%independence%' OR text ILIKE '%hickman%'
            OR text ILIKE '%grandview%' OR text ILIKE '%north kansas city%' OR text ILIKE '%kck%'
          )
        LIMIT 25
    """
    rows = con.execute(query).fetchall()
    print(f"Found {len(rows)} matching artifacts on {plat}:")
    for a, dt, t, u in rows:
        cleaned = ' '.join(t.split())
        print(f"  * @{a} ({dt}):\n    \"{cleaned[:250]}...\"\n    Url: {u}\n")
