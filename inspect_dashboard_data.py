import duckdb
from pathlib import Path

folder = Path("data/processed")
files = [
    "taxi_transit_weather_hourly.parquet",
    "pickup_zone_metrics.parquet",
    "airport_daily_unit_economics.parquet",
    "airport_sensitivity.parquet",
    "hourly_weather_metrics.parquet",
    "hourly_transit_metrics.parquet",
]

con = duckdb.connect()

for name in files:
    path = folder / name
    print(f"\n{'=' * 65}\n{name}")

    if not path.exists():
        print("MISSING")
        continue

    print(f"Size: {path.stat().st_size / 1024:.1f} KB")
    result = con.execute(
        "DESCRIBE SELECT * FROM read_parquet(?)",
        [str(path.resolve())]
    ).fetchall()

    for column in result:
        print(f"  {column[0]}: {column[1]}")

    count = con.execute(
        "SELECT COUNT(*) FROM read_parquet(?)",
        [str(path.resolve())]
    ).fetchone()[0]
    print(f"Rows: {count:,}")

con.close()
