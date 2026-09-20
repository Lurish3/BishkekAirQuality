"""Charts saved as PNG files. Uses the Figure API, so no display is needed."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from matplotlib.figure import Figure


def plot_monthly(monthly: pd.DataFrame, path: str | Path) -> None:
    if monthly.empty:
        raise ValueError("No data to plot")
    fig = Figure(figsize=(10, 4))
    ax = fig.subplots()
    ax.plot(monthly.index, monthly["mean"], marker="o", linewidth=1.2)
    ax.set_title("Monthly mean PM2.5")
    ax.set_xlabel("Month")
    ax.set_ylabel("PM2.5, µg/m³")
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def plot_seasons(summary: pd.DataFrame, path: str | Path) -> None:
    if summary.empty:
        raise ValueError("No data to plot")
    fig = Figure(figsize=(5, 4))
    ax = fig.subplots()
    bars = ax.bar(summary.index, summary["mean"])
    for bar, n in zip(bars, summary["n"], strict=True):
        ax.annotate(
            f"n={int(n)}",
            (bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
        )
    ax.set_title("Mean PM2.5 by season")
    ax.set_ylabel("PM2.5, µg/m³")
    fig.tight_layout()
    fig.savefig(path, dpi=150)

def plot_all_years_monthly(
    monthly: pd.DataFrame,
    path: str | Path,
) -> None:
    """Plot monthly mean PM2.5 across the whole observation period."""
    if monthly.empty:
        raise ValueError("No data to plot")

    dates = pd.to_datetime(
        monthly["year"].astype(str)
        + "-"
        + monthly["month"].astype(str)
        + "-01"
    )

    fig = Figure(figsize=(12, 5))
    ax = fig.subplots()

    ax.plot(
        dates,
        monthly["mean"],
        marker="o",
        linewidth=1.2,
    )

    ax.set_title("Monthly mean PM2.5 in Bishkek")
    ax.set_xlabel("Date")
    ax.set_ylabel("PM2.5, µg/m³")
    ax.grid(alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
