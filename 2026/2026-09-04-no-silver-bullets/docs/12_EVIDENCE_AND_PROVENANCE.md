# 12 — Evidence, Provenance, and Audit

## 1. Scientific Source of Truth

Git commits + immutable raw artifacts + append-only SQLite event ledger. Chat logs, ephemeral runner stdout, and Director prose are not truth.

---

## 2. Cryptographic Hashing

All inputs, manifests, and outputs are indexed with SHA-256 hashes:
* Config YAML SHA-256;
* Public benchmark dataset hash;
* Sealed ground-truth hash;
* Raw candidate artifact hash;
* Result and canonical metric hash.

---

## 3. Environment Fingerprint

Every execution records:
* OS and kernel version;
* Python interpreter and package lock hash;
* Compiler toolchain (if any);
* CPU model, physical/logical cores;
* Total and available system RAM;
* Solvers / library versions (`gmpy2`, `pysat`, `z3`, etc.);
* Active environment variables (filtered for sentinels).

---

## 4. Audit Checklist

* **Integrity**: Manifest complete, commit matches, config hash verified, artifact hashes match.
* **Benchmark**: Correct dataset version, correct split, zero unauthorized accesses to sealed files.
* **Accounting**: All runs included, timeouts retained as data, seeds recorded, matched compute ceilings.
* **Scientific Conduct**: No post-hoc metric replacement, no cherry-picking, no benchmark-specific constants in algorithm code.
