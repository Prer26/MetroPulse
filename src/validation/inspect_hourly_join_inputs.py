
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
con = duckdb.connect(str(root / "metropulse.duckdb"))

try:
    print("\n=== TAXI HOURLY MART SCHEMA ===\n")
    print(
        con.execute("""
            DESCRIBE SELECT * FROM mart_hourly_demand
        """).fetchdf().to_string(index=False)
    )

    print("\n=== TAXI HOURLY SAMPLE ===\n")
    print(
        con.execute("""
            SELECT *
            FROM mart_hourly_demand
            ORDER BY ALL
            LIMIT 5
        """).fetchdf().to_string(index=False)
    )

    print("\n=== TRANSIT PARQUET SCHEMA ===\n")
    transit_path = (
        root / "data" / "processed"
        / "hourly_transit_metrics.parquet"
    )

    print(
        con.execute("""
            DESCRIBE SELECT *
            FROM read_parquet(?)
        """, [str(transit_path)]).fetchdf().to_string(index=False)
    )

finally:
    con.close()
