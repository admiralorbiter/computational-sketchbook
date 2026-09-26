"""
Harvest Grandview C-4 School District Board Briefs (Category 5936).
Downloads articles, metadata, and full text, saving them into the raw data repository.
"""

import os
import re
import json
import time
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://www.grandviewc4.net"
CATEGORY_URL = f"{BASE_URL}/apps/news/category/5936"
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "districts/grandview-c4/governance/board_briefs")
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data/raw/grandview-c4/governance/board_briefs")
METADATA_OUT = os.path.join(PROJECT_ROOT, "districts/grandview-c4/governance/board_briefs_index.json")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def fetch_url(url):
    """Fetch URL using curl with browser headers to avoid Cloudflare/WAF 403."""
    cmd = [
        "curl.exe", "-s", "-L",
        "-A", USER_AGENT,
        url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.stdout

def get_articles_from_page(html):
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    
    # Edlio category layout
    items = soup.find_all("div", class_="news-item-link-container")
    for item in items:
        a_tag = item.find("a", class_="news-item-link")
        if not a_tag:
            continue
        href = a_tag.get("href", "")
        # Find header / title
        header_tag = item.find_next(["h2", "h3"], class_="item-name")
        title = header_tag.get_text(strip=True) if header_tag else ""
        
        # Check date or excerpt if present
        date_tag = item.find_next("span", class_="news-item-date")
        date_str = date_tag.get_text(strip=True) if date_tag else ""
        
        m = re.search(r'/article/(\d+)', href)
        article_id = m.group(1) if m else ""
        
        articles.append({
            "article_id": article_id,
            "title": title,
            "date_display": date_str,
            "url": BASE_URL + href if href.startswith("/") else href
        })
    return articles, bool(soup.find("li", class_="next"))

def harvest_all_briefs(max_pages=20):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    
    all_articles = []
    seen_ids = set()
    
    print(f"[*] Starting Board Briefs harvest from {CATEGORY_URL}")
    for page_idx in range(1, max_pages + 1):
        url = f"{CATEGORY_URL}?pageIndex={page_idx}" if page_idx > 1 else CATEGORY_URL
        print(f"[*] Fetching category page {page_idx}: {url}")
        html = fetch_url(url)
        if not html or "404 - Page Not Found" in html or "Forbidden" in html:
            print(f"[!] Reached end or error at page {page_idx}")
            break
            
        articles, has_next = get_articles_from_page(html)
        if not articles:
            print(f"[*] No articles found on page {page_idx}. Stopping pagination.")
            break
            
        new_count = 0
        for art in articles:
            if art["article_id"] and art["article_id"] not in seen_ids:
                seen_ids.add(art["article_id"])
                all_articles.append(art)
                new_count += 1
                
        print(f"[*] Page {page_idx}: Found {len(articles)} items ({new_count} new). Has next: {has_next}")
        if not has_next:
            break
        time.sleep(1)
        
    print(f"[*] Total unique board brief items discovered: {len(all_articles)}")
    
    # Now harvest article detail
    detailed_records = []
    for idx, art in enumerate(all_articles, 1):
        print(f"[{idx}/{len(all_articles)}] Fetching article {art['article_id']}: {art['title']}")
        art_html = fetch_url(art["url"])
        
        # Save raw HTML
        raw_filename = f"brief_{art['article_id']}.html"
        with open(os.path.join(DATA_RAW_DIR, raw_filename), "w", encoding="utf-8") as f:
            f.write(art_html)
            
        soup = BeautifulSoup(art_html, "html.parser")
        main_content = soup.find("div", id="content_main") or soup.find("article") or soup.find("main")
        body_text = main_content.get_text("\n", strip=True) if main_content else ""
        
        # Parse attachments / PDF links
        attachments = []
        if main_content:
            for a in main_content.find_all("a", href=True):
                href = a["href"]
                if href.endswith(".pdf") or "files.edl.io" in href or "drive.google.com" in href:
                    attachments.append({
                        "text": a.get_text(strip=True),
                        "href": href
                    })
                    
        record = {
            "article_id": art["article_id"],
            "title": art["title"],
            "url": art["url"],
            "date_display": art["date_display"],
            "raw_file": f"data/raw/grandview-c4/governance/board_briefs/{raw_filename}",
            "text_length": len(body_text),
            "attachments": attachments,
            "text_sample": body_text[:400]
        }
        detailed_records.append(record)
        time.sleep(0.5)
        
    with open(METADATA_OUT, "w", encoding="utf-8") as f:
        json.dump(detailed_records, f, indent=2)
        
    print(f"[+] Harvest complete! Metadata written to {METADATA_OUT}")
    return detailed_records

if __name__ == "__main__":
    harvest_all_briefs()
