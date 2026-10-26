
COPY (
    SELECT
        date_trunc('hour', transit_timestamp) AS hour_start,
        borough,
        SUM(ridership) AS total_ridership,
        SUM(transfers) AS total_transfers,
        COUNT(*) AS source_records,
        COUNT(DISTINCT station_complex_id) AS stations_reporting
    FROM stg_transit_ridership
    WHERE transit_timestamp >= TIMESTAMP '2024-04-01 00:00:00'
      AND transit_timestamp < TIMESTAMP '2024-07-01 00:00:00'
    GROUP BY
        date_trunc('hour', transit_timestamp),
        borough
) TO 'data/processed/hourly_transit_metrics.parquet'
(FORMAT PARQUET);
