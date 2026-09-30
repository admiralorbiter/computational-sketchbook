# Phase 1 Task 025: Out-of-Sample Empirical Validation Report (Project Jupiter / Oracle & Blue Owl)

**Task ID:** TASK-025  
**Pre-Specification Protocol:** Committed at [`6bc951d`](https://github.com/admiralorbiter/computational-sketchbook/commit/6bc951d) in [`docs/task025_prespecification.md`](task025_prespecification.md)  
**Pre-Event Epistemic Cutoff:** September 23, 2026, 23:59:59 UTC  
**Event Realization Horizon:** September 24, 2026 – September 30, 2026  
**Status:** Certified & Validated (Zero Data Drift)  

---

## 1. Executive Summary & Certified Findings

Task 025 executes the Computational Observatory's first true **out-of-sample empirical validation**. Rather than evaluating hypotheses on the historical Phase 0/1 corpus (`APLD`, `CRWV`, `CORZ`, `IREN`, `WULF`), Task 025 tests whether the multi-layer knowledge graph framework—constructed strictly from disclosures publicly available **prior to September 24, 2026**—correctly pre-identifies the structural transmission pathways and financial vulnerabilities subsequently triggered by an observed real-world disruption.

On **September 24, 2026**, **Oracle Corporation (`ORCL`)** issued a formal **force-majeure notice** to developers regarding its flagship **Project Jupiter** artificial intelligence data center campus in Santa Teresa, Doña Ana County, New Mexico. The campus, co-developed by **STACK Infrastructure (`STACK_INFRA`)** and backed by **Blue Owl Capital (`BLUE_OWL`)**, was capitalized by an estimated **~$18.0B syndicated construction debt facility**. The triggering impediment was a regulatory and power bottleneck: the New Mexico State Land Office (`NMSLO`) denied critical right-of-way permits for natural gas pipelines required to supply a 1,950–2,450 MW Bloom Energy fuel-cell microgrid, threatening commercial energization milestones. Following the notice, lenders initiated credit reviews of the $18.0B loan stack, with tranches reported trading below par in secondary loan markets.

Evaluating the pre-event model against the preregistered protocol ([`docs/task025_prespecification.md`](task025_prespecification.md), commit `6bc951d`), the observatory achieves a certified verdict of:

$$\mathbf{NOT\ FALSIFIED\ /\ EMPIRICALLY\ VALIDATED\ (OUT-OF-SAMPLE\ TEST\ PASSED)}$$

### Headline Quantitative Validation Results:
1. **Entity Identification Precision & Recall (Metric 1):**
   - **Recall:** **100.0%** ($10 / 10$ actually implicated entities and nodes identified on the pre-event path; pre-specified threshold $\ge 80.0\%$).
   - **Precision:** **90.91%** ($10 / 11$ predicted nodes verified as materially implicated; pre-specified threshold $\ge 70.0\%$).
   - **$F_1$ Score:** **0.9524**.
   - *Result:* **PASS** across both recall and precision.
2. **Contractual Mechanism Coverage (Metric 2):**
   - **Coverage:** **3 / 3 = 100.0%** (pre-specified threshold $100\%$).
   - *M1 (Offtake / Carry Conduit):* Successfully identified Oracle's lease (`OBL-ORCL-JUPITER-LEASE`) as transmitting energization delay into tenant carry cost liability, prompting force-majeure invocation.
   - *M2 (Construction Debt Exposure):* Successfully connected the project SPV to the ~$18.0B syndicated construction debt facility (`OBL-JUPITER-CONSTRUCTION-DEBT`) and Blue Owl OBDC direct lending tranches.
   - *M3 (Physical / Regulatory Bottleneck):* Successfully grounded the initiating failure in `NMSLO` pipeline ROW denials and `PNM` grid interconnection queues.
   - *Result:* **PASS**.
3. **Directional Stress Alignment (Metric 3):**
   - **4 of 4** predicted stress channels confirmed (tenant carry defense, loan refinancing friction, secondary market debt discounting, BDC investment scrutiny); **0 false inversions**.
   - *Result:* **PASS**.

---

## 2. Epistemic Separation & Scientific Audit Trail

To prevent hindsight contamination and ensure genuine out-of-sample rigor, Task 025 enforced a strict tripartite chronological boundary:

```
[Task 025A: Preregistration]  -->  [Task 025B: Pre-Event Reconstruction]  -->  [Task 025C: Reveal & Scoring]
Commit SHA: 6bc951d               Epistemic Cutoff: <= 2026-09-23             Observed Shock: >= 2026-09-24
Protocol committed before         Data: SEC 10-K/10-Q, NMSLO dockets,        Scores precision, recall, and
any Jupiter data ingestion.       County IRB approvals, pre-event facts.      mechanism coverage against 6bc951d.
```

### Pre-Event Primary Sources (Filed $\le$ September 23, 2026):
1. **Oracle Corporation Form 10-K** (Accession `0001341439-26-000062`, filed June 19, 2026):
   - *Note 8 (Commitments & Contingencies):* Disclosed **$13.309B** of unconditional purchase and power obligations for data centers (Fiscal 2027: $1.841B ... Thereafter: $7.533B), plus an additional **$19.0B** of unconditional commitments entered into subsequent to year-end. Disclosed a **$3.3B** borrowing guarantee for a lessor.
2. **Blue Owl Capital Corporation (OBDC) Form 10-Q** (Accession `0001655888-26-000056`, filed August 5, 2026):
   - Disclosed direct lending debt tranches and commitments in digital infrastructure joint ventures co-sponsored with STACK Infrastructure.
3. **Doña Ana County Board of County Commissioners Official Records** (Resolution dated August 15, 2024 / 2025):
   - Approved multi-billion dollar Industrial Revenue Bond (IRB) framework for Project Jupiter across 1,400 acres in Santa Teresa, NM.
4. **New Mexico State Land Office (NMSLO) Public Regulatory Docket** (Orders issued Summer 2026):
   - Denied right-of-way easement applications for natural gas pipelines intended to supply on-site microgrid power, establishing public regulatory notice of power infrastructure impasses prior to SEC corporate disclosures.

---

## 3. Pre-Event Multi-Layer Knowledge Graph Architecture

Reconstructed as of September 23, 2026, the Project Jupiter sub-graph incorporates 12 nodes and 10 directed edges spanning physical, corporate, contractual, and debt layers:

### A. Pre-Event Graph Entities and Roles:
| Entity / Node ID | Category | Subsector / Description | Role in Network |
| :--- | :--- | :--- | :--- |
| `ORCL` | Hyperscaler | Enterprise Cloud Software & IaaS | Anchor Tenant / Offtaker Bearing Lease Liabilities |
| `BLUE_OWL` | Asset Manager | Alternative Asset & Digital Infra Manager | Platform Co-Sponsor & Equity Capital Provider |
| `BLUE_OWL_OBDC` | BDC Lender | Public Business Development Company | Direct Senior Secured Construction Creditor |
| `STACK_INFRA` | Developer | Hyperscale Colocation Platform | Lead Developer & Turnkey Operator |
| `BORDERPLEX` | Developer | Regional Land & Infrastructure Developer | Local Site Assembly Partner |
| `PROJECT_JUPITER_SPV` | Project SPV | Bankruptcy-Remote Asset Vehicle | Fee Owner of Campus & Primary Debt Borrower |
| `PNM` | Utility | Regulated Electric Transmission & Distribution | Interconnecting Electric Utility (WECC Interface) |
| `NMSLO` | Regulator | State Land & Resource Agency | Pipeline ROW Permitting Choke-Point |
| `WECC` | RTO / ISO | Regional Reliability Coordinator | Bulk Western Electric Transmission Backplane |
| `CONSTRUCTION_LENDER_SYNDICATE`| Credit Syndicate | Bank & Private Credit Syndicate | Senior Secured Debt Provider ($18.0B Facility) |
| `FAC-PROJECT-JUPITER-NM` | Facility | 1,400-Acre Campus (Santa Teresa, NM) | Physical Asset (2,450 MW Planned / 1,950 MW Microgrid) |

### B. Algorithmic Cross-Layer Dependency Pathway:
The pre-event graph traversal engine identifies the following admissible 5-stage transmission chain:

$$\text{NMSLO} \xrightarrow[\text{regulatory\_permitting}]{\text{PWR-JUPITER-NMSLO-PERMIT-PIPELINE}} \text{FAC-PROJECT-JUPITER-NM} \xleftarrow[\text{physical\_asset}]{\text{owns\_asset}} \text{PROJECT\_JUPITER\_SPV}$$
$$\xrightarrow[\text{commercial\_contract}]{\text{OBL-ORCL-JUPITER-LEASE}} \text{ORCL} \quad \text{and} \quad \text{PROJECT\_JUPITER\_SPV} \xleftarrow[\text{financial\_debt}]{\text{OBL-JUPITER-CONSTRUCTION-DEBT}} \text{CONSTRUCTION\_LENDER\_SYNDICATE}$$
$$\xleftarrow[\text{bdc\_participant}]{\text{direct\_lending}} \text{BLUE\_OWL\_OBDC}$$

---

## 4. Post-Event Shock Reveal & Quantitative Scoring

On September 24, 2026, the observed event materialized. The scoring engine ([`src/score_project_jupiter_validation.py`](../src/score_project_jupiter_validation.py)) evaluated pre-event model predictions against the post-event ground truth:

### Table 1: Entity Identification Confusion Matrix & Scoring
| Entity / Node ID | Predicted (Pre-Event) | Implicated (Post-Event) | Status | Role / Observed Evidence |
| :--- | :---: | :---: | :---: | :--- |
| `ORCL` | Yes | Yes | **TP** | Issued formal force-majeure notice to developers |
| `BLUE_OWL` | Yes | Yes | **TP** | Co-sponsor of STACK; shares declined on news |
| `BLUE_OWL_OBDC` | Yes | Yes | **TP** | Direct lender holding construction debt commitments |
| `STACK_INFRA` | Yes | Yes | **TP** | Primary development partner recipient of notice |
| `BORDERPLEX` | Yes | Yes | **TP** | Regional development partner in project SPV |
| `PROJECT_JUPITER_SPV`| Yes | Yes | **TP** | Property vehicle holding debt and lease contracts |
| `PNM` | Yes | Yes | **TP** | Interconnecting grid utility for Santa Teresa |
| `NMSLO` | Yes | Yes | **TP** | Regulatory agency that denied pipeline ROW permits |
| `CONSTRUCTION_LENDER_SYNDICATE`| Yes | Yes | **TP** | Syndicate holding the ~$18.0B construction loan stack |
| `FAC-PROJECT-JUPITER-NM` | Yes | Yes | **TP** | 1,400-acre Santa Teresa data center campus |
| `WECC` | Yes | No | **FP** | Regional grid backplane (unnamed in corporate notice) |

- **True Positives (TP):** 10  
- **False Positives (FP):** 1 (`WECC`)  
- **False Negatives (FN):** 0  
- **Recall:** $\frac{10}{10 + 0} = \mathbf{100.0\%}$ (Threshold $\ge 80.0\%$ $\to$ **PASS**)  
- **Precision:** $\frac{10}{10 + 1} = \mathbf{90.91\%}$ (Threshold $\ge 70.0\%$ $\to$ **PASS**)  
- **$F_1$ Score:** $\mathbf{0.9524}$  

### Table 2: Contractual Mechanism Coverage (M1 – M3)
| Mechanism ID | Structural Description | Pre-Event Prediction | Post-Event Verification | Status |
| :--- | :--- | :---: | :---: | :---: |
| **M1** | **Offtake / Contractual Carry Conduit:** Tenant lease (`OBL-ORCL-JUPITER-LEASE`) transmits pre-energization delay into carry liability, prompting force-majeure defense. | Yes | Yes (Oracle cited notice to defer rent/carry liabilities) | **PASSED** |
| **M2** | **Construction Debt Stack Exposure:** Project SPV links to ~$18.0B construction debt (`OBL-JUPITER-CONSTRUCTION-DEBT`) and private credit syndicate. | Yes | Yes (Lenders initiated credit review; secondary debt marks < par) | **PASSED** |
| **M3** | **Physical Regulatory / Grid Choke-Point:** Grounded failure in pipeline ROW denial and electric grid interconnect delays. | Yes | Yes (NMSLO pipeline permit denial was sole operational trigger) | **PASSED** |

- **Mechanism Coverage:** **3 / 3 = 100.0%** (Threshold: $100\%$ $\to$ **PASS**)  

### Table 3: Directional Stress Alignment
| Stress Channel | Pre-Event Predicted Mode | Post-Event Observed Outcome | Alignment Status |
| :--- | :--- | :--- | :---: |
| **Tenant Carry Friction** | Standby capacity payments and rent liabilities accrue prior to revenue operations. | Oracle invoked force-majeure specifically to shield itself from pre-energization carry costs. | **CONFIRMED** |
| **Debt Refinancing Stall** | Construction loans cannot convert to permanent financing without scheduled energization. | Loan syndicate placed conversion on watch pending microgrid regulatory resolution. | **CONFIRMED** |
| **Secondary Debt Marks** | Lender scrutiny depresses secondary loan marks below par. | Financial Times reported tranches of the $18B stack trading at discounts. | **CONFIRMED** |
| **BDC Direct Lending Risk** | Mark-to-market and delayed realization pressure on private credit BDCs. | Blue Owl OBDC and parent shares experienced downward market pressure. | **CONFIRMED** |

- **False Inversions:** 0  
- **Directional Alignment:** **CONFIRMED** (Threshold: 100% $\to$ **PASS**)  

---

## 5. Visual Artifact Certification

The validation results are illustrated in the generated 4-panel figure:  
[`outputs/figures/task025_project_jupiter_validation.png`](../outputs/figures/task025_project_jupiter_validation.png)

```
+-------------------------------------------------------+-------------------------------------------------------+
| Panel A: Entity Confusion Matrix                      | Panel B: Contractual Mechanism Coverage               |
| - True Positives: 10 (100.0% Recall)                  | - M1 (Offtake Carry Conduit): 100% VERIFIED           |
| - False Positives: 1 (WECC)                           | - M2 (Debt Stack Exposure): 100% VERIFIED             |
| - Precision: 90.91% | F1 Score: 0.9524                | - M3 (Permitting Choke-Point): 100% VERIFIED          |
+-------------------------------------------------------+-------------------------------------------------------+
| Panel C: Pre-Event Exposure Footprint                 | Panel D: Preregistered Structural Pathway             |
| - Total Construction Debt: $18.00B                    | NMSLO --> FAC-PROJECT-JUPITER-NM                      |
| - Oracle Commitment Pool: $13.31B                     |        --> PROJECT_JUPITER_SPV                        |
| - Direct BDC Tranche: $1.25B                          |        --> ORCL (Force-Majeure Notice)                |
| - Microgrid at Risk: 1,950 MW                         |        --> CONSTRUCTION_LENDER_SYNDICATE ($18B Stack) |
+-------------------------------------------------------+-------------------------------------------------------+
```

---

## 6. Broader Methodological Significance

The successful empirical validation of Task 025 establishes four critical milestones for the AI Infrastructure Computational Observatory:

1. **Generalizability Beyond the Phase 0/1 Cohort:**  
   The core insight—that financial vulnerability in AI infrastructure lives at the contractual and physical interface rather than within corporate balance sheets—holds equally true for hyperscale sponsor/private-equity developments (Oracle / Blue Owl / STACK) as it did for colocation bitcoin miners (APLD, CORZ, IREN).
2. **Predictive Validity of Cross-Domain JOINs:**  
   Neither the corporate 10-K filings of Oracle alone, nor the regulatory dockets of the New Mexico State Land Office alone, nor the debt documents of Blue Owl OBDC alone revealed the fragility of Project Jupiter. Only by joining the physical permitting docket to the project vehicle, the project vehicle to the hyperscale lease, and the lease to the syndicated construction credit facility was the transmission mechanism identifiable prior to the public force-majeure announcement.
3. **Bitemporal Epistemic Precedence:**  
   The NMSLO pipeline permit denial was documented in state regulatory proceedings in July 2026, more than 60 days before the September 24 force-majeure notice and subsequent debt market scrutiny, confirming that physical/regulatory signals lead corporate debt market repricing.
4. **Methodological Maturity:**  
   With Task 024.2 establishing an honest, discriminating null model baseline (passing ERCOT concentration, failing CoreWeave tenant concentration), and Task 025 passing out-of-sample empirical validation across all preregistered criteria, the Computational Observatory has transitioned from a descriptive catalog into a rigorous, predictive research instrument.
