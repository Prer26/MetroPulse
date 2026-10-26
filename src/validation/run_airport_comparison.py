from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "airport_comparison.sql"

con = duckdb.connect(str(db_path), read_only=True)

try:
    sql = sql_path.read_text(encoding="utf-8")
    result = con.execute(sql).fetchdf()

    print("\n=== JFK VS LAGUARDIA ===\n")
    print(result.to_string(index=False))
finally:
    con.close()