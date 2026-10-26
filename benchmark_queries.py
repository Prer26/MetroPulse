import duckdb
import time
import json
from pathlib import Path

db = Path("metropulse.duckdb")
con = duckdb.connect(str(db), read_only=True)

queries = {
    "Q1_monthly_full_scan": """
        SELECT source_month,
               COUNT(*) AS trips,
               SUM(total_amount) AS recorded_amount,
               MEDIAN(trip_distance) AS median_distance,
               MEDIAN(duration_minutes) AS median_duration
        FROM int_taxi_trips
        GROUP BY source_month
        ORDER BY source_month
    """,
    "Q2_zone_join_aggregation": """
        SELECT z.Zone,
               COUNT(*) AS trips,
               SUM(t.total_amount) AS recorded_amount,
               AVG(t.trip_distance) AS avg_distance
        FROM int_taxi_trips t
        LEFT JOIN taxi_zone_lookup z
          ON t.PULocationID = z.LocationID
        GROUP BY z.Zone
        ORDER BY trips DESC
    """
}

results = []
for name, sql in queries.items():
    # Warm-up execution
    con.execute(sql).fetchall()

    timings = []
    for _ in range(3):
        start = time.perf_counter()
        con.execute(sql).fetchall()
        timings.append(time.perf_counter() - start)

    results.append({
        "query": name,
        "seconds_each_run": [round(x, 4) for x in timings],
        "median_seconds": round(sorted(timings)[1], 4)
    })

con.close()

Path("reports").mkdir(exist_ok=True)
Path("reports/query_benchmark_before.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print(json.dumps(results, indent=2))
print("\nSaved reports/query_benchmark_before.json")
