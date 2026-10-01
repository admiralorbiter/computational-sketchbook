import duckdb
import json

con = duckdb.connect("data/corpus.duckdb", read_only=True)
query = """
SELECT platform, author_handle, title, canonical_url, text
FROM artifacts
WHERE text ILIKE '%rave%' 
   OR text ILIKE '%techno%' 
   OR text ILIKE '%warehouse%'
   OR text ILIKE '%edm%'
   OR text ILIKE '%nighthawk%'
   OR text ILIKE '%nomada%'
ORDER BY published_at DESC NULLS LAST
LIMIT 20;
"""

rows = con.execute(query).fetchall()
print(f"Total matching rows: {len(rows)}")
for r in rows[:10]:
    print("---")
    print(f"Platform: {r[0]} | Author: {r[1]} | Title: {r[2]}")
    print(f"URL: {r[3]}")
    print(f"Text snippet: {(r[4] or '')[:200]}...")
