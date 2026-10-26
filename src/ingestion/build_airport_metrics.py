
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "airport_metrics.sql"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    print("\n=== AIRPORT VS NON-AIRPORT PICKUPS ===\n")
    print(
        con.execute("""
            SELECT *
            FROM mart_airport_metrics
        """).fetchdf().to_string(index=False)
    )
finally:
    con.close()
