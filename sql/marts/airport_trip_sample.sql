
COPY (
    SELECT
        CASE
            WHEN z.Zone IN ('JFK Airport', 'LaGuardia Airport')
            THEN 'Airport'
            ELSE 'Non-airport'
        END AS pickup_group,
        t.total_amount
    FROM int_taxi_trips AS t
    LEFT JOIN read_csv_auto(
        'data/raw/zones/taxi_zone_lookup.csv'
    ) AS z
        ON t.PULocationID = z.LocationID
    WHERE t.total_amount IS NOT NULL
      AND t.total_amount BETWEEN 0 AND 500
) TO 'data/processed/airport_amount_sample.parquet'
(FORMAT PARQUET);
