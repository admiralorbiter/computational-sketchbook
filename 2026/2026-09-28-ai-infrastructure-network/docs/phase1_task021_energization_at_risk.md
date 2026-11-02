# Task 021: Energization-at-Risk & Capital Synchronization Resilience Report (ADR-021.1a)

**Date:** September 30, 2026  
**Decision References:** ADR-021, ADR-021.1, and ADR-021.1a (`docs/decisions.md`)  
**Dataset State:** 62 registered entities, 47 decomposed financial obligations, 57 lifecycle events, 64 financial facts, 44 financial terms, 60 evidence claims, 14 physical facilities, 13 power relationships, 29 typed MW power facts, 27 power terms, 9 primary power claims, 51 obligation-facility attribution links, 14 canonical facility completion facts (`facility_completion_facts.parquet`).  
**Baseline Certification:** 100% exact verbatim substring verification across all 68 Class A SEC claims auto-bound via `data/raw/sec/source_registry.json` plus 1 primary utility disclosure; **0.00% data drift** across balance sheet, power, and attribution layers.

---

## Executive Summary & Core Verdicts

This report delivers the certified findings of **Task 021: Energization-at-Risk & Capital-to-Physical Attribution**, incorporating the epistemic auto-binding, bitemporal completion facts, and layered synchronization architecture of **ADR-021.1a**.

Prior to this work, high-level infrastructure analyses risked severe epistemic distortions by aggregating disparate contractual instruments into synthetic ratios—such as dividing Applied Digital's total consolidated debt by partial utility meter readings, or treating Iris Energy's \$2.4B equipment credit line as drawn, un-hedged debt carrying immediate interest.

By constructing a strict, audited **Attribution Layer** (`obligation_facility_links.parquet`) backed by typed completion dimensions in a canonical evidence table (`facility_completion_facts.parquet`), we enforced two foundational epistemic invariants:
$$\textbf{Universal Attribution Invariant: No facility-level dollar/MW ratio unless the dollar obligation is demonstrably attributable to that facility.}$$
$$\textbf{Dimensional Invariant: Utility service capacity, IT facility capacity, and GPU equipment deployment states are distinct, typed physical dimensions that must not be synthetically subtracted or imputed to zero.}$$

```
========================================================================================================
                      CAPITAL-TO-PHYSICAL ATTRIBUTION & SYNCHRONIZATION ARCHITECTURE
========================================================================================================

  [ CORPORATE & PORTFOLIO DEBT ]          [ PROJECT & EQUIPMENT FINANCING ]        [ PHYSICAL CAMPUS ]
  Held Strictly Separate ($39.358B)       Directly Attributable ($6.090B Funded)   Completion Facts (14 Sites)
  
  * CoreWeave Senior Notes & DDTLs        * Pre-Service Funded Debt ($3.740B):
    ($35.551B across 16 tranches)           - APLD PF1 Bldg 4 7% Notes ($1.59B) ----> Polaris Forge 1 (Bldg 4)
  * APLD Corporate Converts ($450M)         - APLD PF2 6.75% Notes ($2.15B) --------> Polaris Forge 2 (Pre-service)
  * APLD Residual Debt ($56.7M)             (Escrow Released June 18, 2026)
  * TeraWulf Convertibles ($2.525B)
  * Nebius Term Facility ($775M)          * Mixed Operational Exposure ($2.350B):
                                            - APLD PF1 9.25% Notes ($2.35B) --------> Polaris Forge 1 (Bldgs 2-3)
                                              (Bldg 2 100 MW Service-Ready;            350 MW Utility ESA / 60 MW Online
                                               Bldg 3 150 MW Partial Operation)        400 MW Critical IT Campus

  * Corporate Cash / Unallocated --------> * IREN MFSA & Notes ($2.40B) ----------> Mackenzie Campus, BC
                                            (IE Mackenzie Compute Ltd.)             80 MW Utility Online (Since 2022)
                                            [ Committed Capacity, Not Funded Debt ] 80 MW Service-Ready IT Infrastructure
                                            [ Staged Acceptance Window to Dec 2026] [ Staged GPU Server Acceptance ]

                                          * $0 Debt Attributed -------------------> Childress, TX (650 MW Live)
                                          * $0 Debt Attributed -------------------> Denton, TX (100 MW Live Colo)
========================================================================================================
```

### 1. Source-Registry Epistemic Auto-Binding (ADR-021.1a)
To prevent cross-filing false positives (where boilerplate text in one filing accidentally validates a citation to another), all Class A SEC claims bind strictly to their registered source document via `data/raw/sec/source_registry.json` (`accession_number + document_url -> local_file + sha256`). Global quote searches across arbitrary HTML files are prohibited; each claim validates strictly against its own verified local file and SHA-256 cryptographic digest.

### 2. Re-segmentation of \$6.090B Funded Debt
Funded project debt is strictly separated into two distinct risk tranches rather than lumped into a monolithic "pre-service" bucket:
- **\$3.740B Pre-Service Funded Debt:** Comprises \$1.590B Building 4 notes (ComputeCo 3 7.00% notes due 2031) and \$2.150B Polaris Forge 2 notes (ComputeCo 2 6.75% notes due 2031). These funds finance facilities currently under active civil/electrical construction prior to service commencement.
- **\$2.350B Mixed Completion/Operational Exposure:** Comprises the original Polaris Forge 1 notes (ComputeCo 9.250% notes due 2030). Building 2 (100 MW) is already certified Ready-for-Service and operational, while Building 3 (150 MW) is partially operational.

### 3. Modeled Debt Architecture vs Committed Capacity
Funded debt and undrawn equipment credit commitments are economically distinct and are not treated as additive equivalents:
- **Active Funded Debt:** **\$45,447.68M (\$45.448B)**
  * Corporate Balance Sheet Debt: **\$39,357.68M (\$39.358B)** (CoreWeave, TeraWulf, Nebius, APLD corporate)
  * Facility-Attributable Project Debt: **\$6,090.00M (\$6.090B)** (APLD SPVs only)
- **Committed Equipment Financing Capacity:** **\$2,400.00M (\$2.400B)** (IREN Mackenzie credit facility: \$1.2B MFSA + \$1.2B Senior Notes). This represents an undrawn commitment drawn only upon hardware delivery and acceptance through December 31, 2026.

### 4. Annual Carrying Cost Accounting
- **APLD ComputeCo 9.250% Notes due 2030 (\$2.350B):** \$217.375M/year (mixed operational/construction)
- **APLD ComputeCo 3 7.000% Notes due 2031 (\$1.590B):** \$111.300M/year (pre-service Bldg 4)
- **APLD ComputeCo 2 6.750% Notes due 2031 (\$2.150B):** \$145.125M/year (pre-service PF2)
- **Total APLD Project Debt Carrying Cost:** **\$473.800M/year** (of which **\$256.425M/year** is pre-service carry)
- **IREN Mackenzie Full-Capacity Coupon Equivalent:** **\$216.000M/year** (9.00% on \$2.4B committed capacity; full-draw equivalent scenario, not current carry).

### 5. Building 3 Partial-Operation Uncertainty & Proportional Contract-Value Scenario
Applied Digital's Form 10-K specifies that Building 2 (100 MW) is operational, Building 3 (150 MW) is *partially operational*, and Building 4 (150 MW) is under construction. Across the 400 MW campus (\$11.0B 15-year lease = \$733.33M/year total, or ~\$1.833M/MW/year):
- **Uncommissioned Capacity Range:** **150 MW to 300 MW** (37.5% to 75.0% of campus).
- **Proportional Annualized Contract-Value Scenario:**
  * **Building 4 Proportional Scenario (150 MW):** **\$275.0M/year** (\$137.5M per 6 months).
  * **Buildings 3 & 4 Proportional Scenario (300 MW):** **\$550.0M/year** (\$275.0M per 6 months).
  *(Note: This represents a proportional annualized scenario based on overall campus capacity, rather than a contract-literal building-level revenue floor/ceiling, preserving precise legal characterization.)*

### 6. Layered Synchronization Resilience Architecture
Financing structures deploy four distinct synchronization mechanisms to insulate borrowers against timing mismatches:
1. **Applied Digital Direct Parent Completion Guarantees:** Sponsor covenants providing direct protection against construction shortfalls, cost overruns, and mechanic liens (`CLM-APLD-017`).
2. **Escrow Gating:** Condition-precedent escrow accounts releasing funds only upon utility service agreement satisfaction (e.g. Goldman Sachs PF2 escrow released June 18, 2026).
3. **CoreWeave Springing Performance Guaranties:** Uncapped legal indemnities (`CLM-APLD-005`, `CLM-APLD-006`) backstopping tenant/SPV lease payment obligations *after* specified springing events (e.g. data hall delivery and lease commencement).
4. **Staged Equipment Funding Windows:** Availability periods expiring sequentially against equipment delivery milestones (e.g. IREN Mackenzie staged window through December 31, 2026).

---

## 1. Stage A: Attribution Layer Architecture

The Attribution Layer (`obligation_facility_links.parquet`) decomposes the contractual network into 51 link rows across all 47 obligations, establishing four discrete structural tiers:

```mermaid
flowchart TD
    subgraph CorporateTier["Tier 1: Corporate & Portfolio Unallocated ($39.358B Active)"]
        direction TB
        C1["CoreWeave Notes & DDTLs ($35.551B across 16 tranches)"]
        C2["TeraWulf Convertibles ($2.525B across 3 tranches)"]
        C3["APLD Corporate Converts & Residual ($506.7M)"]
        C4["Nebius Term Loan ($775M)"]
        C5["Supermicro Supplier Commitments ($34.2B)"]
    end

    subgraph MultiFacilityTier["Tier 2: Multi-Facility Customer Contracts (Unallocated Dollars)"]
        direction TB
        M1["OBL-CRWV-CORZ-COLOCATION-2024 (590 MW Leased across 5 Sites)<br>Topological Links: Denton, Dalton, Muskogee, Marble, Austin<br>Allocated Dollars: NULL (No Synthetic Pro-Ration)"]
    end

    subgraph DirectProjectTier["Tier 3: Single-Facility Project Financing ($6.090B Active Funded)"]
        direction TB
        P1["APLD ComputeCo 9.25% Notes ($2.35B) -> Polaris Forge 1 (Bldgs 2-3)"]
        P2["APLD ComputeCo 2 6.75% Notes ($2.15B) -> Polaris Forge 2"]
        P3["APLD ComputeCo 3 7.00% Notes ($1.59B) -> Polaris Forge 1 (Bldg 4)"]
    end

    subgraph EquipmentCapTier["Tier 4: Single-Facility Equipment Financing ($2.400B Committed)"]
        direction TB
        E1["IREN Mackenzie MFSA ($1.20B) -> Mackenzie Campus"]
        E2["IREN Mackenzie Notes ($1.20B) -> Mackenzie Campus"]
    end
```

---

## 2. Stage B: Physical Energization Alignment & Canonical Facts

Physical completion dimensions are curated into `data/processed/facility_completion_facts.parquet` with field-level claim provenance, eliminating synthetic defaults:

| Facility ID | Facility Name | Operator | Utility ESA (MW) | Utility Online (MW) | Critical IT (MW) | Service-Ready (MW) | Equipment Accepted | Status | Supporting Claims |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `FAC-APLD-POLARIS-FORGE-1` | Polaris Forge 1 | APLD | 350.0 | 60.0 | 400.0 | 100.0 | *Unknown* | `operational_and_expanding` | `CLM-PWR-MDU-001`, `CLM-PWR-APLD-001`, `CLM-APLD-004` |
| `FAC-APLD-POLARIS-FORGE-2` | Polaris Forge 2 | APLD | *Under review* | — | 200.0 | 0.0 | 0.0 | `under_construction` | `CLM-APLD-003`, `CLM-APLD-011`, `CLM-APLD-016` |
| `FAC-IREN-MACKENZIE` | Mackenzie Campus | IREN | 80.0 | 80.0 | 80.0 | 80.0 | *Unknown* | `operational_and_expanding` | `CLM-IREN-001`, `CLM-IREN-002` |
| `FAC-CORZ-DENTON` | Denton Campus | CORZ | 394.0 | 100.0 | 270.0 | 100.0 | — | `operational_and_expanding` | `CLM-PWR-CORZ-001`, `CLM-CORZ-001` |
| `FAC-CORZ-DALTON` | Dalton Facility | CORZ | 195.0 | — | — | — | — | `operational` | `CLM-PWR-CORZ-001` |
| `FAC-CORZ-MUSKOGEE` | Muskogee Facility | CORZ | 100.0 | — | — | — | — | `operational` | `CLM-PWR-CORZ-001` |
| `FAC-CORZ-MARBLE` | Marble Facility | CORZ | 117.0 | — | — | — | — | `operational` | `CLM-PWR-CORZ-001` |
| `FAC-CORZ-AUSTIN` | Austin Facility | CORZ | 20.0 | — | — | — | — | `operational` | `CLM-PWR-CORZ-001` |
| `FAC-WULF-LAKE-MARINER` | Lake Mariner | WULF | 226.0 | 226.0 | — | 226.0 | — | `operational_and_expanding` | `CLM-PWR-WULF-001` |
| `FAC-IREN-CHILDRESS` | Childress Facility | IREN | 750.0 | 650.0 | — | 650.0 | — | `operational_and_expanding` | `CLM-PWR-IREN-001` |
| `FAC-IREN-SWEETWATER-1` | Sweetwater 1 | IREN | 1400.0 | — | — | 0.0 | 0.0 | `under_construction` | `CLM-PWR-IREN-001` |
| `FAC-IREN-SWEETWATER-2` | Sweetwater 2 | IREN | 600.0 | — | — | 0.0 | 0.0 | `under_construction` | `CLM-PWR-IREN-001` |
| `FAC-NBIS-MANTSALA` | Mäntsälä DC | NBIS | 75.0 | 75.0 | 75.0 | 75.0 | 1.0 | `operational` | `CLM-PWR-NBIS-002` |
| `FAC-NBIS-LAPPEENRANTA` | Lappeenranta AI Factory | NBIS | 310.0 | — | — | 0.0 | 0.0 | `announced` | `CLM-PWR-NBIS-001` |

---

## 3. Publication Visualization: Capital Architecture & Campus Phasing

![Capital Allocation Architecture & Phasing](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/figures/capital_energization_gap.png)

Panel A demonstrates that active corporate debt (\$39.36B) dominates the capitalization profile, while project debt is bounded to \$6.090B at Applied Digital and committed equipment credit stands at \$2.400B at IREN Mackenzie. Panel B depicts Polaris Forge 1 phasing, displaying Building 3 (150 MW) as a hatched uncertainty band reflecting its partially operational status.

---

## 4. Stage C: Temporal Mismatch & Carrying Stress Scenarios

![Slippage Sensitivity & Resilience](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/figures/temporal_mismatch_timeline.png)

### Contractual Slippage Dynamics (Modeled Hypotheses)

| Slippage Window | APLD Total Debt Carry (\$M) | APLD Pre-Service Carry (\$M) | IREN Full-Capacity Coupon Eq. (\$M) | Proportional Delay Scenario Floor (\$M) | Proportional Delay Scenario Ceiling (\$M) | Modeled Qualitative Risk Tier | Layered Synchronization Resilience |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **6 Months Delay** | **\$236.9M** | **\$128.2M** | \$108.0M | **\$137.5M** | **\$275.0M** | *Modeled Hypothesis: Moderate* | PF1 completion guarantee shortfall funding active; PF2 escrow released Jun 18, 2026; CoreWeave springing lease guaranties backstop tenant obligations after delivery. |
| **12 Months Delay** | **\$473.8M** | **\$256.4M** | \$216.0M | **\$275.0M** | **\$550.0M** | *Modeled Hypothesis: High* | Carrying costs consume debt service reserves; Bldg 4 proportional scenario (\$275M) requires equity support; IREN Dec 31, 2026 staged window expires. |
| **18 Months Delay** | **\$710.7M** | **\$384.6M** | \$324.0M | **\$412.5M** | **\$825.0M** | *Modeled Hypothesis: Critical* | SPV debt default acceleration probability escalates without parent equity recapitalization or credit agreement waiver. |

---

## 5. Structural Capital Synchronization Resilience

Rather than leaving capital exposed to naked energization delays, market participants structure layered synchronization devices:

```
[ LAYER 1: DIRECT PARENT COMPLETION GUARANTEES ]
  Applied Digital Parent Completion Guarantees
        |
        +---> PF1 (Nov 20, 2025 Form 8-K): Mandatory obligation to fund construction shortfalls
        |     and remove liens to ensure achievement of Commencement Date.
        |
        +---> PF2 (March 10, 2026 Form 8-K): Direct completion guarantee ensuring completion
              of Construction Period and first Service Commencement Date.

[ LAYER 2: ESCROW HOLDING & CONDITION PRECEDENT GATING ]
  APLD ComputeCo 2 Notes ($2.15B Issued Mar 10, 2026)
        |
        v
  [ Escrow Account at Goldman Sachs ] ---> Gross proceeds held until execution of Electric Service Agreement
        |                                 (Condition Satisfied June 18, 2026; Form 10-K Note 8)
        v
  Conditions Deployment of Proceeds on Grid Interconnect (Debt Bears 6.75% Interest from Issuance; Escrow Gates Drawdowns, Not Coupon Accrual)

[ LAYER 3: STAGED EQUIPMENT ACCEPTANCE DRAWDOWN ]
  IREN Mackenzie Financing ($2.40B MFSA & Notes)
        |
        v
  [ Pro Rata Funding on Delivery & Acceptance ] ---> Borrows ONLY as GPU chips arrive & pass testing
        |                                             (Funding Availability Cliff: Dec 31, 2026)
        v
  Mitigates Capital Exposure Before Hardware Acceptance (Undrawn Capacity Incurs No 9% Note Coupon)

[ LAYER 4: TENANT SPRINGING LEASE GUARANTIES ]
  CoreWeave ELN-02 & ELN-03 Springing Indemnities
        |
        v
  [ Uncapped Tenant Legal Backstop ] ---> Springs to backstop tenant/SPV lease obligations AFTER data hall delivery
        |                                (Class C Reference Proxy: $4.125B on Building 3)
        v
  Insulates Project SPV Equity from Post-Delivery Tenant Default (Does NOT assume pre-delivery construction overruns)
```

---

## 6. Comparative Risk-Transfer Analysis: Tracing a 12-Month Delay Shock Across PF1, PF2, and Mackenzie

When physical delivery or energization lags capital formation, which contractual protections actually absorb the timing mismatch—and where does residual risk land after those protections are applied?

To maintain strict epistemic integrity, we divide this analysis into **Contractually Established Mechanics** (facts verified by Class A SEC filings) and **Modeled Residual-Loss Hypotheses** (analytical projections of post-protection default propagation).

---

### 6.1 Contractually Established Mechanics (What Filings Prove)

The audited primary filings establish three distinct structural archetypes:

| Structure & Facility | Instrument, Pricing & Status | Contractual Capital Commitment | Debt Service & Carrying Reality | Contractually Established Protection & Recourse | Primary Claims |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PF1**<br>*(Polaris Forge 1, ND)* | **\$2.350B Senior Notes @ 9.250%** due Dec 15, 2030.<br>Operating & expanding (Bldg 2 100 MW online; Bldg 3 150 MW partial; Bldg 4 under constr.). | **100% funded up front** on Nov 20, 2025; held in project trust accounts. | **\$217.375M/year cash carry** accrues continuously from issuance. | Note proceeds funded a Debt Service Reserve Account (DSRA); Applied Digital parent has mandatory obligation to fund shortfalls if project funds are insufficient to achieve commencement milestone. | `CLM-APLD-010`, `CLM-APLD-017` |
| **PF2**<br>*(Polaris Forge 2, ND)* | **\$2.150B Senior Notes @ 6.750%** due 2031.<br>Under construction (200 MW critical IT). | **100% funded up front** on March 10, 2026. Proceeds were escrow-gated at Goldman Sachs until ESA execution (satisfied June 18, 2026). | **\$145.125M/year cash carry** accrues from March 10, 2026 issuance date. *(Escrow gated proceeds deployment, not coupon accrual).* | Project accounts include a DSRA; Applied Digital parent provides completion support ensuring completion of Construction Period and first Service Commencement Date. | `CLM-APLD-011`, `CLM-APLD-016`, `CLM-APLD-018` |
| **Mackenzie**<br>*(Mackenzie, BC)* | **Up to \$2.400B Committed Credit** (\$1.2B MFSA + \$1.2B Notes @ 9.000%).<br>Operating facility (80 MW IT online). | **Staged milestone draw:** funds borrow pro rata as GPU hardware is delivered and accepted through Dec 31, 2026. *(Amount drawn at observation date is unknown).* | **9.000% coupon applies strictly to drawn debt.** Undrawn commitments incur commitment fees, not 9% interest carry. *(Total dollar carry cannot be assumed zero without drawn amount).* | IREN parent company guarantees payment obligations; lenders retain contractual recourse against the company and equipment collateral if cash flows are insufficient. | `CLM-IREN-001`, `CLM-IREN-002`, `0001878848-26-000052` |

#### The Primary Comparative Finding:
$$\textbf{PF1 and PF2 mitigate physical-delivery risk primarily after capital is committed (via reserves, escrow conditions, and sponsor completion support), whereas Mackenzie mitigates it partly before capital is drawn (via acceptance-conditioned funding windows).}$$

---

### 6.2 Four-Tier Contractual Protection Taxonomy

Across these project and equipment facilities, market participants construct four functional protection layers:

1. **Preventive Protections (Pre-Deployment Gating):**
   - *Mechanic:* Contractually prevents capital from deploying into physical assets until milestone prerequisites are certified.
   - *Evidence:*
     - **Mackenzie Staged Acceptance:** Lenders fund only upon delivery and acceptance testing of operational GPU servers through Dec 31, 2026 (`CLM-IREN-001`).
     - **PF2 Escrow Gating:** Gross note proceeds withheld from construction accounts until electric service agreement was formally executed (`CLM-APLD-016`).
2. **Buffering Protections (Liquidity Reserves):**
   - *Mechanic:* Pre-funded cash accounts absorb temporary mismatches between debt service and revenue generation.
   - *Evidence:*
     - **PF1 DSRA:** Form 8-K confirms proceeds funded a dedicated debt service reserve account.
     - **PF2 Project Accounts:** Indenture covenants maintain project-level DSRAs and capitalized interest reserves.
3. **Transfer Protections (Third-Party Balance Sheet Backstops):**
   - *Mechanic:* Reallocates financial shortfalls to a distinct corporate balance sheet.
   - *Evidence:*
     - **Applied Digital Completion Guarantees:** Sponsor parent guarantees completion funding if project accounts run dry (`CLM-APLD-017`, `CLM-APLD-018`).
     - **CoreWeave Springing Lease Guaranties:** Uncapped indemnities (`CLM-APLD-005`, `CLM-APLD-006`) backstopping tenant SPV lease obligations *after* data hall delivery.
4. **Recovery Protections (Post-Default Lender Remedies):**
   - *Mechanic:* Legal entitlements granting credit providers rights to seize assets or pursue parent entities following an un-cured default.
   - *Evidence:*
     - **IREN Parent Payment Guarantee & Collateral:** Lenders possess recourse against IREN corporate and security interests in the underlying server hardware (`0001878848-26-000052`).
     - **APLD ComputeCo Indenture Liens:** Noteholders hold senior secured mortgages on project land, electrical substation assets, and colocation contracts.

---

### 6.3 Modeled Residual-Loss Hypotheses: Tracing a 12-Month Delay Shock

To evaluate the resilience of these structures under stress, we trace a hypothetical 12-month physical energization or hardware supply shock. These conclusions represent **modeled hypotheses**, not guaranteed contractual outcomes:

1. **Who writes the first check?**
   - **PF1 / PF2:** The **Applied Digital parent balance sheet** writes the first check under its completion covenants if project accounts run short of construction funds, while capitalized interest reserves and DSRAs absorb immediate coupon requirements.
   - **Mackenzie:** **Nobody writes a debt check on unaccepted chips.** Undrawn capacity incurs no note coupon. However, for any capital already drawn (amount unknown), IREN parent cash flows must service the 9% coupon.
2. **Can lenders stop funding?**
   - **PF1 / PF2:** **No.** Proceeds were 100% funded up front; noteholders have no mechanism to withhold committed cash.
   - **Mackenzie:** **Yes.** Blue Owl and PIMCO are contractually excused from advancing funds if hardware fails acceptance testing, or if the December 31, 2026 window lapses.
3. **Do lenders continue receiving interest?**
   - **PF1 / PF2:** **Yes.** Noteholders receive coupon yield on schedule (\$217.4M/yr on PF1; \$145.1M/yr on PF2; \$111.3M/yr on PF1 Bldg 4), shielded by project reserves and parent completion support.
   - **Mackenzie:** Lenders earn 9.00% yield only on drawn principal. On undrawn commitments, lenders earn commitment fees but face reinvestment yield drag.
4. **Contractual cure rights vs. systemic limits:**
   - **PF1 / PF2:** Applied Digital possesses indenture cure rights and equity injection mechanisms. *However, the public filings do not establish that APLD has an unbounded right to cure mechanics liens, replace EPC contractors, or extend long-stop dates indefinitely without noteholder consent.*
   - **Mackenzie:** IREN has until Dec 31, 2026 to resolve supply chain delivery bottlenecks. If unaccepted, the facility commitment lapses; *whether cross-default provisions propagate to other corporate debt depends on confidential credit terms not disclosed in SEC summaries.*
5. **Protection expiration sequence:**
   - **PF1 / PF2:** Project-level DSRAs and capitalized interest reserves (typically 6–12 months of debt service) deplete first, shifting 100% of carrying costs to the sponsor parent balance sheet.
   - **Mackenzie:** The staged drawdown availability window expires (December 31, 2026).
6. **Where does residual economic loss pool?**
   - **PF1 / PF2 (Modeled Hypothesis):** Residual risk pools heavily on the **Applied Digital sponsor parent balance sheet**. Because CoreWeave's springing lease guaranties only backstop lease obligations *after* data hall delivery, CoreWeave bears zero direct construction-delay carrying costs on unenergized space. If delay exhausts sponsor parent liquidity, residual losses shift to noteholders via debt restructuring.
   - **Mackenzie (Modeled Hypothesis):** Residual loss does *not* land solely on hardware vendors. Because IREN parent guarantees payment obligations and pledges equipment collateral, credit lenders retain legal claims against IREN corporate if drawn cash flows fail. On undrawn capacity, loss is shared between vendor inventory carrying costs and IREN's lost equity opportunity cost.

---

### 6.4 Core Research Synthesis: Do Contractual Protections Eliminate Risk, or Merely Move It?

The central research finding of Task 021 is that **contractual protections do not eliminate temporal mismatch risk; they convert one large physical delivery risk into a sequence of conditional exposures distributed across counterparties:**

```
[ PHYSICAL DELAY SHOCK (12 Months) ]
                │
                ▼
      [ PREVENTIVE GATING ] ---------> Stops capital draw (Mackenzie staged draw; PF2 escrow)
                │ (if capital committed)
                ▼
       [ BUFFERING RESERVES ] -------> Absorbs early carry (PF1/PF2 capitalized interest & DSRA)
                │ (when reserves deplete)
                ▼
      [ SPONSOR TRANSFER ] ----------> Absorbs overruns & debt service (APLD Parent Completion Guarantee)
                │ (if delay outlasts sponsor liquidity)
                ▼
       [ LENDER RECOVERY ] ----------> Foreclosure & restructuring (Indenture liens, Equipment collateral)
```

#### The Hidden Common Nexus (The Systemic JOIN):
When evaluated in isolation, each contract appears insulated:
- The noteholder sees a parent completion guarantee and a DSRA.
- The tenant sees an uncommenced lease with no rent obligation until handover.
- The sponsor sees long-term tenant revenue commitments and executed utility capacity.
- The equipment lender sees staged acceptance gating and parent repayment guarantees.

However, these protections are structurally coupled. In a systemic shock, multiple independent instruments converge onto the **same underlying risk nodes**:
1. **The Shared Anchor Customer:** CoreWeave represents the ultimate source of operating cash flow for both Ellendale (APLD) and Denton/Dalton/Muskogee (CORZ).
2. **The Regional Power Milestone:** Commercial operation across all buildings depends on a common utility energization schedule (e.g. MDU 350 MW transmission expansion).
3. **The Common Sponsor Liquidity Pool:** Applied Digital's parent balance sheet simultaneously backstops PF1 completion shortfalls, PF2 construction covenants, and corporate convertibles.

If a shared power or tenant milestone experiences systemic delay, the sequence of conditional transfers collapses back into a concentrated exposure on the sponsor's equity buffer.

---

### 6.5 Technical Limitations & Bitemporal Query Invariant

> [!NOTE]
> **Technical Architecture Limitation (`facility_completion_facts.parquet`):**
> `facility_completion_facts.parquet` is structured as a **current-state canonical snapshot** with field-level claim IDs, not a fully normalized historical bitemporal fact table.
> Different attributes in a single facility row became public at different times (e.g., APLD 10-K filed July 29, 2026 vs. MDU 10-Q filed August 6, 2026), while the row possesses a single `publicly_known_from` timestamp set to the latest constituent filing (`2026-08-06`).
> For current-state analysis and cross-sectional attribution, this design is rigorous and look-ahead-free. However, researchers conducting historical point-in-time queries (e.g., *"What could an investor know about PF1 completion on February 1, 2026?"*) must query the underlying bitemporal claims (`evidence_claims.parquet`) and obligation facts (`obligation_facts.parquet`) directly, rather than assuming the facility completion snapshot row is historically bitemporal.

---

## 7. Conclusion & Methodological Certification

By enforcing ADR-021.1a:
1. **Source-Registry Auto-Binding Certified:** All 68 Class A SEC claims bind strictly to their registered source document in `data/raw/sec/source_registry.json`. Global searches and cross-filing false positives are completely eliminated.
2. **Re-segmented Funded Project Debt:** Certified at **\$3.740B pre-service funded debt** and **\$2.350B mixed operational exposure**, ending the over-simplified 100% "before service" characterization.
3. **Building 3 Partial-Operation Uncertainty Explicit:** Contract-value delay exposure is formally bounded between a **\$275.0M/year floor scenario** (Building 4) and a **\$550.0M/year ceiling scenario** (Buildings 3 & 4), across an uncommissioned capacity range of 150 MW to 300 MW.
4. **Canonical Evidence Table:** `facility_completion_facts.parquet` provides field-level claim provenance and eliminates hardcoded Python dictionaries from the analysis engine, creating a single, fully-tested source of truth.
5. **Contractual Protection Taxonomy Certified:** Replaced speculative assertions with an evidence-grounded four-tier framework (Preventive, Buffering, Transfer, Recovery) and explicitly delineated contractually proven mechanics from modeled residual-loss hypotheses.
6. **Permanent Ontology Freeze:** The data model, schema definitions, and company scope are permanently frozen at commit `42f9a74`. All subsequent research tasks evaluate substantive economic questions against this verified observatory.
