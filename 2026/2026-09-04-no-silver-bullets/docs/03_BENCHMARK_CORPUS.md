# 03 — Benchmark Corpus

## 1. Why the Benchmark is the Center of the Project

Alternative factoring methods are extremely easy to overfit to:
* Unusually close primes ($|p - q| \ll \sqrt{N}$);
* Smooth $p-1$ or $p+1$;
* Favorable random seeds;
* Tiny bit ranges;
* Handcrafted examples;
* Proxy metrics that do not predict final factorization.

The corpus must therefore contain both known-weak controls and balanced random holdout cases.

---

## 2. Corpus Families

* **Family R — Balanced Random**: $p$ and $q$ are independently generated odd primes with near-equal bit length and no deliberate weakness. Primary research distribution.
* **Family F — Fermat-Positive Control**: $p$ and $q$ chosen close enough that Fermat factorization succeeds quickly. Proves the harness registers structural algorithmic advantages.
* **Family P1 — $p-1$ Positive Control**: Prime $p$ generated with a controlled smoothness profile for $p-1$. Proves structured-factor handling.
* **Family C — Partial-Information Control**: Balanced random semiprimes paired with evaluator-only mechanisms that expose declared bit patterns for calibrating recovery thresholds.
* **Family E — Encoding Controls**: Tiny balanced semiprimes chosen to exercise specific multiplication and carry patterns for validating Track D encodings.

---

## 3. Bit-Size Ladder

* **Canary Ladder (Gate 0)**: 32, 40, 48, 56, 64, 72, 80 bits. (Runtime: seconds to minutes).
* **Pilot Ladder (Gate 1)**: 64, 80, 96, 112, 128 bits (optionally 144/160 bits for cheap methods).
* **Search Ladder (Gate 2)**: Track-specific. Advancement is earned, not assumed. No track may jump directly to large moduli based on a single small “hero” instance.

---

## 4. Minimum Sample Design

For a pilot comparing scaling:
* $\ge 10$ balanced-random instances per bit size;
* $\ge 5$ independent algorithm seeds where stochasticity matters;
* Development / validation / holdout splits fixed prior to search:
  * Development: 40 instances/size;
  * Validation: 20 instances/size;
  * Hidden holdout: 20 instances/size.

---

## 5. Storage & Sealed Separation

Benchmark structure:
```text
benchmarks/
  public/
    v001/
      instances.jsonl
  sealed/
    v001/
      truth.jsonl
```

* **Public record**: `{"instance_id": "R-096-00017", "family": "R", "bits": 96, "N": "..."}`
* **Sealed record**: `{"instance_id": "R-096-00017", "p": "...", "q": "...", "generation_seed": 123456}`

Research-track processes receive only the public directory. Sealed truth is accessible only to the verifier and auditor.

---

## 6. Corpus Invariants

For balanced random instances:
* $p \ne q$;
* $|\text{bitlen}(p) - \text{bitlen}(q)| \le 1$;
* $N = p \cdot q$;
* Both factors pass deterministic/probabilistic primality checks;
* No deliberate closeness or smoothness constraints;
* Generator version and RNG seeds recorded.

---

## 7. Leakage Canaries

Poison files and canary paths detect improper access. Any attempt by research-track code to access sealed files or sentinel environment variables triggers an automatic audit failure and invalidates the run.
