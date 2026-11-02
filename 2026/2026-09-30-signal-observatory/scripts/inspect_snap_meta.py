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
    stories = page_props.get("spotlightFeed", {}).get("spotlightStories", [])
    print(f"Total stories returned: {len(stories)}")
    for i, s in enumerate(stories[:5]):
        meta = s.get("metadata", {})
        story = s.get("story", {})
        snaps = story.get("snapList", [])
        print(f"\n--- Snap #{i+1} ---")
        print("Metadata:", json.dumps(meta, indent=2))
        if snaps:
            print("Snap details:", json.dumps({k: v for k, v in snaps[0].items() if k != "snapUrls"}, indent=2))
            urls = snaps[0].get("snapUrls", {})
            print("Media URL present:", bool(urls.get("mediaUrl")))
            if urls.get("mediaUrl"):
                print("Media URL sample:", urls.get("mediaUrl")[:100] + "...")
