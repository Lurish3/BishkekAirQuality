import unittest

import pandas as pd

from bishkek_air.analyze import (
    completeness_summary,
    monthly_means,
    seasonal_summary,
    yearly_means,
)


def sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2023-01-01",
                    "2023-01-15",
                    "2023-01-31",
                    "2023-07-01",
                    "2023-07-15",
                    "2024-02-01",
                ]
            ),
            "pm25": [100.0, 100.0, 100.0, 20.0, 40.0, 60.0],
        }
    )


class AnalyzeTests(unittest.TestCase):
    def test_monthly_means(self):
        m = monthly_means(sample())

        self.assertEqual(len(m), 3)
        self.assertEqual(
            m.loc[pd.Timestamp("2023-01-01"), "mean"],
            100.0,
        )
        self.assertEqual(
            m.loc[pd.Timestamp("2023-07-01"), "mean"],
            30.0,
        )
        self.assertEqual(
            m.loc[pd.Timestamp("2023-07-01"), "n"],
            2,
        )

    def test_yearly_means(self):
        y = yearly_means(sample())

        self.assertAlmostEqual(
            y.loc[2023, "mean"],
            72.0,
        )
        self.assertEqual(
            y.loc[2024, "n"],
            1,
        )

    def test_seasonal_summary_default_heating_months(self):
        s = seasonal_summary(sample())

        self.assertAlmostEqual(
            s.loc["heating", "mean"],
            (100 * 3 + 60) / 4,
        )
        self.assertEqual(
            s.loc["non-heating", "n"],
            2,
        )
        self.assertEqual(
            s.loc["non-heating", "median"],
            30.0,
        )

    def test_custom_heating_months(self):
        s = seasonal_summary(
            sample(),
            heating_months={7},
        )

        self.assertEqual(
            s.loc["heating", "n"],
            2,
        )

    def test_single_season_only(self):
        df = sample().iloc[:3]
        s = seasonal_summary(df)

        self.assertEqual(
            list(s.index),
            ["heating"],
        )

    def test_empty(self):
        empty = pd.DataFrame(
            {
                "timestamp": pd.to_datetime([]),
                "pm25": [],
            }
        )

        self.assertTrue(
            monthly_means(empty).empty
        )
        self.assertTrue(
            yearly_means(empty).empty
        )

    def test_requires_columns(self):
        with self.assertRaises(ValueError):
            monthly_means(
                pd.DataFrame({"a": [1]})
            )

    def test_completeness_full_range(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    [
                        "2023-01-01 00:00",
                        "2023-01-01 01:00",
                        "2023-01-01 02:00",
                    ]
                ),
                "pm25": [10.0, 20.0, 30.0],
            }
        )

        result = completeness_summary(
            df,
            start=pd.Timestamp("2023-01-01 00:00"),
            end=pd.Timestamp("2023-01-01 02:00"),
        )

        self.assertEqual(
            result["expected_observations"],
            3,
        )
        self.assertEqual(
            result["observed_observations"],
            3,
        )
        self.assertEqual(
            result["missing_observations"],
            0,
        )
        self.assertEqual(
            result["coverage_percent"],
            100.0,
        )

    def test_completeness_detects_missing_timestamp(self):
        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    [
                        "2023-01-01 00:00",
                        "2023-01-01 02:00",
                    ]
                ),
                "pm25": [10.0, 30.0],
            }
        )

        result = completeness_summary(
            df,
            start=pd.Timestamp("2023-01-01 00:00"),
            end=pd.Timestamp("2023-01-01 02:00"),
        )

        self.assertEqual(
            result["expected_observations"],
            3,
        )
        self.assertEqual(
            result["observed_observations"],
            2,
        )
        self.assertEqual(
            result["missing_observations"],
            1,
        )
        self.assertAlmostEqual(
            result["coverage_percent"],
            66.67,
            places=2,
        )

    def test_completeness_empty_dataframe(self):
        empty = pd.DataFrame(
            {
                "timestamp": pd.to_datetime([]),
                "pm25": [],
            }
        )

        result = completeness_summary(
            empty,
            start=pd.Timestamp("2023-01-01 00:00"),
            end=pd.Timestamp("2023-01-01 02:00"),
        )

        self.assertEqual(
            result["expected_observations"],
            3,
        )
        self.assertEqual(
            result["observed_observations"],
            0,
        )
        self.assertEqual(
            result["missing_observations"],
            3,
        )
        self.assertEqual(
            result["coverage_percent"],
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
