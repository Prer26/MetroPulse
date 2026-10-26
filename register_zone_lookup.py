
from pathlib import Path
import duckdb

root = Path(__file__).resolve().parent
db_path = root / "metropulse.duckdb"
lookup_path = root / "data" / "raw" / "zones" / "taxi_zone_lookup.csv"

con = duckdb.connect(str(db_path))

try:
    con.execute("""
        CREATE OR REPLACE TABLE taxi_zone_lookup AS
        SELECT LocationID, Borough, Zone, service_zone
        FROM read_csv_auto(?)
    """, [str(lookup_path)])

    print("Zone lookup rows:",
          con.execute("SELECT COUNT(*) FROM taxi_zone_lookup").fetchone()[0])

    print("\nAirport-related zones:")
    print(con.execute("""
        SELECT LocationID, Borough, Zone
        FROM taxi_zone_lookup
        WHERE Zone ILIKE '%Airport%'
        ORDER BY LocationID
    """).fetchdf().to_string(index=False))

    for col in ["PULocationID", "DOLocationID"]:
        missing = con.execute(f"""
            SELECT COUNT(DISTINCT t.{col})
            FROM int_taxi_trips t
            LEFT JOIN taxi_zone_lookup z
                ON t.{col} = z.LocationID
            WHERE t.{col} IS NOT NULL
                AND z.LocationID IS NULL
        """).fetchone()[0]

        print(f"{col} values without lookup matches:", missing)
finally:
    con.close()
