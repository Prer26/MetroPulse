# MetroPulse

NYC mobility intelligence for April 1–June 30, 2024, combining NYC TLC yellow taxi records, taxi-zone geography, historical weather, and MTA subway ridership.

## Project structure

- `app.py` — Streamlit dashboard
- `sql/` — SQL models and analytical transformations
- `src/` — ingestion, validation, and analytical scripts
- `tests/` — automated data and model checks
- `data/metadata/` — source inventory and integrity metadata
- `reports/` — quality and query-performance evidence
- `docs/` — metric definitions, optimization report, and executive memo

## Setup

Use Python 3.12 or another version supported by the installed dependencies.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the dashboard

```powershell
python -m streamlit run app.py
```

The dashboard includes executive, temporal, geographic, fare/payment, weather/transit, and data-quality views.

## Validation

```powershell
python -m py_compile app.py
python -m pytest tests -v
```

## Data and reproducibility

The core study period is April–June 2024. Large raw datasets are intentionally excluded from version control. Use the ingestion scripts and SQL build workflow in this repository to obtain the official sources and reconstruct the analytical outputs.

Before reproducing the analysis from a clean environment, verify the source URLs, required environment variables, and commands for each ingestion and database-build stage. Do not treat a previously built local DuckDB database as proof that a clean rebuild works.

## Interpretation

NYC TLC records represent citywide market activity, not transactions belonging to a fictional operator. Recorded fare and total amounts are not company revenue or profit. Weather and subway relationships are observational and do not establish causation.

## Known limitations

- The historical period is not a current demand forecast.
- Monthly zone aggregates cannot support exact partial-month daily filtering.
- Results depend on source coverage, data-quality rules, and metric definitions.
- Query benchmark results are environment-specific.

## Deployment

Add the verified public dashboard URL here before submission.

## Submission

Add the verified repository URL, final commit SHA, and explainer-video URL before submitting.
