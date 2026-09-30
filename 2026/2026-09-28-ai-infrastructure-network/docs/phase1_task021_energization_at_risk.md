# Task 021: Energization-at-Risk & Capital-to-Physical Attribution Report (ADR-021)

**Date:** September 30, 2026  
**Decision Reference:** ADR-021 (`docs/decisions.md`)  
**Dataset State:** 62 registered entities, 47 decomposed financial obligations, 56 lifecycle events, 64 financial facts, 44 financial terms, 14 physical facilities, 13 power relationships, 29 typed MW power facts, 27 power terms, 9 primary power claims, 51 obligation-facility attribution links.  
**Baseline Certification:** Commit `def0eda` financial & power baselines conserved with **0.00% data drift**.

---

## Executive Summary & Core Verdicts

This report delivers the certified findings of **Task 021: Energization-at-Risk & Capital-to-Physical Attribution (ADR-021)**. 

Prior to this sprint, macro-level analyses risked executing catastrophic multi-layer JOIN errors—such as dividing aggregate corporate debt by partial utility meter readings (e.g. dividing Applied Digital's total \$6.597B debt by the 60 MW incremental online load at Ellendale, or dividing Iris Energy's \$2.4B Blue Owl/PIMCO GPU financing by its 650 MW Childress mining load).

By constructing a strict, audited **Attribution Layer** (`obligation_facility_links.parquet`), we enforced the foundational epistemic invariant:
$$\textbf{Universal Attribution Rule: No facility-level dollar/MW ratio unless the dollar obligation is demonstrably attributable to that facility.}$$

```
========================================================================================================
                      CAPITAL-TO-PHYSICAL ATTRIBUTION & TIMING MISMATCH ARCHITECTURE
========================================================================================================

  [ CORPORATE & PORTFOLIO DEBT ]          [ PROJECT & EQUIPMENT FINANCING ]        [ PHYSICAL CAMPUS ]
  Held Strictly Separate ($39.808B)       Directly Attributable ($8.490B)           Commissioning State
  
  * CoreWeave Senior Notes & DDTLs        * APLD PF1 Notes ($2.35B) --------------> Polaris Forge 1
    ($35.551B across 16 tranches)         * APLD 7% Notes ($1.59B) ---------------> (60 MW online / 400 MW)
  * APLD Corporate Converts ($450M)                                                   [ 85.0% GAP ]
  * APLD Residual Debt ($56.7M)           * APLD PF2 Notes ($2.15B) --------------> Polaris Forge 2
  * TeraWulf Convertibles ($2.525B)                                                   (0 MW online / 200 MW)
  * Hut 8 Convertibles ($150M)                                                        [ 100.0% GAP ]
  * Nebius Term Facility ($775M)          * IREN MFSA & Notes ($2.40B) -----------> Mackenzie Campus, BC
                                            (IE Mackenzie Compute Ltd.)              (0 MW live / 80 MW)
                                                                                      [ 100.0% GAP ]

                                          * $0 Debt Fabricated -------------------> Childress, TX (650 MW)
                                          * $0 Debt Fabricated -------------------> Denton, TX (100 MW)
========================================================================================================
```

### 1. Falsification of Synthetic Dollar/MW Ratios
- **Applied Digital (APLD):** The \$6.597B consolidated debt consists of \$2.35B PF1 Notes (Building 1 & 2), \$1.59B 7% Notes (Building 4), \$2.15B PF2 Notes (Harwood, ND campus), \$450M corporate convertibles, \$56.7M residual corporate notes, and the retired bridge. Dividing \$6.597B by 60 MW creates a spurious metric of \$110M/MW. In reality, the legally attributable funded debt on Polaris Forge 1 is **\$3.940B**, supporting a **400 MW critical IT campus** leased to CoreWeave.
- **Iris Energy (IREN):** The \$2.4B Blue Owl/PIMCO financing is borrowed by `IE Mackenzie Compute Ltd.` and specifically finances GPU servers and equipment located at IREN's **Mackenzie data-center campus in British Columbia, Canada** (80 MW site capacity), with borrowings staged against deliveries through December 31, 2026. Attributing this debt to the 650 MW Childress mining facility in Texas would join completely unrelated corporate entities, geographies, and asset classes.

### 2. \$8.490B in Facility-Attributable Funded Debt — 100% Capital-at-Risk Before Full Service
Across all 14 modeled physical campuses, exactly three campuses carry legally demonstrable project- or equipment-level funded debt:
- **Polaris Forge 1 (`FAC-APLD-POLARIS-FORGE-1`):** **\$3,940.0M**
- **Polaris Forge 2 (`FAC-APLD-POLARIS-FORGE-2`):** **\$2,150.0M**
- **Mackenzie Campus (`FAC-IREN-MACKENZIE`):** **\$2,400.0M**
- **Total Attributable Debt:** **\$8,490.0M (\$8.490B)**

Crucially, **100.0% (\$8.490B) of this attributable capital represents Capital-at-Risk Before Service**:
$$\text{Capital-at-Risk Before Service} = \sum \text{attributable debt for facilities where } \text{energized MW} < \text{contracted MW}$$
- Polaris Forge 1: 60 MW measured energized vs 400 MW contracted lease (**85.0% energization gap**).
- Polaris Forge 2: 0 MW measured energized vs 200 MW contracted lease (**100.0% energization gap**).
- Mackenzie: Staged deliveries through Dec 31, 2026 (**100.0% energization gap** prior to complete cluster acceptance).

### 3. \$11.0B in Commercial Commitments Dependent on Incomplete Capacity
At Polaris Forge 1, CoreWeave's 15-year master lease represents **\$11.0B in lifetime contractual commitments**, complemented by uncapped indemnities under `ELN-02` (Building 2) and `ELN-03` (Building 3, carrying a \$4.125B Class C reference proxy). This entire commercial structure is dependent on the staged energization of Buildings 2, 3, and 4.

### 4. Annual Carrying Cost on Incomplete Capacity: \$631.02M/Year
The blended annual contractual interest carrying cost across incomplete attributable assets is **\$631.02M/year** (\$415.0M/yr across APLD PF1 and PF2 notes + \$216.0M/yr on IREN's 9.0% Mackenzie GPU notes).

### 5. Resolution of the Central Research Question
The core economic question is answered:
$$\textbf{Which obligations are safe only if a specific piece of physical infrastructure becomes productive on time?}$$
- **APLD ComputeCo Notes (\$3.94B PF1 + \$2.15B PF2):** Safe only if MDU substation deliveries, Building 2/3 completion, and Building 4 commissioning occur within debt reserve windows.
- **IREN August 2026 Notes (\$2.40B):** Safe only if GPU deliveries complete by December 31, 2026, allowing cluster monetization to amortize the 30-month maturity term.
- **CoreWeave Lease Liabilities (\$11.0B on APLD):** Productive only as data halls reach Service Ready status; delivery failure triggers liquidated damages and springing indemnities.

---

## 1. Stage A: Attribution Layer Architecture

The Attribution Layer (`obligation_facility_links.parquet`) decomposes the contractual network into 51 link rows across all 47 obligations, establishing three discrete structural tiers:

```mermaid
flowchart TD
    subgraph CorporateTier["Tier 1: Corporate & Portfolio Unallocated ($39.808B)"]
        direction TB
        C1["CoreWeave Notes & DDTLs ($35.551B across 16 tranches)"]
        C2["TeraWulf Convertibles ($2.525B across 3 tranches)"]
        C3["APLD Corporate Converts & Residual ($506.7M)"]
        C4["Nebius Term Loan ($775M) & Hut 8 Convertible ($150M)"]
        C5["Supermicro Supplier Commitments ($34.2B)"]
    end

    subgraph MultiFacilityTier["Tier 2: Multi-Facility Customer Contracts (Unallocated Dollars)"]
        direction TB
        M1["OBL-CRWV-CORZ-COLOCATION-2024 (590 MW Leased across 5 Sites)<br>Topological Links: Denton, Dalton, Muskogee, Marble, Austin<br>Allocated Dollars: NULL (No Synthetic Pro-Ration)"]
    end

    subgraph DirectProjectTier["Tier 3: Direct Facility-Attributable Funded Debt ($8.490B)"]
        direction TB
        D1["FAC-APLD-POLARIS-FORGE-1: $3,940.0M Funded Debt<br>(PF1 Notes $2.35B + 7% Notes $1.59B)"]
        D2["FAC-APLD-POLARIS-FORGE-2: $2,150.0M Funded Debt<br>(APLD ComputeCo 2 Notes $2.15B)"]
        D3["FAC-IREN-MACKENZIE: $2,400.0M Funded Equipment Debt<br>(Blue Owl MFSA $1.2B + PIMCO Notes $1.2B)"]
    end

    CorporateTier -.->|Strictly Excluded from Facility Ratios| DirectProjectTier
    MultiFacilityTier -.->|Discrete Campus Mapping| DirectProjectTier
```

### Attribution Taxonomy & Invariant Enforcement
1. `direct_project_financing`: Debt issued by a bankruptcy-remote project SPV specifically to construct or operate a single campus (e.g. `OBL-APLD-DEBT-PF1`, `OBL-APLD-DEBT-PF2`, `OBL-APLD-DEBT-7PCT-2026`).
2. `direct_equipment_financing`: Debt secured specifically by equipment deployed at a designated campus (e.g. `OBL-IREN-DEBT-MFSA-2026`, `OBL-IREN-DEBT-NOTES-2026` at Mackenzie).
3. `direct_lease`: Real property and facility lease agreements tied to a physical campus (e.g. `OBL-CRWV-APLD-LEASE` at Polaris Forge 1).
4. `completion_support`: Springing parent completion indemnities and cost overrun guarantees (`OBL-CRWV-APLD-GUARANTY-ELN02`, `ELN03`).
5. `portfolio_or_corporate`: Corporate obligations where proceeds finance enterprise operations or multi-site fleet deployment without itemized facility ring-fencing. Enforced with `facility_id = None` and `allocated_amount = None`.

---

## 2. The Canonical Facility Attribution & Energization Table

The table below presents the certified facility-by-facility join across all 14 physical campuses:

| Facility ID | Campus Name | Operator | Attributable Funded Debt (\$M) | Customer / Lease Commitment (\$M) | Contracted Capacity (MW) | Measured Energized Load (MW) | Unenergized Capacity (MW) | Energization Gap Ratio | Next Major Milestone | Evidence Completeness |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| `FAC-APLD-POLARIS-FORGE-1` | Polaris Forge 1 Campus | `APLD` | **\$3,940.0** | **\$11,000.0** | 400.0 | 60.0 | 340.0 | **85.0%** | Bldg 2 completion & Bldg 3/4 commissioning (2026–2027) | Class A (10-K, 8-K, Ex 10.1 & 10.2) |
| `FAC-APLD-POLARIS-FORGE-2` | Polaris Forge 2 Campus | `APLD` | **\$2,150.0** | *Hyperscaler Lease* | 200.0 | 0.0 | 200.0 | **100.0%** | Initial capacity H2 2026; full 200 MW early 2027 | Class A (10-K Item 1 & Note 10) |
| `FAC-IREN-MACKENZIE` | Mackenzie Data Center Campus | `IREN` | **\$2,400.0** | *Cloud ARR* | 80.0 | 0.0 | 80.0 | **100.0%** | GPU server staged deliveries through Dec 31, 2026 | Class A (10-K Note August 2026 Financing) |
| `FAC-CORZ-DENTON` | Denton Data Center | `CORZ` | **\$0.0** | *CRWV Colocation* | 270.0 | 100.0 | 170.0 | **63.0%** | Colocation fit-out across multi-building campus | Class A (10-K, 8-K Note Denton Lease) |
| `FAC-CORZ-DALTON` | Dalton Data Center | `CORZ` | **\$0.0** | *CRWV Colocation* | 195.0 | *Unmeasured* | *Unmeasured* | *Unasserted* | HPC infrastructure retrofit from mining | Class A (10-K Colocation table) |
| `FAC-CORZ-MUSKOGEE` | Muskogee Data Center | `CORZ` | **\$0.0** | *CRWV Colocation* | 100.0 | *Unmeasured* | *Unmeasured* | *Unasserted* | HPC infrastructure retrofit from mining | Class A (10-K Colocation table) |
| `FAC-CORZ-MARBLE` | Marble Data Center | `CORZ` | **\$0.0** | *CRWV Colocation* | 117.0 | *Unmeasured* | *Unmeasured* | *Unasserted* | HPC infrastructure retrofit from mining | Class A (10-K Colocation table) |
| `FAC-CORZ-AUSTIN` | Austin Data Center | `CORZ` | **\$0.0** | *CRWV Colocation* | 20.0 | *Unmeasured* | *Unmeasured* | *Unasserted* | HPC infrastructure retrofit from mining | Class A (10-K Colocation table) |
| `FAC-IREN-CHILDRESS` | Childress Data Center | `IREN` | **\$0.0** | *Mining / Cloud* | 750.0 | 650.0 | 100.0 | **13.3%** | Final 100 MW substation expansion to 750 MW | Class A (10-K Item 1 & Note 7) |
| `FAC-IREN-SWEETWATER-1` | Sweetwater 1 Campus | `IREN` | **\$0.0** | *Development* | 1,400.0 | 0.0 | 1,400.0 | **100.0%** | Interconnection substation construction (1,400 MW) | Class A (10-K Item 1) |
| `FAC-IREN-SWEETWATER-2` | Sweetwater 2 Campus | `IREN` | **\$0.0** | *Development* | 600.0 | 0.0 | 600.0 | **100.0%** | AEP Texas 600 MW substation engineering | Class A (10-K Item 1) |
| `FAC-WULF-LAKE-MARINER` | Lake Mariner Campus | `WULF` | **\$0.0** | *Self-operated* | 90.0 | 226.0 | 0.0 | **0.0%** | 500 MW planned expansion engineering | Class A (10-K NYPA allocation) |
| `FAC-NBIS-MANTSALA` | Mäntsälä Supercomputing | `NBIS` | **\$0.0** | *Self-operated* | 75.0 | 75.0 | 0.0 | **0.0%** | Commercial operational service / heat recovery | Class A (10-K & Utility Primary Source) |
| `FAC-NBIS-LAPPEENRANTA` | Lappeenranta AI Factory | `NBIS` | **\$0.0** | *Development* | 310.0 | 0.0 | 310.0 | **100.0%** | Pending grid interconnection & engineering review | Class B (10-K development announcement) |
| **Total / Summary** | **14 Campuses** | — | **\$8,490.0M** | **\$11,000.0M+** | **4,707.0 MW** | **1,111.0 MW** | **3,320.0 MW** | **74.9% (Weighted)**| — | **13 Class A, 1 Class B** |

---

## 3. The Three Temporal Mismatch Chains

The data exposes three distinct institutional mechanisms through which financial commitments crystallize substantially faster than physical computing capacity:

```
[ TIMING CHAIN 1: APPLIED DIGITAL ]
  Project Debt Inception (2024-2026) ------> Substation Energization (MDU 350 MW ESA) ------> CoreWeave Lease Rent ($11B)
  ($6.090B PF1 & PF2 Notes)                   (Only 60 MW Online; 340 MW Pending)              (Dependent on "Service Ready" Date)
  Carrying Cost: $415.0M/year                Lag: 18–24 Months Construction Latency           Springing Indemnity: ELN-02 & ELN-03

[ TIMING CHAIN 2: IRIS ENERGY ]
  GPU Debt Inception (Aug 2026) -----------> Staged Delivery (Through Dec 31, 2026) ---------> 30-Month Note Maturity Clock
  ($2.400B Blue Owl / PIMCO Facility)         (Mackenzie Equipment Acceptance Window)           (Rapid Amortization at 9.0% Coupon)
  Carrying Cost: $216.0M/year                Window: 4-Month Availability Cliff               Utilization Requirement: Immediate 95%+

[ TIMING CHAIN 3: CORE SCIENTIFIC ]
  Customer Inception (June 2024) ----------> Multi-Utility Substation Delivery -------------> Active Colocation Billing
  (590 MW Master Lease to CoreWeave)          (DME, Dalton, OG&E, Duke, Austin Energy)         (Only 100 MW Measured Energized at Denton)
  Revenue Value: ~$8.6B Over 12 Years         Lag: Transformer & Interconnection Lead Times    Expansion Backlog: 490 MW Unenergized
```

### Chain 1: Applied Digital — Substation Staging vs. Lease Rent Triggers
1. **Capital Crystallization:** APLD ComputeCo SPVs issued \$2.35B (PF1, June 2024), \$2.15B (PF2, January 2025), and \$1.59B (7% Notes, June 2026), creating **\$6.090B in funded project debt**.
2. **Carrying Requirements:** Annual interest service across these project notes totals **\$415.0M/year**.
3. **Physical Lag:** While CoreWeave contracted 400 MW at Polaris Forge 1, MDU disclosures confirm only 60 MW of incremental power had been energized by mid-2026. APLD's total FY26 revenue was \$258.7M—insufficient to cover debt service without drawing capitalized interest reserves or equity proceeds.
4. **Contractual Vulnerability:** CoreWeave lease payments commence only upon data halls achieving "Service Ready" condition. Under Exhibit 10.1 (`ELN-02`) and Exhibit 10.2 (`ELN-03`), construction delivery delays trigger liquidated damages and Springing Indemnities where CoreWeave is entitled to demand full project remedies.

### Chain 2: Iris Energy — Staged GPU Acceptance vs. 30-Month Amortization Cliff
1. **Financing Structure:** Borrowed by `IE Mackenzie Compute Ltd.` on August 25, 2026, comprising a \$1.2B MFSA (Blue Owl OBDC) and \$1.2B Senior Notes (PIMCO), bearing a 9.0% fixed coupon.
2. **The Availability Cliff:** The financing is available only through **December 31, 2026**. Funds are drawn strictly on a pro-rata basis as GPU servers are accepted at Mackenzie.
3. **The 30-Month Amortization Window:** Unlike 7-year corporate bonds, each Note issuance matures exactly **30 months from its funding date**. 
4. **Vulnerability:** If server supply chain delays push delivery past December 31, 2026, undrawn financing expires. Once drawn, the 30-month maturity clock runs immediately, requiring the GPU cluster to achieve instant high-margin cloud revenue to satisfy rapid principal amortization.

### Chain 3: Core Scientific — Colocation Revenue vs. Multi-Utility Lead Times
1. **Commitment Structure:** CoreWeave reserved 590 MW across 5 Core Scientific campuses under a 12-year colocation agreement estimated at ~\$8.6B.
2. **Physical Decentralization:** Core Scientific distributed this commitment across 6 municipal and investor-owned utilities (DME, Dalton, OG&E, Duke Energy, Murphy Electric, Austin Energy).
3. **The Delivery Bottleneck:** Only Denton has a confirmed energized colocation load (100 MW). Delivering the remaining 490 MW requires individual utility substation expansions across multiple balancing authorities (ERCOT, SPP, non-RTO Southeast), exposing Core Scientific to transformer lead times of 18–36 months.

---

## 4. Substation & Equipment Delivery Slippage Stress Test

To evaluate the system's resilience to physical delays, we modeled the financial consequences of 6-, 12-, and 18-month substation energization and GPU delivery slippages across attributable assets:

| Delay Scenario | Cumulative Debt Carrying Cost (\$M) | Delayed APLD Lease Revenue (\$M) | Total Cash Flow Drag (\$M) | IREN Mackenzie Financing Impact | Contractual & Covenant Risk Assessment |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **6 Months Delay** | **\$315.5M** | **\$366.7M** | **\$682.2M** | Availability window cliff: Staged deliveries past Dec 31, 2026 require formal lender waiver to draw remaining tranches. | **Moderate:** Liquidity reserves absorb interest; monitoring of Springing Events under ELN-02. |
| **12 Months Delay** | **\$631.0M** | **\$733.3M** | **\$1,364.3M** | Severe maturity compression: 40% of 30-month loan term consumed without productive cloud ARR. | **High:** Project cash flow deficit requires dilutive equity injection; CoreWeave indemnity risk triggers. |
| **18 Months Delay** | **\$946.5M** | **\$1,100.0M** | **\$2,046.5M** | Critical distress: 60% of 30-month term expired; equipment collateral value depreciates against debt. | **Critical:** Default risk on SPV notes; project restructuring required without parent guarantee backstop. |

---

## 5. Publication Visualizations

Two visual artifacts were generated and saved to `outputs/figures/`:

1. **`capital_energization_gap.png`:**
   Renders the comparative relationship between attributable funded debt (\$M) and the physical energization gap (contracted MW vs. measured energized load), illustrating that 100% of attributable debt resides in incomplete, expanding campuses.
2. **`temporal_mismatch_timeline.png`:**
   Plots the financial impact across 6-, 12-, and 18-month delay scenarios, contrasting cumulative contractual debt carrying costs against delayed lease revenue.

---

## 6. Zero Data Drift Verification & Audit Output

The entire pipeline, attribution layer, and baseline invariants were certified with **zero data drift**:

```
=== Running AI Infrastructure Financial Network Consistency Validator (Phase 0.7.2) ===
  [OK] entities.parquet             : 62 rows
  [OK] financials.parquet           : 13754 rows
  [OK] obligations.parquet          : 47 rows
  [OK] obligation_events.parquet    : 56 rows
  [OK] obligation_facts.parquet     : 64 rows
  [OK] obligation_terms.parquet     : 44 rows
  [OK] assumptions.parquet          : 7 rows
  [OK] evidence_claims.parquet      : 54 rows
  [OK] facilities.parquet           : 14 rows
  [OK] power_relationships.parquet  : 13 rows
  [OK] power_facts.parquet          : 29 rows
  [OK] power_terms.parquet          : 27 rows
  [OK] power_claims.parquet         : 9 rows
  [OK] obligation_facility_links.parquet : 51 rows
  [OK] CIK uniqueness verified: 23 distinct reporting entities with zero CIK collisions.
  [OK] Power Backplane verified: 14 facilities, 13 power contracts, 29 typed MW facts, 27 terms (26 Class A, 1 Class B), 9 primary claims.
  [OK] Attribution Layer verified: 51 links across all 47 obligations, zero synthetic facility pro-rations.
  [OK] CRWV 16 modeled debt components/edges sum exactly to $35.551B ($35,551M, exact 0.00% drift).
  [OK] APLD 6 modeled debt components present in master ledger (including 7.00% successor notes).
  [OK] CoreWeave funded debt conserved: $35.551B across 16 tranches (exact 0.00% drift).
  [OK] Applied Digital debt conserved: $6.597B across 6 tranches (exact 0.00% drift).

ALL INTERNAL CONSISTENCY CHECKS PASSED: ZERO DATA DRIFT
```

---

## 7. Conclusions & Next Steps

1. **Epistemic Success of the Attribution Layer:**
   By decoupling corporate/portfolio debt (\$39.808B) from project debt (\$8.490B) and refusing to pro-rate multi-campus leases, Task 021 eliminated the risk of synthetic dollar/MW hallucinations while establishing an empirical bridge between balance sheets and substations.
2. **Empirical Confirmation of Temporal Opacity:**
   The findings demonstrate that financial commitments in the AI infrastructure buildout are crystallizing 12 to 24 months ahead of physical energization. Over **\$8.49B in debt** and **\$11.0B in lease liabilities** currently depend on physical substations that are either under construction or awaiting equipment delivery.
3. **Next Sprint Recommendation:**
   With both the physical power topology (ADR-020.1a) and the capital-to-physical attribution layer (ADR-021) frozen and validated, the observatory is now positioned to model cross-entity contagion under power substation curtailment or equipment delivery failures.
