"""Polynomial selection interfaces and CADO-NFS baseline selector.

Supports:
1. CandidatePolynomialSelector: Abstract base class for all R3 polynomial selectors.
2. CadoPolynomialSelector: Mature baseline wrapping discrete CADO `polyselect` and `polyselect_ropt`.
"""

from abc import ABC, abstractmethod
from pathlib import Path
import tempfile
import time
from typing import List, Optional, Tuple, Union

from nsb.baselines.cado_nfs.adapter import CadoSubprocessAdapter
from nsb.baselines.cado_nfs.models import CadoPolyselectResult, NfsPolynomialPair
from nsb.baselines.cado_nfs.parser import parse_cado_poly_blocks, parse_cado_poly_file
from nsb.baselines.cado_nfs.profiles import CadoParameterProfile
from nsb.baselines.cado_nfs.verifier import verify_nfs_polynomial_pair


class CandidatePolynomialSelector(ABC):
    """Abstract interface for all NFS polynomial selectors."""

    @abstractmethod
    def select_polynomial(
        self,
        n: int,
        degree: int = 5,
        timeout_seconds: float = 300.0,
        **kwargs,
    ) -> CadoPolyselectResult:
        """Select an NFS polynomial pair for integer modulus n."""
        pass


class CadoPolynomialSelector(CandidatePolynomialSelector):
    """Mature baseline polynomial selector wrapping CADO-NFS discrete binaries.

    Pipeline:
    1. Run `polyselect` to find initial size-optimized polynomial pair.
       Supports CADO-style work-range splitting across [admin..admax] by `adrange`.
    2. Run `polyselect_ropt` to perform root optimization using matching Bf/Bg/area geometry.
    """

    def __init__(
        self,
        adapter: Optional[CadoSubprocessAdapter] = None,
        run_ropt: bool = True,
        enable_ropt: Optional[bool] = None,
        threads: int = 1,
    ):
        self.adapter = adapter or CadoSubprocessAdapter()
        self.enable_ropt = run_ropt if enable_ropt is None else enable_ropt
        self.threads = threads

    def select_polynomial(
        self,
        n: int,
        degree: int = 5,
        p_val: int = 420,
        admin: int = 0,
        admax: int = 10000,
        adrange: Optional[int] = None,
        incr: int = 60,
        nq: int = 1000,
        nrkeep: int = 10,
        ropteffort: float = 5.0,
        bf: Optional[int] = None,
        bg: Optional[int] = None,
        area: Optional[float] = None,
        keep: Optional[int] = None,
        profile: Optional[CadoParameterProfile] = None,
        timeout_seconds: float = 300.0,
        extra_polyselect_flags: Optional[List[str]] = None,
        extra_ropt_flags: Optional[List[str]] = None,
        **kwargs,
    ) -> CadoPolyselectResult:
        """Select polynomial using real CADO-NFS polyselect (+ ropt) pipeline."""
        if profile is not None:
            degree = profile.degree
            p_val = profile.p_val
            admin = profile.admin
            admax = profile.admax
            adrange = profile.adrange
            incr = profile.incr
            nq = profile.nq
            nrkeep = profile.nrkeep
            ropteffort = profile.ropteffort
            bf = profile.bf
            bg = profile.bg
            area = profile.area
            if keep is None and hasattr(profile, "keep"):
                keep = profile.keep

        executed_commands: List[str] = []
        total_cpu = 0.0
        total_wall = 0.0
        all_stdout: List[str] = []

        with tempfile.TemporaryDirectory(prefix="cado_polyselect_") as tmp_dir:
            tmp_path = Path(tmp_dir)
            t0 = time.time()

            # Stage 1: polyselect work ranges
            # If adrange is specified and splits admin..admax, run range-by-range like CADO task code
            work_ranges = []
            if adrange is not None and adrange > 0 and adrange < (admax - admin):
                curr = admin
                while curr < admax:
                    nxt = min(admax, curr + adrange)
                    work_ranges.append((curr, nxt))
                    curr = nxt
            else:
                work_ranges.append((admin, admax))

            all_candidate_blocks: List[NfsPolynomialPair] = []

            for r_admin, r_admax in work_ranges:
                poly_args = [
                    "-N", str(n),
                    "-degree", str(degree),
                    "-t", str(self.threads),
                    "-P", str(p_val),
                    "-admin", str(r_admin),
                    "-admax", str(r_admax),
                    "-incr", str(incr),
                    "-nq", str(nq),
                ]
                if keep is not None:
                    poly_args.extend(["-keep", str(keep)])
                if extra_polyselect_flags:
                    poly_args.extend(extra_polyselect_flags)

                remaining_timeout = max(5.0, timeout_seconds - (time.time() - t0))
                res1 = self.adapter.run_binary(
                    "polyselect",
                    poly_args,
                    timeout_seconds=remaining_timeout,
                    cwd=tmp_path,
                )
                total_cpu += res1.cpu_seconds
                total_wall += res1.wall_seconds
                executed_commands.append(" ".join(res1.command))
                all_stdout.append(res1.stdout)

                if res1.returncode != 0:
                    raise RuntimeError(
                        f"polyselect failed for range [{r_admin}..{r_admax}] "
                        f"(returncode {res1.returncode}):\n{res1.stderr or res1.stdout}"
                    )

                blocks = parse_cado_poly_blocks(res1.stdout)
                all_candidate_blocks.extend(blocks)

            if not all_candidate_blocks:
                raise ValueError(
                    f"polyselect produced 0 candidate polynomial blocks for N={n}:\n"
                    f"{''.join(all_stdout)[:1000]}"
                )

            # Task-level candidate retention: retain best nrkeep blocks by lowest exp_E (CADO preference).
            # Fail closed if candidates lack the exp_E needed for that ordering.
            if nrkeep is not None:
                if len(all_candidate_blocks) > nrkeep:
                    for idx, b in enumerate(all_candidate_blocks):
                        if b.metadata.get("exp_e") is None:
                            raise ValueError(
                                f"Candidate block {idx} lacks required 'exp_e' metadata for task-level nrkeep pruning "
                                f"(found {len(all_candidate_blocks)} candidates, nrkeep={nrkeep})"
                            )
                    all_candidate_blocks.sort(key=lambda b: float(b.metadata["exp_e"]))
                    all_candidate_blocks = all_candidate_blocks[:nrkeep]
                elif any(b.metadata.get("exp_e") is not None for b in all_candidate_blocks):
                    for idx, b in enumerate(all_candidate_blocks):
                        if b.metadata.get("exp_e") is None:
                            raise ValueError(
                                f"Candidate block {idx} lacks required 'exp_e' metadata for task-level ordering"
                            )
                    all_candidate_blocks.sort(key=lambda b: float(b.metadata["exp_e"]))

            # Save stage 1 candidate blocks into a candidate file for ropt
            candidates_file = tmp_path / "stage1_candidates.polys"
            with open(candidates_file, "w", encoding="utf-8") as cf:
                for b in all_candidate_blocks:
                    b.N = n
                    cf.write(b.to_cado_poly_string() + "\n")

            current_pair = all_candidate_blocks[0]
            current_pair.N = n

            # Stage 2: root optimization (polyselect_ropt) if enabled
            if self.enable_ropt:
                ropt_args = [
                    "-inputpolys", str(candidates_file),
                    "-ropteffort", f"{ropteffort}",
                    "-t", str(self.threads),
                ]
                # Tie ropt geometry to profile/scorer settings
                if bf is not None:
                    ropt_args.extend(["-Bf", str(bf)])
                if bg is not None:
                    ropt_args.extend(["-Bg", str(bg)])
                if area is not None:
                    ropt_args.extend(["-area", str(int(area))])
                if extra_ropt_flags:
                    ropt_args.extend(extra_ropt_flags)

                remaining_timeout = max(5.0, timeout_seconds - (time.time() - t0))
                res2 = self.adapter.run_binary(
                    "polyselect_ropt",
                    ropt_args,
                    timeout_seconds=remaining_timeout,
                    cwd=tmp_path,
                )
                total_cpu += res2.cpu_seconds
                total_wall += res2.wall_seconds
                executed_commands.append(" ".join(res2.command))
                all_stdout.append(res2.stdout)

                if res2.returncode != 0:
                    raise RuntimeError(
                        f"polyselect_ropt failed (returncode {res2.returncode}):\n{res2.stderr or res2.stdout}"
                    )

                ropt_blocks = parse_cado_poly_blocks(res2.stdout)
                if ropt_blocks:
                    # 1. Look for explicit "0-th best polynomial found" block
                    best_block = None
                    for b in ropt_blocks:
                        if b.metadata.get("is_best") or b.metadata.get("best_rank") == 0:
                            best_block = b
                            break

                    # 2. Select block with highest Murphy-E if parsed in metadata
                    if best_block is None:
                        scored_blocks = [b for b in ropt_blocks if "murphy_e" in b.metadata]
                        if scored_blocks:
                            best_block = max(scored_blocks, key=lambda b: b.metadata["murphy_e"])

                    # 3. Fallback: evaluate Murphy-E via neutral CadoScorer
                    if best_block is None and len(ropt_blocks) > 1:
                        try:
                            from nsb.baselines.cado_nfs.scorer import CadoScorer
                            scorer = CadoScorer(adapter=self.adapter)
                            best_score = -1.0
                            for b in ropt_blocks:
                                b.N = n
                                s_res = scorer.score(
                                    b,
                                    bf=bf or 1000000,
                                    bg=bg or 500000,
                                    area=area or 1e7,
                                )
                                if s_res.murphy_e > best_score:
                                    best_score = s_res.murphy_e
                                    best_block = b
                        except Exception:
                            best_block = ropt_blocks[0]

                    current_pair = best_block or ropt_blocks[0]
                    current_pair.N = n

            # Independent mathematical verification
            is_valid, msg = verify_nfs_polynomial_pair(current_pair)
            if not is_valid:
                raise ValueError(f"Selected polynomial pair failed mathematical verification: {msg}")

            return CadoPolyselectResult(
                pair=current_pair,
                modulus_n=n,
                degree=degree,
                cpu_seconds=round(total_cpu, 4),
                wall_seconds=round(total_wall, 4),
                raw_output="\n---\n".join(all_stdout),
                command=executed_commands,
            )

    def run_ropt(
        self,
        poly: NfsPolynomialPair,
        profile: CadoParameterProfile,
        timeout_seconds: float = 300.0,
        extra_ropt_flags: Optional[List[str]] = None,
        tmp_dir: Optional[Path] = None,
    ) -> CadoPolyselectResult:
        """Run standalone CADO polyselect_ropt on an existing polynomial pair."""
        t0 = time.time()
        executed_commands: List[str] = []

        def _do_ropt(work_dir: Path) -> CadoPolyselectResult:
            cand_file = work_dir / "candidate.poly"
            poly.save_cado_poly_file(cand_file)

            ropt_args = [
                "-inputpolys", str(cand_file),
                "-ropteffort", str(profile.ropteffort),
                "-t", str(self.threads),
            ]
            if profile.bf is not None:
                ropt_args.extend(["-Bf", str(profile.bf)])
            if profile.bg is not None:
                ropt_args.extend(["-Bg", str(profile.bg)])
            if profile.area is not None:
                ropt_args.extend(["-area", str(int(profile.area))])
            if extra_ropt_flags:
                ropt_args.extend(extra_ropt_flags)

            res = self.adapter.run_binary(
                "polyselect_ropt",
                ropt_args,
                timeout_seconds=timeout_seconds,
                cwd=work_dir,
            )
            executed_commands.append(" ".join(res.command))

            if res.returncode != 0:
                raise RuntimeError(
                    f"polyselect_ropt failed (returncode {res.returncode}):\n{res.stderr or res.stdout}"
                )

            ropt_blocks = parse_cado_poly_blocks(res.stdout)
            if not ropt_blocks:
                # Return original pair if ropt found no improvements
                best_pair = poly
            else:
                best_pair = None
                for b in ropt_blocks:
                    if b.metadata.get("is_best") or b.metadata.get("best_rank") == 0:
                        best_pair = b
                        break
                if best_pair is None:
                    scored_blocks = [b for b in ropt_blocks if "murphy_e" in b.metadata]
                    if scored_blocks:
                        best_pair = max(scored_blocks, key=lambda b: b.metadata["murphy_e"])
                    else:
                        best_pair = ropt_blocks[0]

            best_pair.N = poly.N
            is_valid, msg = verify_nfs_polynomial_pair(best_pair)
            if not is_valid:
                raise ValueError(f"Root-optimized polynomial pair failed verification: {msg}")

            return CadoPolyselectResult(
                pair=best_pair,
                modulus_n=poly.N,
                degree=profile.degree,
                cpu_seconds=round(res.cpu_seconds, 4),
                wall_seconds=round(res.wall_seconds, 4),
                raw_output=res.stdout,
                command=executed_commands,
            )

        if tmp_dir is not None:
            return _do_ropt(tmp_dir)
        else:
            with tempfile.TemporaryDirectory(prefix="cado_ropt_") as td:
                return _do_ropt(Path(td))

    def generate_stage1_pool(
        self,
        n: int,
        profile: CadoParameterProfile,
        timeout_seconds: float = 300.0,
        run_ropt_on_candidates: bool = True,
    ) -> Tuple[List[NfsPolynomialPair], float, float]:
        """Generate a candidate pool using CADO polyselect (+ ropt) and measure consumed resources."""
        executed_commands: List[str] = []
        total_cpu = 0.0
        total_wall = 0.0

        with tempfile.TemporaryDirectory(prefix="cado_pool_") as tmp_dir:
            tmp_path = Path(tmp_dir)
            t0 = time.time()

            work_ranges = []
            if profile.adrange is not None and profile.adrange > 0 and profile.adrange < (profile.admax - profile.admin):
                curr = profile.admin
                while curr < profile.admax:
                    nxt = min(profile.admax, curr + profile.adrange)
                    work_ranges.append((curr, nxt))
                    curr = nxt
            else:
                work_ranges.append((profile.admin, profile.admax))

            all_candidate_blocks: List[NfsPolynomialPair] = []
            for r_admin, r_admax in work_ranges:
                poly_args = [
                    "-N", str(n),
                    "-degree", str(profile.degree),
                    "-t", str(self.threads),
                    "-P", str(profile.p_val),
                    "-admin", str(r_admin),
                    "-admax", str(r_admax),
                    "-incr", str(profile.incr),
                    "-nq", str(profile.nq),
                ]
                remaining_timeout = max(5.0, timeout_seconds - (time.time() - t0))
                res1 = self.adapter.run_binary(
                    "polyselect",
                    poly_args,
                    timeout_seconds=remaining_timeout,
                    cwd=tmp_path,
                )
                total_cpu += res1.cpu_seconds
                total_wall += res1.wall_seconds
                if res1.returncode != 0:
                    raise RuntimeError(f"polyselect failed for pool generation: {res1.stderr}")
                blocks = parse_cado_poly_blocks(res1.stdout)
                all_candidate_blocks.extend(blocks)

            if not all_candidate_blocks:
                raise ValueError(f"polyselect produced 0 candidate blocks for N={n}")

            if profile.nrkeep is not None and len(all_candidate_blocks) > profile.nrkeep:
                all_candidate_blocks.sort(key=lambda b: float(b.metadata.get("exp_e", 0.0)))
                all_candidate_blocks = all_candidate_blocks[:profile.nrkeep]

            for b in all_candidate_blocks:
                b.N = n

            if not run_ropt_on_candidates:
                return all_candidate_blocks, round(total_cpu, 4), round(total_wall, 4)

            # Also run ropt to populate ropt'd pool
            candidates_file = tmp_path / "stage1_candidates.polys"
            with open(candidates_file, "w", encoding="utf-8") as cf:
                for b in all_candidate_blocks:
                    cf.write(b.to_cado_poly_string() + "\n")

            ropt_args = [
                "-inputpolys", str(candidates_file),
                "-ropteffort", str(profile.ropteffort),
                "-t", str(self.threads),
                "-Bf", str(profile.bf),
                "-Bg", str(profile.bg),
                "-area", str(int(profile.area)),
            ]
            remaining_timeout = max(5.0, timeout_seconds - (time.time() - t0))
            res2 = self.adapter.run_binary(
                "polyselect_ropt",
                ropt_args,
                timeout_seconds=remaining_timeout,
                cwd=tmp_path,
            )
            total_cpu += res2.cpu_seconds
            total_wall += res2.wall_seconds

            if res2.returncode != 0:
                raise RuntimeError(
                    f"polyselect_ropt failed for pool generation (returncode {res2.returncode}):\n{res2.stderr or res2.stdout}"
                )

            ropt_blocks = parse_cado_poly_blocks(res2.stdout)
            if not ropt_blocks:
                raise ValueError("polyselect_ropt produced 0 valid polynomial blocks for candidate pool")
            for p in ropt_blocks:
                p.N = n

            return ropt_blocks, round(total_cpu, 4), round(total_wall, 4)

