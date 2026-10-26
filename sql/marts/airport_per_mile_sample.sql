
COPY (
    SELECT
        z.Zone AS airport,
        t.total_amount / NULLIF(t.trip_distance, 0)
            AS recorded_amount_per_mile
    FROM int_taxi_trips AS t
    JOIN read_csv_auto(
        'data/raw/zones/taxi_zone_lookup.csv'
    ) AS z
        ON t.PULocationID = z.LocationID
    WHERE z.Zone IN ('JFK Airport', 'LaGuardia Airport')
      AND t.trip_distance > 0
      AND t.total_amount BETWEEN 0 AND 500
) TO 'data/processed/airport_per_mile_sample.parquet'
(FORMAT PARQUET);
