
CREATE OR REPLACE VIEW int_taxi_trips AS
SELECT
    *,
    
    CAST(tpep_pickup_datetime AS DATE) AS pickup_date,
    EXTRACT(HOUR FROM tpep_pickup_datetime) AS pickup_hour,
    EXTRACT(DOW FROM tpep_pickup_datetime) AS pickup_day_of_week,

    DATE_DIFF(
        'second',
        tpep_pickup_datetime,
        tpep_dropoff_datetime
    ) / 60.0 AS duration_minutes,

    CASE
        WHEN trip_distance > 0
        THEN fare_amount / trip_distance
        ELSE NULL
    END AS fare_per_mile,

    CASE
        WHEN trip_distance > 0
         AND tpep_dropoff_datetime > tpep_pickup_datetime
        THEN trip_distance /
             (DATE_DIFF(
                 'second',
                 tpep_pickup_datetime,
                 tpep_dropoff_datetime
             ) / 3600.0)
        ELSE NULL
    END AS average_speed_mph,

    CASE
        WHEN passenger_count IS NULL THEN TRUE
        ELSE FALSE
    END AS has_missing_passenger_count,

    CASE
        WHEN trip_distance <= 0 OR trip_distance IS NULL
        THEN TRUE
        ELSE FALSE
    END AS has_invalid_distance,

    CASE
        WHEN fare_amount < 0 THEN TRUE
        ELSE FALSE
    END AS has_negative_fare,

    CASE
        WHEN tpep_dropoff_datetime < tpep_pickup_datetime
        THEN TRUE
        ELSE FALSE
    END AS has_negative_duration

FROM stg_taxi_trips;
