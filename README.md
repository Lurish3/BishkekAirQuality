# Bishkek Air Quality

Python project for analyzing PM2.5 measurements from Bishkek.

The project reads CSV data, cleans invalid measurements, calculates descriptive statistics, and produces CSV, JSON, and PNG outputs.

## Features

* CSV loading and validation
* Quality-control filtering
* PM2.5 data cleaning
* Monthly and yearly statistics
* Heating vs. non-heating season comparison
* Data completeness calculation
* CSV, JSON, and PNG output
* Automated tests and Ruff linting

## Data

The project uses PM2.5 measurements from the U.S. Department of State air-quality monitoring data available through AirNow. AirNow provides access to air-quality data from U.S. embassies and consulates. The data is preliminary and is not the same as fully validated regulatory data in the EPA Air Quality System (AQS). See `docs/data-notes.md` for the dataset-specific notes.

The current dataset contains:

| Year | Coverage          |
| ---- | ----------------- |
| 2019 | February–December |
| 2020 | January–December  |
| 2021 | January–December  |
| 2022 | January–December  |
| 2023 | January–December  |
| 2024 | January–June      |

The 2024 data is incomplete and should not be directly compared with full-year results.

Some YTD files contain a small number of measurements from the beginning of the following year. When `--year` is used, only measurements from the selected calendar year are analyzed.

Raw data files are kept outside the repository.

## Installation

Requires Python 3.10 or newer.

git clone https://github.com/Lurish3/BishkekAirQuality.git
cd BishkekAirQuality

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

For fish shell:

source .venv/bin/activate.fish

## Usage

The main command is `bishkek-air`.

Example using the 2020 dataset:

bishkek-air data/raw/Bishkek_PM2.5_2020_YTD.csv \
    --timestamp-col "Date (LT)" \
    --value-col "Raw Conc." \
    --timestamp-format "%Y-%m-%d %I:%M %p" \
    --qc-col "QC Name" \
    --qc-valid Valid \
    --year 2020 \
    --out output/2020

The command creates:

output/2020/
├── monthly_means.csv
├── yearly_means.csv
├── seasonal_summary.csv
├── cleaning_report.json
├── monthly_means.png
└── seasonal_summary.png

## Command options

| Option               | Description                  | Default   |
| -------------------- | ---------------------------- | --------- |
| `--timestamp-col`    | Timestamp column             | required  |
| `--value-col`        | PM2.5 column                 | required  |
| `--qc-col`           | Quality-control column       | none      |
| `--qc-valid`         | QC value considered valid    | `Valid`   |
| `--timestamp-format` | Timestamp format             | automatic |
| `--sep`              | CSV separator                | `,`       |
| `--out`              | Output directory             | `output`  |
| `--year`             | Select a calendar year       | none      |
| `--invalid`          | Invalid marker values        | `-999`    |
| `--max-value`        | Maximum accepted PM2.5 value | `1000`    |

## Data cleaning

Before analysis, the program removes:

* missing timestamps or PM2.5 values;
* invalid marker values such as `-999`;
* measurements with invalid QC;
* negative PM2.5 values;
* values above the configured maximum;
* duplicate timestamps.

For duplicate timestamps, the first remaining row is kept.

The default maximum value is `1000 µg/m³`. This is a configurable validation rule, not a claim that higher concentrations are physically impossible.

Every cleaning step is recorded in `cleaning_report.json`.

For a 2020 run, the report includes counts such as:

{
  "rows_in": 8652,
  "dropped_missing": 0,
  "dropped_invalid_marker": 11,
  "dropped_invalid_qc": 21,
  "dropped_negative": 526,
  "dropped_above_max": 0,
  "dropped_duplicate_timestamps": 0,
  "rows_out": 8094
}

## Analysis

The project calculates:

* monthly mean PM2.5 and observation count;
* yearly mean, standard deviation, quartiles, minimum, maximum, and observation count;
* heating and non-heating season statistics;
* expected, observed, and missing hourly observations;
* percentage of temporal coverage.

November–March is currently used as the heating season. This is an analytical grouping, not a claim that heating is the cause of higher PM2.5 concentrations.

## Project-wide analysis

Monthly results from the available years can be combined with:

python scripts/combine_monthly.py

This creates:

output/all_years_monthly.csv

The combined dataset covers 65 calendar months:

* February–December 2019
* 2020–2023
* January–June 2024

Create the overall monthly chart:

python scripts/make_all_years_plot.py

Output:

output/all_years_monthly.png

Generate the yearly summary:

python scripts/make_yearly_summary.py

Output:

output/yearly_summary.csv

## Reproducibility

Each CLI run records information about the input and environment in `cleaning_report.json`, including:

* input file;
* SHA-256 hash of the input file;
* analysis parameters;
* cleaning counts;
* data completeness;
* Python version;
* pandas version;
* matplotlib version;
* project version.

This makes it possible to identify which input data and settings produced a result.

## Tests

Run the test suite with:

pytest -q

Current test suite:

27 passed

Run Ruff:

ruff check .

CI runs both linting and tests on GitHub Actions.

## Project structure

bishkek-air-quality/
├── data/raw/              # Raw datasets
├── docs/                  # Data documentation
├── scripts/               # Additional analysis scripts
├── output/                # Generated results
├── src/bishkek_air/       # Main Python package
├── tests/                 # Automated tests
├── README.md
├── LICENSE
├── pyproject.toml
└── .gitignore

Main modules:

* `load.py` — CSV loading
* `clean.py` — data cleaning
* `analyze.py` — descriptive statistics
* `plots.py` — charts
* `cli.py` — command-line interface

## Limitations

* The dataset represents a monitoring location, not the whole city.
* Missing observations can affect calculated statistics.
* Different monitoring instruments or locations may not be directly comparable.
* The analysis does not include weather, traffic, or other possible PM2.5 sources.
* Seasonal differences are descriptive and do not establish causation.
* 2024 contains only January–June data.

## License

The project code is licensed under the MIT License. See `LICENSE`.

The original PM2.5 data is not automatically covered by this license. Its source terms and redistribution conditions should be checked before redistributing the data.

