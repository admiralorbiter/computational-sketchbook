import sys
import duckdb

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect()

categories = {
    'used_machinery_inversion': "text ILIKE '%deere%' OR text ILIKE '%used tractor%' OR (text ILIKE '%auction%' AND (text ILIKE '%tractor%' OR text ILIKE '%machinery%'))",
    'insurance_authority_cancellation': "text ILIKE '%insurance%' OR text ILIKE '%mc revoked%' OR text ILIKE '%fmcsa%'",
    'double_brokering_fraud': "text ILIKE '%double broker%' OR text ILIKE '%carrier411%' OR text ILIKE '%tql%'",
    'fertilizer_monopoly_gouging': "(text ILIKE '%anhydrous%' OR text ILIKE '%fertilizer%') AND (text ILIKE '%price%' OR text ILIKE '%gouging%' OR text ILIKE '%cost%')",
    'emissions_def_crisis': "text ILIKE '%def %' OR text ILIKE '%emissions%' OR text ILIKE '%exhaust fluid%'",
    'farmland_land_use_clash': "text ILIKE '%data center%' OR text ILIKE '%solar%' OR text ILIKE '%billionaire%' OR text ILIKE '%foreign%'"
}

for cat_name, condition in categories.items():
    print(f"=== CATEGORY: {cat_name} ===")
    query = f"""
        SELECT platform, author_handle, text, canonical_url 
        FROM 'data/normalized/artifacts.parquet' 
        WHERE (run_id LIKE '%farmers%' OR run_id LIKE '%truckers%') AND ({condition})
        LIMIT 5
    """
    rows = con.execute(query).fetchall()
    for p, author, text, url in rows:
        cleaned = ' '.join(text.split())[:200]
        print(f"  [{p}] @{author}: {cleaned}... ({url})")
    print()
