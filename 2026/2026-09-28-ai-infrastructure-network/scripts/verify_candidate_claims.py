import json

def get_filings(path):
    with open(path) as f:
        d = json.load(f)
    if 'filings' in d and 'recent' in d['filings']:
        return d['filings']['recent']
    elif 'accessionNumber' in d:
        return d
    return {}

files = {
    'CRWV': ['data/raw/sec/CRWV_submissions_0001769628.json', 'data/raw/sec/CRWV_submissions_older.json'],
    'APLD': ['data/raw/sec/APLD_submissions_0001144879.json'],
    'ORCL': ['data/raw/sec/ORCL_submissions_0001341439.json'],
    'SMCI': ['data/raw/sec/SMCI_submissions_0001375365.json'],
    'MSFT': ['data/raw/sec/MSFT_submissions_0000789019.json'],
    'NVDA': ['data/raw/sec/NVDA_submissions_0001045810.json']
}

all_filings = {}
for entity, paths in files.items():
    all_filings[entity] = {}
    for p in paths:
        fdict = get_filings(p)
        if not fdict:
            continue
        for acc, form, fdate, doc in zip(fdict['accessionNumber'], fdict['form'], fdict['filingDate'], fdict['primaryDocument']):
            all_filings[entity][acc] = {'form': form, 'filingDate': fdate, 'primaryDocument': doc}

candidate_claims = [
    ('CRWV', '0001769628-26-000366', '10-Q', '2026-08-12'),
    ('CRWV', '0001769628-26-000104', '10-K', '2026-03-02'),
    ('CRWV', '0001769628-26-000236', '8-K',  '2026-05-18'),
    ('CRWV', '0001193125-25-058309', 'S-1/A', '2025-03-20'),
    ('CRWV', '0001769628-25-000019', '8-K',  '2025-05-21'),
    ('CRWV', '0001769628-25-000033', '8-K',  '2025-07-31'),
    ('CRWV', '0001769628-25-000050', '8-K',  '2025-09-30'),
    ('CRWV', '0001769628-25-000105', '8-K',  '2025-12-11'),
    ('CRWV', '0001769628-26-000129', '8-K',  '2026-03-31'),
    ('CRWV', '0001769628-26-000164', '8-K',  '2026-04-14'),
    ('CRWV', '0001769628-26-000291', '8-K',  '2026-06-18'),
    ('CRWV', '0001769628-26-000222', '10-Q', '2026-05-08'),
    ('APLD', '0001144879-26-000048', '10-K', '2026-07-29'),
    ('APLD', '0001493152-26-014498', '8-K/A', '2026-04-01'),
    ('APLD', '0001493152-26-028899', '8-K',  '2026-06-16'),
    ('APLD', '0001641172-25-013199', '8-K',  '2025-06-02'),
    ('APLD', '0001144879-24-000171', '8-K',  '2024-06-17'),
    ('APLD', '0001493152-25-006049', '8-K',  '2025-02-12'),
    ('APLD', '0001493152-24-048226', '8-K',  '2024-12-02'),
    ('APLD', '0001493152-26-021333', '8-K',  '2026-05-05'),
    ('SMCI', '0001375365-26-000022', '10-K', '2026-08-31'),
    ('ORCL', '0001193125-26-277521', '10-K', '2026-06-22'),
    ('MSFT', '0001193125-26-323660', '10-K', '2026-07-29')
]

errors = 0
for entity, acc, form, fdate in candidate_claims:
    found = all_filings[entity].get(acc)
    if not found:
        print("FAIL MISSING:", entity, acc)
        errors += 1
    elif found['form'] != form:
        print("FAIL FORM:", entity, acc, "expected", form, "got", found['form'])
        errors += 1
    elif found['filingDate'] != fdate:
        print("FAIL DATE:", entity, acc, "expected", fdate, "got", found['filingDate'])
        errors += 1
    else:
        print("PASS:", entity, acc, form, fdate, "->", found['primaryDocument'])

print(f"Total tested: {len(candidate_claims)}, errors: {errors}")
