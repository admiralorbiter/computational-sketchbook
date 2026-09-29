# Architectural Decisions Log (`docs/decisions.md`)

This log records the durable architectural, methodological, and data design choices for the AI Infrastructure Financial Network project.

---

### ADR-001: Separation of Obligation Graph (Layer 2) from Financial Statements (Layer 1)
- **Status:** Accepted (2026-09-28)
- **Context:** Standard equity and credit research models focus on individual corporate financial statements (Revenue, Debt/EBITDA, Cash Flow). However, systemic risk in large infrastructure buildouts emerges not from isolated balance sheets, but from the joint contractual obligations between entities (the "bubble in the joins").
- **Decision:** Separate the analytical architecture into three distinct layers: (1) Standardized accounting financials via SEC XBRL, (2) The contractual obligation graph where contracts are directed edges with rich legal attributes, and (3) Shared systemic assumptions.
- **Consequences:** Financial statements provide the baseline solvency capacity of individual nodes, while the obligation graph provides the transmission network across which shocks propagate.

---

### ADR-002: Direct SEC EDGAR XBRL Ingestion with Local Immutable Caching
- **Status:** Accepted (2026-09-28)
- **Context:** Third-party financial data APIs frequently abstract away filing dates, restatements, footnote disclosures, or charge prohibitive subscription fees. SEC's `data.sec.gov` API provides authoritative US-GAAP facts with complete accession numbers and filing metadata.
- **Decision:** Implement `src/sec_ingest.py` to query `data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` directly, cache raw responses immutably under `data/raw/sec/`, and parse standardized metrics into Parquet/CSV tables.
- **Consequences:** Eliminates external vendor dependencies, guarantees 100% reproducible baseline data, and preserves verifiable SEC accession numbers for every fact.

---

### ADR-003: First-Class Representation of Project SPVs and Physical Campuses
- **Status:** Accepted (2026-09-28)
- **Context:** In large data center and compute buildouts, material contractual obligations and debt facilities are frequently isolated in bankruptcy-remote Special Purpose Vehicles (e.g. `CoreWeave Compute Acquisition Co. VIII, LLC`, `APLD ELN-02 LLC`) or tied to specific physical campuses (`Polaris Forge 1`). Modeling only parent corporate tickers obscures structural perimeter opacity.
- **Decision:** Model project SPVs and physical asset campuses as first-class nodes in the network graph. Provide an explicit unwrapping method (`unwrap_spv_perimeter()`) in `src/graph.py` to allow comparative analysis between the legal entity graph and the consolidated economic graph.
- **Consequences:** Enables direct tracking of perimeter opacity, parent guarantees, and project-level execution risks (e.g., substation energization delays).

---

### ADR-004: Assumption-Indexed Multi-Hop Contagion Propagation Architecture
- **Status:** Accepted (2026-09-28)
- **Context:** Conventional credit stress tests ask "Does Entity X default under a macro recession?". The deeper research question for an infrastructure buildout is: "What single economic assumption supports the largest contractual value across otherwise independent balance sheets, and what happens when that assumption breaks?"
- **Decision:** Index all contractual obligations to shared systemic assumptions ($A_1 \dots A_m$). Build a multi-hop simulation engine (`src/stress.py`) that perturbs one or more assumptions, identifies 1st-order stressed edges, tags distressed debtors/creditors, and traces 2nd-order outgoing obligation impairments.
- **Consequences:** Replaces speculative bankruptcy prediction with an observable transmission model that maps exact domino paths across nodes.

---

### ADR-005: Strict Three-Tier Evidence Trust Hierarchy (A/B/C)
- **Status:** Accepted (2026-09-28)
- **Context:** Repeated LLM processing often blurs the distinction between a binding legal contract and executive conference call commentary.
- **Decision:** Mandate three evidence classes: Class A (Filed SEC contracts/10-K notes), Class B (Company asserted/IR transcripts), Class C (Analytical/inferred). Store every supporting fact in an audited `evidence_claims.parquet` ledger with accession numbers and verbatim quotes.
- **Consequences:** Prevents hallucination creep and enables downstream users to filter network edges by evidence certainty.
