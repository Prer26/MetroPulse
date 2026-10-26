
import requests

API_URL = "https://data.ny.gov/resource/wujg-7c2s.json"

params = {
    "$where": (
        "transit_timestamp >= '2024-04-01T00:00:00' "
        "AND transit_timestamp < '2024-07-01T00:00:00' "
        "AND transit_mode = 'subway'"
    ),
    "$limit": 1000,
    "$order": "transit_timestamp, station_complex_id",
}

response = requests.get(API_URL, params=params, timeout=60)

print("HTTP status:", response.status_code)
response.raise_for_status()

rows = response.json()

print("Records received:", len(rows))

if rows:
    print("\nFirst record:")
    print(rows[0])

    print("\nFields received:")
    print(list(rows[0].keys()))

    print("\nAll records within requested date range:",
          all(
              "2024-04-01" <= row["transit_timestamp"][:10] <= "2024-06-30"
              for row in rows
          ))
