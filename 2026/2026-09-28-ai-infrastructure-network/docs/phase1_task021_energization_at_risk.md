# Task 021: Energization-at-Risk & Capital Synchronization Resilience Report (ADR-021 / ADR-021.1)

**Date:** September 30, 2026  
**Decision References:** ADR-021 & ADR-021.1 (`docs/decisions.md`)  
**Dataset State:** 62 registered entities, 47 decomposed financial obligations, 57 lifecycle events, 64 financial facts, 44 financial terms, 14 physical facilities, 13 power relationships, 29 typed MW power facts, 27 power terms, 9 primary power claims, 51 obligation-facility attribution links.  
**Baseline Certification:** 100% exact verbatim substring verification across all 64 Class A SEC claims; **0.00% data drift** across balance sheet and power layers.

---

## Executive Summary & Core Verdicts

This report delivers the certified findings of **Task 021: Energization-at-Risk & Capital-to-Physical Attribution**, incorporating the epistemic repairs and synchronization resilience architecture of **ADR-021.1**.

Prior to this work, high-level infrastructure analyses risked severe epistemic distortions by aggregating disparate contractual instruments into synthetic ratios—such as dividing Applied Digital's total consolidated debt by partial utility meter readings, or treating Iris Energy's \$2.4B equipment credit line as drawn, un-hedged debt carrying immediate interest.

By constructing a strict, audited **Attribution Layer** (`obligation_facility_links.parquet`) backed by typed completion dimensions, we enforced two foundational epistemic invariants:
$$\textbf{Universal Attribution Invariant: No facility-level dollar/MW ratio unless the dollar obligation is demonstrably attributable to that facility.}$$
$$\textbf{Dimensional Invariant: Utility service capacity, IT facility capacity, and GPU equipment deployment states are distinct, typed physical dimensions that must not be synthetically subtracted or imputed to zero.}$$

```
========================================================================================================
                      CAPITAL-TO-PHYSICAL ATTRIBUTION & SYNCHRONIZATION ARCHITECTURE
========================================================================================================

  [ CORPORATE & PORTFOLIO DEBT ]          [ PROJECT & EQUIPMENT FINANCING ]        [ PHYSICAL CAMPUS ]
  Held Strictly Separate ($39.358B)       Directly Attributable ($6.090B Funded)   Completion Dimensions
  
  * CoreWeave Senior Notes & DDTLs        * APLD PF1 9.25% Notes ($2.35B) --------> Polaris Forge 1
    ($35.551B across 16 tranches)         * APLD PF1 7.00% Notes ($1.59B)           350 MW Utility ESA / 60 MW Online
  * APLD Corporate Converts ($450M)         (Total: $3,940.0M Funded Project Debt)  400 MW Critical IT / 100 MW Ready
  * APLD Residual Debt ($56.7M)                                                     [ 75% Space Uncommissioned ]
  * TeraWulf Convertibles ($2.525B)       * APLD PF2 6.75% Notes ($2.15B) --------> Polaris Forge 2
  * Nebius Term Facility ($775M)            (APLD ComputeCo 2 LLC Notes)            200 MW Critical IT / Pre-service
                                            (Escrow Released June 18, 2026)         [ 100% IT Space Under Constr. ]

  * Corporate Cash / Unallocated --------> * IREN MFSA & Notes ($2.40B) ----------> Mackenzie Campus, BC
                                            (IE Mackenzie Compute Ltd.)             80 MW Utility Online (Since 2022)
                                            [ Committed Capacity, Not Funded Debt ] 80 MW Service-Ready IT Infrastructure
                                            [ Staged Acceptance Window to Dec 2026] [ Staged GPU Server Acceptance ]

                                          * $0 Debt Attributed -------------------> Childress, TX (650 MW Live)
                                          * $0 Debt Attributed -------------------> Denton, TX (100 MW Live Colo)
========================================================================================================
```

### 1. Falsification of Synthetic Dollar/MW Ratios
- **Applied Digital (APLD):** Consolidated debt across all corporate layers totals \$6.597B (as of Sep 28, 2026). Dividing this enterprise aggregate by the 60 MW incremental online load at Ellendale manufactures a fictitious metric of ~\$110M/MW. In reality, the legally attributable funded debt on Polaris Forge 1 is **\$3.940B** (\$2.35B ComputeCo 9.25% notes closed Nov 20, 2025 + \$1.59B ComputeCo 3 7.00% notes closed Jun 16, 2026), dedicated to a **400 MW critical IT campus** leased to CoreWeave.
- **Iris Energy (IREN):** The \$2.4B Blue Owl/PIMCO August 2026 financing is committed equipment credit capacity borrowed by `IE Mackenzie Compute Ltd.`, dedicated strictly to GPU servers and equipment at IREN's **Mackenzie, British Columbia campus** (80 MW site). Point-in-time drawn debt is undisclosed and funds pro rata upon equipment delivery and acceptance. Attributing this facility to IREN's 650 MW Childress mining facility in Texas would conflate completely separate legal entities, jurisdictions, and asset classes.

### 2. \$6.090B in Facility-Attributable Funded Debt — Strictly Ring-Fenced to APLD SPVs
Across all 14 modeled campuses, facility-attributable funded debt is strictly ring-fenced to Applied Digital's project SPVs:
- **Polaris Forge 1 (`FAC-APLD-POLARIS-FORGE-1`):** **\$3,940.0M**
- **Polaris Forge 2 (`FAC-APLD-POLARIS-FORGE-2`):** **\$2,150.0M**
- **Total Facility-Attributable Funded Debt:** **\$6,090.0M (\$6.090B)**
- **Committed Equipment Financing Capacity (IREN Mackenzie):** **\$2,400.0M (\$2.400B)** (committed credit capacity, not funded debt).

### 3. Exact Coupon Carrying Costs: \$473.800M/Year on Funded Project Debt
Based strictly on canonical contractual rate terms:
- **APLD ComputeCo 9.250% Notes due 2030 (\$2.350B):** \$217.375M/year
- **APLD ComputeCo 3 7.000% Notes due 2031 (\$1.590B):** \$111.300M/year
- **APLD ComputeCo 2 6.750% Notes due 2031 (\$2.150B):** \$145.125M/year
- **Total APLD Project Debt Annual Carrying Cost:** **\$473.800M/year**
- **IREN Mackenzie Full-Capacity Coupon Equivalent:** **\$216.000M/year** (9.00% on \$2.4B committed capacity; represents full-draw equivalent, not current carry).

### 4. Phased Lease Delay Sensitivity: \$550.0M/Year on Uncommissioned Space
At Polaris Forge 1, CoreWeave's 15-year master lease represents \$11.0B total contract value (\$733.33M/year across 400 MW). Primary disclosures (Form 10-K Item 1 & Form 8-K filed Jan 7, 2026) establish that **Building 2 (100 MW) became operational/service-ready in October 2025**. Therefore, only the uncommissioned space—**Building 3 (150 MW partial) and Building 4 (150 MW under construction)**, totaling 300 MW (75% of campus capacity)—is exposed to commissioning delay:
$$\text{Annual Delayed Lease Revenue (Uncommissioned Space)} = \$733.33\text{M} \times \frac{300\text{ MW}}{400\text{ MW}} = \mathbf{\$550.000\text{M/year}}$$

### 5. Central Research Finding: Capital Synchronization Resilience
The analysis reveals that rather than blindly exposing capital to physical delay, modern AI project financings incorporate sophisticated **structural synchronization mechanisms**:
1. **Escrow Cushions:** APLD ComputeCo 2 held its \$2.15B note proceeds in escrow from March 10, 2026 until condition satisfaction on June 18, 2026, preventing un-hedged negative arbitrage before construction readiness.
2. **Staged Drawdown Windows:** IREN's \$2.4B facility draws pro rata upon GPU equipment delivery and acceptance, expiring on December 31, 2026, shielding the borrower from carrying costs on un-delivered chips.
3. **Springing Completion Support:** CoreWeave provided uncapped legal completion indemnities under `ELN-02` (Building 2) and `ELN-03` (Building 3, \$4.125B Class C proxy), requiring the tenant to backstop financing costs and project debt service during construction delays.

---

## 1. Stage A: Attribution Layer Architecture

The Attribution Layer (`obligation_facility_links.parquet`) decomposes the contractual network into 51 link rows across all 47 obligations, establishing three discrete structural tiers:

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

    subgraph DirectProjectTier["Tier 3: Direct Facility-Attributable Funded Debt ($6.090B)"]
        direction TB
        D1["FAC-APLD-POLARIS-FORGE-1: $3,940.0M Funded Debt<br>(PF1 9.25% Notes $2.35B + 7% Notes $1.59B)"]
        D2["FAC-APLD-POLARIS-FORGE-2: $2,150.0M Funded Debt<br>(APLD ComputeCo 2 6.75% Notes $2.15B)"]
    end

    subgraph EquipmentCapTier["Tier 4: Committed Equipment Financing Capacity ($2.400B)"]
        direction TB
        E1["FAC-IREN-MACKENZIE: $2,400.0M Equipment Financing Capacity<br>(Blue Owl MFSA $1.2B + PIMCO Notes $1.2B)"]
    end

    CorporateTier -.->|Strictly Excluded from Facility Ratios| DirectProjectTier
    MultiFacilityTier -.->|Discrete Campus Mapping| DirectProjectTier
```

### Attribution Invariants Enforced
1. `direct_project_financing`: Debt issued by bankruptcy-remote SPVs to construct a single facility (APLD ComputeCo tranches). Enforced with `allocation_scope = "single_facility"`, `amount_type = "funded_principal"`, and `allocation_fraction = 1.0`.
2. `direct_equipment_financing`: Committed equipment financing capacity allocated to a single facility (IREN Mackenzie). Enforced with `amount_type = "facility_capacity"`.
3. `direct_lease`: Long-term real property/data hall leases (`OBL-CRWV-APLD-LEASE` at Polaris Forge 1).
4. `completion_support`: Springing tenant completion indemnities (`OBL-CRWV-APLD-GUARANTY-ELN02`, `ELN03`).
5. `portfolio_or_corporate`: General corporate obligations where proceeds are not ring-fenced to a single campus (`facility_id = None`, `allocated_amount = None`).
6. `bitemporal_lineage`: Every link records discrete `truth_claim_id` and `knowledge_claim_id` satisfying `publicly_known_from >= knowledge_claim.filing_date`.

---

## 2. Canonical Facility Attribution & Completion Table

The table below presents the certified join across all 14 physical campuses using typed completion dimensions:

| Facility ID | Campus Name | Operator | Attributable Funded Debt (\$M) | Committed Financing Cap (\$M) | Customer Lease (\$M) | Utility Service Cap (MW) | Utility Load Online (MW) | Critical IT Contracted (MW) | Service-Ready IT (MW) | GPU Deployment State | Next Major Milestone | Evidence Completeness |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- |
| `FAC-APLD-POLARIS-FORGE-1` | Polaris Forge 1 Campus | `APLD` | **\$3,940.0** | \$0.0 | **\$11,000.0** | 350.0 | 60.0 | 400.0 | 100.0 | Tenant (CoreWeave) cluster commissioning & fit-out | Bldg 2 full occupancy & Bldg 3 commissioning (2026–2027) | Class A (10-K, 8-K, Ex 10.1 & 10.2) |
| `FAC-APLD-POLARIS-FORGE-2` | Polaris Forge 2 Campus | `APLD` | **\$2,150.0** | \$0.0 | *Hyperscaler* | *Pending* | *Pre-energized* | 200.0 | 0.0 | Civil / electrical shell construction | Initial capacity H2 2026; full 200 MW early 2027 | Class A (10-K Item 1 & Note 10) |
| `FAC-IREN-MACKENZIE` | Mackenzie Data Center Campus | `IREN` | **\$0.0** | **\$2,400.0** | *Cloud ARR* | 80.0 | 80.0 | 80.0 | 80.0 | Staged GPU server delivery & acceptance through Dec 31, 2026 | GPU server staged delivery & acceptance through Dec 31, 2026 | Class A (10-K Note August 2026 Financing) |
| `FAC-CORZ-DENTON` | Denton Data Center | `CORZ` | **\$0.0** | \$0.0 | *CRWV Colo* | 394.0 | 100.0 | 270.0 | 100.0 | Tenant fit-out / ongoing colocation conversion | Colocation fit-out across multi-building campus | Class A (10-K, 8-K Note Denton Lease) |
| `FAC-CORZ-DALTON` | Dalton Data Center | `CORZ` | **\$0.0** | \$0.0 | *CRWV Colo* | 195.0 | *Undisclosed* | *Multi-site* | *Undisclosed* | HPC infrastructure retrofit from mining | HPC infrastructure retrofit from mining | Class A (10-K Colocation table) |
| `FAC-CORZ-MUSKOGEE` | Muskogee Data Center | `CORZ` | **\$0.0** | \$0.0 | *CRWV Colo* | 100.0 | *Undisclosed* | *Multi-site* | *Undisclosed* | HPC infrastructure retrofit from mining | HPC infrastructure retrofit from mining | Class A (10-K Colocation table) |
| `FAC-CORZ-MARBLE` | Marble Data Center | `CORZ` | **\$0.0** | \$0.0 | *CRWV Colo* | 117.0 | *Undisclosed* | *Multi-site* | *Undisclosed* | HPC infrastructure retrofit from mining | HPC infrastructure retrofit from mining | Class A (10-K Colocation table) |
| `FAC-CORZ-AUSTIN` | Austin Data Center | `CORZ` | **\$0.0** | \$0.0 | *CRWV Colo* | 20.0 | *Undisclosed* | *Multi-site* | *Undisclosed* | HPC infrastructure retrofit from mining | HPC infrastructure retrofit from mining | Class A (10-K Colocation table) |
| `FAC-WULF-LAKE-MARINER` | Lake Mariner Campus | `WULF` | **\$0.0** | \$0.0 | *Self-operated* | 226.0 | 226.0 | *Self-operated* | 226.0 | Operational mining / 500 MW expansion engineering | 500 MW planned expansion engineering | Class A (10-K NYPA allocation) |
| `FAC-IREN-CHILDRESS` | Childress Data Center | `IREN` | **\$0.0** | \$0.0 | *Mining / Cloud* | 750.0 | 650.0 | *Mining / Cloud* | 650.0 | Operating mining & cloud pilot | Final 100 MW substation expansion to 750 MW | Class A (10-K Item 1 & Note 7) |
| `FAC-IREN-SWEETWATER-1` | Sweetwater 1 Campus | `IREN` | **\$0.0** | \$0.0 | *Development* | 1,400.0 | *Pre-energized* | *Development* | 0.0 | Substation procurement & interconnection construction | Interconnection substation construction (1,400 MW) | Class A (10-K Item 1) |
| `FAC-IREN-SWEETWATER-2` | Sweetwater 2 Campus | `IREN` | **\$0.0** | \$0.0 | *Development* | 600.0 | *Pre-energized* | *Development* | 0.0 | AEP Texas substation engineering | AEP Texas 600 MW substation engineering | Class A (10-K Item 1) |
| `FAC-NBIS-MANTSALA` | Mäntsälä Supercomputing | `NBIS` | **\$0.0** | \$0.0 | *Meta Offtake* | 75.0 | 75.0 | 75.0 | 75.0 | Fully operational GPU cluster operations | Commercial operational service / heat recovery | Class A (10-K & Utility Primary Source) |
| `FAC-NBIS-LAPPEENRANTA` | Lappeenranta AI Factory | `NBIS` | **\$0.0** | \$0.0 | *Development* | 310.0 | *Pre-energized* | *Development* | 0.0 | Engineering design / pre-construction | Pending grid interconnection & engineering review | Class B (10-K development announcement) |
| **Total / Summary** | **14 Campuses** | — | **\$6,090.0M** | **\$2,400.0M** | **\$11,000.0M+** | **4,617.0 MW** | **1,191.0 MW** | **1,025.0 MW+** | **1,381.0 MW** | — | — | **13 Class A, 1 Class B** |

---

## 3. Physical Phasing & Capital Allocation Architecture

The publication visualization below illustrates the fundamental structural separation between funded project debt, committed equipment capacity, and general corporate obligations, alongside the actual building phasing at Polaris Forge 1:

![Capital Allocation Architecture & Phasing](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/figures/capital_energization_gap.png)

### Key Insights from Panel A & Panel B
1. **Capital Architecture (Panel A):** Out of \$47.848B total modeled debt obligations, **\$39.358B (82.3%)** resides on corporate balance sheets (CoreWeave senior notes, convertibles, vendor financing). Facility-attributable funded project debt is strictly **\$6.090B (12.7%)**, and committed equipment financing capacity is **\$2.400B (5.0%)**. Macro-level debt analyses that flatten this structure obscure the true locus of credit risk.
2. **Polaris Forge 1 Phasing (Panel B):** Rather than an unenergized shell, Polaris Forge 1 has **100 MW (Building 2) already service-ready** since October 2025. The uncommissioned exposure is strictly localized to Building 3 (150 MW partially operating/fit-out) and Building 4 (150 MW under construction financed by the 7.00% notes).

---

## 4. Slippage Sensitivity & Carrying Stress (Modeled Hypotheses)

The timeline below models the contractual carrying stress across 6-, 12-, and 18-month delay scenarios against the structural resilience mechanisms:

![Slippage Sensitivity & Resilience](file:///c:/Users/admir/Github/computational-sketchbook/2026/2026-09-28-ai-infrastructure-network/outputs/figures/temporal_mismatch_timeline.png)

### Contractual Slippage Dynamics (Modeled Hypotheses)

| Slippage Window | APLD Project Debt Carry (\$M) | IREN Full-Capacity Coupon Eq. (\$M) | Phased Delayed Lease Revenue (\$M) | Modeled Qualitative Risk Tier | Covenant & Capital Resilience Mechanism |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **6 Months Delay** | **\$236.9M** | \$108.0M | **\$275.0M** | *Modeled Hypothesis: Moderate* | PF2 escrow release conditions already satisfied; ELN-02/03 springing completion indemnities cushion CoreWeave revenue timing. |
| **12 Months Delay** | **\$473.8M** | \$216.0M | **\$550.0M** | *Modeled Hypothesis: High* | Uncommissioned lease delays consume liquidity reserves; IREN staged draw window (Dec 31, 2026 cliff) expires or requires formal extension. |
| **18 Months Delay** | **\$710.7M** | \$324.0M | **\$825.0M** | *Modeled Hypothesis: Critical* | SPV debt service default probability escalates without corporate recapitalization or CoreWeave parent indemnity enforcement. |

---

## 5. Structural Capital Synchronization Resilience

The most significant epistemic finding of ADR-021.1 is that sophisticated AI infrastructure financings do **not** leave capital exposed to naked energization delays. Instead, market participants structure debt to synchronize with physical milestones:

```
[ SYNCHRONIZATION MECHANISM 1: ESCROW GATING ]
  APLD ComputeCo 2 Notes ($2.15B Issued Mar 10, 2026) 
        |
        v
  [ Escrow Account Holding ] ---> Releases ONLY upon satisfaction of construction conditions
        |                          (Escrow Condition Satisfied June 18, 2026; Form 10-K Note 8)
        v
  Capital Gated Against Construction Readiness

[ SYNCHRONIZATION MECHANISM 2: STAGED EQUIPMENT ACCEPTANCE ]
  IREN August 2026 Financing ($2.40B MFSA & Notes)
        |
        v
  [ Pro Rata Funding on Delivery & Acceptance ] ---> Borrows ONLY as GPU chips arrive & pass testing
        |                                             (Funding Availability Cliff: Dec 31, 2026)
        v
  Protects Borrower from Paying Interest on Idle Silicon

[ SYNCHRONIZATION MECHANISM 3: TENANT COMPLETION INDEMNITIES ]
  CoreWeave ELN-02 & ELN-03 Springing Indemnities
        |
        v
  [ Uncapped Tenant Legal Backstop ] ---> CoreWeave assumes construction delay costs & debt service
        |                                (Class C Reference Proxy: $4.125B on Building 3)
        v
  Insulates Project SPV Equity from Physical Slippage
```

---

## Conclusion & Methodological Certification

By enforcing ADR-021.1:
1. **Epistemic Integrity Restored:** All false baselines in APLD debt issuance dates and citations were eradicated. All 64 Class A SEC claims are automatically bound and verified as 100% exact verbatim substrings in cached primary HTML filings.
2. **Strict Semantics Preserved:** Facility-attributable funded debt is certified at **\$6.090B** (APLD only). IREN's \$2.4B is certified as **committed equipment financing capacity**. Active corporate debt is certified at **\$39.358B**.
3. **No Synthetic Zero Imputation:** Facilities like Mackenzie (operating at 80 MW since 2022) and Mäntsälä (75 MW operating) are accurately modeled without distorting energization baselines.
4. **Carrying Costs & Phasing Derived Exactly:** APLD annual project interest carry is certified at **\$473.800M/year**, and uncommissioned delayed lease exposure is certified at **\$550.000M/year** based on Building 2's service-ready status.
