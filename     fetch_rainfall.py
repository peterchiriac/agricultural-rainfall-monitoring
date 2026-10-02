import requests

r = requests.get('https://environment.data.gov.uk/flood-monitoring/id/measures/E7050-rainfall-tipping_bucket_raingauge-t-15_min-mm/readings?_sorted&_limit=3')  # Get request
r.raise_for_status()

with open("readings_raw.json", "wb") as json_file:
    json_file.write(r.content) # save the raw file

data = r.json()

print("HTTP status:", r.status_code) 
print("Top-Level keys:", list(data.keys()))
print("Reading count:", len(data["items"]))

