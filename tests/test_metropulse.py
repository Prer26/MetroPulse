import duckdb
import pytest
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "metropulse.duckdb"
EXPECTED_TAXI_ROWS = 10_777_315


@pytest.fixture(scope="module")
def con():
    db = duckdb.connect(str(DB_PATH), read_only=True)
    yield db
    db.close()


def test_database_exists():
    assert DB_PATH.exists()


def test_required_tables_exist(con):
    tables = {
        row[0] for row in con.execute("SHOW TABLES").fetchall()
    }
    required = {
        "stg_taxi_trips",
        "int_taxi_trips",
        "stg_transit_ridership",
        "mart_monthly_taxi_metrics",
        "mart_hourly_demand",
        "mart_pickup_zone_metrics",
        "mart_airport_metrics",
    }
    assert required.issubset(tables)


def test_raw_to_staging_taxi_count_reconciles(con):
    raw_count = con.execute(
        "SELECT COUNT(*) FROM stg_taxi_trips"
    ).fetchone()[0]
    intermediate_count = con.execute(
        "SELECT COUNT(*) FROM int_taxi_trips"
    ).fetchone()[0]
    assert raw_count == EXPECTED_TAXI_ROWS
    assert intermediate_count == raw_count


def test_monthly_mart_reconciles_to_taxi_fact(con):
    mart_count = con.execute(
        "SELECT SUM(total_trips) FROM mart_monthly_taxi_metrics"
    ).fetchone()[0]
    assert mart_count == EXPECTED_TAXI_ROWS


def test_monthly_mart_has_three_months(con):
    months = con.execute(
        "SELECT COUNT(DISTINCT source_month) "
        "FROM mart_monthly_taxi_metrics"
    ).fetchone()[0]
    assert months == 3


def test_hourly_demand_has_expected_grain(con):
    rows = con.execute(
        "SELECT COUNT(*) FROM mart_hourly_demand"
    ).fetchone()[0]
    assert rows == 72


def test_hourly_demand_keys_are_unique(con):
    duplicates = con.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT source_month, pickup_hour
            FROM mart_hourly_demand
            GROUP BY source_month, pickup_hour
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    assert duplicates == 0


def test_zone_mart_reconciles_to_taxi_fact(con):
    zone_count = con.execute(
        "SELECT SUM(total_trips) FROM mart_pickup_zone_metrics"
    ).fetchone()[0]
    assert zone_count == EXPECTED_TAXI_ROWS


def test_zone_mart_has_zone_names(con):
    missing = con.execute("""
        SELECT COUNT(*)
        FROM mart_pickup_zone_metrics
        WHERE pickup_zone IS NULL OR TRIM(pickup_zone) = ''
    """).fetchone()[0]
    assert missing == 0


def test_airport_groups_are_present(con):
    groups = con.execute(
        "SELECT COUNT(DISTINCT pickup_group) FROM mart_airport_metrics"
    ).fetchone()[0]
    assert groups == 2


def test_taxi_quality_flags_exist(con):
    columns = {
        row[0] for row in con.execute(
            "DESCRIBE SELECT * FROM int_taxi_trips"
        ).fetchall()
    }
    required_flags = {
        "has_missing_passenger_count",
        "has_invalid_distance",
        "has_negative_fare",
        "has_negative_duration",
    }
    assert required_flags.issubset(columns)


def test_transit_quality_flags_are_clear(con):
    invalid = con.execute("""
        SELECT
            COUNT(*) FILTER (WHERE flag_invalid_timestamp) +
            COUNT(*) FILTER (WHERE flag_invalid_ridership) +
            COUNT(*) FILTER (WHERE flag_invalid_transfers)
        FROM stg_transit_ridership
    """).fetchone()[0]
    assert invalid == 0


def test_monthly_metrics_have_valid_values(con):
    invalid = con.execute("""
        SELECT COUNT(*)
        FROM mart_monthly_taxi_metrics
        WHERE total_trips <= 0
           OR avg_amount_per_trip IS NULL
           OR total_recorded_amount IS NULL
    """).fetchone()[0]
    assert invalid == 0

def test_q2_taxi_window_excludes_exactly_24_boundary_or_anomalous_rows(con):
    q2_rows = con.execute("""
        SELECT COUNT(*)
        FROM int_taxi_trips
        WHERE tpep_pickup_datetime >= TIMESTAMP '2024-04-01 00:00:00'
          AND tpep_pickup_datetime < TIMESTAMP '2024-07-01 00:00:00'
    """).fetchone()[0]

    outside_rows = con.execute("""
        SELECT COUNT(*)
        FROM int_taxi_trips
        WHERE tpep_pickup_datetime < TIMESTAMP '2024-04-01 00:00:00'
           OR tpep_pickup_datetime >= TIMESTAMP '2024-07-01 00:00:00'
    """).fetchone()[0]

    assert q2_rows == 10_777_291
    assert outside_rows == 24
    assert q2_rows + outside_rows == EXPECTED_TAXI_ROWS


def test_q2_out_of_window_rows_are_retained_in_intermediate_view(con):
    outside_rows = con.execute("""
        SELECT COUNT(*)
        FROM int_taxi_trips
        WHERE tpep_pickup_datetime < TIMESTAMP '2024-04-01 00:00:00'
           OR tpep_pickup_datetime >= TIMESTAMP '2024-07-01 00:00:00'
    """).fetchone()[0]

    assert outside_rows == 24


def test_hourly_comparison_parquet_reconciles_to_q2_taxi_count(con):
    parquet_path = DB_PATH.parent / "data" / "processed" / "taxi_hourly_comparison.parquet"
    assert parquet_path.exists(), f"Missing hourly comparison: {parquet_path}"

    hourly_rows, summed_trips = con.execute("""
        SELECT COUNT(*), COALESCE(SUM(taxi_trips), 0)
        FROM read_parquet(?)
    """, [str(parquet_path)]).fetchone()

    assert hourly_rows == 2_184
    assert summed_trips == 10_777_291
