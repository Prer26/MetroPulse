
import duckdb
from pathlib import Path

con = duckdb.connect("metropulse.duckdb")

files = sorted(
    Path("data/raw/taxi").glob("yellow_tripdata_2024-*.parquet")
)

for file in files:
    print(f"\n{'=' * 50}")
    print(f"FILE: {file.name}")

    row_count = con.execute(
        "SELECT COUNT(*) FROM read_parquet(?)",
        [str(file)]
    ).fetchone()[0]

    print(f"ROWS: {row_count:,}")

print("\nAPRIL DATASET SCHEMA")
april_file = "data/raw/taxi/yellow_tripdata_2024-04.parquet"

schema = con.execute(
    "DESCRIBE SELECT * FROM read_parquet(?)",
    [april_file]
).fetchall()

for column_name, column_type, *_ in schema:
    print(f"{column_name:<30} {column_type}")

con.close()
print("\nInspection complete!")
