import duckdb
import json
from pathlib import Path

con = duckdb.connect()

print("=== 1. DISAPPEARED STORY DETECTOR QUERY ===")
# Topics that had high grassroots emotion/friction but little or no institutional coverage
disappeared_query = """
SELECT platform, author_handle, published_at, canonical_url, text
FROM 'data/normalized/artifacts.parquet'
WHERE (text ILIKE '%farewell%' OR text ILIKE '%strawberry hill%' OR text ILIKE '%subtropolis%' OR text ILIKE '%dollar store%' OR text ILIKE '%surcharge%')
ORDER BY published_at DESC NULLS LAST
LIMIT 30;
"""
res = con.execute(disappeared_query).fetchall()
print(f"Found {len(res)} grassroots artifacts for candidates of media-missed stories.")

print("\n=== 2. CROSS-PLATFORM LENS ON ICE RAIDS ===")
ice_query = """
SELECT platform, COUNT(*) as cnt, 
       SUM(CASE WHEN engagement_likes IS NOT NULL THEN engagement_likes ELSE 0 END) as total_likes,
       SUM(CASE WHEN engagement_views IS NOT NULL THEN engagement_views ELSE 0 END) as total_views
FROM 'data/normalized/artifacts.parquet'
WHERE text ILIKE '%ice%' OR text ILIKE '%dodge city%' OR text ILIKE '%garden city%' OR text ILIKE '%redadas%'
GROUP BY platform
ORDER BY cnt DESC;
"""
for row in con.execute(ice_query).fetchall():
    print(f"Platform: {row[0]} | Count: {row[1]} | Likes: {row[2]} | Views: {row[3]}")

# Sample top quotes from each platform for ICE
print("\n--- Cross-platform quotes for ICE ---")
for plat in ['reddit', 'facebook', 'tiktok', 'youtube']:
    sample = con.execute(f"""
        SELECT author_handle, canonical_url, text 
        FROM 'data/normalized/artifacts.parquet'
        WHERE (text ILIKE '%ice%' OR text ILIKE '%dodge city%' OR text ILIKE '%redadas%')
          AND platform = '{plat}'
        LIMIT 2;
    """).fetchall()
    print(f"\n[{plat.upper()}]")
    for a, u, t in sample:
        snippet = (t or '').replace('\n', ' ')[:150]
        print(f"  @{a}: {snippet}... ({u})")

print("\n=== 3. REPUTATION ARC FORENSICS ON WESTPORT ===")
westport_query = """
SELECT published_at, platform, author_handle, text, canonical_url
FROM 'data/normalized/artifacts.parquet'
WHERE text ILIKE '%westport%'
ORDER BY published_at ASC NULLS LAST;
"""
wp_rows = con.execute(westport_query).fetchall()
print(f"Total Westport artifacts: {len(wp_rows)}")
for d, p, a, t, u in wp_rows[:5]:
    snippet = (t or '').replace('\n', ' ')[:120]
    print(f"  [{d}] ({p}) @{a}: {snippet}...")
