"""CADO-NFS relation collection harness wrapping discrete `makefb` and `las` binaries.

Supports:
1. Exact parameter parity (identical factor base bounds, large prime bounds, special-q range).
2. Summed CPU accounting for factor base generation + lattice sieving.
3. Parsing of raw relations, yield metrics, and throughput.
"""

from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional, Union

from nsb.baselines.cado_nfs.adapter import CadoSubprocessAdapter
from nsb.baselines.cado_nfs.models import CadoSieveResult, NfsPolynomialPair
from nsb.baselines.cado_nfs.parser import parse_las_output
from nsb.baselines.cado_nfs.profiles import CadoParameterProfile


class CadoRelationCollector:
    """Manages discrete relation collection using CADO `makefb` and `las`."""

    def __init__(
        self,
        adapter: Optional[CadoSubprocessAdapter] = None,
        threads: int = 1,
    ):
        self.adapter = adapter or CadoSubprocessAdapter()
        self.threads = threads

    def collect_relations(
        self,
        poly: Union[NfsPolynomialPair, str, Path],
        q_start: int,
        q_range: int,
        i_param: int = 11,
        lim0: int = 500_000,
        lim1: int = 1_000_000,
        lpb0: int = 22,
        lpb1: int = 22,
        mfb0: Optional[int] = None,
        mfb1: Optional[int] = None,
        sqside: int = 1,
        ncurves0: Optional[int] = None,
        ncurves1: Optional[int] = None,
        lambda0: Optional[float] = None,
        lambda1: Optional[float] = None,
        profile: Optional[CadoParameterProfile] = None,
        run_makefb: bool = True,
        validate_with_check_rels: bool = True,
        timeout_seconds: float = 300.0,
        extra_las_flags: Optional[List[str]] = None,
    ) -> CadoSieveResult:
        """Run discrete relation collection on a fixed special-q range.

        Args:
            poly: NfsPolynomialPair instance, or path to .poly file.
            q_start: Starting special-q prime.
            q_range: Length of special-q interval (q1 = q_start + q_range).
            i_param: Sieve region parameter I (default: 11 for custom canary plumbing).
            lim0: Side 0 factor base bound (default: 500,000).
            lim1: Side 1 factor base bound (default: 1,000,000).
            lpb0: Side 0 large prime bound in bits (default: 22).
            lpb1: Side 1 large prime bound in bits (default: 22).
            mfb0: Side 0 maximal factor base bound (default: 2 * lpb0).
            mfb1: Side 1 maximal factor base bound (default: 2 * lpb1).
            sqside: Special-q side (default: 1, algebraic side).
            ncurves0: Number of ECM curves for side 0 cofactorization.
            ncurves1: Number of ECM curves for side 1 cofactorization.
            profile: Optional CadoParameterProfile overriding sieving parameters.
            run_makefb: If True (default), runs discrete side-specific makefb.
            validate_with_check_rels: If True, validates relations with check_rels.
            timeout_seconds: Maximum wall time.
            extra_las_flags: Extra arguments to pass to las.

        Returns:
            CadoSieveResult with relation counts, sorted relations hash, and summed CPU time.
        """
        if profile is not None:
            i_param = profile.i_param
            lim0 = profile.lim0
            lim1 = profile.lim1
            lpb0 = profile.lpb0
            lpb1 = profile.lpb1
            mfb0_val = profile.mfb0
            mfb1_val = profile.mfb1
            sqside = profile.sqside
            ncurves0 = profile.ncurves0
            ncurves1 = profile.ncurves1
            lambda0_val = profile.lambda0 if profile.lambda0 is not None else lambda0
            lambda1_val = profile.lambda1 if profile.lambda1 is not None else lambda1
        else:
            mfb0_val = mfb0 if mfb0 is not None else (2 * lpb0)
            mfb1_val = mfb1 if mfb1 is not None else (2 * lpb1)
            lambda0_val = lambda0
            lambda1_val = lambda1

        total_cpu = 0.0
        total_wall = 0.0
        raw_outputs: List[str] = []

        with tempfile.TemporaryDirectory(prefix="cado_sieve_") as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Prepare poly file
            if isinstance(poly, NfsPolynomialPair):
                poly_path = tmp_path / "target.poly"
                poly.save_cado_poly_file(poly_path)
            elif isinstance(poly, (str, Path)):
                poly_candidate = Path(poly)
                if poly_candidate.is_file():
                    poly_path = poly_candidate
                else:
                    poly_path = tmp_path / "target.poly"
                    poly_path.write_text(str(poly), encoding="utf-8")
            else:
                raise TypeError(f"Unsupported poly type: {type(poly)}")

            # Mandatory / side-specific makefb step
            fb_args_las: List[str] = []
            if run_makefb:
                # Side 0 factor base (maxbits derived from I per CADO task implementation)
                fb0_path = tmp_path / "side0.fb"
                fb0_args = [
                    "-poly", str(poly_path),
                    "-lim", str(lim0),
                    "-maxbits", str(i_param),
                    "-side", "0",
                    "-out", str(fb0_path),
                ]
                fb0_res = self.adapter.run_binary(
                    "makefb",
                    fb0_args,
                    timeout_seconds=min(120.0, timeout_seconds),
                    cwd=tmp_path,
                )
                total_cpu += fb0_res.cpu_seconds
                total_wall += fb0_res.wall_seconds
                raw_outputs.append(fb0_res.stdout)

                if fb0_res.returncode != 0 or not fb0_path.exists() or fb0_path.stat().st_size == 0:
                    raise RuntimeError(
                        f"makefb side 0 failed (returncode {fb0_res.returncode}):\n"
                        f"{fb0_res.stderr or fb0_res.stdout}"
                    )

                # Side 1 factor base (maxbits derived from I per CADO task implementation)
                fb1_path = tmp_path / "side1.fb"
                fb1_args = [
                    "-poly", str(poly_path),
                    "-lim", str(lim1),
                    "-maxbits", str(i_param),
                    "-side", "1",
                    "-out", str(fb1_path),
                ]
                fb1_res = self.adapter.run_binary(
                    "makefb",
                    fb1_args,
                    timeout_seconds=min(120.0, timeout_seconds),
                    cwd=tmp_path,
                )
                total_cpu += fb1_res.cpu_seconds
                total_wall += fb1_res.wall_seconds
                raw_outputs.append(fb1_res.stdout)

                if fb1_res.returncode != 0 or not fb1_path.exists() or fb1_path.stat().st_size == 0:
                    raise RuntimeError(
                        f"makefb side 1 failed (returncode {fb1_res.returncode}):\n"
                        f"{fb1_res.stderr or fb1_res.stdout}"
                    )

                fb_args_las = [
                    "-fb0", str(fb0_path),
                    "-fb1", str(fb1_path),
                ]

            # las step with complete CADO parameter profile
            q_end = q_start + q_range
            las_args = [
                "-poly", str(poly_path),
                "-I", str(i_param),
                "-lim0", str(lim0),
                "-lim1", str(lim1),
                "-lpb0", str(lpb0),
                "-lpb1", str(lpb1),
                "-mfb0", str(mfb0_val),
                "-mfb1", str(mfb1_val),
                "-sqside", str(sqside),
                "-q0", str(q_start),
                "-q1", str(q_end),
                "-t", str(self.threads),
            ]
            if ncurves0 is not None:
                las_args.extend(["-ncurves0", str(ncurves0)])
            if ncurves1 is not None:
                las_args.extend(["-ncurves1", str(ncurves1)])
            if lambda0_val is not None:
                las_args.extend(["-lambda0", str(lambda0_val)])
            if lambda1_val is not None:
                las_args.extend(["-lambda1", str(lambda1_val)])
            las_args.extend(fb_args_las)
            if extra_las_flags:
                las_args.extend(extra_las_flags)

            las_res = self.adapter.run_binary(
                "las",
                las_args,
                timeout_seconds=timeout_seconds,
                cwd=tmp_path,
            )
            total_cpu += las_res.cpu_seconds
            total_wall += las_res.wall_seconds
            raw_outputs.append(las_res.stdout)

            if las_res.returncode != 0:
                raise RuntimeError(
                    f"las execution failed (returncode {las_res.returncode}):\n"
                    f"{las_res.stderr or las_res.stdout}"
                )

            # Parse results
            sieve_res = parse_las_output(las_res.stdout)

            # Validate relations with check_rels if enabled
            checked_rels = False
            if validate_with_check_rels:
                check_rels_bin = self.adapter.env.get_binary_path("check_rels")
                if not check_rels_bin or not check_rels_bin.exists():
                    raise RuntimeError(
                        "check_rels binary is required for relation validation but was not found. "
                        "Ensure CADO was built into build/nsb-r3 and misc/check_rels is present."
                    )
                # Extract relations into text file
                relations_lines = [
                    line for line in las_res.stdout.splitlines()
                    if not line.startswith("#") and ":" in line and "," in line
                ]

                # Conservation check: relations sent to check_rels must equal parsed relations
                if sieve_res.parsed_relations_count is not None:
                    if len(relations_lines) != sieve_res.parsed_relations_count:
                        raise ValueError(
                            f"Relation conservation mismatch: {len(relations_lines)} lines extracted "
                            f"for check_rels but {sieve_res.parsed_relations_count} lines parsed from las"
                        )

                if relations_lines:
                    rel_file = tmp_path / "relations.txt"
                    rel_file.write_text("\n".join(relations_lines) + "\n", encoding="utf-8")
                    chk_args = [
                        "-poly", str(poly_path),
                        "-lpb0", str(lpb0),
                        "-lpb1", str(lpb1),
                        "-check_primality",
                        str(rel_file),
                    ]
                    chk_res = self.adapter.run_binary(
                        "check_rels",
                        chk_args,
                        timeout_seconds=60.0,
                        cwd=tmp_path,
                    )
                    total_cpu += chk_res.cpu_seconds
                    total_wall += chk_res.wall_seconds
                    if chk_res.returncode != 0:
                        raise RuntimeError(
                            f"check_rels validation failed (returncode {chk_res.returncode}):\n{chk_res.stderr or chk_res.stdout}"
                        )
                    checked_rels = True

            sieve_res.checked_with_check_rels = checked_rels

            # Use summed discrete CPU accounting if higher than internal las timer
            if total_cpu > 0:
                sieve_res.cpu_seconds = round(total_cpu, 4)
                sieve_res.wall_seconds = round(total_wall, 4)
                if sieve_res.cpu_seconds > 0:
                    sieve_res.relations_per_cpu_second = round(
                        sieve_res.unique_relations / sieve_res.cpu_seconds, 4
                    )
            sieve_res.checked_with_check_rels = checked_rels
            sieve_res.raw_output = "\n---\n".join(raw_outputs)
            sieve_res.q_start = q_start
            sieve_res.q_range = q_range

            return sieve_res
