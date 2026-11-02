"""Automated test suite for Step 0 of the KCMO Homicide Research Project."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.checks import (
    run_step0_completion_checks,
    run_step1_pilot_checks,
    run_synthetic_multi_entity_fixture,
)
from src.cli import DEFAULT_DB, DEFAULT_EXPORTS_DIR, DEFAULT_QUEUE_CSV, DEFAULT_WORKBOOK, main as cli_main
from src.importer import extract_firearm_flag


class TestStep0Foundation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not DEFAULT_DB.exists():
            cli_main(["--rebuild", "--skip-checks"])

    def test_all_step0_completion_checks_pass(self) -> None:
        results = run_step0_completion_checks(
            workbook_path=DEFAULT_WORKBOOK,
            db_path=DEFAULT_DB,
            queue_csv_path=DEFAULT_QUEUE_CSV,
        )
        self.assertTrue(results["all_passed"], msg=f"Checks failed: {results}")

    def test_all_step1_pilot_checks_pass(self) -> None:
        results = run_step1_pilot_checks(
            db_path=DEFAULT_DB,
            exports_dir=DEFAULT_EXPORTS_DIR,
        )
        self.assertTrue(results["all_passed"], msg=f"Step 1 checks failed: {results}")

    def test_synthetic_multi_entity_fixture(self) -> None:
        fixture = run_synthetic_multi_entity_fixture()
        self.assertTrue(fixture["passed"])
        self.assertEqual(fixture["incident_count"], 1)
        self.assertEqual(fixture["victim_count"], 2)
        self.assertEqual(fixture["unnamed_victim_count"], 1)
        self.assertEqual(fixture["defendant_count"], 2)
        self.assertEqual(fixture["convicted_defendants"], 1)
        self.assertEqual(fixture["acquitted_defendants"], 1)
        self.assertEqual(fixture["total_charge_counts"], 4)

    def test_false_vs_missing_firearm_flag_distinct(self) -> None:
        raw_false, bool_false, field_false = extract_firearm_flag({"fire_arm_used_flag": False})
        self.assertEqual(raw_false, "false")
        self.assertEqual(bool_false, 0)
        self.assertEqual(field_false, "fire_arm_used_flag")

        raw_null, bool_null, field_null = extract_firearm_flag({"firearm_used_flag": None})
        self.assertIsNone(raw_null)
        self.assertIsNone(bool_null)
        self.assertEqual(field_null, "firearm_used_flag")

        raw_missing, bool_missing, field_missing = extract_firearm_flag({})
        self.assertIsNone(raw_missing)
        self.assertIsNone(bool_missing)
        self.assertIsNone(field_missing)


if __name__ == "__main__":
    unittest.main()
