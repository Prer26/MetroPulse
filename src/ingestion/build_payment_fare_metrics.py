
from pathlib import Path

import duckdb

# --------------------------------------------------
# PATHS
# --------------------------------------------------

# Project root: duckdb-practice/
ROOT = Path(__file__).resolve().parents[2]

DB_PATH = ROOT / "metropulse.duckdb"
OUTPUT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "payment_fare_metrics.parquet"
)

# --------------------------------------------------
# VALIDATE PATHS
# --------------------------------------------------

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"DuckDB database not found: {DB_PATH}\n"
        "Check that metropulse.duckdb exists in the project root."
    )

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

print("=" * 65)
print("METROPULSE — PAYMENT & FARE MART")
print("=" * 65)
print(f"Database: {DB_PATH}")
print(f"Output:   {OUTPUT_PATH}")

# --------------------------------------------------
# BUILD ANALYTICAL MART
# --------------------------------------------------

QUERY = """
SELECT
    source_month,
    payment_type,

    CASE payment_type
        WHEN 0 THEN 'Unknown or unmapped'
        WHEN 1 THEN 'Credit card'
        WHEN 2 THEN 'Cash'
        WHEN 3 THEN 'No charge'
        WHEN 4 THEN 'Dispute'
        WHEN 5 THEN 'Unknown'
        WHEN 6 THEN 'Voided trip'
        ELSE 'Other or undocumented'
    END AS payment_label,

    COUNT(*) AS trip_count,

    SUM(fare_amount) AS total_recorded_fare,
    SUM(total_amount) AS total_recorded_amount,

    AVG(total_amount) AS avg_recorded_amount_per_trip,
    MEDIAN(total_amount) AS median_recorded_amount_per_trip,

    SUM(tip_amount) AS total_recorded_tips,
    AVG(tip_amount) AS avg_recorded_tip,
    MEDIAN(tip_amount) AS median_recorded_tip,

    COUNT(*) FILTER (
        WHERE fare_amount < 0
    ) AS negative_fare_trips,

    COUNT(*) FILTER (
        WHERE total_amount < 0
    ) AS negative_total_trips,

    COUNT(*) FILTER (
        WHERE trip_distance IS NULL OR trip_distance <= 0
    ) AS invalid_distance_trips,

    COUNT(*) FILTER (
        WHERE payment_type = 1
          AND fare_amount > 0
          AND tip_amount IS NOT NULL
    ) AS eligible_card_fare_trips,

    SUM(tip_amount) FILTER (
        WHERE payment_type = 1
          AND fare_amount > 0
          AND tip_amount IS NOT NULL
    ) AS card_recorded_tips,

    SUM(fare_amount) FILTER (
        WHERE payment_type = 1
          AND fare_amount > 0
          AND tip_amount IS NOT NULL
    ) AS eligible_card_fares,

    CASE
        WHEN payment_type = 1
          AND SUM(fare_amount) FILTER (
              WHERE payment_type = 1
                AND fare_amount > 0
                AND tip_amount IS NOT NULL
          ) > 0
        THEN
            100.0 *
            SUM(tip_amount) FILTER (
                WHERE payment_type = 1
                  AND fare_amount > 0
                  AND tip_amount IS NOT NULL
            )
            /
            SUM(fare_amount) FILTER (
                WHERE payment_type = 1
                  AND fare_amount > 0
                  AND tip_amount IS NOT NULL
            )
        ELSE NULL
    END AS card_tip_to_fare_pct

FROM int_taxi_trips

GROUP BY
    source_month,
    payment_type

ORDER BY
    source_month,
    payment_type
"""

# --------------------------------------------------
# EXECUTE AND VALIDATE
# --------------------------------------------------

con = duckdb.connect(str(DB_PATH), read_only=False)

try:
    # Confirm the required source table exists.
    tables = {
        row[0]
        for row in con.execute("SHOW TABLES").fetchall()
    }

    if "int_taxi_trips" not in tables:
        raise RuntimeError(
            "'int_taxi_trips' was not found in the database. "
            "Confirm the correct database is being used."
        )

    source_count = con.execute(
        "SELECT COUNT(*) FROM int_taxi_trips"
    ).fetchone()[0]

    print(f"\nSource trip count: {source_count:,}")
    print("\nBuilding payment and fare metrics...")

    # Write the new Parquet file.
    # Escape apostrophes in the output path for SQL safety.
    output_sql_path = str(OUTPUT_PATH.resolve()).replace("'", "''")

    con.execute(
        f"""
        COPY ({QUERY})
        TO '{output_sql_path}'
        (FORMAT PARQUET)
        """
    )

    # Verify the generated mart.
    mart_count = con.execute(
        """
        SELECT COALESCE(SUM(trip_count), 0)
        FROM read_parquet(?)
        """,
        [str(OUTPUT_PATH.resolve())],
    ).fetchone()[0]

    mart_rows = con.execute(
        """
        SELECT COUNT(*)
        FROM read_parquet(?)
        """,
        [str(OUTPUT_PATH.resolve())],
    ).fetchone()[0]

    if mart_count != source_count:
        raise AssertionError(
            f"Trip-count reconciliation failed: "
            f"source={source_count:,}, mart={mart_count:,}"
        )

    print("\nPAYMENT & FARE MART CREATED SUCCESSFULLY")
    print("-" * 65)
    print(f"Output file: {OUTPUT_PATH}")
    print(f"Mart rows:   {mart_rows:,}")
    print(f"Source trips:{source_count:>12,}")
    print(f"Mart trips:  {mart_count:>12,}")
    print("Reconciliation: PASSED")

    print("\nTrip counts by month and payment code:")

    result = con.execute(
        """
        SELECT
            source_month,
            payment_type,
            payment_label,
            trip_count,
            avg_recorded_amount_per_trip,
            total_recorded_tips,
            card_tip_to_fare_pct
        FROM read_parquet(?)
        ORDER BY source_month, payment_type
        """,
        [str(OUTPUT_PATH.resolve())],
    ).fetchdf()

    print(result.to_string(index=False))

finally:
    con.close()
