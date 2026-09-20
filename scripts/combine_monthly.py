from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
RESULT_PATH = OUTPUT_DIR / "all_years_monthly.csv"


def main() -> None:
    frames = []

    for year in range(2019, 2025):
        path = OUTPUT_DIR / str(year) / "monthly_means.csv"

        if not path.is_file():
            print(f"Warning: file not found: {path}")
            continue

        df = pd.read_csv(path)

        df["year"] = pd.to_datetime(df["month"]).dt.year
        df["month"] = pd.to_datetime(df["month"]).dt.month

        frames.append(df[["year", "month", "mean", "n"]])

    if not frames:
        raise SystemExit("No monthly files found.")

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(["year", "month"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_csv(RESULT_PATH, index=False)

    print(f"Saved: {RESULT_PATH}")
    print(f"Rows: {len(combined)}")


if __name__ == "__main__":
    main()
