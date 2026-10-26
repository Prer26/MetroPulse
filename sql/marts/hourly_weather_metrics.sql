
COPY (
    SELECT
        CAST(time AS TIMESTAMP) AS hour_start,
        CAST("temperature_2m (°C)" AS DOUBLE) AS temperature_c,
        CAST("relative_humidity_2m (%)" AS DOUBLE) AS relative_humidity_pct,
        CAST("precipitation (mm)" AS DOUBLE) AS precipitation_mm,
        CAST("wind_speed_10m (km/h)" AS DOUBLE) AS wind_speed_kmh,
        CAST("precipitation (mm)" AS DOUBLE) > 0 AS is_rainy_hour
    FROM read_csv(
        'data/raw/weather/open-meteo-40.74N74.04W32m.csv',
        skip=2,
        header=true,
        all_varchar=true
    )
    WHERE TRY_CAST(time AS TIMESTAMP) >= TIMESTAMP '2024-04-01 00:00:00'
      AND TRY_CAST(time AS TIMESTAMP) < TIMESTAMP '2024-07-01 00:00:00'
) TO 'data/processed/hourly_weather_metrics.parquet'
(FORMAT PARQUET);
