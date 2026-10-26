
from pathlib import Path
import csv
import hashlib
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "metadata"
OUTPUT_FILE = OUTPUT_DIR / "source_inventory.csv"

# Files we have downloaded so far
EXPECTED_FILES = {
    "taxi_april": "taxi/yellow_tripdata_2024-04.parquet",
    "taxi_may": "taxi/yellow_tripdata_2024-05.parquet",
    "taxi_june": "taxi/yellow_tripdata_2024-06.parquet",
    "weather": "weather/open-meteo-40.74N74.04W32m.csv",
    "zone_lookup": "zones/taxi_zone_lookup.csv",
    "zone_boundaries_zip": "zones/taxi_zones.zip",
}

def calculate_sha256(file_path):
    """Calculate a file's SHA-256 checksum without loading it all into memory."""
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    extracted_at = datetime.now(timezone.utc).isoformat()

    rows = []

    for source_name, relative_path in EXPECTED_FILES.items():
        file_path = RAW_DIR / relative_path

        if not file_path.is_file():
            print(f"MISSING: {relative_path}")
            continue

        rows.append({
            "source_name": source_name,
            "relative_path": file_path.relative_to(PROJECT_ROOT).as_posix(),
            "file_size_bytes": file_path.stat().st_size,
            "sha256": calculate_sha256(file_path),
            "inventory_created_at_utc": extracted_at,
        })

        print(f"FOUND: {relative_path}")

    fieldnames = [
        "source_name",
        "relative_path",
        "file_size_bytes",
        "sha256",
        "inventory_created_at_utc",
    ]

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nInventory saved to: {OUTPUT_FILE}")
    print(f"Files recorded: {len(rows)} of {len(EXPECTED_FILES)}")


if __name__ == "__main__":
    main()
