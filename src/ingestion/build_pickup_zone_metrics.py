
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
con = duckdb.connect(str(root / "metropulse.duckdb"))

sql_path = root / "sql" / "marts" / "pickup_zone_metrics.sql"
output_path = root / "data" / "processed" / "pickup_zone_metrics.parquet"

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    con.execute("""
        COPY (
            SELECT *
            FROM mart_pickup_zone_metrics
        )
        TO 'data/processed/pickup_zone_metrics.parquet'
        (FORMAT PARQUET)
    """)

    result = con.execute("""
        SELECT
            COUNT(*) AS zone_month_rows,
            COUNT(DISTINCT pickup_location_id) AS distinct_zones,
            SUM(total_trips) AS total_trips
        FROM read_parquet(?)
    """, [str(output_path)]).fetchdf()

    print("\n=== EXPORTED PICKUP ZONE MART ===\n")
    print(result.to_string(index=False))
    print(f"\nSaved: {output_path}")

finally:
    con.close()
