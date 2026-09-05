# 06 — Track B: Evolved Algebraic Representations

## 1. Research Question

Can automated program/evolutionary search discover algebraic representations of arbitrary semiprimes that produce better smoothness/relation yield than conventional candidate-generation strategies?

---

## 2. Evaluation Cascade (Multi-Fidelity)

* **Level B0 — Validity Filter**: Reject immediately if coefficients are invalid, modular relationship fails, or degree/reducibility rules fail.
* **Level B1 — Cheap Proxy**: Compute algebraic norm diagnostics, root properties, and Murphy-style $\alpha / E$ metrics.
* **Level B2 — Empirical Micro-Sieve**: Run a tiny fixed sieve/sample measuring actual smooth relation yield.
* **Level B3 — Downstream Test**: Run full relation gathering and dependency solving on top candidates.

*The director never promotes on Level B1 alone.*

---

## 3. Evolutionary Loop

```text
seed generators
   |
generate candidates
   |
validity filter (B0)
   |
proxy score (B1)
   |
micro-sieve (B2)
   |
Pareto frontier
   |
mutate / recombine generator programs
   |
repeat
```

---

## 4. Canaries & Pilot B-P1

* **B-CANARY-1**: Known invalid candidate rejected deterministically.
* **B-CANARY-2**: Known valid representation scored consistently.
* **B-CANARY-3**: Deterministic ranking and raw micro-sieve data retention on small synthetic $N$.
* **Pilot B-P1**: Matched sieve budget comparing baseline vs evolved generator. Primary metric: `valid_unique_relations / total_CPU_second`.

---

## 5. Promotion Criteria

Promote a generator lineage if validation relation yield improves by $\ge 25\%$ at matched CPU budget across unseen moduli, and the gain is not erased by downstream tests.
