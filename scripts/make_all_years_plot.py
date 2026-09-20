from pathlib import Path

import pandas as pd

from bishkek_air.plots import plot_all_years_monthly


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "output" / "all_years_monthly.csv"
OUTPUT_PATH = PROJECT_ROOT / "output" / "all_years_monthly.png"


def main() -> None:
    if not INPUT_PATH.is_file():
        raise SystemExit(f"File not found: {INPUT_PATH}")

    monthly = pd.read_csv(INPUT_PATH)

    plot_all_years_monthly(monthly, OUTPUT_PATH)

    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
