
from pathlib import Path
import duckdb
import numpy as np

root = Path(__file__).resolve().parents[2]
db_path = root / "metropulse.duckdb"
data_path = (
    root / "data" / "processed"
    / "airport_daily_unit_economics.parquet"
)

con = duckdb.connect(str(db_path), read_only=True)

try:
    daily = con.execute("""
        SELECT
            pickup_date,
            MAX(median_amount_per_mile)
                FILTER (WHERE airport = 'JFK Airport') AS jfk,
            MAX(median_amount_per_mile)
                FILTER (WHERE airport = 'LaGuardia Airport') AS lga
        FROM read_parquet(?)
        GROUP BY pickup_date
        HAVING COUNT(DISTINCT airport) = 2
        ORDER BY pickup_date
    """, [str(data_path)]).fetchdf()
finally:
    con.close()

daily = daily.dropna(subset=["jfk", "lga"])

# One paired difference per date: LaGuardia minus JFK.
differences = (
    daily["lga"].to_numpy() - daily["jfk"].to_numpy()
)

rng = np.random.default_rng(42)
bootstrap_reps = 10_000
n = len(differences)

bootstrap_means = np.empty(bootstrap_reps)

for i in range(bootstrap_reps):
    sampled = rng.choice(differences, size=n, replace=True)
    bootstrap_means[i] = sampled.mean()

observed_difference = differences.mean()
ci_low, ci_high = np.percentile(
    bootstrap_means, [2.5, 97.5]
)

print("\n=== PAIRED DAILY BOOTSTRAP ===\n")
print(f"Matched dates: {n}")
print(f"Mean daily-median difference (LGA - JFK): "
      f"${observed_difference:.3f} per mile")
print(f"95% bootstrap CI: [${ci_low:.3f}, ${ci_high:.3f}]")

if ci_low > 0:
    print("Interpretation: the interval is entirely above zero.")
elif ci_high < 0:
    print("Interpretation: the interval is entirely below zero.")
else:
    print("Interpretation: the interval includes zero.")

print(
    "\nCaution: this interval describes variation across the "
    "observed daily differences. It does not establish profitability "
    "or causation, and serial dependence between days may affect "
    "the interval."
)
