
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parents[2]
con = duckdb.connect(str(root / "metropulse.duckdb"))

sql_path = root / "sql" / "marts" / "weather_demand_adjusted.sql"

try:
    result = con.execute(
        sql_path.read_text(encoding="utf-8")
    ).fetchdf()

    print("\n=== WEATHER DEMAND: HOUR-OF-DAY & DAY-TYPE COMPARISON ===\n")
    print(result.to_string(index=False))

    output_path = root / "data" / "processed" / "weather_demand_adjusted.csv"
    result.to_csv(output_path, index=False)
    print(f"\nSaved results to: {output_path}")

finally:
    con.close()
