# Query Performance Optimization Report

## Method

Each query was warmed up once and then timed across three executions. The median of the three measured runs is reported. Timings are specific to this machine, DuckDB version, database, and execution environment.

## Results

| Query | Baseline median (s) | Mart median (s) | Time reduction | Result validation |
|---|---:|---:|---:|---|
| Monthly taxi metrics | 1.3289 | 0.0009 | 99.94% | PASS |
| Pickup-zone summaries | 0.5334 | 0.0038 | 99.12% | PASS |

## Interpretation

- Monthly metrics use the existing three-row monthly mart instead of recomputing aggregates from the intermediate trip view.
- Pickup-zone summaries use the existing zone mart instead of repeating the large trip-to-zone join and aggregation.
- The validation script confirmed matching grouped values for the tested monthly measures and shared zone measures within its configured numeric tolerances.
- The zone benchmark compares trip counts and recorded amounts; it does not compare average distance because that measure is not included in the selected zone-mart query.
- These results demonstrate faster analytical queries against precomputed marts. They do not establish an equivalent speedup for the entire dashboard.

## Reproducibility

- Baseline timings: `reports/query_benchmark_before.json`
- Post-mart timings: `reports/query_benchmark_after.json`
- Query plans and table schemas: `reports/query_plan_analysis.json`
- Output equivalence checks: `reports/query_result_validation.json`
- Scripts: `benchmark_queries.py`, `inspect_query_plans.py`, `benchmark_marts.py`, `validate_query_optimizations.py`
