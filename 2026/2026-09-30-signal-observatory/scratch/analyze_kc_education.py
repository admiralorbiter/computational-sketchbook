import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

districts = {
    'Urban Core (KCPS, KCKPS, Hickman Mills, Center, Grandview)': [
        'KCPS', 'Kansas City Public Schools', 'KCKPS', 'Kansas City Kansas',
        'Hickman Mills', 'Center School', 'Grandview', 'tax abatement', 'charter'
    ],
    'Suburban Johnson County (SMSD, Blue Valley, Olathe)': [
        'Shawnee Mission', 'SMSD', 'Blue Valley', 'Olathe', 'Johnson County'
    ],
    'Suburban Northland & Eastern Jackson (NKC, Lee\'s Summit, Independence, Park Hill, Liberty)': [
        'North Kansas City', 'NKC', 'Lee\'s Summit', 'Independence', 'Park Hill', 'Liberty', '4-day'
    ],
    'Exurban / Rural Outer Ring (Grain Valley, Smithville, Kearney, Belton, Gardner Edgerton)': [
        'Grain Valley', 'Smithville', 'Kearney', 'Belton', 'Gardner Edgerton', 'book ban'
    ]
}

print('=== KANSAS CITY REGIONAL EDUCATION AUDIT (5,054 Corpus Artifacts) ===\n')

for tier_name, terms in districts.items():
    print(f'************************************************************')
    print(f'TIER: {tier_name}')
    print(f'************************************************************')
    
    # Build OR clause
    escaped_terms = [t.replace("'", "''") for t in terms]
    where_clause = ' OR '.join([f"text ILIKE '%{t}%'" for t in escaped_terms])
    query = f"""
        SELECT platform, author_handle, text, canonical_url 
        FROM 'data/normalized/artifacts.parquet' 
        WHERE ({where_clause})
        ORDER BY published_at DESC
        LIMIT 6
    """
    rows = con.execute(query).fetchall()
    print(f'Sample findings ({len(rows)} displayed):')
    for p, author, text, url in rows:
        cleaned = ' '.join(text.split())[:200]
        print(f"  [{p}] @{author}: {cleaned}... ({url})")
    print()
