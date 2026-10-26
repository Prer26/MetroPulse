
CREATE OR REPLACE TABLE mart_monthly_taxi_metrics AS
SELECT
    source_month,
    COUNT(*) AS total_trips,

    SUM(passenger_count) AS recorded_passengers,
    COUNT(*) FILTER (
        WHERE passenger_count IS NULL
    ) AS trips_missing_passenger_count,

    ROUND(SUM(fare_amount), 2) AS total_base_fare,
    ROUND(SUM(total_amount), 2) AS total_recorded_amount,
    ROUND(AVG(total_amount), 2) AS avg_amount_per_trip,
    ROUND(AVG(fare_amount), 2) AS avg_base_fare,

    ROUND(AVG(trip_distance), 2) AS avg_trip_distance_miles,
    ROUND(MEDIAN(trip_distance), 2) AS median_trip_distance_miles,

    ROUND(AVG(duration_minutes), 2) AS avg_duration_minutes,
    ROUND(MEDIAN(duration_minutes), 2) AS median_duration_minutes,

    ROUND(SUM(tip_amount), 2) AS total_tips,
    ROUND(AVG(tip_amount), 2) AS avg_tip_per_trip,

    COUNT(*) FILTER (
        WHERE trip_distance <= 0 OR trip_distance IS NULL
    ) AS invalid_distance_trips,

    COUNT(*) FILTER (
        WHERE duration_minutes <= 0
    ) AS nonpositive_duration_trips,

    COUNT(*) FILTER (
        WHERE fare_amount < 0
    ) AS negative_fare_trips

FROM int_taxi_trips
GROUP BY source_month
ORDER BY source_month;
