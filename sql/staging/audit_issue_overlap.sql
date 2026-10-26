
WITH flagged AS (
    SELECT
        *,
        passenger_count IS NULL AS missing_passenger,
        fare_amount < 0 AS negative_fare,
        total_amount < 0 AS negative_total,
        trip_distance <= 0
            OR trip_distance IS NULL AS invalid_distance,
        tpep_dropoff_datetime < tpep_pickup_datetime
            AS negative_duration,
        tpep_dropoff_datetime = tpep_pickup_datetime
            AS zero_duration,
        passenger_count = 0 AS zero_passengers
    FROM stg_taxi_trips
)
SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE missing_passenger
           OR negative_fare
           OR negative_total
           OR invalid_distance
           OR negative_duration
           OR zero_duration
           OR zero_passengers
    ) AS rows_with_any_flag,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE missing_passenger
               OR negative_fare
               OR negative_total
               OR invalid_distance
               OR negative_duration
               OR zero_duration
               OR zero_passengers
        ) / COUNT(*),
        3
    ) AS pct_with_any_flag,

    COUNT(*) FILTER (
        WHERE negative_fare AND negative_total
    ) AS negative_fare_and_total,

    COUNT(*) FILTER (
        WHERE missing_passenger AND invalid_distance
    ) AS missing_passenger_and_invalid_distance,

    COUNT(*) FILTER (
        WHERE negative_duration OR zero_duration
    ) AS invalid_or_zero_duration

FROM flagged;
