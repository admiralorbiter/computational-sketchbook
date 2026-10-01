import duckdb

con = duckdb.connect()

runs = con.execute("SELECT DISTINCT run_id, count(1) FROM 'data/normalized/artifacts.parquet' GROUP BY run_id").fetchall()
print("Available Runs in Corpus:")
for r, c in runs:
    print(f"  {r}: {c} artifacts")

print("\n=== ICE RAID RUN BREAKDOWN ===")
ice_runs = [r for r, _ in runs if 'ice' in (r or '').lower()]
for r in ice_runs:
    stats = con.execute(f"""
        SELECT platform, count(1) 
        FROM 'data/normalized/artifacts.parquet' 
        WHERE run_id = '{r}' 
        GROUP BY platform
    """).fetchall()
    print(f"\nRun: {r}")
    for p, c in stats:
        print(f"  Platform: {p} -> {c} items")

print("\n=== SAMPLE ICE CITIZEN / COMMUNITY ARTIFACTS ===")
ice_sample = con.execute("""
    SELECT platform, author_handle, published_at, text, canonical_url
    FROM 'data/normalized/artifacts.parquet'
    WHERE run_id LIKE '%ice%'
    ORDER BY platform, published_at DESC NULLS LAST
""").fetchall()

current_plat = None
for p, a, dt, t, u in ice_sample:
    if p != current_plat:
        current_plat = p
        print(f"\n--- Platform: {p.upper()} ---")
    snippet = (t or '').replace('\n', ' ')[:140]
    print(f"  [{dt}] @{a}: {snippet}... ({u})")
