
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "monthly_taxi_metrics.sql"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    print("\n=== METROPULSE MONTHLY TAXI METRICS ===\n")
    print(
        con.execute("""
            SELECT *
            FROM mart_monthly_taxi_metrics
            ORDER BY source_month
        """).fetchdf().to_string(index=False)
    )
finally:
    con.close()
