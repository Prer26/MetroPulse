
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "staging" / "audit_quality_by_month.sql"

con = duckdb.connect(str(db_path), read_only=True)

try:
    result = con.execute(
        sql_path.read_text(encoding="utf-8")
    ).fetchdf()

    print("\n=== DATA QUALITY BY MONTH ===\n")
    print(result.to_string(index=False))
finally:
    con.close()
