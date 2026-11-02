import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

r = requests.get('https://www.snapchat.com/spotlight', headers=headers, timeout=10)
match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
if not match:
    # search for props script
    match = re.search(r'<script[^>]*>(\{"props":\{.*?)</script>', r.text, re.DOTALL)

if match:
    data = json.loads(match.group(1))
    print("Top-level keys in props:", list(data.get("props", {}).keys()))
    page_props = data.get("props", {}).get("pageProps", {})
    print("Keys in pageProps:", list(page_props.keys()))
    spotlight = page_props.get("spotlightFeed") or page_props.get("spotlight") or page_props.get("curatedFeed")
    if spotlight:
        print("Found spotlight field:", type(spotlight))
    else:
        for k, v in page_props.items():
            if isinstance(v, (dict, list)):
                print(f"  pageProps[{k}]: {type(v)}")
else:
    print("Could not find props script")
