import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

rows = con.execute('''
    SELECT artifact_id, platform, author_handle, published_at, text, canonical_url 
    FROM 'data/normalized/artifacts.parquet' 
    WHERE (published_at >= '2026-08-01' OR text ILIKE '%2026%')
      AND (run_id ILIKE '%education%' OR run_id ILIKE '%kcps%' OR run_id ILIKE '%kckps%')
    ORDER BY published_at DESC
    LIMIT 25
''').fetchall()

print(f"Total recent 2026 items in corpus: {len(rows)}")
for aid, p, a, dt, t, u in rows:
    cleaned = ' '.join(t.split())[:200]
    print(f"[{aid[:8]}] [{dt}] [{p}] @{a}: \"{cleaned}\"")
    print(f"       Link: {u}")
