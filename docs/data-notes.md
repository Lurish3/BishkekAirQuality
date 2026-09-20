# Data notes

## Source

The project uses hourly PM2.5 measurements from the U.S. Department of
State air quality monitoring program (DOSAir), collected at the U.S.
Embassy monitoring site in Bishkek, Kyrgyzstan.

The Department of State developed DOSAir in partnership with the U.S.
Environmental Protection Agency (EPA). The program provides air-quality
measurements from monitoring sites at U.S. diplomatic missions.

Source context:
- U.S. Department of State — Air Quality Monitoring Program (DOSAir)
- U.S. Embassy Bishkek air-quality monitoring site
- AirNow / DOSAir data distribution

## Files

The raw data used by this project consists of six CSV files:

- `Bishkek_PM2.5_2019_YTD.csv`
- `Bishkek_PM2.5_2020_YTD.csv`
- `Bishkek_PM2.5_2021_YTD.csv`
- `Bishkek_PM2.5_2022_YTD.csv`
- `Bishkek_PM2.5_2023_YTD.csv`
- `Bishkek_PM2.5_2024_YTD.csv`

The files are yearly/YTD exports and should not be assumed to contain a
complete calendar year.

## Columns used

The analysis uses:

- `Date (LT)` — local-time timestamp supplied by the dataset.
- `Raw Conc.` — raw PM2.5 concentration.
- `Conc. Unit` — concentration unit; the supplied files use `UG/M3`.
- `QC Name` — quality-control status.

Other columns present in the source files, such as AQI and NowCast
concentration, are not used in the current analysis.

The measurement duration in the supplied files is `1 Hr`.

## Timestamp

The source timestamp format is:

`%Y-%m-%d %I:%M %p`

The project parses the `Date (LT)` column using this format.

The analysis treats the timestamp as local time as provided by the source.
No timezone conversion is performed.

## Coverage

The supplied files do not all represent complete calendar years.

- 2019 begins on 2019-02-06.
- 2020 contains observations for the calendar year 2020.
- 2021 contains observations for the calendar year 2021.
- 2022 contains observations for the calendar year 2022.
- 2023 contains observations for the calendar year 2023.
- 2024 contains observations only through 2024-06-30.

Some YTD files also contain a small number of observations belonging to
the following calendar year. The analysis uses the `--year` filter when
a single calendar year is analysed.

Therefore incomplete years must not be interpreted as directly
comparable to complete years without accounting for their different
observation periods.

## Cleaning

The current cleaning pipeline performs the following operations:

1. Removes rows with a missing timestamp or PM2.5 value.
2. Removes configured invalid marker values. The default marker is `-999`.
3. Removes rows whose QC value is not `Valid` when a QC column is supplied.
4. Removes negative PM2.5 concentrations.
5. Removes values above the configurable maximum value.
   The default maximum is `1000 µg/m³`.
6. Removes duplicate timestamps, keeping the first observation.
7. Sorts the resulting data chronologically.

The cleaning process records the number of rows removed at each step in
`cleaning_report.json`.

## Units

PM2.5 concentration is analysed in micrograms per cubic metre (`µg/m³`).

The source CSV files encode this unit as `UG/M3`.

## Seasonal analysis

For descriptive seasonal analysis, the project defines the heating
season as November through March:

- November
- December
- January
- February
- March

All other months are classified as non-heating.

This classification is an analytical convention used by this project.
The analysis describes differences between these groups and does not by
itself establish causation.

## Completeness

The project calculates expected hourly observations between the selected
start and end timestamps and compares them with the timestamps actually
present in the cleaned data.

The resulting coverage information is stored in
`cleaning_report.json`.

## Reproducibility

Each CLI run records:

- input file path;
- SHA-256 hash of the input file;
- analysis parameters;
- cleaning statistics;
- completeness statistics;
- Python version;
- pandas version;
- matplotlib version;
- project version.

This allows the analysis configuration and the exact input file used for
a run to be identified.

## Limitations

This project is a descriptive analysis of one monitoring site.

The results should not automatically be interpreted as representative
of the air quality across all of Bishkek.

The project does not currently model meteorological variables, emissions,
population exposure, causal relationships, or health effects.

Incomplete observation periods and missing hourly observations can affect
annual and monthly summaries.

The current cleaning threshold of `1000 µg/m³` is a configurable data
validation rule, not a claim that every value below this threshold is
necessarily physically correct.

## Data provenance

The raw CSV files are preserved in `data/raw/`.

The project does not modify these raw files. Cleaning and analysis are
performed on data loaded into memory, and derived results are written to
`output/`.

The SHA-256 hash recorded in each `cleaning_report.json` identifies the
exact input file used for that run.
