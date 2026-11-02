import streamlit as st
import pandas as pd
from pathlib import Path

# ---- Page Configuration ----
st.set_page_config(
    page_title="Colorado Environmental Dashboard",
    page_icon="🏔️",
    layout="wide"
)

# ---- Load CSV Files ----
data_folder = Path(__file__).resolve().parent.parent / "Data"

@st.cache_data
def load_data():
    air = pd.read_csv(data_folder / "colorado_air_quality.csv")
    energy = pd.read_csv(data_folder / "home_energy_use.csv")

    air["date"] = pd.to_datetime(air["date"])
    energy["month"] = pd.to_datetime(energy["month"])

    return air, energy

air_quality, energy = load_data()

# ---- Dashboard Title ----
st.title("🏔️ Colorado Environmental Dashboard")

st.write(
    "Exploring air quality, wildfire smoke, electricity consumption, "
    "and household energy costs across Colorado during 2025."
)

st.caption(
    "Data source: Synthetic classroom datasets. "
    "These observations do not represent actual Colorado measurements."
)

# ---- Sidebar Filters ----
st.sidebar.header("Dashboard Filters")

st.sidebar.subheader("Air Quality Filters")

selected_cities = st.sidebar.multiselect(
    "Select Cities",
    options=sorted(air_quality["city"].unique()),
    default=sorted(air_quality["city"].unique())
)

selected_aqi = st.sidebar.multiselect(
    "AQI Category",
    options=sorted(air_quality["aqi_category"].unique()),
    default=sorted(air_quality["aqi_category"].unique())
)

st.sidebar.subheader("Time Period")

month_range = st.sidebar.slider(
    "Select Months",
    min_value=1,
    max_value=12,
    value=(1, 12)
)

st.sidebar.subheader("Home Energy Filters")

selected_regions = st.sidebar.multiselect(
    "Select Regions",
    options=sorted(energy["region"].unique()),
    default=sorted(energy["region"].unique())
)

selected_home_types = st.sidebar.multiselect(
    "Select Home Types",
    options=sorted(energy["home_type"].unique()),
    default=sorted(energy["home_type"].unique())
)

# ---- Filter Data ----
filtered_air = air_quality[
    air_quality["city"].isin(selected_cities)
    & air_quality["aqi_category"].isin(selected_aqi)
    & air_quality["date"].dt.month.between(
        month_range[0], month_range[1]
    )
].copy()

filtered_energy = energy[
    energy["region"].isin(selected_regions)
    & energy["home_type"].isin(selected_home_types)
    & energy["month"].dt.month.between(
        month_range[0], month_range[1]
    )
].copy()

if filtered_air.empty or filtered_energy.empty:
    st.warning(
        "No data available for the selected filters. "
        "Please adjust your selections."
    )
    st.stop()

# ---- Calculate Dashboard Metrics ----
average_aqi = filtered_air["aqi"].mean()

smoke_observations = (
    filtered_air["wildfire_smoke"] == "Yes"
).sum()

city_aqi = (
    filtered_air.groupby("city")["aqi"]
    .mean()
    .sort_values(ascending=False)
)

highest_aqi_city = city_aqi.index[0]

average_kwh = filtered_energy["kwh_used"].mean()

average_bill = filtered_energy["bill_usd"].mean()

solar_households = filtered_energy.loc[
    filtered_energy["has_solar"] == "Yes",
    "household_id"
].nunique()

# ---- Row 1: Air Quality KPI Cards ----
st.header("🌤️ Colorado Air Quality Overview")

kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric(
    "Average AQI",
    f"{average_aqi:.1f}"
)

kpi2.metric(
    "Smoke Observations",
    f"{smoke_observations:,}"
)

kpi3.metric(
    "Highest Average AQI City",
    highest_aqi_city,
    delta=f"{city_aqi.iloc[0]:.1f} AQI",
    delta_color="off"
)

# ---- Row 2: Air Quality Charts ----
st.write("### Row 2: Colorado Air Quality")

col1, col2 = st.columns(2)

daily_aqi = (
    filtered_air.groupby("date", as_index=False)["aqi"]
    .mean()
)

with col1:
    st.subheader("Air Quality Trends Over Time")

    st.line_chart(
        daily_aqi,
        x="date",
        y="aqi"
    )

    st.caption(
        "Average daily Air Quality Index across selected cities."
    )

with col2:
    st.subheader("Average Air Quality by City")

    st.bar_chart(
        city_aqi
    )

    st.caption(
        "Higher AQI values indicate worse air quality."
    )

# ---- Row 3: Home Energy KPI Cards ----
st.header("⚡ Colorado Home Energy Overview")

kpi4, kpi5, kpi6 = st.columns(3)

kpi4.metric(
    "Average Electricity Use",
    f"{average_kwh:,.0f} kWh"
)

kpi5.metric(
    "Average Monthly Bill",
    f"${average_bill:,.2f}"
)

kpi6.metric(
    "Households With Solar",
    f"{solar_households:,}"
)

# ---- Row 4: Home Energy Charts ----
st.write("### Row 4: Colorado Home Energy Use")

colA, colB, colC = st.columns(3)

monthly_energy = (
    filtered_energy.groupby("month", as_index=False)["kwh_used"]
    .mean()
)

monthly_bills = (
    filtered_energy.groupby("month", as_index=False)["bill_usd"]
    .mean()
)

solar_comparison = (
    filtered_energy.groupby("has_solar")["bill_usd"]
    .mean()
    .rename(index={"Yes": "Solar", "No": "No Solar"})
)

with colA:
    st.subheader("Monthly Electricity Consumption")

    st.line_chart(
        monthly_energy,
        x="month",
        y="kwh_used"
    )

    st.caption(
        "Average monthly electricity consumption per household."
    )

with colB:
    st.subheader("Average Electricity Bills")

    st.line_chart(
        monthly_bills,
        x="month",
        y="bill_usd"
    )

    st.caption(
        "Average monthly household electricity bills in USD."
    )

with colC:
    st.subheader("Solar vs. Non-Solar Homes")

    st.bar_chart(
        solar_comparison
    )

    st.caption(
        "Average electricity bills by solar panel ownership. "
        "This comparison does not establish solar savings."
    )

# ---- Row 5: Additional Environmental Analysis ----
st.header("📊 Environmental Analysis")

col4, col5 = st.columns(2)

with col4:
    st.subheader("Temperature vs. Air Quality")

    st.scatter_chart(
        filtered_air,
        x="temp_f",
        y="aqi",
        color="city"
    )

    st.caption(
        "Relationship between temperature (°F) and AQI."
    )

with col5:
    st.subheader("Impact of Wildfire Smoke")

    smoke_comparison = (
        filtered_air.groupby("wildfire_smoke")["aqi"]
        .mean()
        .rename(index={"Yes": "Smoke", "No": "No Smoke"})
    )

    st.bar_chart(
        smoke_comparison
    )

    st.caption(
        "Average AQI for observations with and without wildfire smoke."
    )

# ---- Row 6: Key Insights ----
st.header("💡 Key Insights")

highest_month = (
    filtered_air.assign(
        month_number=filtered_air["date"].dt.month
    )
    .groupby("month_number")["aqi"]
    .mean()
    .idxmax()
)

highest_month_name = pd.Timestamp(
    year=2025,
    month=int(highest_month),
    day=1
).strftime("%B")

peak_energy_month = monthly_energy.loc[
    monthly_energy["kwh_used"].idxmax(),
    "month"
].strftime("%B")

st.write(
    f"**1. Air Quality:** {highest_aqi_city} has the highest "
    f"average AQI ({city_aqi.iloc[0]:.1f}) among selected cities."
)

st.write(
    f"**2. Seasonal Trends:** {highest_month_name} has the "
    "highest average AQI in the selected period."
)

st.write(
    f"**3. Energy Consumption:** {peak_energy_month} has the "
    "highest average household electricity consumption "
    "in the selected data."
)

if {"Yes", "No"}.issubset(set(smoke_comparison.index)):
    smoke_aqi = smoke_comparison["Smoke"]
    no_smoke_aqi = smoke_comparison["No Smoke"]

    st.write(
        f"**4. Wildfire Smoke:** Average AQI is {smoke_aqi:.1f} "
        f"with smoke compared with {no_smoke_aqi:.1f} without smoke."
    )
else:
    st.write(
        "**4. Wildfire Smoke:** Both smoke and non-smoke "
        "observations are needed for a comparison."
    )

# ---- Row 7: Dataset Tables ----
st.header("📁 Explore the Datasets")

tab1, tab2 = st.tabs([
    "🌤️ Air Quality Data",
    "⚡ Home Energy Data"
])

with tab1:
    st.subheader("Colorado Air Quality Dataset")

    st.dataframe(
        filtered_air,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Air Quality CSV",
        data=filtered_air.to_csv(index=False),
        file_name="filtered_colorado_air_quality.csv",
        mime="text/csv"
    )

with tab2:
    st.subheader("Colorado Home Energy Dataset")

    st.dataframe(
        filtered_energy,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Home Energy CSV",
        data=filtered_energy.to_csv(index=False),
        file_name="filtered_home_energy_use.csv",
        mime="text/csv"
    )

# ---- Dashboard Information ----
with st.expander("About This Dashboard"):
    st.write(
        "This interactive dashboard analyzes two synthetic "
        "Colorado environmental datasets from 2025."
    )

    st.write(
        "The air quality dataset contains measurements "
        "of AQI, temperature, and wildfire smoke."
    )

    st.write(
        "The home energy dataset contains household "
        "electricity consumption, energy bills, and solar information."
    )

    st.write(
        "Use the sidebar filters to explore different "
        "cities, regions, home types, and months."
    )

    st.info(
        "These are synthetic classroom datasets. "
        "The two datasets describe different observations "
        "and are analyzed separately rather than joined."
    )