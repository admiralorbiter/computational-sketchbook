import io
import zipfile
import requests
import pandas as pd

# Test sdf21_1a.zip
url21 = "https://nces.ed.gov/ccd/Data/zip/sdf21_1a.zip"
print(f"Fetching {url21}...")
r21 = requests.get(url21, timeout=30)
with zipfile.ZipFile(io.BytesIO(r21.content)) as z:
    print("Files in sdf21_1a.zip:", z.namelist())
    for fn in z.namelist():
        if fn.endswith(".txt") or fn.endswith(".csv"):
            with z.open(fn) as f:
                df = pd.read_csv(f, sep="\t" if fn.endswith(".txt") else ",", nrows=5, encoding="latin1")
                print(f"Columns in {fn}:")
                for c in df.columns:
                    if any(k in c.lower() for k in ["leaid", "v33", "t06", "b11", "c14", "c15", "c19", "b10", "b12", "b13", "e13", "v11", "v13", "v15", "v21", "v23", "v27", "v37", "v40", "v45", "v90", "tcurel", "tcurinst", "tcursupp", "totalrev", "totalexp", "tfedrev", "tstrev", "tlocrev"]):
                        print(f"  {c}")
