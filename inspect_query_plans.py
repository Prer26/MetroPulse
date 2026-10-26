import duckdb
import json
from pathlib import Path

con = duckdb.connect("metropulse.duckdb", read_only=True)

report = {}

for table in [
    "int_taxi_trips",
    "mart_monthly_taxi_metrics",
    "mart_pickup_zone_metrics",
    "taxi_zone_lookup",
]:
    report[table] = {
        "schema": con.execute(f'DESCRIBE "{table}"').fetchdf().to_dict("records"),
        "row_count": con.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0],
    }

queries = {
    "monthly_full_scan": """
        SELECT source_month, COUNT(*) AS trips,
               SUM(total_amount) AS recorded_amount,
               MEDIAN(trip_distance) AS median_distance,
               MEDIAN(duration_minutes) AS median_duration
        FROM int_taxi_trips
        GROUP BY source_month
        ORDER BY source_month
    """,
    "zone_join_aggregation": """
        SELECT z.Zone, COUNT(*) AS trips,
               SUM(t.total_amount) AS recorded_amount,
               AVG(t.trip_distance) AS avg_distance
        FROM int_taxi_trips t
        LEFT JOIN taxi_zone_lookup z
          ON t.PULocationID = z.LocationID
        GROUP BY z.Zone
        ORDER BY trips DESC
    """
}

for name, sql in queries.items():
    report[name] = con.execute(
        "EXPLAIN ANALYZE " + sql
    ).fetchdf().to_dict("records")

con.close()

Path("reports").mkdir(exist_ok=True)
Path("reports/query_plan_analysis.json").write_text(
    json.dumps(report, indent=2, default=str), encoding="utf-8"
)
print("Saved reports/query_plan_analysis.json")
print("\nExisting mart schemas and row counts:")
for table in ["mart_monthly_taxi_metrics", "mart_pickup_zone_metrics"]:
    print(f"\n{table}:")
    for column in report[table]["schema"]:
        print(f"  {column['column_name']}: {column['column_type']}")
    print("  rows:", report[table]["row_count"])
print("\nQuery plans saved for both baseline queries.")
