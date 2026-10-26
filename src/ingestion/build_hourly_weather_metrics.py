
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "hourly_weather_metrics.sql"
output_path = root / "data" / "processed" / "hourly_weather_metrics.parquet"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    result = con.execute("""
        SELECT
            COUNT(*) AS hourly_rows,
            COUNT(DISTINCT hour_start) AS distinct_hours,
            MIN(hour_start) AS first_hour,
            MAX(hour_start) AS last_hour,
            COUNT(*) FILTER (WHERE is_rainy_hour) AS rainy_hours,
            COUNT(*) FILTER (WHERE precipitation_mm IS NULL)
                AS missing_precipitation,
            AVG(temperature_c) AS avg_temperature_c,
            SUM(precipitation_mm) AS total_precipitation_mm
        FROM read_parquet(?)
    """, [str(output_path)]).fetchdf()

    print("\n=== HOURLY WEATHER MART VALIDATION ===\n")
    print(result.to_string(index=False))

finally:
    con.close()
