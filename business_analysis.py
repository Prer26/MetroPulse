
import duckdb

DB_PATH = "metropulse.duckdb"

con = duckdb.connect(DB_PATH, read_only=True)

def show(title, query):
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)
    result = con.execute(query).fetchdf()
    print(result.to_string(index=False))
    return result


# 1. Airport opportunity
show(
    "ANALYSIS 1: AIRPORT BUSINESS OPPORTUNITY",
    """
    SELECT
        pickup_group,
        total_trips,
        ROUND(trip_share_pct, 2) AS trip_share_pct,
        ROUND(total_recorded_amount, 2) AS recorded_amount,
        ROUND(avg_recorded_amount_per_trip, 2) AS avg_amount_per_trip,
        ROUND(median_recorded_amount, 2) AS median_amount,
        ROUND(avg_distance_miles, 2) AS avg_distance_miles,
        ROUND(avg_duration_minutes, 2) AS avg_duration_minutes,
        ROUND(invalid_distance_pct, 2) AS invalid_distance_pct
    FROM mart_airport_metrics
    ORDER BY total_trips DESC
    """
)


# 2. Highest-volume pickup zones across the full quarter
show(
    "ANALYSIS 2A: TOP PICKUP ZONES BY TRIP VOLUME",
    """
    SELECT
        pickup_location_id,
        pickup_borough,
        pickup_zone,
        SUM(total_trips) AS q2_trips,
        ROUND(SUM(total_recorded_amount), 2) AS recorded_amount,
        ROUND(
            SUM(total_recorded_amount) / NULLIF(SUM(total_trips), 0),
            2
        ) AS avg_amount_per_trip,
        ROUND(
            100.0 * SUM(invalid_distance_trips)
            / NULLIF(SUM(total_trips), 0),
            2
        ) AS invalid_distance_pct
    FROM mart_pickup_zone_metrics
    GROUP BY pickup_location_id, pickup_borough, pickup_zone
    ORDER BY q2_trips DESC
    LIMIT 15
    """
)


# 3. Check whether the strongest zones are consistent across months
show(
    "ANALYSIS 2B: MONTHLY PERFORMANCE OF TOP ZONES",
    """
    WITH zone_totals AS (
        SELECT
            pickup_location_id,
            SUM(total_trips) AS q2_trips
        FROM mart_pickup_zone_metrics
        GROUP BY pickup_location_id
    ),
    top_zones AS (
        SELECT pickup_location_id
        FROM zone_totals
        ORDER BY q2_trips DESC
        LIMIT 10
    )
    SELECT
        m.pickup_zone,
        m.pickup_borough,
        m.source_month,
        m.total_trips,
        ROUND(m.avg_recorded_amount, 2) AS avg_amount_per_trip,
        ROUND(m.invalid_distance_pct, 2) AS invalid_distance_pct
    FROM mart_pickup_zone_metrics m
    JOIN top_zones z
        ON m.pickup_location_id = z.pickup_location_id
    ORDER BY m.pickup_zone, m.source_month
    """
)


# 4. Strongest hours by volume
show(
    "ANALYSIS 2C: QUARTERLY HOURLY DEMAND",
    """
    SELECT
        pickup_hour,
        SUM(total_trips) AS q2_trips,
        ROUND(AVG(avg_recorded_amount), 2) AS avg_monthly_amount_per_trip,
        ROUND(AVG(median_duration_minutes), 2) AS avg_monthly_median_duration,
        SUM(invalid_distance_trips) AS invalid_distance_trips,
        ROUND(AVG(invalid_distance_pct), 2) AS avg_invalid_distance_pct
    FROM mart_hourly_demand
    GROUP BY pickup_hour
    ORDER BY q2_trips DESC
    """
)


# 5. Check if demand patterns change by month
show(
    "ANALYSIS 2D: HOURLY DEMAND BY MONTH",
    """
    SELECT
        source_month,
        pickup_hour,
        total_trips,
        ROUND(avg_recorded_amount, 2) AS avg_recorded_amount,
        ROUND(median_duration_minutes, 2) AS median_duration_minutes
    FROM mart_hourly_demand
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY source_month
        ORDER BY total_trips DESC
    ) <= 8
    ORDER BY source_month, total_trips DESC
    """
)


# 6. Overall monthly business context
show(
    "QUARTERLY BUSINESS BASELINE",
    """
    SELECT
        source_month,
        total_trips,
        ROUND(total_recorded_amount, 2) AS recorded_amount,
        ROUND(avg_amount_per_trip, 2) AS avg_amount_per_trip,
        ROUND(avg_duration_minutes, 2) AS avg_duration_minutes,
        ROUND(median_duration_minutes, 2) AS median_duration_minutes,
        invalid_distance_trips,
        negative_fare_trips
    FROM mart_monthly_taxi_metrics
    ORDER BY source_month
    """
)

con.close()
print("\nAnalysis complete. Database was opened read-only.")
