
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "airport_per_mile_sample.sql"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    sample_path = root / "data" / "processed" / "airport_per_mile_sample.parquet"

    print("\n=== AIRPORT AMOUNT-PER-MILE DATA ===\n")
    print(
        con.execute("""
            SELECT
                airport,
                COUNT(*) AS eligible_trips,
                ROUND(MEDIAN(recorded_amount_per_mile), 3)
                    AS median_amount_per_mile
            FROM read_parquet(?)
            GROUP BY airport
            ORDER BY airport
        """, [str(sample_path)]).fetchdf().to_string(index=False)
    )
finally:
    con.close()
