import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
url = 'https://www2.ed.gov/about/inits/ed/edfacts/data-files/index.html'
r = requests.get(url, headers=headers, timeout=15)
print('Status:', r.status_code)
soup = BeautifulSoup(r.text, 'html.parser')
for a in soup.find_all('a', href=True):
    t = a.get_text(strip=True)
    href = a['href']
    if any(k in t.lower() or k in href.lower() for k in ['disabilit', 'idea', 'english', 'lep', 'special', 'fs002', 'fs141']):
        print(f'{t} -> {href}')
