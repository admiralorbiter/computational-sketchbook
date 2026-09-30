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
| `parent_entity_id` | String | Yes | Parent corporate entity ID for dynamic SPV unwrapping; null for root parents. | `APLD`, `CRWV` |
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
| `obligation_id` | String | No | Primary Key: `OBL-{FROM}-{TO}-{NUM}`. | `OBL-CRWV-APLD-LEASE` |
| `from_entity` | String | No | Debtor, Lessee, Obligor, or Buyer entity ID. | `CRWV_SPV_VIII` |
| `to_entity` | String | No | Creditor, Lessor, Obligee, or Seller entity ID. | `APLD_COMPUTECO` |
| `project_id` | String | Yes | Physical asset or campus slug if project-specific. | `POLARIS_FORGE_1` |
| `obligation_type` | String | No | Taxonomy: `datacenter_lease`, `debt_facility`, `aggregate_residual_debt`, `gpu_procurement`, `customer_revenue_concentration`, `equity_investment`, `contingent_guarantee`. | `datacenter_lease` |
| `amount` | Float | Yes | Headline contract value or credit facility principal in USD; null for uncapped contingent guarantees. | `11000000000.0` |
| `amount_known` | Boolean | No | True if contractual face value is explicitly stated; False if uncapped indemnity. | `True`, `False` |
| `amount_type` | String | No | Taxonomy: `principal_outstanding`, `facility_capacity`, `lifetime_contract_value`, `remaining_commitment`, `recognized_revenue`, `equity_investment`, `contingent_obligations`. | `principal_outstanding` |
| `as_of_date` | Date (str)| No | Baseline financial snapshot date (`YYYY-MM-DD`). | `2026-05-31` |
| `observed_as_of` | Date (str)| No | Financial observation period end date (`YYYY-MM-DD`). | `2026-05-31` |
| `economic_valid_from` | Date (str)| No | Inception / effective date in economic reality (`YYYY-MM-DD`). | `2025-05-28` |
| `economic_valid_to` | Date (str)| Yes | Expiration, maturity, or extinguishment date in economic reality; null if indefinite/unexpired. | `2040-05-31` |
| `publicly_known_from` | Date (str)| No | SEC filing date or public disclosure date when outside observers learned of contract (Information Clock). | `2025-06-02` |
| `valid_from` | Date (str)| No | Backwards-compatible alias for `economic_valid_from`. | `2025-05-28` |
| `valid_to` | Date (str)| Yes | Backwards-compatible alias for `economic_valid_to`. | `2040-05-31` |
| `rate_type` | String | No | Interest rate classification: `fixed`, `floating`, `none`. | `fixed`, `floating` |
| `benchmark_rate` | String | Yes | Underlying floating benchmark index: `SOFR`, null if fixed/non-debt. | `SOFR` |
| `supersedes` | String | Yes | Obligation ID of prior contract being extinguished/replaced; null if initial. | `OBL-APLD-DEBT-BRIDGE` |
| `superseded_by` | String | Yes | Obligation ID of successor contract replacing this obligation; null if active. | `OBL-APLD-DEBT-7PCT-2026` |
| `currency` | String | No | Currency denomination (`USD`). | `USD` |
| `effective_date` | Date (str)| Yes | Execution date of master contract. | `2025-05-28` |
| `maturity_date` | Date (str)| Yes | Contract expiration or debt maturity date. | `2040-05-31` |
| `term_years` | Float | Yes | Stated initial contractual duration in years. | `15.0` |
| `capacity_mw` | Float | Yes | Contracted critical IT electrical load in Megawatts (MW). | `400.0` |
| `capacity_description` | String | Yes | Specific hall, building, or operational phasing details. | `Building 3 (150 MW)` |
| `reference_exposure_estimate` | Float | Yes | Inferred Class C proxy value for uncapped obligations; null otherwise. | `4125000000.0` |
| `reference_exposure_class` | String | Yes | Epistemic class of reference proxy: `Class C (Analytical Proxy)`. | `Class C (Analytical Proxy)` |
| `committed_or_optional` | String | No | Legal commitment mode: `committed`, `optional`. | `committed` |
| `recourse` | String | No | Recourse scope: `full_recourse`, `limited_recourse_spv`, `non_recourse_spv`, `springing_parent_guaranty`, `equity_risk`. | `limited_recourse_spv` |
| `collateral` | String | Yes | Assets pledged as first-priority security. | *Text* |
| `guarantee` | String | Yes | Parent guarantee status and carve-outs. | *Text* |
| `termination_rights` | String | Yes | Contractual cancellation triggers and penalties. | *Text* |
| `payment_conditions` | String | Yes | Milestones, take-or-pay clauses, or rate structures. | *Text* |
| `claim_ids` | String | No | Foreign Key referencing `evidence_claims.claim_id`. | `CLM-APLD-001,CLM-APLD-004` |
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
| `quote_type` | String | No | Typology: `exact_quote` (verbatim substring), `source_excerpt` (abridged excerpt), `analyst_summary` (synthetic reconciliation). | `exact_quote` |
| `exact_quote` | String | No | Verbatim quotation or audited excerpt transcribed from primary source. | *Text* |
| `evidence_class` | String | No | Trust class: `A` (Filed), `B` (Asserted), `C` (Inferred). | `A` |
| `extraction_method` | String | No | Protocol used to retrieve the disclosure. | `SEC EDGAR 10-K direct audit` |
| `verifier_notes` | String | Yes | Analytical context on structural leverage. | *Text* |

---

## 6. Fact-Level Bitemporal Ledger (`obligation_facts.parquet` / `obligation_facts.csv`)

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `fact_id` | String | No | Primary Key: `FACT-{ENTITY/OBL}-{ATTR}-{YYYYMMDD}`. | `FACT-CRWV-DDTL1-PRIN-20260630` |
| `obligation_id` | String | Yes | Foreign Key referencing `obligations.obligation_id`; null for entity-level facts (e.g. aggregate swaps). | `OBL-CRWV-DEBT-DDTL1` |
| `entity_id` | String | No | Foreign Key referencing `entities.entity_id`. | `CRWV` |
| `attribute` | String | No | Measured attribute name: `principal_outstanding`, `swap_notional`, `facility_capacity`, `capacity_mw`, `lifetime_contract_value`, `reference_exposure_estimate`. | `principal_outstanding` |
| `value` | Float | Yes | Numeric measured value in base units; null if unquantified/uncapped. | `1300000000.0` |
| `unit` | String | No | Measurement unit: `USD`, `MW`. | `USD` |
| `economic_as_of` | Date (str)| No | Balance sheet or period-end date of the measurement in economic reality (`YYYY-MM-DD`). | `2026-06-30` |
| `publicly_known_from` | Date (str)| No | SEC filing or announcement date when the measurement became public knowledge (Information Clock). | `2026-08-12` |
| `truth_claim_id` | String | No | Foreign Key referencing `evidence_claims.claim_id` certifying audited ground truth. | `CLM-CRWV-001` |
| `knowledge_claim_id` | String | No | Foreign Key referencing `evidence_claims.claim_id` certifying earliest contemporaneous public awareness. | `CLM-CRWV-007` |
| `claim_id` | String | No | Legacy Foreign Key alias for `truth_claim_id`. | `CLM-CRWV-001` |
| `evidence_class` | String | No | Trust classification: `A` (Filed), `B` (Asserted), `C` (Inferred). | `A` |

---

## 7. Obligation Lifecycle Events Ledger (`obligation_events.parquet` / `obligation_events.csv`)

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `event_id` | String | No | Primary Key: `EVT-{OBLIGATION_SUFFIX}-{EVENT_TYPE}`. | `EVT-APLD-DEBT-BRIDGE-SUPERSEDED` |
| `obligation_id` | String | No | Foreign Key referencing `obligations.obligation_id`. | `OBL-APLD-DEBT-BRIDGE` |
| `event_type` | String | No | Lifecycle event classification: `created`, `superseded`, `amended`, `extinguished`. | `superseded` |
| `economic_effective_at` | Date (str)| No | Effective date of the event in economic reality (`YYYY-MM-DD`). | `2026-06-16` |
| `publicly_known_at` | Date (str)| No | Date when the event was publicly disclosed (e.g. Form 8-K filing date). | `2026-06-18` |
| `related_obligation_id` | String | Yes | Foreign Key referencing successor or linked obligation; null if standalone. | `OBL-APLD-DEBT-7PCT-2026` |
| `claim_id` | String | No | Foreign Key referencing `evidence_claims.claim_id` substantiating the event. | `CLM-APLD-008` |
| `description` | String | No | Detailed contractual narrative describing the lifecycle transition. | *Text* |

---

## 8. Attribute-Level Contract Terms Provenance Ledger (`obligation_terms.parquet` / `obligation_terms.csv`)

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `term_id` | String | No | Primary Key: `TRM-{ENTITY}-{SUFFIX}-{ATTR}`. | `TRM-WULF-CONV2030-RATE` |
| `obligation_id` | String | No | Foreign Key referencing `obligations.obligation_id`. | `OBL-WULF-DEBT-CONV-2030` |
| `attribute` | String | No | Specific contractual attribute: `principal_amount`, `interest_rate`, `effective_date`, `maturity_date`, `maturity_rule`, `recourse`, `contracted_capacity_mw`, `term_years`, `margin_bps`, `floor_bps`, `benchmark`, `contract_value`. | `interest_rate` |
| `value` | String | No | String-encoded verbatim or normalized contractual value. | `0.0275` |
| `claim_id` | String | No | Foreign Key referencing `evidence_claims.claim_id`. | `CLM-WULF-002` |
| `source_locator` | String | Yes | Item, Note, or Exhibit reference in the cited primary SEC filing. | `Item 1.01` |
| `evidence_class` | String | No | Trust classification: `A` (Filed), `B` (Asserted), `C` (Inferred). | `A` |

---

## 9. Obligation Rate Legs Ledger (`obligation_rate_legs.parquet` / `obligation_rate_legs.csv`)

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `leg_id` | String | No | Primary Key: `LEG-{ENTITY}-{SUFFIX}-{TYPE}`. | `LEG-CRWV-DDTL4-FLOATING` |
| `obligation_id` | String | No | Foreign Key referencing `obligations.obligation_id`. | `OBL-CRWV-DEBT-DDTL4` |
| `leg_type` | String | No | Rate leg classification: `floating`, `fixed`. | `floating` |
| `principal` | Float | No | Allocated principal balance for this specific tranche/leg in USD. | `1400000000.0` |
| `benchmark` | String | Yes | Underlying floating benchmark index: `SOFR`, null if fixed leg. | `SOFR` |
| `margin_bps` | Float | Yes | Spread over benchmark in basis points. | `225.0` |
| `floor_bps` | Float | Yes | Benchmark floor in basis points. | `0.0` |
| `fixed_coupon` | Float | Yes | Annual fixed coupon rate as a decimal (e.g. 0.0635 for 6.35%); null if floating. | `0.0635` |
| `spread_grid_id` | String | Yes | Identifier for credit-spread matrix; null if fixed/single-spread. | `null` |
| `description` | String | Yes | Contractual description of the rate tranche. | *Text* |

---

## 10. Facilities Registry (`facilities.parquet` / `facilities.csv`)

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `facility_id` | String | No | Primary Key: `FAC-{OPERATOR}-{CAMPUS}`. | `FAC-APLD-POLARIS-FORGE-1` |
| `facility_name` | String | No | Official commercial name of the campus or data center. | `Polaris Forge 1 Campus` |
| `operator_entity_id` | String | No | Foreign Key referencing `entities.entity_id` (primary operating entity). | `APLD` |
| `landlord_spv_entity_id` | String | Yes | Foreign Key referencing `entities.entity_id` (property-holding SPV); null if operating co direct. | `APLD_COMPUTECO` |
| `tenant_entity_id` | String | Yes | Foreign Key referencing `entities.entity_id` (anchor AI tenant); null if unleased/self-operated. | `CRWV` |
| `city` | String | No | Municipality or town location. | `Ellendale` |
| `county` | String | Yes | County or district jurisdiction. | `Dickey County` |
| `state_or_country` | String | No | State or ISO country code (`US-ND`, `US-TX`, `FI`). | `US-ND` |
| `status` | String | No | Operational status: `operational`, `operational_and_expanding`, `under_construction`, `announced`. | `operational_and_expanding` |
| `primary_grid_region` | String | Yes | Operational balancing authority / RTO control area: `MISO`, `ERCOT`, `SPP`, `NYISO`, `FINGRID`, or `None` (for local municipal distribution or pending interconnections). Note: SERC is excluded as it is a NERC Regional Entity, not an operational balancing authority. | `MISO` |
| `description` | String | Yes | Summary of campus physical and computing architecture. | *Text* |

---

## 11. Power Relationships Ledger (`power_relationships.parquet` / `power_relationships.csv`)

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `power_rel_id` | String | No | Primary Key: `PWR-{OPERATOR}-{CAMPUS}-{UTILITY_SHORT}`. | `PWR-APLD-PF1-MDU-ESA` |
| `facility_id` | String | No | Foreign Key referencing `facilities.facility_id`. | `FAC-APLD-POLARIS-FORGE-1` |
| `utility_entity_id` | String | Yes | Foreign Key referencing `entities.entity_id` (contractual electric utility); null if direct transmission interconnection or pending. | `MDU` |
| `grid_operator_entity_id` | String | Yes | Foreign Key referencing `entities.entity_id` (RTO/ISO/TSO); null if non-RTO municipal distribution or pending. | `MISO` |
| `relationship_type` | String | No | Taxonomy: `electric_service_agreement`, `interconnection_agreement`, `power_allocation_agreement`, `interconnection_request`. | `electric_service_agreement` |
| `reliability_regime` | String | No | Mechanism-specific reliability state: `firm_service`, `mandatory_grid_emergency_curtailment`, `voluntary_price_response`, `interconnection_not_energized`, `interruptible_tariff`. | `firm_service` |
| `firm_or_interruptible` | String | No | Operational status summary: `firm`, `curtailable`, `not_energized`. | `firm` |
| `curtailment_rights` | String | Yes | Curtailment conditions, emergency protocols, or demand response commitments. | *Text* |
| `tariff_structure` | String | Yes | Rate design, cost-of-service, or wholesale pass-through pricing mechanism. | *Text* |
| `effective_date` | Date (str)| Yes | Execution date of power contract (`YYYY-MM-DD`). | `2024-06-04` |
| `term_years` | Float | Yes | Stated initial agreement term duration in years. | `12.0` |
| `capacity_basis_mw` | Float | No | Non-overlapping electrical capacity basis in Megawatts (MW) for regional concentration analysis. | `350.0` |
| `claim_id` | String | No | Foreign Key referencing `power_claims.claim_id` (capacity/contract basis claim). | `CLM-PWR-MDU-001` |
| `evidence_class` | String | No | Trust classification: `A` (Filed), `B` (Asserted), `C` (Inferred). | `A` |
| `reliability_claim_id` | String | No | Foreign Key referencing `power_claims.claim_id` for specific reliability regime provenance. | `CLM-PWR-CORZ-002` |
| `reliability_evidence_class` | String | No | Trust classification for reliability regime: `A` (Filed), `B` (Asserted). | `A` |

---

## 12. Power Facts Ledger (`power_facts.parquet` / `power_facts.csv`)

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `fact_id` | String | No | Primary Key: `PFACT-{OPERATOR}-{CAMPUS}-{MW_TYPE}`. | `PFACT-APLD-PF1-CRIT-IT` |
| `facility_id` | String | No | Foreign Key referencing `facilities.facility_id`. | `FAC-APLD-POLARIS-FORGE-1` |
| `power_rel_id` | String | No | Foreign Key referencing `power_relationships.power_rel_id`. | `PWR-APLD-PF1-MDU-ESA` |
| `mw_type` | String | No | Strictly typed MW concept: `critical_it_mw`, `leased_customer_mw`, `gross_utility_capacity_mw`, `contracted_service_mw`, `energized_mw`, `planned_mw`, `interconnection_request_mw`. | `critical_it_mw` |
| `value_mw` | Float | No | Electrical power capacity in Megawatts (MW). | `400.0` |
| `economic_as_of` | Date (str)| No | Measurement date in economic reality (`YYYY-MM-DD`). | `2026-05-31` |
| `publicly_known_from` | Date (str)| No | Date when measurement was publicly disclosed (Information Clock). | `2026-07-29` |
| `truth_claim_id` | String | No | Foreign Key referencing `evidence_claims.claim_id` or `power_claims.claim_id`. | `CLM-PWR-APLD-001` |
| `knowledge_claim_id` | String | No | Foreign Key referencing earliest public disclosure claim. | `CLM-PWR-APLD-001` |
| `evidence_class` | String | No | Trust classification: `A` (Filed), `B` (Asserted), `C` (Inferred). | `A` |

---

## 13. Power Contract Terms Ledger (`power_terms.parquet` / `power_terms.csv`)

Tracks 27 attribute-level contract terms (14 numeric capacity/MW terms, 100% Class A; 13 contractual reliability regime terms, 12 Class A, 1 Class B).

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `term_id` | String | No | Primary Key: `PTERM-{OPERATOR}-{CAMPUS}-{ATTR}`. | `PTERM-APLD-PF1-ESA-INC` |
| `power_rel_id` | String | No | Foreign Key referencing `power_relationships.power_rel_id`. | `PWR-APLD-PF1-MDU-ESA` |
| `attribute` | String | No | Contractual attribute: `approved_service_capacity_mw`, `gross_utility_capacity_mw`, `allocated_hydro_power_mw`, `total_energized_capacity_mw`, `operating_datacenter_capacity_mw`, `planned_development_capacity_mw`, `grid_connection_capacity_mw`, `contracted_electricity_connection_mw`, `reliability_regime`. | `reliability_regime` |
| `value` | String | No | String-encoded contractual value or regulatory parameter (`350.0`, `firm_service`, `mandatory_grid_emergency_curtailment`, `voluntary_price_response`). | `mandatory_grid_emergency_curtailment` |
| `claim_id` | String | No | Foreign Key referencing `power_claims.claim_id`. | `CLM-PWR-CORZ-002` |
| `source_locator` | String | Yes | Specific Note, Item, or Exhibit locator in cited filing. | `Item 8.01 Form 8-K` |
| `evidence_class` | String | No | Trust classification: `A` (Filed), `B` (Asserted). | `A` |

---

## 14. Power Evidence Ledger (`power_claims.parquet` / `power_claims.csv`)

Tracks 9 primary evidence claims: 8 primary SEC EDGAR submissions validated via HTML verbatim quotes + 1 primary utility disclosure (`CLM-PWR-NBIS-002`) verified against cached raw source via cryptographic SHA-256 hash.

| Column Name | Data Type | Nullable | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `claim_id` | String | No | Primary Key: `CLM-PWR-{ENTITY}-{NUM}`. | `CLM-PWR-MDU-001` |
| `entity_id` | String | No | Company filing the source disclosure (`MDU`, `APLD`, `CORZ`, `WULF`, `IREN`, `NBIS`, `NIVOS`). | `MDU` |
| `filing_type` | String | No | Regulatory filing type: `10-K`, `10-Q`, `8-K`, `20-F`, `PressRelease`. | `10-Q` |
| `accession_number` | String | No | Unique SEC EDGAR accession number or utility disclosure identifier. | `0000067716-26-000072` |
| `filing_date` | Date (str)| No | Date filed with regulatory commission or released (`YYYY-MM-DD`). | `2026-08-06` |
| `document_url` | String | No | Direct HTTPS hyperlink to filing text. | `https://www.sec.gov/...` |
| `section_locator` | String | No | Specific section or header in filing. | `Item 2. MD&A` |
| `quote_type` | String | No | Typology: `source_excerpt`. | `source_excerpt` |
| `exact_quote` | String | No | 100% normalized contiguous verbatim substring transcribed from primary disclosure. | *Text* |
| `evidence_class` | String | No | Trust classification: `A` (Filed), `B` (Asserted), `C` (Inferred). | `A` |
| `extraction_method` | String | No | Audit protocol used to extract disclosure (`SEC Form 10-Q direct audit`, `Utility Press Disclosure direct audit`). | `SEC Form 10-Q direct audit` |
| `verifier_notes` | String | Yes | Analytical context on physical power connectivity and grid boundary. | *Text* |

---

## 15. Obligation-to-Facility Attribution Ledger (`obligation_facility_links.parquet` / `obligation_facility_links.csv`)

Tracks 51 granular attribution links across all 47 decomposed financial obligations, enforcing the ADR-021 Invariant: **No facility-level dollar allocation unless demonstrably attributable to that facility.** Corporate debt remains corporate; portfolio credit remains portfolio; multi-facility contracts maintain discrete topological links with null allocated amounts to avoid synthetic pro-ration.

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `link_id` | String | No | Primary Key: `LNK-{OBLIGATION_ID}` or `LNK-{OBLIGATION_ID}-{CAMPUS}`. | `LNK-APLD-DEBT-PF1` |
| `obligation_id` | String | No | Foreign Key referencing `obligations.obligation_id`. | `OBL-APLD-DEBT-PF1` |
| `facility_id` | String | Yes | Foreign Key referencing `facilities.facility_id`; null for unallocated corporate/portfolio obligations. | `FAC-APLD-POLARIS-FORGE-1` |
| `link_type` | String | No | Taxonomy: `direct_project_financing`, `direct_equipment_financing`, `direct_customer_contract`, `direct_lease`, `completion_support`, `parent_guarantee`, `portfolio_or_corporate`, `proceeds_partially_allocated`, `unknown`. | `direct_project_financing` |
| `allocation_scope` | String | No | Scope taxonomy: `single_facility`, `multi_facility`, `corporate_unallocated`, `unknown`. | `single_facility` |
| `allocated_amount` | Float | Yes | Disclosed funded principal, lease commitment, or contract value in USD; null for multi-facility, uncapped, or corporate unallocated. | `2350000000.0` |
| `allocation_fraction`| Float | Yes | Disclosed proportion of obligation allocated (e.g. `1.0`, `0.5`); null otherwise. | `1.0` |
| `amount_type` | String | No | Taxonomy: `funded_principal`, `facility_capacity`, `lease_commitment`, `contingent_indemnity`, `guarantee_recourse`, `unallocated_debt`, `capacity_reservation`, `equity_investment`, `customer_concentration`, `joint_and_several_liability`. | `funded_principal` |
| `evidence_class` | String | No | Trust classification: `A` (Filed), `B` (Asserted), `C` (Inferred). | `A` |
| `truth_claim_id` | String | No | Foreign Key referencing primary source establishing ontological truth of the link. | `CLM-APLD-003` |
| `knowledge_claim_id` | String | No | Foreign Key referencing disclosure establishing public awareness of the link. | `CLM-APLD-010` |
| `claim_id` | String | No | Backward-compatible Foreign Key referencing primary claim. | `CLM-APLD-003` |
| `economic_from` | Date (str)| No | Effective date in economic reality (`YYYY-MM-DD`). | `2025-11-20` |
| `publicly_known_from`| Date (str)| No | Earliest date publicly disclosed (`YYYY-MM-DD`). | `2026-01-08` |
| `notes` | String | Yes | Detailed provenance and boundary documentation. | *Text* |

---

## 16. Facility Completion Facts (`facility_completion_facts.parquet` / `facility_completion_facts.csv`)

Tracks 14 canonical facility completion records capturing typed physical, energization, and contractual status dimensions across all modeled campuses with bitemporal dates and claim IDs (ADR-021.1a).

| Column Name | Data Type | Nullable | Description / Controlled Vocabulary | Example |
| :--- | :--- | :--- | :--- | :--- |
| `facility_id` | String | No | Primary Key. Foreign Key referencing `facilities.facility_id`. | `FAC-APLD-POLARIS-FORGE-1` |
| `facility_name` | String | No | Canonical facility name. | `Polaris Forge 1 (Ellendale)` |
| `operator_entity_id` | String | No | Foreign Key referencing `entities.entity_id`. | `APLD` |
| `utility_service_capacity_mw` | Float | Yes | Total utility agreement service capacity (MW); null if pending/uncontracted. | `350.0` |
| `utility_load_online_mw` | Float | Yes | Energized utility load online as of observation horizon (MW); null if pre-energized/undisclosed. | `60.0` |
| `critical_it_contracted_mw` | Float | Yes | Contracted critical IT load under anchor lease or colocation (MW); null if self-operated/uncontracted. | `400.0` |
| `service_ready_it_mw` | Float | Yes | Certified Ready-for-Service or operating critical IT capacity (MW); 0.0 if under construction. | `100.0` |
| `gpu_equipment_deployment_state` | String | No | Descriptive status of tenant/operator GPU cluster deployment. | `Tenant (CoreWeave) cluster commissioning & fit-out` |
| `gpu_compute_operational_mw` | Float | Yes | IT load actively executing commercial GPU compute (MW); null if tenant-managed/undisclosed. | `75.0` |
| `equipment_accepted_fraction` | Float | Yes | Fraction of cluster IT equipment delivered, accepted, and funded (0.0 to 1.0); null if tenant-owned. | `0.0`, `1.0` |
| `completion_status` | String | No | Status taxonomy: `operational`, `operational_and_expanding`, `under_construction`, `announced`. | `operational_and_expanding` |
| `next_milestone` | String | No | Next development, energization, or cluster acceptance milestone. | `Building 2 full tenant occupancy & Building 3 commissioning (2026-2027)` |
| `economic_as_of` | Date (str)| No | Period-end date of the measurement in economic reality (`YYYY-MM-DD`). | `2026-05-31` |
| `publicly_known_from` | Date (str)| No | Earliest date publicly disclosed (`YYYY-MM-DD`). | `2026-07-29` |
| `truth_claim_id` | String | No | Foreign Key referencing `evidence_claims.claim_id` or `power_claims.claim_id`. | `CLM-APLD-004` |
| `knowledge_claim_id` | String | No | Foreign Key referencing disclosure establishing public awareness. | `CLM-APLD-004` |
| `evidence_class` | String | No | Trust classification: `A` (Filed), `B` (Asserted). | `A` |
| `verifier_notes` | String | Yes | Analytical context on physical phasing, substation readiness, and escrow conditions. | *Text* |


