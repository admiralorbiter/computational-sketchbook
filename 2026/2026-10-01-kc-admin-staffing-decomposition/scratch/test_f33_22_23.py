import io
import zipfile
import requests
import pandas as pd

# Check sdf22_1a.zip
url22 = "https://nces.ed.gov/ccd/Data/zip/sdf22_1a.zip"
print(f"Fetching {url22}...")
r22 = requests.get(url22, timeout=30)
with zipfile.ZipFile(io.BytesIO(r22.content)) as z:
    print("Files in sdf22_1a.zip:", z.namelist())
    with z.open("sdf22_1a.txt") as f:
        df22 = pd.read_csv(f, sep="\t", nrows=5, encoding="latin1")
        print("sdf22 columns match check:", all(c in df22.columns for c in ["LEAID", "C14", "C15", "B11", "TOTALREV", "TCURELSC", "V21", "V15", "V13"]))

# Check sdf23_1a.txt
url23 = "https://nces.ed.gov/sites/default/files/data-asset/ccd-common-core-data/2025/09/documentation-nces-common-core-data-school-district-finance-survey-f-33-school-year-2022-23-fiscal/2025306_2.zip"
print(f"Fetching {url23}...")
r23 = requests.get(url23, timeout=30)
with zipfile.ZipFile(io.BytesIO(r23.content)) as z:
    print("Files in sdf23 zip:", z.namelist())
    with z.open("sdf23_1a.txt") as f:
        df23 = pd.read_csv(f, sep="\t", nrows=5, encoding="latin1")
        print("sdf23 columns match check:", all(c in df23.columns for c in ["LEAID", "C14", "C15", "B11", "TOTALREV", "TCURELSC", "V21", "V15", "V13"]))
