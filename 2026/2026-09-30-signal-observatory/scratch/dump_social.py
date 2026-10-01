import duckdb
import sys

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

rows = con.execute("""
    SELECT platform, author_handle, text, canonical_url
    FROM 'data/normalized/artifacts.parquet'
    WHERE run_id = 'run_2026-10-kc-social-voices'
""").fetchall()

print(f"Total in run_2026-10-kc-social-voices: {len(rows)}")
for p, a, t, u in rows:
    cleaned = ' '.join(t.split())
    print(f"[{p}] @{a}:\n  \"{cleaned}\"\n  Url: {u}\n")
