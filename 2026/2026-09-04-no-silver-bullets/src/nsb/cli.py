"""NSB Command Line Interface."""

import argparse
from pathlib import Path
import sys
import yaml
from nsb import __version__
from nsb.benchmarks.corpus import create_corpus_split
from nsb.core.config import load_config
from nsb.pilots.engine import run_pilot_suite
from nsb.smoke import run_smoke_suite


def main() -> int:
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--config",
        type=str,
        default="config/defaults.yaml",
        help="Path to configuration file",
    )

    parser = argparse.ArgumentParser(
        prog="nsb",
        parents=[parent_parser],
        description="No Silver Bullet: Classical Integer Factorization Experimental Laboratory",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Laboratory commands")

    # info command
    subparsers.add_parser("info", parents=[parent_parser], help="Display laboratory contract and environment info")

    # generate-corpus command
    gen_parser = subparsers.add_parser(
        "generate-corpus", parents=[parent_parser], help="Generate public instances and sealed ground truth"
    )
    gen_parser.add_argument("--split", type=str, default="smoke", help="Dataset split (e.g., dev, val, holdout, smoke)")
    gen_parser.add_argument("--seed", type=int, default=None, help="Master RNG seed override")
    gen_parser.add_argument("--output-dir", type=str, default=".", help="Root directory for output benchmarks")

    # smoke command
    smoke_parser = subparsers.add_parser("smoke", parents=[parent_parser], help="Execute smoke test and canary suite")
    smoke_parser.add_argument("--allow-dirty", action="store_true", help="Allow running on dirty git working tree (non-canonical)")

    # pilot command
    pilot_parser = subparsers.add_parser("pilot", parents=[parent_parser], help="Execute Gate 1 pilot suite")
    pilot_parser.add_argument("--allow-dirty", action="store_true", help="Allow running on dirty git working tree (non-canonical)")

    # wave1 command
    wave1_parser = subparsers.add_parser("wave1", parents=[parent_parser], help="Execute R1 Wave 1 research suite")
    wave1_parser.add_argument("--allow-dirty", action="store_true", help="Allow running on dirty git working tree (non-canonical)")

    args = parser.parse_args()

    if args.command is None or args.command == "info":
        try:
            config, chash = load_config(args.config)
            print(f"No Silver Bullet v{__version__}")
            print(f"Contract: {config.contract_id}")
            print(f"Config Hash: {chash[:16]}...")
            print(f"Database: {config.storage.database_path}")
            return 0
        except Exception as e:
            print(f"Error loading configuration: {e}", file=sys.stderr)
            return 1

    elif args.command == "generate-corpus":
        try:
            config_path = Path(args.config)
            with open(config_path, "r", encoding="utf-8") as f:
                raw_cfg = yaml.safe_load(f) or {}

            benchmark_version = raw_cfg.get("benchmark_version", "v001_smoke")
            gen_cfg = raw_cfg.get("benchmark_generation", {})
            seed = args.seed if args.seed is not None else gen_cfg.get("seed", 42)
            instances_spec = gen_cfg.get("instances", [
                {"family": "R", "bit_sizes": [32, 40, 48], "count_per_size": 2},
                {"family": "F", "bit_sizes": [48], "count_per_size": 1},
                {"family": "P1", "bit_sizes": [48], "count_per_size": 1},
                {"family": "C", "bit_sizes": [48], "count_per_size": 1},
                {"family": "E", "bit_sizes": [16, 24], "count_per_size": 1},
            ])

            print(f"Generating corpus version '{benchmark_version}' split '{args.split}' with seed {seed}...")
            manifest = create_corpus_split(
                output_base_dir=args.output_dir,
                version=benchmark_version,
                split=args.split,
                spec=instances_spec,
                master_seed=seed,
            )
            print(f"Success: Generated {manifest['total_instances']} instances.")
            print(f"Public file: {manifest['public_file']} (SHA-256: {manifest['public_sha256'][:16]}...)")
            print(f"Sealed file: {manifest['sealed_file']} (SHA-256: {manifest['sealed_sha256'][:16]}...)")
            return 0
        except Exception as e:
            print(f"Error generating corpus: {e}", file=sys.stderr)
            return 1

    elif args.command == "smoke":
        success = run_smoke_suite(config_path=args.config, allow_dirty=args.allow_dirty)
        return 0 if success else 1

    elif args.command == "pilot":
        cfg = "config/pilot.yaml" if args.config == "config/defaults.yaml" else args.config
        success = run_pilot_suite(config_path=cfg, allow_dirty=args.allow_dirty)
        return 0 if success else 1

    elif args.command == "wave1":
        from nsb.experiments.wave1_runner import run_wave1_suite
        cfg = "config/wave1.yaml" if args.config == "config/defaults.yaml" else args.config
        success = run_wave1_suite(config_path=cfg, allow_dirty=args.allow_dirty)
        return 0 if success else 1


    return 0


if __name__ == "__main__":
    sys.exit(main())
