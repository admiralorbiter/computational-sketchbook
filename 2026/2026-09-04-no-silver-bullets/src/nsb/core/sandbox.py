"""Worker execution sandbox enforcing strict physical isolation from sealed ground truth."""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from nsb.benchmarks.corpus import TRIPWIRE_FILENAME


class IsolationViolationError(RuntimeError):
    """Raised when sealed truth or tripwire files are detected inside a worker sandbox."""
    pass


class WorkerSandbox:
    """Manages an isolated execution directory for research workers.

    Workers operate in a sandboxed scratch workspace where only public benchmarks
    are mounted/copied. Sealed truth directories are strictly excluded.
    """

    def __init__(
        self,
        base_dir: Union[str, Path],
        scratch_base: Optional[Union[str, Path]] = None,
        cleanup_on_exit: bool = False,
    ):
        self.base_dir = Path(base_dir).resolve()
        self.scratch_base = Path(scratch_base).resolve() if scratch_base else (self.base_dir / "experiments" / "sandboxes")
        self.cleanup_on_exit = cleanup_on_exit
        self.sandbox_dir: Optional[Path] = None

    def setup(
        self,
        experiment_id: str,
        run_id: str,
        version: Optional[str] = None,
        split: Optional[str] = None,
    ) -> Path:
        """Create the isolated sandbox directory with only public benchmark assets."""
        self.sandbox_dir = self.scratch_base / experiment_id / run_id
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

        # Mirror public benchmarks if available
        public_src = self.base_dir / "benchmarks" / "public"
        if public_src.exists():
            dest_public = self.sandbox_dir / "benchmarks" / "public"
            if version and split:
                src_split = public_src / version / split
                if src_split.exists():
                    dest_split = dest_public / version / split
                    dest_split.parent.mkdir(parents=True, exist_ok=True)
                    if dest_split.exists():
                        shutil.rmtree(dest_split)
                    shutil.copytree(src_split, dest_split)
            else:
                if dest_public.exists():
                    shutil.rmtree(dest_public)
                shutil.copytree(public_src, dest_public)

        # Audit that sealed truth is definitely NOT present in sandbox
        self.verify_no_sealed_leakage(self.sandbox_dir)
        return self.sandbox_dir

    @staticmethod
    def verify_no_sealed_leakage(target_dir: Union[str, Path]) -> None:
        """Scan directory to ensure no sealed truth or tripwire files exist."""
        path = Path(target_dir)
        for root, dirs, files in os.walk(path):
            if "sealed" in dirs:
                raise IsolationViolationError(f"Sealed directory detected in sandbox: {Path(root) / 'sealed'}")
            for f in files:
                if f == TRIPWIRE_FILENAME:
                    raise IsolationViolationError(f"Tripwire file detected in sandbox: {Path(root) / f}")
                if f == "truth.jsonl":
                    raise IsolationViolationError(f"Sealed truth.jsonl detected in sandbox: {Path(root) / f}")

    def cleanup(self) -> None:
        if self.cleanup_on_exit and self.sandbox_dir and self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)

    def __enter__(self) -> "WorkerSandbox":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.cleanup()
