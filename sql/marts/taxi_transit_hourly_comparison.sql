
COPY (
    WITH transit_hourly AS (
        SELECT
            hour_start,
            SUM(total_ridership) AS total_ridership,
            SUM(total_transfers) AS total_transfers,
            SUM(source_records) AS transit_source_records
        FROM read_parquet(
            'data/processed/hourly_transit_metrics.parquet'
        )
        GROUP BY hour_start
    ),
    taxi_hourly AS (
        SELECT *
        FROM read_parquet(
            'data/processed/taxi_hourly_comparison.parquet'
        )
    )
    SELECT
        t.hour_start,
        t.taxi_trips,
        t.avg_recorded_amount,
        t.median_duration_minutes,
        t.invalid_distance_trips,
        s.total_ridership,
        s.total_transfers,
        s.transit_source_records
    FROM taxi_hourly AS t
    INNER JOIN transit_hourly AS s
        ON t.hour_start = s.hour_start
    ORDER BY t.hour_start
) TO 'data/processed/taxi_transit_hourly_comparison.parquet'
(FORMAT PARQUET);
