
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "intermediate" / "int_taxi_trips.sql"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    print("Intermediate taxi view created successfully!")

    print("\nSample records:")
    print(con.execute("""
        SELECT
            source_month,
            pickup_date,
            pickup_hour,
            duration_minutes,
            fare_per_mile,
            average_speed_mph,
            has_missing_passenger_count,
            has_invalid_distance
        FROM int_taxi_trips
        LIMIT 5
    """).fetchdf().to_string(index=False))

    print("\nRows by month:")
    print(con.execute("""
        SELECT source_month, COUNT(*) AS total_rows
        FROM int_taxi_trips
        GROUP BY source_month
        ORDER BY source_month
    """).fetchdf().to_string(index=False))

finally:
    con.close()
