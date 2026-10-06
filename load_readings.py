import duckdb
import json

con = duckdb.connect("rainfall.duckdb")

# Create the Silver tables if they do not already exist.
# Stations, measures and readings are modelled as separate entities,
# with foreign keys preserving their one-to-many relationships.
con.execute("""CREATE TABLE IF NOT EXISTS stations(
   station_id VARCHAR PRIMARY KEY,
   station_reference_number VARCHAR,
   latitude DECIMAL(8,6),
   longitude DECIMAL(9,6)
   )
""")


con.execute("""CREATE TABLE IF NOT EXISTS measures(
   measure_id VARCHAR PRIMARY KEY,
   station_id VARCHAR REFERENCES stations(station_id),
   unit VARCHAR,
   period_seconds INTEGER,
   parameter VARCHAR
   )
""")


con.execute("""
    CREATE TABLE IF NOT EXISTS rainfall_readings (
        reading_id VARCHAR PRIMARY KEY,
        reading_time TIMESTAMPTZ NOT NULL,
        measure_id VARCHAR NOT NULL REFERENCES measures(measure_id),
        rainfall_mm DOUBLE
        )
""") 

# Insert station metadata. Existing station IDs are skipped so the load
# can be rerun safely without creating duplicate records.

station_sql = """
INSERT INTO stations (
    station_id,
    station_reference_number,
    latitude,
    longitude
)
VALUES (
    $station_id,
    $station_reference_number,
    $latitude,
    $longitude
)
ON CONFLICT (station_id) DO NOTHING
"""

station_params = {
    "station_id": "http://environment.data.gov.uk/flood-monitoring/id/stations/E7050",
    "station_reference_number": "E7050",
    "latitude": 52.186277,
    "longitude": -1.171327
}

# Insert metadata describing what the station measures and how often.
# The station_id foreign key links the measure back to its station.

measure_sql = """
INSERT INTO measures (
    measure_id,
    station_id,
    unit,
    period_seconds,
    parameter
)
VALUES (
    $measure_id,
    $station_id,
    $unit,
    $period_seconds,
    $parameter
)
ON CONFLICT (measure_id) DO NOTHING
"""

measure_params = {
    "measure_id" : "http://environment.data.gov.uk/flood-monitoring/id/measures/E7050-rainfall-tipping_bucket_raingauge-t-15_min-mm",
    "station_id" : "http://environment.data.gov.uk/flood-monitoring/id/stations/E7050",
    "unit" : "mm",
    "period_seconds" : 900,
    "parameter" : "rainfall"
}

# Load parent entities before readings so foreign-key references are valid.
con.execute(station_sql, station_params)
con.execute(measure_sql, measure_params)


# Read the preserved Bronze API response rather than requesting the source again.
with open("readings_raw.json", "r") as json_file:
    data = json.load(json_file)


print("Readings to load:", len(data["items"]))

# Skip existing reading IDs so repeat loads are safe.
insert_sql = """
INSERT INTO rainfall_readings (
    reading_id,
    reading_time,
    measure_id,
    rainfall_mm
)
VALUES (
    $reading_id,
    $reading_time,
    $measure_id,
    $rainfall_mm
) 
ON CONFLICT (reading_id) DO NOTHING
"""   

for reading in data["items"]:  
    params = {
        "reading_id": reading["@id"],
        "reading_time": reading["dateTime"],
        "measure_id": reading["measure"],
        "rainfall_mm": reading.get("value")
    } 
    con.execute(insert_sql, params)

# Verify the total number of readings stored after the load.
reading_count = con.execute(
    "SELECT COUNT(*) FROM rainfall_readings"
).fetchone()[0]

print(f"Load complete. Total readings in database: {reading_count}") 

con.close()




