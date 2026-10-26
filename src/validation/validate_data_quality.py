from pathlib import Path
import json
from datetime import datetime
import duckdb

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "metropulse.duckdb"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = REPORT_DIR / "data_quality_report.json"

EXPECTED_START = "2024-04-01 00:00:00"
EXPECTED_END = "2024-07-01 00:00:00"
DETAIL_TABLES = ("stg_taxi_trips", "int_taxi_trips")

def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. Run this script from "
            "the project's src/validation folder or update DB_PATH."
        )

    con = duckdb.connect(str(DB_PATH), read_only=True)
    checks = []
    findings = []

    def add_check(name, status, details, severity="info"):
        item = {
            "check": name,
            "status": status,
            "severity": severity,
            "details": details,
        }
        checks.append(item)
        if status in ("REVIEW", "FAIL"):
            findings.append(item)
        print(f"[{status}] {name}: {details}")

    try:
        tables = {
            row[0] for row in con.execute("SHOW TABLES").fetchall()
        }
        if "int_taxi_trips" not in tables:
            raise RuntimeError("Required table int_taxi_trips is missing.")

        source_count = con.execute(
            "SELECT COUNT(*) FROM int_taxi_trips"
        ).fetchone()[0]
        add_check("Source row count", "INFO",
                  f"int_taxi_trips contains {source_count:,} rows")

        # Core field-level quality checks on the detailed analytical table.
        metrics = con.execute("""
            SELECT
                COUNT(*) AS total_rows,
                COUNT(*) FILTER (WHERE passenger_count IS NULL) AS missing_passenger_count,
                COUNT(*) FILTER (WHERE passenger_count = 0) AS zero_passenger_count,
                COUNT(*) FILTER (WHERE fare_amount < 0) AS negative_fare,
                COUNT(*) FILTER (WHERE total_amount < 0) AS negative_total_amount,
                COUNT(*) FILTER (WHERE trip_distance <= 0 OR trip_distance IS NULL) AS nonpositive_or_missing_distance,
                COUNT(*) FILTER (WHERE duration_minutes < 0) AS negative_duration,
                COUNT(*) FILTER (WHERE duration_minutes = 0) AS zero_duration,
                COUNT(*) FILTER (WHERE tpep_pickup_datetime IS NULL) AS missing_pickup_timestamp,
                COUNT(*) FILTER (WHERE tpep_dropoff_datetime IS NULL) AS missing_dropoff_timestamp,
                COUNT(*) FILTER (
                    WHERE tpep_pickup_datetime IS NOT NULL
                      AND tpep_dropoff_datetime IS NOT NULL
                      AND tpep_dropoff_datetime < tpep_pickup_datetime
                ) AS dropoff_before_pickup,
                COUNT(*) FILTER (
                    WHERE tpep_pickup_datetime < TIMESTAMP '2024-04-01 00:00:00'
                       OR tpep_pickup_datetime >= TIMESTAMP '2024-07-01 00:00:00'
                ) AS pickup_outside_q2_2024
            FROM int_taxi_trips
        """).fetchone()
        names = [
            "total_rows", "missing_passenger_count", "zero_passenger_count",
            "negative_fare", "negative_total_amount",
            "nonpositive_or_missing_distance", "negative_duration",
            "zero_duration", "missing_pickup_timestamp",
            "missing_dropoff_timestamp", "dropoff_before_pickup",
            "pickup_outside_q2_2024",
        ]
        m = dict(zip(names, metrics))
        total = m["total_rows"] or 1

        issue_specs = [
            ("Missing passenger count", "missing_passenger_count"),
            ("Zero passenger count", "zero_passenger_count"),
            ("Negative fare", "negative_fare"),
            ("Negative total amount", "negative_total_amount"),
            ("Nonpositive or missing trip distance", "nonpositive_or_missing_distance"),
            ("Negative duration", "negative_duration"),
            ("Zero duration", "zero_duration"),
            ("Missing pickup timestamp", "missing_pickup_timestamp"),
            ("Missing dropoff timestamp", "missing_dropoff_timestamp"),
            ("Dropoff before pickup", "dropoff_before_pickup"),
            ("Pickup timestamps outside Q2 2024", "pickup_outside_q2_2024"),
        ]
        for label, key in issue_specs:
            count = m[key]
            pct = count / total * 100
            if count == 0:
                status = "PASS"
            elif key in ("missing_pickup_timestamp", "missing_dropoff_timestamp"):
                status = "FAIL"
            else:
                status = "REVIEW"
            add_check(label, status, f"{count:,} rows ({pct:.4f}%)",
                      "error" if status == "FAIL" else ("warning" if status == "REVIEW" else "info"))

        date_range = con.execute("""
            SELECT MIN(tpep_pickup_datetime), MAX(tpep_pickup_datetime)
            FROM int_taxi_trips
        """).fetchone()
        add_check("Pickup timestamp range", "INFO",
                  f"min={date_range[0]}, max={date_range[1]}")

        # Exact duplicate check across all columns in the detailed table.
        # COUNT(*) - COUNT(DISTINCT row) is avoided because DuckDB struct handling
        # can vary by version; GROUP BY all columns counts duplicate groups directly.
        cols = [row[0] for row in con.execute("DESCRIBE int_taxi_trips").fetchall()]
        quoted_cols = ", ".join('"' + col.replace('"', '""') + '"' for col in cols)
        duplicate_excess = con.execute(
            f"SELECT COALESCE(SUM(n - 1), 0) FROM "
            f"(SELECT COUNT(*) AS n FROM int_taxi_trips "
            f"GROUP BY {quoted_cols} HAVING COUNT(*) > 1)"
        ).fetchone()[0]
        add_check("Exact duplicate excess rows",
                  "PASS" if duplicate_excess == 0 else "REVIEW",
                  f"{duplicate_excess:,} excess duplicate rows",
                  "warning" if duplicate_excess else "info")

        # Row-count reconciliation is meaningful only between detailed pipeline
        # tables. The 5-row taxi_trips table is a demo/sample table, not a peer.
        counts = {}
        for table in DETAIL_TABLES:
            if table in tables:
                counts[table] = con.execute(
                    f'SELECT COUNT(*) FROM "{table}"'
                ).fetchone()[0]
        if "stg_taxi_trips" in counts and "int_taxi_trips" in counts:
            diff = counts["int_taxi_trips"] - counts["stg_taxi_trips"]
            add_check(
                "Staging-to-intermediate row-count reconciliation",
                "PASS" if diff == 0 else "REVIEW",
                f"stg_taxi_trips={counts['stg_taxi_trips']:,}; "
                f"int_taxi_trips={counts['int_taxi_trips']:,}; difference={diff:,}",
                "warning" if diff else "info",
            )
        else:
            add_check("Staging-to-intermediate row-count reconciliation",
                      "REVIEW", "One or both detailed pipeline tables are missing",
                      "warning")

        # Check each expected month in the intermediate table.
        monthly = con.execute("""
            SELECT source_month, COUNT(*) AS row_count
            FROM int_taxi_trips
            GROUP BY source_month
            ORDER BY source_month
        """).fetchall()
        monthly_counts = {str(month): count for month, count in monthly}
        expected_months = {"2024-04", "2024-05", "2024-06"}
        observed_months = set(monthly_counts)
        month_ok = expected_months.issubset(observed_months)
        add_check(
            "Expected Q2 2024 source months",
            "PASS" if month_ok else "REVIEW",
            f"monthly counts={monthly_counts}; expected months={sorted(expected_months)}",
            "warning" if not month_ok else "info",
        )

        # Demo table is deliberately reported as informational, never reconciled
        # against the 10M+ row analytical dataset.
        if "taxi_trips" in tables:
            sample_count = con.execute("SELECT COUNT(*) FROM taxi_trips").fetchone()[0]
            add_check("Demo table excluded from full-dataset reconciliation",
                      "INFO",
                      f"taxi_trips contains {sample_count:,} sample rows; not compared with int_taxi_trips")

        report = {
            "database": str(DB_PATH),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "source_table": "int_taxi_trips",
            "source_row_count": source_count,
            "checks_run": len(checks),
            "review_items": sum(x["status"] in ("REVIEW", "FAIL") for x in checks),
            "checks": checks,
            "monthly_source_counts": monthly_counts,
        }
        REPORT_PATH.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"\nChecks run: {len(checks)}")
        print(f"Items for review: {report['review_items']}")
        print(f"JSON report saved to: {REPORT_PATH}")
    finally:
        con.close()

if __name__ == "__main__":
    main()
