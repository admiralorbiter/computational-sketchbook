import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

r = requests.get('https://www.snapchat.com/spotlight', headers=headers, timeout=10)
match = re.search(r'<script[^>]*>(\{"props":\{.*?)</script>', r.text, re.DOTALL)

if match:
    data = json.loads(match.group(1))
    page_props = data.get("props", {}).get("pageProps", {})
    spotlight_feed = page_props.get("spotlightFeed", {})
    print("spotlightFeed keys:", list(spotlight_feed.keys()))
    
    # Check if there are snap items / stories
    feed_items = []
    for k, v in spotlight_feed.items():
        if isinstance(v, list):
            print(f"  spotlightFeed[{k}] (list of {len(v)} items)")
            feed_items.extend(v)
        elif isinstance(v, dict):
            print(f"  spotlightFeed[{k}] (dict keys: {list(v.keys())})")
            
    video_meta = page_props.get("videoMetadata", {})
    print("videoMetadata keys:", list(video_meta.keys()) if isinstance(video_meta, dict) else type(video_meta))
    
    # Print sample snap item
    if feed_items:
        first = feed_items[0]
        print("\nFirst feed item keys:", list(first.keys()) if isinstance(first, dict) else type(first))
        print("Sample item preview:", json.dumps(first, indent=2)[:500])
