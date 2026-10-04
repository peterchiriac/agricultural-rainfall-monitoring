import duckdb
import json

con = duckdb.connect("rainfall.duckdb")

con.execute("""
    CREATE TABLE IF NOT EXISTS rainfall_readings (
        reading_id VARCHAR PRIMARY KEY,
        reading_time TIMESTAMPTZ NOT NULL,
        measure_id VARCHAR NOT NULL,
        rainfall_mm DOUBLE
        )
""") # table creation

print(con.execute("DESCRIBE rainfall_readings").fetchall())

with open("readings_raw.json", "r") as json_file:
    data = json.load(json_file) # file loading. read the preserved API response without fetching again

print("Readings to load:", len(data["items"]))

insert_sql = """INSERT INTO rainfall_readings (reading_id, reading_time, measure_id, rainfall_mm)
VALUES ($reading_id, $reading_time, $measure_id, $rainfall_mm) ON CONFLICT (reading_id) DO NOTHING"""   # Skip existing reading IDs so repeat loads are safe

for reading in data["items"]:   # load every reading
    params = {
        "reading_id": reading["@id"],
        "reading_time": reading["dateTime"],
        "measure_id": reading["measure"],
        "rainfall_mm": reading.get("value") # handling missing values
            } # parameter mapping: map API fields to SQL parameters
    con.execute(insert_sql, params)

print(con.execute("SELECT * FROM rainfall_readings").fetchall()) # verification. inspect the stored readings

con.close()