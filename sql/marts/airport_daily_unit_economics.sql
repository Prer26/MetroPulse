
COPY (
    SELECT
        CAST(t.tpep_pickup_datetime AS DATE) AS pickup_date,
        z.Zone AS airport,
        COUNT(*) AS eligible_trips,
        MEDIAN(
            t.total_amount / NULLIF(t.trip_distance, 0)
        ) AS median_amount_per_mile,
        AVG(
            t.total_amount / NULLIF(t.trip_distance, 0)
        ) AS mean_amount_per_mile
    FROM int_taxi_trips AS t
    JOIN read_csv_auto(
        'data/raw/zones/taxi_zone_lookup.csv'
    ) AS z
        ON t.PULocationID = z.LocationID
    
       WHERE z.Zone IN (
       'JFK Airport',
       'LaGuardia Airport'
    )
  AND t.tpep_pickup_datetime >= TIMESTAMP '2024-04-01 00:00:00'
  AND t.tpep_pickup_datetime <  TIMESTAMP '2024-07-01 00:00:00'
  AND t.trip_distance > 0
  AND t.total_amount BETWEEN 0 AND 500

      AND t.tpep_pickup_datetime IS NOT NULL
      AND t.trip_distance > 0
      AND t.total_amount BETWEEN 0 AND 500
    GROUP BY
        CAST(t.tpep_pickup_datetime AS DATE),
        z.Zone
) TO 'data/processed/airport_daily_unit_economics.parquet'
(FORMAT PARQUET);
