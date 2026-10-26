
-- MetroPulse: Yellow Taxi Staging View
-- Period: April 1 - June 30, 2024
-- Original Parquet files remain unchanged.

CREATE OR REPLACE VIEW stg_taxi_trips AS

SELECT
    *,
    '2024-04' AS source_month
FROM read_parquet('data/raw/taxi/yellow_tripdata_2024-04.parquet')

UNION ALL

SELECT
    *,
    '2024-05' AS source_month
FROM read_parquet('data/raw/taxi/yellow_tripdata_2024-05.parquet')

UNION ALL

SELECT
    *,
    '2024-06' AS source_month
FROM read_parquet('data/raw/taxi/yellow_tripdata_2024-06.parquet');
