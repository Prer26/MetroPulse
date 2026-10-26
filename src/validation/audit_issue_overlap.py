
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "metropulse.duckdb"
SQL_PATH = PROJECT_ROOT / "sql" / "staging" / "audit_issue_overlap.sql"

con = duckdb.connect(str(DB_PATH), read_only=True)

try:
    sql = SQL_PATH.read_text(encoding="utf-8")
    result = con.execute(sql).fetchdf()

    print("\n=== METROPULSE: DATA QUALITY OVERLAP AUDIT ===\n")
    print(result.to_string(index=False))
finally:
    con.close()
