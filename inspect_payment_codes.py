import duckdb

con = duckdb.connect("metropulse.duckdb", read_only=True)

print("\nPAYMENT TYPES")
print(con.execute("""
    SELECT payment_type, COUNT(*) AS trips
    FROM int_taxi_trips
    GROUP BY payment_type
    ORDER BY payment_type
""").fetchdf().to_string(index=False))

print("\nZONE MAPPING TABLES")
print(con.execute("SHOW TABLES").fetchdf().to_string(index=False))

con.close()
