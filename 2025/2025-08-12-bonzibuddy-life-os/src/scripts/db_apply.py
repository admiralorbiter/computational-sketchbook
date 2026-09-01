import os, glob, sqlite3, sys, pathlib

DB_URL = os.environ.get("DATABASE_URL", "sqlite:///var/bonzibuddy.db")
assert DB_URL.startswith("sqlite:///"), "Only sqlite URLs are supported in v0"
db_path = DB_URL.replace("sqlite:///", "", 1)

os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# Ensure schema_version exists
cur.execute("""
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
)
""")
conn.commit()

cur.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version")
current = cur.fetchone()[0]

migrations = sorted(glob.glob("migrations/*.sql"))
applied_any = False
for path in migrations:
    # filenames like 0001_desc.sql
    try:
        ver = int(os.path.basename(path).split("_")[0])
    except Exception:
        print(f"Skipping {path}: cannot parse version")
        continue
    if ver <= current:
        continue
    print(f"Applying {path} ...")
    sql = pathlib.Path(path).read_text(encoding="utf-8")
    try:
        conn.executescript(sql)
        # if migration didn't insert into schema_version, insert now
        cur.execute("INSERT OR IGNORE INTO schema_version(version) VALUES (?)", (ver,))
        conn.commit()
        applied_any = True
    except Exception as e:
        conn.rollback()
        print(f"ERROR applying {path}: {e}")
        sys.exit(1)

if not applied_any:
    print(f"No migrations to apply (current={current}).")
else:
    print("Migrations applied successfully.")
conn.close()
