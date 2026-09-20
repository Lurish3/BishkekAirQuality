"""Numbers for the README "Results" section, computed from output/all_years_monthly.csv.

Input columns: year, month, mean, n  (monthly mean and number of hourly values).
Averages over several months are weighted by n, so they equal the mean of all hourly
values in those months. The table already reflects the cleaning rules used to make it.

Usage:
    python scripts/summarize_results.py [--input output/all_years_monthly.csv] [--months 3 4 5 6]
"""

from __future__ import annotations

import argparse
import calendar

import pandas as pd

HEATING = {11, 12, 1, 2, 3}  # same assumption as in the main analysis
LOW_COVERAGE = 0.75


def weighted_mean(part: pd.DataFrame) -> float:
    return float((part["mean"] * part["n"]).sum() / part["n"].sum())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="output/all_years_monthly.csv")
    p.add_argument("--months", type=int, nargs="+", default=[3, 4, 5, 6])
    args = p.parse_args()

    df = pd.read_csv(args.input)
    df["expected"] = [calendar.monthrange(y, m)[1] * 24 for y, m in zip(df["year"], df["month"])]
    df["coverage"] = df["n"] / df["expected"]
    df["label"] = df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)

    print(f"Months in table: {len(df)}  ({df['label'].iloc[0]} .. {df['label'].iloc[-1]})")
    print(f"Hourly values (sum of n): {int(df['n'].sum())}")

    print("\n== Highest and lowest monthly means ==")
    print(df.nlargest(3, "mean")[["label", "mean", "n"]].round(1).to_string(index=False))
    print(df.nsmallest(3, "mean")[["label", "mean", "n"]].round(1).to_string(index=False))

    print("\n== Heating (Nov-Mar) vs non-heating, weighted by n ==")
    is_heating = df["month"].isin(HEATING)
    print(f"heating:      {weighted_mean(df[is_heating]):.1f} ug/m3  (n = {int(df[is_heating]['n'].sum())})")
    print(f"non-heating:  {weighted_mean(df[~is_heating]):.1f} ug/m3  (n = {int(df[~is_heating]['n'].sum())})")

    print("\n== Complete heating seasons (Nov Y .. Mar Y+1), weighted by n ==")
    rows = []
    for year in sorted(df["year"].unique()):
        wanted = [(year, 11), (year, 12), (year + 1, 1), (year + 1, 2), (year + 1, 3)]
        part = df[[(y, m) in wanted for y, m in zip(df["year"], df["month"])]]
        if len(part) == 5:
            rows.append({"season": f"{year}/{year + 1}", "mean": round(weighted_mean(part), 1),
                         "n": int(part["n"].sum())})
    print(pd.DataFrame(rows).to_string(index=False))

    months = sorted(args.months)
    print(f"\n== Same months in every year: {months}, weighted by n (only years with all of them) ==")
    rows = []
    for year in sorted(df["year"].unique()):
        part = df[(df["year"] == year) & (df["month"].isin(months))]
        if len(part) == len(months):
            rows.append({"year": year, "mean": round(weighted_mean(part), 1),
                         "n": int(part["n"].sum()),
                         "min_coverage": round(float(part["coverage"].min()), 2)})
    print(pd.DataFrame(rows).to_string(index=False))

    print(f"\n== Months with less than {LOW_COVERAGE:.0%} of expected hourly values ==")
    low = df[df["coverage"] < LOW_COVERAGE]
    print(low[["label", "n", "expected", "coverage"]].round(2).to_string(index=False)
          if not low.empty else "none")


if __name__ == "__main__":
    main()
