
COPY (
    SELECT
        date_trunc('hour', tpep_pickup_datetime) AS hour_start,
        COUNT(*) AS taxi_trips,
        AVG(total_amount) AS avg_recorded_amount,
        MEDIAN(duration_minutes) AS median_duration_minutes,
        COUNT(*) FILTER (
            WHERE has_invalid_distance
        ) AS invalid_distance_trips
    FROM int_taxi_trips
    WHERE tpep_pickup_datetime >= TIMESTAMP '2024-04-01 00:00:00'
      AND tpep_pickup_datetime < TIMESTAMP '2024-07-01 00:00:00'
    GROUP BY date_trunc('hour', tpep_pickup_datetime)
) TO 'data/processed/taxi_hourly_comparison.parquet'
(FORMAT PARQUET);
