
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
con = duckdb.connect(str(root / "metropulse.duckdb"))

sql_path = (
    root / "sql" / "marts"
    / "weather_demand_daytype_summary.sql"
)

try:
    result = con.execute(
        sql_path.read_text(encoding="utf-8")
    ).fetchdf()

    print("\n=== RAINY VS DRY: WEEKDAY / WEEKEND SUMMARY ===\n")
    print(result.to_string(index=False))

finally:
    con.close()
