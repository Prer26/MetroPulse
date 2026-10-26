
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[2]
SQL_FILE = ROOT / "sql" / "staging" / "stg_taxi_trips.sql"

con = duckdb.connect(str(ROOT / "metropulse.duckdb"))

try:
    sql = SQL_FILE.read_text(encoding="utf-8")
    con.execute(sql)

    total = con.execute(
        "SELECT COUNT(*) FROM stg_taxi_trips"
    ).fetchone()[0]

    print("Taxi staging view created successfully!")
    print(f"Total rows: {total:,}")

    print("\nRows by source month:")
    result = con.execute("""
        SELECT source_month, COUNT(*) AS row_count
        FROM stg_taxi_trips
        GROUP BY source_month
        ORDER BY source_month
    """).fetchall()

    for month, count in result:
        print(f"{month}: {count:,}")

finally:
    con.close()
