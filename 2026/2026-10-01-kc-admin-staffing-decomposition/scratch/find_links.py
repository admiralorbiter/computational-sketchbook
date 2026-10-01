import re

with open(r'C:\Users\admir\.gemini\antigravity\brain\ed240f75-6c83-4e24-b746-0d7d3a4d4032\.system_generated\steps\683\content.md', encoding='utf-8') as f:
    text = f.read()

links = set(re.findall(r'\[(.*?)\]\((.*?)\)', text))
for text_label, url in sorted(links):
    if any(k in text_label.lower() or k in url.lower() for k in ['budget', 'financ', 'profile', 'personnel', 'staff', 'so66', 'ksde']):
        print(f"{text_label} -> {url}")
