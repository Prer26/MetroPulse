
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = root / "sql" / "marts" / "airport_trip_sample.sql"

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    sample_path = root / "data" / "processed" / "airport_amount_sample.parquet"

    print("Airport comparison dataset created.")
    print(
        con.execute(
            "SELECT pickup_group, COUNT(*) AS rows FROM read_parquet(?) GROUP BY 1 ORDER BY 1",
            [str(sample_path)]
        ).fetchdf().to_string(index=False)
    )
finally:
    con.close()
