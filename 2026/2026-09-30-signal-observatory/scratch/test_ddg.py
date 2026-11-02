import sys
from ddgs import DDGS
from observatory.store.corpus import CorpusStore
from observatory.models import Artifact, Platform, ContentType, DiscoveryMethod

sys.stdout.reconfigure(encoding='utf-8')
corpus = CorpusStore()
RUN_ID = "run_2026-10-kumed-observatory"

queries = [
    '"KU Med" reddit nursing working',
    '"KU Med" parking employees shuttle reddit',
    '"KU Medical Center" research "Glassdoor"',
    '"KUMC" vs "Lawrence" University of Kansas reddit',
    'University of Kansas "Douglas Girod" "no confidence" faculty',
    'Liberty Hospital "University of Kansas Health System" Andrew Bailey controversy'
]

artifacts = []
with DDGS() as ddgs:
    for q in queries:
        print(f"Searching: {q}...")
        try:
            results = list(ddgs.text(q, max_results=8))
            print(f"  -> Found {len(results)} items.")
            for r in results:
                url = r.get("href", "")
                title = r.get("title", "")
                body = r.get("body", "")
                full_text = f"{title}\n\n{body}"
                plat = Platform.REDDIT if "reddit.com" in url else Platform.REVIEWS if ("indeed.com" in url or "glassdoor.com" in url) else Platform.WEB
                art = Artifact(
                    native_id=url,
                    platform=plat,
                    content_type=ContentType.POST,
                    author_handle="community_voice",
                    published_at="2026-10-01T12:00:00Z",
                    text=full_text,
                    canonical_url=url,
                    discovery_method=DiscoveryMethod.SEARCH,
                    run_id=RUN_ID,
                )
                artifacts.append(art)
                print(f"     [{plat}] {title[:60]}")
        except Exception as e:
            print(f"  Error: {e}")

if artifacts:
    saved = corpus.store_artifacts(artifacts)
    print(f"\nSuccessfully stored {saved} real community & review artifacts in parquet!")
