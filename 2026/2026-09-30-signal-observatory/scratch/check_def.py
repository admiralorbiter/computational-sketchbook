import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()
rows = con.execute('''
    SELECT platform, author_handle, text, canonical_url 
    FROM 'data/normalized/artifacts.parquet' 
    WHERE (run_id LIKE '%farmers%' OR run_id LIKE '%truckers%')
      AND (text ILIKE '% def %' OR text ILIKE '%diesel exhaust fluid%' OR text ILIKE '%derate%' OR text ILIKE '%tier 4%' OR text ILIKE '%dpf%')
    LIMIT 10
''').fetchall()
for p, a, t, u in rows:
    cleaned = ' '.join(t.split())[:180]
    print(f"[{p}] @{a}: {cleaned}... ({u})")
