from __future__ import annotations
from dataclasses import dataclass
import pandas as pd

DEFAULT_INVALID_VALUES: tuple[float, ...] = (-999.0,)
DEFAULT_MAX_VALUE: float = 1000.0
DEFAULT_VALID_QC: str = "Valid"

@dataclass(frozen=True)
class CleaningReport:
    """Summary of rows removed during cleaning."""
    rows_in: int
    dropped_missing: int
    dropped_invalid_marker: int
    dropped_invalid_qc: int
    dropped_out_of_range: int
    dropped_duplicate_timestamps: int
    rows_out: int

def clean_measurements(
    df: pd.DataFrame,
    *,
    invalid_values: tuple[float, ...] = DEFAULT_INVALID_VALUES,
    max_value: float = DEFAULT_MAX_VALUE,
    valid_qc: str = DEFAULT_VALID_QC,
) -> tuple[pd.DataFrame, CleaningReport]:
    """Return cleaned measurements and a report of removed rows."""
    if not {"timestamp", "pm25"}.issubset(df.columns):
        raise ValueError("DataFrame must have columns 'timestamp' and 'pm25'")

    rows_in = len(df)
    out = df.copy()

    missing = out["timestamp"].isna() | out["pm25"].isna()
    dropped_missing = int(missing.sum())
    out = out.loc[~missing]

    marker = out["pm25"].isin(list(invalid_values))
    dropped_marker = int(marker.sum())
    out = out.loc[~marker]

    if "qc" in out.columns:
        invalid_qc = out["qc"] != valid_qc
        dropped_invalid_qc = int(invalid_qc.sum())
        out = out.loc[~invalid_qc]
    else:
        dropped_invalid_qc = 0

    outside = (out["pm25"] < 0) | (out["pm25"] > max_value)
    dropped_range = int(outside.sum())
    out = out.loc[~outside]

    before = len(out)
    out = out.drop_duplicates(subset="timestamp", keep="first")
    dropped_dupes = before - len(out)

    out = out.sort_values("timestamp").reset_index(drop=True)

    report = CleaningReport(
        rows_in=rows_in,
        dropped_missing=dropped_missing,
        dropped_invalid_marker=dropped_marker,
        dropped_invalid_qc=dropped_invalid_qc,
        dropped_out_of_range=dropped_range,
        dropped_duplicate_timestamps=dropped_dupes,
        rows_out=len(out),
    )

    return out, report
