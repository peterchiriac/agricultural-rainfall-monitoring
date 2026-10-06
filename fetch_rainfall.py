import requests
from datetime import datetime, timedelta

measure = "E7050-rainfall-tipping_bucket_raingauge-t-15_min-mm"
date = "2026-10-01"

url =  f"https://environment.data.gov.uk/flood-monitoring/id/measures/{measure}/readings?date={date}&_limit=100"

# Request rainfall readings from the Environment Agency API.
r = requests.get(url) 
r.raise_for_status()

# Preserve the raw API response as the Bronze layer.
with open("readings_raw.json", "wb") as json_file:
    json_file.write(r.content) 

# Parse the response for validation.
data = r.json()

timestamps = []

# Convert API timestamps to datetime objects for interval checks.
for reading in data["items"]:
    s = reading["dateTime"]
    dt = datetime.fromisoformat(s)
    timestamps.append(dt)

timestamps.sort()

# Flag gaps or irregular intervals in the expected 15-minute sequence.
for i in range(1, len(timestamps)):
    difference = timestamps[i] - timestamps[i - 1]
    if difference != timedelta(minutes=15):
        print("Unexpected interval:", timestamps[i-1], timestamps[i], difference)

# Sanity check
expected_readings = 96
actual_readings = len(set(timestamps))
completeness = actual_readings / expected_readings * 100 

print("HTTP status:", r.status_code) 
print("Expected readings:", expected_readings)
print("Actual readings:", actual_readings)
print("Completeness:", completeness)
print("Earliest:", timestamps[0])
print("Latest:", timestamps[-1])



