
CREATE OR REPLACE TABLE mart_airport_metrics AS
SELECT
    CASE
        WHEN z.Zone IN ('JFK Airport', 'LaGuardia Airport')
        THEN 'Airport'
        ELSE 'Non-airport'
    END AS pickup_group,

    COUNT(*) AS total_trips,

    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS trip_share_pct,

    ROUND(SUM(t.total_amount), 2) AS total_recorded_amount,

    ROUND(AVG(t.total_amount), 2) AS avg_recorded_amount_per_trip,

    ROUND(MEDIAN(t.total_amount), 2) AS median_recorded_amount,

    ROUND(AVG(t.trip_distance), 2) AS avg_distance_miles,

    ROUND(MEDIAN(t.trip_distance), 2) AS median_distance_miles,

    ROUND(AVG(t.duration_minutes), 2) AS avg_duration_minutes,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE t.trip_distance <= 0
               OR t.trip_distance IS NULL
        ) / COUNT(*),
        2
    ) AS invalid_distance_pct

FROM int_taxi_trips AS t
LEFT JOIN read_csv_auto(
    'data/raw/zones/taxi_zone_lookup.csv'
) AS z
    ON t.PULocationID = z.LocationID

GROUP BY 1
ORDER BY total_trips DESC;
