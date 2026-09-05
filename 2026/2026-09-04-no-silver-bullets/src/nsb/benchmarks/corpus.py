"""Corpus storage, isolation, and serialization management."""

import hashlib
import json
import math
from pathlib import Path
import random
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field

from nsb.benchmarks.generator import (
    generate_family_c,
    generate_family_e,
    generate_family_f,
    generate_family_p1,
    generate_family_r,
)
from nsb.core.hashing import hash_file, hash_object

TRIPWIRE_FILENAME = "TRIPWIRE_DO_NOT_READ.txt"
TRIPWIRE_CONTENT = (
    "SECURITY WARNING: This file is a tamper and leakage canary tripwire for No Silver Bullet.\n"
    "Research-track code and candidate generators MUST NEVER access this file or directory.\n"
    "Accessing this file triggers an automatic failure verdict and run invalidation.\n"
)


class PublicInstance(BaseModel):
    instance_id: str
    family: str
    bits: int
    N: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SealedTruth(BaseModel):
    instance_id: str
    p: str
    q: str
    generation_seed: int
    extra: Dict[str, Any] = Field(default_factory=dict)


def build_instance_id(family: str, bits: int, index: int) -> str:
    """Canonical instance ID: <FAMILY>-<BITS:03d>-<INDEX:05d>."""
    return f"{family.upper()}-{bits:03d}-{index:05d}"


def create_corpus_split(
    output_base_dir: Union[str, Path],
    version: str,
    split: str,
    spec: List[Dict[str, Any]],
    master_seed: int,
) -> Dict[str, Any]:
    """Generate and write public instances and sealed ground truth for a dataset split.

    Args:
        output_base_dir: Root directory of repository or benchmarks folder.
        version: Benchmark version (e.g., 'v001_smoke').
        split: Dataset split ('dev', 'val', 'holdout', 'smoke').
        spec: List of instance specifications with keys 'family', 'bit_sizes', 'count_per_size'.
        master_seed: Master RNG seed for reproducibility.

    Returns:
        Manifest dictionary with SHA-256 hashes and instance counts.
    """
    base = Path(output_base_dir)
    public_dir = base / "benchmarks" / "public" / version / split
    sealed_dir = base / "benchmarks" / "sealed" / version / split

    public_dir.mkdir(parents=True, exist_ok=True)
    sealed_dir.mkdir(parents=True, exist_ok=True)

    # Write tripwire canary file in sealed directory
    tripwire_path = sealed_dir / TRIPWIRE_FILENAME
    with open(tripwire_path, "w", encoding="utf-8") as f:
        f.write(TRIPWIRE_CONTENT)

    public_file = public_dir / "instances.jsonl"
    sealed_file = sealed_dir / "truth.jsonl"

    rng = random.Random(master_seed)
    instances_public: List[Dict[str, Any]] = []
    instances_sealed: List[Dict[str, Any]] = []
    global_used_primes: Set[int] = set()

    for entry in spec:
        family = entry["family"].upper()
        bit_sizes = entry["bit_sizes"]
        count = entry.get("count_per_size", 1)

        for bits in bit_sizes:
            for idx in range(count):
                inst_seed = rng.randint(1, 2**63 - 1)
                inst_rng = random.Random(inst_seed)
                inst_id = build_instance_id(family, bits, idx + 1)
                meta: Dict[str, Any] = {}
                extra: Dict[str, Any] = {}

                if family == "R":
                    N, p, q = generate_family_r(bits, inst_rng, used_primes=global_used_primes)
                elif family == "F":
                    N, p, q = generate_family_f(bits, inst_rng)
                    extra["delta"] = q - p
                elif family == "P1":
                    N, p, q = generate_family_p1(bits, inst_rng)
                elif family == "C":
                    N, p, q, oracle = generate_family_c(bits, inst_rng)
                    meta["oracle"] = oracle
                elif family == "E":
                    N, p, q = generate_family_e(bits, inst_rng)
                else:
                    raise ValueError(f"Unknown benchmark family: {family}")

                pub_obj = PublicInstance(
                    instance_id=inst_id,
                    family=family,
                    bits=bits,
                    N=str(N),
                    metadata=meta,
                )
                instances_public.append(pub_obj.model_dump())

                seal_obj = SealedTruth(
                    instance_id=inst_id,
                    p=str(p),
                    q=str(q),
                    generation_seed=inst_seed,
                    extra=extra,
                )
                instances_sealed.append(seal_obj.model_dump())

    # Pairwise coprimality check for all generated instances
    moduli_list = [(inst["instance_id"], int(inst["N"])) for inst in instances_public]
    for i in range(len(moduli_list)):
        for j in range(i + 1, len(moduli_list)):
            id_i, n_i = moduli_list[i]
            id_j, n_j = moduli_list[j]
            g = math.gcd(n_i, n_j)
            if g != 1:
                raise ValueError(
                    f"Corpus pairwise coprimality assertion failed between {id_i} and {id_j}: shared factor gcd = {g}"
                )

    # Write public instances.jsonl
    with open(public_file, "w", encoding="utf-8") as f:
        for row in instances_public:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")

    # Write sealed truth.jsonl
    with open(sealed_file, "w", encoding="utf-8") as f:
        for row in instances_sealed:
            f.write(json.dumps(row, separators=(",", ":")) + "\n")

    pub_hash = hash_file(public_file)
    seal_hash = hash_file(sealed_file)

    manifest = {
        "benchmark_version": version,
        "split": split,
        "master_seed": master_seed,
        "total_instances": len(instances_public),
        "public_file": str(public_file),
        "public_sha256": pub_hash,
        "sealed_file": str(sealed_file),
        "sealed_sha256": seal_hash,
    }

    manifest_path = public_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest


def load_public_instances(
    base_dir: Union[str, Path], version: str, split: str
) -> List[PublicInstance]:
    """Load public benchmark instances. Does NOT access sealed truth."""
    path = Path(base_dir) / "benchmarks" / "public" / version / split / "instances.jsonl"
    if not path.is_file():
        raise FileNotFoundError(f"Public benchmark file not found: {path}")

    instances: List[PublicInstance] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line.strip())
                instances.append(PublicInstance(**data))
    return instances


def load_sealed_truth(
    base_dir: Union[str, Path], version: str, split: str
) -> Dict[str, SealedTruth]:
    """Load sealed truth for verifier only. Never call from research-track code."""
    path = Path(base_dir) / "benchmarks" / "sealed" / version / split / "truth.jsonl"
    if not path.is_file():
        raise FileNotFoundError(f"Sealed truth file not found: {path}")

    truth_map: Dict[str, SealedTruth] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line.strip())
                obj = SealedTruth(**data)
                truth_map[obj.instance_id] = obj
    return truth_map


def generate_wave2_confirmatory_corpus(base_dir: Union[str, Path]) -> Dict[str, Any]:
    """Generate the canonical 150-modulus Wave 2 confirmatory corpus (v002_wave2/confirmatory).

    150 balanced semiprimes (Family R), 30 per size across 32, 48, 64, 80, 96 bits, master_seed=20260904.
    """
    spec = [
        {
            "family": "R",
            "bit_sizes": [32, 48, 64, 80, 96],
            "count_per_size": 30,
        }
    ]
    return create_corpus_split(
        output_base_dir=base_dir,
        version="v002_wave2",
        split="confirmatory",
        spec=spec,
        master_seed=20260904,
    )


def derive_phase2b_seed(freeze_sha: str) -> int:
    """Derive deterministic master seed for Phase 2B holdout from freeze commit SHA."""
    raw = f"{freeze_sha}:NSB-R2-WAVE2-B-PHASE2B:v003".encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF


def generate_wave2_phase2b_holdout(
    base_dir: Union[str, Path],
    freeze_sha: str,
    force: bool = False,
) -> Dict[str, Any]:
    """Generate the canonical 150-modulus Wave 2 Phase 2B holdout corpus (v003_wave2/search_holdout).

    150 balanced semiprimes (Family R), 30 per size across 32, 48, 64, 80, 96 bits.
    Master seed derived deterministically from the pre-holdout freeze commit SHA.
    """
    target_path = (
        Path(base_dir) / "benchmarks" / "public" / "v003_wave2" / "search_holdout" / "instances.jsonl"
    )
    if target_path.exists() and not force:
        raise FileExistsError(
            f"Phase 2B holdout corpus already exists at {target_path}. Pass force=True to overwrite."
        )

    seed = derive_phase2b_seed(freeze_sha)
    spec = [
        {
            "family": "R",
            "bit_sizes": [32, 48, 64, 80, 96],
            "count_per_size": 30,
        }
    ]
    return create_corpus_split(
        output_base_dir=base_dir,
        version="v003_wave2",
        split="search_holdout",
        spec=spec,
        master_seed=seed,
    )


def derive_phase2b_seed_v4(freeze_sha: str) -> int:
    """Derive deterministic master seed for Phase 2B holdout v004 from freeze commit SHA."""
    raw = f"{freeze_sha}:NSB-R2-WAVE2-B-PHASE2B:v004".encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:16], 16) & 0x7FFFFFFFFFFFFFFF


def generate_wave2_phase2b_holdout_v4(
    base_dir: Union[str, Path],
    freeze_sha: str,
    force: bool = False,
) -> Dict[str, Any]:
    """Generate the canonical 150-modulus Wave 2 Phase 2B holdout corpus (v004_wave2/search_holdout).

    150 balanced semiprimes (Family R), 30 per size across 32, 48, 64, 80, 96 bits.
    Master seed derived deterministically from the pre-holdout freeze commit SHA.
    """
    target_path = (
        Path(base_dir) / "benchmarks" / "public" / "v004_wave2" / "search_holdout" / "instances.jsonl"
    )
    if target_path.exists() and not force:
        raise FileExistsError(
            f"Phase 2B holdout corpus already exists at {target_path}. Pass force=True to overwrite."
        )

    seed = derive_phase2b_seed_v4(freeze_sha)
    spec = [
        {
            "family": "R",
            "bit_sizes": [32, 48, 64, 80, 96],
            "count_per_size": 30,
        }
    ]
    return create_corpus_split(
        output_base_dir=base_dir,
        version="v004_wave2",
        split="search_holdout",
        spec=spec,
        master_seed=seed,
    )
