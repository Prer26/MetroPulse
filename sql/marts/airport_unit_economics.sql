SELECT
    z.Zone AS airport,
    t.source_month,

    COUNT(*) AS total_pickup_trips,

    COUNT(*) FILTER (
        WHERE t.trip_distance > 0
          AND t.total_amount IS NOT NULL
    ) AS trips_eligible_for_amount_per_mile,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE t.trip_distance <= 0
               OR t.trip_distance IS NULL
        ) / COUNT(*),
        2
    ) AS invalid_distance_pct,

    ROUND(
        SUM(t.total_amount) FILTER (
            WHERE t.trip_distance > 0
              AND t.total_amount IS NOT NULL
        )
        /
        NULLIF(
            SUM(t.trip_distance) FILTER (
                WHERE t.trip_distance > 0
                  AND t.total_amount IS NOT NULL
            ),
            0
        ),
        2
    ) AS recorded_amount_per_mile,

    ROUND(
        MEDIAN(
            t.total_amount / NULLIF(t.trip_distance, 0)
        ) FILTER (
            WHERE t.trip_distance > 0
              AND t.total_amount IS NOT NULL
        ),
        2
    ) AS median_recorded_amount_per_mile

FROM int_taxi_trips AS t
JOIN read_csv_auto(
    'data/raw/zones/taxi_zone_lookup.csv'
) AS z
    ON t.PULocationID = z.LocationID

WHERE z.Zone IN ('JFK Airport', 'LaGuardia Airport')

GROUP BY z.Zone, t.source_month
ORDER BY t.source_month, z.Zone;