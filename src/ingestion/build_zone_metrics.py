
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "pickup_zone_metrics.sql"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    print("\n=== TOP 10 PICKUP ZONES BY TRIP VOLUME ===\n")
    print(con.execute("""
        SELECT
            pickup_borough,
            pickup_zone,
            SUM(total_trips) AS total_trips,
            ROUND(SUM(total_recorded_amount), 2)
                AS total_recorded_amount
        FROM mart_pickup_zone_metrics
        GROUP BY pickup_borough, pickup_zone
        ORDER BY total_trips DESC
        LIMIT 10
    """).fetchdf().to_string(index=False))

    print("\n=== ZONE LOOKUP COVERAGE ===\n")
    print(con.execute("""
        SELECT
            COUNT(*) AS zone_month_rows,
            COUNT(*) FILTER (
                WHERE pickup_zone IS NULL
            ) AS unmatched_zone_rows
        FROM mart_pickup_zone_metrics
    """).fetchdf().to_string(index=False))

finally:
    con.close()
