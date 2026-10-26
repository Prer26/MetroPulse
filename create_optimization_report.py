import json
from pathlib import Path

reports = Path("reports")
before = json.loads((reports / "query_benchmark_before.json").read_text(encoding="utf-8"))
after = json.loads((reports / "query_benchmark_after.json").read_text(encoding="utf-8"))
validation = json.loads((reports / "query_result_validation.json").read_text(encoding="utf-8"))

before_map = {x["query"]: x for x in before}
pairs = [
    ("Monthly taxi metrics", "Q1_monthly_full_scan", "Q1_original_monthly",
     "Q1_optimized_monthly_mart"),
    ("Pickup-zone summaries", "Q2_zone_join_aggregation", "Q2_original_zone",
     "Q2_zone_mart"),
]

lines = [
    "# Query Performance Optimization Report",
    "",
    "## Method",
    "",
    "Each query was warmed up once and then timed across three executions. "
    "The median of the three measured runs is reported. Timings are specific "
    "to this machine, DuckDB version, database, and execution environment.",
    "",
    "## Results",
    "",
    "| Query | Baseline median (s) | Mart median (s) | Time reduction | Result validation |",
    "|---|---:|---:|---:|---|",
]

for label, baseline_key, original_key, optimized_key in pairs:
    b = before_map[baseline_key]["median_seconds"]
    original = after[original_key]["median_seconds"]
    optimized = after[optimized_key]["median_seconds"]
    reduction = (1 - optimized / original) * 100 if original else 0
    status = validation["monthly" if "Monthly" in label else "zones"]["values_match"]
    lines.append(
        f"| {label} | {b:.4f} | {optimized:.4f} | {reduction:.2f}% | "
        f"{'PASS' if status else 'INVESTIGATE'} |"
    )

lines += [
    "",
    "## Interpretation",
    "",
    "- Monthly metrics use the existing three-row monthly mart instead of "
    "recomputing aggregates from the intermediate trip view.",
    "- Pickup-zone summaries use the existing zone mart instead of repeating "
    "the large trip-to-zone join and aggregation.",
    "- The validation script confirmed matching grouped values for the tested "
    "monthly measures and shared zone measures within its configured numeric "
    "tolerances.",
    "- The zone benchmark compares trip counts and recorded amounts; it does "
    "not compare average distance because that measure is not included in "
    "the selected zone-mart query.",
    "- These results demonstrate faster analytical queries against precomputed "
    "marts. They do not establish an equivalent speedup for the entire dashboard.",
    "",
    "## Reproducibility",
    "",
    "- Baseline timings: `reports/query_benchmark_before.json`",
    "- Post-mart timings: `reports/query_benchmark_after.json`",
    "- Query plans and table schemas: `reports/query_plan_analysis.json`",
    "- Output equivalence checks: `reports/query_result_validation.json`",
    "- Scripts: `benchmark_queries.py`, `inspect_query_plans.py`, "
    "`benchmark_marts.py`, `validate_query_optimizations.py`",
    "",
]

Path("docs").mkdir(exist_ok=True)
Path("docs/query_optimization_report.md").write_text(
    "\n".join(lines), encoding="utf-8"
)
print("Created docs/query_optimization_report.md")
print("\n".join(lines))
