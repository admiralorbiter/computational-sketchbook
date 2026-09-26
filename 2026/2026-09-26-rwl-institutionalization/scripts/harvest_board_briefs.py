"""
Harvest Grandview C-4 School District Board Briefs.

Edlio categoryId=5936 is not treated as a trustworthy corpus boundary.
The category currently returns ordinary district news as well as Board Briefs.
This collector discovers category articles, preserves their raw HTML, and then
validates Board Brief membership from article content before writing the corpus index.
"""

import os
import re
import json
import time
import subprocess
from bs4 import BeautifulSoup

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "https://www.grandviewc4.net"
CATEGORY_URL = f"{BASE_URL}/apps/news/category/5936"
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data/raw/grandview-c4/governance/board_briefs")
METADATA_OUT = os.path.join(PROJECT_ROOT, "districts/grandview-c4/governance/board_briefs_index.json")
REJECTED_OUT = os.path.join(PROJECT_ROOT, "districts/grandview-c4/governance/board_briefs_rejected_index.json")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

BOARD_BRIEF_DATE_PATTERNS = [
    re.compile(r"Board Briefs?\s*[-–—:]\s*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})", re.I),
    re.compile(r"Regular Open Meeting Brief\s*[-–—:]\s*([A-Z][a-z]+\s+\d{1,2},\s+\d{4})", re.I),
]

def fetch_url(url):
    cmd = ["curl.exe", "-s", "-L", "-A", USER_AGENT, url]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"curl failed ({res.returncode}) for {url}: {res.stderr[:300]}")
    return res.stdout

def get_articles_from_page(html):
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "")
        m = re.search(r"/apps/news/article/(\d+)", href)
        if not m:
            continue
        article_id = m.group(1)
        url = BASE_URL + href if href.startswith("/") else href
        articles.append({"article_id": article_id, "url": url})
    return articles

def parse_article(article_id, url, html):
    soup = BeautifulSoup(html, "html.parser")
    main_content = soup.find("div", id="content_main") or soup.find("article") or soup.find("main")
    body_text = main_content.get_text("\n", strip=True) if main_content else ""

    title = ""
    h1 = soup.find("h1")
    og = soup.find("meta", property="og:title")
    title_tag = soup.find("title")
    if h1:
        title = h1.get_text(" ", strip=True)
    elif og and og.get("content"):
        title = og["content"].strip()
    elif title_tag:
        title = title_tag.get_text(" ", strip=True)

    search_text = f"{title}\n{body_text}"
    date_display = ""
    for pat in BOARD_BRIEF_DATE_PATTERNS:
        m = pat.search(search_text)
        if m:
            date_display = m.group(1)
            break

    is_board_brief = bool(
        re.search(r"\bBoard Briefs?\b", search_text, re.I)
        and (
            re.search(r"Board Briefs?\s*[-–—:]", search_text, re.I)
            or "what took place during our board meetings" in body_text.lower()
            or "regular open meeting brief" in body_text.lower()
        )
    )

    attachments = []
    if main_content:
        for a in main_content.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf") or "files.edl.io" in href or "drive.google.com" in href:
                attachments.append({"text": a.get_text(" ", strip=True), "href": href})

    return {
        "article_id": article_id,
        "title": title,
        "url": url,
        "date_display": date_display,
        "is_board_brief": is_board_brief,
        "raw_file": f"data/raw/grandview-c4/governance/board_briefs/brief_{article_id}.html",
        "text_length": len(body_text),
        "attachments": attachments,
        "text_sample": body_text[:500],
    }

def harvest_all_briefs(max_pages=50):
    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    discovered = {}
    stale_pages = 0
    for page_idx in range(1, max_pages + 1):
        url = f"{CATEGORY_URL}?pageIndex={page_idx}" if page_idx > 1 else CATEGORY_URL
        html = fetch_url(url)
        if not html or "404 - Page Not Found" in html or "Forbidden" in html:
            break

        page_articles = get_articles_from_page(html)
        new_count = 0
        for art in page_articles:
            if art["article_id"] not in discovered:
                discovered[art["article_id"]] = art
                new_count += 1

        print(f"[*] Page {page_idx}: {len(page_articles)} candidate links, {new_count} new")
        stale_pages = stale_pages + 1 if (not page_articles or new_count == 0) else 0
        if stale_pages >= 2:
            break
        time.sleep(0.5)

    accepted, rejected = [], []
    for idx, art in enumerate(discovered.values(), 1):
        print(f"[{idx}/{len(discovered)}] Fetching article {art['article_id']}")
        art_html = fetch_url(art["url"])
        raw_filename = f"brief_{art['article_id']}.html"
        with open(os.path.join(DATA_RAW_DIR, raw_filename), "w", encoding="utf-8") as fh:
            fh.write(art_html)

        record = parse_article(art["article_id"], art["url"], art_html)
        (accepted if record["is_board_brief"] else rejected).append(record)
        time.sleep(0.25)

    accepted.sort(key=lambda r: (r["date_display"], r["article_id"]))
    with open(METADATA_OUT, "w", encoding="utf-8") as fh:
        json.dump(accepted, fh, indent=2)
    with open(REJECTED_OUT, "w", encoding="utf-8") as fh:
        json.dump(rejected, fh, indent=2)

    print(f"[+] Validated Board Briefs: {len(accepted)}")
    print(f"[+] Rejected category contaminants: {len(rejected)}")
    return accepted

if __name__ == "__main__":
    harvest_all_briefs()
