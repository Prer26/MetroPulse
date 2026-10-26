
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
sql_path = (
    root / "sql" / "marts" / "airport_daily_unit_economics.sql"
)

con = duckdb.connect(str(db_path))

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    output_path = (
        root / "data" / "processed"
        / "airport_daily_unit_economics.parquet"
    )

    print("\n=== DAILY AIRPORT UNIT ECONOMICS ===\n")

    result = con.execute("""
        SELECT
            airport,
            COUNT(*) AS days,
            SUM(eligible_trips) AS eligible_trips,
            ROUND(AVG(median_amount_per_mile), 3)
                AS average_daily_median_per_mile,
            ROUND(AVG(mean_amount_per_mile), 3)
                AS average_daily_mean_per_mile
        FROM read_parquet(?)
        GROUP BY airport
        ORDER BY airport
    """, [str(output_path)]).fetchdf()

    print(result.to_string(index=False))

    print(f"\nSaved daily metrics to: {output_path}")

finally:
    con.close()
