"""Unit tests for Carry-Save Adder tree SAT encoder and comparative scaling."""

import pytest
from nsb.tracks.constraint_graph.encoder import CarrySaveAdderSATEncoder, SchoolbookSATEncoder
from nsb.tracks.constraint_graph.semantic import verify_encoding_semantic_equivalence
from nsb.tracks.constraint_graph.benchmark import run_paired_sat_comparison


def test_carry_save_encoder_structure():
    csa = CarrySaveAdderSATEncoder()
    cnf, mapping = csa.encode(143)  # 11 * 13 (8-bit)
    assert len(cnf.clauses) > 0
    assert "p_vars" in mapping
    assert "q_vars" in mapping
    assert mapping["architecture"] == "carry_save_tree"


def test_carry_save_semantic_equivalence():
    csa = CarrySaveAdderSATEncoder()
    res = verify_encoding_semantic_equivalence(csa, 7, 11)
    assert res.equivalent is True
    assert (7, 11) in res.valid_factor_pairs


def test_paired_sat_comparison():
    res = run_paired_sat_comparison(N=3233, bits=12, timeout_seconds=2.0)
    assert res.bits == 12
    assert res.satisfiable is True
    assert res.factors_recovered == [53, 61]
    assert res.schoolbook_time > 0.0
    assert res.csa_time > 0.0
    assert res.speedup > 0.0
