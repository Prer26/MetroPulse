
WITH hourly AS (
    SELECT
        hour_start,
        taxi_trips,
        total_ridership,
        precipitation_mm,
        is_rainy_hour,
        EXTRACT(HOUR FROM hour_start) AS hour_of_day,
        CASE
            WHEN EXTRACT(DOW FROM hour_start) IN (0, 6)
                THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type
    FROM read_parquet(
        'data/processed/taxi_transit_weather_hourly.parquet'
    )
),
grouped AS (
    SELECT
        hour_of_day,
        day_type,
        is_rainy_hour,
        COUNT(*) AS hours_observed,
        AVG(taxi_trips) AS avg_taxi_trips,
        AVG(total_ridership) AS avg_subway_ridership
    FROM hourly
    GROUP BY hour_of_day, day_type, is_rainy_hour
)
SELECT
    hour_of_day,
    day_type,
    MAX(hours_observed) FILTER (WHERE is_rainy_hour)
        AS rainy_hours,
    MAX(hours_observed) FILTER (WHERE NOT is_rainy_hour)
        AS non_rainy_hours,
    ROUND(MAX(avg_taxi_trips) FILTER (WHERE is_rainy_hour), 2)
        AS rainy_avg_taxi_trips,
    ROUND(MAX(avg_taxi_trips) FILTER (WHERE NOT is_rainy_hour), 2)
        AS dry_avg_taxi_trips,
    ROUND(
        100.0 * (
            MAX(avg_taxi_trips) FILTER (WHERE is_rainy_hour)
            / NULLIF(
                MAX(avg_taxi_trips) FILTER (WHERE NOT is_rainy_hour),
                0
            ) - 1
        ), 2
    ) AS taxi_pct_difference
FROM grouped
GROUP BY hour_of_day, day_type
HAVING COUNT(*) FILTER (WHERE is_rainy_hour) > 0
   AND COUNT(*) FILTER (WHERE NOT is_rainy_hour) > 0
ORDER BY day_type, hour_of_day;
