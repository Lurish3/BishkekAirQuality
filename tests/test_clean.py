import unittest

import pandas as pd

from bishkek_air.clean import clean_measurements


def make_df(rows):
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [r[0] for r in rows],
                errors="coerce",
            ),
            "pm25": [r[1] for r in rows],
        }
    )


class CleanTests(unittest.TestCase):
    def test_removes_each_kind_of_bad_row_and_counts_it(self):
        df = make_df(
            [
                ("2023-01-01 03:00", 30.0),
                ("2023-01-01 01:00", 10.0),
                ("2023-01-01 02:00", -999.0),
                ("2023-01-01 04:00", -5.0),
                ("2023-01-01 05:00", 5000.0),
                ("2023-01-01 01:00", 99.0),
                (None, 12.0),
                ("2023-01-01 06:00", float("nan")),
            ]
        )

        cleaned, report = clean_measurements(df)

        self.assertEqual(report.rows_in, 8)
        self.assertEqual(report.dropped_missing, 2)
        self.assertEqual(report.dropped_invalid_marker, 1)
        self.assertEqual(report.dropped_out_of_range, 2)
        self.assertEqual(report.dropped_duplicate_timestamps, 1)
        self.assertEqual(report.rows_out, 2)

        self.assertEqual(
            list(cleaned["pm25"]),
            [10.0, 30.0],
        )

    def test_counts_add_up(self):
        df = make_df(
            [
                ("2023-01-01", 1.0),
                ("2023-01-02", -999.0),
                ("2023-01-03", 2.0),
            ]
        )

        _, report = clean_measurements(df)

        dropped = (
            report.dropped_missing
            + report.dropped_invalid_marker
            + report.dropped_out_of_range
            + report.dropped_duplicate_timestamps
        )

        self.assertEqual(
            report.rows_in - dropped,
            report.rows_out,
        )

    def test_custom_marker(self):
        df = make_df(
            [
                ("2023-01-01", 1.0),
                ("2023-01-02", 0.0),
            ]
        )

        cleaned, report = clean_measurements(
            df,
            invalid_values=(0.0,),
        )

        self.assertEqual(
            report.dropped_invalid_marker,
            1,
        )

        self.assertEqual(len(cleaned), 1)

    def test_requires_columns(self):
        with self.assertRaises(ValueError):
            clean_measurements(
                pd.DataFrame({"a": [1]})
            )

    def test_empty_input(self):
        cleaned, report = clean_measurements(
            make_df([])
        )

        self.assertTrue(cleaned.empty)
        self.assertEqual(
            report.rows_out,
            0,
        )

    def test_removes_invalid_qc(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    [
                        "2023-01-01 01:00",
                        "2023-01-01 02:00",
                        "2023-01-01 03:00",
                    ]
                ),
                "pm25": [10.0, 20.0, 30.0],
                "qc": ["Valid", "Invalid", "Valid"],
            }
        )

        cleaned, report = clean_measurements(df)

        self.assertEqual(
            report.dropped_invalid_qc,
            1,
        )

        self.assertEqual(
            report.rows_out,
            2,
        )

        self.assertEqual(
            list(cleaned["pm25"]),
            [10.0, 30.0],
        )


if __name__ == "__main__":
    unittest.main()
