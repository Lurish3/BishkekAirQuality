"""How much do negative PM2.5 values matter for the results?

Small negative readings can be measurement noise. If a cleaning rule removes ONLY the
negative values, the averages can shift upwards. This script measures that shift so that
the cleaning decision can be justified with numbers instead of assumed.

It is standalone (only pandas) and does not depend on the bishkek_air package.

Example (same options as the main program):

    python scripts/check_negatives.py data/raw/Bishkek_PM2.5_20*_YTD.csv \
        --timestamp-col "Date (LT)" --value-col "Raw Conc." \
        --timestamp-format "%Y-%m-%d %I:%M %p" \
        --qc-col "QC Name" --qc-valid Valid --out output/negatives_check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

HEATING_MONTHS = {11, 12, 1, 2, 3}  # same assumption as in the main analysis


def load_all(args: argparse.Namespace) -> pd.DataFrame:
    frames = []
    for path in args.csv:
        raw = pd.read_csv(path)
        wanted = [args.timestamp_col, args.value_col] + ([args.qc_col] if args.qc_col else [])
        missing = [c for c in wanted if c not in raw.columns]
        if missing:
            sys.exit(f"error: columns {missing} not found in {path}. Have: {list(raw.columns)}")
        frame = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    raw[args.timestamp_col], format=args.timestamp_format, errors="coerce"
                ),
                "pm25": pd.to_numeric(raw[args.value_col], errors="coerce"),
            }
        )
        if args.qc_col:
            frame["qc"] = raw[args.qc_col].astype(str).str.strip()
        frames.append(frame)
    df = pd.concat(frames, ignore_index=True)

    df = df.dropna(subset=["timestamp", "pm25"])
    if args.qc_col and args.qc_valid is not None:
        df = df[df["qc"] == args.qc_valid]
    df = df[~df["pm25"].isin(args.invalid)]  # "no data" markers such as -999
    df = df.drop_duplicates(subset="timestamp", keep="first")
    return df.sort_values("timestamp").reset_index(drop=True)


def negatives_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per year: how many values are negative, and how negative."""
    rows = []
    for year, part in [*df.groupby(df["timestamp"].dt.year), ("all", df)]:
        neg = part.loc[part["pm25"] < 0, "pm25"]
        rows.append(
            {
                "year": year,
                "n_rows": len(part),
                "n_negative": len(neg),
                "share_negative_%": round(100 * len(neg) / len(part), 2) if len(part) else 0.0,
                "min_negative": neg.min() if len(neg) else float("nan"),
                "median_negative": neg.median() if len(neg) else float("nan"),
                "n_exact_zero": int((part["pm25"] == 0).sum()),
            }
        )
    return pd.DataFrame(rows).set_index("year")


def compare_means(df: pd.DataFrame) -> pd.DataFrame:
    """Mean PM2.5 under three rules for negative values, per year and per season."""
    df = df.assign(
        year=df["timestamp"].dt.year,
        season=df["timestamp"].dt.month.map(
            lambda m: "heating" if m in HEATING_MONTHS else "non-heating"
        ),
    )

    def three_means(part: pd.DataFrame) -> pd.Series:
        v = part["pm25"]
        return pd.Series(
            {
                "n": len(v),
                "mean_negatives_removed": v[v >= 0].mean(),
                "mean_negatives_kept": v.mean(),
                "mean_negatives_as_zero": v.clip(lower=0).mean(),
            }
        )

    by_year = df.groupby("year")[["pm25"]].apply(three_means)
    by_season = df.groupby("season")[["pm25"]].apply(three_means)
    overall = three_means(df).to_frame("all").T
    out = pd.concat([by_year.astype(float), by_season, overall])
    out["difference_removed_minus_kept"] = (
        out["mean_negatives_removed"] - out["mean_negatives_kept"]
    )
    out.index = out.index.map(str)
    return out.round(3)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("csv", nargs="+")
    p.add_argument("--timestamp-col", required=True)
    p.add_argument("--value-col", required=True)
    p.add_argument("--timestamp-format", default=None)
    p.add_argument("--qc-col", default=None)
    p.add_argument("--qc-valid", default=None)
    p.add_argument("--invalid", type=float, nargs="*", default=[-999.0])
    p.add_argument("--out", default="output/negatives_check")
    args = p.parse_args()

    df = load_all(args)
    if df.empty:
        sys.exit("error: no rows left after basic cleaning")

    summary = negatives_summary(df)
    means = compare_means(df)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out / "negatives_summary.csv")
    means.to_csv(out / "means_by_rule.csv")

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 20)
    print("\n== How many negative values, and how negative ==")
    print(summary.to_string())
    print("\n== Mean PM2.5 under three rules for negative values ==")
    print(means.to_string())
    print(f"\nTables saved to {out.resolve()}")
    print(
        "\nHow to read it: if 'difference_removed_minus_kept' is small compared with the "
        "means, the rule barely matters; if it is large, explain your choice in the README."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
