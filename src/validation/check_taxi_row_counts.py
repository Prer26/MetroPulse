
import duckdb

con = duckdb.connect("metropulse.duckdb")

query = """
SELECT
    COUNT(*) AS all_trips,
    COUNT(*) FILTER (
        WHERE tpep_pickup_datetime >= TIMESTAMP '2024-04-01 00:00:00'
          AND tpep_pickup_datetime < TIMESTAMP '2024-07-01 00:00:00'
    ) AS trips_inside_quarter,
    COUNT(*) FILTER (
        WHERE tpep_pickup_datetime < TIMESTAMP '2024-04-01 00:00:00'
           OR tpep_pickup_datetime >= TIMESTAMP '2024-07-01 00:00:00'
    ) AS trips_outside_quarter,
    MIN(tpep_pickup_datetime) AS earliest_pickup,
    MAX(tpep_pickup_datetime) AS latest_pickup
FROM int_taxi_trips;
"""

print(con.execute(query).fetchdf().to_string(index=False))
con.close()
