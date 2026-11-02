import asyncio
import sys
from observatory.collectors.youtube import YouTubeCollector
from observatory.collectors.snapchat import SnapchatCollector
from observatory.collectors.footage import CitizenFootageCollector
from observatory.store.corpus import CorpusStore
from observatory.models import Platform

sys.stdout.reconfigure(encoding='utf-8')

corpus = CorpusStore()

async def pull_fresh_social():
    print("=== STEP 1: HARVESTING YOUTUBE COMMENTS ON RECENT KC SCHOOL VIDEOS ===")
    yt = YouTubeCollector()
    
    # 1. Search for recent KC school videos
    search_queries = [
        "Olathe school closures elementary 2026",
        "Blue Valley school district cuts 2026",
        "Kansas school cell phone ban Yondr 2026",
        "KCPS school board tax abatement",
        "Independence school district 4 day week"
    ]
    
    found_videos = []
    for sq in search_queries:
        try:
            arts, _, _ = await yt.search(sq, limit=5)
            for a in arts:
                if a.native_id not in [v['id'] for v in found_videos]:
                    found_videos.append({'id': a.native_id, 'title': a.text[:60]})
        except Exception as e:
            print(f"Error searching YT: {e}")
            
    print(f"Found {len(found_videos)} recent YouTube video discussions to harvest comments from.")
    
    total_comments_saved = 0
    for v in found_videos[:10]:
        vid = v['id']
        title = v['title']
        print(f"  Harvesting comments from: {title} ({vid})...")
        try:
            comments, raw = await yt.fetch_comments(vid, max_comments=30)
            if comments:
                for c in comments:
                    c.run_id = "run_2026-10-kc-social-voices"
                corpus.store_raw(raw, platform="youtube", query_id=f"comments_{vid}")
                saved = corpus.store_artifacts(comments)
                total_comments_saved += saved
                print(f"    -> Stored {saved} user comments.")
        except Exception as e:
            print(f"    -> Error: {e}")
            
    print(f"Total new YouTube comments stored: {total_comments_saved}\n")

    print("=== STEP 2: HARVESTING SNAPCHAT SPOTLIGHT ON KC SCHOOLS ===")
    snap = SnapchatCollector()
    snap_queries = [
        "Olathe High School",
        "Blue Valley High",
        "Shawnee Mission school",
        "KCPS school",
        "Kansas City school fight"
    ]
    total_snaps_saved = 0
    for sq in snap_queries:
        print(f"  Searching Snapchat for: {sq}...")
        try:
            snaps, _, raw = await snap.search(sq, limit=8)
            if snaps:
                for s in snaps:
                    s.run_id = "run_2026-10-kc-social-voices"
                corpus.store_raw(raw, platform="snapchat", query_id=f"snap_{sq[:8]}")
                saved = corpus.store_artifacts(snaps)
                total_snaps_saved += saved
                print(f"    -> Stored {saved} Spotlight clips.")
        except Exception as e:
            print(f"    -> Error: {e}")
    print(f"Total new Snapchat artifacts stored: {total_snaps_saved}\n")

    print("=== STEP 3: HARVESTING FACEBOOK & INSTAGRAM PARENT/STUDENT POSTS ===")
    cf = CitizenFootageCollector()
    meta_queries = [
        "site:facebook.com Olathe school closures parents",
        "site:facebook.com Blue Valley classified staff cuts",
        "site:facebook.com Independence school district 4-day week parents",
        "site:instagram.com Shawnee Mission school walkout",
        "site:instagram.com Olathe school cell phone ban"
    ]
    total_meta_saved = 0
    for mq in meta_queries:
        print(f"  Searching Meta/Citizen for: {mq}...")
        try:
            arts, _, raw = await cf.search(mq, limit=8)
            if arts:
                for a in arts:
                    a.run_id = "run_2026-10-kc-social-voices"
                corpus.store_raw(raw, platform="citizen", query_id=f"meta_{mq[:8]}")
                saved = corpus.store_artifacts(arts)
                total_meta_saved += saved
                print(f"    -> Stored {saved} Facebook/Instagram clips.")
        except Exception as e:
            print(f"    -> Error: {e}")
    print(f"Total new Facebook/Instagram artifacts stored: {total_meta_saved}\n")

asyncio.run(pull_fresh_social())
