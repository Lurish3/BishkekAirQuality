# bishkek-air-quality

A small educational project: monthly, yearly and heating vs. non-heating season statistics of PM2.5
measurements, from a CSV file to tables and charts.

> **Status:** version 0.1, work in progress. It is a student project, not a scientific study and not
> health advice. It does not replace consultation with a doctor.

## What it does

- Reads a CSV file with a timestamp column and a PM2.5 column.
- Cleans it and **counts every removed row** (missing values, "no data" markers, out-of-range values,
  duplicate timestamps).
- Computes monthly means, yearly means and a heating vs. non-heating season summary.
- Saves CSV tables, a cleaning report (JSON) and PNG charts.

Not included yet: forecasts, maps, real-time data, a website.

## Demo

The demo uses **synthetic (invented) data**, not real measurements.

```bash
python scripts/make_sample_data.py
bishkek-air data/sample/synthetic.csv \
  --timestamp-col datetime --value-col pm25 \
  --timestamp-format "%Y-%m-%d %H:%M" --out output
```

Output in `output/`: `monthly_means.csv`, `yearly_means.csv`, `seasonal_summary.csv`,
`cleaning_report.json`, `monthly_means.png`, `seasonal_summary.png`.

## Installation

Requires Python 3.10 or newer.

```bash
git clone https://github.com/<your-nickname>/bishkek-air-quality.git
cd bishkek-air-quality
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage with real data

1. Download an open dataset and check its license (see `docs/data-notes.md`).
2. Put the file into `data/raw/` (it is git-ignored on purpose: some data cannot be republished).
3. Open the file, note the column names, units and the "no data" marker in `docs/data-notes.md`.
4. Run:

```bash
bishkek-air data/raw/<file>.csv --timestamp-col "<date column>" --value-col "<pm25 column>"
```

If your data is an Excel file, export it to CSV first (reading Excel directly is on the roadmap).

## Configuration

| Option | Meaning | Default |
|---|---|---|
| `--timestamp-col` | date/time column name (required) | — |
| `--value-col` | PM2.5 column name (required) | — |
| `--timestamp-format` | date format, e.g. `"%d.%m.%Y %H:%M"` | auto-detect |
| `--sep` | CSV separator | `,` |
| `--out` | output directory | `output` |
| `--invalid` | values meaning "no data" | `-999` |
| `--max-value` | values above this are errors | `1000` |

The defaults for `--invalid`, `--max-value` and the heating season months (Nov-Mar, in
`src/bishkek_air/analyze.py`) are **assumptions**. Check them against your data and sources.

## Testing

```bash
pytest                                              # inside the virtual environment
PYTHONPATH=src:tests python -m unittest discover -s tests   # without installing anything
ruff check .
```

## Limitations

- One measuring point does not describe the whole city.
- Different devices are not directly comparable.
- Gaps in the data affect the means; see `cleaning_report.json` and `n` in the tables.
- A seasonal difference is an observation, not proof of its cause.

## Roadmap

- [ ] Read Excel files directly
- [ ] Data notes and cleaning decisions for the real dataset
- [ ] Short Russian explanation page for non-programmers
- [ ] Compare with a second data source
- [ ] Notebook with step-by-step explanation

## License

Code: MIT (see `LICENSE`). Data has its own license: follow the terms of the source you use and# Bishkek Air Quality

Python project for analyzing PM2.5 measurements collected in Bishkek, Kyrgyzstan.

The project processes CSV datasets, removes invalid measurements, calculates monthly, yearly and seasonal statistics, and generates charts.

## Features

* CSV loading and validation
* PM2.5 data cleaning
* QC filtering
* Monthly and yearly statistics
* Heating vs. non-heating season comparison
* CSV, JSON and PNG output
* Automated tests

## Requirements

* Python 3.10+
* pandas
* matplotlib
* pytest

## Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd bishkek-air-quality
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install pandas matplotlib pytest
```

## Usage

The main command is `bishkek-air`.

Example:

```bash
bishkek-air data/raw/Bishkek_PM2.5_2020_YTD.csv \
    --timestamp-col "Date (LT)" \
    --value-col "Raw Conc." \
    --timestamp-format "%Y-%m-%d %I:%M %p" \
    --qc-col "QC Name" \
    --qc-valid Valid \
    --year 2020 \
    --out output/2020
```

For the 2020 dataset, this leaves 8,094 valid observations after cleaning.

The command creates:

```text
output/2020/
├── monthly_means.csv
├── yearly_means.csv
├── seasonal_summary.csv
├── cleaning_report.json
├── monthly_means.png
└── seasonal_summary.png
```

### Command options

| Option               | Description                  |
| -------------------- | ---------------------------- |
| `--timestamp-col`    | Timestamp column             |
| `--value-col`        | PM2.5 column                 |
| `--qc-col`           | QC column                    |
| `--qc-valid`         | Valid QC value               |
| `--timestamp-format` | Timestamp format             |
| `--sep`              | CSV separator                |
| `--out`              | Output directory             |
| `--year`             | Select a calendar year       |
| `--invalid`          | Invalid marker values        |
| `--max-value`        | Maximum accepted PM2.5 value |

Default invalid marker: `-999`.

Default maximum value: `1000`.

## Data cleaning

Before analysis, the following records are removed:

* missing timestamps or PM2.5 values;
* invalid marker values such as `-999`;
* measurements with invalid QC;
* negative PM2.5 values;
* values above the configured maximum;
* duplicate timestamps.

A JSON report with the number of removed records is written to `cleaning_report.json`.

Example:

```json
{
  "rows_in": 8652,
  "dropped_missing": 0,
  "dropped_invalid_marker": 11,
  "dropped_invalid_qc": 21,
  "dropped_out_of_range": 526,
  "dropped_duplicate_timestamps": 0,
  "rows_out": 8094
}
```

## Analysis

Monthly results are stored in:

```text
monthly_means.csv
```

Yearly results:

```text
yearly_means.csv
```

Seasonal results:

```text
seasonal_summary.csv
```

For the seasonal comparison, the project uses November–March as the heating season. This is an analytical choice, not a causal claim about the source of PM2.5.

## Project-wide results

Monthly results from all available years can be combined with:

```bash
python scripts/combine_monthly.py
```

This creates:

```text
output/all_years_monthly.csv
```

The combined dataset currently contains 65 months:

* February–December 2019
* 2020–2023
* January–June 2024

Create the overall monthly chart with:

```bash
python scripts/make_all_years_plot.py
```

Output:

```text
output/all_years_monthly.png
```

A yearly summary can be generated with:

```bash
python scripts/make_yearly_summary.py
```

Output:

```text
output/yearly_summary.csv
```

It contains:

```text
year
mean
n
heating_mean
non_heating_mean
```

## Data coverage

| Year | Coverage          |
| ---- | ----------------- |
| 2019 | February–December |
| 2020 | January–December  |
| 2021 | January–December  |
| 2022 | January–December  |
| 2023 | January–December  |
| 2024 | January–June      |

2024 is incomplete, so its yearly mean is not directly comparable with full-year values.

Some YTD files contain a small number of measurements from the beginning of the following year. The `--year` option removes those records when calculating statistics for a specific calendar year.

## Project structure

```text
bishkek-air-quality/
├── data/raw/              # Raw CSV datasets
├── docs/                  # Data notes
├── scripts/               # Additional analysis scripts
├── output/                # Generated results
├── src/bishkek_air/       # Main Python package
├── tests/                 # Automated tests
├── README.md
├── LICENSE
├── pyproject.toml
└── .gitignore
```

Main modules:

* `load.py` — CSV loading
* `clean.py` — data cleaning
* `analyze.py` — statistics
* `plots.py` — charts
* `cli.py` — command-line interface

## Tests

Run:

```bash
pytest -q
```

Current test suite:

```text
23 passed
```

## Limitations

The project only analyzes the available PM2.5 measurements. It does not use meteorological data or other variables to determine why PM2.5 concentrations change.

The seasonal comparison should therefore be treated as a descriptive statistic rather than evidence of causation.

## License

No license has been specified yet.
