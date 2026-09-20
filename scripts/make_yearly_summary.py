from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
RESULT_PATH = OUTPUT_DIR / "yearly_summary.csv"

HEATING_MONTHS = {11, 12, 1, 2, 3}


def main() -> None:
    rows = []

    for year in range(2019, 2025):
        yearly_path = OUTPUT_DIR / str(year) / "yearly_means.csv"
        seasonal_path = OUTPUT_DIR / str(year) / "seasonal_summary.csv"

        if not yearly_path.is_file():
            print(f"Warning: file not found: {yearly_path}")
            continue

        if not seasonal_path.is_file():
            print(f"Warning: file not found: {seasonal_path}")
            continue

        yearly = pd.read_csv(yearly_path)
        seasonal = pd.read_csv(seasonal_path)

        if yearly.empty:
            continue

        yearly_mean = yearly.iloc[0]["mean"]
        yearly_n = yearly.iloc[0]["n"]

        heating = seasonal[
            seasonal["season"] == "heating"
        ]

        non_heating = seasonal[
            seasonal["season"] == "non-heating"
        ]

        if heating.empty or non_heating.empty:
            print(f"Warning: incomplete seasonal data for {year}")
            continue

        rows.append(
            {
                "year": year,
                "mean": yearly_mean,
                "n": yearly_n,
                "heating_mean": heating.iloc[0]["mean"],
                "non_heating_mean": non_heating.iloc[0]["mean"],
            }
        )

    if not rows:
        raise SystemExit("No yearly results found.")

    summary = pd.DataFrame(rows)
    summary = summary.sort_values("year")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(RESULT_PATH, index=False)

    print(f"Saved: {RESULT_PATH}")
    print(f"Rows: {len(summary)}")


if __name__ == "__main__":
    main()
