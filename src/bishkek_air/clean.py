from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

DEFAULT_INVALID_VALUES: tuple[float, ...] = (-999.0,)
DEFAULT_MAX_VALUE: float = 1000.0
DEFAULT_VALID_QC: str = "Valid"

@dataclass(frozen=True)
class CleaningReport:
    rows_in: int
    dropped_missing: int
    dropped_invalid_marker: int
    dropped_invalid_qc: int
    dropped_negative: int
    dropped_above_max: int
    dropped_duplicate_timestamps: int
    rows_out: int

def clean_measurements(
    df: pd.DataFrame,
    *,
    invalid_values: tuple[float, ...] = DEFAULT_INVALID_VALUES,
    max_value: float = DEFAULT_MAX_VALUE,
    valid_qc: str = DEFAULT_VALID_QC,
) -> tuple[pd.DataFrame, CleaningReport]:
    if not {"timestamp", "pm25"}.issubset(df.columns):
        raise ValueError(
            "DataFrame must have columns 'timestamp' and 'pm25'"
        )

    rows_in = len(df)
    out = df.copy()

    missing = out["timestamp"].isna() | out["pm25"].isna()
    dropped_missing = int(missing.sum())
    out = out.loc[~missing]

    marker = out["pm25"].isin(list(invalid_values))
    dropped_invalid_marker = int(marker.sum())
    out = out.loc[~marker]

    if "qc" in out.columns:
        invalid_qc = out["qc"] != valid_qc
        dropped_invalid_qc = int(invalid_qc.sum())
        out = out.loc[~invalid_qc]
    else:
        dropped_invalid_qc = 0

    negative = out["pm25"] < 0
    dropped_negative = int(negative.sum())
    out = out.loc[~negative]

    above_max = out["pm25"] > max_value
    dropped_above_max = int(above_max.sum())
    out = out.loc[~above_max]

    before = len(out)
    out = out.drop_duplicates(
        subset="timestamp",
        keep="first",
    )
    dropped_duplicate_timestamps = before - len(out)

    out = out.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    report = CleaningReport(
        rows_in=rows_in,
        dropped_missing=dropped_missing,
        dropped_invalid_marker=dropped_invalid_marker,
        dropped_invalid_qc=dropped_invalid_qc,
        dropped_negative=dropped_negative,
        dropped_above_max=dropped_above_max,
        dropped_duplicate_timestamps=dropped_duplicate_timestamps,
        rows_out=len(out),
    )

    return out, report
