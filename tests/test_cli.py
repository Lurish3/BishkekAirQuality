import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from bishkek_air.cli import main
from helpers import SIMPLE_ROWS, write_csv


class CliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def run_cli(self, *args):
        err = io.StringIO()

        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(err),
        ):
            code = main([str(a) for a in args])

        return code, err.getvalue()

    def test_end_to_end(self):
        rows = SIMPLE_ROWS + [
            ("2023-07-20 00:00", "-999"),
            ("2023-07-21 00:00", "abc"),
        ]

        csv = write_csv(self.dir / "in.csv", rows)
        out = self.dir / "out"

        code, _ = self.run_cli(
            csv,
            "--timestamp-col",
            "ts",
            "--value-col",
            "value",
            "--out",
            out,
        )

        self.assertEqual(code, 0)

        for name in (
            "monthly_means.csv",
            "yearly_means.csv",
            "seasonal_summary.csv",
            "cleaning_report.json",
            "monthly_means.png",
            "seasonal_summary.png",
        ):
            self.assertTrue((out / name).is_file(), name)

        monthly = pd.read_csv(
            out / "monthly_means.csv",
            index_col="month",
        )

        self.assertEqual(
            monthly.loc["2023-01-01", "mean"],
            100.0,
        )
        self.assertEqual(
            monthly.loc["2023-07-01", "mean"],
            20.0,
        )

        report = json.loads(
            (out / "cleaning_report.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(report["rows_in"], 7)
        self.assertEqual(report["rows_out"], 5)

    def test_year_completeness_uses_available_period(self):
        rows = [
            ("2024-01-01 01:00", "10"),
            ("2024-01-01 02:00", "20"),
            ("2024-06-30 23:00", "30"),
        ]

        csv = write_csv(self.dir / "in.csv", rows)
        out = self.dir / "out"

        code, _ = self.run_cli(
            csv,
            "--timestamp-col",
            "ts",
            "--value-col",
            "value",
            "--year",
            "2024",
            "--out",
            out,
        )

        self.assertEqual(code, 0)

        report = json.loads(
            (out / "cleaning_report.json").read_text(
                encoding="utf-8"
            )
        )

        completeness = report["completeness"]

        self.assertEqual(
            completeness["first_timestamp"],
            "2024-01-01T01:00:00",
        )
        self.assertEqual(
            completeness["last_timestamp"],
            "2024-06-30T23:00:00",
        )
        self.assertEqual(
            completeness["expected_observations"],
            4367,
        )
        self.assertEqual(
            completeness["observed_observations"],
            3,
        )

    def test_missing_file_returns_2(self):
        code, err = self.run_cli(
            self.dir / "nope.csv",
            "--timestamp-col",
            "ts",
            "--value-col",
            "value",
        )

        self.assertEqual(code, 2)
        self.assertIn("not found", err)

    def test_wrong_column_returns_2(self):
        csv = write_csv(self.dir / "in.csv", SIMPLE_ROWS)

        code, err = self.run_cli(
            csv,
            "--timestamp-col",
            "ts",
            "--value-col",
            "oops",
        )

        self.assertEqual(code, 2)
        self.assertIn("oops", err)

    def test_nothing_valid_returns_2(self):
        csv = write_csv(
            self.dir / "in.csv",
            [
                ("2023-01-01", "-999"),
                ("2023-01-02", "-999"),
            ],
        )

        code, err = self.run_cli(
            csv,
            "--timestamp-col",
            "ts",
            "--value-col",
            "value",
        )

        self.assertEqual(code, 2)
        self.assertIn("No valid rows", err)


if __name__ == "__main__":
    unittest.main()
