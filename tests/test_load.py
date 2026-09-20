import tempfile
import unittest
from pathlib import Path

from bishkek_air.load import DataFormatError, load_measurements
from helpers import SIMPLE_ROWS, write_csv


class LoadTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_happy_path(self):
        path = write_csv(self.dir / "a.csv", SIMPLE_ROWS)
        df = load_measurements(path, timestamp_col="ts", value_col="value")
        self.assertEqual(list(df.columns), ["timestamp", "pm25"])
        self.assertEqual(len(df), 5)
        self.assertEqual(df["pm25"].iloc[0], 100.0)

    def test_explicit_timestamp_format(self):
        path = write_csv(self.dir / "a.csv", [("05.03.2023 14:00", "7"), ("bad", "8")])
        df = load_measurements(
            path, timestamp_col="ts", value_col="value", timestamp_format="%d.%m.%Y %H:%M"
        )
        self.assertEqual(df["timestamp"].iloc[0].month, 3)
        self.assertTrue(df["timestamp"].isna().iloc[1])

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_measurements(self.dir / "nope.csv", timestamp_col="ts", value_col="value")

    def test_missing_column_lists_available(self):
        path = write_csv(self.dir / "a.csv", SIMPLE_ROWS)
        with self.assertRaises(DataFormatError) as ctx:
            load_measurements(path, timestamp_col="ts", value_col="wrong")
        self.assertIn("wrong", str(ctx.exception))
        self.assertIn("Available columns", str(ctx.exception))

    def test_unparseable_values_become_missing_not_errors(self):
        path = write_csv(self.dir / "a.csv", [("not a date", "5"), ("2023-01-01", "abc")])
        df = load_measurements(path, timestamp_col="ts", value_col="value")
        self.assertTrue(df["timestamp"].isna().iloc[0])
        self.assertTrue(df["pm25"].isna().iloc[1])

    def test_empty_file(self):
        path = self.dir / "empty.csv"
        path.write_text("", encoding="utf-8")
        with self.assertRaises(DataFormatError):
            load_measurements(path, timestamp_col="ts", value_col="value")


if __name__ == "__main__":
    unittest.main()
