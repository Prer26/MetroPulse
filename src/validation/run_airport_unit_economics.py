from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "airport_unit_economics.sql"

con = duckdb.connect(str(db_path), read_only=True)

try:
    result = con.execute(
        sql_path.read_text(encoding="utf-8")
    ).fetchdf()

    print("\n=== AIRPORT RECORDED AMOUNT PER MILE ===\n")
    print(result.to_string(index=False))
finally:
    con.close()