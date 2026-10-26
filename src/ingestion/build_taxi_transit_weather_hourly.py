
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
con = duckdb.connect(str(root / "metropulse.duckdb"))

sql_path = (
    root / "sql" / "marts"
    / "taxi_transit_weather_hourly.sql"
)

output_path = (
    root / "data" / "processed"
    / "taxi_transit_weather_hourly.parquet"
)

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    result = con.execute("""
        SELECT
            COUNT(*) AS joined_hours,
            COUNT(DISTINCT hour_start) AS distinct_hours,
            MIN(hour_start) AS first_hour,
            MAX(hour_start) AS last_hour,
            SUM(taxi_trips) AS total_taxi_trips,
            SUM(total_ridership) AS total_recorded_ridership,
            COUNT(*) FILTER (WHERE is_rainy_hour)
                AS rainy_hours,
            COUNT(*) FILTER (WHERE NOT is_rainy_hour)
                AS non_rainy_hours,
            COUNT(*) FILTER (WHERE temperature_c IS NULL)
                AS missing_temperature
        FROM read_parquet(?)
    """, [str(output_path)]).fetchdf()

    print("\n=== COMBINED TAXI, TRANSIT & WEATHER VALIDATION ===\n")
    print(result.to_string(index=False))

finally:
    con.close()
