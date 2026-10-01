import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

print("=== HARVESTING FIRSTHAND VOICES: TEACHERS, PARENTS, AND STUDENTS ===\n")

voice_queries = [
    ("TEACHER VOICES (Firsthand working conditions, admin disconnect, burnout)",
     """(text ILIKE '%I am a teacher%' OR text ILIKE '%I teach%' OR text ILIKE '%my classroom%' 
         OR text ILIKE '%as a teacher%' OR text ILIKE '%my admin%' OR text ILIKE '%I resigned%'
         OR text ILIKE '%our district%' OR text ILIKE '%teaching in%')
        AND (text ILIKE '%kansas%' OR text ILIKE '%missouri%' OR text ILIKE '%kcps%' 
         OR text ILIKE '%olathe%' OR text ILIKE '%shawnee%' OR text ILIKE '%blue valley%'
         OR text ILIKE '%independence%' OR text ILIKE '%hickman%' OR text ILIKE '%school%')"""),
    
    ("PARENT VOICES (Childcare costs, school closures, safety, busing, special ed)",
     """(text ILIKE '%as a parent%' OR text ILIKE '%my kid%' OR text ILIKE '%my son%' 
         OR text ILIKE '%my daughter%' OR text ILIKE '%my children%' OR text ILIKE '%our elementary%'
         OR text ILIKE '%childcare%' OR text ILIKE '%daycare%')
        AND (text ILIKE '%kansas%' OR text ILIKE '%missouri%' OR text ILIKE '%kcps%' 
         OR text ILIKE '%olathe%' OR text ILIKE '%shawnee%' OR text ILIKE '%independence%'
         OR text ILIKE '%blue valley%' OR text ILIKE '%school%')"""),
         
    ("STUDENT VOICES (Walkouts, phone bans, safety, hallway conditions)",
     """(text ILIKE '%student%' OR text ILIKE '%walkout%' OR text ILIKE '%protest%' 
         OR text ILIKE '%high schooler%' OR text ILIKE '%in class%')
        AND (text ILIKE '%yondr%' OR text ILIKE '%cell phone%' OR text ILIKE '%gun%' 
         OR text ILIKE '%bathroom%' OR text ILIKE '%walked out%' OR text ILIKE '%protesting%')
        AND (text ILIKE '%kansas%' OR text ILIKE '%missouri%' OR text ILIKE '%kc%' OR text ILIKE '%school%')""")
]

for label, cond in voice_queries:
    print(f"********************************************************************")
    print(f"{label}")
    print(f"********************************************************************")
    query = f"""
        SELECT artifact_id, platform, author_handle, published_at, text, canonical_url
        FROM 'data/normalized/artifacts.parquet'
        WHERE {cond}
        LIMIT 6
    """
    rows = con.execute(query).fetchall()
    print(f"Found {len(rows)} matching artifacts:")
    for aid, p, author, dt, text, url in rows:
        cleaned = " ".join(text.split())[:350]
        print(f"  [{p}] @{author} ({dt}):")
        print(f"    \"{cleaned}\"")
        print(f"    -> {url}\n")
    print()
