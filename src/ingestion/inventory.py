from pathlib import Path
import csv
import hashlib
import sys
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "metadata"
OUTPUT_FILE = OUTPUT_DIR / "source_inventory.csv"

EXPECTED_FILES = {
    "taxi_april": "taxi/yellow_tripdata_2024-04.parquet",
    "taxi_may": "taxi/yellow_tripdata_2024-05.parquet",
    "taxi_june": "taxi/yellow_tripdata_2024-06.parquet",
    "weather": "weather/open-meteo-40.74N74.04W32m.csv",
    "zone_lookup": "zones/taxi_zone_lookup.csv",
    "zone_boundaries_zip": "zones/taxi_zones.zip",
    "subway_q2": "transit/mta_subway_2024_q2.jsonl",
}

def calculate_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    missing = []
    rows = []

    for source_name, relative_path in EXPECTED_FILES.items():
        path = RAW_DIR / relative_path

        if not path.is_file():
            missing.append(relative_path)
            print(f"MISSING: {relative_path}")
            continue

        rows.append({
            "source_name": source_name,
            "relative_path": path.relative_to(PROJECT_ROOT).as_posix(),
            "file_size_bytes": path.stat().st_size,
            "sha256": calculate_sha256(path),
            "inventory_created_at_utc": datetime.now(timezone.utc).isoformat(),
        })
        print(f"FOUND: {relative_path}")

    if missing:
        print(f"\nERROR: {len(missing)} required source file(s) missing.")
        print("Inventory was not replaced. Restore/download the missing files first.")
        return 1

    fieldnames = [
        "source_name",
        "relative_path",
        "file_size_bytes",
        "sha256",
        "inventory_created_at_utc",
    ]

    temporary = OUTPUT_FILE.with_suffix(".csv.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    temporary.replace(OUTPUT_FILE)
    print(f"\nInventory saved: {OUTPUT_FILE}")
    print(f"Files recorded: {len(rows)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
