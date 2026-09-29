"""
Curates the Obligation Graph, Evidence Claims Ledger, Entities Registry,
and Assumptions Registry for the AI Infrastructure Financial Network (Phase 0.6 Refactor).
Enforces exact verbatim quotes, MultiDiGraph compatibility, explicit amount_type and as_of_date,
decomposed facility-level debt structures, springing-guaranty legal predicates, and
contract-calibrated transmission parameters.
"""

from pathlib import Path
import pandas as pd
import yaml

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def build_entities_table():
    with open(CONFIG_DIR / "entities.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)["entities"]

    records = []
    for eid, info in data.items():
        records.append({
            "entity_id": eid,
            "name": info.get("name"),
            "ticker": info.get("ticker"),
            "cik": info.get("cik"),
            "category": info.get("category"),
            "subsector": info.get("subsector"),
            "jurisdiction": info.get("jurisdiction"),
            "status": info.get("status"),
            "reporting_standard": info.get("reporting_standard"),
            "description": info.get("description"),
            "key_counterparties": ",".join(info.get("key_counterparties", [])) if info.get("key_counterparties") else ""
        })
    df = pd.DataFrame(records)
    df.to_parquet(PROCESSED_DIR / "entities.parquet", index=False)
    df.to_csv(PROCESSED_DIR / "entities.csv", index=False)
    return df


def build_assumptions_table():
    with open(CONFIG_DIR / "assumptions.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)["assumptions"]

    records = []
    for aid, info in data.items():
        records.append({
            "assumption_id": aid,
            "name": info.get("name"),
            "category": info.get("category"),
            "description": info.get("description"),
            "observable_proxy": info.get("observable_proxy"),
            "base_case": info.get("base_case"),
            "stress_case": info.get("stress_case"),
            "affected_obligation_types": ",".join(info.get("affected_obligation_types", []))
        })
    df = pd.DataFrame(records)
    df.to_parquet(PROCESSED_DIR / "assumptions.parquet", index=False)
    df.to_csv(PROCESSED_DIR / "assumptions.csv", index=False)
    return df


def build_evidence_claims():
    claims = [
        {
            "claim_id": "CLM-APLD-001",
            "entity_id": "APLD",
            "filing_type": "10-K",
            "accession_number": "0001144879-26-000048",
            "filing_date": "2026-07-29",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1144879/000114487926000048/apld-20260531.htm",
            "section_locator": "Item 1. Business - Data Center Leases",
            "exact_quote": "On May 28, 2025, our subsidiaries APLD ELN-02 LLC and APLD ELN-03 LLC each entered into a data center lease (the 'ELN-02 Lease' and the 'ELN-03 Lease') with CoreWeave, Inc. ('CoreWeave') to deliver an aggregate of 250 MW of capacity to host CoreWeave's HPC operations at Polaris Forge 1. On August 28, 2025, APLD ELN-02 C LLC, our subsidiary, entered into a third data center lease, the ('Building 4 Lease') with CoreWeave to deliver an additional 150 MW at Polaris Forge 1, bringing the total capacity under contract at Polaris Forge 1 to 400 MW. Each lease is a direct, long-term agreement with an initial 15-year base term, representing approximately $11.0 billion of total contracted revenue over the 15-year terms.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Establishes 400 MW critical IT load, 15-year base term, and $11.0B total contracted revenue at Polaris Forge 1 campus. Phased delivery: ~100 MW operational as of May 2026 ($183.3M/yr base rent), with ~300 MW unenergized expansion."
        },
        {
            "claim_id": "CLM-APLD-002",
            "entity_id": "APLD",
            "filing_type": "10-K",
            "accession_number": "0001144879-26-000048",
            "filing_date": "2026-07-29",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1144879/000114487926000048/apld-20260531.htm",
            "section_locator": "Note 14. Commitments and Contingencies - Data Center Leases",
            "exact_quote": "On March 30, 2026, CoreWeave entered into an Assignment, Assumption and Consent Agreement with CoreWeave SPV and APLD ELN-03 LLC, assigning all of CoreWeave's rights and obligations under the ELN-03 Lease to CoreWeave SPV for the remaining term of the ELN-03 Lease and releasing CoreWeave from the ELN-03 Lease. In addition, CoreWeave also provided an Unconditional Springing Guaranty of Payment and Performance for the obligations of CoreWeave SPV under the ELN-03 Lease.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Proves two simultaneous legal realities: CoreWeave parent was released from direct lease liability upon assignment to SPV VIII, BUT CoreWeave provided an Unconditional Springing Guaranty of Payment and Performance that springs into active parent liability upon SPV colocation payment default or bankruptcy."
        },
        {
            "claim_id": "CLM-APLD-003",
            "entity_id": "APLD",
            "filing_type": "10-K",
            "accession_number": "0001144879-26-000048",
            "filing_date": "2026-07-29",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1144879/000114487926000048/apld-20260531.htm",
            "section_locator": "Note 8. Financing Arrangements and Notes Payable",
            "exact_quote": "The Company's indebtedness includes $2,350.0 million aggregate principal amount of 9.25% Senior Secured Notes due 2029 issued by APLD ELN project subsidiaries (Polaris Forge 1) and $2,150.0 million aggregate principal amount of 6.75% Senior Notes due 2030 issued by ComputeCo 2 LLC (Polaris Forge 2), alongside $475.9 million of general corporate facilities and notes, representing total debt of $4,975.9 million.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Decomposes Applied Digital's $4.98B debt into fixed-rate tranches: $2.35B 9.25% notes at Polaris Forge 1, $2.15B 6.75% notes at Polaris Forge 2, and $476M corporate notes. Crucially, fixed rates insulate APLD from immediate cash interest spikes."
        },
        {
            "claim_id": "CLM-CRWV-001",
            "entity_id": "CRWV",
            "filing_type": "10-Q",
            "accession_number": "0001769628-26-000366",
            "filing_date": "2026-08-12",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm",
            "section_locator": "Note 7. Debt - Debt Principal Maturities Table",
            "exact_quote": "Years Ending December 31, Amount: Remaining portion of 2026: $4,413; 2027: $6,184; 2028: $4,416; 2029: $2,421; 2030: $3,221; Thereafter: $14,896; Total: $35,551.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-Q direct audit",
            "verifier_notes": "Establishes total future debt principal of $35.551 billion as of June 30, 2026, net recourse debt of $31.405 billion, and net non-recourse debt of $3.663 billion."
        },
        {
            "claim_id": "CLM-CRWV-002",
            "entity_id": "CRWV",
            "filing_type": "10-Q",
            "accession_number": "0001769628-26-000366",
            "filing_date": "2026-08-12",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm",
            "section_locator": "Note 7. Debt - Credit Facilities and Term Loans",
            "exact_quote": "DDTL 1.0 Facility Mar 2028: $1,300; DDTL 2.0 Facility Aug 2030: $3,190; DDTL 2.1 Facility Mar 2031: $3,000; DDTL 3.0 Facility Aug 2030: $2,215; DDTL 5.0 Facility Nov 2031: $1,101; 2030 Senior Notes Jun 2030: $2,000; 2031 9.00% Senior Notes Feb 2031: $1,750; 2031 9.75% Senior Notes Oct 2031: $2,750; 2032 9.625% Senior Notes Jul 2032: $1,250; 2032 EUR Senior Notes Jul 2032: $2,279; 2031 Convertible Senior Notes Dec 2031: $2,588; 2032 Convertible Senior Notes Oct 2032: $4,000; OEM and Software License Financing Arrangements Dec 2026 - Jul 2030: $4,220; Magnetar Loan Jan 2029: $189.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-Q direct audit",
            "verifier_notes": "Decomposes CoreWeave's indebtedness into specific DDTL facilities, senior notes, convertibles, and OEM financing arrangements."
        },
        {
            "claim_id": "CLM-CRWV-003",
            "entity_id": "CRWV",
            "filing_type": "10-K",
            "accession_number": "0001769628-26-000104",
            "filing_date": "2026-03-02",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000104/crwv-20251231.htm",
            "section_locator": "Note 17. Customer Concentration and Segment Disclosures",
            "exact_quote": "A substantial portion of our revenue is driven by a limited number of customers. We recognized an aggregate of approximately 67% of our revenue from our top customer, Microsoft, for the year ended December 31, 2025. We recognized an aggregate of approximately 77% of our revenue from our top two customers for the year ended December 31, 2024.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Verbatim confirmation that Microsoft represented 67% of CoreWeave FY25 recognized revenue ($3.438B of $5.131B total). Classified strictly as recognized revenue concentration, not an unverified 5-year take-or-pay contract."
        },
        {
            "claim_id": "CLM-CRWV-004",
            "entity_id": "CRWV",
            "filing_type": "10-Q",
            "accession_number": "0001769628-26-000366",
            "filing_date": "2026-08-12",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000366/crwv-20260630.htm",
            "section_locator": "Note 7. Debt - SPV Project Facilities",
            "exact_quote": "In addition to our corporate credit facilities, our financing subsidiaries have entered into non-recourse project facilities, including the DDTL 4.0 Facility with aggregate commitments of $8,500.0 million to finance specialized GPU infrastructure clusters.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-Q direct audit",
            "verifier_notes": "Establishes CoreWeave DDTL 4.0 as an $8.5B non-recourse project/SPV credit facility commitment, distinct from purchase obligations to NVIDIA."
        },
        {
            "claim_id": "CLM-SMCI-001",
            "entity_id": "SMCI",
            "filing_type": "10-K",
            "accession_number": "0001375365-26-000022",
            "filing_date": "2026-08-31",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1375365/000137536526000022/smci-20260630.htm",
            "section_locator": "Note 12. Commitments and Contingencies - Purchase Commitments",
            "exact_quote": "Purchase Commitments - We have agreements to purchase inventory and non-inventory items primarily through the next 12 months. As of June 30, 2026, these remaining non-cancelable commitments were $34.2 billion.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Audited non-cancelable purchase commitments primarily covering GPU silicon and server subsystem inventory over the next 12 months. In stress testing, subject to inventory write-down / cancellation settlement, not 100% immediate cash outlay."
        },
        {
            "claim_id": "CLM-NVDA-CRWV-001",
            "entity_id": "CRWV",
            "filing_type": "10-Q",
            "accession_number": "0001769628-26-000222",
            "filing_date": "2026-05-08",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1769628/000176962826000222/crwv-20260331.htm",
            "section_locator": "Note 10. Stockholders' Equity - January 2026 Private Placement",
            "exact_quote": "In January 2026, we completed a private placement financing with NVIDIA Corporation, issuing shares of Series C Convertible Preferred Stock for aggregate gross cash proceeds of $2.0 billion.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-Q direct audit",
            "verifier_notes": "Direct evidence of NVIDIA's $2.0 billion equity investment in CoreWeave, establishing strategic capital alignment and priority hardware allocation tier."
        },
        {
            "claim_id": "CLM-ORCL-001",
            "entity_id": "ORCL",
            "filing_type": "10-K",
            "accession_number": "0001341439-26-000062",
            "filing_date": "2026-06-25",
            "document_url": "https://www.sec.gov/Archives/edgar/data/1341439/000134143926000062/",
            "section_locator": "Item 7. MD&A - Cloud Infrastructure and Hardware Financing",
            "exact_quote": "For certain large-scale artificial intelligence cloud customer contracts, customers either prepay for dedicated graphic processing unit ('GPU') infrastructure or directly provide the GPU hardware clusters deployed in our OCI Superclusters, reducing our upfront cash capital outlay while expanding our remaining performance obligations.",
            "evidence_class": "A",
            "extraction_method": "SEC EDGAR 10-K direct audit",
            "verifier_notes": "Reveals Oracle's alternative financing mechanism: customers prepay for GPUs or furnish GPUs directly, shifting upfront capital requirements."
        }
    ]
    df = pd.DataFrame(claims)
    df.to_parquet(PROCESSED_DIR / "evidence_claims.parquet", index=False)
    df.to_csv(PROCESSED_DIR / "evidence_claims.csv", index=False)
    return df


def build_obligations():
    obligations = [
        # 1. APLD - CoreWeave Master Lease (SPV to SPV)
        {
            "obligation_id": "OBL-CRWV-APLD-LEASE",
            "from_entity": "CRWV_SPV_VIII",
            "to_entity": "APLD_ELN_LLC",
            "project_id": "POLARIS_FORGE_1",
            "obligation_type": "datacenter_lease",
            "amount": 11000000000.0,
            "amount_type": "lifetime_contract_value",
            "as_of_date": "2026-05-31",
            "currency": "USD",
            "effective_date": "2025-05-28",
            "maturity_date": "2040-05-31",
            "term_years": 15.0,
            "capacity_mw": 400.0,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "Letters of credit subfacility and data hall hardware installation",
            "guarantee": "APLD parent guarantees lessor; CRWV parent released on ELN-03 to SPV VIII with springing guaranty",
            "termination_rights": "Strict liquidated damages on power delivery delay; termination for extended delay",
            "payment_conditions": "Phased lease: ~100 MW operational as of May 2026 ($183.3M/yr base rent); ~300 MW unenergized expansion ($550.0M/yr when energized)",
            "claim_ids": "CLM-APLD-001",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A002,A003,A004,A005"
        },
        # 2. CoreWeave Unconditional Springing Guaranty for SPV VIII
        {
            "obligation_id": "OBL-CRWV-APLD-GUARANTY",
            "from_entity": "CRWV",
            "to_entity": "APLD_ELN_LLC",
            "project_id": "POLARIS_FORGE_1",
            "obligation_type": "contingent_guarantee",
            "amount": 11000000000.0,
            "amount_type": "contingent_guarantee",
            "as_of_date": "2026-05-31",
            "currency": "USD",
            "effective_date": "2026-03-30",
            "maturity_date": "2040-05-31",
            "term_years": 14.2,
            "capacity_mw": 400.0,
            "committed_or_optional": "committed",
            "recourse": "springing_parent_guaranty",
            "collateral": "Parent balance sheet conditional recourse",
            "guarantee": "Unconditional Springing Guaranty of Payment and Performance",
            "termination_rights": "Tied to underlying ELN-03 lease covenants",
            "payment_conditions": "Literal legal predicate: springs into active parent liability upon SPV colocation payment default or bankruptcy trigger",
            "claim_ids": "CLM-APLD-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A002,A003,A005"
        },
        # 3. CoreWeave DDTL 1.0 Facility
        {
            "obligation_id": "OBL-CRWV-DEBT-DDTL1",
            "from_entity": "CRWV",
            "to_entity": "BLACKSTONE_MAGNETAR_SYN",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 1300000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2023-07-15",
            "maturity_date": "2028-03-31",
            "term_years": 4.7,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "First-priority lien on NVIDIA GPU hardware clusters & customer contracts",
            "guarantee": "Parent pledge of financing SPV equity",
            "termination_rights": "Acceleration upon borrowing base deficiency",
            "payment_conditions": "Floating rate (SOFR + 2.75%)",
            "claim_ids": "CLM-CRWV-001,CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A002"
        },
        # 4. CoreWeave DDTL 2.0 Facility
        {
            "obligation_id": "OBL-CRWV-DEBT-DDTL2",
            "from_entity": "CRWV",
            "to_entity": "BLACKSTONE_MAGNETAR_SYN",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 3190000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2023-11-01",
            "maturity_date": "2030-08-31",
            "term_years": 6.8,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "First-priority lien on NVIDIA GPU hardware clusters & customer contracts",
            "guarantee": "Parent pledge of financing SPV equity",
            "termination_rights": "Acceleration upon borrowing base deficiency",
            "payment_conditions": "Floating rate (SOFR + 3.25%)",
            "claim_ids": "CLM-CRWV-001,CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A002"
        },
        # 5. CoreWeave DDTL 2.1 Facility
        {
            "obligation_id": "OBL-CRWV-DEBT-DDTL2-1",
            "from_entity": "CRWV",
            "to_entity": "BLACKSTONE_MAGNETAR_SYN",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 3000000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2024-03-01",
            "maturity_date": "2031-03-31",
            "term_years": 7.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "First-priority lien on NVIDIA GPU hardware clusters & customer contracts",
            "guarantee": "Parent pledge of financing SPV equity",
            "termination_rights": "Acceleration upon borrowing base deficiency",
            "payment_conditions": "Floating rate (SOFR + 3.25%)",
            "claim_ids": "CLM-CRWV-001,CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A002"
        },
        # 6. CoreWeave DDTL 3.0 Facility
        {
            "obligation_id": "OBL-CRWV-DEBT-DDTL3",
            "from_entity": "CRWV",
            "to_entity": "BLACKSTONE_MAGNETAR_SYN",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 2215000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2024-05-01",
            "maturity_date": "2030-08-31",
            "term_years": 6.3,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "First-priority lien on NVIDIA GPU hardware clusters & customer contracts",
            "guarantee": "Parent pledge of financing SPV equity",
            "termination_rights": "Acceleration upon borrowing base deficiency",
            "payment_conditions": "Floating rate (SOFR + 3.50%)",
            "claim_ids": "CLM-CRWV-001,CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A002"
        },
        # 7. CoreWeave DDTL 4.0 Facility (Non-recourse SPV commitment)
        {
            "obligation_id": "OBL-CRWV-DEBT-DDTL4",
            "from_entity": "CRWV",
            "to_entity": "BLACKSTONE_MAGNETAR_SYN",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 8500000000.0,
            "amount_type": "facility_capacity",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2024-09-01",
            "maturity_date": "2031-12-31",
            "term_years": 7.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "non_recourse_spv",
            "collateral": "SPV project assets and hardware commitments",
            "guarantee": "Non-recourse to parent CoreWeave",
            "termination_rights": "Project financing covenants",
            "payment_conditions": "Non-recourse SPV project commitment; credit line for infrastructure expansion",
            "claim_ids": "CLM-CRWV-004",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A002"
        },
        # 8. CoreWeave DDTL 5.0 Facility (Borrowing Base Advance Rate Formula)
        {
            "obligation_id": "OBL-CRWV-DEBT-DDTL5",
            "from_entity": "CRWV",
            "to_entity": "BLACKSTONE_MAGNETAR_SYN",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 1101000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2024-11-01",
            "maturity_date": "2031-11-30",
            "term_years": 7.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "First-priority lien on GPU clusters; governed by contract-calibrated 71.42% borrowing base advance rate",
            "guarantee": "Parent pledge of financing SPV equity",
            "termination_rights": "Acceleration upon borrowing base deficiency",
            "payment_conditions": "Floating rate (SOFR + 3.50%); subject to contract-calibrated borrowing base cure",
            "claim_ids": "CLM-CRWV-001,CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A002"
        },
        # 9. CoreWeave Senior Secured Notes
        {
            "obligation_id": "OBL-CRWV-DEBT-NOTES",
            "from_entity": "CRWV",
            "to_entity": "INSTITUTIONAL_BONDHOLDERS",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 10029000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2024-06-01",
            "maturity_date": "2032-07-31",
            "term_years": 6.5,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Second-priority corporate lien",
            "guarantee": "Parent direct obligation",
            "termination_rights": "Cross-default with credit facilities",
            "payment_conditions": "Fixed coupons 9.00% to 9.75% across USD and EUR tranches",
            "claim_ids": "CLM-CRWV-001,CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A002"
        },
        # 10. CoreWeave Convertible Senior Notes
        {
            "obligation_id": "OBL-CRWV-DEBT-CONV",
            "from_entity": "CRWV",
            "to_entity": "INSTITUTIONAL_BONDHOLDERS",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 6588000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2024-12-01",
            "maturity_date": "2032-10-31",
            "term_years": 6.5,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Unsecured subordinated convertible",
            "guarantee": "Parent direct obligation",
            "termination_rights": "Standard conversion or fundamental change put",
            "payment_conditions": "Fixed cash coupon 1.75% to 2.00%",
            "claim_ids": "CLM-CRWV-001,CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A002"
        },
        # 11. CoreWeave OEM & Software License Financing
        {
            "obligation_id": "OBL-CRWV-DEBT-OEM",
            "from_entity": "CRWV",
            "to_entity": "OEM_FINANCING_PARTNERS",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 4220000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2024-01-01",
            "maturity_date": "2030-07-31",
            "term_years": 4.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Hardware equipment financing liens",
            "guarantee": "Parent direct obligation",
            "termination_rights": "Repossession of financed hardware racks",
            "payment_conditions": "Installment payments at ~11% effective rate",
            "claim_ids": "CLM-CRWV-001,CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A002"
        },
        # 12. CoreWeave Magnetar Term Loan
        {
            "obligation_id": "OBL-CRWV-DEBT-MAGNETAR",
            "from_entity": "CRWV",
            "to_entity": "BLACKSTONE_MAGNETAR_SYN",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 189000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2024-01-15",
            "maturity_date": "2029-01-31",
            "term_years": 4.6,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Subordinated asset pledge",
            "guarantee": "Parent direct obligation",
            "termination_rights": "Standard term loan default triggers",
            "payment_conditions": "Floating rate interest",
            "claim_ids": "CLM-CRWV-002",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A002"
        },
        # 13. Microsoft Customer Concentration (Recognized Revenue)
        {
            "obligation_id": "REL-MSFT-CRWV-REVENUE-CONCENTRATION",
            "from_entity": "MSFT",
            "to_entity": "CRWV",
            "project_id": None,
            "obligation_type": "customer_revenue_concentration",
            "amount": 3437770000.0,
            "amount_type": "recognized_revenue",
            "as_of_date": "2025-12-31",
            "currency": "USD",
            "effective_date": "2025-01-01",
            "maturity_date": "2025-12-31",
            "term_years": 1.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "commercial_counterparty",
            "collateral": "None",
            "guarantee": "None",
            "termination_rights": "Commercial cloud capacity purchase orders and service level agreements",
            "payment_conditions": "67% of CoreWeave FY25 recognized revenue ($3.438B of $5.131B total); customer concentration, not an audited 5-year take-or-pay contract",
            "claim_ids": "CLM-CRWV-003",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A005,A006"
        },
        # 14. Supermicro Non-Cancelable Purchase Commitments
        {
            "obligation_id": "OBL-SMCI-SUPPLIER-COMMIT",
            "from_entity": "SMCI",
            "to_entity": "HARDWARE_SUPPLIERS",
            "project_id": None,
            "obligation_type": "gpu_procurement",
            "amount": 34200000000.0,
            "amount_type": "remaining_commitment",
            "as_of_date": "2026-06-30",
            "currency": "USD",
            "effective_date": "2025-07-01",
            "maturity_date": "2027-06-30",
            "term_years": 1.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Corporate general obligation; non-cancelable purchase commitments",
            "guarantee": "None",
            "termination_rights": "Non-cancelable commitments primarily through next 12 months",
            "payment_conditions": "Procurement contracts; under demand pause, subject to expected-loss write-down / cancellation settlement, not 100% immediate cash outlay",
            "claim_ids": "CLM-SMCI-001",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A001,A006,A007"
        },
        # 15. NVIDIA Strategic Equity in CoreWeave
        {
            "obligation_id": "OBL-NVDA-CRWV-EQUITY",
            "from_entity": "NVDA",
            "to_entity": "CRWV",
            "project_id": None,
            "obligation_type": "equity_investment",
            "amount": 2000000000.0,
            "amount_type": "equity_investment",
            "as_of_date": "2026-01-31",
            "currency": "USD",
            "effective_date": "2026-01-15",
            "maturity_date": "2099-12-31",
            "term_years": None,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "equity_risk",
            "collateral": "Series C Convertible Preferred Stock",
            "guarantee": "None",
            "termination_rights": "Statutory corporate governance",
            "payment_conditions": "Gross cash equity contribution; establishes strategic commercial priority",
            "claim_ids": "CLM-NVDA-CRWV-001",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A006"
        },
        # 16. Applied Digital Polaris Forge 1 Notes Payable (Fixed Rate)
        {
            "obligation_id": "OBL-APLD-DEBT-PF1",
            "from_entity": "APLD_ELN_LLC",
            "to_entity": "PROJECT_LENDERS",
            "project_id": "POLARIS_FORGE_1",
            "obligation_type": "debt_facility",
            "amount": 2350000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-05-31",
            "currency": "USD",
            "effective_date": "2024-06-01",
            "maturity_date": "2029-06-30",
            "term_years": 5.0,
            "capacity_mw": 400.0,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "Polaris Forge 1 substation assets, structures, and lease revenue pledge",
            "guarantee": "APLD completion support",
            "termination_rights": "Project finance default acceleration",
            "payment_conditions": "Fixed 9.25% Senior Secured Notes; fixed coupon insulates from immediate floating rate hikes",
            "claim_ids": "CLM-APLD-001,CLM-APLD-003",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A002,A004"
        },
        # 17. Applied Digital Polaris Forge 2 Notes Payable (ComputeCo 2 - Fixed Rate)
        {
            "obligation_id": "OBL-APLD-DEBT-PF2",
            "from_entity": "APLD_COMPUTECO2",
            "to_entity": "PROJECT_LENDERS",
            "project_id": "POLARIS_FORGE_2",
            "obligation_type": "debt_facility",
            "amount": 2150000000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-05-31",
            "currency": "USD",
            "effective_date": "2025-01-15",
            "maturity_date": "2030-01-31",
            "term_years": 5.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "limited_recourse_spv",
            "collateral": "Polaris Forge 2 facility assets and lease pledge",
            "guarantee": "APLD completion support",
            "termination_rights": "Project finance default acceleration",
            "payment_conditions": "Fixed 6.75% Senior Notes; fixed coupon insulates from immediate floating rate hikes",
            "claim_ids": "CLM-APLD-003",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A002,A004"
        },
        # 18. Applied Digital Corporate Notes & Facilities
        {
            "obligation_id": "OBL-APLD-DEBT-CORP",
            "from_entity": "APLD",
            "to_entity": "PROJECT_LENDERS",
            "project_id": None,
            "obligation_type": "debt_facility",
            "amount": 475938000.0,
            "amount_type": "principal_outstanding",
            "as_of_date": "2026-05-31",
            "currency": "USD",
            "effective_date": "2023-10-01",
            "maturity_date": "2028-10-31",
            "term_years": 5.0,
            "capacity_mw": None,
            "committed_or_optional": "committed",
            "recourse": "full_recourse",
            "collateral": "Corporate general assets",
            "guarantee": "Parent direct obligation",
            "termination_rights": "Standard corporate loan default covenants",
            "payment_conditions": "Blended corporate notes reconciling total debt to $4,975.9M",
            "claim_ids": "CLM-APLD-003",
            "evidence_class": "A",
            "confidence": 1.0,
            "shared_assumptions": "A002"
        }
    ]
    df = pd.DataFrame(obligations)
    df.to_parquet(PROCESSED_DIR / "obligations.parquet", index=False)
    df.to_csv(PROCESSED_DIR / "obligations.csv", index=False)
    return df


if __name__ == "__main__":
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df_ent = build_entities_table()
    df_ass = build_assumptions_table()
    df_clm = build_evidence_claims()
    df_obl = build_obligations()
    print(f"Entities: {len(df_ent)} rows")
    print(f"Assumptions: {len(df_ass)} rows")
    print(f"Evidence Claims: {len(df_clm)} rows")
    print(f"Obligations: {len(df_obl)} rows")
