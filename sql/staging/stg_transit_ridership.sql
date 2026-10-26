
CREATE OR REPLACE VIEW stg_transit_ridership AS
WITH raw AS (
    SELECT *
    FROM read_json(
        'data/raw/transit/mta_subway_2024_q2.jsonl',
        format = 'newline_delimited',
        columns = {
            'transit_timestamp': 'VARCHAR',
            'transit_mode': 'VARCHAR',
            'station_complex_id': 'VARCHAR',
            'station_complex': 'VARCHAR',
            'borough': 'VARCHAR',
            'payment_method': 'VARCHAR',
            'fare_class_category': 'VARCHAR',
            'ridership': 'VARCHAR',
            'transfers': 'VARCHAR',
            'latitude': 'VARCHAR',
            'longitude': 'VARCHAR',
            'georeference': 'STRUCT("type" VARCHAR, coordinates DOUBLE[])'
        }
    )
)
SELECT
    TRY_CAST(transit_timestamp AS TIMESTAMP) AS transit_timestamp,
    transit_mode,
    station_complex_id,
    station_complex,
    borough,
    payment_method,
    fare_class_category,
    TRY_CAST(ridership AS DOUBLE) AS ridership,
    TRY_CAST(transfers AS DOUBLE) AS transfers,
    TRY_CAST(latitude AS DOUBLE) AS latitude,
    TRY_CAST(longitude AS DOUBLE) AS longitude,
    georeference,

    CASE
        WHEN transit_timestamp IS NULL
          OR TRY_CAST(transit_timestamp AS TIMESTAMP) IS NULL
        THEN TRUE ELSE FALSE
    END AS flag_invalid_timestamp,

    CASE
        WHEN ridership IS NULL
          OR TRY_CAST(ridership AS DOUBLE) IS NULL
          OR TRY_CAST(ridership AS DOUBLE) < 0
        THEN TRUE ELSE FALSE
    END AS flag_invalid_ridership,

    CASE
        WHEN transfers IS NULL
          OR TRY_CAST(transfers AS DOUBLE) IS NULL
          OR TRY_CAST(transfers AS DOUBLE) < 0
        THEN TRUE ELSE FALSE
    END AS flag_invalid_transfers

FROM raw;
