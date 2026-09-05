# 13 — Implementation Plan

## Phase 0 — Repository Skeleton & Foundation (Current)
* Directory layout, documentation, schemas (`experiment.schema.json`, `result.schema.json`).
* Configuration defaults (`config/defaults.yaml`, `config/smoke.yaml`).
* SQLite ledger database initialization (`state/experiments.sqlite`).
* Packaging setup (`pyproject.toml`) and environment validation.

## Phase 1 — Benchmark Generator & Exact Verifier
* Prime generator supporting balanced random semiprimes (Family R) and control families (F, P1, C, E).
* Sealed vs public file isolation (`benchmarks/public/` vs `benchmarks/sealed/`).
* Exact factor verification, primality verification, and leakage tripwires.

## Phase 2 — Resource-Aware Runner
* Subprocess execution with hard wall-time, CPU-time, and memory limits.
* Capture of stdout/stderr, environment fingerprint, and SHA-256 artifact hashing.
* Result schema validation and clean timeout/failure recording.

## Phase 3 — Baseline Adapters
* Native implementations of Fermat factorization, Pollard $\rho$, and Pollard $p-1$.
* Control suite verification.

## Phase 4 — Track D: Constraint Graph
* Toy multiplication SAT/CSP encoder with standard schoolbook adder constraints.
* Semantic equivalence verifier for tiny inputs (8–20 bits).
* Solvers interface (`python-sat`, `z3-solver`).

## Phase 5 — Track C: Partial Information Bridge
* Oracle partial-bit generator (MSB/LSB/blocks).
* Recovery backend using lattice/small-root methods.
* Sealed evaluator scoring information gain and downstream success.

## Phase 6 — Track B: Algebraic Evolution Evaluator
* Candidate representation schema (polynomial pairs mod $N$).
* Multi-fidelity cascade: B0 validity, B1 proxy, B2 micro-sieve.
* Baseline candidate generator.

## Phase 7 — Track A: Tensor/Lattice Laboratory
* Lattice builder with tunable scaling.
* Baseline reduction (LLL) and Babai-like neighborhood sampler.
* Relation evaluator, deduplicator, and dependency solver.

## Phase 8 — Smoke Suite & Review Packet Generator
* End-to-end smoke command (`python -m nsb.run --config config/smoke.yaml`).
* Review packet generator producing executive summary, track metrics, and audit verdict.

## Phase 9 — Research Director v0
* Proposal-only engine generating schema-compliant experiment proposals from canonical metric feedback.
