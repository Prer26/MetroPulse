
COPY (
    WITH scenarios AS (
        SELECT 500 AS amount_cap
        UNION ALL SELECT 300
        UNION ALL SELECT 200
    ),
    daily AS (
        SELECT
            s.amount_cap,
            CAST(t.tpep_pickup_datetime AS DATE) AS pickup_date,
            z.Zone AS airport,
            MEDIAN(
                t.total_amount / NULLIF(t.trip_distance, 0)
            ) AS median_amount_per_mile
        FROM int_taxi_trips AS t
        JOIN read_csv_auto(
            'data/raw/zones/taxi_zone_lookup.csv'
        ) AS z
            ON t.PULocationID = z.LocationID
        CROSS JOIN scenarios AS s
        WHERE z.Zone IN (
            'JFK Airport',
            'LaGuardia Airport'
        )
          AND t.tpep_pickup_datetime >= TIMESTAMP '2024-04-01 00:00:00'
          AND t.tpep_pickup_datetime <  TIMESTAMP '2024-07-01 00:00:00'
          AND t.trip_distance > 0
          AND t.total_amount BETWEEN 0 AND s.amount_cap
        GROUP BY
            s.amount_cap,
            CAST(t.tpep_pickup_datetime AS DATE),
            z.Zone
    )
    SELECT
        amount_cap,
        pickup_date,
        MAX(median_amount_per_mile)
            FILTER (WHERE airport = 'JFK Airport') AS jfk_median,
        MAX(median_amount_per_mile)
            FILTER (WHERE airport = 'LaGuardia Airport') AS lga_median,
        MAX(median_amount_per_mile)
            FILTER (WHERE airport = 'LaGuardia Airport')
        -
        MAX(median_amount_per_mile)
            FILTER (WHERE airport = 'JFK Airport') AS difference
    FROM daily
    GROUP BY amount_cap, pickup_date
    HAVING COUNT(DISTINCT airport) = 2
) TO 'data/processed/airport_sensitivity.parquet'
(FORMAT PARQUET);
