import duckdb

con = duckdb.connect("rainfall.duckdb")


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

print(
    con.execute("SELECT * FROM daily_rainfall_summary").fetchall()
)

con.close()