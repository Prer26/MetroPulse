import duckdb

con = duckdb.connect("metropulse.duckdb", read_only=True)

path = "data/processed/payment_fare_metrics.parquet"

try:
    print("Mart rows:", con.execute(
        "SELECT COUNT(*) FROM read_parquet(?)",
        [path]
    ).fetchone()[0])

    print("Mart trip count:", con.execute(
        "SELECT SUM(trip_count) FROM read_parquet(?)",
        [path]
    ).fetchone()[0])

finally:
    con.close()
