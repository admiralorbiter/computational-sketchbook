"""Command-line interface for Step 0 of the KCMO Homicide Research Project."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .checks import run_step0_completion_checks, run_step1_pilot_checks
from .exporter import export_research_queue
from .importer import import_starter_workbook
from .pilot_merge import merge_and_export_pilot

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WORKBOOK = PROJECT_ROOT / "input" / "Kansas_City_Homicide_Project_Starter.xlsx"
DEFAULT_DB = PROJECT_ROOT / "data" / "kcmo_homicide.sqlite"
DEFAULT_RESEARCH_BACKUP = PROJECT_ROOT / "data" / "research" / "reviewed_bundle.json"
DEFAULT_PILOT_DIR = PROJECT_ROOT / "data" / "research" / "pilot_batch_1"
DEFAULT_EXPORTS_DIR = PROJECT_ROOT / "exports"
DEFAULT_QUEUE_CSV = DEFAULT_EXPORTS_DIR / "2020_research_queue.csv"
DEFAULT_QUEUE_JSONL = DEFAULT_EXPORTS_DIR / "2020_research_queue.jsonl"
DEFAULT_AUDIT_JSON = DEFAULT_EXPORTS_DIR / "step0_audit_summary.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="KCMO Homicide Research Project — Step 0 Reproducible Import & Queue Exporter"
    )
    parser.add_argument(
        "--workbook",
        type=Path,
        default=DEFAULT_WORKBOOK,
        help="Path to immutable Kansas_City_Homicide_Project_Starter.xlsx",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Path to SQLite database file",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Drop and recreate import tables while preserving any reviewed research state",
    )
    parser.add_argument(
        "--export-year",
        type=int,
        default=2020,
        help="Dataset year to export to the research queue (default: 2020)",
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip running Step 0 completion checks after import and export",
    )
    args = parser.parse_args(argv)

    import_summary = import_starter_workbook(
        workbook_path=args.workbook,
        db_path=args.db,
        rebuild=args.rebuild,
        research_backup_path=DEFAULT_RESEARCH_BACKUP,
    )

    export_summary = export_research_queue(
        db_path=args.db,
        csv_path=DEFAULT_QUEUE_CSV,
        jsonl_path=DEFAULT_QUEUE_JSONL,
        dataset_year=args.export_year,
    )

    pilot_merge_summary = {}
    if (DEFAULT_PILOT_DIR / "verifier_review.jsonl").exists():
        pilot_merge_summary = merge_and_export_pilot(
            db_path=args.db,
            pilot_dir=DEFAULT_PILOT_DIR,
            exports_dir=DEFAULT_EXPORTS_DIR,
            research_backup_path=DEFAULT_RESEARCH_BACKUP,
        )
        export_summary = export_research_queue(
            db_path=args.db,
            csv_path=DEFAULT_QUEUE_CSV,
            jsonl_path=DEFAULT_QUEUE_JSONL,
            dataset_year=args.export_year,
        )

    checks_summary = {}
    step1_checks_summary = {}
    if not args.skip_checks:
        checks_summary = run_step0_completion_checks(
            workbook_path=args.workbook,
            db_path=args.db,
            queue_csv_path=DEFAULT_QUEUE_CSV,
        )
        if pilot_merge_summary:
            step1_checks_summary = run_step1_pilot_checks(
                db_path=args.db,
                exports_dir=DEFAULT_EXPORTS_DIR,
            )

    full_report = {
        "import_summary": import_summary,
        "export_summary": export_summary,
        "pilot_merge_summary": pilot_merge_summary,
        "completion_checks": checks_summary,
        "step1_pilot_checks": step1_checks_summary,
    }

    DEFAULT_AUDIT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_AUDIT_JSON.write_text(json.dumps(full_report, indent=2), encoding="utf-8")

    print(json.dumps(full_report, indent=2))
    if checks_summary and not checks_summary.get("all_passed", False):
        return 1
    if step1_checks_summary and not step1_checks_summary.get("all_passed", False):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
