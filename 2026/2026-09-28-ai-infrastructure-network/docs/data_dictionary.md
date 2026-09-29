# Data Dictionary: AI Infrastructure Financial Network

This document defines the schema, types, constraints, and operational definitions for all standardized datasets in `data/processed/`.

---

## 1. Entities Registry (`entities.parquet` / `entities.csv`)

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `entity_id` | String | No | Primary Key. Standardized uppercase ticker or canonical slug. | `CRWV`, `POLARIS_FORGE_1` |
| `name` | String | No | Legal entity corporate name. | `CoreWeave, Inc.` |
| `ticker` | String | Yes | Stock ticker symbol for publicly traded entities; null otherwise. | `CRWV`, `NVDA` |
| `cik` | String | Yes | SEC EDGAR 10-digit Central Index Key (CIK). | `0001769628` |
| `category` | String | No | Broad industry layer: `hardware_supplier`, `hyperscaler_cloud`, `neocloud_operator`, `datacenter_developer`, `server_oem`, `hyperscaler_anchor`, `private_credit_syndicate`, `project_spv`, `physical_asset_project`. | `neocloud_operator` |
| `subsector` | String | Yes | Detailed operational classification. | `specialized_gpu_cloud` |
| `jurisdiction` | String | Yes | State/Country of incorporation. | `US-DE`, `US-ND` |
| `status` | String | No | Operational status: `public`, `private_syndicate`, `subsidiary_spv`, `physical_asset`. | `public` |
| `reporting_standard` | String | Yes | Primary accounting framework: `US-GAAP`, `US-GAAP_consolidated`, `null`. | `US-GAAP` |
| `description` | String | Yes | Summary of strategic role in the AI infrastructure buildout. | *Text* |
| `key_counterparties` | String | Yes | Comma-separated list of major connected `entity_id` nodes. | `NVDA,APLD,MSFT` |

---

## 2. Standardized Financial Facts (`financials.parquet` / `financials.csv`)

| Column Name | Data Type | Nullable | Description / Standardized Concept | Example |
| :--- | :--- | :--- | :--- | :--- |
| `entity_id` | String | No | Foreign Key referencing `entities.entity_id`. | `NVDA` |
| `ticker` | String | No | Public ticker symbol. | `NVDA` |
| `cik` | String | No | SEC CIK code. | `0001045810` |
| `metric` | String | No | Standardized metric name: `revenue`, `cost_of_revenue`, `operating_income`, `net_income`, `cash_and_equivalents`, `operating_cash_flow`, `capital_expenditures`, `ppe_net`, `accounts_receivable`, `inventory`, `operating_lease_liabilities`, `total_debt`, `backlog_rpo`. | `revenue` |
| `concept_name` | String | No | Exact US-GAAP XBRL element matched in the SEC filing. | `Revenues` |
| `period_end` | Date (str)| No | Balance sheet or income statement reporting period end (`YYYY-MM-DD`). | `2026-07-26` |
| `fiscal_year` | Integer | Yes | Reporting fiscal year. | `2026` |
| `fiscal_period` | String | Yes | Fiscal quarter/annual tag: `FY`, `Q1`, `Q2`, `Q3`, `Q4`. | `Q2` |
| `form` | String | No | SEC Form type: `10-K`, `10-Q`, `10-K/A`, `10-Q/A`, `S-1`. | `10-Q` |
| `value` | Float | No | Monetary value in base currency units (unscaled, exact USD). | `96221000000.0` |
| `unit` | String | No | Currency denomination (`USD`). | `USD` |
| `filed_date` | Date (str)| No | Date the filing was accepted by EDGAR (`YYYY-MM-DD`). | `2026-08-26` |
| `accession_number` | String | No | SEC accession identifier (`0001045810-26-000082`). | `0001045810-26-000082` |
| `start_date` | Date (str)| Yes | Measurement period start date for flow metrics (income/cash flows). | `2026-04-29` |

---

## 3. Obligation Ledger (`obligations.parquet` / `obligations.csv`)

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `obligation_id` | String | No | Primary Key: `OBL-{FROM}-{TO}-{NUM}`. | `OBL-CRWV-APLD-001` |
| `from_entity` | String | No | Debtor, Lessee, Obligor, or Buyer entity ID. | `CRWV_SPV_VIII` |
| `to_entity` | String | No | Creditor, Lessor, Obligee, or Seller entity ID. | `APLD_ELN_LLC` |
| `project_id` | String | Yes | Physical asset or campus slug if project-specific. | `POLARIS_FORGE_1` |
| `obligation_type` | String | No | Taxonomy: `datacenter_lease`, `debt_facility`, `collateral_pledge`, `gpu_procurement`, `server_assembly`, `anchor_offtake`, `equity_investment`, `guarantee_parent`. | `datacenter_lease` |
| `amount` | Float | No | Headline contract value or credit facility size in USD. | `11000000000.0` |
| `currency` | String | No | Currency denomination (`USD`). | `USD` |
| `effective_date` | Date (str)| No | Execution date of master contract. | `2025-05-28` |
| `maturity_date` | Date (str)| Yes | Contract expiration or debt maturity date. | `2040-05-31` |
| `term_years` | Float | Yes | Stated initial contractual duration in years. | `15.0` |
| `capacity_mw` | Float | Yes | Contracted critical IT electrical load in Megawatts (MW). | `400.0` |
| `committed_or_optional` | String | No | Legal commitment mode: `committed`, `optional`. | `committed` |
| `recourse` | String | No | Recourse scope: `full_recourse`, `limited_recourse_spv`, `non_recourse`, `equity_risk`. | `limited_recourse_spv` |
| `collateral` | String | Yes | Assets pledged as first-priority security. | *Text* |
| `guarantee` | String | Yes | Parent guarantee status and carve-outs. | *Text* |
| `termination_rights` | String | Yes | Contractual cancellation triggers and penalties. | *Text* |
| `payment_conditions` | String | Yes | Milestones, take-or-pay clauses, or rate structures. | *Text* |
| `claim_id` | String | No | Foreign Key referencing `evidence_claims.claim_id`. | `CLM-APLD-001` |
| `evidence_class` | String | No | Trust classification: `A` (Filed), `B` (Asserted), `C` (Inferred). | `A` |
| `confidence` | Float | No | Subjective epistemic confidence score (0.0 to 1.0). | `1.0` |
| `shared_assumptions` | String | No | Comma-separated list of assumption IDs supporting edge. | `A002,A003,A004,A005` |

---

## 4. Assumptions Registry (`assumptions.parquet` / `assumptions.csv`)

| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `assumption_id` | String | No | Primary Key: `A001` through `A999`. | `A001` |
| `name` | String | No | Short symbolic slug. | `GPU_RESIDUAL_VALUE` |
| `category` | String | No | Domain: `collateral_valuation`, `capital_markets`, `operations`, `physical_infrastructure`, `commercial_concentration`, `macro_capex`. | `collateral_valuation` |
| `description` | String | No | Formal statement of the underlying economic proposition. | *Text* |
| `observable_proxy` | String | No | Real-world observable data feed or channel check proxy. | *Text* |
| `base_case` | String | No | Prevailing market consensus baseline. | *Text* |
| `stress_case` | String | No | Adversarial stress test parameters. | *Text* |
| `affected_obligation_types` | String | No | Comma-separated list of vulnerable contract types. | `debt_facility,collateral_pledge` |

---

## 5. Evidence Ledger (`evidence_claims.parquet` / `evidence_claims.csv`)

| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `claim_id` | String | No | Primary Key: `CLM-{ENTITY}-{NUM}`. | `CLM-APLD-001` |
| `entity_id` | String | No | Company filing the source disclosure. | `APLD` |
| `filing_type` | String | No | SEC document type: `10-K`, `10-Q`, `8-K`, `Exhibit 10.x`. | `10-K` |
| `accession_number` | String | No | Unique SEC EDGAR accession number. | `0001144879-26-000048` |
| `filing_date` | Date (str)| No | Date filed with the SEC. | `2026-07-29` |
| `document_url` | String | No | Direct HTTPS hyperlink to SEC filing text. | `https://www.sec.gov/...` |
| `section_locator` | String | No | Specific Footnote, Item number, or Agreement Title. | `Item 1. Business` |
| `exact_quote` | String | No | Verbatim quotation transcribed from the primary source. | *Text* |
| `evidence_class` | String | No | Trust class: `A` (Filed), `B` (Asserted), `C` (Inferred). | `A` |
| `extraction_method` | String | No | Protocol used to retrieve the disclosure. | `SEC EDGAR 10-K direct audit` |
| `verifier_notes` | String | Yes | Analytical context on structural leverage. | *Text* |
