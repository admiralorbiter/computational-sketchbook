import duckdb

con = duckdb.connect()
res = con.execute("SELECT * FROM 'data/normalized/artifacts.parquet' LIMIT 1")
columns = [desc[0] for desc in res.description]
print("Columns:", columns)

stats = con.execute("""
    SELECT platform, COUNT(*) as cnt 
    FROM 'data/normalized/artifacts.parquet' 
    GROUP BY platform 
    ORDER BY cnt DESC
""").fetchall()

print("Platform distribution:")
for p, c in stats:
    print(f"  {p}: {c}")

total = con.execute("SELECT COUNT(*) FROM 'data/normalized/artifacts.parquet'").fetchone()[0]
print(f"Total artifacts: {total}")
