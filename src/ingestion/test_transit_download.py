
import json
import time
from datetime import date
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "transit"
OUTPUT_FILE = OUTPUT_DIR / "test_mta_2024-04-01.jsonl"

API_URL = "https://data.ny.gov/resource/wujg-7c2s.json"
EXPECTED_ROWS = 73642
BATCH_SIZE = 1000
MAX_RETRIES = 5


def fetch_batch(session, offset):
    params = {
        "$where": (
            "transit_timestamp >= '2024-04-01T00:00:00' "
            "AND transit_timestamp < '2024-04-02T00:00:00' "
            "AND transit_mode = 'subway'"
        ),
        "$limit": BATCH_SIZE,
        "$offset": offset,
        "$order": (
            "transit_timestamp, station_complex_id, "
            "payment_method, fare_class_category"
        ),
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(API_URL, params=params, timeout=120)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as error:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"Batch failed at offset {offset}"
                ) from error

            wait = min(2 ** attempt, 30)
            print(f"Request failed: {error}. Retrying in {wait}s...")
            time.sleep(wait)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists():
        raise FileExistsError(
            f"{OUTPUT_FILE} already exists. "
            "Inspect or rename it before running this test again."
        )

    total_rows = 0
    offset = 0

    with requests.Session() as session:
        session.headers.update({"User-Agent": "MetroPulse-Assessment/1.0"})

        with OUTPUT_FILE.open("w", encoding="utf-8") as output:
            while True:
                rows = fetch_batch(session, offset)

                if not rows:
                    break

                for row in rows:
                    output.write(json.dumps(row, separators=(",", ":")))
                    output.write("\n")

                total_rows += len(rows)
                offset += len(rows)

                print(f"Downloaded {total_rows:,} records")

                if len(rows) < BATCH_SIZE:
                    break

                time.sleep(0.2)

    print("\n--- DOWNLOAD VALIDATION ---")
    print(f"Expected rows:   {EXPECTED_ROWS:,}")
    print(f"Downloaded rows: {total_rows:,}")
    print(f"Output file:     {OUTPUT_FILE}")

    if total_rows != EXPECTED_ROWS:
        raise RuntimeError(
            "Row count mismatch. Do not treat this download as complete."
        )

    print("PASS: Downloaded count matches the API summary.")


if __name__ == "__main__":
    main()
