
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"

con = duckdb.connect(str(db_path))

try:
    print("\n=== DUCKDB VERSION ===")
    print(con.execute("SELECT version()").fetchone()[0])

    print("\n=== JSON READER FUNCTION ===")
    print(
        con.execute("""
            SELECT function_name, function_type
            FROM duckdb_functions()
            WHERE function_name IN (
                'read_json_auto',
                'read_json'
            )
            ORDER BY function_name
        """).fetchdf().to_string(index=False)
    )
finally:
    con.close()
