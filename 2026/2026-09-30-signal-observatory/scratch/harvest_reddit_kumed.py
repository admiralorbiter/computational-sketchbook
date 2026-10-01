import asyncio
import sys
import httpx
from bs4 import BeautifulSoup
from observatory.store.corpus import CorpusStore
from observatory.models import Artifact, Platform, ContentType, DiscoveryMethod

sys.stdout.reconfigure(encoding='utf-8')
corpus = CorpusStore()

RUN_ID = "run_2026-10-kumed-observatory"

# Specific known Reddit URLs and search targets for KU Med / KUMC / UKHS / Lawrence
REDDIT_URLS = [
    # Working at KU Med / Nursing / Staffing
    "https://old.reddit.com/r/nursing/comments/16lflx8/the_university_of_kansas_health_system/",
    "https://old.reddit.com/r/kansascity/comments/16g46b3/working_at_ku_med/",
    "https://old.reddit.com/r/kansascity/comments/1b3df6z/nursing_at_ku_med_vs_st_lukes/",
    "https://old.reddit.com/r/kansascity/comments/17qff44/ku_med_parking_situation/",
    "https://old.reddit.com/r/kansascity/comments/16u1p2e/anyone_work_at_ku_med_in_research/",
    "https://old.reddit.com/r/lawrence/comments/1beeaqf/ku_faculty_senate_straw_poll_no_confidence_in/",
    "https://old.reddit.com/r/lawrence/comments/17796k0/ku_gateway_district_stadium_renovation_vs_faculty/",
    "https://old.reddit.com/r/kansascity/comments/1crk5a7/liberty_hospital_ku_health_system_merger/"
]

async def harvest_reddit_threads():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    artifacts = []
    async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
        for url in REDDIT_URLS:
            print(f"Fetching: {url}...")
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    title = soup.find('title').text if soup.find('title') else "Reddit Discussion"
                    
                    # Get main post
                    post_body = ""
                    entry = soup.find('div', class_='entry')
                    if entry:
                        md = entry.find('div', class_='md')
                        if md:
                            post_body = md.get_text(separator=' ').strip()
                    
                    # Get top comments
                    comments = []
                    for c in soup.find_all('div', class_='comment')[:10]:
                        author_tag = c.find('a', class_='author')
                        author = author_tag.text if author_tag else "anonymous"
                        cmd = c.find('div', class_='md')
                        if cmd:
                            comment_text = cmd.get_text(separator=' ').strip()
                            comments.append(f"[@{author}]: {comment_text}")
                    
                    full_content = f"TITLE: {title}\n\nPOST:\n{post_body}\n\nCOMMENTS:\n" + "\n---\n".join(comments)
                    
                    art = Artifact(
                        native_id=url,
                        platform=Platform.REDDIT,
                        content_type=ContentType.POST,
                        author_handle="reddit_community",
                        published_at="2026-10-01T12:00:00Z",
                        text=full_content,
                        canonical_url=url,
                        discovery_method=DiscoveryMethod.SEARCH,
                        run_id=RUN_ID,
                    )
                    artifacts.append(art)
                    print(f"  -> Successfully parsed thread with {len(comments)} comments.")
                else:
                    print(f"  -> Failed with status {resp.status_code}")
            except Exception as e:
                print(f"  -> Error fetching {url}: {e}")
                
    if artifacts:
        saved = corpus.store_artifacts(artifacts)
        print(f"\nSuccessfully stored {saved} in-depth Reddit discussion threads!")

if __name__ == "__main__":
    asyncio.run(harvest_reddit_threads())
