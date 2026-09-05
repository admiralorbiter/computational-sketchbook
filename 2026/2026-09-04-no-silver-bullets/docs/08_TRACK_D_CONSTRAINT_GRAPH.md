# 08 — Track D: Constraint-Graph Inversion

## 1. Research Question

Is direct inversion of multiplication hard partly because the standard binary/carry encoding creates an unnecessarily difficult constraint graph?

---

## 2. Search Object: The Encoding

The search target is the arithmetic encoding, not merely solver flags:
* Schoolbook binary;
* Block multiplication;
* Carry-save intermediate forms;
* Redundant/signed-digit representations;
* Radix alternatives;
* Graph/tensor formulations localizing carry propagation.

Any encoding must be strictly semantically equivalent to $p \cdot q = N$ over the factor domain.

---

## 3. Dual Evaluators

* **D1 — Semantic Verifier**: For small inputs (8–20 bits), enumerate or sample assignments to prove equivalence.
* **D2 — Performance Evaluator**: Measure variables, clauses, graph edges, treewidth approximations, solver decisions/conflicts, CPU time, and peak memory.

---

## 4. Canaries & Pilot D-P1

* **D-CANARY-1**: Semantic equivalence on 8–20-bit toy multiplication.
* **D-CANARY-2**: 20–32-bit balanced semiprime; solver recovers valid factors.
* **D-CANARY-3**: Injected malformed carry caught by semantic verifier.
* **Pilot D-P1**: Bit sizes 24, 32, 40, 48, 56, 64, 72. Primary metric: `median solve CPU time`.

---

## 5. Promotion Criteria

Promote an encoding if semantic equivalence is proven on canaries, solve time improves $\ge 2\times$ over baseline at matched solver settings across $\ge 3$ adjacent bit sizes, and structural graph diagnostics provide a plausible mechanism.
