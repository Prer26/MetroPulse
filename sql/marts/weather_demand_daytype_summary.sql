
WITH hourly AS (
    SELECT
        hour_start,
        taxi_trips,
        is_rainy_hour,
        CASE
            WHEN EXTRACT(DOW FROM hour_start) IN (0, 6)
                THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type
    FROM read_parquet(
        'data/processed/taxi_transit_weather_hourly.parquet'
    )
),
summary AS (
    SELECT
        day_type,
        is_rainy_hour,
        COUNT(*) AS hours_observed,
        AVG(taxi_trips) AS avg_taxi_trips
    FROM hourly
    GROUP BY day_type, is_rainy_hour
)
SELECT
    day_type,
    MAX(hours_observed) FILTER (WHERE is_rainy_hour)
        AS rainy_hours,
    MAX(hours_observed) FILTER (WHERE NOT is_rainy_hour)
        AS dry_hours,
    ROUND(
        MAX(avg_taxi_trips) FILTER (WHERE is_rainy_hour), 2
    ) AS rainy_avg_taxi_trips,
    ROUND(
        MAX(avg_taxi_trips) FILTER (WHERE NOT is_rainy_hour), 2
    ) AS dry_avg_taxi_trips,
    ROUND(
        100.0 * (
            MAX(avg_taxi_trips) FILTER (WHERE is_rainy_hour)
            / NULLIF(
                MAX(avg_taxi_trips) FILTER (WHERE NOT is_rainy_hour),
                0
            ) - 1
        ), 2
    ) AS pct_difference
FROM summary
GROUP BY day_type
ORDER BY day_type;
