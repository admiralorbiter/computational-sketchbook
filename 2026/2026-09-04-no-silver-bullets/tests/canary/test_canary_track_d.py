"""Canary tests for Track D: D-CANARY-1, D-CANARY-2, and D-CANARY-3."""

import pytest
from nsb.tracks.constraint_graph.encoder import SchoolbookSATEncoder
from nsb.tracks.constraint_graph.solver import SATSolverAdapter
from nsb.tracks.constraint_graph.semantic import verify_encoding_semantic_equivalence
from nsb.benchmarks.corpus import load_public_instances
from nsb.verifier.factor import verify_factors


def test_d_canary_1_semantic_equivalence():
    """D-CANARY-1: 8-16 bit toy multiplication semantic equivalence."""
    encoder = SchoolbookSATEncoder(symmetry_breaking=True)
    # p = 11, q = 13 -> N = 143 (8-bit)
    res = verify_encoding_semantic_equivalence(encoder, p_true=11, q_true=13)
    assert res.equivalent is True
    assert (11, 13) in res.valid_factor_pairs
    assert res.models_found == 1  # Unique factorization with symmetry breaking

    # p = 17, q = 23 -> N = 391 (9-bit)
    res2 = verify_encoding_semantic_equivalence(encoder, p_true=17, q_true=23)
    assert res2.equivalent is True
    assert (17, 23) in res2.valid_factor_pairs


def test_d_canary_2_known_factor_solve():
    """D-CANARY-2: Factor balanced semiprime up to 24 bits."""
    # Factor E-016-00001 from public benchmark corpus
    instances = load_public_instances(".", "v001_smoke", "smoke")
    inst_by_id = {i.instance_id: i for i in instances}

    e16 = inst_by_id.get("E-016-00001")
    assert e16 is not None
    N_16 = int(e16.N)

    encoder = SchoolbookSATEncoder(symmetry_breaking=True)
    cnf, mapping = encoder.encode(N_16)
    solver = SATSolverAdapter(solver_name="cadical195")
    res = solver.solve(cnf, mapping)

    assert res.satisfiable is True
    assert len(res.factors) == 2
    verif = verify_factors(N_16, res.factors[0], res.factors[1])
    assert verif.verified is True

    # Factor E-024-00001 (24-bit)
    e24 = inst_by_id.get("E-024-00001")
    assert e24 is not None
    N_24 = int(e24.N)

    cnf_24, mapping_24 = encoder.encode(N_24)
    res_24 = solver.solve(cnf_24, mapping_24)
    assert res_24.satisfiable is True
    verif_24 = verify_factors(N_24, res_24.factors[0], res_24.factors[1])
    assert verif_24.verified is True


def test_d_canary_3_malformed_encoding_detected():
    """D-CANARY-3: Malformed carry logic is caught and rejected by semantic verifier."""
    malformed_encoder = SchoolbookSATEncoder(inject_malformed_carry=True)
    res = verify_encoding_semantic_equivalence(malformed_encoder, p_true=11, q_true=13)
    # The malformed carry causes semantic equivalence to fail!
    assert res.equivalent is False
    assert res.error != ""
