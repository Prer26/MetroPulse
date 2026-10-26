
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
con = duckdb.connect(str(root / "metropulse.duckdb"))

sql_path = root / "sql" / "marts" / "airport_sensitivity.sql"
output_path = root / "data" / "processed" / "airport_sensitivity.parquet"

try:
    con.execute(sql_path.read_text(encoding="utf-8"))

    result = con.execute("""
        SELECT
            amount_cap,
            COUNT(*) AS matched_days,
            ROUND(AVG(jfk_median), 3) AS avg_daily_median_jfk,
            ROUND(AVG(lga_median), 3) AS avg_daily_median_lga,
            ROUND(AVG(difference), 3) AS avg_daily_difference,
            ROUND(
                100.0 * AVG(difference)
                / NULLIF(AVG(jfk_median), 0), 1
            ) AS pct_higher_at_lga
        FROM read_parquet(?)
        GROUP BY amount_cap
        ORDER BY amount_cap DESC
    """, [str(output_path)]).fetchdf()

    print("\n=== AIRPORT SENSITIVITY ANALYSIS ===\n")
    print(result.to_string(index=False))
finally:
    con.close()
