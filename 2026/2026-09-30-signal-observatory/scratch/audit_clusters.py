import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

target_districts = [
    ("KCPS (Urban Core MO)", ["KCPS", "Lincoln Prep", "tax abatement"]),
    ("KCKPS (Urban Core KS)", ["KCKPS", "Sumner", "Wyandotte"]),
    ("Shawnee Mission (Suburban KS)", ["Shawnee Mission", "SMSD"]),
    ("Blue Valley & Olathe (Affluent Suburb KS)", ["Blue Valley", "Olathe"]),
    ("North Kansas City & Park Hill (Northland MO)", ["North Kansas City", "NKC", "Park Hill"]),
    ("Lee's Summit R-7 (Suburban MO)", ["Lee's Summit", "LSR7"]),
    ("Independence ISD (4-Day Week / East Jackson)", ["Independence", "4-day", "four-day"]),
    ("South Jackson: Hickman Mills & Grandview", ["Hickman Mills", "Grandview"]),
    ("Exurban / Rural: Grain Valley, Kearney, Smithville", ["Grain Valley", "Kearney", "Smithville"])
]

for label, terms in target_districts:
    print(f"==================================================")
    print(f"DISTRICT CLUSTER: {label}")
    print(f"==================================================")
    escaped = [t.replace("'", "''") for t in terms]
    where = " OR ".join([f"text ILIKE '%{t}%'" for t in escaped])
    query = f"""
        SELECT platform, author_handle, text, canonical_url
        FROM 'data/normalized/artifacts.parquet'
        WHERE ({where})
        LIMIT 4
    """
    rows = con.execute(query).fetchall()
    for p, author, text, url in rows:
        cleaned = " ".join(text.split())[:220]
        print(f"  * [{p}] @{author}: \"{cleaned}\" -> {url}")
    print()
