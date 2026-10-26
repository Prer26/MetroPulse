
import requests

URL = "https://data.ny.gov/resource/wujg-7c2s.json"

params = {
    "$select": (
        "MIN(transit_timestamp) AS first_timestamp, "
        "MAX(transit_timestamp) AS last_timestamp, "
        "COUNT(*) AS row_count"
    ),
    "$where": (
        "transit_timestamp >= '2024-04-01T00:00:00' "
        "AND transit_timestamp < '2024-04-02T00:00:00' "
        "AND transit_mode = 'subway'"
    ),
}

response = requests.get(URL, params=params, timeout=60)
print("HTTP status:", response.status_code)
response.raise_for_status()

print("April 1 subway record summary:")
print(response.json())
