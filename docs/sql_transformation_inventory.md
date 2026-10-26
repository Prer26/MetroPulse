# SQL Transformation Inventory

- SQL files discovered: **24**
- Build scripts discovered: **15**

A file count alone does not prove that every SQL file is an independent, successfully executed transformation. Pair each transformation with its build script and verify its output.

## SQL files

- `sql/intermediate/int_taxi_trips.sql`
- `sql/marts/airport_comparison.sql`
- `sql/marts/airport_daily_unit_economics.sql`
- `sql/marts/airport_metrics.sql`
- `sql/marts/airport_per_mile_sample.sql`
- `sql/marts/airport_sensitivity.sql`
- `sql/marts/airport_trip_sample.sql`
- `sql/marts/airport_unit_economics.sql`
- `sql/marts/hourly_demand.sql`
- `sql/marts/hourly_transit_metrics.sql`
- `sql/marts/hourly_weather_metrics.sql`
- `sql/marts/monthly_taxi_metrics.sql`
- `sql/marts/pickup_zone_metrics.sql`
- `sql/marts/taxi_hourly_comparison.sql`
- `sql/marts/taxi_transit_hourly_comparison.sql`
- `sql/marts/taxi_transit_weather_hourly.sql`
- `sql/marts/weather_demand_adjusted.sql`
- `sql/marts/weather_demand_analysis.sql`
- `sql/marts/weather_demand_daytype_summary.sql`
- `sql/staging/audit_issue_overlap.sql`
- `sql/staging/audit_quality_by_month.sql`
- `sql/staging/audit_taxi_quality.sql`
- `sql/staging/stg_taxi_trips.sql`
- `sql/staging/stg_transit_ridership.sql`

## Build scripts

- `src/ingestion/build_airport_metrics.py`
- `src/ingestion/build_hourly_demand.py`
- `src/ingestion/build_hourly_transit_metrics.py`
- `src/ingestion/build_hourly_weather_metrics.py`
- `src/ingestion/build_intermediate.py`
- `src/ingestion/build_monthly_metrics.py`
- `src/ingestion/build_payment_fare_metrics.py`
- `src/ingestion/build_pickup_zone_metrics.py`
- `src/ingestion/build_staging.py`
- `src/ingestion/build_taxi_hourly_comparison.py`
- `src/ingestion/build_taxi_transit_comparison.py`
- `src/ingestion/build_taxi_transit_weather_hourly.py`
- `src/ingestion/build_transit_staging.py`
- `src/ingestion/build_zone_metrics.py`
- `src/validation/build_airport_daily_unit_economics.py`

## Verification checklist

- [ ] At least 12 meaningful SQL transformations are documented.
- [ ] Each transformation has a documented input and output.
- [ ] The build process runs successfully and can be repeated.
- [ ] Joins and aggregations are checked for double counting.
- [ ] Relevant tests and reconciliation checks pass.
