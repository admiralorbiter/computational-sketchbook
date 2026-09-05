# 10 — Smoke Test and Canary Plan

## 1. Goal

The smoke suite finishes quickly ($\le 10$ minutes on standard development hardware) to verify plumbing, baselines, and canaries before any serious compute is scheduled.

---

## 2. Smoke Suite Phases

* **Phase S0 — Environment**: Python runtime, solver/factoring binaries, hardware specs, SQLite writable, git commit clean/recorded.
* **Phase S1 — Benchmark Generator**: Generate fixed-seed synthetic instances: 2 balanced random each at 32/40/48 bits; 1 Fermat control (48-bit); 1 $p-1$ control (48-bit); 1 partial-bit control (48-bit). Verify public/sealed separation.
* **Phase S2 — Baseline Controls**: Run trivial baseline, Fermat on close-prime control, $p-1$ on smooth control, and general small baseline. Verify correct method/structure matching.
* **Phase S3 — Track Canaries**:
  * Track A: Construct lattice, generate candidate, validate $\ge 1$ relation.
  * Track B: Validate representation, reject invalid one, compute proxy + micro-yield.
  * Track C: Oracle partial-bit recovery succeeds; insufficient information fails cleanly.
  * Track D: Semantic equivalence on toy encoding; solve tiny semiprime.
* **Phase S4 — Director Dry Run**: Director receives synthetic metrics and emits one schema-valid proposal per track (no automatic execution in smoke).
* **Phase S5 — Audit Packet**: Generate review packet with manifest, results, metrics, audit verdict, and status summary.

---

## 3. Smoke Command

```powershell
python -m nsb.run --config config/smoke.yaml
```

The command exits with a non-zero exit code if any required canary fails.
