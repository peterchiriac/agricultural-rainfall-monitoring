import duckdb

# Connect to the local DuckDB database.
con = duckdb.connect("rainfall.duckdb")

# Build the Gold daily rainfall summary from Silver readings.
con.execute("""
CREATE OR REPLACE TABLE daily_rainfall_summary AS
    SELECT
    CAST(reading_time AT TIME ZONE 'UTC' AS DATE) AS date,
    measure_id,
    SUM(rainfall_mm) AS total_rainfall_mm,
    COUNT(DISTINCT reading_id) AS actual_readings,
    96 AS expected_readings,
    COUNT(DISTINCT reading_id) / 96 * 100 AS completeness_pct
FROM rainfall_readings
GROUP BY date, measure_id
""")

# Export the Gold summary as CSV for Tableau.
con.execute("""
    COPY (SELECT * FROM daily_rainfall_summary)
    TO 'daily_rainfall_summary.csv' 
    (HEADER, DELIMITER ',')
""")

print("Gold summary:")
print(
    con.execute("SELECT * FROM daily_rainfall_summary").fetchall()
)

con.close()