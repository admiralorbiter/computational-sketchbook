# 05 — Track A: Tensor/Lattice Relation Discovery

## 1. Research Question

Can modern structured sampling improve the rate at which a Schnorr-style lattice construction yields useful factorization relations?

---

## 2. Pipeline

```text
N
 |
small-prime basis / parameters
 |
lattice construction
 |
basis reduction / approximation
 |
candidate neighborhood or low-energy sampler
 |
candidate -> arithmetic relation
 |
smoothness / relation verifier
 |
relation database
 |
dependency / congruence-of-squares stage
 |
factor attempt
```

---

## 3. Modules

* **A1 — Lattice Builder**: Generates integer/rational lattice basis from $N$, factor base size, and scaling parameters. Invariant: Builder has no access to hidden factors.
* **A2 — Baseline Generator**: Reduction (LLL) and Babai-like approximate closest vector with bounded local perturbations.
* **A3 — Structured Sampler**: Modular samplers (tensor-network low-energy search, beam search, stochastic local search).
* **A4 — Relation Evaluator**: Smoothness tests against factor base, full/partial relation classification, deduplication, and cost tracking.
* **A5 — Relation Combiner**: Dependency matrix construction and factor extraction.

---

## 4. Canaries & Pilot A-P1

* **A-CANARY-1**: Handcrafted tiny modulus yielding known valid relation.
* **A-CANARY-2**: 32–48 bit synthetic semiprime; pipeline reaches exact factor on positive control.
* **A-CANARY-3**: No-leak test blocking sealed truth access.
* **Pilot A-P1**: Bit sizes 48, 56, 64, 72, 80, 88, 96. Primary metric: `unique_verifier_valid_relations / CPU_second`.

---

## 5. Promotion Criteria

Promote a sampler if:
* $\ge 1.5\times$ relation rate gain over baseline on validation set across 3 adjacent bit sizes;
* No $> 25\%$ regression in relation independence/diversity;
* Improvement survives at least 3 random seeds.
