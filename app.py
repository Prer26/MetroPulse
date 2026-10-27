from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st
import geopandas as gpd
import plotly.express as px
import zipfile
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"
DB_PATH = ROOT / "metropulse.duckdb"
ZONE_LOOKUP_PATH = ROOT / "data" / "raw" / "zones" / "taxi_zone_lookup.csv"

st.set_page_config(
    page_title="MetroPulse | NYC Mobility Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.35rem; padding-bottom: 2.2rem; max-width: 1600px;}
      [data-testid="stMetric"] {
          background: rgba(120, 120, 120, 0.045);
          border: 1px solid rgba(120, 120, 120, 0.14);
          padding: 12px 15px;
          border-radius: 14px;
      }
      [data-testid="stMetricLabel"] {font-size: .88rem;}
      [data-testid="stMetricValue"] {font-size: 1.65rem;}
      div[data-testid="stHorizontalBlock"] {gap: 1rem;}
      .hero {
          padding: 1.2rem 1.45rem;
          border-radius: 18px;
          border: 1px solid rgba(120,120,120,.18);
          background: linear-gradient(115deg, rgba(86,130,180,.13), rgba(88,170,145,.07));
          margin-bottom: .8rem;
      }
      div[data-testid="stDataFrame"] {border-radius: 12px; overflow: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner="Loading MetroPulse datasets...")
def load_parquet(filename: str) -> pd.DataFrame:
    path = DATA / filename
    if not path.exists():
        return pd.DataFrame()
    con = duckdb.connect()
    try:
        return con.execute("SELECT * FROM read_parquet(?)", [str(path)]).fetchdf()
    finally:
        con.close()


@st.cache_data(show_spinner=False)
def load_zone_lookup() -> pd.DataFrame:
    if not ZONE_LOOKUP_PATH.exists():
        return pd.DataFrame(columns=["LocationID", "Borough", "Zone", "service_zone"])
    return pd.read_csv(ZONE_LOOKUP_PATH)


@st.cache_data(show_spinner="Preparing trip filter options...")
def load_trip_filter_options():
    """Load optional trip filters; cloud deployments may not include raw Parquet sources."""
    if not DB_PATH.exists():
        return {"payments": [], "rates": []}
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        payments = con.execute(
            "SELECT DISTINCT payment_type FROM int_taxi_trips "
            "WHERE payment_type IS NOT NULL ORDER BY payment_type"
        ).fetchdf()["payment_type"].tolist()
        rates = con.execute(
            "SELECT DISTINCT RatecodeID FROM int_taxi_trips "
            "WHERE RatecodeID IS NOT NULL ORDER BY RatecodeID"
        ).fetchdf()["RatecodeID"].tolist()
        return {"payments": [int(x) for x in payments], "rates": [int(x) for x in rates]}
    except Exception:
        # The view may reference raw Parquet files that are intentionally not deployed.
        return {"payments": [], "rates": []}
    finally:
        con.close()


def payment_label(code):
    labels = {
        0: "0 - Unknown / unmapped",
        1: "1 - Credit card",
        2: "2 - Cash",
        3: "3 - No charge",
        4: "4 - Dispute",
        5: "5 - Unknown",
        6: "6 - Voided trip",
    }
    return labels.get(int(code), f"{code} - Other / unmapped")


def rate_label(code):
    labels = {
        1: "1 - Standard rate",
        2: "2 - JFK",
        3: "3 - Newark",
        4: "4 - Nassau or Westchester",
        5: "5 - Negotiated fare",
        6: "6 - Group ride",
    }
    return labels.get(int(code), f"{code} - Unknown / other")


def query_filtered_trips(
    start_date, end_date, pickup_boroughs, pickup_zones, dropoff_zones,
    payment_types, rate_codes, airport_filter
):
    """Return filtered trip-level summaries from DuckDB; never load all trips into Streamlit."""
    if not DB_PATH.exists():
        return pd.DataFrame(), pd.DataFrame(), "Database file not found."

    where = [
        "t.pickup_date BETWEEN ? AND ?",
        "t.PULocationID = pu.LocationID",
        "t.DOLocationID = dof.LocationID",
    ]
    params = [str(start_date), str(end_date)]

    if pickup_boroughs:
        where.append("pu.Borough IN (" + ",".join(["?"] * len(pickup_boroughs)) + ")")
        params.extend(pickup_boroughs)
    if pickup_zones:
        where.append("pu.Zone IN (" + ",".join(["?"] * len(pickup_zones)) + ")")
        params.extend(pickup_zones)
    if dropoff_zones:
        where.append("dof.Zone IN (" + ",".join(["?"] * len(dropoff_zones)) + ")")
        params.extend(dropoff_zones)
    if payment_types:
        where.append("t.payment_type IN (" + ",".join(["?"] * len(payment_types)) + ")")
        params.extend(payment_types)
    if rate_codes:
        where.append("t.RatecodeID IN (" + ",".join(["?"] * len(rate_codes)) + ")")
        params.extend(rate_codes)

    if airport_filter == "Airport pickups (JFK + LaGuardia)":
        where.append("t.PULocationID IN (132, 138)")
    elif airport_filter == "Non-airport pickups":
        where.append("(t.PULocationID NOT IN (132, 138) OR t.PULocationID IS NULL)")

    where_sql = " AND ".join(where)
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        summary = con.execute(f"""
            SELECT
                COUNT(*) AS trips,
                SUM(COALESCE(t.passenger_count, 0)) AS recorded_passengers,
                SUM(t.fare_amount) AS recorded_fares,
                SUM(t.tip_amount) AS recorded_tips,
                SUM(t.total_amount) AS recorded_amount,
                AVG(t.total_amount) AS avg_recorded_amount,
                MEDIAN(t.total_amount) AS median_recorded_amount,
                MEDIAN(t.trip_distance) FILTER (WHERE t.trip_distance > 0) AS median_distance_miles,
                COUNT(*) FILTER (WHERE t.has_missing_passenger_count) AS missing_passenger_count_trips,
                COUNT(*) FILTER (WHERE t.has_invalid_distance) AS invalid_distance_trips,
                COUNT(*) FILTER (WHERE t.has_negative_fare) AS negative_fare_trips,
                COUNT(*) FILTER (WHERE t.has_negative_duration) AS negative_duration_trips
            FROM int_taxi_trips t
            JOIN taxi_zone_lookup pu ON t.PULocationID = pu.LocationID
            JOIN taxi_zone_lookup dof ON t.DOLocationID = dof.LocationID
            WHERE {where_sql}
        """, params).fetchdf()

        by_payment = con.execute(f"""
            SELECT
                t.payment_type,
                COUNT(*) AS trip_count,
                SUM(t.total_amount) AS recorded_amount,
                SUM(t.fare_amount) AS recorded_fare,
                SUM(t.tip_amount) AS recorded_tips,
                AVG(t.total_amount) AS avg_recorded_amount
            FROM int_taxi_trips t
            JOIN taxi_zone_lookup pu ON t.PULocationID = pu.LocationID
            JOIN taxi_zone_lookup dof ON t.DOLocationID = dof.LocationID
            WHERE {where_sql}
            GROUP BY t.payment_type
            ORDER BY trip_count DESC
        """, params).fetchdf()
        return summary, by_payment, None
    except Exception as exc:
        return pd.DataFrame(), pd.DataFrame(), str(exc)
    finally:
        con.close()


hourly = load_parquet("taxi_transit_weather_hourly.parquet")
zones = load_parquet("pickup_zone_metrics.parquet")
airport = load_parquet("airport_daily_unit_economics.parquet")
airport_sensitivity = load_parquet("airport_sensitivity.parquet")
payment_fares = load_parquet("payment_fare_metrics.parquet")

if hourly.empty:
    st.title("MetroPulse")
    st.error("The combined hourly dataset could not be found. Build the taxi, subway and weather marts first.")
    st.code("python .\\src\\ingestion\\build_taxi_transit_weather_hourly.py")
    st.stop()

hourly["hour_start"] = pd.to_datetime(hourly["hour_start"])
hourly["is_rainy_hour"] = hourly["is_rainy_hour"].astype(bool)
hourly["service_date"] = hourly["hour_start"].dt.date
hourly["hour_of_day"] = hourly["hour_start"].dt.hour
hourly["day_type"] = hourly["hour_start"].dt.dayofweek.map(
    lambda x: "Weekend" if x >= 5 else "Weekday"
)

min_date = hourly["hour_start"].min().date()
max_date = hourly["hour_start"].max().date()

st.sidebar.markdown("#  MetroPulse")
st.sidebar.caption("NYC mobility intelligence")
st.sidebar.divider()
st.sidebar.subheader("Dashboard filters")

start_date = st.sidebar.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

if start_date > end_date:
    st.sidebar.error("Start date must be on or before end date.")
    st.stop()

rain_filter = st.sidebar.selectbox("Weather condition", ["All hours", "Rainy hours", "Non-rainy hours"])
day_filter = st.sidebar.selectbox("Day type", ["All days", "Weekdays", "Weekends"])
# Empty multiselects intentionally mean "All" in the trip query. This avoids filling the UI
# with dozens of selected chips on first load while still allowing searchable narrowing.
selected_hours = st.sidebar.multiselect(
    "Hour of day (optional)", list(range(24)), default=[],
    format_func=lambda hour: f"{hour:02d}:00",
    placeholder="All 24 hours"
)

zone_lookup = load_zone_lookup()
filter_options = load_trip_filter_options()

with st.sidebar.expander("Trip-level filters", expanded=False):
    borough_options = sorted(zone_lookup["Borough"].dropna().astype(str).unique().tolist()) if not zone_lookup.empty else []
    selected_boroughs = st.multiselect(
        "Pickup borough (optional)", borough_options, default=[],
        placeholder="All boroughs"
    )

    pickup_options = sorted(
        zone_lookup.loc[zone_lookup["Borough"].isin(selected_boroughs), "Zone"].dropna().astype(str).unique().tolist()
    ) if selected_boroughs and not zone_lookup.empty else (
        sorted(zone_lookup["Zone"].dropna().astype(str).unique().tolist()) if not zone_lookup.empty else []
    )
    selected_pickups = st.multiselect(
        "Pickup zone (optional)", pickup_options, default=[],
        placeholder="All pickup zones"
    )

    dropoff_options = sorted(zone_lookup["Zone"].dropna().astype(str).unique().tolist()) if not zone_lookup.empty else []
    selected_dropoffs = st.multiselect(
        "Drop-off zone (optional)", dropoff_options, default=[],
        placeholder="All drop-off zones"
    )

    payment_options = filter_options["payments"]
    selected_payments = st.multiselect(
        "Payment type (optional)", payment_options, default=[],
        format_func=payment_label, placeholder="All payment types"
    )
    rate_options = filter_options["rates"]
    selected_rates = st.multiselect(
        "Rate type (optional)", rate_options, default=[],
        format_func=rate_label, placeholder="All rate types"
    )
    airport_filter = st.selectbox(
        "Airport pickup",
        ["All trips", "Airport pickups (JFK + LaGuardia)", "Non-airport pickups"],
        help="Airport pickup uses JFK (132) and LaGuardia (138) pickup-zone IDs. Newark (1) is not included in this definition."
    )

filtered = hourly[
    (hourly["service_date"] >= start_date)
    & (hourly["service_date"] <= end_date)
].copy()
if rain_filter == "Rainy hours":
    filtered = filtered[filtered["is_rainy_hour"]]
elif rain_filter == "Non-rainy hours":
    filtered = filtered[~filtered["is_rainy_hour"]]
if day_filter == "Weekdays":
    filtered = filtered[filtered["day_type"] == "Weekday"]
elif day_filter == "Weekends":
    filtered = filtered[filtered["day_type"] == "Weekend"]
if selected_hours:
    filtered = filtered[filtered["hour_of_day"].isin(selected_hours)]

st.sidebar.divider()
st.sidebar.caption("Source period: April to June 2024")
st.sidebar.caption("Leave optional filters empty to include all values. Hourly charts use the combined pre-aggregated mart; trip-level filters apply to the trip summary and payment breakdown.")

st.markdown(
    """
    <div class="hero">
      <h1 style="margin:0;">MetroPulse</h1>
      <p style="margin:.35rem 0 0 0;">
        NYC Mobility Intelligence | Taxi demand, subway ridership, weather and data quality
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    f"Selected period: {start_date:%b %d, %Y}  to  {end_date:%b %d, %Y} "
    f"| {len(filtered):,} hourly observations after filters"
)

if filtered.empty:
    st.warning("No observations match the selected date, weather, day-type and hour filters.")
    st.stop()

# TRIP-LEVEL SUMMARY
# Trip-level views depend on raw Parquet files that are intentionally not deployed to Streamlit Cloud.
# Keep the optional section graceful when those files are unavailable; pre-aggregated marts power the dashboard below.
st.markdown("### Trip-level snapshot")
trip_summary, trip_payment_summary, trip_error = query_filtered_trips(
    start_date,
    end_date,
    selected_boroughs,
    selected_pickups,
    selected_dropoffs,
    selected_payments,
    selected_rates,
    airport_filter,
)
if trip_error:
    # Hide the optional trip-level warning in the cloud dashboard.
    pass
elif not trip_summary.empty:
    row = trip_summary.iloc[0]
    a, b, c, d = st.columns(4)
    a.metric("Filtered trips", f"{int(row['trips'] or 0):,}")
    b.metric(
        "Recorded amount",
        "N/A" if pd.isna(row["recorded_amount"]) else f"${row['recorded_amount']:,.0f}",
    )
    c.metric(
        "Recorded tips",
        "N/A" if pd.isna(row["recorded_tips"]) else f"${row['recorded_tips']:,.0f}",
    )
    d.metric("Invalid-distance trips", f"{int(row['invalid_distance_trips'] or 0):,}")
    st.caption(
        "These trip-level metrics respond to the borough, pickup/drop-off zone, payment, rate and airport filters. "
        "The six analytical tabs below continue to use their stated hourly/monthly grains."
    )
    if not trip_payment_summary.empty:
        st.markdown("#### Payment breakdown for selected trips")
        payment_view = trip_payment_summary.copy()
        payment_view["payment_label"] = payment_view["payment_type"].map(
            lambda value: payment_label(value) if pd.notna(value) else "Null / missing"
        )
        payment_view["trip_share_pct"] = (
            100 * payment_view["trip_count"] / max(trip_payment_summary["trip_count"].sum(), 1)
        )
        st.dataframe(
            payment_view[[
                "payment_label", "trip_count", "trip_share_pct",
                "recorded_amount", "recorded_fare", "recorded_tips", "avg_recorded_amount"
            ]].round(2),
            hide_index=True,
            use_container_width=True,
        )
else:
    st.info("No trip-level results matched the selected trip filters.")

tab_exec, tab_time, tab_geo, tab_fares, tab_weather, tab_quality = st.tabs(
    ["Executive overview", "Temporal demand", "Geographic demand", "Fares & payments", "Weather & subway", "Data quality"]
)

# EXECUTIVE OVERVIEW
with tab_exec:
    st.subheader("Quarter-to-date mobility snapshot")
    trips = int(filtered["taxi_trips"].sum())
    ridership = int(filtered["total_ridership"].sum())
    mean_trips = filtered["taxi_trips"].mean()
    rain = filtered[filtered["is_rainy_hour"]]
    dry = filtered[~filtered["is_rainy_hour"]]
    rain_diff = rain["taxi_trips"].mean() - dry["taxi_trips"].mean() if not rain.empty and not dry.empty else None

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Taxi trips", f"{trips:,}")
    k2.metric("Recorded subway ridership", f"{ridership:,.0f}")
    k3.metric("Average taxi trips / hour", f"{mean_trips:,.0f}")
    k4.metric("Rainy vs. dry difference", "N/A" if rain_diff is None else f"{rain_diff:+,.0f}",
              help="Difference in mean hourly taxi trips. Descriptive and unadjusted; not causal.")

    st.caption("Taxi trips are summed from hourly aggregates. Subway ridership is the sum of recorded station-hour ridership values. Rain comparison is descriptive, unadjusted and not causal.")

    # Evidence-led investment decision with compact pilot cards and a four-week roadmap.
    st.markdown("### Business decision: should a company enter NYC's taxi market?")
    st.info(
        "**Recommendation: CONDITIONAL GO for two small operational pilots.** "
        "Q2 data shows meaningful airport activity and concentrated Manhattan demand "
        "during the late afternoon. It does not prove that a new operator would be "
        "profitable. Validate unit economics before scaling."
    )

    st.markdown("#### Opportunity evidence")
    ev1, ev2, ev3, ev4 = st.columns(4)
    ev1.metric("Q2 taxi trips", "10.78M")
    ev2.metric("Airport trip share", "7.81%")
    ev3.metric("JFK Q2 pickups", "487,038")
    ev4.metric(
        "Busiest pickup hour", "6 PM",
        help="765,822 pickups across the quarter in the underlying hourly demand analysis."
    )

    st.markdown("### Recommended operational pilots")
    st.caption(
        "Start small, compare with control shifts, and scale only if measured unit economics support it."
    )
    pilot1, pilot2 = st.columns(2, gap="large")

    with pilot1:
        with st.container(border=True):
            st.markdown("####  Pilot 1 | Airport operations")
            st.caption("START SMALL | JFK BENCHMARKED AGAINST LGA")
            a1, a2 = st.columns(2)
            a1.metric("JFK pickups", "487,038")
            a2.metric("LaGuardia pickups", "354,408")
            st.markdown("**Average recorded amount per trip**")
            a1, a2 = st.columns(2)
            a1.metric("JFK", "$77.26")
            a2.metric("LaGuardia", "$67.09")
            st.divider()
            st.markdown("**Measure success by**")
            st.markdown(
                "- Net contribution per vehicle-hour\n"
                "- Queue and passenger waiting time\n"
                "- Empty return miles and operating costs"
            )

    with pilot2:
        with st.container(border=True):
            st.markdown("####  Pilot 2 | Peak-hour positioning")
            st.caption("TEST WINDOW | 4 to 7 PM | HIGH-VOLUME MANHATTAN")
            p1, p2 = st.columns(2)
            p1.metric("Midtown Center", "125,014", help="Pickups during the 4 to 6 PM analysis window.")
            p2.metric("Upper East Side South", "116,284", help="Pickups during the 4 to 6 PM analysis window.")
            st.markdown("**Compare pilot shifts with control shifts**")
            st.markdown(
                "- Trips per vehicle-hour\n"
                "- Empty miles per completed trip\n"
                "- Pickup waiting time and net contribution"
            )

    st.markdown("### Four-week pilot roadmap")
    weeks = st.columns(4, gap="small")
    roadmap = [
        ("WEEK 1", "Baseline", "Measure demand, costs, utilization and empty miles."),
        ("WEEK 2", "Launch", "Start both limited pilots."),
        ("WEEK 3", "Optimize", "Compare pilot and control shifts."),
        ("WEEK 4", "Decide", "Scale, extend or stop each pilot."),
    ]
    for col, (week, heading, detail) in zip(weeks, roadmap):
        with col:
            with st.container(border=True):
                st.caption(week)
                st.markdown(f"**{heading}**")
                st.caption(detail)

    st.markdown("### Proposed scale-up criteria")
    criteria1, criteria2 = st.columns(2, gap="medium")
    with criteria1:
        st.markdown(
            "- **>=10%** improvement in contribution per vehicle-hour\n"
            "- **>=8%** fewer empty miles per completed trip"
        )
    with criteria2:
        st.markdown(
            "- No material decline in service quality\n"
            "- Positive contribution after measured variable costs"
        )
    st.caption(
        "Targets are proposed, not observed results. Recorded trip amounts are not profit. "
        "Validate driver payouts, vehicle costs, utilization, airport waiting time and empty return "
        "journeys before scaling. Evidence covers Q2 2024 and is not a current-market forecast."
    )

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown("#### Daily taxi demand")
        daily = filtered.groupby("service_date", as_index=False).agg(taxi_trips=("taxi_trips", "sum"))
        st.line_chart(daily.set_index("service_date"), y="taxi_trips", use_container_width=True)
    with right:
        st.markdown("#### Average taxi trips by weather")
        split = filtered.groupby("is_rainy_hour", as_index=False).agg(
            hours=("hour_start", "size"), avg_taxi_trips=("taxi_trips", "mean")
        )
        split["Condition"] = split["is_rainy_hour"].map({True: "Rainy", False: "Non-rainy"})
        st.bar_chart(split.set_index("Condition")[["avg_taxi_trips"]], use_container_width=True)
        st.dataframe(split[["Condition", "hours", "avg_taxi_trips"]].round(2), hide_index=True, use_container_width=True)

# TEMPORAL DEMAND
with tab_time:
    st.subheader("When does demand occur?")
    st.caption("Explore the daily rhythm of taxi demand and compare weekday and weekend patterns for the selected period.")

    # Summarise the observed hours, then highlight the busiest hour without implying causality.
    by_hour = filtered.groupby("hour_of_day", as_index=False).agg(
        avg_taxi_trips=("taxi_trips", "mean"),
        median_taxi_trips=("taxi_trips", "median"),
        hours_observed=("hour_start", "size"),
        avg_recorded_amount=("avg_recorded_amount", "mean"),
        median_duration_minutes=("median_duration_minutes", "median"),
    ).sort_values("hour_of_day")

    if not by_hour.empty:
        peak = by_hour.loc[by_hour["avg_taxi_trips"].idxmax()]
        quiet = by_hour.loc[by_hour["avg_taxi_trips"].idxmin()]
        peak_hour_label = f"{int(peak['hour_of_day']):02d}:00 to {(int(peak['hour_of_day']) + 1) % 24:02d}:00"
        quiet_hour_label = f"{int(quiet['hour_of_day']):02d}:00 to {(int(quiet['hour_of_day']) + 1) % 24:02d}:00"
        m1, m2, m3 = st.columns(3)
        m1.metric("Busiest average hour", peak_hour_label, help="Hour with the highest mean taxi-trip count in the filtered observations.")
        m2.metric("Peak-hour average trips", f"{peak['avg_taxi_trips']:,.0f}")
        m3.metric("Quietest average hour", quiet_hour_label, help="Hour with the lowest mean taxi-trip count in the filtered observations.")

    left, right = st.columns([1, 1.15])
    with left:
        st.markdown("#### Average taxi trips by hour")
        st.bar_chart(by_hour.set_index("hour_of_day")[["avg_taxi_trips"]], use_container_width=True)
        st.caption("Each bar is the mean across observed instances of that hour, not the total for the entire quarter.")
    with right:
        st.markdown("#### Weekday vs. weekend profile")
        by_day_hour = filtered.groupby(["hour_of_day", "day_type"], as_index=False).agg(
            avg_taxi_trips=("taxi_trips", "mean"),
            hours_observed=("hour_start", "size"),
        )
        if not by_day_hour.empty:
            pivot = by_day_hour.pivot(index="hour_of_day", columns="day_type", values="avg_taxi_trips")
            st.line_chart(pivot, use_container_width=True)
            st.caption("Compare the shape of demand across the day. Unequal observation counts can affect averages.")
        else:
            st.info("Not enough observations for a weekday/weekend comparison.")

    st.markdown("#### Hourly demand detail")
    display_table = by_hour.rename(columns={
        "hour_of_day": "Hour (24h)",
        "hours_observed": "Observed hours",
        "avg_taxi_trips": "Average taxi trips",
        "median_taxi_trips": "Median taxi trips",
        "median_duration_minutes": "Median duration (min)",
        "avg_recorded_amount": "Average recorded amount ($)",
    })
    st.dataframe(display_table.round(2), hide_index=True, use_container_width=True)
    st.caption("Hourly profiles average the observations that remain after the date, weather, day-type and hour filters. Recorded amounts are not profit or operator revenue.")

# GEOGRAPHIC DEMAND
with tab_geo:
    st.subheader("Where do pickups concentrate?")
    st.caption("Compare pickup hotspots and borough-level demand for the months covered by the selected date range.")
    if zones.empty:
        st.warning(r"Pickup-zone dataset not found. Build it with `python .\src\ingestion\build_pickup_zone_metrics.py`.")
    else:
        zone_data = zones.copy()
        start_month = pd.Timestamp(start_date).strftime("%Y-%m")
        end_month = pd.Timestamp(end_date).strftime("%Y-%m")
        zone_data = zone_data[(zone_data["source_month"] >= start_month) & (zone_data["source_month"] <= end_month)]
        if zone_data.empty:
            st.info("No monthly zone aggregates match the selected dates.")
        else:
            st.caption("Note: zone metrics are monthly aggregates. Selecting part of a month includes that full month's zone totals.")
            zone_summary = zone_data.groupby(["pickup_zone", "pickup_borough"], as_index=False).agg(
                total_trips=("total_trips", "sum"),
                total_recorded_amount=("total_recorded_amount", "sum"),
                invalid_distance_trips=("invalid_distance_trips", "sum"),
                median_distance_miles=("median_distance_miles", "median"),
            ).sort_values("total_trips", ascending=False)
            zone_total = zone_summary["total_trips"].sum()
            zone_summary["trip_share_pct"] = zone_summary["total_trips"] / zone_total * 100 if zone_total else 0

            # REAL TAXI ZONE CHOROPLETH MAP
            st.markdown("#### NYC pickup demand map")
            st.caption(
                "Each taxi-zone polygon is shaded by recorded pickup trips "
                "for the selected monthly aggregates."
            )

            shapefile_zip = ROOT / "data" / "raw" / "zones" / "taxi_zones.zip"

            try:
                if not shapefile_zip.exists():
                    st.warning(
                        "Taxi-zone boundaries are unavailable. "
                        "Place taxi_zones.zip in data/raw/zones/."
                    )
                else:
                    # Read official zone polygons from the ZIP shapefile.
                    with zipfile.ZipFile(shapefile_zip) as archive:
                        shp_name = next(
                            name for name in archive.namelist()
                            if name.lower().endswith(".shp")
                        )
                        shp_folder = Path("data") / "raw" / "zones" / "_map_shapes"
                        shp_folder.mkdir(parents=True, exist_ok=True)
                        archive.extractall(shp_folder)

                    shp_path = shp_folder / shp_name
                    zone_shapes = gpd.read_file(shp_path)

                    # Normalize the shapefile ID column.
                    id_candidates = [
                        col for col in zone_shapes.columns
                        if col.lower() in {"locationid", "location_id"}
                    ]
                    if not id_candidates:
                        st.error(
                            "Could not identify the taxi-zone ID in the shapefile. "
                            f"Available columns: {list(zone_shapes.columns)}"
                        )
                    else:
                        shape_id = id_candidates[0]
                        zone_shapes["LocationID"] = (
                            pd.to_numeric(zone_shapes[shape_id], errors="coerce")
                            .astype("Int64")
                        )

                        # Aggregate by zone ID, not zone name, to avoid
                        # accidentally combining zones with similar names.
                        map_metrics = (
                            zone_data.groupby("pickup_location_id", as_index=False)
                            .agg(total_trips=("total_trips", "sum"))
                        )
                        map_metrics["pickup_location_id"] = (
                            pd.to_numeric(
                                map_metrics["pickup_location_id"],
                                errors="coerce"
                            ).astype("Int64")
                        )

                        map_data = zone_shapes.merge(
                            map_metrics,
                            left_on="LocationID",
                            right_on="pickup_location_id",
                            how="left",
                            validate="one_to_one",
                        )
                        map_data["total_trips"] = (
                            map_data["total_trips"].fillna(0)
                        )

                        # Plotly's geographic map requires longitude/latitude.
                        if map_data.crs is not None:
                            map_data = map_data.to_crs(epsg=4326)

                        geojson = map_data.__geo_interface__
                        map_data["LocationID"] = map_data["LocationID"].astype(str)

                        fig = px.choropleth_map(
                            map_data,
                            geojson=geojson,
                            locations="LocationID",
                            featureidkey="properties.LocationID",
                            color="total_trips",
                            hover_name=(
                                "zone" if "zone" in map_data.columns
                                else "Zone" if "Zone" in map_data.columns
                                else "LocationID"
                            ),
                            hover_data={
                                "LocationID": True,
                                "total_trips": ":,.0f",
                            },
                            color_continuous_scale="Viridis",
                            map_style="carto-positron",
                            zoom=8.5,
                            center={"lat": 40.73, "lon": -73.94},
                            opacity=0.72,
                            labels={
                                "total_trips": "Pickup trips",
                                "LocationID": "Taxi zone ID",
                            },
                        )
                        fig.update_layout(
                            height=650,
                            margin={"r": 0, "t": 10, "l": 0, "b": 0},
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.caption(
                            "Source: NYC TLC taxi-zone boundaries and MetroPulse "
                            "pickup-zone aggregates. Zone totals are monthly "
                            "aggregates; partial-month date selections include "
                            "the full selected months."
                        )

            except Exception as exc:
                st.warning(
                    "The pickup-demand map could not be rendered. "
                    f"Check the shapefile, CRS and map dependencies. Details: {exc}"
                )

            a, b, c = st.columns(3)
            a.metric("Pickup zones", f"{zone_summary['pickup_zone'].nunique():,}")
            b.metric("Trips in selected monthly aggregates", f"{int(zone_total):,}")
            c.metric("Unlabelled zones", f"{int(zone_summary['pickup_zone'].isna().sum()):,}")
            left, right = st.columns([1.15, 1])
            with left:
                st.markdown("#### 15 busiest pickup zones")
                top = zone_summary.head(15).sort_values("total_trips")
                st.bar_chart(top.set_index("pickup_zone")[["total_trips"]], horizontal=True, use_container_width=True)
            with right:
                st.markdown("#### Demand by borough")
                borough = zone_summary.groupby("pickup_borough", as_index=False).agg(
                    total_trips=("total_trips", "sum"),
                    total_recorded_amount=("total_recorded_amount", "sum"),
                ).sort_values("total_trips", ascending=False)
                st.bar_chart(borough.set_index("pickup_borough")[["total_trips"]], horizontal=True, use_container_width=True)
                st.dataframe(borough.rename(columns={"pickup_borough":"Borough", "total_trips":"Trips", "total_recorded_amount":"Recorded amount ($)"}).round(2), hide_index=True, use_container_width=True)
            st.markdown("#### Explore pickup zones")
            borough_options = sorted(zone_summary["pickup_borough"].dropna().astype(str).unique().tolist())
            chosen_boroughs = st.multiselect("Filter boroughs", borough_options, key="geo_borough_filter", placeholder="All boroughs")
            detail = zone_summary if not chosen_boroughs else zone_summary[zone_summary["pickup_borough"].astype(str).isin(chosen_boroughs)]
            st.dataframe(detail[["pickup_zone", "pickup_borough", "total_trips", "trip_share_pct", "total_recorded_amount", "median_distance_miles", "invalid_distance_trips"]].rename(columns={"pickup_zone":"Pickup zone", "pickup_borough":"Borough", "total_trips":"Trips", "trip_share_pct":"Share of zone trips (%)", "total_recorded_amount":"Recorded amount ($)", "median_distance_miles":"Median distance (mi)", "invalid_distance_trips":"Invalid-distance trips"}).round(2), hide_index=True, use_container_width=True)

# FARES AND PAYMENTS
with tab_fares:
    st.subheader("Fares, payments and recorded trip economics")
    st.caption(
        "Recorded trip amounts are not profit or operator revenue. "
        "Payment-code labels are provisional and should be validated against source documentation."
    )

    if payment_fares.empty:
        st.warning(
            "The payment/fare mart is not available. Build it with "
            "`python .\\src\\ingestion\\build_payment_fare_metrics.py`."
        )
    else:
        pf = payment_fares.copy()
        pf["source_month"] = pf["source_month"].astype(str)
        selected_start_month = pd.Timestamp(start_date).strftime("%Y-%m")
        selected_end_month = pd.Timestamp(end_date).strftime("%Y-%m")
        pf = pf[
            (pf["source_month"] >= selected_start_month)
            & (pf["source_month"] <= selected_end_month)
        ].copy()

        if pf.empty:
            st.info("No payment/fare monthly summaries match the selected date range.")
        else:
            st.info(
                "Payment and fare summaries are monthly aggregates. "
                "If the selected dates cover only part of a month, the entire selected month is included."
            )

            month_totals = (
                pf.groupby("source_month", as_index=False)
                .agg(
                    trips=("trip_count", "sum"),
                    recorded_amount=("total_recorded_amount", "sum"),
                    recorded_fares=("total_recorded_fare", "sum"),
                    recorded_tips=("total_recorded_tips", "sum"),
                )
                .sort_values("source_month")
            )

            total_payment_trips = int(pf["trip_count"].sum())
            total_recorded_amount = pf["total_recorded_amount"].sum()
            total_recorded_tips = pf["total_recorded_tips"].sum()

            k1, k2, k3 = st.columns(3)
            k1.metric("Trips in payment mart", f"{total_payment_trips:,}")
            k2.metric(
                "Recorded amount",
                "N/A" if pd.isna(total_recorded_amount) else f"${total_recorded_amount:,.0f}",
            )
            k3.metric(
                "Recorded tips",
                "N/A" if pd.isna(total_recorded_tips) else f"${total_recorded_tips:,.0f}",
            )

            left, right = st.columns(2)
            with left:
                st.markdown("#### Recorded amount by month")
                st.bar_chart(
                    month_totals.set_index("source_month")[["recorded_amount"]],
                    use_container_width=True,
                )
            with right:
                st.markdown("#### Recorded tips by month")
                st.bar_chart(
                    month_totals.set_index("source_month")[["recorded_tips"]],
                    use_container_width=True,
                )

            st.markdown("#### Payment-method mix")
            payment_summary = (
                pf.groupby(["payment_type", "payment_label"], as_index=False)
                .agg(
                    trip_count=("trip_count", "sum"),
                    recorded_amount=("total_recorded_amount", "sum"),
                    recorded_fare=("total_recorded_fare", "sum"),
                    recorded_tips=("total_recorded_tips", "sum"),
                    negative_fare_trips=("negative_fare_trips", "sum"),
                    negative_total_trips=("negative_total_trips", "sum"),
                    invalid_distance_trips=("invalid_distance_trips", "sum"),
                )
                .sort_values("trip_count", ascending=False)
            )
            denominator = payment_summary["trip_count"].sum()
            payment_summary["trip_share_pct"] = (
                100 * payment_summary["trip_count"] / denominator
                if denominator
                else 0.0
            )
            st.bar_chart(
                payment_summary.set_index("payment_label")[["trip_count"]],
                horizontal=True,
                use_container_width=True,
            )
            st.dataframe(
                payment_summary[
                    [
                        "payment_type",
                        "payment_label",
                        "trip_count",
                        "trip_share_pct",
                        "recorded_amount",
                        "recorded_fare",
                        "recorded_tips",
                        "negative_fare_trips",
                        "negative_total_trips",
                        "invalid_distance_trips",
                    ]
                ].round(2),
                hide_index=True,
                use_container_width=True,
            )

            st.markdown("#### Card tip-to-fare ratio by month")
            card_tips = pf[pf["payment_type"] == 1].copy()
            if not card_tips.empty:
                st.line_chart(
                    card_tips.set_index("source_month")[["card_tip_to_fare_pct"]],
                    use_container_width=True,
                )
                st.caption(
                    "This ratio uses card trips with positive recorded fares and non-null recorded tips. "
                    "It is not a measure of driver earnings or profit."
                )
            else:
                st.info("No eligible card-payment observations are available for this period.")

            st.markdown("#### Monthly payment/fare detail")
            st.dataframe(
                pf.sort_values(["source_month", "payment_type"]),
                hide_index=True,
                use_container_width=True,
            )

    st.markdown("#### Average recorded amount by hour")
    amount_hour = filtered.groupby("hour_of_day", as_index=False).agg(
        avg_recorded_amount=("avg_recorded_amount", "mean")
    )
    st.bar_chart(
        amount_hour.set_index("hour_of_day"),
        y="avg_recorded_amount",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Airport daily unit economics")
    st.caption(
        "Compare JFK and LaGuardia using the selected date range. "
        "Recorded trip amounts are not profit."
    )

    if not airport.empty:
        airport_view = airport.copy()
        if "pickup_date" in airport_view.columns:
            airport_view["pickup_date"] = pd.to_datetime(
                airport_view["pickup_date"], errors="coerce"
            )
            airport_view = airport_view[
                (airport_view["pickup_date"].dt.date >= start_date)
                & (airport_view["pickup_date"].dt.date <= end_date)
            ]

        if not airport_view.empty:
            airport_chart = (
                airport_view.groupby("airport", as_index=False)
                .agg(
                    eligible_trips=("eligible_trips", "sum"),
                    median_amount_per_mile=("median_amount_per_mile", "median"),
                )
                .sort_values("median_amount_per_mile", ascending=True)
            )

            st.markdown("##### Median daily recorded amount per mile")
            st.bar_chart(
                airport_chart.set_index("airport")[["median_amount_per_mile"]],
                horizontal=True,
                use_container_width=True,
            )

            st.markdown("##### Eligible trip volume")
            st.bar_chart(
                airport_chart.set_index("airport")[["eligible_trips"]],
                horizontal=True,
                use_container_width=True,
            )

            st.markdown("##### Daily unit-economics detail")
            st.dataframe(
                airport_view,
                hide_index=True,
                use_container_width=True,
            )
            st.caption(
                "Amount per mile is the median of daily airport medians "
                "within the selected dates. Eligible trip volume is summed "
                "across those dates. Neither metric measures profit."
            )
        else:
            st.info("No airport observations match the selected date range.")
    else:
        st.info("Airport unit-economics mart is not available.")

    if not airport_sensitivity.empty:
        st.markdown("#### Sensitivity to recorded-amount cap")
        sensitivity_view = airport_sensitivity.rename(columns={
            "amount_cap": "Recorded amount cap ($)",
            "matched_days": "Matched dates",
            "avg_daily_median_jfk": "JFK median ($/mile)",
            "avg_daily_median_lga": "LaGuardia median ($/mile)",
            "avg_daily_difference": "Difference ($/mile)",
            "pct_higher_at_lga": "LaGuardia higher (%)",
        }).copy()

        numeric_columns = [
            "JFK median ($/mile)",
            "LaGuardia median ($/mile)",
            "Difference ($/mile)",
            "LaGuardia higher (%)",
        ]
        for column in numeric_columns:
            if column in sensitivity_view.columns:
                sensitivity_view[column] = sensitivity_view[column].map(
                    lambda value: f"{value:,.3f}" if pd.notna(value) else "N/A"
                )

        st.dataframe(
            sensitivity_view,
            hide_index=True,
            use_container_width=True,
        )
        st.caption(
            "Sensitivity scenarios reuse the same underlying trips. "
            "Recorded amount per mile is not profit."
        )

    st.info(
        "Payment-code labels are provisional. Unknown or unmapped codes "
        "remain visible until verified against source documentation."
    )

# WEATHER AND SUBWAY
with tab_weather:
    st.subheader("How do weather and transit align with taxi demand?")
    st.caption("These are descriptive hourly relationships. They should not be interpreted as causal effects.")
    weather = filtered.groupby("is_rainy_hour", as_index=False).agg(
        hours=("hour_start", "size"), avg_taxi_trips=("taxi_trips", "mean"),
        median_taxi_trips=("taxi_trips", "median"), avg_ridership=("total_ridership", "mean"),
        avg_transfers=("total_transfers", "mean"), avg_precipitation_mm=("precipitation_mm", "mean"),
        avg_temperature_c=("temperature_c", "mean"), avg_wind_speed_kmh=("wind_speed_kmh", "mean"),
    )
    weather["Condition"] = weather["is_rainy_hour"].map({True: "Rainy", False: "Non-rainy"})
    rain_row = weather[weather["is_rainy_hour"] == True]
    dry_row = weather[weather["is_rainy_hour"] == False]
    if not rain_row.empty and not dry_row.empty:
        rain_avg = float(rain_row.iloc[0]["avg_taxi_trips"])
        dry_avg = float(dry_row.iloc[0]["avg_taxi_trips"])
        delta = rain_avg - dry_avg
        m1, m2, m3 = st.columns(3)
        m1.metric("Rainy-hour average trips", f"{rain_avg:,.0f}")
        m2.metric("Non-rainy-hour average trips", f"{dry_avg:,.0f}")
        m3.metric("Rainy minus non-rainy", f"{delta:+,.0f}", help="Unadjusted difference in observed hourly averages; not causal.")
    st.markdown("#### Weather comparison")
    st.dataframe(weather[["Condition", "hours", "avg_taxi_trips", "median_taxi_trips", "avg_ridership", "avg_transfers", "avg_precipitation_mm", "avg_temperature_c", "avg_wind_speed_kmh"]].round(2), hide_index=True, use_container_width=True)
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("#### Taxi demand vs. recorded subway ridership")
        st.scatter_chart(filtered, x="total_ridership", y="taxi_trips", color="is_rainy_hour", use_container_width=True)
    with right:
        st.markdown("#### Hourly transit relationship")
        if len(filtered) >= 3 and filtered["total_ridership"].nunique() > 1:
            corr = filtered[["taxi_trips", "total_ridership"]].corr().iloc[0, 1]
            st.metric("Pearson correlation", f"{corr:.3f}")
            st.caption("Correlation can reflect shared daily and weekly patterns.")
        else:
            st.info("Not enough variation in the selected observations to calculate correlation.")
        transit_summary = filtered[["total_ridership", "total_transfers", "taxi_trips"]].corr(numeric_only=True)
        st.dataframe(transit_summary.round(3), use_container_width=True)
    st.caption("Ridership is summed recorded station-hour ridership, not necessarily unique people. Rainy-hour comparisons are descriptive and unadjusted.")

# DATA QUALITY
with tab_quality:
    import json

    st.subheader("Data quality and coverage")
    st.caption(
        "Trip-level checks come from the saved full-dataset audit. "
        "Hourly checks below are separate and respond to the dashboard filters."
    )

    report_path = ROOT / "reports" / "data_quality_report.json"

    if report_path.exists():
        try:
            with report_path.open("r", encoding="utf-8-sig") as report_file:
                audit = json.load(report_file)

            audit_checks = audit.get("checks", [])
            q2_reconciliation = audit.get("q2_window_reconciliation", {})

            metric1, metric2, metric3 = st.columns(3)
            metric1.metric(
                "Audited trip rows",
                f"{audit.get('source_row_count', 0):,}"
            )
            metric2.metric(
                "Checks run",
                f"{audit.get('checks_run', len(audit_checks)):,}"
            )
            metric3.metric(
                "Items requiring review",
                f"{audit.get('review_items', 0):,}"
            )

            st.markdown("#### Full trip-level audit")
            st.caption(
                f"Generated: {audit.get('generated_at', 'Not recorded')} | "
                f"Source: {audit.get('source_table', 'Not recorded')}"
            )

            audit_table = pd.DataFrame([
                {
                    "Check": item.get("check", "Unnamed check"),
                    "Status": item.get("status", "UNKNOWN"),
                    "Severity": item.get("severity", "unknown"),
                    "Details": item.get("details", "")
                }
                for item in audit_checks
            ])

            if not audit_table.empty:
                st.dataframe(
                    audit_table,
                    hide_index=True,
                    use_container_width=True
                )

            if q2_reconciliation:
                st.markdown("#### Q2 2024 timestamp reconciliation")

                rec1, rec2, rec3 = st.columns(3)
                rec1.metric(
                    "Rows inside Q2 window",
                    f"{q2_reconciliation.get('in_window_rows', 0):,}"
                )
                rec2.metric(
                    "Rows outside Q2 window",
                    f"{q2_reconciliation.get('out_of_window_rows', 0):,}"
                )
                rec3.metric(
                    "Timestamp anomalies",
                    f"{q2_reconciliation.get('older_or_future_timestamp_anomalies', 0):,}"
                )

                st.caption(
                    "Q2 window: "
                    f"{q2_reconciliation.get('period_start_inclusive', 'Not recorded')} "
                    "inclusive to "
                    f"{q2_reconciliation.get('period_end_exclusive', 'Not recorded')} "
                    "exclusive."
                )
                st.info(q2_reconciliation.get(
                    "handling_rule",
                    "No timestamp handling rule recorded."
                ))
                st.caption(q2_reconciliation.get(
                    "classification_note",
                    "Timestamp classification may not establish record validity."
                ))
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            st.error(f"Could not load the saved trip-level quality report: {exc}")
    else:
        st.warning(
            "The full trip-level quality report is unavailable. "
            "Ensure reports/data_quality_report.json is included in the deployment."
        )

    st.markdown("#### Hourly quality checks")
    trips = int(filtered["taxi_trips"].sum())
    invalid_distance = int(filtered["invalid_distance_trips"].sum())
    invalid_pct = 100 * invalid_distance / trips if trips else 0
    missing_temp = int(filtered["temperature_c"].isna().sum())
    missing_rider = int(filtered["total_ridership"].isna().sum())
    missing_weather = int(
        filtered[["temperature_c", "precipitation_mm", "wind_speed_kmh"]]
        .isna()
        .any(axis=1)
        .sum()
    )

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Hourly observations", f"{len(filtered):,}")
    q2.metric("Taxi trips in filtered hours", f"{trips:,}")
    q3.metric("Invalid-distance share", f"{invalid_pct:.2f}%")
    q4.metric("Hours missing weather fields", f"{missing_weather:,}")

    quality_table = pd.DataFrame([
        {
            "Check": "Hourly observations",
            "Count": len(filtered),
            "Interpretation": "Hourly rows after dashboard filters."
        },
        {
            "Check": "Taxi trips flagged for invalid distance",
            "Count": invalid_distance,
            "Interpretation": "Invalid-distance trip counts carried by hourly aggregates."
        },
        {
            "Check": "Hours with missing temperature",
            "Count": missing_temp,
            "Interpretation": "Hourly rows without temperature."
        },
        {
            "Check": "Hours with missing subway ridership",
            "Count": missing_rider,
            "Interpretation": "Hourly rows without recorded ridership."
        },
        {
            "Check": "Hours with any missing weather field",
            "Count": missing_weather,
            "Interpretation": "At least one available weather measurement is missing."
        },
    ])

    st.dataframe(
        quality_table,
        hide_index=True,
        use_container_width=True
    )

    st.markdown("#### Invalid-distance share by hour")
    quality_by_hour = filtered.groupby(
        "hour_of_day",
        as_index=False
    ).agg(
        invalid_distance_trips=("invalid_distance_trips", "sum"),
        taxi_trips=("taxi_trips", "sum")
    )
    quality_by_hour["invalid_distance_pct"] = (
        100 * quality_by_hour["invalid_distance_trips"]
        / quality_by_hour["taxi_trips"].replace(0, pd.NA)
    )
    st.bar_chart(
        quality_by_hour.set_index("hour_of_day")[["invalid_distance_pct"]],
        use_container_width=True
    )

st.divider()
st.caption(
    f"MetroPulse | Data period Apr to Jun 2024 | Dashboard refreshed {pd.Timestamp.now():%Y-%m-%d %H:%M} | "
    "Figures are based on available pre-aggregated marts."
)

