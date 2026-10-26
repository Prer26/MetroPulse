
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "staging" / "stg_transit_ridership.sql"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    print("\n=== TRANSIT STAGING VIEW CREATED ===\n")

    print(con.execute("""
        SELECT
            COUNT(*) AS total_rows,
            MIN(transit_timestamp) AS first_timestamp,
            MAX(transit_timestamp) AS last_timestamp,
            COUNT(*) FILTER (
                WHERE flag_invalid_timestamp
            ) AS invalid_timestamps,
            COUNT(*) FILTER (
                WHERE flag_invalid_ridership
            ) AS invalid_ridership,
            COUNT(*) FILTER (
                WHERE flag_invalid_transfers
            ) AS invalid_transfers
        FROM stg_transit_ridership
    """).fetchdf().to_string(index=False))

finally:
    con.close()
