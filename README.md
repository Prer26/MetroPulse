 <div align="center">

# 🌆 MetroPulse

### NYC Mobility Intelligence | Q2 2024

Turning taxi, subway, weather, and geographic data into practical mobility insights.

[![Live Dashboard](https://img.shields.io/badge/Live%20Dashboard-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://metropulse-d79bit6957zkt6me5ro6mu.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/Prer26/MetroPulse)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-FFF000?style=for-the-badge)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)

**Study period:** April 1 – June 30, 2024  
**Geography:** New York City  
**Dashboard:** [Open MetroPulse](https://metropulse-d79bit6957zkt6me5ro6mu.streamlit.app/)

</div>

---

## 🎬 Dashboard Preview

<img width="1872" height="905" alt="image" src="https://github.com/user-attachments/assets/f3641724-2bfe-40ff-9a40-831a8cf23b91" />


## 📌 About the Project

MetroPulse is an interactive mobility-intelligence project that analyzes New York City yellow taxi demand during Q2 2024 and explores its relationship with geographic pickup patterns, subway ridership, weather, fares, and data quality.

The project combines public datasets, Python-based data processing, SQL transformations, a DuckDB analytical database, automated checks, statistical comparisons, and a Streamlit dashboard.

Its goal is to turn raw mobility data into understandable evidence that can inform operational decisions while making assumptions, uncertainty, and data limitations visible.

## 🎯 Business Question

**What can Q2 2024 NYC mobility data tell us about where and when taxi demand concentrates, and which operational opportunities deserve further testing?**

The dashboard supports exploration of historical demand patterns. It does not establish that a new taxi operator would be profitable, nor does it prove that weather or another factor caused a demand change.

## 💡 Business Decisions and Recommendations

The current recommendation is a **conditional go for two small operational pilots**, followed by an evidence-based review before scaling.

### 1. Airport-focused supply and pricing operations

**Business opportunity**

Investigate whether airport-related trips at JFK and LaGuardia support a viable operational strategy. The analysis compares airport activity and amount-per-mile metrics, including sensitivity checks and statistical uncertainty.

**Recommended action**

Run a limited airport-focused pilot using an operator-specific baseline. Track:

- Completed trips and realized fare.
- Empty and repositioning miles.
- Driver time and utilization.
- Driver incentives and operating costs.
- Cancellations and service outcomes.
- Contribution margin after relevant costs.

**Expected impact**

The pilot can establish whether airport-focused operations merit further investment and identify the conditions under which the economics may be attractive.

**Risks and limitations**

Recorded trip amounts and amount-per-mile are not profit. Trip mix, distance, tolls, driver costs, deadheading, time of day, and airport operating constraints may change the result.

**Decision rule:** do not scale based on fare metrics alone. Validate unit economics with actual operating costs.

### 2. Peak-hour fleet positioning

**Business opportunity**

Investigate whether taxi demand is concentrated at particular hours and pickup zones, including late-afternoon activity.

**Recommended action**

Test a small, time-bounded fleet-positioning intervention in selected zones against a comparable baseline or control period.

Measure:

- Completed trips per driver-hour.
- Passenger wait time.
- Empty and repositioning distance.
- Driver utilization.
- Cancellations.
- Net contribution after operating costs.

**Expected impact**

A controlled pilot can help determine whether targeted positioning improves utilization and service outcomes without creating excessive empty mileage.

**Risks and limitations**

High historical pickup counts do not necessarily mean unmet demand or future profitability. Rankings depend on the selected time window, filters, source coverage, and aggregation grain.

**Decision rule:** compare the pilot with a predefined baseline and expand only if the measured results justify it.

### Overall recommendation

Proceed with controlled pilots rather than an unconditional market-entry decision. Establish baseline metrics, define success and stop criteria in advance, measure costs, and review the results before scaling.

## 📊 Dashboard Features

MetroPulse contains six dashboard sections:

1. **Executive overview** — headline indicators and business recommendation.
2. **Temporal demand** — hourly and time-based taxi demand patterns.
3. **Geographic demand** — pickup-zone comparisons.
4. **Fares & payments** — fare and payment-related metrics.
5. **Weather & subway** — descriptive comparisons involving weather, taxi activity, and recorded subway ridership.
6. **Data quality** — completeness, validity, timestamp, and reconciliation checks.

Interactive filters include the date range, weather condition, day type, and hour of day.

### Dashboard Screenshots

Add screenshots captured from your live dashboard. These suggested filenames keep the repository organized.

| View | Screenshot path |
|---|---|
| Executive overview | `docs/assets/dashboard-overview.png` |
| Temporal demand | `docs/assets/temporal-demand.png` |
| Geographic demand | `docs/assets/geographic-demand.png` |
| Fares and payments | `docs/assets/fares-payments.png` |
| Weather and subway | `docs/assets/weather-subway.png` |
| Data quality | `docs/assets/data-quality.png` |

Example Markdown for displaying an image:

```markdown
![MetroPulse executive overview](docs/assets/dashboard-overview.png)
```

Create the `docs/assets/` folder and add your actual image files before committing the screenshots. Do not leave broken image links in the final README.

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Ingestion, data processing, validation, and dashboard logic |
| Streamlit | Interactive dashboard and user-facing filters |
| DuckDB | Analytical database and SQL execution |
| SQL | Staging, intermediate transformations, and analytical marts |
| pandas | Tabular data manipulation |
| PyArrow | Parquet data processing |
| Plotly and Streamlit chart components | Data visualization |
| GeoPandas | Geospatial processing where used |
| pytest | Automated testing and reconciliation checks |
| Parquet, CSV, JSON | Source data, processed outputs, and metadata |
| Git and GitHub | Version control and public source repository |
| Streamlit Community Cloud | Public dashboard hosting |

The exact dependencies are listed in `requirements.txt`. Only claim additional libraries or a dependency lock file if they are actually present in the repository.

## 🗃️ Data Sources and Study Period

The project focuses on April 1 through June 30, 2024, using public-source data relating to:

- NYC TLC yellow taxi trip records for April, May, and June 2024.
- Taxi-zone lookup and geographic reference data.
- Open-Meteo historical weather observations.
- MTA subway ridership records for the corresponding period.

Large raw datasets are intentionally excluded from Git. The repository contains ingestion scripts and source metadata intended to support acquisition and reconstruction of the analytical outputs.

## 🧪 Data Quality and Reconciliation

The existing generated quality report records:

- **10,777,315** rows in the intermediate taxi dataset.
- **10,777,291** rows within the Q2 pickup-timestamp window.
- **24** records outside that window.
- Matching staging and intermediate row counts in the recorded reconciliation.
- Expected monthly source counts for April, May, and June 2024.

The Q2 window is defined as:

`[2024-04-01 00:00:00, 2024-07-01 00:00:00)`

The 24 out-of-window records are retained in the source and intermediate layers but excluded from Q2-specific metrics. The quality report classifies 17 as older/future timestamp anomalies and 7 as adjacent-period boundary records. This classification alone does not prove that a record is invalid.

Other reviewed conditions include missing or zero passenger counts, negative fares or total amounts, nonpositive or missing trip distance, and zero or negative duration.

These conditions are flagged for interpretation; they should not automatically be described as fraud or treated as invalid without a clearly defined rule.

Detailed output: [`reports/data_quality_report.json`](reports/data_quality_report.json)

## 📈 Statistical Analysis and Interpretation

The project includes uncertainty intervals for selected comparisons and sensitivity checks for airport amount-per-mile metrics.

Detailed analysis: [`reports/statistical_analysis.md`](reports/statistical_analysis.md)

Important limitations:

- Weather comparisons are descriptive and unadjusted; they do not establish causation.
- Airport amount-per-mile differences are not profit estimates.
- Observational results may be affected by time, location, trip mix, service availability, and other confounders.
- Bootstrap intervals depend on the resampling method and may not fully account for serial dependence.
- Sensitivity checks using the same data are robustness checks, not independent replications.
- Taxi trips and subway station-hour ridership have different grains and coverage, so they should not be treated as a direct passenger-for-passenger comparison.
- Historical Q2 2024 patterns are not a current demand forecast.

## ⚡ Query Performance

The query optimization report compares selected baseline queries with mart-backed queries and documents result validation.

Reported timings are environment-specific and apply to the queries benchmarked. They should not be presented as a guaranteed speedup for the entire dashboard.

See [`docs/query_optimization_report.md`](docs/query_optimization_report.md) and the benchmark JSON files in `reports/`.

## 🏗️ Project Structure

The main project files include:

- `app.py` — Streamlit dashboard.
- `build_all.py` — analytical build orchestration.
- `requirements.txt` — Python dependencies.
- `AI_USAGE.md` — AI-use disclosure.
- `src/ingestion/` — source ingestion and preparation scripts.
- `tests/` — automated data and model checks.
- `data/metadata/` — source inventory and ingestion metadata.
- `data/processed/` — processed analytical outputs where included.
- `reports/` — quality, statistical, and query benchmark reports.
- `docs/` — metric dictionary, SQL inventory, optimization report, and executive memo.
- SQL transformation directory — confirm the exact folder name in the repository before documenting it.

## 🚀 Getting Started

### Prerequisites

- Python 3.12, or a version confirmed compatible with the dependencies and deployment runtime.
- Git.
- Access to the public source datasets required by the ingestion workflow.

### 1. Clone the repository

```bash
git clone https://github.com/Prer26/MetroPulse.git
cd MetroPulse
```

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Run the dashboard

```bash
python -m streamlit run app.py
```

Open the local URL printed by Streamlit in your browser.

## ✅ Validation

Run the automated tests:

```bash
python -m pytest tests -v
```

Compile-check the dashboard:

```bash
python -m py_compile app.py
```

Sixteen tests previously passed in the local environment. Re-run the commands after the final changes and use the final results in your submission.

Passing tests alone does not prove that all ingestion steps or a clean end-to-end rebuild work.

## 🔁 Data Reproducibility

The repository excludes large raw datasets, so a fresh environment must acquire the source data before rebuilding the analytical database and outputs.

Before claiming that the entire pipeline is reproducible, test the complete workflow in a clean environment and document the exact sequence for:

1. Downloading TLC taxi, weather, and taxi-zone data.
2. Acquiring MTA records for the full analysis window.
3. Building DuckDB tables and SQL outputs in dependency order.
4. Regenerating quality and statistical reports.
5. Running tests and confirming source-to-mart reconciliations.

Do not treat an existing local `metropulse.duckdb` as proof that a clean rebuild succeeds. Verify the current ingestion and build scripts, required inputs, and execution order before running the pipeline.

Do not commit raw data, secrets, API tokens, or local credentials.

## 📚 Documentation

- [`docs/metric_dictionary.md`](docs/metric_dictionary.md) — metric definitions, grains, filters, and interpretation notes.
- [`docs/sql_transformation_inventory.md`](docs/sql_transformation_inventory.md) — SQL model inventory.
- [`docs/query_optimization_report.md`](docs/query_optimization_report.md) — benchmark and optimization notes.
- [`docs/executive_memo.md`](docs/executive_memo.md) — executive decision memo; verify the final rendered memo is one page.
- [`reports/statistical_analysis.md`](reports/statistical_analysis.md) — statistical comparisons and limitations.
- [`reports/data_quality_report.json`](reports/data_quality_report.json) — generated quality report.
- [`AI_USAGE.md`](AI_USAGE.md) — AI-use disclosure.

## 🤖 AI Use

See [`AI_USAGE.md`](AI_USAGE.md) for the project's AI-use disclosure. Keep it accurate and consistent with the assistance and tools used during the project.

## 🔐 Dependencies and Environment

- `requirements.txt` lists runtime dependencies.
- Confirm whether an environment example file and a dependency lock file exist in the final repository.
- If the assessment requires these files, add and test them before submission.
- Keep secrets and local environment files out of Git.
- The public dashboard and source workflow should not depend on evaluator-owned credentials or paid services.

## 🌐 Deployment and Submission

- **Public repository:** https://github.com/Prer26/MetroPulse
- **Live dashboard:** https://metropulse-d79bit6957zkt6me5ro6mu.streamlit.app/
- **Final commit SHA:** add the SHA of the final commit after all approved changes are committed.
- **Explainer video:** (https://drive.google.com/file/d/1iD0QUpmUDlifsplttKS7RNvoYn3G3XD_/view?usp=sharing)  https://drive.google.com/file/d/1oyojVe7VXOyIlVoLZJXWYVPYUCsvIc_y/view?usp=sharing



---

<div align="center">

**MetroPulse — Data-informed mobility decisions, with uncertainty made visible.**

</div>
