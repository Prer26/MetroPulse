import duckdb

con = duckdb.connect("metropulse.duckdb", read_only=True)

for table in ["int_taxi_trips", "stg_taxi_trips"]:
    print(f"\n{'=' * 55}")
    print(table)
    for row in con.execute(f"DESCRIBE {table}").fetchall():
        print(f"{row[0]}: {row[1]}")

con.close()
