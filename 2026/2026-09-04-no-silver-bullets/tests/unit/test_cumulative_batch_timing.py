"""Unit tests for repaired cumulative multi-batch throughput timing in AlgebraicEvaluator."""

from nsb.tracks.algebraic_evolution.evaluator import AlgebraicEvaluator
from nsb.tracks.algebraic_evolution.representation import create_base_m_representation


def test_benchmark_relation_throughput_achieves_minimum_cpu():
    """Verify benchmark_relation_throughput runs in batches until cumulative CPU >= min_cpu_seconds."""
    evaluator = AlgebraicEvaluator(small_primes_bound=250)
    pair = create_base_m_representation(2944186489, degree=3)

    # Request min 0.05s for quick test execution
    res = evaluator.benchmark_relation_throughput(
        pair,
        bound_a=50,
        bound_b=10,
        min_cpu_seconds=0.05,
    )

    assert res["batches_executed"] >= 1
    assert res["cumulative_cpu_seconds"] >= 0.04  # Allows small timer granularity margin
    assert res["single_batch_smooth_relations"] >= 0
    assert res["throughput_relations_per_core_sec"] >= 0.0
    # Throughput should not be an insane timer-resolution artifact like 78000x
    assert res["throughput_relations_per_core_sec"] < 1e7


def test_evaluate_paired_throughput_benchmark():
    """Verify paired throughput benchmark compares candidate vs baseline stably."""
    evaluator = AlgebraicEvaluator(small_primes_bound=250)
    N = 2944186489
    p3 = create_base_m_representation(N, degree=3)
    p2 = create_base_m_representation(N, degree=2)

    res = evaluator.evaluate_paired_throughput_benchmark(
        N=N,
        cand_pair=p3,
        base_pair=p2,
        bound_a=50,
        bound_b=10,
        min_cpu_seconds=0.05,
    )

    assert "cand_throughput" in res
    assert "base_throughput" in res
    assert "throughput_ratio" in res
    assert res["cand_cpu_seconds"] >= 0.04
    assert res["base_cpu_seconds"] >= 0.04
