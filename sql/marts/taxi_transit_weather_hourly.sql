
COPY (
    SELECT
        t.hour_start,
        t.taxi_trips,
        t.avg_recorded_amount,
        t.median_duration_minutes,
        t.invalid_distance_trips,
        s.total_ridership,
        s.total_transfers,
        w.temperature_c,
        w.relative_humidity_pct,
        w.precipitation_mm,
        w.wind_speed_kmh,
        w.is_rainy_hour
    FROM read_parquet(
        'data/processed/taxi_transit_hourly_comparison.parquet'
    ) AS t
    INNER JOIN read_parquet(
        'data/processed/hourly_weather_metrics.parquet'
    ) AS w
        ON t.hour_start = w.hour_start
    INNER JOIN (
        SELECT
            hour_start,
            SUM(total_ridership) AS total_ridership,
            SUM(total_transfers) AS total_transfers
        FROM read_parquet(
            'data/processed/hourly_transit_metrics.parquet'
        )
        GROUP BY hour_start
    ) AS s
        ON t.hour_start = s.hour_start
) TO 'data/processed/taxi_transit_weather_hourly.parquet'
(FORMAT PARQUET);
