
SELECT
    CASE
        WHEN is_rainy_hour THEN 'Rainy'
        ELSE 'Non-rainy'
    END AS weather_group,
    COUNT(*) AS hours_observed,
    ROUND(AVG(taxi_trips), 2) AS avg_taxi_trips_per_hour,
    ROUND(MEDIAN(taxi_trips), 2) AS median_taxi_trips_per_hour,
    ROUND(AVG(total_ridership), 2) AS avg_subway_ridership_per_hour,
    ROUND(AVG(precipitation_mm), 3) AS avg_precipitation_mm,
    ROUND(AVG(temperature_c), 2) AS avg_temperature_c
FROM read_parquet(
    'data/processed/taxi_transit_weather_hourly.parquet'
)
GROUP BY is_rainy_hour
ORDER BY is_rainy_hour DESC;
