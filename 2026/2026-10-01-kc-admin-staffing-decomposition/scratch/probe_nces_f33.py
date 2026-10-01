import requests
import re
from bs4 import BeautifulSoup

url = "https://nces.ed.gov/use-work/dataset/documentation-nces-common-core-data-school-district-finance-survey-f-33-school-year-2022-23-fiscal"
r = requests.get(url, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")
for a in soup.find_all("a", href=True):
    href = a["href"]
    if any(k in href.lower() for k in ["zip", "csv", "txt", "pdf", "data", "download"]):
        print(f"{a.get_text(strip=True)} -> {href}")
