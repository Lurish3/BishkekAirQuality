"""Descriptive statistics and data completeness analysis."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

HEATING_MONTHS: frozenset[int] = frozenset({11, 12, 1, 2, 3})


def _require_columns(df: pd.DataFrame) -> None:
    if not {"timestamp", "pm25"}.issubset(df.columns):
        raise ValueError(
            "DataFrame must have columns 'timestamp' and 'pm25'"
        )


def monthly_means(df: pd.DataFrame) -> pd.DataFrame:
    """Mean PM2.5 and number of observations (n) per calendar month."""
    _require_columns(df)

    if df.empty:
        return pd.DataFrame(columns=["mean", "n"])

    monthly = (
        df.set_index("timestamp")["pm25"]
        .resample("MS")
        .agg(["mean", "count"])
    )

    monthly = monthly.rename(columns={"count": "n"})
    monthly = monthly[monthly["n"] > 0]
    monthly.index.name = "month"

    return monthly


def yearly_means(df: pd.DataFrame) -> pd.DataFrame:
    """Descriptive PM2.5 statistics for each calendar year."""
    _require_columns(df)

    if df.empty:
        return pd.DataFrame(
            columns=[
                "mean",
                "std",
                "min",
                "q1",
                "median",
                "q3",
                "max",
                "n",
            ]
        )

    yearly = (
        df.groupby(df["timestamp"].dt.year)["pm25"]
        .agg(
            mean="mean",
            std="std",
            min="min",
            q1=lambda values: values.quantile(0.25),
            median="median",
            q3=lambda values: values.quantile(0.75),
            max="max",
            n="count",
        )
    )

    yearly.index.name = "year"

    return yearly


def seasonal_summary(
    df: pd.DataFrame,
    heating_months: Iterable[int] = HEATING_MONTHS,
) -> pd.DataFrame:
    """Descriptive PM2.5 statistics for heating and non-heating seasons."""
    _require_columns(df)

    heating = set(heating_months)

    season = df["timestamp"].dt.month.map(
        lambda month: (
            "heating"
            if month in heating
            else "non-heating"
        )
    )

    summary = (
        df.assign(season=season)
        .groupby("season")["pm25"]
        .agg(
            mean="mean",
            std="std",
            min="min",
            q1=lambda values: values.quantile(0.25),
            median="median",
            q3=lambda values: values.quantile(0.75),
            max="max",
            n="count",
        )
    )

    summary.index.name = "season"

    return summary


def completeness_summary(
    df: pd.DataFrame,
    *,
    start: pd.Timestamp | None = None,
    end: pd.Timestamp | None = None,
    frequency: str = "h",
) -> dict[str, object]:
    """Calculate temporal coverage for an expected regular time range."""
    _require_columns(df)

    if start is None or end is None:
        if df.empty:
            return {
                "first_timestamp": None,
                "last_timestamp": None,
                "expected_observations": 0,
                "observed_observations": 0,
                "missing_observations": 0,
                "coverage_percent": 0.0,
            }

        start = df["timestamp"].min().floor(frequency)
        end = df["timestamp"].max().floor(frequency)

    expected_index = pd.date_range(
        start=start,
        end=end,
        freq=frequency,
    )

    observed_index = pd.DatetimeIndex(
        df["timestamp"]
    ).floor(frequency).unique()

    observed_index = observed_index[
        (observed_index >= start)
        & (observed_index <= end)
    ]

    expected_observations = len(expected_index)
    observed_observations = len(observed_index)
    missing_observations = max(
        expected_observations - observed_observations,
        0,
    )

    if expected_observations:
        coverage_percent = (
            observed_observations
            / expected_observations
            * 100
        )
    else:
        coverage_percent = 0.0

    return {
        "first_timestamp": start.isoformat(),
        "last_timestamp": end.isoformat(),
        "expected_observations": expected_observations,
        "observed_observations": observed_observations,
        "missing_observations": missing_observations,
        "coverage_percent": round(coverage_percent, 2),
    }
