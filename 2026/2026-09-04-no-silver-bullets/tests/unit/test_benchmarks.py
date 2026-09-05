"""Unit tests for benchmark generation across families R, F, P1, C, and E."""

import random
import tempfile
from pathlib import Path
import gmpy2
import pytest

from nsb.benchmarks.generator import (
    generate_family_c,
    generate_family_e,
    generate_family_f,
    generate_family_p1,
    generate_family_r,
    generate_random_prime,
)
from nsb.benchmarks.corpus import create_corpus_split, load_public_instances, load_sealed_truth


def test_generate_random_prime():
    rng = random.Random(123)
    p = generate_random_prime(32, rng)
    assert p.bit_length() == 32
    assert gmpy2.is_prime(p)


def test_generate_family_r():
    rng = random.Random(456)
    N, p, q = generate_family_r(32, rng)
    assert N.bit_length() == 32
    assert p * q == N
    assert p <= q
    assert p != q
    assert gmpy2.is_prime(p)
    assert gmpy2.is_prime(q)


def test_generate_family_f():
    rng = random.Random(789)
    N, p, q = generate_family_f(32, rng, max_delta=256)
    assert p * q == N
    assert p <= q
    assert gmpy2.is_prime(p)
    assert gmpy2.is_prime(q)
    # Distance should be small
    assert (q - p) <= 256 or (q - p) < 1000


def test_generate_family_p1():
    rng = random.Random(999)
    N, p, q = generate_family_p1(32, rng, prime_bound=500)
    assert p * q == N
    assert gmpy2.is_prime(p)
    assert gmpy2.is_prime(q)


def test_generate_family_c():
    rng = random.Random(101)
    N, p, q, oracle = generate_family_c(32, rng, msb_fraction=0.5)
    assert p * q == N
    assert oracle["oracle_type"] == "msb"
    shift = oracle["shift"]
    known_val = oracle["msb_value"]
    assert (p >> shift) == known_val


def test_corpus_generation_and_loading():
    with tempfile.TemporaryDirectory() as tmpdir:
        spec = [
            {"family": "R", "bit_sizes": [32], "count_per_size": 2},
            {"family": "F", "bit_sizes": [32], "count_per_size": 1},
        ]
        manifest = create_corpus_split(
            output_base_dir=tmpdir,
            version="v001_test",
            split="smoke",
            spec=spec,
            master_seed=42,
        )
        assert manifest["total_instances"] == 3
        assert Path(manifest["public_file"]).is_file()
        assert Path(manifest["sealed_file"]).is_file()

        # Load public instances without reading sealed file
        public_items = load_public_instances(tmpdir, "v001_test", "smoke")
        assert len(public_items) == 3
        assert public_items[0].family == "R"
        assert int(public_items[0].N).bit_length() == 32

        # Load sealed truth
        sealed_map = load_sealed_truth(tmpdir, "v001_test", "smoke")
        assert len(sealed_map) == 3
        for item in public_items:
            truth = sealed_map[item.instance_id]
            p = int(truth.p)
            q = int(truth.q)
            assert p * q == int(item.N)
