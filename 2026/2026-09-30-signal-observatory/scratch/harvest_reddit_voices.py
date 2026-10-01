import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

print("=== DEEP EXTRACTION OF FIRSTHAND REDDIT TEACHER & PARENT VOICES ===\n")

rows = con.execute('''
    SELECT author_handle, text, canonical_url 
    FROM 'data/normalized/artifacts.parquet' 
    WHERE platform = 'reddit'
      AND (
          text ILIKE '%teach%' OR text ILIKE '%parent%' OR text ILIKE '%student%' 
          OR text ILIKE '%admin%' OR text ILIKE '%district%' OR text ILIKE '%4 day%'
          OR text ILIKE '%salary%' OR text ILIKE '%board%'
      )
      AND (
          text ILIKE '%kansas city%' OR text ILIKE '%kcps%' OR text ILIKE '%independence%'
          OR text ILIKE '%shawnee%' OR text ILIKE '%olathe%' OR text ILIKE '%lee''s summit%'
          OR text ILIKE '%blue valley%' OR text ILIKE '%north kansas city%' OR text ILIKE '%hickman%'
          OR text ILIKE '%grandview%' OR text ILIKE '%grain valley%'
      )
    LIMIT 15
''').fetchall()

print(f"Total matching firsthand Reddit threads: {len(rows)}\n")

for i, (author, text, url) in enumerate(rows, 1):
    print(f"[{i}] Author: @{author}")
    print(f"    URL: {url}")
    print("    EXCERPT:")
    print("    " + "\n    ".join(text.split("\n")[:8]))
    print("-" * 70)
