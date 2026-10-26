
SELECT
    source_month,
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE passenger_count IS NULL
    ) AS missing_passengers,

    COUNT(*) FILTER (
        WHERE fare_amount < 0
    ) AS negative_fares,

    COUNT(*) FILTER (
        WHERE total_amount < 0
    ) AS negative_totals,

    COUNT(*) FILTER (
        WHERE trip_distance <= 0
           OR trip_distance IS NULL
    ) AS invalid_distances,

    COUNT(*) FILTER (
        WHERE tpep_dropoff_datetime < tpep_pickup_datetime
    ) AS negative_durations,

    COUNT(*) FILTER (
        WHERE tpep_dropoff_datetime = tpep_pickup_datetime
    ) AS zero_durations

FROM stg_taxi_trips
GROUP BY source_month
ORDER BY source_month;
