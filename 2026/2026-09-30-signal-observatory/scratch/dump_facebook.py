import duckdb
import sys

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

print("=== ALL FACEBOOK ARTIFACTS IN OBSERVATORY ===")
rows = con.execute("""
    SELECT author_handle, text, canonical_url
    FROM 'data/normalized/artifacts.parquet'
    WHERE platform = 'facebook'
""").fetchall()

print(f"Total: {len(rows)}")
for a, t, u in rows:
    cleaned = ' '.join(t.split())
    print(f"@{a}:\n  \"{cleaned[:300]}\"\n  Url: {u}\n")
