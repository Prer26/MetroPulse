
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
data_path = (
    root / "data" / "processed"
    / "airport_daily_unit_economics.parquet"
)

con = duckdb.connect(str(db_path), read_only=True)

try:
    print("\n=== DATE RANGE CHECK ===\n")

    print(con.execute("""
        SELECT
            airport,
            MIN(pickup_date) AS first_date,
            MAX(pickup_date) AS last_date,
            COUNT(*) AS daily_rows,
            COUNT(DISTINCT pickup_date) AS distinct_dates,
            COUNT(*) FILTER (
                WHERE pickup_date < DATE '2024-04-01'
                   OR pickup_date > DATE '2024-06-30'
            ) AS dates_outside_period
        FROM read_parquet(?)
        GROUP BY airport
        ORDER BY airport
    """, [str(data_path)]).fetchdf().to_string(index=False))

    print("\n=== DATES OUTSIDE THE STUDY PERIOD ===\n")

    print(con.execute("""
        SELECT airport, pickup_date, eligible_trips
        FROM read_parquet(?)
        WHERE pickup_date < DATE '2024-04-01'
           OR pickup_date > DATE '2024-06-30'
        ORDER BY pickup_date
        LIMIT 20
    """, [str(data_path)]).fetchdf().to_string(index=False))

finally:
    con.close()
