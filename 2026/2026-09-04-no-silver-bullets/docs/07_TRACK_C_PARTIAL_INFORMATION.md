# 07 — Track C: Partial-Information Bridge

## 1. Research Question

Can a method compute from $N$ alone a compact set of constraints about a hidden factor that crosses a known lattice/small-root recovery threshold?

---

## 2. Leakage Boundary

```text
+-------------------------+
|     PROPOSER PROCESS    |
| Receives: N, config     |
| Outputs: constraints    |
+-------------------------+
             |
             v
+-------------------------+
|    EVALUATOR PROCESS    |
| Receives: constraints,  |
|           hidden p, q   |
| Outputs: accuracy/gain  |
+-------------------------+
```

The proposer must never receive evaluator feedback that directly leaks factor bits for hidden holdout instances.

---

## 3. Positive-Control Calibration Ladder

Before exploratory search, calibrate the recovery backend using oracle-provided partial bits:
* Reveal 25%, 35%, 45%, ~50% of one factor;
* Test contiguous MSB, contiguous LSB, and fragmented blocks;
* Measure recovery rate and runtime to map the practical threshold of the implementation.

---

## 4. Constraint Schema

Candidate statements:
* **Bit Block**: $\text{bits}[p, \text{start}:\text{end}] = v$
* **Interval**: $L \le p < U$
* **Congruence**: $p \equiv a \pmod m$
* **Approximation**: $|p - \hat{p}| < B$
* **Polynomial**: $f(p, x, \dots)$ has a small root modulo $N$ or $p$.

---

## 5. Canaries & Promotion Criteria

* **C-CANARY-1**: Oracle MSB information recovers factor exactly.
* **C-CANARY-2**: Insufficient information cleanly reports failure rather than hallucinating success.
* **C-CANARY-3**: Sealed boundary blocks truth access in proposer.
* **Promotion**: Must beat zero-information baseline on hidden validation, generalize across independent moduli, and improve downstream exact recovery.
