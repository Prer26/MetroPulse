
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "hourly_demand.sql"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    print("\n=== HOURLY TAXI DEMAND ===\n")

    print(con.execute("""
        SELECT *
        FROM mart_hourly_demand
        ORDER BY source_month, pickup_hour
    """).fetchdf().to_string(index=False))

    print("\n=== BUSIEST HOURS BY MONTH ===\n")

    print(con.execute("""
        SELECT *
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (
                       PARTITION BY source_month
                       ORDER BY total_trips DESC
                   ) AS hour_rank
            FROM mart_hourly_demand
        )
        WHERE hour_rank <= 3
        ORDER BY source_month, hour_rank
    """).fetchdf().to_string(index=False))

finally:
    con.close()
