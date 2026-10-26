SELECT
    z.Zone AS airport,
    t.source_month,
    COUNT(*) AS total_trips,
    ROUND(AVG(t.total_amount), 2) AS avg_recorded_amount,
    ROUND(MEDIAN(t.total_amount), 2) AS median_recorded_amount,
    ROUND(AVG(t.trip_distance), 2) AS avg_distance_miles,
    ROUND(MEDIAN(t.trip_distance), 2) AS median_distance_miles,
    ROUND(MEDIAN(t.duration_minutes), 2) AS median_duration_minutes,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE t.trip_distance <= 0 OR t.trip_distance IS NULL
        ) / COUNT(*),
        2
    ) AS invalid_distance_pct
FROM int_taxi_trips AS t
JOIN read_csv_auto(
    'data/raw/zones/taxi_zone_lookup.csv'
) AS z
    ON t.PULocationID = z.LocationID
WHERE z.Zone IN ('JFK Airport', 'LaGuardia Airport')
GROUP BY z.Zone, t.source_month
ORDER BY z.Zone, t.source_month;