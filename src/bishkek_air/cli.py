"""Command line entry point: CSV in, tables and charts out."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from .analyze import (
    completeness_summary,
    monthly_means,
    seasonal_summary,
    yearly_means,
)
from .clean import (
    DEFAULT_INVALID_VALUES,
    DEFAULT_MAX_VALUE,
    DEFAULT_VALID_QC,
    clean_measurements,
)
from .load import DataFormatError, load_measurements
from .plots import plot_monthly, plot_seasons


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bishkek-air",
        description="Monthly and seasonal PM2.5 statistics from a CSV file.",
    )

    parser.add_argument(
        "csv",
        help="path to the CSV file",
    )
    parser.add_argument(
        "--timestamp-col",
        required=True,
        help="name of the date/time column",
    )
    parser.add_argument(
        "--value-col",
        required=True,
        help="name of the PM2.5 column",
    )
    parser.add_argument(
        "--qc-col",
        default=None,
        help="optional quality-control column, e.g. 'QC Name'",
    )
    parser.add_argument(
        "--qc-valid",
        default=DEFAULT_VALID_QC,
        help="QC value considered valid (default: Valid)",
    )
    parser.add_argument(
        "--timestamp-format",
        default=None,
        help=(
            'optional date format, e.g. '
            '"%%Y-%%m-%%d %%I:%%M %%p" '
            "(default: detect automatically)"
        ),
    )
    parser.add_argument(
        "--sep",
        default=",",
        help="CSV separator (default: ,)",
    )
    parser.add_argument(
        "--out",
        default="output",
        help="output directory (default: output)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="keep only measurements from this calendar year",
    )
    parser.add_argument(
        "--invalid",
        type=float,
        nargs="*",
        default=list(DEFAULT_INVALID_VALUES),
        help="values that mean 'no data' (default: -999)",
    )
    parser.add_argument(
        "--max-value",
        type=float,
        default=DEFAULT_MAX_VALUE,
        help="values above this are treated as errors (default: 1000)",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        raw = load_measurements(
            args.csv,
            timestamp_col=args.timestamp_col,
            value_col=args.value_col,
            qc_col=args.qc_col,
            sep=args.sep,
            timestamp_format=args.timestamp_format,
        )

        if args.year is not None:
            raw = raw[
                raw["timestamp"].dt.year == args.year
            ].copy()

            if raw.empty:
                raise DataFormatError(
                    f"No rows found for year {args.year}"
                )

        cleaned, report = clean_measurements(
            raw,
            invalid_values=tuple(args.invalid),
            max_value=args.max_value,
            valid_qc=args.qc_valid,
        )

        if cleaned.empty:
            raise DataFormatError(
                "No valid rows left after cleaning"
            )

    except (FileNotFoundError, DataFormatError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    monthly = monthly_means(cleaned)
    yearly = yearly_means(cleaned)
    seasons = seasonal_summary(cleaned)

    monthly.to_csv(out / "monthly_means.csv")
    yearly.to_csv(out / "yearly_means.csv")
    seasons.to_csv(out / "seasonal_summary.csv")

    if args.year is not None:
        completeness = completeness_summary(
            cleaned,
            start=pd.Timestamp(
                year=args.year,
                month=1,
                day=1,
            ),
            end=pd.Timestamp(
                year=args.year,
                month=12,
                day=31,
                hour=23,
            ),
        )
    else:
        completeness = completeness_summary(cleaned)

    input_path = Path(args.csv)
    input_sha256 = hashlib.sha256(
        input_path.read_bytes()
    ).hexdigest()

    report_data = asdict(report)

    report_data.update(
        {
            "input_file": str(input_path),
            "input_sha256": input_sha256,
            "year": args.year,
            "timestamp_col": args.timestamp_col,
            "value_col": args.value_col,
            "qc_col": args.qc_col,
            "qc_valid": args.qc_valid,
            "timestamp_format": args.timestamp_format,
            "separator": args.sep,
            "invalid_values": args.invalid,
            "max_value": args.max_value,
            "python_version": platform.python_version(),
            "pandas_version": version("pandas"),
            "matplotlib_version": version("matplotlib"),
            "project_version": version("bishkek-air-quality"),
            "completeness": completeness,
        }
    )

    (out / "cleaning_report.json").write_text(
        json.dumps(
            report_data,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    plot_monthly(
        monthly,
        out / "monthly_means.png",
    )

    plot_seasons(
        seasons,
        out / "seasonal_summary.png",
    )

    print(
        f"Rows read: {report.rows_in}, "
        f"kept: {report.rows_out}"
    )
    print(
        f"Results written to: {out.resolve()}"
    )

    return 0
