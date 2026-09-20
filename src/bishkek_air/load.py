"""Reading a CSV file into a tidy table."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class DataFormatError(ValueError):
    """The input file does not look like the expected measurement data."""


def load_measurements(
    path: str | Path,
    *,
    timestamp_col: str,
    value_col: str,
    qc_col: str | None = None,
    sep: str = ",",
    timestamp_format: str | None = None,
) -> pd.DataFrame:
    """Load a CSV and return timestamp, pm25 and optional QC columns."""
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"Data file not found: {path}")

    try:
        raw = pd.read_csv(path, sep=sep)
    except (
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
        UnicodeDecodeError,
    ) as exc:
        raise DataFormatError(f"Cannot read {path} as CSV: {exc}") from exc

    required_columns = [timestamp_col, value_col]

    if qc_col is not None:
        required_columns.append(qc_col)

    missing = [col for col in required_columns if col not in raw.columns]

    if missing:
        raise DataFormatError(
            f"Columns not found: {missing}. "
            f"Available columns: {list(raw.columns)}"
        )

    if timestamp_format is not None:
        timestamp = pd.to_datetime(
            raw[timestamp_col],
            format=timestamp_format,
            errors="coerce",
        )
    else:
        timestamp = pd.to_datetime(
            raw[timestamp_col],
            errors="coerce",
        )

    out = pd.DataFrame(
        {
            "timestamp": timestamp,
            "pm25": pd.to_numeric(
                raw[value_col],
                errors="coerce",
            ),
        }
    )

    if qc_col is not None:
        out["qc"] = raw[qc_col]

    return out
