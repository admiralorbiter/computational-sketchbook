#!/usr/bin/env python3
"""Environment verification and diagnostic utility for CADO-NFS integration.

Validates:
1. Lockfile configuration (config/external/cado_nfs.lock.yaml).
2. Git commit integrity in CADO source tree.
3. Binary executability and SHA-256 fingerprinting.
4. Execution platform (Linux native vs WSL2 bridge vs Windows host).
"""

import argparse
import json
from pathlib import Path
import sys

from nsb.baselines.cado_nfs.environment import CadoEnvironment


def main():
    parser = argparse.ArgumentParser(description="Verify CADO-NFS environment and lockfile.")
    parser.add_argument(
        "--cado-root",
        type=str,
        default=None,
        help="Path to CADO-NFS repository root",
    )
    parser.add_argument(
        "--lockfile",
        type=str,
        default="config/external/cado_nfs.lock.yaml",
        help="Path to lockfile",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON fingerprint",
    )
    args = parser.parse_args()

    env = CadoEnvironment(cado_root=args.cado_root, lockfile_path=args.lockfile)
    fp = env.fingerprint()

    if args.json:
        print(json.dumps(fp, indent=2))
        return

    print("=" * 65)
    print(" CADO-NFS Environment & Dependency Diagnostic")
    print("=" * 65)
    print(f"Platform:              {fp['platform']} ({fp['cpu_architecture']}, {fp['cpu_count']} cores)")
    print(f"CPU Model:             {fp.get('cpu_model', 'N/A')}")
    ram = fp.get("ram", {})
    print(f"RAM (Total / Avail):   {ram.get('total_mb', 0)} MB / {ram.get('available_mb', 0)} MB")
    print(f"Native Linux:          {'YES' if fp['is_linux'] else 'NO'}")
    print(f"Windows Host:          {'YES' if fp['is_windows'] else 'NO'}")
    if fp["is_windows"]:
        print(f"WSL Available:         {'YES' if fp.get('has_wsl') else 'NO'}")
    print(f"CADO Root Directory:   {fp['cado_root']}")
    print(f"CADO Root Exists:      {'YES' if fp['cado_root_exists'] else 'NO'}")

    pinned = fp["pinned_git_commit"]
    detected = fp["detected_git_commit"]
    print(f"Pinned Commit:         {pinned}")
    print(f"Detected Commit:       {detected or 'NOT FOUND'}")

    commit_match = bool(detected and pinned and detected == pinned)
    print(f"Commit Exact Match:    {'YES' if commit_match else 'NO'}")
    print(f"Working Tree Clean:    {'YES' if fp.get('is_git_clean') else 'NO'}")
    
    tc = fp.get("toolchain", {})
    print(f"Compiler (gcc):        {tc.get('gcc', 'N/A')}")
    print(f"Build (cmake):         {tc.get('cmake', 'N/A')}")
    print(f"VCS (git):             {tc.get('git', 'N/A')}")
    print("-" * 65)
    print("Canonical Discrete Binaries:")
    for b_name in ["polyselect", "polyselect_ropt", "score", "makefb", "las", "check_rels"]:
        b_info = fp["binary_hashes"].get(b_name)
        if b_info:
            sha_short = b_info["sha256"][:16] + "..."
            print(f"  [FOUND] {b_name:<16} -> {sha_short} ({b_info['path']})")
        else:
            print(f"  [MISSING] {b_name:<16}")

    print("-" * 65)
    valid, msg = env.validate_for_canonical_execution()
    if valid:
        print(f"STATUS: PASS - {msg}")
        sys.exit(0)
    else:
        print(f"STATUS: FAIL/HOLD - {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
