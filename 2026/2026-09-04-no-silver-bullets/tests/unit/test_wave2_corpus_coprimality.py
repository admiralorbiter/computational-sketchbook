"""Tests verifying strict pairwise coprimality and factor uniqueness for Wave 2 corpus."""

import math
from collections import Counter
from pathlib import Path

from nsb.benchmarks.corpus import load_public_instances, load_sealed_truth


def test_wave2_corpus_pairwise_coprimality_and_unique_factors():
    instances = load_public_instances(".", "v002_wave2", "confirmatory")
    assert len(instances) == 150, f"Expected 150 instances, got {len(instances)}"

    # Check 30 per bit size
    counts = Counter(inst.bits for inst in instances)
    for b in [32, 48, 64, 80, 96]:
        assert counts[b] == 30, f"Expected 30 instances for {b}b, got {counts[b]}"

    truth = load_sealed_truth(".", "v002_wave2", "confirmatory")
    assert len(truth) == 150

    # 1. Verify all 300 prime factors are mutually distinct (zero factor reuse across whole corpus)
    seen_primes = set()
    for inst in instances:
        t = truth[inst.instance_id]
        p, q = int(t.p), int(t.q)
        assert p * q == int(inst.N), f"Factorization mismatch for {inst.instance_id}"
        assert p < q, f"Expected p < q for {inst.instance_id}"
        assert p not in seen_primes, f"Prime {p} reused in instance {inst.instance_id}!"
        seen_primes.add(p)
        assert q not in seen_primes, f"Prime {q} reused in instance {inst.instance_id}!"
        seen_primes.add(q)

    assert len(seen_primes) == 300, f"Expected 300 distinct primes, found {len(seen_primes)}"

    # 2. Mechanically assert all 11,175 pairwise GCDs == 1
    moduli = [int(inst.N) for inst in instances]
    n = len(moduli)
    pairs_checked = 0
    for i in range(n):
        for j in range(i + 1, n):
            g = math.gcd(moduli[i], moduli[j])
            assert g == 1, (
                f"Pairwise coprimality failure between {instances[i].instance_id} "
                f"and {instances[j].instance_id}: gcd = {g}"
            )
            pairs_checked += 1

    assert pairs_checked == 11175, f"Expected 11,175 pairs checked, got {pairs_checked}"
