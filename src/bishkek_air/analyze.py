"""Simple descriptive statistics: monthly, yearly and heating vs. non-heating season."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

# ASSUMPTION: heating season months. Verify the real dates from an official source
# and change them here (or pass your own set to seasonal_summary).
HEATING_MONTHS: frozenset[int] = frozenset({11, 12, 1, 2, 3})


def _require_columns(df: pd.DataFrame) -> None:
    if not {"timestamp", "pm25"}.issubset(df.columns):
        raise ValueError("DataFrame must have columns 'timestamp' and 'pm25'")


def monthly_means(df: pd.DataFrame) -> pd.DataFrame:
    """Mean PM2.5 and number of observations (n) per calendar month."""
    _require_columns(df)
    if df.empty:
        return pd.DataFrame(columns=["mean", "n"])
    monthly = df.set_index("timestamp")["pm25"].resample("MS").agg(["mean", "count"])
    monthly = monthly.rename(columns={"count": "n"})
    monthly = monthly[monthly["n"] > 0]
    monthly.index.name = "month"
    return monthly


def yearly_means(df: pd.DataFrame) -> pd.DataFrame:
    """Mean PM2.5 and number of observations (n) per calendar year."""
    _require_columns(df)
    if df.empty:
        return pd.DataFrame(columns=["mean", "n"])
    yearly = df.groupby(df["timestamp"].dt.year)["pm25"].agg(["mean", "count"])
    yearly = yearly.rename(columns={"count": "n"})
    yearly.index.name = "year"
    return yearly


def seasonal_summary(
    df: pd.DataFrame, heating_months: Iterable[int] = HEATING_MONTHS
) -> pd.DataFrame:
    """Mean, median and n for the 'heating' and 'non-heating' seasons."""
    _require_columns(df)
    heating = set(heating_months)
    season = df["timestamp"].dt.month.map(lambda m: "heating" if m in heating else "non-heating")
    summary = df.groupby(season)["pm25"].agg(["mean", "median", "count"])
    summary = summary.rename(columns={"count": "n"})
    summary.index.name = "season"
    return summary
