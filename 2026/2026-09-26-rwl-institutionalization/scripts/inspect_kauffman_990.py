"""
Inspect Kauffman Foundation Form 990-PF electronic filings (2019-2024)
via ProPublica Nonprofit Explorer e-file XML/HTML endpoints.
Searches for all grants paid to Consolidated School District No. 4 (Grandview).
"""

import urllib.request
import gzip
import re
import json

FILINGS = {
    "TY2024": "202523169349103332",
    "TY2023": "202443209349101644",
    "TY2022": "202303199349101530",
    "TY2021": "202213189349105236",
    "TY2020": "202143159349103869",
    "TY2019": "202003169349101105",
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def inspect_all():
    results = {}
    for tax_year, filing_id in FILINGS.items():
        print(f"\n==================================================")
        print(f"[*] Checking {tax_year} (Filing ID: {filing_id})")
        url = f"https://projects.propublica.org/nonprofits/full_text/{filing_id}/IRS990PF"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            resp = urllib.request.urlopen(req)
            raw = resp.read()
            # check if gzip
            if raw[:2] == b'\x1f\x8b':
                html = gzip.decompress(raw).decode("utf-8", errors="replace")
            else:
                html = raw.decode("utf-8", errors="replace")
                
            print(f"[+] Downloaded & decompressed: {len(html):,} bytes.")
            
            # Search for Grandview / Consolidated School District No. 4
            pattern = re.compile(r"CONSOLIDATED\s+SCHOOL\s+DISTRICT\s+NO\.?\s*4|GRANDVIEW", re.I)
            matches = list(pattern.finditer(html))
            print(f"[+] Pattern matches found: {len(matches)}")
            
            records = []
            for m in matches:
                pos = m.start()
                r_start = html.rfind("<tr", 0, pos)
                r_end = html.find("</tr>", pos)
                if r_start != -1 and r_end != -1:
                    row_html = html[r_start:r_end+5]
                    # Determine whether this is in Line 3a (Paid During Year) or 3b (Approved for Future)
                    chunk_before = html[max(0, pos-15000):pos]
                    is_3b = "GrantOrContriApprvForFutGrp" in row_html or "Approved for Future" in chunk_before[-2000:]
                    section = "Line 3b (Approved for Future)" if is_3b else "Line 3a (Paid During Year)"
                    
                    # Clean text
                    clean_row = re.sub(r"<[^>]+>", " | ", row_html)
                    clean_row = " ".join(clean_row.split())
                    
                    # Extract dollar amount
                    amt_m = re.findall(r"\b\d{1,3}(?:,\d{3})+\b", clean_row)
                    
                    rec = {
                        "tax_year": tax_year,
                        "filing_id": filing_id,
                        "section": section,
                        "amounts": amt_m,
                        "row_text": clean_row
                    }
                    if rec not in records:
                        records.append(rec)
                        print(f"  -> {section}: Amounts: {amt_m}")
                        print(f"     Text: {clean_row[:220]}...")
                        
            results[tax_year] = records
        except Exception as e:
            print(f"[!] Error fetching {tax_year}: {e}")
            results[tax_year] = []
            
    with open("data/raw/grandview-c4/finance/kauffman_990pf_grandview_grants.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("\n[+] Full results saved to data/raw/grandview-c4/finance/kauffman_990pf_grandview_grants.json")

if __name__ == "__main__":
    inspect_all()
