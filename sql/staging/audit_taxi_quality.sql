
-- MetroPulse: Initial Taxi Data Quality Audit
-- Investigate anomalies before deciding how to handle them.

-- 1. Missing pickup or drop-off timestamps
SELECT
    'missing_timestamps' AS issue,
    COUNT(*) AS affected_rows
FROM stg_taxi_trips
WHERE tpep_pickup_datetime IS NULL
   OR tpep_dropoff_datetime IS NULL

UNION ALL

-- 2. Drop-off occurs before pickup
SELECT
    'negative_duration' AS issue,
    COUNT(*) AS affected_rows
FROM stg_taxi_trips
WHERE tpep_dropoff_datetime < tpep_pickup_datetime

UNION ALL

-- 3. Zero or negative trip distance
SELECT
    'nonpositive_distance' AS issue,
    COUNT(*) AS affected_rows
FROM stg_taxi_trips
WHERE trip_distance <= 0 OR trip_distance IS NULL

UNION ALL

-- 4. Negative fare amount
SELECT
    'negative_fare' AS issue,
    COUNT(*) AS affected_rows
FROM stg_taxi_trips
WHERE fare_amount < 0

UNION ALL

-- 5. Negative total amount
SELECT
    'negative_total' AS issue,
    COUNT(*) AS affected_rows
FROM stg_taxi_trips
WHERE total_amount < 0

UNION ALL

-- 6. Missing passenger count
SELECT
    'missing_passenger_count' AS issue,
    COUNT(*) AS affected_rows
FROM stg_taxi_trips
WHERE passenger_count IS NULL

UNION ALL

-- 7. Zero passenger count
SELECT
    'zero_passenger_count' AS issue,
    COUNT(*) AS affected_rows
FROM stg_taxi_trips
WHERE passenger_count = 0

UNION ALL

-- 8. Pickup and drop-off timestamps are identical
SELECT
    'zero_duration' AS issue,
    COUNT(*) AS affected_rows
FROM stg_taxi_trips
WHERE tpep_dropoff_datetime = tpep_pickup_datetime

ORDER BY issue;
