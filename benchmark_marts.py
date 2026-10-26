import duckdb
import time
import json
from pathlib import Path

con = duckdb.connect("metropulse.duckdb", read_only=True)

queries = {
    "Q1_original_monthly": """
        SELECT source_month, COUNT(*) AS trips,
               SUM(total_amount) AS recorded_amount,
               MEDIAN(trip_distance) AS median_distance,
               MEDIAN(duration_minutes) AS median_duration
        FROM int_taxi_trips
        GROUP BY source_month ORDER BY source_month
    """,
    "Q1_optimized_monthly_mart": """
        SELECT source_month, total_trips AS trips,
               total_recorded_amount AS recorded_amount,
               median_trip_distance_miles AS median_distance,
               median_duration_minutes AS median_duration
        FROM mart_monthly_taxi_metrics
        ORDER BY source_month
    """,
    "Q2_original_zone": """
        SELECT z.Zone, COUNT(*) AS trips,
               SUM(t.total_amount) AS recorded_amount
        FROM int_taxi_trips t
        LEFT JOIN taxi_zone_lookup z
          ON t.PULocationID = z.LocationID
        GROUP BY z.Zone ORDER BY trips DESC
    """,
    "Q2_zone_mart": """
        SELECT pickup_zone AS zone,
               SUM(total_trips) AS trips,
               SUM(total_recorded_amount) AS recorded_amount
        FROM mart_pickup_zone_metrics
        GROUP BY pickup_zone ORDER BY trips DESC
    """
}

results = {}
for name, sql in queries.items():
    con.execute(sql).fetchall()
    timings = []
    for _ in range(3):
        start = time.perf_counter()
        rows = con.execute(sql).fetchall()
        timings.append(time.perf_counter() - start)
    results[name] = {
        "median_seconds": round(sorted(timings)[1], 4),
        "rows_returned": len(rows),
        "runs_seconds": [round(t, 4) for t in timings]
    }

con.close()
Path("reports").mkdir(exist_ok=True)
Path("reports/query_benchmark_after.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print(json.dumps(results, indent=2))
print("\nSaved reports/query_benchmark_after.json")
print("Note: zone comparison uses only shared metrics; average distance is not in the zone mart.")
