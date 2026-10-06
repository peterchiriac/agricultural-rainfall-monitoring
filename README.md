# Agricultural Rainfall Monitoring

A Python and DuckDB data pipeline for processing Environment Agency rainfall data for agricultural monitoring.

The project collects rainfall readings from the Environment Agency Real Time flood-monitoring API, preserves the raw response, transforms the data into a relational model, and produces a daily rainfall summary for visualisation in Tableau.

## Use Case

The pipeline is designed around a simple agricultural use case: helping a farm manager or grower monitor recent rainfall near agricultural land while also showing whether the underlying data is complete.

Rainfall totals alone can be misleading when readings are missing, so the pipeline produces both:

- daily rainfall in millimetres
- measurement completeness for the day

## Pipeline Architecture

```text
Environment Agency API
        |
        v
Bronze: readings_raw.json
        |
        v
Silver: DuckDB
        |
        |-- stations
        |-- measures
        |-- rainfall_readings
        |
        v
Gold: daily_rainfall_summary
        |
        v
daily_rainfall_summary.csv
        |
        v
Tableau dashboard
```

### Bronze

`fetch_rainfall.py` requests rainfall readings from the Environment Agency API and stores the raw response unchanged in `readings_raw.json`.

The script also performs basic source-data validation by checking:

- HTTP request success
- expected number of readings
- unique reading count
- 15-minute reading intervals
- daily completeness

Preserving the raw response means the downstream transformation can be rerun without requesting the source data again.

### Silver

`load_readings.py` loads the Bronze data into DuckDB using three related tables:

```text
stations
   |
   | 1:M
   v
measures
   |
   | 1:M
   v
rainfall_readings
```

Station, measure and reading data are stored separately to avoid repeatedly storing the same metadata and to preserve the relationships between the source entities.

Primary and foreign keys enforce these relationships.

The load uses `ON CONFLICT DO NOTHING` on entity IDs so that rerunning the script does not create duplicate records.

### Gold

`build_gold.py` creates `daily_rainfall_summary`, containing:

- date
- rainfall measure
- total daily rainfall
- actual reading count
- expected reading count
- completeness percentage

Daily aggregation uses UTC because the source readings are timestamped in UTC. This prevents local timezone conversion from splitting one source day across two dates.

The Gold table is exported to `daily_rainfall_summary.csv` for use in Tableau.

## Dashboard

The Tableau dashboard presents two simple operational metrics:

- daily rainfall
- data completeness

The packaged Tableau workbook is available at:

`dashboard/agricultural_rainfall_monitoring.twbx`

## Running the Pipeline

Run the scripts in order:

```bash
python fetch_rainfall.py
python load_readings.py
python build_gold.py
```

This produces the flow:

```text
API -> raw JSON -> DuckDB -> daily summary -> CSV
```

## Current Scope

The current prototype processes one selected Environment Agency rainfall measure and date.

The data model can represent multiple stations and measures, but ingestion is not yet automated across multiple locations.

The current measure reports at 15-minute intervals, giving an expected 96 readings per UTC day.

## Future Improvements

Possible next steps include:

- parameterising ingestion across multiple stations, measures and dates
- deriving expected reading counts from each measure's reporting period
- adding ingestion metadata such as retrieval time and source URL
- handling revised readings rather than only ignoring duplicate IDs
- expanding missing-value validation
- handling API pagination for larger requests
- adding automated tests
- supporting rainfall totals and completeness over user-defined time windows, making the data more useful for planning agricultural interventions and historical or seasonal comparisons

## Data Source

This project uses Environment Agency rainfall data from the Real Time flood-monitoring API (Beta).

Environment Agency data is used under the Open Government Licence.