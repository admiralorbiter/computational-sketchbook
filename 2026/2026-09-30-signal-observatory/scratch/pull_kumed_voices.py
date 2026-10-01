import asyncio
import sys
import logging
from ddgs import DDGS
from observatory.collectors.youtube import YouTubeCollector
from observatory.collectors.reddit import RedditCollector
from observatory.collectors.footage import CitizenFootageCollector
from observatory.store.corpus import CorpusStore
from observatory.models import Artifact, Platform, ContentType, DiscoveryMethod

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)

corpus = CorpusStore()

RUN_ID = "run_2026-10-kumed-observatory"

async def pull_kumed():
    print("=== HARVESTING KUMED, UKHS, AND LAWRENCE-KUMC ARTIFACTS ===")
    
    # 1. REDDIT SEARCHES (via DDGS to avoid old.reddit rate limits and get specific threads)
    print("\n--- STEP 1: Targeted Reddit Searches ---")
    reddit_queries = [
        "site:reddit.com/r/kansascity 'KU Med' OR 'KUMC'",
        "site:reddit.com/r/lawrence 'KU Med' OR 'KUMC'",
        "site:reddit.com/r/ku 'KUMC' OR 'KU Med' OR 'Girod'",
        "site:reddit.com 'University of Kansas Health System' nurse OR nursing OR pay",
        "site:reddit.com 'KUMC' postdoc OR 'graduate studies' OR researcher",
        "site:reddit.com 'KU Med' parking shuttle",
        "site:reddit.com 'KU Med' toxic OR admin OR management",
        "site:reddit.com 'United Academics of KU' Girod OR union"
    ]
    
    reddit_artifacts = []
    with DDGS() as ddgs:
        for q in reddit_queries:
            print(f"  Searching Reddit: {q}...")
            try:
                results = list(ddgs.text(q, max_results=10))
                for r in results:
                    url = r.get("href", "")
                    title = r.get("title", "")
                    body = r.get("body", "")
                    full_text = f"{title}\n\n{body}"
                    art = Artifact(
                        native_id=url,
                        platform=Platform.REDDIT,
                        content_type=ContentType.POST,
                        author_handle="reddit_user",
                        published_at="2026-10-01T12:00:00Z",
                        text=full_text,
                        canonical_url=url,
                        discovery_method=DiscoveryMethod.SEARCH,
                        run_id=RUN_ID,
                    )
                    reddit_artifacts.append(art)
            except Exception as e:
                print(f"    Error: {e}")
                
    if reddit_artifacts:
        saved = corpus.store_artifacts(reddit_artifacts)
        print(f"  -> Saved {saved} Reddit artifacts.")

    # 2. YOUTUBE VIDEOS & COMMENTS
    print("\n--- STEP 2: YouTube Search and Comments ---")
    yt = YouTubeCollector()
    yt_queries = [
        "University of Kansas Health System",
        "KU Medical Center research",
        "Chancellor Douglas Girod KU",
        "Liberty Hospital University of Kansas Health System",
        "KU Cancer Center NCI comprehensive"
    ]
    found_videos = []
    for yq in yt_queries:
        print(f"  Searching YouTube: {yq}...")
        try:
            arts, _, _ = await yt.search(yq, limit=5)
            for a in arts:
                if a.native_id not in [v['id'] for v in found_videos]:
                    found_videos.append({'id': a.native_id, 'title': a.text[:60]})
        except Exception as e:
            print(f"    Error: {e}")

    print(f"  Found {len(found_videos)} YouTube videos. Fetching comments...")
    total_comments = 0
    for v in found_videos[:8]:
        vid = v['id']
        title = v['title']
        print(f"    Fetching comments for {title} ({vid})...")
        try:
            comments, raw = await yt.fetch_comments(vid, max_comments=25)
            if comments:
                for c in comments:
                    c.run_id = RUN_ID
                corpus.store_raw(raw, platform="youtube", query_id=f"kumed_{vid}")
                saved = corpus.store_artifacts(comments)
                total_comments += saved
        except Exception as e:
            print(f"    Error: {e}")
    print(f"  -> Saved {total_comments} YouTube comments.")

    # 3. META / CITIZEN / REVIEWS
    print("\n--- STEP 3: Facebook, Reviews, and Local Discourse ---")
    cf = CitizenFootageCollector()
    meta_queries = [
        "site:facebook.com 'The University of Kansas Health System'",
        "site:facebook.com 'KU Medical Center'",
        "site:facebook.com 'United Academics of KU'",
        "site:facebook.com 'Liberty Hospital' 'University of Kansas'",
        "site:indeed.com/cmp 'University-of-Kansas-Medical-Center' reviews",
        "site:glassdoor.com/Reviews 'University-of-Kansas-Medical-Center-Reviews'"
    ]
    meta_artifacts = []
    with DDGS() as ddgs:
        for mq in meta_queries:
            print(f"  Searching: {mq}...")
            try:
                results = list(ddgs.text(mq, max_results=8))
                for r in results:
                    url = r.get("href", "")
                    title = r.get("title", "")
                    body = r.get("body", "")
                    full_text = f"{title}\n\n{body}"
                    plat = Platform.FACEBOOK if "facebook.com" in url else Platform.REVIEWS if "indeed.com" in url or "glassdoor.com" in url else Platform.WEB
                    art = Artifact(
                        native_id=url,
                        platform=plat,
                        content_type=ContentType.POST,
                        author_handle="patron_or_worker",
                        published_at="2026-10-01T12:00:00Z",
                        text=full_text,
                        canonical_url=url,
                        discovery_method=DiscoveryMethod.SEARCH,
                        run_id=RUN_ID,
                    )
                    meta_artifacts.append(art)
            except Exception as e:
                print(f"    Error: {e}")

    if meta_artifacts:
        saved = corpus.store_artifacts(meta_artifacts)
        print(f"  -> Saved {saved} Meta / Review artifacts.")

    print("\n=== HARVEST COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(pull_kumed())
