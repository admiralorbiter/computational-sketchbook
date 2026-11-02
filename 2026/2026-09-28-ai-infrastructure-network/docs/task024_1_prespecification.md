# Task 024.1 Pre-Specification Protocol: Calibrated Cross-Domain Dependency Paths & Non-Tautological Falsification

**Status:** Pre-Specified & Committed Prior to Analysis Execution  
**Date:** September 30, 2026  
**Data Freeze Baseline:** Commit [`42f9a74`](https://github.com/admiralorbiter/computational-sketchbook/commit/42f9a74)  

---

## 1. Context & Motivation

External review of Task 024 (commit `70a3c8c`) identified critical methodological limitations in the initial implementation:
1. **The Zero-Baseline Fallacy:** Calculating percentage gain ($\% \Delta = \frac{\text{Join} - 0}{0}$) as $+100\%$ or $+\infty$ is mathematically uninformative. Comparing a financial graph (defined to omit physical facilities) with a joined graph containing facilities proves that dimensions were merged; it does not prove emergent systemic risk.
2. **Hardcoded Targets vs. Graph Traversal:** In the initial engine, downstream facilities (`PF1`, `Denton`, `Dalton`, `Muskogee`, `Marble`, `Austin`) and debt amounts (`$3.940B`) were declared in a configuration dictionary rather than traversed algorithmically across typed graph edges.
3. **Connectivity vs. Causal Transmission:** Summing all debt across the 63-node connected component conflated topological graph reachability with financial loss transmission.
4. **Dimension Mixing & Attribution Drift:** Contracted critical IT MW (400 MW at PF1) was mixed with utility service MW (826 MW at CORZ) into a synthetic 1,226 MW hybrid. Unallocated corporate DDTLs ($13.643B) were loosely characterized as facility debt.

This pre-specification protocol defines the rigorous, non-tautological experimental rules for **Task 024.1: Calibrated Cross-Domain Dependency Paths**.

---

## 2. Admissible Graph Traversal Rules

All reachability in Task 024.1 must be computed **purely via algorithmically traversed, typed graph edges**. No target facility or debt volume may be hardcoded.

### Admissible Path Sequences:

1. **Hyperscaler Demand Shock (`MSFT`):**
   $$\text{Customer} \xrightarrow[\text{recognized\_revenue}]{\text{contract}} \text{Tenant} \xrightarrow[\text{equity\_ownership}]{\text{hierarchy}} \text{Tenant SPV} \xrightarrow[\text{lease / colocation}]{\text{contract}} \text{Landlord} \xrightarrow[\text{direct\_lease}]{\text{link}} \text{Facility} \xrightarrow[\text{power\_service}]{\text{grid}} \text{Utility} \xrightarrow[\text{transmission}]{\text{grid}} \text{RTO}$$

2. **GPU Collateral Value Depletion (`ASM-GPU-MTM` / `GPU_COLLATERAL`):**
   $$\text{Asset Class} \xrightarrow[\text{secures}]{\text{lien}} \text{Credit Facility} \xrightarrow[\text{borrower}]{\text{debt}} \text{DDTL SPV} \xrightarrow[\text{recourse}]{\text{guaranty}} \text{Parent} \xrightarrow[\text{tenant}]{\text{lease}} \text{Facility} \xrightarrow[\text{power}]{\text{grid}} \text{Utility}$$

3. **Transmission Substation Delay (`MDU`):**
   $$\text{Utility} \xrightarrow[\text{power\_service}]{\text{grid}} \text{Facility} \xrightarrow[\text{direct\_project\_financing}]{\text{link}} \text{Project Debt} \xrightarrow[\text{creditor}]{\text{debt}} \text{Lenders} \xrightarrow[\text{shortfall\_guaranty}]{\text{guaranty}} \text{Parent}$$

---

## 3. Metric Definitions & Nomenclature

1. **Elimination of $+100\%$ / $+\infty$ on Absent Dimensions:**
   - Where a metric dimension is structurally unmodeled in a single-layer baseline (e.g. MW in $G_{\text{fin}}$, Debt in $G_{\text{phys}}$), the comparison shall be labeled:
     $$\textbf{Not Representable in Isolated Layer} \longrightarrow \textbf{Representable in Joined Graph}$$
   - No percentage gain shall be computed with a zero denominator.

2. **Component Perimeter vs. Direct Path Attribution:**
   - **`connected_component_financial_perimeter_b`**: The total debt residing within the undirected connected component. *Disclaimer: Measures topological cluster perimeter, not financial shock loss.*
   - **`directly_attributed_facility_debt_b`**: The debt principal directly allocated to the traversed facility via `obligation_facility_links.parquet` with verified Class A/B evidence claims.

3. **Strict Separation of Power Dimensions:**
   - **`utility_service_capacity_mw`**: Gross utility substation/service capacity (e.g. PF1 = 350.0 MW; CORZ = 826.0 MW; Total = 1,176.0 MW).
   - **`critical_it_contracted_mw`**: Contracted tenant IT power (e.g. PF1 = 400.0 MW; CORZ = 590.0 MW; Total = 990.0 MW).
   - *Invariant:* These dimensions must never be summed into a hybrid scalar.

4. **Normalized Graph Metrics:**
   - Articulation points and bridges must be reported as both raw counts and percentage shares of total layer nodes ($\frac{N_{\text{art}}}{N}$).

---

## 4. Three Pre-Specified Falsification Criteria

The thesis *"The risk lives in the JOIN"* shall be evaluated against three discriminating criteria:

### Criterion 1: Cross-Layer Path Reconstructibility
- **Rule:** The joined graph must discover evidence-backed, typed dependency paths between the initiating shock and downstream physical/financial exposures that have **Path Reconstructibility = False** in every single constituent layer ($G_{\text{fin}}$, $G_{\text{cont}}$, $G_{\text{phys}}$).
- **Falsification Threshold:** If any admissible cross-layer path can be fully reconstructed from a single isolated layer, or if zero admissible paths connect the shock to physical/financial endpoints, Criterion 1 fails.

### Criterion 2: Physical Facility Cut-Vertex Identification
- **Rule:** The cross-layer join must reveal at least **three (3) physical data center facilities** as formal network articulation points (cut-vertices) whose severance fragments the network and disconnects power nodes from capital providers.
- **Falsification Threshold:** If $N_{\text{fac\_art}} < 3$, Criterion 2 fails.

### Criterion 3: Null Model Concentration Significance ($p < 0.05$)
- **Rule:** Under a degree-preserving bipartite configuration null model ($N=1,000$ permutations of facility-to-contract assignments), the empirical CoreWeave tenant concentration (1,176.0 MW utility / 990.0 MW IT) and ERCOT grid concentration (3,164.0 MW / 71.89%) must exceed the 95th percentile ($p < 0.05$) of randomized network topologies.
- **Falsification Threshold:** If empirical concentration is statistically indistinguishable from random graph joining ($p \ge 0.05$), Criterion 3 fails.

---

## 5. Protocol Sealing

This protocol is committed to version control **prior** to the execution of the calibrated Task 024.1 analysis engine. Any modification to these thresholds after execution constitutes an invalid post-hoc adjustment.
