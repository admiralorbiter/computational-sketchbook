# Task 025A Pre-Specification Protocol: Out-of-Sample Shock Transmission & Structural Path Validation (Project Jupiter / Oracle & Blue Owl)

**Status:** Pre-Specified & Committed Prior to Ingestion & Post-Event Scoring  
**Date:** September 30, 2026  
**Epistemic Cutoff (Pre-Event Baseline):** September 23, 2026, 23:59:59 UTC  
**Event Realization Horizon:** September 24, 2026 – September 30, 2026  
**Target Shock Case:** Project Jupiter Data Center Campus (New Mexico) Force-Majeure & Power/Permitting Interruption  

---

## 1. Context & Research Objective

In Tasks 021 through 024, the Computational Observatory established internal consistency, bitemporal point-in-time reconstruction, and structural reconvergence across the frozen 5-company Phase 0/1 portfolio (`APLD`, `CRWV`, `CORZ`, `IREN`, `WULF`). In Task 024.2, the fixed-degree facility-capacity permutation test demonstrated that while ERCOT regional grid concentration is statistically exceptional ($p = 0.0060$), tenant concentration on CoreWeave is explainable by facility degree distribution ($p = 0.816$), confirming that the analytical instrument can produce both positive and negative results without confirmation bias.

**Task 025** executes the observatory's first true **out-of-sample empirical validation**. 

On **September 24, 2026**, market disclosures revealed that **Oracle Corporation (`ORCL`)** issued a formal force-majeure notice regarding its flagship **Project Jupiter** data center development in New Mexico—a multi-gigawatt hyperscale campus developed in partnership with **Blue Owl Capital (`BLUE_OWL`)** and **STACK Infrastructure (`STACK`)**, capitalized by an estimated **~$18B construction debt financing stack**. Reporting (Reuters, Financial Times) indicated immediate lender scrutiny, concerns over contractually mandated carry costs during energization delays, and secondary trading of project debt below par.

This natural experiment allows us to test whether the multi-layer knowledge graph, constructed strictly from evidence available **on or before September 23, 2026**, successfully pre-identifies the structural dependency pathway through which physical power and permitting delays propagate into financial stress.

---

## 2. Epistemic Separation & Sequencing Rules

To guarantee strict scientific integrity and prevent hindsight bias, Task 025 was designed with chronologically decoupled stages:

```
[Task 025A: Protocol]       -->  [Task 025B: Pre-Event Graph]  -->  [Task 025C: Reveal & Scoring]
Commit: 6bc951d (Sept 30)         Cutoff: <= 2026-09-23             Evidence: >= 2026-09-24
Protocol committed to Git.        Reconstructs pre-event G_join.    Scores precision/recall.
```

> [!NOTE] Methodological Classification: Retrospective Temporal Holdout Backtest
> Because protocol commit `6bc951d` was committed on September 30, 2026—following the September 24 public force-majeure report—this experiment is formally classified as a **Retrospective Temporal Holdout Validation / Historical Backtest** using an epistemic cutoff of September 23, 2026, rather than a prospective out-of-sample prediction. Git establishes that the analytical code and scoring rubric were committed without post-hoc cherry-picking of thresholds, but retrospective backtests inherently possess weaker epistemic blindness than ex-ante prospective commits. Genuine prospective validation requires an immutable frozen commit *prior* to real-world shock occurrence.

1. **Task 025A (This Document):** Pre-specifies hypotheses, admissible traversal sequences, target entity/contract candidate sets, directional stress mechanisms, and quantitative precision/recall rubrics.
2. **Task 025B (Pre-Event Reconstruction):** Constructs the pre-event knowledge graph $G_{\text{join}}(t \le \text{2026-09-23})$ using only primary disclosures available before September 24, 2026 (Oracle 10-K, NMSLO pipeline permit denial orders of July 15, 2026, and Reuters debt reporting of September 18, 2026).
3. **Task 025C (Post-Event Reveal & Scoring):** Ingests the September 24+ observed event record and scores the pre-event model against the preregistered criteria.

---

## 3. Preregistered Hypotheses

### What the Model DOES NOT Predict:
- The model **does not** predict the stochastic timing, political likelihood, or exact calendar date of a force-majeure event.
- The model **does not** predict equity price movements (e.g., "Oracle shares will fall $X\%$") or secondary market bond yield spreads.

### What the Model DOES Predict:
**Core Assertion:**  
*"If a power, permitting, or energization shock occurs at Project Jupiter in New Mexico, the pre-event joined graph $G_{\text{join}}$ predicts that exposure propagates along specific, typed contractual and structural conduits, implicating an identifiable set of entities, SPVs, and debt facilities before public corporate reporting reveals the loss."*

### Pre-Specified Structural Hypotheses:

1. **Hypothesis 1 (Admissible Cross-Layer Dependency Path):**  
   The physical grid delay transmits to financial capital providers via the following exact 5-stage typed edge sequence:
   $$\text{Utility Interconnection (PNM / WECC)} \xrightarrow[\text{power\_service}]{\text{grid}} \text{Facility (PROJECT\_JUPITER)} \xrightarrow[\text{project\_asset}]{\text{physical}} \text{Developer/Landlord SPV (STACK / BLUE\_OWL SPV)}$$
   $$\xrightarrow[\text{lease / offtake}]{\text{contract}} \text{Tenant / Obligor (ORCL)} \xrightarrow[\text{credit\_agreement}]{\text{finance}} \text{Syndicate / Credit Vehicles (BLUE\_OWL\_OBDC / Debt Syndicate)}$$

2. **Hypothesis 2 (Contractual Carry Friction Mechanism):**  
   The primary financial vulnerability in the pre-event contract structure is not operating loss, but **contractual carry friction**: under the lease/development structure, delays in energization or commercial operation trigger contractual obligations (standby capacity reservation payments, construction period interest carry, or delay penalties) that fall upon the tenant (`ORCL`) or developer vehicle unless explicitly excused by force-majeure provisions.

3. **Hypothesis 3 (Debt Stack & Collateral Refinancing Vulnerability):**  
   The ~$18B construction debt facility is reliant upon scheduled commercial energization milestones for conversion into permanent financing; an unmitigated delay impairs collateral coverage ratios, triggers lender syndication review, and causes debt valuation stress in private credit / secondary loan markets.

4. **Hypothesis 4 (Bitemporal Knowledge Asymmetry):**  
   Physical substation and regulatory permitting hurdles exist in public utility / municipal dockets with an **epistemic precedence of at least 30 days** prior to formal SEC disclosure by the public entities (`ORCL`, `BLUE_OWL_OBDC`).

---

## 4. Candidate Entities and Graph Schema for Project Jupiter

To enable rigorous precision and recall scoring, the pre-event universe of candidate entities and relationships is preregistered below:

### A. Pre-Specified Candidate Entity Universe ($\mathcal{E}_{\text{candidate}}$):
1. `ORCL`: Oracle Corporation (Ultimate Tenant / Cloud Infrastructure Sponsor)
2. `BLUE_OWL`: Blue Owl Capital Inc. (Alternative Asset Manager / Co-Sponsor)
3. `BLUE_OWL_OBDC`: Blue Owl Capital Corporation (Public BDC / Direct Lending Vehicle)
4. `STACK_INFRASTRUCTURE`: STACK Infrastructure (Data Center Developer / Operating Partner)
5. `PROJECT_JUPITER_SPV`: Project-specific joint venture / property vehicle (holding the New Mexico asset)
6. `PNM`: Public Service Company of New Mexico (Interconnecting Transmission & Distribution Utility)
7. `WECC`: Western Electricity Coordinating Council (Regional Reliability Balancing Authority)
8. `PROJECT_JUPITER_FACILITY`: The New Mexico hyperscale campus (~1,000 MW planned critical capacity)
9. `CONSTRUCTION_LENDER_SYNDICATE`: The institutional banking and private credit syndicate providing the ~$18B construction loan stack

### B. Typed Edge Typology:
- `interconnects_to` (Grid $\to$ Facility): Substation / transmission interconnect capacity.
- `owns_or_develops` (Developer/SPV $\to$ Facility): Property fee/leasehold ownership and construction management.
- `leases_to` (SPV $\to$ Tenant): Long-term hyperscale colocation / synthetic lease agreement.
- `finances` (Lender $\to$ SPV): Construction debt facility secured by project assets and lease assignment.
- `guarantees_or_supports` (Parent $\to$ Lease / Debt): Corporate parent completion or payment guaranties.

---

## 5. Scoring Rubric & Quantitative Acceptance Criteria

Task 025C will evaluate the pre-event model against the post-September 24 event record according to three formal metrics:

### Metric 1: Entity Graph Precision, Recall, and $F_1$ Score
Let $\mathcal{E}_{\text{pred}}$ be the set of entities discovered on the active Project Jupiter dependency path in $G_{\text{join}}(t \le \text{2026-09-23})$.  
Let $\mathcal{E}_{\text{impl}}$ be the set of entities verified as materially implicated in the post-September 24 disclosures (named in force-majeure notices, public regulatory filings, or reporting on the debt syndicate).

$$\text{Recall}_{\text{entity}} = \frac{|\mathcal{E}_{\text{pred}} \cap \mathcal{E}_{\text{impl}}|}{|\mathcal{E}_{\text{impl}}|}, \quad \text{Precision}_{\text{entity}} = \frac{|\mathcal{E}_{\text{pred}} \cap \mathcal{E}_{\text{impl}}|}{|\mathcal{E}_{\text{pred}}|}, \quad F_1 = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

- **Passing Threshold:**
  - $\text{Recall}_{\text{entity}} \ge 0.80$ (at least 80% of all actually implicated entities were captured by the pre-event graph).
  - $\text{Precision}_{\text{entity}} \ge 0.70$ (at least 70% of graph-predicted entities were materially relevant).

### Metric 2: Contractual Mechanism Identification (Mechanism Coverage)
The model must successfully identify and type three key structural mechanisms:
1. **Mechanism M1 (Offtake / Carry Conduit):** The model correctly identifies that tenant `ORCL` bears contractual carry/capacity liability to the developer SPV prior to energization.
2. **Mechanism M2 (Construction Debt Exposure):** The model connects the project SPV to the ~$18B construction debt stack and private credit/bank syndicate.
3. **Mechanism M3 (Physical Grid Bottleneck):** The model grounds the disruption in the utility interconnection bottleneck (`PNM`/`WECC`).
- **Passing Threshold:** All 3 mechanisms must be verified ($3/3 = 100\%$).

### Metric 3: Directional Stress Alignment
The model's qualitative directional stress predictions (unmitigated carry liabilities, refinancing/syndication friction, collateral impairment) must match the observed real-world stress modes, with zero false inversions (e.g. predicting positive windfall cash flow from delayed facilities).

---

## 6. Overall Falsification Verdict Rule

The empirical validation outcome will be formally classified under one of three mutually exclusive determinations:

1. **NOT FALSIFIED / EMPIRICALLY VALIDATED:**
   - $\text{Recall}_{\text{entity}} \ge 0.80$, $\text{Precision}_{\text{entity}} \ge 0.70$
   - Mechanism Coverage $= 3/3$ ($100\%$)
   - Directional Stress Alignment verified across all implicated channels.

2. **PARTIALLY VALIDATED / MIXED RESULT:**
   - $\text{Recall}_{\text{entity}} \ge 0.60$, $\text{Precision}_{\text{entity}} \ge 0.50$
   - Mechanism Coverage $\ge 2/3$.

3. **FALSIFIED / PREDICTION FAILURE:**
   - $\text{Recall}_{\text{entity}} < 0.60$, OR
   - Mechanism Coverage $\le 1/3$, OR
   - The pre-event graph fails to connect the physical facility to the debt financing stack.

---

## 7. Protocol Sealing & Hash Integrity

This protocol is committed to the Git repository **before** creating pre-event tables or ingesting post-event evidence. The Git commit SHA of this file establishes the immutable timestamp and baseline for Task 025.
