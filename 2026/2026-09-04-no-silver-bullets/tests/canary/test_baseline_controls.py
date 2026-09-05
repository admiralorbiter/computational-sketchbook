"""Canary tests validating baseline controls on synthetic benchmark instances."""

from pathlib import Path
import pytest
from nsb.benchmarks.corpus import load_public_instances
from nsb.baselines.portfolio import run_baseline_solve


def test_baseline_controls_positive_and_negative():
    instances = load_public_instances(".", "v001_smoke", "smoke")
    inst_by_id = {inst.instance_id: inst for inst in instances}

    # 1. Positive Control: Family F (close primes) should be cracked by Fermat
    f_inst = inst_by_id.get("F-048-00001")
    assert f_inst is not None
    N_f = int(f_inst.N)
    f_res, f_verif = run_baseline_solve("fermat", N_f, max_seconds=2.0)
    assert f_res.success is True
    assert f_verif.verified is True
    assert f_res.steps <= 100  # Should crack in very few steps

    # 2. Positive Control: Family P1 (smooth p-1) should be cracked by Pollard p-1
    p1_inst = inst_by_id.get("P1-048-00001")
    assert p1_inst is not None
    N_p1 = int(p1_inst.N)
    p1_res, p1_verif = run_baseline_solve("pollard_pm1", N_p1, max_seconds=2.0)
    assert p1_res.success is True
    assert p1_verif.verified is True

    # 3. Negative Control: Fermat should NOT crack balanced Family R in few steps
    r_inst = inst_by_id.get("R-048-00001")
    assert r_inst is not None
    N_r = int(r_inst.N)
    r_res, r_verif = run_baseline_solve("fermat", N_r, max_steps=1000)
    assert r_res.success is False
    assert r_verif.verified is False
