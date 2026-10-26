
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[2]
SQL_FILE = ROOT / "sql" / "staging" / "audit_taxi_quality.sql"

con = duckdb.connect(str(ROOT / "metropulse.duckdb"))

try:
    sql = SQL_FILE.read_text(encoding="utf-8")
    result = con.execute(sql).fetchdf()

    total = con.execute(
        "SELECT COUNT(*) FROM stg_taxi_trips"
    ).fetchone()[0]

    print(f"Total records audited: {total:,}")
    print("\nINITIAL DATA QUALITY RESULTS")
    print(result.to_string(index=False))

    result["affected_pct"] = (
        result["affected_rows"] / total * 100
    ).round(3)

    print("\nISSUE PERCENTAGES")
    print(result.to_string(index=False))

finally:
    con.close()
