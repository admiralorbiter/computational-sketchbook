import sys
sys.stdout.reconfigure(encoding="utf-8")
import duckdb
from collections import defaultdict

con = duckdb.connect()

print("=" * 60)
print("EXPERIMENT 1: DISAPPEARED STORY DETECTOR")
print("=" * 60)

# Check coverage ratio: mainstream/broadcast vs citizen/review/reddit
queries = [
    ("West Bottoms DIY & Warehouse Scene", "(text ILIKE '%west bottoms%' OR text ILIKE '%farewell%' OR text ILIKE '%nomada%')"),
    ("Strawberry Hill Gentrification & Tax Strain", "(text ILIKE '%strawberry hill%' OR text ILIKE '%gentrif%')"),
    ("KCPS / KCKPS Teacher Staffing Whisper Network", "(text ILIKE '%teacher%' OR text ILIKE '%burnout%' OR text ILIKE '%resignation%' OR text ILIKE '%staffing%')"),
    ("Restaurant Surcharges & Sneak Fees", "(text ILIKE '%surcharge%' OR text ILIKE '%service fee%' OR text ILIKE '%went downhill%')"),
    ("Dollar Store Armed Robbery & Worker Safety", "(text ILIKE '%dollar general%' OR text ILIKE '%dollar tree%' OR text ILIKE '%robbery%')")
]

for label, cond in queries:
    stats = con.execute(f"""
        SELECT 
            SUM(CASE WHEN platform IN ('reddit', 'tiktok', 'reviews', 'facebook') THEN 1 ELSE 0 END) as grassroots_count,
            SUM(CASE WHEN platform IN ('youtube', 'web') AND (author_handle ILIKE '%kmbc%' OR author_handle ILIKE '%kshb%' OR author_handle ILIKE '%kctv%' OR author_handle ILIKE '%fox4%' OR author_handle ILIKE '%star%') THEN 1 ELSE 0 END) as mainstream_count,
            COUNT(*) as total
        FROM 'data/normalized/artifacts.parquet'
        WHERE {cond}
    """).fetchone()
    grassroots = stats[0] or 0
    mainstream = stats[1] or 0
    total = stats[2] or 0
    ratio = (grassroots / (mainstream + 0.1))
    print(f"\nTopic: {label}")
    print(f"  Grassroots / Citizen Artifacts: {grassroots}")
    print(f"  Mainstream News Coverage: {mainstream}")
    print(f"  Disappearance Ratio (Grassroots-to-Media): {ratio:.1f}x")

print("\n" + "=" * 60)
print("EXPERIMENT 2: CROSS-PLATFORM LENS EFFECT (ICE CRISIS)")
print("=" * 60)

# Break down platforms for the ICE raids and protest run
ice_stats = con.execute("""
    SELECT platform, COUNT(*) as cnt,
           SUM(CASE WHEN engagement_likes IS NOT NULL THEN engagement_likes ELSE 0 END) as likes,
           SUM(CASE WHEN engagement_views IS NOT NULL THEN engagement_views ELSE 0 END) as views
    FROM 'data/normalized/artifacts.parquet'
    WHERE run_id LIKE '%ice%' OR text ILIKE '%dodge city%' OR text ILIKE '%garden city%' OR text ILIKE '%redadas%'
    GROUP BY platform
""").fetchall()

for plat, c, l, v in ice_stats:
    print(f"Platform: {plat:10} | Artifacts: {c:5} | Likes: {l:8} | Views: {v:10}")

print("\n" + "=" * 60)
print("EXPERIMENT 3: REPUTATION ARC FORENSICS (WESTPORT)")
print("=" * 60)

wp_timeline = con.execute("""
    SELECT strftime(TRY_CAST(published_at AS TIMESTAMP), '%Y-%m') as ym, platform, COUNT(*) as cnt
    FROM 'data/normalized/artifacts.parquet'
    WHERE text ILIKE '%westport%'
    GROUP BY ym, platform
    ORDER BY ym ASC NULLS LAST
""").fetchall()

timeline_map = defaultdict(lambda: defaultdict(int))
for ym, plat, cnt in wp_timeline:
    timeline_map[ym or "Undated"][plat] += cnt

print(f"{'Year-Month':12} | {'Reddit':6} | {'TikTok':6} | {'Facebook':8} | {'YouTube':8} | {'Reviews':8} | {'Total':6}")
print("-" * 65)
for ym in sorted(timeline_map.keys()):
    r = timeline_map[ym]['reddit']
    t = timeline_map[ym]['tiktok']
    f = timeline_map[ym]['facebook']
    y = timeline_map[ym]['youtube']
    v = timeline_map[ym]['reviews']
    tot = r + t + f + y + v
    print(f"{ym:12} | {r:6} | {t:6} | {f:8} | {y:8} | {v:8} | {tot:6}")
