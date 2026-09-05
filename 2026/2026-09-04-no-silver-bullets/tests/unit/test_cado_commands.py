"""Unit tests for discrete CADO command execution, adapter mocking, and R3 runner."""

from pathlib import Path
from unittest.mock import MagicMock
import pytest

from nsb.baselines.cado_nfs.adapter import CadoSubprocessAdapter, CommandExecutionResult
from nsb.baselines.cado_nfs.environment import CadoEnvironment
from nsb.baselines.cado_nfs.models import NfsPolynomialPair
from nsb.baselines.cado_nfs.polyselect import CadoPolynomialSelector
from nsb.baselines.cado_nfs.scorer import CadoScorer
from nsb.baselines.cado_nfs.sieve import CadoRelationCollector
from nsb.experiments.r3_nfs_baseline_runner import R3BaselineRunner


def test_adapter_command_building_native():
    adapter = CadoSubprocessAdapter(use_wsl_bridge=False)
    cmd = adapter.build_command("score", ["--full", "test.poly"])
    assert cmd[-2:] == ["--full", "test.poly"]
    assert not any("wsl" in c for c in cmd)


def test_adapter_command_building_wsl():
    adapter = CadoSubprocessAdapter(use_wsl_bridge=True, wsl_distro="Ubuntu")
    cmd = adapter.build_command("score", ["--full", "test.poly"])
    assert cmd[0] == "wsl.exe"
    assert cmd[1] == "-d"
    assert cmd[2] == "Ubuntu"
    assert "--full" in cmd
    assert "test.poly" in cmd


def test_scorer_with_mock_adapter():
    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)
    mock_adapter.run_binary.return_value = CommandExecutionResult(
        command=["score", "-poly", "tmp.poly", "-Bf", "1000000", "-Bg", "500000", "-area", "1.00e+07"],
        binary_name="score",
        returncode=0,
        stdout="""
        # exp_E 43.1, lognorm 45.2, skew 1.5, 3 rroots
        # MurphyE(Bf=1000000, Bg=500000, area=1.00e+07) = 2.45e-11
        """,
        stderr="",
        wall_seconds=0.15,
        cpu_seconds=0.14,
        max_rss_mb=12.5,
    )

    pair = NfsPolynomialPair(
        f1_coeffs=[-5832, 0, 0, 1],
        f2_coeffs=[-18, 1],
        N=5893,
        m=18,
    )

    scorer = CadoScorer(adapter=mock_adapter)
    res = scorer.score(pair)

    assert abs(res.murphy_e - 2.45e-11) < 1e-15
    assert abs(res.lognorm - 45.2) < 1e-3
    assert abs(res.exp_e - 43.1) < 1e-3
    assert res.rroots == 3
    assert res.cpu_seconds == 0.14
    assert res.wall_seconds == 0.15
    mock_adapter.run_binary.assert_called_once()
    call_args = mock_adapter.run_binary.call_args
    assert call_args[0][0] == "score"
    assert "--full" in call_args[0][1]
    assert "-poly" not in call_args[0][1]
    assert "-Bf" in call_args[0][1]


def test_polyselect_with_mock_adapter():
    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)

    poly_output = """
    n: 5893
    skew: 1.5
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 42.1
    """

    # Return candidate poly block for polyselect, and optimized poly for ropt
    mock_adapter.run_binary.side_effect = [
        CommandExecutionResult(
            command=["polyselect", "-N", "5893", "-degree", "3", "-P", "420"],
            binary_name="polyselect",
            returncode=0,
            stdout=poly_output,
            stderr="",
            wall_seconds=0.40,
            cpu_seconds=0.38,
            max_rss_mb=20.0,
        ),
        CommandExecutionResult(
            command=["polyselect_ropt", "-inputpolys", "stage1_candidates.polys", "-ropteffort", "5"],
            binary_name="polyselect_ropt",
            returncode=0,
            stdout=poly_output,
            stderr="",
            wall_seconds=0.30,
            cpu_seconds=0.28,
            max_rss_mb=22.0,
        ),
    ]

    selector = CadoPolynomialSelector(adapter=mock_adapter, run_ropt=True)
    res = selector.select_polynomial(n=5893, degree=3)

    assert res.modulus_n == 5893
    assert res.degree == 3
    # Total CPU = 0.38 + 0.28 = 0.66
    assert abs(res.cpu_seconds - 0.66) < 1e-3
    assert abs(res.wall_seconds - 0.70) < 1e-3
    assert res.pair.degree1 == 3
    assert res.pair.m == 18


def test_polyselect_ropt_selects_global_best_not_first():
    """Verify polyselect_ropt selects 0-th best polynomial rather than the first parsed block."""
    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)

    stage1_output = """
    n: 5893
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 42.1
    """

    # ROPT emits block 1 (suboptimal input) then block 2 (0-th best found)
    ropt_output = """
    # Processing input 0
    n: 5893
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # MurphyE(Bf=1000000, Bg=500000, area=1.00e+07) = 1.00e-12

    # 0-th best polynomial found (Murphy_E=9.50e-11):
    n: 5893
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # skew: 2.2
    # MurphyE(Bf=1000000, Bg=500000, area=1.00e+07) = 9.50e-11
    """

    mock_adapter.run_binary.side_effect = [
        CommandExecutionResult(
            command=["polyselect"], binary_name="polyselect", returncode=0, stdout=stage1_output, stderr="", wall_seconds=0.2, cpu_seconds=0.2, max_rss_mb=10.0
        ),
        CommandExecutionResult(
            command=["polyselect_ropt"], binary_name="polyselect_ropt", returncode=0, stdout=ropt_output, stderr="", wall_seconds=0.3, cpu_seconds=0.3, max_rss_mb=15.0
        ),
    ]

    selector = CadoPolynomialSelector(adapter=mock_adapter, run_ropt=True)
    res = selector.select_polynomial(n=5893, degree=3)

    assert res.pair.metadata.get("is_best") is True or res.pair.metadata.get("best_rank") == 0
    assert abs(res.pair.metadata.get("murphy_e") - 9.50e-11) < 1e-15


def test_relation_collector_with_mock_adapter():
    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)
    mock_adapter.env = MagicMock(spec=CadoEnvironment)
    # Return an existing path for check_rels binary check
    mock_adapter.env.get_binary_path.return_value = Path(__file__)

    las_output = """
    # las output
    # special-q: 500000..500200
    10,1:2,3:5
    11,1:2,5:7
    # Total 2 relations
    # Total cpu time: 1.2s
    # Total elapsed time: 0.5s
    """

    mock_results = [
        # makefb side 0
        CommandExecutionResult(
            command=["makefb", "-side", "0"],
            binary_name="makefb",
            returncode=0,
            stdout="",
            stderr="",
            wall_seconds=0.1,
            cpu_seconds=0.1,
            max_rss_mb=10.0,
        ),
        # makefb side 1
        CommandExecutionResult(
            command=["makefb", "-side", "1"],
            binary_name="makefb",
            returncode=0,
            stdout="",
            stderr="",
            wall_seconds=0.1,
            cpu_seconds=0.1,
            max_rss_mb=10.0,
        ),
        # las
        CommandExecutionResult(
            command=["las", "-poly", "target.poly"],
            binary_name="las",
            returncode=0,
            stdout=las_output,
            stderr="",
            wall_seconds=0.52,
            cpu_seconds=1.25,
            max_rss_mb=45.0,
        ),
        # check_rels
        CommandExecutionResult(
            command=["check_rels", "-poly", "target.poly", "-lpb0", "22", "-lpb1", "22", "-check_primality", "relations.txt"],
            binary_name="check_rels",
            returncode=0,
            stdout="",
            stderr="",
            wall_seconds=0.05,
            cpu_seconds=0.05,
            max_rss_mb=5.0,
        ),
    ]

    def mock_run(binary_name, args, **kwargs):
        if binary_name == "makefb":
            for i, arg in enumerate(args):
                if arg == "-out" and i + 1 < len(args):
                    Path(args[i + 1]).write_text("dummy fb", encoding="utf-8")
        return mock_results.pop(0)

    mock_adapter.run_binary.side_effect = mock_run

    pair = NfsPolynomialPair(
        f1_coeffs=[-5832, 0, 0, 1],
        f2_coeffs=[-18, 1],
        N=5893,
        m=18,
    )

    collector = CadoRelationCollector(adapter=mock_adapter)
    res = collector.collect_relations(pair, q_start=500000, q_range=200, run_makefb=True, validate_with_check_rels=True)

    assert res.unique_relations == 2
    assert res.total_relations == 2
    assert res.relations_hash != ""
    assert res.checked_with_check_rels is True


def test_relation_collector_fails_if_check_rels_fails():
    """Verify collect_relations fails closed if check_rels returns non-zero."""
    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)
    mock_adapter.env = MagicMock(spec=CadoEnvironment)
    mock_adapter.env.get_binary_path.return_value = Path(__file__)

    las_output = """
    10,1:2,3:5
    # Total 1 reports
    """

    mock_results = [
        CommandExecutionResult(command=["makefb"], binary_name="makefb", returncode=0, stdout="", stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=10.0),
        CommandExecutionResult(command=["makefb"], binary_name="makefb", returncode=0, stdout="", stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=10.0),
        CommandExecutionResult(command=["las"], binary_name="las", returncode=0, stdout=las_output, stderr="", wall_seconds=0.5, cpu_seconds=1.0, max_rss_mb=30.0),
        CommandExecutionResult(command=["check_rels"], binary_name="check_rels", returncode=1, stdout="Corrupted relation", stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=5.0),
    ]

    def mock_run(binary_name, args, **kwargs):
        if binary_name == "makefb":
            for i, arg in enumerate(args):
                if arg == "-out" and i + 1 < len(args):
                    Path(args[i + 1]).write_text("dummy fb", encoding="utf-8")
        return mock_results.pop(0)

    mock_adapter.run_binary.side_effect = mock_run

    pair = NfsPolynomialPair(f1_coeffs=[-5832, 0, 0, 1], f2_coeffs=[-18, 1], N=5893, m=18)
    collector = CadoRelationCollector(adapter=mock_adapter)

    import pytest
    with pytest.raises(RuntimeError, match="check_rels validation failed"):
        collector.collect_relations(pair, q_start=500000, q_range=200, run_makefb=True, validate_with_check_rels=True)


def test_r3_runner_g0_gate():
    runner = R3BaselineRunner()
    g0 = runner.run_g0_environment_gate()
    assert "gate" in g0
    assert g0["gate"] == "R3-G0"
    assert "fingerprint" in g0
    # On Windows host, g0 must fail-closed
    if runner.env.is_windows:
        assert g0["passed"] is False
        assert "Linux" in g0["message"]


def test_r3_runner_g2_mock_paired_invariance():
    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)
    mock_adapter.env = MagicMock(spec=CadoEnvironment)
    mock_adapter.env.get_binary_path.return_value = Path(__file__)

    mock_env = MagicMock(spec=CadoEnvironment)
    mock_env.validate_for_canonical_execution.return_value = (True, "OK")
    mock_env.fingerprint.return_value = {}

    las_output = """
    # special-q: 500000..500200
    10,1:2,3:5
    11,1:2,5:7
    # Total 2 relations
    # Total cpu: 1.0s
    """

    # 4 runs of A1 -> B1 -> B2 -> A2 (each runs makefb0, makefb1, las, check_rels)
    mock_results = []
    for _ in range(4):
        # makefb0
        mock_results.append(CommandExecutionResult(
            command=["makefb"], binary_name="makefb", returncode=0, stdout="", stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=10.0
        ))
        # makefb1
        mock_results.append(CommandExecutionResult(
            command=["makefb"], binary_name="makefb", returncode=0, stdout="", stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=10.0
        ))
        # las
        mock_results.append(CommandExecutionResult(
            command=["las"], binary_name="las", returncode=0, stdout=las_output, stderr="", wall_seconds=0.5, cpu_seconds=1.0, max_rss_mb=30.0
        ))
        # check_rels
        mock_results.append(CommandExecutionResult(
            command=["check_rels"], binary_name="check_rels", returncode=0, stdout="", stderr="", wall_seconds=0.05, cpu_seconds=0.05, max_rss_mb=5.0
        ))

    def mock_run(binary_name, args, **kwargs):
        if binary_name == "makefb":
            for i, arg in enumerate(args):
                if arg == "-out" and i + 1 < len(args):
                    Path(args[i + 1]).write_text("dummy fb", encoding="utf-8")
        return mock_results.pop(0)

    mock_adapter.run_binary.side_effect = mock_run

    pair = NfsPolynomialPair(
        f1_coeffs=[-5832, 0, 0, 1],
        f2_coeffs=[-18, 1],
        N=5893,
        m=18,
    )

    runner = R3BaselineRunner(environment=mock_env, adapter=mock_adapter)
    g2_res = runner.run_g2_deterministic_rerun_canary(pair, q_start=500000, q_range=200)

    assert g2_res["passed"] is True
    assert g2_res["deterministic_rerun_verified"] is True
    assert g2_res["invariance_verified"] is True
    assert g2_res["relation_record_hash"] != "MISMATCH"
    assert g2_res["ab_pairs_hash"] != "MISMATCH"
    assert g2_res["runs"]["A1"]["relations_hash"] == g2_res["runs"]["B1"]["relations_hash"]
    assert g2_res["runs"]["A1"]["ab_pairs_hash"] == g2_res["runs"]["B1"]["ab_pairs_hash"]
    assert g2_res["runs"]["A1"]["checked_with_check_rels"] is True
    assert g2_res["runs"]["B2"]["checked_with_check_rels"] is True


def test_smoke_c60_fixture_mathematical_validity():
    """Verify that the committed 60-digit smoke polynomial fixture is mathematically valid."""
    from nsb.experiments.r3_nfs_baseline_runner import SMOKE_60_DIGIT_COMPOSITE, VERIFIED_C60_POLY
    from nsb.baselines.cado_nfs.verifier import verify_nfs_polynomial_pair

    assert VERIFIED_C60_POLY.eval_f1(VERIFIED_C60_POLY.m) == SMOKE_60_DIGIT_COMPOSITE
    assert VERIFIED_C60_POLY.eval_f2(VERIFIED_C60_POLY.m) == 0
    valid, msg = verify_nfs_polynomial_pair(VERIFIED_C60_POLY)
    assert valid is True, f"VERIFIED_C60_POLY failed verification: {msg}"


def test_cado_profile_geometry_derivations():
    """Verify CADO profile scoring geometry and task parameters match params.c60."""
    from nsb.baselines.cado_nfs.profiles import CADO_PARAMS_C60, CANARY_PLUMBING_C60

    # CADO_PARAMS_C60: lpb0=18, lpb1=19, I=10, qmin=61961
    assert CADO_PARAMS_C60.bf == 2**19 == 524288
    assert CADO_PARAMS_C60.bg == 2**18 == 262144
    assert CADO_PARAMS_C60.area == float((2 ** (2 * 10 - 1)) * 61961) == 32485408768.0
    assert CADO_PARAMS_C60.ncurves0 == 2
    assert CADO_PARAMS_C60.ncurves1 == 2
    assert CADO_PARAMS_C60.admin == 0
    assert CADO_PARAMS_C60.admax == 10000
    assert CADO_PARAMS_C60.adrange == 5000
    assert CADO_PARAMS_C60.incr == 60
    assert CADO_PARAMS_C60.nrkeep == 10

    # CANARY_PLUMBING_C60: lpb0=22, lpb1=22, I=11, qmin=500000
    assert CANARY_PLUMBING_C60.bf == 2**22 == 4194304
    assert CANARY_PLUMBING_C60.bg == 2**22 == 4194304
    assert CANARY_PLUMBING_C60.area == float((2 ** (2 * 11 - 1)) * 500000) == 1048576000000.0
    assert CANARY_PLUMBING_C60.ncurves0 == 2
    assert CANARY_PLUMBING_C60.ncurves1 == 2


def test_polyselect_command_args_absence_of_nrkeep():
    """Explicitly assert -nrkeep is NEVER passed to the polyselect binary."""
    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)

    poly_output = """
    n: 5893
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 40.0
    """

    mock_adapter.run_binary.return_value = CommandExecutionResult(
        command=["polyselect"], binary_name="polyselect", returncode=0, stdout=poly_output, stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=10.0
    )

    selector = CadoPolynomialSelector(adapter=mock_adapter, run_ropt=False)

    # Case 1: default nrkeep=10, keep=None
    selector.select_polynomial(n=5893, degree=3, nrkeep=10, keep=None)
    calls = mock_adapter.run_binary.call_args_list
    assert len(calls) == 1
    poly_args = calls[0][0][1]
    assert "-nrkeep" not in poly_args
    assert "-keep" not in poly_args

    # Case 2: keep=5 explicitly set
    mock_adapter.reset_mock()
    selector.select_polynomial(n=5893, degree=3, nrkeep=10, keep=5)
    calls = mock_adapter.run_binary.call_args_list
    assert len(calls) == 1
    poly_args = calls[0][0][1]
    assert "-nrkeep" not in poly_args
    assert "-keep" in poly_args
    keep_idx = poly_args.index("-keep")
    assert poly_args[keep_idx + 1] == "5"


def test_polyselect_task_level_global_nrkeep_pruning_adversarial():
    """Adversarial test: two work ranges produce 6 candidates total, nrkeep=3.

    ROPT must receive exactly the global best 3 polynomials by lowest exp_E across both ranges.
    """
    from nsb.baselines.cado_nfs.parser import parse_cado_poly_blocks

    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)

    # Range 1 produces 3 candidates: exp_E 45.0, 40.0, 55.0
    range1_output = """
    n: 5893
    skew: 1.1
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 45.0

    n: 5893
    skew: 1.2
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 40.0

    n: 5893
    skew: 1.3
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 55.0
    """

    # Range 2 produces 3 candidates: exp_E 35.0, 50.0, 30.0
    range2_output = """
    n: 5893
    skew: 1.4
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 35.0

    n: 5893
    skew: 1.5
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 50.0

    n: 5893
    skew: 1.6
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 30.0
    """

    ropt_output = """
    # 0-th best polynomial found (Murphy_E=1.23e-10):
    n: 5893
    skew: 1.6
    c0: -5832
    c1: 0
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # MurphyE(Bf=1000000, Bg=500000, area=1.00e+07) = 1.23e-10
    """

    ropt_input_content = []

    def mock_run(binary_name, args, **kwargs):
        if binary_name == "polyselect":
            admin_val = int(args[args.index("-admin") + 1])
            stdout = range1_output if admin_val == 0 else range2_output
            return CommandExecutionResult(
                command=["polyselect"] + args, binary_name="polyselect", returncode=0, stdout=stdout, stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=10.0
            )
        elif binary_name == "polyselect_ropt":
            inputpolys_path = args[args.index("-inputpolys") + 1]
            ropt_input_content.append(Path(inputpolys_path).read_text(encoding="utf-8"))
            return CommandExecutionResult(
                command=["polyselect_ropt"] + args, binary_name="polyselect_ropt", returncode=0, stdout=ropt_output, stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=10.0
            )
        return CommandExecutionResult(command=[binary_name], binary_name=binary_name, returncode=0, stdout="", stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=10.0)

    mock_adapter.run_binary.side_effect = mock_run

    selector = CadoPolynomialSelector(adapter=mock_adapter, run_ropt=True)
    res = selector.select_polynomial(
        n=5893,
        degree=3,
        admin=0,
        admax=10000,
        adrange=5000,  # Forces 2 work ranges: [0..5000] and [5000..10000]
        nrkeep=3,      # Must retain exactly the global best 3
    )

    # Verify ROPT was executed and received inputpolys
    assert len(ropt_input_content) == 1
    retained_blocks = parse_cado_poly_blocks(ropt_input_content[0])

    # Must contain exactly nrkeep = 3 blocks
    assert len(retained_blocks) == 3

    # The 3 lowest exp_E values across both ranges are: 30.0 (skew=1.6), 35.0 (skew=1.4), 40.0 (skew=1.2)
    retained_exp_e = [b.metadata["exp_e"] for b in retained_blocks]
    assert retained_exp_e == [30.0, 35.0, 40.0]
    retained_skews = [round(b.skew, 1) for b in retained_blocks]
    assert retained_skews == [1.6, 1.4, 1.2]


def test_polyselect_task_level_nrkeep_pruning_missing_exp_e_fails_closed():
    """Assert fail-closed behavior if candidates in an overflow set lack required exp_e metadata."""
    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)

    # 3 candidates produced, but one lacks exp_E, and nrkeep=2
    output_missing_exp_e = """
    n: 5893
    c0: -5832
    c1: 1
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 45.0

    n: 5893
    c0: -5832
    c1: 2
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # MISSING exp_E!

    n: 5893
    c0: -5832
    c1: 3
    c2: 0
    c3: 1
    Y0: -18
    Y1: 1
    # m: 18
    # exp_E 35.0
    """

    mock_adapter.run_binary.return_value = CommandExecutionResult(
        command=["polyselect"], binary_name="polyselect", returncode=0, stdout=output_missing_exp_e, stderr="", wall_seconds=0.1, cpu_seconds=0.1, max_rss_mb=10.0
    )

    selector = CadoPolynomialSelector(adapter=mock_adapter, run_ropt=False)
    with pytest.raises(ValueError, match=r"exp_e"):
        selector.select_polynomial(n=5893, degree=3, nrkeep=2)


def test_environment_fingerprint_provenance_fields():
    """Verify that CadoEnvironment.fingerprint() includes comprehensive hardware and provenance fields."""
    env = CadoEnvironment()
    fp = env.fingerprint()

    # Core identification & WSL status (unconditional, no KeyError)
    assert "has_wsl" in fp
    assert isinstance(fp["has_wsl"], bool)
    assert "platform" in fp
    assert "is_linux" in fp
    assert "is_windows" in fp

    # NSB repository provenance
    assert "nsb_git_commit" in fp
    assert "nsb_git_dirty" in fp
    assert isinstance(fp["nsb_git_dirty"], bool)
    assert "installed_python_packages" in fp
    assert "installed_python_packages_hash" in fp
    assert isinstance(fp["installed_python_packages_hash"], str)
    assert len(fp["installed_python_packages_hash"]) == 64

    # Hardware provenance
    assert "cpu_model" in fp
    assert isinstance(fp["cpu_model"], str)
    assert "ram" in fp
    assert "total_bytes" in fp["ram"]
    assert "available_bytes" in fp["ram"]
    assert fp["ram"]["total_bytes"] >= 0

    # Software & environment provenance
    assert "python_version" in fp
    assert "python_executable" in fp
    assert "python_dependency_locks" in fp
    assert "toolchain" in fp
    assert "cmake_cache" in fp
    assert "effective_cmake_flags" in fp["cmake_cache"]
    assert "relevant_env_vars" in fp


def test_parser_conservation_check_fail_closed():
    """Verify that parse_las_output fails closed if reported relation count mismatches parsed relation count."""
    from nsb.baselines.cado_nfs.parser import parse_las_output

    # las text claiming 3 relations, but only 2 relation lines present
    mismatched_output = """
    # special-q: 500000..500200
    10,1:2,3:5
    11,1:2,5:7
    # Total 3 relations
    # Total cpu: 1.0s
    """
    with pytest.raises(ValueError, match=r"[Cc]onservation"):
        parse_las_output(mismatched_output, enforce_conservation=True)


def test_validate_for_canonical_execution_nsb_dirty_fails(monkeypatch):
    """G0 validation must fail closed when NSB git working tree is dirty."""
    env = CadoEnvironment()
    # Force is_linux = True on class property
    monkeypatch.setattr(CadoEnvironment, "is_linux", property(lambda self: True))
    # Mock NSB status as dirty
    monkeypatch.setattr(env, "get_nsb_git_status", lambda: ("0123456789abcdef0123456789abcdef01234567", True))

    passed, msg = env.validate_for_canonical_execution()
    assert passed is False
    assert "dirty" in msg.lower() or "uncommitted" in msg.lower()


def test_validate_for_canonical_execution_toolchain_version_enforcement(monkeypatch, tmp_path):
    """G0 validation must fail when GCC < 10.0 or CMake < 3.18 or GMP < 6.1."""
    env = CadoEnvironment(cado_root=tmp_path)
    monkeypatch.setattr(CadoEnvironment, "is_linux", property(lambda self: True))
    monkeypatch.setattr(env, "get_nsb_git_status", lambda: ("0123456789abcdef0123456789abcdef01234567", False))
    monkeypatch.setattr(env, "get_gmp_mpfr_versions", lambda: {"gmp": "6.2.1", "mpfr": "4.1.0"})

    # Case 1: GCC 9.4.0 < 10.0
    monkeypatch.setattr(env, "get_toolchain_versions", lambda: {
        "gcc": "9.4.0",
        "cmake": "cmake version 3.22.1",
        "git": "git version 2.34.1"
    })
    passed, msg = env.validate_for_canonical_execution()
    assert passed is False
    assert "GCC" in msg and "10.0" in msg

    # Case 2: CMake 3.16.0 < 3.18
    monkeypatch.setattr(env, "get_toolchain_versions", lambda: {
        "gcc": "11.2.0",
        "cmake": "cmake version 3.16.0",
        "git": "git version 2.34.1"
    })
    passed, msg = env.validate_for_canonical_execution()
    assert passed is False
    assert "CMake" in msg and "3.18" in msg

    # Case 3: GMP 5.1.0 < 6.1
    monkeypatch.setattr(env, "get_toolchain_versions", lambda: {
        "gcc": "11.2.0",
        "cmake": "cmake version 3.22.1",
        "git": "git version 2.34.1"
    })
    monkeypatch.setattr(env, "get_gmp_mpfr_versions", lambda: {"gmp": "5.1.0", "mpfr": "4.1.0"})
    passed, msg = env.validate_for_canonical_execution()
    assert passed is False
    assert "libgmp" in msg


def test_parse_cmake_cache_flags(tmp_path):
    """Test extracting effective CMake flags from CMakeCache.txt."""
    cache_file = tmp_path / "CMakeCache.txt"
    cache_file.write_text("""
    # This is a comment
    CMAKE_BUILD_TYPE:STRING=Release
    CMAKE_C_COMPILER:FILEPATH=/usr/bin/gcc-11
    CMAKE_CXX_COMPILER:FILEPATH=/usr/bin/g++-11
    CMAKE_C_FLAGS_RELEASE:STRING=-O3 -DNDEBUG
    CMAKE_GENERATOR:INTERNAL=Unix Makefiles
    UNRELATED_VAR:STRING=foo
    """, encoding="utf-8")

    flags = CadoEnvironment.parse_cmake_cache_flags(cache_file)
    assert flags["CMAKE_BUILD_TYPE"] == "Release"
    assert flags["CMAKE_C_COMPILER"] == "/usr/bin/gcc-11"
    assert flags["CMAKE_CXX_COMPILER"] == "/usr/bin/g++-11"
    assert flags["CMAKE_C_FLAGS_RELEASE"] == "-O3 -DNDEBUG"
    assert flags["CMAKE_GENERATOR"] == "Unix Makefiles"
    assert "UNRELATED_VAR" not in flags


def test_g1_fails_when_conservation_checked_is_false(monkeypatch):
    """G1 must fail if relation conservation was not checked."""
    from nsb.baselines.cado_nfs.models import NfsPolynomialPair, CadoPolyselectResult, CadoScoreResult, CadoSieveResult
    from nsb.experiments.r3_nfs_baseline_runner import R3BaselineRunner, VERIFIED_C60_POLY, SMOKE_60_DIGIT_COMPOSITE

    runner = R3BaselineRunner()
    monkeypatch.setattr(runner, "run_g0_environment_gate", lambda: {"passed": True})

    monkeypatch.setattr(runner.selector, "select_polynomial", lambda **kw: CadoPolyselectResult(
        modulus_n=SMOKE_60_DIGIT_COMPOSITE,
        degree=4,
        pair=VERIFIED_C60_POLY,
        stage1_candidates_count=1,
        selected_rank=0,
        cpu_seconds=1.0,
        wall_seconds=1.0,
        raw_output="",
        command=["polyselect"],
    ))
    monkeypatch.setattr(runner.scorer, "score", lambda *args, **kw: CadoScoreResult(
        murphy_e=1e-10, lognorm=40.0, exp_e=38.0, skew=2.0, rroots=2, raw_output=""
    ))

    # Mock sieve result with conservation_checked = False
    mock_sieve = CadoSieveResult(
        q_start=500000,
        q_range=200,
        wall_seconds=0.5,
        total_relations=10,
        unique_relations=10,
        relations_hash="abcd" * 16,
        ab_pairs_hash="1234" * 16,
        checked_with_check_rels=True,
        conservation_checked=False,  # NOT CHECKED
        cpu_seconds=1.0,
        relations_per_cpu_second=10.0,
    )
    monkeypatch.setattr(runner.collector, "collect_relations", lambda **kw: mock_sieve)

    res = runner.run_g1_canary()
    assert res["passed"] is False


def test_registered_profiles_freeze():
    """Verify pinned CADO profiles (c60, c70, c80, c90) are frozen and retrievable."""
    from nsb.baselines.cado_nfs.profiles import (
        get_cado_profile,
        CADO_PARAMS_C60,
        CADO_PARAMS_C70,
        CADO_PARAMS_C80,
        CADO_PARAMS_C90,
        CADO_PARAMS_C95,
        CADO_PARAMS_C100,
        CANARY_PLUMBING_C60,
    )

    for name, expected in [
        ("c60_pinned", CADO_PARAMS_C60),
        ("canary_plumbing_c60", CANARY_PLUMBING_C60),
        ("c70_pinned", CADO_PARAMS_C70),
        ("c80_pinned", CADO_PARAMS_C80),
        ("c90_pinned", CADO_PARAMS_C90),
        ("c95_pinned", CADO_PARAMS_C95),
        ("c100_pinned", CADO_PARAMS_C100),
    ]:
        p = get_cado_profile(name)
        assert p == expected
        sieve_dict = p.to_sieve_dict()
        assert sieve_dict["profile_name"] == name
        assert sieve_dict["target_digits"] == p.target_digits
        assert sieve_dict["i_param"] == p.i_param
        assert sieve_dict["lim0"] == p.lim0
        assert sieve_dict["lim1"] == p.lim1
        assert sieve_dict["lpb0"] == p.lpb0
        assert sieve_dict["lpb1"] == p.lpb1
        assert sieve_dict["mfb0"] == p.mfb0
        assert sieve_dict["mfb1"] == p.mfb1
        assert sieve_dict["ncurves0"] == p.ncurves0
        assert sieve_dict["ncurves1"] == p.ncurves1
        if p.lambda0 is not None:
            assert sieve_dict["lambda0"] == p.lambda0
        if p.lambda1 is not None:
            assert sieve_dict["lambda1"] == p.lambda1


def test_g2_profile_parity_and_cross_gate_hash(monkeypatch):
    """Verify G2 accepts profile and validates cross-gate relations hash."""
    from nsb.baselines.cado_nfs.models import CadoSieveResult
    from nsb.baselines.cado_nfs.profiles import CANARY_PLUMBING_C60
    from nsb.experiments.r3_nfs_baseline_runner import R3BaselineRunner, VERIFIED_C60_POLY

    runner = R3BaselineRunner()
    monkeypatch.setattr(runner, "run_g0_environment_gate", lambda: {"passed": True})

    collected_profiles = []

    def mock_collect(poly, q_start, q_range, profile=None, **kwargs):
        collected_profiles.append(profile)
        return CadoSieveResult(
            q_start=q_start,
            q_range=q_range,
            wall_seconds=0.1,
            total_relations=100,
            unique_relations=100,
            relations_hash="matching_hash_1234",
            ab_pairs_hash="matching_ab_1234",
            checked_with_check_rels=True,
            conservation_checked=True,
            cpu_seconds=0.2,
            relations_per_cpu_second=500.0,
        )

    monkeypatch.setattr(runner.collector, "collect_relations", mock_collect)

    # 1. Matching expected hash
    res_match = runner.run_g2_deterministic_rerun_canary(
        pair=VERIFIED_C60_POLY,
        profile=CANARY_PLUMBING_C60,
        expected_relations_hash="matching_hash_1234",
    )
    assert res_match["passed"] is True
    assert res_match["cross_gate_hash_match"] is True
    assert res_match["profile_name"] == "canary_plumbing_c60"
    assert "sieve_profile" in res_match
    assert len(collected_profiles) == 4
    assert all(p == CANARY_PLUMBING_C60 for p in collected_profiles)

    # 2. Mismatching expected hash
    res_mismatch = runner.run_g2_deterministic_rerun_canary(
        pair=VERIFIED_C60_POLY,
        profile=CANARY_PLUMBING_C60,
        expected_relations_hash="different_hash_5678",
    )
    assert res_mismatch["passed"] is False
    assert res_mismatch["cross_gate_hash_match"] is False


def test_pinned_profiles_mechanical_derivation():
    """Verify that area, Bf, and Bg match their exact mathematical derivations for all profiles."""
    from nsb.baselines.cado_nfs.profiles import _REGISTERED_PROFILES

    for name, profile in _REGISTERED_PROFILES.items():
        # 1. Bf = 2^lpb1
        assert profile.bf == (1 << profile.lpb1), f"{name}: bf={profile.bf} != 2^{profile.lpb1}"
        assert profile.bf == profile.expected_bf

        # 2. Bg = 2^lpb0
        assert profile.bg == (1 << profile.lpb0), f"{name}: bg={profile.bg} != 2^{profile.lpb0}"
        assert profile.bg == profile.expected_bg

        # 3. Area = 2^(2*I - 1) * qmin
        derived_area = float((1 << (2 * profile.i_param - 1)) * profile.qmin)
        assert abs(profile.area - derived_area) < 1e-3, (
            f"{name}: area={profile.area} != 2^(2*{profile.i_param}-1) * {profile.qmin} = {derived_area}"
        )
        assert abs(profile.area - profile.expected_area) < 1e-3

        # 4. to_full_dict has all required fields
        full_dict = profile.to_full_dict()
        assert full_dict["name"] == name
        assert full_dict["area"] == profile.area
        assert full_dict["bf"] == profile.bf
        assert full_dict["bg"] == profile.bg


def test_g3_instance_record_schema():
    """Verify that a G3 calibration instance output record conforms to all preregistered schema fields."""
    from nsb.experiments.r3_calibration_runner import R3CalibrationRunner
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY, SMOKE_60_DIGIT_COMPOSITE
    from nsb.baselines.cado_nfs.models import (
        CadoPolyselectResult,
        CadoScoreResult,
        CadoSieveResult,
    )

    runner = R3CalibrationRunner()

    runner.selector.select_polynomial = MagicMock(return_value=CadoPolyselectResult(
        pair=VERIFIED_C60_POLY,
        modulus_n=SMOKE_60_DIGIT_COMPOSITE,
        degree=4,
        cpu_seconds=1.23,
        wall_seconds=1.25,
        raw_output="",
        command=["polyselect"],
    ))

    runner.scorer.score = MagicMock(return_value=CadoScoreResult(
        murphy_e=1.23e-10,
        lognorm=45.2,
        exp_e=43.1,
        rroots=3,
        cpu_seconds=0.45,
        wall_seconds=0.46,
    ))

    runner.collector.collect_relations = MagicMock(return_value=CadoSieveResult(
        total_relations=100,
        unique_relations=95,
        q_start=61961,
        q_range=2000,
        cpu_seconds=3.45,
        wall_seconds=3.50,
        relations_per_cpu_second=27.5,
        relations_hash="testhash123",
        checked_with_check_rels=True,
        conservation_checked=True,
    ))

    mock_instance = {
        "instance_id": "c60_mock_001",
        "digits": 60,
        "N": SMOKE_60_DIGIT_COMPOSITE,
    }

    rec = runner.run_single_instance(mock_instance, timeout_seconds=600.0)

    # Top-level preregistered fields
    required_top_keys = {
        "instance_id", "digits", "N", "profile_name", "profile",
        "polynomial", "polyselect", "scoring", "sieving",
        "total_cpu_seconds", "total_wall_seconds", "timeout_seconds", "passed"
    }
    assert required_top_keys.issubset(rec.keys()), f"Missing top-level keys: {required_top_keys - rec.keys()}"
    assert rec["timeout_seconds"] == 600.0
    assert rec["passed"] is True

    # Polynomial block
    poly = rec["polynomial"]
    required_poly_keys = {"f1_coeffs", "f2_coeffs", "m", "degree1", "degree2", "skew"}
    assert required_poly_keys.issubset(poly.keys()), f"Missing polynomial keys: {required_poly_keys - poly.keys()}"
    assert poly["f1_coeffs"] == VERIFIED_C60_POLY.f1_coeffs
    assert poly["f2_coeffs"] == VERIFIED_C60_POLY.f2_coeffs
    assert poly["m"] == VERIFIED_C60_POLY.m
    assert poly["degree1"] == 4
    assert poly["degree2"] == 1
    assert poly["skew"] == 1.5

    # Polyselect block
    polyselect = rec["polyselect"]
    required_polyselect_keys = {"degree1", "degree2", "skew", "cpu_seconds", "wall_seconds"}
    assert required_polyselect_keys.issubset(polyselect.keys())

    # Scoring block
    scoring = rec["scoring"]
    required_scoring_keys = {"murphy_e", "lognorm", "exp_e", "rroots", "cpu_seconds"}
    assert required_scoring_keys.issubset(scoring.keys())
    assert scoring["murphy_e"] == 1.23e-10

    # Sieving block
    sieving = rec["sieving"]
    required_sieving_keys = {
        "q_start", "q_range", "unique_relations", "total_relations",
        "relations_hash", "checked_with_check_rels", "conservation_checked",
        "wall_seconds", "cpu_seconds", "relations_per_cpu_second"
    }
    assert required_sieving_keys.issubset(sieving.keys()), f"Missing sieving keys: {required_sieving_keys - sieving.keys()}"
    assert sieving["wall_seconds"] == 3.50
    assert sieving["cpu_seconds"] == 3.45
    assert sieving["conservation_checked"] is True
    assert sieving["checked_with_check_rels"] is True


def test_compute_distribution_metrics_precision():
    """Verify that compute_distribution_metrics does not truncate small floating point numbers (e.g. Murphy-E)."""
    from nsb.experiments.r3_calibration_runner import compute_distribution_metrics

    # Pinned 80d calibration Murphy-E raw observations
    raw_vals = [2.56e-06, 2.73e-06, 2.73e-06, 2.95e-06, 2.97e-06, 3.02e-06, 3.09e-06, 3.14e-06, 3.39e-06, 4.04e-06]
    metrics = compute_distribution_metrics(raw_vals)

    assert metrics["count"] == 10
    assert metrics["min"] == 2.56e-6
    assert metrics["max"] == 4.04e-6
    assert abs(metrics["p10"] - 2.713e-6) < 1e-12
    assert abs(metrics["p50"] - 2.995e-6) < 1e-12
    assert abs(metrics["p90"] - 3.455e-6) < 1e-12
    # Ensure percentiles are distinct, not collapsed to identical 3e-6 by 6-decimal rounding
    assert metrics["p10"] != metrics["p50"] != metrics["p90"]


def test_c95_c100_sieve_command_building(tmp_path):
    """Verify that c95 and c100 profiles inject -lambda0 and -lambda1 into las command arguments."""
    from nsb.baselines.cado_nfs.sieve import CadoRelationCollector
    from nsb.baselines.cado_nfs.profiles import CADO_PARAMS_C95, CADO_PARAMS_C100
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)
    mock_adapter.run_binary.return_value = CommandExecutionResult(
        command=["las"],
        binary_name="las",
        returncode=0,
        stdout="1,2:3:5\n# Total 1 relations\n# Total cpu time: 0.1s\n# Total elapsed time: 0.1s\n",
        stderr="",
        wall_seconds=0.1,
        cpu_seconds=0.1,
        max_rss_mb=10.0,
    )

    collector = CadoRelationCollector(adapter=mock_adapter)

    # 1. c95 profile
    collector.collect_relations(
        poly=VERIFIED_C60_POLY,
        q_start=100000,
        q_range=5000,
        profile=CADO_PARAMS_C95,
        run_makefb=False,
        validate_with_check_rels=False,
    )
    call_args_c95 = mock_adapter.run_binary.call_args[0][1]
    assert "-lambda0" in call_args_c95
    idx_l0 = call_args_c95.index("-lambda0")
    assert call_args_c95[idx_l0 + 1] == "1.94"
    assert "-lambda1" in call_args_c95
    idx_l1 = call_args_c95.index("-lambda1")
    assert call_args_c95[idx_l1 + 1] == "1.91"

    # 2. c100 profile
    collector.collect_relations(
        poly=VERIFIED_C60_POLY,
        q_start=180000,
        q_range=5000,
        profile=CADO_PARAMS_C100,
        run_makefb=False,
        validate_with_check_rels=False,
    )
    call_args_c100 = mock_adapter.run_binary.call_args[0][1]
    assert "-lambda0" in call_args_c100
    idx_l0_100 = call_args_c100.index("-lambda0")
    assert call_args_c100[idx_l0_100 + 1] == "1.9" or call_args_c100[idx_l0_100 + 1] == "1.90"
    assert "-lambda1" in call_args_c100
    idx_l1_100 = call_args_c100.index("-lambda1")
    assert call_args_c100[idx_l1_100 + 1] == "1.93"


def test_scorer_integer_area_formatting():
    """Verify that CadoScorer formats area as exact integer string rather than scientific notation."""
    from nsb.baselines.cado_nfs.scorer import CadoScorer
    from nsb.experiments.r3_nfs_baseline_runner import VERIFIED_C60_POLY

    mock_adapter = MagicMock(spec=CadoSubprocessAdapter)
    mock_adapter.run_binary.return_value = CommandExecutionResult(
        command=["score"],
        binary_name="score",
        returncode=0,
        stdout="# exp_E 43.1, lognorm 45.2, skew 1.5, 3 rroots\n# MurphyE = 2.45e-11\n",
        stderr="",
        wall_seconds=0.1,
        cpu_seconds=0.1,
        max_rss_mb=10.0,
    )

    scorer = CadoScorer(adapter=mock_adapter)
    # Area = 32485408768.0 (c60 profile area)
    scorer.score(VERIFIED_C60_POLY, area=32485408768.0)

    call_args = mock_adapter.run_binary.call_args[0][1]
    assert "-area" in call_args
    idx_area = call_args.index("-area")
    area_arg = call_args[idx_area + 1]
    assert area_arg == "32485408768"
    assert "e+" not in area_arg

