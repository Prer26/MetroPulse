
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
data_path = root / "data" / "processed" / "taxi_transit_weather_hourly.parquet"

con = duckdb.connect(str(db_path), read_only=True)

try:
    df = con.execute("""
        SELECT
            CAST(hour_start AS DATE) AS service_date,
            CASE
                WHEN EXTRACT(DOW FROM hour_start) IN (0, 6)
                    THEN 'Weekend'
                ELSE 'Weekday'
            END AS day_type,
            is_rainy_hour,
            taxi_trips
        FROM read_parquet(?)
        ORDER BY hour_start
    """, [str(data_path)]).fetchdf()
finally:
    con.close()

df["service_date"] = pd.to_datetime(df["service_date"])

# One row per date: compare that day's rainy and dry hourly averages.
daily = (
    df.groupby(["service_date", "day_type", "is_rainy_hour"])
      .agg(
          hours=("taxi_trips", "size"),
          avg_taxi_trips=("taxi_trips", "mean")
      )
      .reset_index()
)

# Keep dates that contain both rainy and dry hours.
wide = daily.pivot(
    index=["service_date", "day_type"],
    columns="is_rainy_hour",
    values="avg_taxi_trips"
).dropna(subset=[False, True]).reset_index()

wide["difference"] = wide[True] - wide[False]

print("\n=== PAIRED-DATE WEATHER COMPARISON ===")
print("Dates with both rainy and dry hours:", len(wide))

for day_type in ["Weekday", "Weekend"]:
    subset = wide[wide["day_type"] == day_type]
    if subset.empty:
        continue

    differences = subset["difference"].to_numpy()
    rng = np.random.default_rng(42)
    bootstrap_means = np.array([
        rng.choice(differences, size=len(differences), replace=True).mean()
        for _ in range(10000)
    ])

    lower, upper = np.percentile(bootstrap_means, [2.5, 97.5])

    print(f"\n{day_type}")
    print("Dates:", len(subset))
    print(f"Mean daily difference (rainy-hour avg - dry-hour avg): {differences.mean():.2f}")
    print(f"95% date-bootstrap CI: [{lower:.2f}, {upper:.2f}] trips/hour")
    print("Positive dates:", int((differences > 0).sum()))
    print("Negative dates:", int((differences < 0).sum()))

print("\nNote: This is a paired-date descriptive analysis.")
print("It does not establish causality and may not fully adjust for hour-of-day patterns.")
