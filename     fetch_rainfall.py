import requests
from datetime import datetime, timedelta

r = requests.get('https://environment.data.gov.uk/flood-monitoring/id/measures/E7050-rainfall-tipping_bucket_raingauge-t-15_min-mm/readings?date=2026-10-01&_limit=100')  # Get request
r.raise_for_status()

with open("readings_raw.json", "wb") as json_file:
    json_file.write(r.content) # save the raw file

data = r.json() # Parse the JSON response into Python dictionaries and lists

timestamps = []


for reading in data["items"]:
	s = reading["dateTime"]
	dt = datetime.fromisoformat(s)
	timestamps.append(dt)

timestamps.sort()

for i in range(1, len(timestamps)):
    difference = timestamps[i] - timestamps[i - 1]
    if difference != timedelta(minutes=15):
        print("Unexpected interval:", timestamps[i-1], timestamps[i], difference)

# Sanity check
expected_readings = 96
actual_readings = len(set(timestamps))
completeness = actual_readings/expected_readings * 100 

print("Expected readings:", expected_readings)
print("Actual readings:", actual_readings)
print("Completeness:", completeness)

print("Timestamp count:", len(timestamps))
print("Earliest:", timestamps[0])
print("Latest:", timestamps[-1])

print("HTTP status:", r.status_code) 
print("Top-Level keys:", list(data.keys()))
print("Reading count:", len(data["items"]))

