
import duckdb

# Connect to our existing MetroPulse database
con = duckdb.connect("metropulse.duckdb")

# Inspect the April 2024 taxi dataset
file_path = "data/raw/taxi/yellow_tripdata_2024-04.parquet"

print("\n--- COLUMN NAMES AND DATA TYPES ---")
print(con.execute(f"DESCRIBE SELECT * FROM read_parquet('{file_path}')").fetchdf())

print("\n--- TOTAL ROWS IN APRIL ---")
print(con.execute(f"SELECT COUNT(*) AS total_rows FROM read_parquet('{file_path}')").fetchdf())

con.close()
