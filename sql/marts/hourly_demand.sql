
CREATE OR REPLACE TABLE mart_hourly_demand AS
SELECT
    source_month,
    pickup_hour,
    COUNT(*) AS total_trips,

    ROUND(AVG(total_amount), 2) AS avg_recorded_amount,

    ROUND(
        MEDIAN(duration_minutes),
        2
    ) AS median_duration_minutes,

    COUNT(*) FILTER (
        WHERE trip_distance <= 0
           OR trip_distance IS NULL
    ) AS invalid_distance_trips,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE trip_distance <= 0
               OR trip_distance IS NULL
        ) / COUNT(*),
        2
    ) AS invalid_distance_pct

FROM int_taxi_trips
WHERE pickup_hour BETWEEN 0 AND 23
GROUP BY source_month, pickup_hour
ORDER BY source_month, pickup_hour;
