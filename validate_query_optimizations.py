import duckdb
import json
import math
import time
from pathlib import Path

con = duckdb.connect("metropulse.duckdb", read_only=True)

checks = {
    "monthly": {
        "before": """
            SELECT source_month, COUNT(*) AS trips,
                   SUM(total_amount) AS amount,
                   MEDIAN(trip_distance) AS median_distance,
                   MEDIAN(duration_minutes) AS median_duration
            FROM int_taxi_trips
            GROUP BY source_month ORDER BY source_month
        """,
        "after": """
            SELECT source_month, total_trips, total_recorded_amount,
                   median_trip_distance_miles, median_duration_minutes
            FROM mart_monthly_taxi_metrics ORDER BY source_month
        """,
        "key": 0
    },
    "zones": {
        "before": """
            SELECT z.Zone, COUNT(*) AS trips, SUM(t.total_amount) AS amount
            FROM int_taxi_trips t
            LEFT JOIN taxi_zone_lookup z ON t.PULocationID = z.LocationID
            GROUP BY z.Zone ORDER BY z.Zone NULLS FIRST
        """,
        "after": """
            SELECT pickup_zone, SUM(total_trips), SUM(total_recorded_amount)
            FROM mart_pickup_zone_metrics
            GROUP BY pickup_zone ORDER BY pickup_zone NULLS FIRST
        """,
        "key": 0
    }
}

report = {}
for name, q in checks.items():
    before = con.execute(q["before"]).fetchall()
    after = con.execute(q["after"]).fetchall()

    # Compare rows by key; compare numeric measures with tolerances.
    left = {str(r[0]): r[1:] for r in before}
    right = {str(r[0]): r[1:] for r in after}
    differences = []
    for key in sorted(set(left) | set(right)):
        if key not in left or key not in right:
            differences.append({"key": key, "reason": "key missing on one side"})
            continue
        for i, (a, b) in enumerate(zip(left[key], right[key])):
            if a is None or b is None:
                same = a is None and b is None
            elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
                same = math.isclose(a, b, rel_tol=1e-7, abs_tol=0.01)
            else:
                same = a == b
            if not same:
                differences.append({
                    "key": key, "measure_index": i,
                    "before": a, "after": b
                })

    report[name] = {
        "before_rows": len(before),
        "after_rows": len(after),
        "values_match": len(differences) == 0,
        "difference_count": len(differences),
        "sample_differences": differences[:10]
    }

con.close()
Path("reports").mkdir(exist_ok=True)
Path("reports/query_result_validation.json").write_text(
    json.dumps(report, indent=2, default=str), encoding="utf-8"
)
print(json.dumps(report, indent=2))
print("\nSaved reports/query_result_validation.json")
