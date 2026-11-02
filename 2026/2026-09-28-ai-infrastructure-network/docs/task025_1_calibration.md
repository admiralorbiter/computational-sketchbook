# Task 025.1 Calibration Protocol: Retrospective Temporal Holdout & Epistemic Audit (Project Jupiter)

**Status:** Retrospective Amendment & Calibration Protocol  
**Date:** September 30, 2026  
**Original Immutable Protocol:** [`docs/task025_prespecification.md`](task025_prespecification.md) (committed at [`6bc951d`](https://github.com/admiralorbiter/computational-sketchbook/commit/6bc951d))  
**Epistemic Baseline Cutoff ($t_0$):** September 23, 2026, 23:59:59 UTC  
**Observed Shock Horizon:** September 24, 2026 – September 30, 2026  
**Target Natural Experiment:** Project Jupiter (Santa Teresa, Doña Ana County, NM) Force-Majeure Notice & ~$18B Debt Stack  

---

## 1. Context & Epistemic Reclassification

External scientific review of Task 025 identified critical methodological issues requiring formal calibration:

1. **Commit Sequencing & Evidentiary Category:**
   - The original pre-specification protocol was committed to version control on **September 30, 2026** ([`6bc951d`](https://github.com/admiralorbiter/computational-sketchbook/commit/6bc951d)), six days after the public force-majeure disclosure on **September 24, 2026**.
   - While Git preserves the audit trail demonstrating that the analysis code and scoring rubrics were committed prior to execution, Git cannot establish blindness to the real-world event itself.
   - Consequently, Task 025 is formally reclassified from an *"ex-ante prospective out-of-sample prediction"* to a:
     $$\mathbf{Retrospective\ Temporal\ Holdout\ Validation\ /\ Historical\ Backtest}$$
   - To maintain institutional transparency, the original protocol ([`docs/task025_prespecification.md`](task025_prespecification.md)) remains frozen and immutable; this document records the retrospective calibration rules.

2. **Decoupling Preregistered Models from Post-Hoc Calibrated Subgraphs:**
   - The original `6bc951d` Hypothesis 1 modeled a linear grid sequence starting with `PNM / WECC` and omitting `NMSLO` and `BORDERPLEX`.
   - In Task 025.1, the original preregistered model and the retrospectively calibrated models are scored independently and never conflated:
     - **Model A (Original Preregistered Hypothesis 1):** Scored strictly against the original PNM/WECC candidate set. (Result: Fails operative path discovery because PNM/WECC was an unevidenced fallback, not the operative microgrid choke-point).
     - **Model B (Calibrated Strict Linear Conduit):** Algorithmically discovers the physical-to-financial spine (`NMSLO -> FAC -> SPV -> ORCL -> SYNDICATE`). Evaluated against the post-event evidence truth set.
     - **Model C (Calibrated Descriptive Augmented Subgraph):** Branching corporate-augmented tree incorporating developer (`STACK_INFRA`), sponsor (`BLUE_OWL`), and regional partner (`BORDERPLEX`). Evaluated as a descriptive reconstruction.

---

## 2. Calibrated Methodological Rules

### Rule 1: Zero Post-Event Contract Knowledge in Pre-Event Graph
- *The Flaw:* Prior revisions described Oracle's lease (`OBL-ORCL-JUPITER-LEASE`) at $t_0$ as containing specific delay carry-fee obligations and force-majeure provisions. Those detailed risk-allocation clauses only became public with reporting on September 24–25, 2026.
- *The Correction:* At $t_0$ (September 23, 2026), the pre-event graph models only what was publicly knowable: that Oracle was anchor colocation tenant at Project Jupiter for the 2.45 GW fuel-cell microgrid campus. The payment mechanics and delay clauses are marked **`UNKNOWN_AT_T0`**. Post-event evidence subsequently reveals the contractual carry friction.

### Rule 2: Pure Algorithmic Graph Traversal & Subgraph Structure
- *The Flaw:* Traversal previously returned manually declared dictionaries without NetworkX discovery or edge verification, and serialized branching corporate structures into a synthetic single line.
- *The Correction:* 
  1. The strict linear conduit is discovered via NetworkX path traversal (`nx.all_simple_paths` / `nx.shortest_path`) across verified physical, asset, and financing edges.
  2. The corporate-augmented structure is modeled as a **branching subgraph/tree**, with SPV ownership and sponsorship edges traversed dynamically via `G.in_edges()`.
  3. Every step in the path and tree is asserted to exist in the underlying NetworkX graph `G`.

### Rule 3: Isolation of Pre-Event Baseline Conditions
- *The Flaw:* On September 18, 2026 (five days before $t_0$), Reuters/FT reported that Project Jupiter's ~$18B debt stack was trading at 89–91 cents on the dollar amid syndication hurdles. Prior code treated this as a predicted post-event outcome.
- *The Correction:* September 18 debt discounting and syndication friction are modeled as **observed baseline conditions at $t_0$**. The scoring engine evaluates only **incremental stress** realized on or after September 24 (the tenant force-majeure notice, rent defense, and lender covenant reviews).

### Rule 4: Evidence-Driven Truth Set & Post-Event Ledger
- *The Flaw:* Post-event truth sets were hardcoded in Python dictionaries, and several cited URLs did not support their claims.
- *The Correction:*
  1. Primary post-event evidence is compiled in [`data/processed/task025/jupiter_postevent_evidence.parquet`](../data/processed/task025/jupiter_postevent_evidence.parquet).
  2. The post-event ground-truth set ($\mathcal{E}_{\text{impl}}$) is derived algorithmically from primary post-event shock claims.
  3. Unverified claims (e.g. unevidenced post-event developer coordination links) are excised, establishing a verified **7-node truth set**:
     $$\mathcal{E}_{\text{impl}} = \{ \text{NMSLO}, \text{FAC-PROJECT-JUPITER-NM}, \text{PROJECT\_JUPITER\_SPV}, \text{ORCL}, \text{CONSTRUCTION\_LENDER\_SYNDICATE}, \text{STACK\_INFRA}, \text{BLUE\_OWL} \}$$
  4. In the 8-node descriptive augmented tree, `BORDERPLEX` is scored as an honest **False Positive** (Precision = 7/8 = 87.5%, Recall = 7/7 = 100.0%).

### Rule 5: Rigorous Bitemporal Precedence Accounting (Hypothesis 4)
- *The Flaw:* The original Hypothesis 4 specified lead time over *formal SEC filings by ORCL / Blue Owl*, whereas the code scored lead time over the *September 24 news report*.
- *The Correction:*
  - **Metric 4A (Regulatory-to-Public-Notice Lead Time):** NMSLO denial on July 15, 2026 $\to$ September 24, 2026 public force-majeure report = **71 calendar days** (Lead time over debt press of Sept 18 = **65 days**).
  - **Metric 4B (Preregistered SEC Disclosure Endpoint):** As of September 30, 2026, neither Oracle nor Blue Owl OBDC filed a Form 8-K or 10-Q disclosing the force-majeure notice. The SEC disclosure endpoint is formally recognized as **RIGHT-CENSORED**:
    $$\Delta t_{\text{SEC}} \ge \mathbf{77\ Calendar\ Days\ (Right-Censored)}$$
    This demonstrates that physical regulatory signals preceded formal SEC corporate transparency by over 2.5 months.
