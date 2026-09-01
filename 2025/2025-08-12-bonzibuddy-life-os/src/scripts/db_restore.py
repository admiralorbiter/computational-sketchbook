import os, sqlite3, sys, shutil

if len(sys.argv) < 3 or sys.argv[1] != "--from":
    print("Usage: python scripts/db_restore.py --from backups/<file>")
    sys.exit(1)
src = sys.argv[2]
DB_URL = os.environ.get("DATABASE_URL", "sqlite:///var/bonzibuddy.db")
dst = DB_URL.replace("sqlite:///", "", 1)
os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.copy2(src, dst)
print(f"Restored {src} -> {dst}")
