
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
con = duckdb.connect(str(root / "metropulse.duckdb"))

sql_path = (
    root / "sql" / "marts"
    / "taxi_transit_hourly_comparison.sql"
)

output_path = (
    root / "data" / "processed"
    / "taxi_transit_hourly_comparison.parquet"
)

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    print("\n=== TAXI–SUBWAY HOURLY JOIN VALIDATION ===\n")

    validation = con.execute("""
        SELECT
            COUNT(*) AS joined_hours,
            COUNT(DISTINCT hour_start) AS distinct_hours,
            MIN(hour_start) AS first_hour,
            MAX(hour_start) AS last_hour,
            SUM(taxi_trips) AS total_taxi_trips,
            SUM(total_ridership) AS total_recorded_ridership
        FROM read_parquet(?)
    """, [str(output_path)]).fetchdf()

    print(validation.to_string(index=False))

    print("\n=== HOURLY CORRELATIONS ===\n")

    correlations = con.execute("""
        SELECT
            CORR(taxi_trips, total_ridership)
                AS taxi_ridership_correlation,
            CORR(taxi_trips, total_transfers)
                AS taxi_transfers_correlation,
            CORR(total_ridership, total_transfers)
                AS ridership_transfers_correlation
        FROM read_parquet(?)
    """, [str(output_path)]).fetchdf()

    print(correlations.to_string(index=False))

finally:
    con.close()
