
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "hourly_transit_metrics.sql"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    output_path = (
        root / "data" / "processed"
        / "hourly_transit_metrics.parquet"
    )

    print("\n=== HOURLY TRANSIT METRICS ===\n")

    result = con.execute("""
        SELECT
            COUNT(*) AS hourly_borough_rows,
            COUNT(DISTINCT hour_start) AS distinct_hours,
            MIN(hour_start) AS first_hour,
            MAX(hour_start) AS last_hour,
            SUM(total_ridership) AS total_recorded_ridership,
            SUM(total_transfers) AS total_recorded_transfers
        FROM read_parquet(?)
    """, [str(output_path)]).fetchdf()

    print(result.to_string(index=False))

    print("\n=== RIDERSHIP BY BOROUGH ===\n")

    borough_result = con.execute("""
        SELECT
            borough,
            SUM(total_ridership) AS total_ridership,
            SUM(total_transfers) AS total_transfers
        FROM read_parquet(?)
        GROUP BY borough
        ORDER BY total_ridership DESC
    """, [str(output_path)]).fetchdf()

    print(borough_result.to_string(index=False))

finally:
    con.close()
