import os, sqlite3, shutil, time

DB_URL = os.environ.get("DATABASE_URL", "sqlite:///var/bonzibuddy.db")
db_path = DB_URL.replace("sqlite:///", "", 1)
os.makedirs("backups", exist_ok=True)
ts = time.strftime("%Y%m%d-%H%M%S")
dest = f"backups/bonzibuddy-{ts}.db"

# Use SQLite backup API
src_conn = sqlite3.connect(db_path)
dst_conn = sqlite3.connect(dest)
with dst_conn:
    src_conn.backup(dst_conn)
dst_conn.close()
src_conn.close()
print(dest)
