
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
transit_file = (
    root / "data" / "raw" / "transit"
    / "mta_subway_2024_q2.jsonl"
)

con = duckdb.connect(str(db_path))

try:
    print("\n=== TRANSIT SCHEMA ===\n")

    schema = con.execute("""
        DESCRIBE
        SELECT *
        FROM read_json_auto(?, format = 'newline_delimited')
        LIMIT 1000
    """, [str(transit_file)]).fetchdf()

    print(schema.to_string(index=False))

    print("\n=== SAMPLE RECORDS ===\n")

    sample = con.execute("""
        SELECT *
        FROM read_json_auto(?, format = 'newline_delimited')
        LIMIT 5
    """, [str(transit_file)]).fetchdf()

    print(sample.to_string(index=False))

finally:
    con.close()
