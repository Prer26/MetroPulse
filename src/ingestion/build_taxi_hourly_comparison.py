
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
con = duckdb.connect(str(root / "metropulse.duckdb"))

try:
    sql_path = root / "sql" / "marts" / "taxi_hourly_comparison.sql"
    con.execute(sql_path.read_text(encoding="utf-8"))

    output_path = (
        root / "data" / "processed"
        / "taxi_hourly_comparison.parquet"
    )

    print("\n=== HOURLY TAXI COMPARISON INPUT ===\n")
    print(con.execute("""
        SELECT
            COUNT(*) AS hourly_rows,
            MIN(hour_start) AS first_hour,
            MAX(hour_start) AS last_hour,
            SUM(taxi_trips) AS total_taxi_trips
        FROM read_parquet(?)
    """, [str(output_path)]).fetchdf().to_string(index=False))
finally:
    con.close()
