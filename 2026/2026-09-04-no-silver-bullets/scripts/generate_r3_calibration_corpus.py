"""Deterministic generator for R3-G3 public baseline calibration corpus (v005_r3_calibration).

Generates 10 balanced random semiprimes per size class (60, 70, 80, 90 decimal digits; 40 total).
Binds:
- Master seed string: NSB-R3-CALIBRATION-CORPUS-20260904-V001
- Strict digit lengths: len(str(N)) in {60, 70, 80, 90}
- Balanced factor lengths: len(str(p)) == len(str(q)) == digits // 2
- Fermat distance safety: |p - q| > 10^(digits // 4)
- Global pairwise coprimality: gcd(Ni, Nj) == 1 for all i != j
- Global factor uniqueness: all 80 primes distinct
- Verifiable SHA-256 manifest
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from typing import Any, Dict, List, Set, Tuple

import gmpy2

from nsb.benchmarks.corpus import TRIPWIRE_CONTENT, TRIPWIRE_FILENAME
from nsb.core.hashing import hash_file

MASTER_SEED_STRING = "NSB-R3-CALIBRATION-CORPUS-20260904-V001"
TARGET_DIGITS = [60, 70, 80, 90]
COUNT_PER_SIZE = 10


def generate_prime_in_range(low: int, high: int, rng: random.Random) -> int:
    """Generate prime uniformly in [low, high] using gmpy2.is_prime."""
    while True:
        candidate = rng.randint(low, high)
        if candidate % 2 == 0:
            candidate += 1
        if candidate > high:
            candidate = low if low % 2 != 0 else low + 1
        p = int(gmpy2.next_prime(candidate))
        if low <= p <= high:
            return p


def generate_balanced_semiprime(
    digits: int,
    rng: random.Random,
    used_primes: Set[int],
) -> Tuple[int, int, int]:
    """Generate balanced semiprime N = p * q with exact digit length."""
    d = digits // 2
    low = int(math.isqrt(10 ** (2 * d - 1))) + 1
    high = 10**d - 1
    min_diff = 10 ** (digits // 4)

    for _ in range(10000):
        p = generate_prime_in_range(low, high, rng)
        if p in used_primes:
            continue
        q = generate_prime_in_range(low, high, rng)
        if q in used_primes or q == p:
            continue

        if p > q:
            p, q = q, p

        if (q - p) < min_diff:
            continue

        N = p * q
        s_N = str(N)
        if len(s_N) == digits and len(str(p)) == d and len(str(q)) == d:
            used_primes.add(p)
            used_primes.add(q)
            return N, p, q

    raise RuntimeError(f"Failed to generate balanced semiprime for {digits} digits after 10000 attempts.")


def build_corpus(master_seed_str: str = MASTER_SEED_STRING) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Deterministically generate the 40 calibration instances."""
    seed_int = int(hashlib.sha256(master_seed_str.encode("utf-8")).hexdigest()[:16], 16)
    rng = random.Random(seed_int)

    public_instances: List[Dict[str, Any]] = []
    sealed_instances: List[Dict[str, Any]] = []
    used_primes: Set[int] = set()
    moduli: List[int] = []

    for digits in TARGET_DIGITS:
        for idx in range(1, COUNT_PER_SIZE + 1):
            inst_id = f"R3-CALIB-D{digits:03d}-{idx:05d}"
            N, p, q = generate_balanced_semiprime(digits, rng, used_primes)
            moduli.append(N)

            pub = {
                "instance_id": inst_id,
                "digits": digits,
                "family": "balanced_semiprime",
                "N": str(N),
                "metadata": {
                    "master_seed": master_seed_str,
                    "digits": digits,
                    "approx_bits": N.bit_length(),
                    "index": idx,
                },
            }
            seal = {
                "instance_id": inst_id,
                "digits": digits,
                "N": str(N),
                "p": str(p),
                "q": str(q),
            }
            public_instances.append(pub)
            sealed_instances.append(seal)

    # Invariant assertions
    # 1. Total count
    assert len(public_instances) == len(TARGET_DIGITS) * COUNT_PER_SIZE == 40
    # 2. Pairwise coprimality
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            g = math.gcd(moduli[i], moduli[j])
            assert g == 1, f"Coprimality violation between {public_instances[i]['instance_id']} and {public_instances[j]['instance_id']}: gcd={g}"
    # 3. Factor uniqueness
    assert len(used_primes) == 80

    return public_instances, sealed_instances


def write_corpus(
    repo_root: Path,
    public_instances: List[Dict[str, Any]],
    sealed_instances: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Write public, sealed, and manifest files."""
    version = "v005_r3_calibration"
    split = "public_calibration"

    pub_dir = repo_root / "benchmarks" / "public" / version / split
    seal_dir = repo_root / "benchmarks" / "sealed" / version / split
    pub_dir.mkdir(parents=True, exist_ok=True)
    seal_dir.mkdir(parents=True, exist_ok=True)

    # Tripwire
    tw_file = seal_dir / TRIPWIRE_FILENAME
    tw_file.write_text(TRIPWIRE_CONTENT, encoding="utf-8")

    # Instances
    pub_file = pub_dir / "instances.jsonl"
    with open(pub_file, "w", encoding="utf-8") as f:
        for inst in public_instances:
            f.write(json.dumps(inst) + "\n")

    seal_file = seal_dir / "truth.jsonl"
    with open(seal_file, "w", encoding="utf-8") as f:
        for inst in sealed_instances:
            f.write(json.dumps(inst) + "\n")

    pub_sha = hash_file(pub_file)
    seal_sha = hash_file(seal_file)

    manifest = {
        "benchmark_version": version,
        "split": split,
        "master_seed": MASTER_SEED_STRING,
        "total_instances": len(public_instances),
        "target_digit_sizes": TARGET_DIGITS,
        "instances_per_size": COUNT_PER_SIZE,
        "public_file": f"benchmarks/public/{version}/{split}/instances.jsonl",
        "public_sha256": pub_sha,
        "sealed_file": f"benchmarks/sealed/{version}/{split}/truth.jsonl",
        "sealed_sha256": seal_sha,
    }

    manifest_file = pub_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Also write canonical repo-level config file for direct runner lookup
    config_dir = repo_root / "config" / "baselines"
    config_dir.mkdir(parents=True, exist_ok=True)
    corpus_summary = {
        "benchmark_version": version,
        "split": split,
        "master_seed": MASTER_SEED_STRING,
        "manifest_sha256": hash_file(manifest_file),
        "public_sha256": pub_sha,
        "instances": public_instances,
    }
    (config_dir / "r3_calibration_corpus.json").write_text(
        json.dumps(corpus_summary, indent=2), encoding="utf-8"
    )

    print(f"Generated {len(public_instances)} instances.")
    print(f"Public file: {pub_file} (SHA: {pub_sha})")
    print(f"Sealed file: {seal_file} (SHA: {seal_sha})")
    print(f"Manifest written to: {manifest_file}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate R3 baseline calibration corpus")
    parser.add_argument("--repo-root", type=str, default=".")
    parser.add_argument("--verify", action="store_true", help="Verify existing corpus without re-generating")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    pub_inst, seal_inst = build_corpus()

    if args.verify:
        manifest_file = repo_root / "benchmarks" / "public" / "v005_r3_calibration" / "public_calibration" / "manifest.json"
        if not manifest_file.exists():
            print("ERROR: Manifest not found.")
            sys.exit(1)
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        pub_file = repo_root / "benchmarks" / "public" / "v005_r3_calibration" / "public_calibration" / "instances.jsonl"
        calc_sha = hash_file(pub_file)
        if calc_sha != manifest["public_sha256"]:
            print(f"ERROR: SHA mismatch: {calc_sha} != {manifest['public_sha256']}")
            sys.exit(1)
        print(f"Verified corpus successfully: {manifest['total_instances']} instances, SHA={calc_sha}")
        return

    write_corpus(repo_root, pub_inst, seal_inst)


if __name__ == "__main__":
    main()
