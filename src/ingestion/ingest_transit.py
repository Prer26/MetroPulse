
import hashlib
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parents[2]

TRANSIT_DIR = ROOT / "data" / "raw" / "transit"
DAILY_DIR = TRANSIT_DIR / "daily"
METADATA_DIR = ROOT / "data" / "metadata"

FINAL_FILE = TRANSIT_DIR / "mta_subway_2024_q2.jsonl"
CHECKPOINT_FILE = TRANSIT_DIR / "mta_subway_2024_q2_checkpoint.json"
METADATA_FILE = METADATA_DIR / "mta_ingestion.json"

API_URL = "https://data.ny.gov/resource/wujg-7c2s.json"

START_DATE = date(2024, 4, 1)
END_DATE = date(2024, 7, 1)  # Exclusive

BATCH_SIZE = 1000
MAX_RETRIES = 5
TIMEOUT_SECONDS = 120
REQUEST_PAUSE = 0.2

USER_AGENT = "MetroPulse-Assessment/1.0"

# Fields expected to identify one ridership observation.
RECORD_KEY = (
    "transit_timestamp",
    "transit_mode",
    "station_complex_id",
    "payment_method",
    "fare_class_category",
)


# ==================================================
# 2. GENERAL UTILITIES
# ==================================================

def utc_now():
    return datetime.now(timezone.utc).isoformat()


def save_json_atomically(path, data):
    """Write JSON to a temporary file, then replace the destination."""
    temporary = path.with_suffix(path.suffix + ".tmp")

    with temporary.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    temporary.replace(path)


def load_json(path, default):
    if not path.exists():
        return default

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def daily_path(day):
    return DAILY_DIR / f"mta_{day.isoformat()}.jsonl"


def where_clause(start, end):
    return (
        f"transit_timestamp >= '{start}' "
        f"AND transit_timestamp < '{end}' "
        "AND transit_mode = 'subway'"
    )


# ==================================================
# 3. API REQUESTS WITH RETRIES
# ==================================================

def request_json(session, params):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(
                API_URL,
                params=params,
                timeout=TIMEOUT_SECONDS,
            )
            response.raise_for_status()

            result = response.json()

            if not isinstance(result, list):
                raise ValueError("Expected a JSON list from the API.")

            return result

        except (requests.RequestException, ValueError) as error:
            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    f"API request failed after {MAX_RETRIES} attempts."
                ) from error

            delay = min(2 ** attempt, 30)

            print(
                f"Request failed (attempt {attempt}/{MAX_RETRIES}): "
                f"{error}"
            )
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)


def get_expected_count(session, day):
    next_day = day + timedelta(days=1)

    result = request_json(
        session,
        {
            "$select": "COUNT(*) AS row_count",
            "$where": where_clause(
                f"{day.isoformat()}T00:00:00",
                f"{next_day.isoformat()}T00:00:00",
            ),
        },
    )

    if len(result) != 1:
        raise RuntimeError(f"Unexpected count response for {day}.")

    return int(result[0]["row_count"])


# ==================================================
# 4. DOWNLOAD AND VALIDATE A SINGLE DAY
# ==================================================

def validate_daily_file(path, expected_count, day):
    """
    Verify JSON readability, date range, row count and duplicate keys.
    A duplicate key is reported as an issue, not silently removed.
    """
    row_count = 0
    duplicate_keys = 0
    seen_keys = set()

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise RuntimeError(
                    f"Invalid JSON at {path}, line {line_number}"
                ) from error

            timestamp = row.get("transit_timestamp", "")

            if not timestamp.startswith(day.isoformat()):
                raise RuntimeError(
                    f"Unexpected timestamp on {day}: {timestamp}"
                )

            key = tuple(row.get(field) for field in RECORD_KEY)

            if any(value is None for value in key):
                raise RuntimeError(
                    f"Missing record-key field at line {line_number}"
                )

            if key in seen_keys:
                duplicate_keys += 1
            else:
                seen_keys.add(key)

            row_count += 1

    if row_count != expected_count:
        raise RuntimeError(
            f"Row-count mismatch for {day}: "
            f"expected {expected_count:,}, found {row_count:,}"
        )

    if duplicate_keys:
        raise RuntimeError(
            f"{day} has {duplicate_keys:,} duplicate record keys. "
            "Investigate before accepting this day."
        )

    return row_count


def download_day(session, day, expected_count):
    final_daily_file = daily_path(day)
    temporary_file = final_daily_file.with_suffix(".jsonl.tmp")
    next_day = day + timedelta(days=1)

    # If a previous run saved the daily file but stopped before updating
    # the checkpoint, validate it and reuse it instead of downloading again.
    if final_daily_file.exists():
        try:
            count = validate_daily_file(
                final_daily_file,
                expected_count,
                day,
            )
            print(f"Reusing verified daily file: {day}")
            return count
        except RuntimeError:
            print(f"Existing daily file failed validation: {day}")
            final_daily_file.unlink()

    if temporary_file.exists():
        temporary_file.unlink()

    count = 0
    offset = 0

    # This ordering is deterministic for the available grouping fields.
    order = (
        "transit_timestamp, station_complex_id, "
        "payment_method, fare_class_category"
    )

    with temporary_file.open("w", encoding="utf-8") as output:
        while True:
            rows = request_json(
                session,
                {
                    "$where": where_clause(
                        f"{day.isoformat()}T00:00:00",
                        f"{next_day.isoformat()}T00:00:00",
                    ),
                    "$limit": BATCH_SIZE,
                    "$offset": offset,
                    "$order": order,
                },
            )

            if not rows:
                break

            for row in rows:
                output.write(
                    json.dumps(row, separators=(",", ":")) + "\n"
                )

            count += len(rows)
            offset += len(rows)

            print(f"  {day}: retrieved {count:,}/{expected_count:,}")

            if len(rows) < BATCH_SIZE:
                break

            time.sleep(REQUEST_PAUSE)

    # Do not accept a day until it passes all validation checks.
    validate_daily_file(temporary_file, expected_count, day)

    # Atomic rename prevents a partially written file being mistaken
    # for a completed daily file.
    temporary_file.replace(final_daily_file)

    print(f"Verified {day}: {count:,} records")
    return count


# ==================================================
# 5. COMBINE ALL VERIFIED DAILY FILES
# ==================================================

def build_final_file(completed_days):
    temporary_final = FINAL_FILE.with_suffix(".jsonl.tmp")
    total_rows = 0

    with temporary_final.open("wb") as destination:
        day = START_DATE

        while day < END_DATE:
            day_key = day.isoformat()

            if day_key not in completed_days:
                raise RuntimeError(f"Missing checkpoint for {day_key}")

            path = daily_path(day)

            expected = completed_days[day_key]["downloaded_rows"]

            # Validate every source file again before combining.
            validate_daily_file(path, expected, day)

            with path.open("rb") as source:
                while True:
                    chunk = source.read(1024 * 1024)

                    if not chunk:
                        break

                    destination.write(chunk)

            total_rows += expected
            day += timedelta(days=1)

    # Atomic replacement: the final file appears only after assembly.
    temporary_final.replace(FINAL_FILE)

    return total_rows


# ==================================================
# 6. MAIN INGESTION PIPELINE
# ==================================================

def main():
    TRANSIT_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    if FINAL_FILE.exists():
        raise FileExistsError(
            f"{FINAL_FILE} already exists. "
            "Inspect it before deciding whether to replace it."
        )

    state = load_json(
        CHECKPOINT_FILE,
        {
            "source_url": API_URL,
            "start_date": START_DATE.isoformat(),
            "end_date_exclusive": END_DATE.isoformat(),
            "started_at_utc": utc_now(),
            "completed_days": {},
        },
    )

    if (
        state.get("start_date") != START_DATE.isoformat()
        or state.get("end_date_exclusive") != END_DATE.isoformat()
    ):
        raise RuntimeError(
            "Checkpoint date range does not match this script."
        )

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    day = START_DATE

    try:
        while day < END_DATE:
            day_key = day.isoformat()

            print(f"\nProcessing {day_key}...")

            expected = get_expected_count(session, day)
            print(f"API expected count: {expected:,}")

            actual = download_day(session, day, expected)

            state["completed_days"][day_key] = {
                "expected_rows": expected,
                "downloaded_rows": actual,
                "completed_at_utc": utc_now(),
            }

            save_json_atomically(CHECKPOINT_FILE, state)

            print(f"Checkpoint saved for {day_key}")
            day += timedelta(days=1)

    except Exception:
        print(
            "\nINGESTION INCOMPLETE. Completed daily files and checkpoints "
            "are preserved. Resolve the error before rerunning."
        )
        raise

    expected_days = (END_DATE - START_DATE).days

    if len(state["completed_days"]) != expected_days:
        raise RuntimeError(
            f"Expected {expected_days} completed days; "
            f"found {len(state['completed_days'])}."
        )

    print("\nAll 91 daily files are verified. Combining them...")

    total_rows = build_final_file(state["completed_days"])

    # Independently count lines in the assembled output.
    with FINAL_FILE.open("rb") as file:
        assembled_rows = sum(
            chunk.count(b"\n")
            for chunk in iter(lambda: file.read(1024 * 1024), b"")
        )

    if assembled_rows != total_rows:
        raise RuntimeError(
            f"Final line-count mismatch: expected {total_rows:,}, "
            f"found {assembled_rows:,}."
        )

    metadata = {
        "source_url": API_URL,
        "filter": "transit_mode = subway",
        "start_date_inclusive": START_DATE.isoformat(),
        "end_date_exclusive": END_DATE.isoformat(),
        "output_file": FINAL_FILE.relative_to(ROOT).as_posix(),
        "rows_retrieved": total_rows,
        "completed_days": expected_days,
        "started_at_utc": state["started_at_utc"],
        "completed_at_utc": utc_now(),
        "file_size_bytes": FINAL_FILE.stat().st_size,
        "sha256": calculate_sha256(FINAL_FILE),
        "status": "completed",
        "daily_counts": state["completed_days"],
        "pagination_note": (
            "Offset pagination was used. Matching row counts and unique "
            "record-key checks do not prove absence of all possible "
            "omissions if the source changes during extraction."
        ),
    }

    save_json_atomically(METADATA_FILE, metadata)

    print("\n" + "=" * 50)
    print("METROPULSE MTA INGESTION COMPLETED")
    print("=" * 50)
    print(f"Days verified: {expected_days}/{expected_days}")
    print(f"Rows downloaded: {total_rows:,}")
    print(f"Final line count: {assembled_rows:,}")
    print(f"File size: {FINAL_FILE.stat().st_size:,} bytes")
    print(f"SHA-256: {metadata['sha256']}")
    print(f"Data: {FINAL_FILE}")
    print(f"Metadata: {METADATA_FILE}")


if __name__ == "__main__":
    main()
