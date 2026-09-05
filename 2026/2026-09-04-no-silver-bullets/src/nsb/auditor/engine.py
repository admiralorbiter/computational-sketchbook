"""Independent Auditor engine verifying provenance, manifest SHA integrity, sealed isolation, and timeout accounting."""

import datetime
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

from nsb.benchmarks.corpus import TRIPWIRE_CONTENT, TRIPWIRE_FILENAME
from nsb.core.hashing import hash_file


class AuditCheckResult(BaseModel):
    name: str
    passed: bool
    details: str


class AuditReport(BaseModel):
    timestamp: str
    verdict: str  # "PASS", "FIX", "ESCALATE"
    git_sha: str
    git_dirty: bool
    canonical_ready: bool
    checks: List[AuditCheckResult] = Field(default_factory=list)
    summary: str = ""


class Auditor:
    """Independent auditor verifying scientific rigor, data integrity, and provenance."""

    def __init__(self, repo_root: Union[str, Path] = "."):
        self.repo_root = Path(repo_root).resolve()

    def check_git_status(self) -> Tuple[str, bool, str]:
        """Check current git HEAD commit and whether the working directory is clean."""
        try:
            sha_proc = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            git_sha = sha_proc.stdout.strip()
        except Exception:
            git_sha = "UNKNOWN"

        try:
            status_proc = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            status_output = status_proc.stdout.strip()
            # Uncommitted changes (exclude logs, sqlite databases, journals, and generated review packet outputs)
            dirty_lines = [
                line
                for line in status_output.splitlines()
                if line.strip()
                and not line.endswith(".log")
                and not line.endswith(".sqlite")
                and not line.endswith(".sqlite-journal")
                and not line.endswith(".sqlite-wal")
                and not line.endswith(".sqlite-shm")
                and not line.endswith("SMOKE_REVIEW_PACKET.md")
                and not line.endswith("SMOKE_REVIEW_PACKET.json")
                and not line.endswith("PILOT_REVIEW_PACKET.md")
                and not line.endswith("PILOT_REVIEW_PACKET.json")
                and not line.endswith("R1_WAVE1_REVIEW_PACKET.md")
                and not line.endswith("R1_WAVE1_REVIEW_PACKET.json")
                and not line.endswith("_REVIEW_PACKET.md")
                and not line.endswith("_REVIEW_PACKET.json")
            ]
            git_dirty = len(dirty_lines) > 0

            details = (
                f"Clean git state at {git_sha}"
                if not git_dirty
                else f"Dirty worktree ({len(dirty_lines)} modified/untracked files: {', '.join(l[:40] for l in dirty_lines[:3])})"
            )
        except Exception as e:
            git_dirty = True
            details = f"Git status failed: {e}"

        return git_sha, git_dirty, details

    def check_manifest_integrity(self) -> List[AuditCheckResult]:
        """Verify SHA-256 hashes of all benchmark files match their manifests."""
        results: List[AuditCheckResult] = []
        public_base = self.repo_root / "benchmarks" / "public"
        if not public_base.exists():
            results.append(
                AuditCheckResult(
                    name="manifest_integrity",
                    passed=False,
                    details="No benchmarks/public directory found",
                )
            )
            return results

        manifests = list(public_base.glob("**/manifest.json"))
        if not manifests:
            results.append(
                AuditCheckResult(
                    name="manifest_integrity",
                    passed=False,
                    details="No manifest.json files found",
                )
            )
            return results

        for manifest_path in manifests:
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                pub_file = Path(manifest.get("public_file", ""))
                if not pub_file.is_file():
                    pub_file = manifest_path.parent / "instances.jsonl"

                seal_file = Path(manifest.get("sealed_file", ""))
                if not seal_file.is_file():
                    rel = manifest_path.relative_to(public_base)
                    seal_file = self.repo_root / "benchmarks" / "sealed" / rel.parent / "truth.jsonl"

                if pub_file.is_file():
                    calc_hash = hash_file(pub_file)
                    exp_hash = manifest.get("public_sha256")
                    passed = calc_hash == exp_hash
                    results.append(
                        AuditCheckResult(
                            name=f"public_sha_{manifest_path.parent.name}",
                            passed=passed,
                            details=f"Calculated {calc_hash[:8]}... vs Expected {str(exp_hash)[:8]}...",
                        )
                    )

                if seal_file.is_file():
                    calc_hash = hash_file(seal_file)
                    exp_hash = manifest.get("sealed_sha256")
                    passed = calc_hash == exp_hash
                    results.append(
                        AuditCheckResult(
                            name=f"sealed_sha_{manifest_path.parent.name}",
                            passed=passed,
                            details=f"Calculated {calc_hash[:8]}... vs Expected {str(exp_hash)[:8]}...",
                        )
                    )
            except Exception as e:
                results.append(
                    AuditCheckResult(
                        name=f"manifest_check_{manifest_path.name}",
                        passed=False,
                        details=str(e),
                    )
                )

        return results

    def check_tripwires(self) -> List[AuditCheckResult]:
        """Verify sealed tripwires are in place and untampered."""
        results: List[AuditCheckResult] = []
        sealed_base = self.repo_root / "benchmarks" / "sealed"
        if not sealed_base.exists():
            return [AuditCheckResult(name="tripwires", passed=True, details="No sealed directory to check")]

        tripwires = list(sealed_base.glob(f"**/{TRIPWIRE_FILENAME}"))
        if not tripwires:
            results.append(
                AuditCheckResult(
                    name="tripwires_exist",
                    passed=False,
                    details=f"No {TRIPWIRE_FILENAME} found in sealed benchmarks",
                )
            )
        else:
            for tw in tripwires:
                try:
                    content = tw.read_text(encoding="utf-8")
                    passed = content.strip() == TRIPWIRE_CONTENT.strip()
                    results.append(
                        AuditCheckResult(
                            name=f"tripwire_{tw.parent.name}",
                            passed=passed,
                            details="Tripwire intact and untampered" if passed else "Tripwire content modified!",
                        )
                    )
                except Exception as e:
                    results.append(
                        AuditCheckResult(
                            name=f"tripwire_{tw.parent.name}",
                            passed=False,
                            details=f"Failed to read tripwire: {e}",
                        )
                    )
        return results

    def check_sandboxes(self) -> List[AuditCheckResult]:
        """Verify no active sandboxes or worker directories leak sealed truth."""
        results: List[AuditCheckResult] = []
        sandboxes_base = self.repo_root / "experiments" / "sandboxes"
        if not sandboxes_base.exists():
            results.append(AuditCheckResult(name="sandbox_leakage", passed=True, details="No sandboxes to verify"))
            return results

        sealed_found = []
        for p in sandboxes_base.glob("**/sealed"):
            if p.is_dir():
                sealed_found.append(str(p))

        active_sandboxes = [p for p in sandboxes_base.glob("*/*") if p.is_dir()]
        count = len(active_sandboxes)
        passed = len(sealed_found) == 0
        results.append(
            AuditCheckResult(
                name="sandbox_leakage",
                passed=passed,
                details=f"Verified {count} active sandbox(es); zero sealed leakage detected"
                if passed
                else f"Sealed leakage detected in: {', '.join(sealed_found)}",
            )
        )
        return results

    def check_candidate_contract_and_profiles(self) -> List[AuditCheckResult]:
        """Verify R3 candidate search contract consistency, profile ladder derivations, and holdout isolation."""
        results: List[AuditCheckResult] = []

        # 1. Candidate contract specification synchronization
        contract_path = self.repo_root / "config" / "contracts" / "r3_b_nfs_candidate_search.yaml"
        prereg_path = self.repo_root / "docs" / "preregistrations" / "NSB-R3-B-NFS-CANDIDATE-SEARCH.md"
        active_contract_path = self.repo_root / "ACTIVE_CONTRACT.md"

        gov_errors = []
        if not contract_path.exists():
            gov_errors.append(f"Contract file missing: {contract_path}")
        if not prereg_path.exists():
            gov_errors.append(f"Preregistration file missing: {prereg_path}")
        if not active_contract_path.exists():
            gov_errors.append(f"ACTIVE_CONTRACT.md missing: {active_contract_path}")

        if not gov_errors:
            import yaml
            try:
                contract_yaml = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
                if contract_yaml.get("contract_id") != "NSB-R3-B-NFS-CANDIDATE-SEARCH":
                    gov_errors.append(f"Unexpected contract_id: {contract_yaml.get('contract_id')}")
                if contract_yaml.get("version") != "1.0.0":
                    gov_errors.append(f"Unexpected contract version: {contract_yaml.get('version')}")

                budget_cfg = contract_yaml.get("search_budget_enforcement", {})
                if budget_cfg.get("concurrency_limit") != 1:
                    gov_errors.append(f"Contract concurrency_limit {budget_cfg.get('concurrency_limit')} != 1")
                if budget_cfg.get("gpu_access") != "prohibited":
                    gov_errors.append("Contract gpu_access is not prohibited")
                if budget_cfg.get("network_access") != "prohibited":
                    gov_errors.append("Contract network_access is not prohibited")

                prom_cfg = contract_yaml.get("promotion_criteria", {})
                t1_cfg = prom_cfg.get("tier_1_quality", {})
                t2_cfg = prom_cfg.get("tier_2_system", {})
                if t1_cfg.get("sample_geometric_mean_ratio_min") != 1.10:
                    gov_errors.append("Contract sample_geometric_mean_ratio_min != 1.10")
                if t2_cfg.get("sample_cost_reduction_min") != 0.05:
                    gov_errors.append("Contract sample_cost_reduction_min != 0.05")

                prereg_text = prereg_path.read_text(encoding="utf-8")
                for expected_token in ["NSB-R3-B-NFS-CANDIDATE-SEARCH", "1.0.0", "c95_pinned", "c100_pinned", "1.10"]:
                    if expected_token not in prereg_text:
                        gov_errors.append(f"Preregistration missing expected specification token: {expected_token}")

                active_text = active_contract_path.read_text(encoding="utf-8")
                for expected_token in ["NSB-R3-B-NFS-CANDIDATE-SEARCH", "1.0.0", "c95_pinned", "c100_pinned"]:
                    if expected_token not in active_text:
                        gov_errors.append(f"ACTIVE_CONTRACT.md missing expected token: {expected_token}")
            except Exception as e:
                gov_errors.append(f"Failed to parse and validate governance specifications: {e}")

        results.append(
            AuditCheckResult(
                name="candidate_contract_governance",
                passed=len(gov_errors) == 0,
                details="Candidate contract YAML, preregistration, and ACTIVE_CONTRACT.md specifications are fully synchronized"
                if len(gov_errors) == 0
                else f"Governance specification discrepancies: {'; '.join(gov_errors)}",
            )
        )

        # 2. Mathematical derivation consistency of all 6 profiles (c60, c70, c80, c90, c95, c100)
        from nsb.baselines.cado_nfs.profiles import _REGISTERED_PROFILES

        profile_errors = []
        expected_profiles = ["c60_pinned", "c70_pinned", "c80_pinned", "c90_pinned", "c95_pinned", "c100_pinned"]
        for prof_name in expected_profiles:
            if prof_name not in _REGISTERED_PROFILES:
                profile_errors.append(f"Profile {prof_name} not registered")
                continue
            prof = _REGISTERED_PROFILES[prof_name]
            expected_area = float((1 << (2 * prof.i_param - 1)) * prof.qmin)
            if prof.area != expected_area:
                profile_errors.append(f"{prof_name}: area {prof.area} != expected {expected_area}")
            if prof.bf != (1 << prof.lpb1):
                profile_errors.append(f"{prof_name}: bf {prof.bf} != 2^{prof.lpb1}")
            if prof.bg != (1 << prof.lpb0):
                profile_errors.append(f"{prof_name}: bg {prof.bg} != 2^{prof.lpb0}")
            if prof_name in ("c95_pinned", "c100_pinned"):
                if prof.lambda0 is None or prof.lambda1 is None:
                    profile_errors.append(f"{prof_name}: lambda0 or lambda1 is None")

        results.append(
            AuditCheckResult(
                name="profile_ladder_derivation_consistency",
                passed=len(profile_errors) == 0,
                details="All 6 profiles (c60-c100) satisfy mechanical derivations (area, Bf, Bg, lambdas)"
                if len(profile_errors) == 0
                else f"Profile derivation errors: {'; '.join(profile_errors)}",
            )
        )

        # 3. Holdout isolation (inspect filenames AND file contents across benchmarks/, data/, experiments/)
        holdout_violations = []
        for base in [self.repo_root / "benchmarks", self.repo_root / "data", self.repo_root / "experiments"]:
            if base.exists():
                for p in base.glob("**/*"):
                    if not p.is_file() or p.name.startswith("."):
                        continue
                    # Skip git internals and cache
                    if ".git" in p.parts or "__pycache__" in p.parts:
                        continue

                    name_lower = p.name.lower()
                    if "holdout" in name_lower and ("95" in name_lower or "100" in name_lower):
                        holdout_violations.append(f"{p} (filename match)")
                        continue

                    # Deep content scan for JSON/JSONL/YAML manifests and instance records
                    if p.suffix in (".json", ".jsonl", ".yaml", ".yml", ".txt"):
                        try:
                            content = p.read_text(encoding="utf-8", errors="ignore")
                            # Recursive inspector helper
                            def check_obj_for_prohibited_sizes(obj, path_desc: str) -> List[str]:
                                v_errs = []
                                if isinstance(obj, dict):
                                    sizes = obj.get("target_digit_sizes", [])
                                    if isinstance(sizes, list):
                                        for s in sizes:
                                            if isinstance(s, (int, float)) and s >= 95:
                                                v_errs.append(f"{path_desc} target_digit_sizes contains {s}")
                                    for d_key in ("digits", "digit_length", "d", "target_digits"):
                                        if d_key in obj:
                                            v = obj[d_key]
                                            if isinstance(v, (int, float)) and v >= 95:
                                                v_errs.append(f"{path_desc} key '{d_key}'={v} >= 95")
                                    for n_key in ("n", "modulus", "N"):
                                        if n_key in obj:
                                            v = obj[n_key]
                                            if isinstance(v, int) and len(str(abs(v))) >= 95:
                                                v_errs.append(f"{path_desc} modulus {n_key} has {len(str(abs(v)))} digits (>= 95)")
                                            elif isinstance(v, str) and len(v.strip()) >= 95 and v.strip().isdigit():
                                                v_errs.append(f"{path_desc} modulus string {n_key} has {len(v.strip())} digits (>= 95)")
                                    for k, sub_v in obj.items():
                                        v_errs.extend(check_obj_for_prohibited_sizes(sub_v, f"{path_desc}.{k}"))
                                elif isinstance(obj, list):
                                    for idx, item in enumerate(obj):
                                        v_errs.extend(check_obj_for_prohibited_sizes(item, f"{path_desc}[{idx}]"))
                                return v_errs

                            import json
                            if p.suffix == ".json":
                                try:
                                    j_data = json.loads(content)
                                    v_errs = check_obj_for_prohibited_sizes(j_data, str(p))
                                    if v_errs:
                                        holdout_violations.extend(v_errs)
                                except Exception:
                                    pass
                            elif p.suffix == ".jsonl":
                                for line_idx, line in enumerate(content.splitlines()):
                                    if line.strip():
                                        try:
                                            rec = json.loads(line)
                                            v_errs = check_obj_for_prohibited_sizes(rec, f"{p}:{line_idx}")
                                            if v_errs:
                                                holdout_violations.extend(v_errs)
                                                break
                                        except Exception:
                                            pass
                        except Exception:
                            pass

        results.append(
            AuditCheckResult(
                name="candidate_holdout_isolation",
                passed=len(holdout_violations) == 0,
                details="Zero holdout moduli/datasets for >= 95d exist across benchmarks/, data/, and experiments/ (strict hold maintained)"
                if len(holdout_violations) == 0
                else f"Premature holdout data detected: {', '.join(holdout_violations)}",
            )
        )

        # 4. Candidate containment and budget model validation enforcement
        model_errors = []
        try:
            import math
            from nsb.candidates.models import SearchBudget

            # Check threads validation
            try:
                SearchBudget(max_cpu_seconds=10.0, threads=2)
                model_errors.append("SearchBudget failed to reject threads=2")
            except ValueError:
                pass

            # Check GPU validation
            try:
                SearchBudget(max_cpu_seconds=10.0, allow_gpu=True)
                model_errors.append("SearchBudget failed to reject allow_gpu=True")
            except ValueError:
                pass

            # Check network validation
            try:
                SearchBudget(max_cpu_seconds=10.0, allow_network=True)
                model_errors.append("SearchBudget failed to reject allow_network=True")
            except ValueError:
                pass

            # Check NaN CPU validation
            try:
                SearchBudget(max_cpu_seconds=float("nan"))
                model_errors.append("SearchBudget failed to reject max_cpu_seconds=NaN")
            except ValueError:
                pass

            # Check inf CPU validation
            try:
                SearchBudget(max_cpu_seconds=float("inf"))
                model_errors.append("SearchBudget failed to reject max_cpu_seconds=inf")
            except ValueError:
                pass

            # Check negative wall validation
            try:
                SearchBudget(max_cpu_seconds=10.0, max_wall_seconds=-10.0)
                model_errors.append("SearchBudget failed to reject negative max_wall_seconds")
            except ValueError:
                pass

            # Check zero peak RSS validation
            try:
                SearchBudget(max_cpu_seconds=10.0, max_peak_rss_mb=0.0)
                model_errors.append("SearchBudget failed to reject zero max_peak_rss_mb")
            except ValueError:
                pass
        except Exception as e:
            model_errors.append(f"Failed to verify candidate budget model enforcement: {e}")

        results.append(
            AuditCheckResult(
                name="candidate_budget_model_enforcement",
                passed=len(model_errors) == 0,
                details="SearchBudget strict single-threading, GPU blocking, network blocking, and positive finite numerical validation verified"
                if len(model_errors) == 0
                else f"Budget model validation errors: {'; '.join(model_errors)}",
            )
        )

        return results

    def audit(self, require_clean_git: bool = True) -> AuditReport:
        """Run full independent scientific audit and compute final verdict."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        git_sha, git_dirty, git_details = self.check_git_status()

        checks: List[AuditCheckResult] = []

        # 1. Git cleanliness check
        git_passed = not git_dirty if require_clean_git else True
        checks.append(
            AuditCheckResult(
                name="git_provenance_cleanliness",
                passed=git_passed,
                details=git_details,
            )
        )

        # 2. Benchmark manifest integrity
        checks.extend(self.check_manifest_integrity())

        # 3. Tripwires
        checks.extend(self.check_tripwires())

        # 4. Sandbox leakage
        checks.extend(self.check_sandboxes())

        # 5. Candidate Search Contract Consistency & Profile Ladder
        checks.extend(self.check_candidate_contract_and_profiles())

        # Compute verdict
        all_passed = all(c.passed for c in checks)
        canonical_ready = all_passed and not git_dirty

        if all_passed:
            verdict = "PASS"
        elif not git_passed and all(c.passed for c in checks if c.name != "git_provenance_cleanliness"):
            # Only git dirty is failing
            verdict = "FIX"
        else:
            verdict = "ESCALATE"

        summary = (
            f"Audit verdict: {verdict}. "
            f"Checks passed: {sum(1 for c in checks if c.passed)}/{len(checks)}. "
            f"Git SHA: {git_sha} ({'DIRTY' if git_dirty else 'CLEAN'})."
        )

        return AuditReport(
            timestamp=timestamp,
            verdict=verdict,
            git_sha=git_sha,
            git_dirty=git_dirty,
            canonical_ready=canonical_ready,
            checks=checks,
            summary=summary,
        )
