
CREATE OR REPLACE TABLE mart_pickup_zone_metrics AS
SELECT
    t.source_month,
    t.PULocationID AS pickup_location_id,
    z.Borough AS pickup_borough,
    z.Zone AS pickup_zone,
    COUNT(*) AS total_trips,
    ROUND(SUM(t.total_amount), 2) AS total_recorded_amount,
    ROUND(AVG(t.total_amount), 2) AS avg_recorded_amount,
    ROUND(MEDIAN(t.trip_distance), 2) AS median_distance_miles,
    COUNT(*) FILTER (
        WHERE t.trip_distance <= 0
           OR t.trip_distance IS NULL
    ) AS invalid_distance_trips,
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
GROUP BY
    t.source_month,
    t.PULocationID,
    z.Borough,
    z.Zone;
