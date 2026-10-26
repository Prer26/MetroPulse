from pathlib import Path
import hashlib
import os
import time
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"

SOURCES = {
    "taxi_april": (
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-04.parquet",
        "taxi/yellow_tripdata_2024-04.parquet",
    ),
    "taxi_may": (
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-05.parquet",
        "taxi/yellow_tripdata_2024-05.parquet",
    ),
    "taxi_june": (
        "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-06.parquet",
        "taxi/yellow_tripdata_2024-06.parquet",
    ),
    "weather": (
        "https://archive-api.open-meteo.com/v1/archive?latitude=40.74&longitude=-74.04&start_date=2024-04-01&end_date=2024-06-30&hourly=temperature_2m,precipitation,rain,snowfall,wind_speed_10m&timezone=America%2FNew_York",
        "weather/open-meteo-40.74N74.04W32m.csv",
    ),
    "zone_lookup": (
        "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv",
        "zones/taxi_zone_lookup.csv",
    ),
    "zone_boundaries_zip": (
        "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip",
        "zones/taxi_zones.zip",
    ),
}

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def download(name, url, relative_path):
    destination = RAW / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        print(f"KEEP existing raw file: {relative_path}")
        return

    temporary = destination.with_suffix(destination.suffix + ".part")
    last_error = None

    for attempt in range(1, 5):
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "MetroPulse/1.0"}
            )
            with urllib.request.urlopen(request, timeout=90) as response:
                status = getattr(response, "status", 200)
                if status != 200:
                    raise RuntimeError(f"Unexpected HTTP status: {status}")

                with temporary.open("wb") as out:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        out.write(chunk)

            if not temporary.exists() or temporary.stat().st_size == 0:
                raise RuntimeError("Downloaded file is empty")

            os.replace(temporary, destination)
            print(
                f"DOWNLOADED {name}: {destination.relative_to(ROOT)} "
                f"({destination.stat().st_size:,} bytes; "
                f"SHA-256 {sha256(destination)})"
            )
            return

        except Exception as exc:
            last_error = exc
            temporary.unlink(missing_ok=True)
            if attempt < 4:
                delay = 2 ** attempt
                print(f"{name}: attempt {attempt} failed ({exc}); retry in {delay}s")
                time.sleep(delay)

    raise RuntimeError(f"Failed to download {name}: {last_error}") from last_error

def main():
    for name, (url, relative_path) in SOURCES.items():
        download(name, url, relative_path)

if __name__ == "__main__":
    main()
