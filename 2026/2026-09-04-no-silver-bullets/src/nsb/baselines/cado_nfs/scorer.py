"""CADO-NFS polynomial scoring harness using discrete `score` binary.

Evaluates an NfsPolynomialPair using CADO's native scoring executable:
`polyselect/score --full <poly_file>`
extracting Murphy-E, exp_E (lognorm), alpha, skewness, and tracking exact CPU core-seconds.
"""

from pathlib import Path
import tempfile
from typing import List, Optional, Union

from nsb.baselines.cado_nfs.adapter import CadoSubprocessAdapter
from nsb.baselines.cado_nfs.models import CadoScoreResult, NfsPolynomialPair
from nsb.baselines.cado_nfs.parser import parse_cado_score_output


class CadoScorer:
    """Wrapper around discrete CADO-NFS `score` binary."""

    def __init__(self, adapter: Optional[CadoSubprocessAdapter] = None):
        self.adapter = adapter or CadoSubprocessAdapter()

    def score(
        self,
        poly: Union[NfsPolynomialPair, str, Path],
        bf: int = 1_000_000,
        bg: int = 500_000,
        area: float = 1e7,
        flags: Optional[List[str]] = None,
        timeout_seconds: float = 60.0,
    ) -> CadoScoreResult:
        """Evaluate polynomial pair with CADO score binary.

        Args:
            poly: NfsPolynomialPair instance, or path to .poly file.
            bf: Algebraic side factor base bound (Bf).
            bg: Rational side factor base bound (Bg).
            area: Sieve area.
            flags: Optional custom command line flags.
            timeout_seconds: Maximum wall-clock execution time.

        Returns:
            CadoScoreResult containing parsed metrics and CPU timings.
        """
        temp_poly_file: Optional[Path] = None

        try:
            if isinstance(poly, NfsPolynomialPair):
                with tempfile.NamedTemporaryFile(mode="w", suffix=".poly", delete=False, encoding="utf-8") as tf:
                    tf.write(poly.to_cado_poly_string())
                    temp_poly_file = Path(tf.name)
                poly_path = temp_poly_file
            elif isinstance(poly, (str, Path)):
                poly_path = Path(poly)
                if not poly_path.is_file():
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".poly", delete=False, encoding="utf-8") as tf:
                        tf.write(str(poly))
                        temp_poly_file = Path(tf.name)
                    poly_path = temp_poly_file
            else:
                raise TypeError(f"Unsupported poly type: {type(poly)}")

            if flags is not None:
                args = list(flags)
                if "--full" not in args:
                    args = ["--full"] + args
                args.append(str(poly_path))
            else:
                args = [
                    "--full",
                    "-Bf", str(bf),
                    "-Bg", str(bg),
                    "-area", str(int(area)),
                    str(poly_path),
                ]
            cmd_result = self.adapter.run_binary("score", args, timeout_seconds=timeout_seconds)

            if cmd_result.returncode != 0:
                raise RuntimeError(
                    f"CADO score failed with return code {cmd_result.returncode}:\n"
                    f"{cmd_result.stderr or cmd_result.stdout}"
                )

            score_res = parse_cado_score_output(cmd_result.stdout)
            score_res.wall_seconds = cmd_result.wall_seconds
            score_res.cpu_seconds = cmd_result.cpu_seconds
            return score_res

        finally:
            if temp_poly_file and temp_poly_file.exists():
                try:
                    temp_poly_file.unlink()
                except Exception:
                    pass
