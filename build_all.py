from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable

STEPS = [
    # Source inventory and base views
    ("Validate source inventory", [PYTHON, "src/ingestion/inventory.py"]),
    ("Build taxi staging", [PYTHON, "src/ingestion/build_staging.py"]),
    ("Build taxi intermediate", [PYTHON, "src/ingestion/build_intermediate.py"]),
    ("Build transit staging", [PYTHON, "src/ingestion/build_transit_staging.py"]),

    # Base marts
    ("Build monthly taxi mart", [PYTHON, "src/ingestion/build_monthly_metrics.py"]),
    ("Build hourly demand mart", [PYTHON, "src/ingestion/build_hourly_demand.py"]),
    ("Build pickup-zone mart", [PYTHON, "src/ingestion/build_pickup_zone_metrics.py"]),
    ("Build airport mart", [PYTHON, "src/ingestion/build_airport_metrics.py"]),
    ("Build payment/fare mart", [PYTHON, "src/ingestion/build_payment_fare_metrics.py"]),
    ("Build hourly transit mart", [PYTHON, "src/ingestion/build_hourly_transit_metrics.py"]),
    ("Build hourly weather mart", [PYTHON, "src/ingestion/build_hourly_weather_metrics.py"]),

    # Dependent hourly joins
    ("Build hourly taxi comparison", [PYTHON, "src/ingestion/build_taxi_hourly_comparison.py"]),
    ("Build taxi/transit comparison", [PYTHON, "src/ingestion/build_taxi_transit_comparison.py"]),
    ("Build taxi/transit/weather mart", [PYTHON, "src/ingestion/build_taxi_transit_weather_hourly.py"]),

    # Airport exports are standalone SQL files
    ("Build airport trip sample", ["sql/marts/airport_trip_sample.sql"]),
    ("Build airport per-mile sample", ["sql/marts/airport_per_mile_sample.sql"]),
    ("Build airport daily unit economics", ["sql/marts/airport_daily_unit_economics.sql"]),
    ("Build airport sensitivity", ["sql/marts/airport_sensitivity.sql"]),

    # Automated tests
    ("Run automated tests", [PYTHON, "-m", "pytest", "tests", "-q"]),
]

def run_step(label, command):
    print(f"\n{'=' * 72}\n{label}\n{'=' * 72}", flush=True)

    if command[0] == "sql/marts/airport_trip_sample.sql":
        sql_files = command
        import duckdb
        db = ROOT / "metropulse.duckdb"
        with duckdb.connect(str(db)) as con:
            for relative in sql_files:
                con.execute((ROOT / relative).read_text(encoding="utf-8"))
        return

    if command[0] == "sql/marts/airport_per_mile_sample.sql":
        import duckdb
        with duckdb.connect(str(ROOT / "metropulse.duckdb")) as con:
            con.execute((ROOT / command[0]).read_text(encoding="utf-8"))
        return

    if command[0] == "sql/marts/airport_daily_unit_economics.sql":
        import duckdb
        with duckdb.connect(str(ROOT / "metropulse.duckdb")) as con:
            con.execute((ROOT / command[0]).read_text(encoding="utf-8"))
        return

    if command[0] == "sql/marts/airport_sensitivity.sql":
        import duckdb
        with duckdb.connect(str(ROOT / "metropulse.duckdb")) as con:
            con.execute((ROOT / command[0]).read_text(encoding="utf-8"))
        return

    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(
            f"Step failed: {label} (exit code {result.returncode})"
        )

def main():
    for index, (label, command) in enumerate(STEPS, start=1):
        print(f"\nSTEP {index}/{len(STEPS)}", flush=True)
        run_step(label, command)

    print("\nSUCCESS: all build steps and tests completed.", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nBUILD FAILED: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
