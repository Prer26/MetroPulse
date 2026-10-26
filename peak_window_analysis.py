
import duckdb

con = duckdb.connect("metropulse.duckdb", read_only=True)

queries = [
    (
        "A. TOP ZONES DURING THE 4 PM–7 PM WINDOW",
        """
        SELECT
            t.PULocationID AS zone_id,
            z.Borough AS borough,
            z.Zone AS zone,
            COUNT(*) AS trips,
            ROUND(SUM(t.total_amount), 2) AS recorded_amount,
            ROUND(AVG(t.total_amount), 2) AS avg_amount_per_trip,
            ROUND(AVG(t.duration_minutes), 2) AS avg_duration_minutes,
            ROUND(
                100.0 * COUNT(*) FILTER (
                    WHERE t.has_invalid_distance
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS invalid_distance_pct
        FROM int_taxi_trips t
        LEFT JOIN taxi_zone_lookup z
            ON t.PULocationID = z.LocationID
        WHERE t.pickup_hour BETWEEN 16 AND 18
        GROUP BY t.PULocationID, z.Borough, z.Zone
        ORDER BY trips DESC
        LIMIT 15
        """
    ),
    (
        "B. TOP ZONE-HOUR COMBINATIONS",
        """
        SELECT
            t.pickup_hour,
            t.PULocationID AS zone_id,
            z.Borough AS borough,
            z.Zone AS zone,
            COUNT(*) AS trips,
            ROUND(AVG(t.total_amount), 2) AS avg_amount_per_trip,
            ROUND(AVG(t.duration_minutes), 2) AS avg_duration_minutes
        FROM int_taxi_trips t
        LEFT JOIN taxi_zone_lookup z
            ON t.PULocationID = z.LocationID
        WHERE t.pickup_hour BETWEEN 16 AND 18
        GROUP BY t.pickup_hour, t.PULocationID, z.Borough, z.Zone
        ORDER BY trips DESC
        LIMIT 20
        """
    ),
    (
        "C. MONTHLY CONSISTENCY FOR THE PEAK-WINDOW LEADERS",
        """
        WITH peak_zones AS (
            SELECT PULocationID
            FROM int_taxi_trips
            WHERE pickup_hour BETWEEN 16 AND 18
            GROUP BY PULocationID
            ORDER BY COUNT(*) DESC
            LIMIT 10
        )
        SELECT
            t.source_month,
            t.PULocationID AS zone_id,
            z.Borough AS borough,
            z.Zone AS zone,
            COUNT(*) AS trips,
            ROUND(AVG(t.total_amount), 2) AS avg_amount_per_trip
        FROM int_taxi_trips t
        JOIN peak_zones p
            ON t.PULocationID = p.PULocationID
        LEFT JOIN taxi_zone_lookup z
            ON t.PULocationID = z.LocationID
        WHERE t.pickup_hour BETWEEN 16 AND 18
        GROUP BY
            t.source_month,
            t.PULocationID,
            z.Borough,
            z.Zone
        ORDER BY z.Zone, t.source_month
        """
    )
]

for title, query in queries:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)
    print(con.execute(query).fetchdf().to_string(index=False))

con.close()
print("\nAnalysis complete. Database remains unchanged.")
