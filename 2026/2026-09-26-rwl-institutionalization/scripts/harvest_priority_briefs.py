import subprocess
import os
import re
from bs4 import BeautifulSoup

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_BRIEFS_DIR = os.path.join(PROJECT_ROOT, "data/raw/grandview-c4/governance/board_briefs")
os.makedirs(RAW_BRIEFS_DIR, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

BRIEFS = {
    "2024-12-19": ("2011053", "https://www.grandviewc4.net/apps/news/article/2011053"),
    "2025-01-16": ("2020964", "https://www.grandviewc4.net/apps/news/article/2020964"),
    "2025-03-20": ("2053567", "https://www.grandviewc4.net/apps/news/article/2053567"),
    "2026-04-16": ("2191177", "https://www.grandviewc4.net/apps/news/article/2191177?categoryId=5936"),
    "2026-06-18": ("2210618", "https://www.grandviewc4.net/apps/news/article/2210618?categoryId=5936"),
}

def harvest_brief(date, art_id, url):
    out_file = os.path.join(RAW_BRIEFS_DIR, f"brief_{art_id}.html")
    print(f"[*] Fetching Board Brief {date} ({art_id}) from {url}...")
    cmd = ["curl.exe", "-s", "-L", "-A", USER_AGENT, url]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    html = res.stdout
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Saved {out_file} ({len(html)} bytes)")
    return html

if __name__ == "__main__":
    for date, (art_id, url) in BRIEFS.items():
        harvest_brief(date, art_id, url)
