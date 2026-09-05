# Track B Post-Hoc Oracle-Grid Diagnostic Report (B0-Filtered Correction)
## Systematic 35-Slot Grid Analysis Restricted to Feasible B0-Valid Representations

**Generated**: 2026-09-04T15:45:17.399299+00:00  
**Diagnostic Scope**: Evaluation of all 35 generated candidate slots restricted strictly to the feasible Level $B_0$-valid subset ($30$ valid candidates per modulus; $5$ positive translations $m+1 \dots m+5$ rejected by $B_0$ leading-coefficient check) for empirical Level B3 relation yield ($A=100, B=20, FB=250$) across all 150 moduli of `v004_wave2/search_holdout` and `v002_wave2/confirmatory` ($300$ moduli total, $9,000$ feasible evaluations).  

---

## 1. Executive Summary & Diagnostic Decision Fork

### Feasible Oracle Floor vs Frozen Candidate Selector Floor (`v004_wave2`):
- **64-bit Cohort**: Feasible Oracle Floor = **100.0%** (30/30) vs Candidate Selector Floor = **43.3%** (13/30)
- **80-bit Cohort**: Feasible Oracle Floor = **30.0%** (9/30) vs Candidate Selector Floor = **3.3%** (1/30)
- **96-bit Cohort**: Feasible Oracle Floor = **0.0%** (0/30) vs Candidate Selector Floor = **0.0%** (0/30)

> [!IMPORTANT]
> **STRATEGIC VERDICT**: Within the frozen 35-slot local translation/rotation neighborhood, restricted to its B0-valid subset, and under the fixed A=100, B=20, FB=250 micro-sieve assay, even the empirical oracle fails the 50% relation floor at 80 bits (30.0% in v004, 23.3% in v002) and reaches zero yield at 96 bits (0.0% in both corpora). At 64 bits, a selector gap is confirmed: the feasible oracle reaches 100.0% (30/30). While the B1+α candidate selector fails the floor at 43.3% (13/30) and canonical base-m at 30.0% (9/30), the Murphy-E proxy barely clears the floor with 56.7% (17/30 moduli, 23 total relations). However, neither prospective selector approaches the oracle's 30/30 coverage, and neither provides a path through 80/96 bits. Because the search space is exhausted at 80 and 96 bits, further micro-objective optimization on this local search family cannot rescue the scaling regime.

---

## 2. v004_wave2/search_holdout: Feasible Cohort Performance & Regret

| Bit Size | Feasible Oracle Yield | Cand Yield | Murphy Yield | Base Yield | Cand Regret | Cand Avg Rank | Murphy Avg Rank | Feasible Oracle Floor % | Cand Floor % | Base Floor % |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **32b** | 0.054048 | 0.041043 | 0.041203 | 0.026891 | +0.013005 | 6.7 / 30 | 6.3 / 30 | **100.0%** (30/30) | 100.0% | 100.0% |
| **48b** | 0.006989 | 0.004975 | 0.002268 | 0.003415 | +0.002014 | 6.8 / 30 | 16.3 / 30 | **100.0%** (30/30) | 100.0% | 100.0% |
| **64b** | 0.000733 | 0.000293 | 0.000307 | 0.000173 | +0.000440 | 12.6 / 30 | 10.9 / 30 | **100.0%** (30/30) | 43.3% | 30.0% |
| **80b** | 0.000120 | 0.000013 | 0.000013 | 0.000000 | +0.000107 | 15.2 / 30 | 15.2 / 30 | **30.0%** (9/30) | 3.3% | 0.0% |
| **96b** | 0.000000 | 0.000000 | 0.000000 | 0.000000 | +0.000000 | 15.5 / 30 | 15.5 / 30 | **0.0%** (0/30) | 0.0% | 0.0% |

---

## 3. Correlation Structure Over Feasible B0-Valid Representations

Spearman ($\rho$) and Kendall ($\tau$) rank correlations across all evaluated $B_0$-valid representation-modulus pairs per cohort in `v004`:

| Cohort | Metric | Level B1 Log-Norm | Murphy $\alpha$ | B1 + $\alpha$ Score | Approximate Murphy-$E$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **32b** | Spearman $\rho$ | -0.5025 | -0.5666 | -0.5521 | 0.5824 |
| | Kendall $\tau$ | -0.3454 | -0.3943 | -0.3853 | 0.4066 |
| **48b** | Spearman $\rho$ | -0.479 | -0.411 | -0.5188 | -0.2145 |
| | Kendall $\tau$ | -0.3461 | -0.2911 | -0.3772 | -0.1467 |
| **64b** | Spearman $\rho$ | -0.1731 | -0.1773 | -0.1915 | 0.2051 |
| | Kendall $\tau$ | -0.1393 | -0.1426 | -0.1542 | 0.1649 |
| **80b** | Spearman $\rho$ | 0.0234 | -0.0685 | 0.0168 | -0.0158 |
| | Kendall $\tau$ | 0.0191 | -0.056 | 0.0137 | -0.0129 |
| **96b** | Spearman $\rho$ | N/A | N/A | N/A | N/A |
| | Kendall $\tau$ | N/A | N/A | N/A | N/A |

---

## 4. Operation Frequencies Among Feasible Oracle Winners

Distribution of winning operations (Canonical base-$m$ vs Feasible Negative Translations vs Rotations) across active moduli ($>0$ relations) in `v004`:

| Cohort | Active Moduli | Canonical Base-$m$ | Feasible Translations ($m - k$) | Linear Rotations ($u, v$) |
| :---: | :---: | :---: | :---: | :---: |
| **32b** | 30/30 | 0 (0.0%) | 6 (20.0%) | 24 (80.0%) |
| **48b** | 30/30 | 2 (6.7%) | 4 (13.3%) | 24 (80.0%) |
| **64b** | 30/30 | 0 (0.0%) | 3 (10.0%) | 27 (90.0%) |
| **80b** | 9/30 | 0 (0.0%) | 0 (0.0%) | 9 (100.0%) |
| **96b** | 0/30 (Zero Relations) | 0 | 0 | 0 |

---

## 5. Cross-Corpus Comparison (`v002_wave2/confirmatory` vs `v004_wave2/search_holdout`)

Comparison of Feasible Oracle Floor % and Mean Oracle Yield across both independent 150-modulus corpora:

| Bit Size | v002 Feasible Oracle Floor % | v004 Feasible Oracle Floor % | v002 Feasible Oracle Yield | v004 Feasible Oracle Yield | v002 Cand Floor % | v004 Cand Floor % |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **32b** | 100.0% (30/30) | 100.0% (30/30) | 0.057196 | 0.054048 | 100.0% | 100.0% |
| **48b** | 100.0% (30/30) | 100.0% (30/30) | 0.007590 | 0.006989 | 100.0% | 100.0% |
| **64b** | 100.0% (30/30) | 100.0% (30/30) | 0.000787 | 0.000733 | 63.3% | 43.3% |
| **80b** | 23.3% (7/30) | 30.0% (9/30) | 0.000093 | 0.000120 | 6.7% | 3.3% |
| **96b** | 0.0% (0/30) | 0.0% (0/30) | 0.000000 | 0.000000 | 0.0% | 0.0% |

---

## 6. Strategic Takeaways & Project North Star

1. **B0 Feasibility Alignment**: Generated slots contain exactly 30 valid representations per modulus (the 5 positive translations $m+1 \dots m+5$ are mechanically invalid as $N < (m+k)^3$ reduces degree to $\le 2$, leaving $x^3$ coefficient 0). The oracle, rankings, and correlations are strictly restricted to the valid 30-representation subset.
2. **The 64-bit Selector Deficiency & Nuance**: At 64 bits, the feasible oracle clears the $50\%$ floor ($100.0\%$, 30/30 moduli), proving that higher-yield representations existed in the grid. However, the surrogate selectors ranked them on average $12.6 / 30$ ($B1+\alpha$) and $10.9 / 30$ (Murphy-$E$). B1+$\alpha$ fails the relation floor ($13/30 = 43.3\%$), while Murphy-$E$ barely clears it ($17/30 = 56.7\%$, with 23 relations vs 22 for B1+$\alpha$). Neither prospective selector approaches the empirical oracle's $30/30$ coverage, and neither provides a viable path through 80/96 bits.
3. **The 80-bit and 96-bit Search Space Collapse**: At 80 bits, the feasible oracle hits only $30.0\%$ ($9/30$ in v004, $23.3\%$ in v002), and at 96 bits reaches $0.0\%$ ($0/30$ in both corpora). Even the empirical oracle fails the floor.
4. **Roadmap Decision**: The local translation/rotation search family is **PARKED**. The project will not conduct further micro-objective tweaking; Track B transitions toward materially broader polynomial selection and mature NFS relation-collection baselines (CADO-NFS / realistic factoring machinery).