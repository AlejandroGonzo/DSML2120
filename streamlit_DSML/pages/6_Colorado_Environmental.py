import streamlit as st
import pandas as pd
import plotly.express as px
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
    "Exploring air quality, weather, and household "
    "energy consumption across Colorado during 2025."
)

st.caption(
    "Data source: Synthetic classroom datasets. "
    "Results do not represent actual Colorado measurements."
)

# ---- Sidebar Filters ----
st.sidebar.header("🔎 Dashboard Filters")

if st.sidebar.button("🔄 Reset Filters"):
    st.session_state["reset_filters"] = True

if st.session_state.pop("reset_filters", False):
    for key in [
        "city_filter",
        "month_filter",
        "home_filter",
        "ev_filter",
        "solar_filter",
        "region_filter"
    ]:
        st.session_state.pop(key, None)

st.sidebar.subheader("🌤️ Air Quality")

selected_cities = st.sidebar.multiselect(
    "Select Cities",
    options=sorted(air_quality["city"].unique()),
    default=sorted(air_quality["city"].unique()),
    key="city_filter"
)

st.sidebar.subheader("📅 Time Period")

month_range = st.sidebar.slider(
    "Select Months",
    min_value=1,
    max_value=12,
    value=(1, 12),
    key="month_filter"
)

st.sidebar.subheader("🏠 Home Energy")

selected_regions = st.sidebar.multiselect(
    "Select Regions",
    options=sorted(energy["region"].unique()),
    default=sorted(energy["region"].unique()),
    key="region_filter"
)

selected_home_types = st.sidebar.multiselect(
    "Select Home Types",
    options=sorted(energy["home_type"].unique()),
    default=sorted(energy["home_type"].unique()),
    key="home_filter"
)

selected_ev = st.sidebar.selectbox(
    "Electric Vehicle Ownership",
    ["All Households", "Yes", "No"],
    key="ev_filter"
)

selected_solar = st.sidebar.selectbox(
    "Solar Panel Ownership",
    ["All Households", "Yes", "No"],
    key="solar_filter"
)

# ---- Filter Datasets ----
filtered_air = air_quality[
    air_quality["city"].isin(selected_cities)
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

if selected_ev != "All Households":
    filtered_energy = filtered_energy[
        filtered_energy["has_ev"] == selected_ev
    ]

if selected_solar != "All Households":
    filtered_energy = filtered_energy[
        filtered_energy["has_solar"] == selected_solar
    ]

if filtered_air.empty or filtered_energy.empty:
    st.warning(
        "No data available for these filters. "
        "Please change your selections."
    )
    st.stop()

# ---- KPI Cards ----
st.header("📊 Environmental Overview")

average_aqi = filtered_air["aqi"].mean()
average_energy = filtered_energy["kwh_used"].mean()

solar_households = filtered_energy.loc[
    filtered_energy["has_solar"] == "Yes",
    "household_id"
].nunique()

total_households = filtered_energy["household_id"].nunique()

solar_percentage = (
    solar_households / total_households * 100
    if total_households > 0 else 0
)

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(
        "🌤️ Average AQI",
        f"{average_aqi:.1f}"
    )

with kpi2:
    st.metric(
        "⚡ Average Energy Use",
        f"{average_energy:,.0f} kWh"
    )

with kpi3:
    st.metric(
        "🌱 Solar Adoption",
        f"{solar_percentage:.1f}%"
    )

st.divider()

# ---- Row 1: Air Quality Analysis ----
st.header("🌤️ Colorado Air Quality Analysis")

col1, col2 = st.columns(2, gap="large")

# ---- Question 1 ----
with col1:
    st.subheader(
        "Q1: Does wildfire smoke make Colorado's air quality worse?"
    )

    smoke_data = (
        filtered_air.groupby(
            "wildfire_smoke", as_index=False
        )["aqi"]
        .mean()
    )

    smoke_data["wildfire_smoke"] = smoke_data[
        "wildfire_smoke"
    ].replace({
        "Yes": "Smoke",
        "No": "No Smoke"
    })

    fig1 = px.bar(
        smoke_data,
        x="wildfire_smoke",
        y="aqi",
        color="wildfire_smoke",
        color_discrete_map={
            "Smoke": "#FF6B6B",
            "No Smoke": "#4DA8FF"
        },
        labels={
            "wildfire_smoke": "Wildfire Smoke",
            "aqi": "Average Air Quality Index"
        },
        text_auto=".1f"
    )

    fig1.update_layout(
        showlegend=False,
        height=350,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.caption(
        "Columns: wildfire_smoke, aqi | Chart: Bar chart"
    )

# ---- Question 2 ----
with col2:
    st.subheader(
        "Q2: Is temperature related to air pollution in Colorado?"
    )

    pollution_data = filtered_air.dropna(
        subset=["temp_f", "pm25_ugm3"]
    )

    fig2 = px.scatter(
        pollution_data,
        x="temp_f",
        y="pm25_ugm3",
        color="city",
        opacity=0.65,
        labels={
            "temp_f": "Temperature (°F)",
            "pm25_ugm3": "PM2.5 (µg/m³)",
            "city": "City"
        },
        hover_data=["date"]
    )

    fig2.update_layout(
        height=350,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.caption(
        "Columns: temp_f, pm25_ugm3 | Chart: Scatter plot"
    )

st.divider()

# ---- Row 2: Home Energy Analysis ----
st.header("⚡ Colorado Home Energy Analysis")

col3, col4 = st.columns(2, gap="large")

# ---- Question 3 ----
with col3:
    st.subheader(
        "Q3: Do different types of homes use different amounts of electricity?"
    )

    home_data = (
        filtered_energy.groupby(
            "home_type", as_index=False
        )["kwh_used"]
        .mean()
        .sort_values("kwh_used", ascending=False)
    )

    fig3 = px.bar(
        home_data,
        x="home_type",
        y="kwh_used",
        color="home_type",
        labels={
            "home_type": "Home Type",
            "kwh_used": "Average Electricity Use (kWh)"
        },
        text_auto=".0f"
    )

    fig3.update_layout(
        showlegend=False,
        height=350,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.caption(
        "Columns: home_type, kwh_used | Chart: Bar chart"
    )

# ---- Question 4 ----
with col4:
    st.subheader(
        "Q4: Do households with electric vehicles use more electricity?"
    )

    ev_data = (
        filtered_energy.groupby(
            "has_ev", as_index=False
        )["kwh_used"]
        .mean()
    )

    ev_data["has_ev"] = ev_data["has_ev"].replace({
        "Yes": "Has EV",
        "No": "No EV"
    })

    fig4 = px.bar(
        ev_data,
        x="has_ev",
        y="kwh_used",
        color="has_ev",
        color_discrete_map={
            "Has EV": "#A66BFF",
            "No EV": "#4DA8FF"
        },
        labels={
            "has_ev": "Electric Vehicle Ownership",
            "kwh_used": "Average Electricity Use (kWh)"
        },
        text_auto=".0f"
    )

    fig4.update_layout(
        showlegend=False,
        height=350,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    st.caption(
        "Columns: has_ev, kwh_used | Chart: Bar chart"
    )

st.divider()

# ---- Key Insights ----
st.header("💡 Key Insights")

insight1, insight2, insight3 = st.columns(3)

with insight1:
    st.subheader("🔥 Wildfire Smoke")

    smoke_lookup = smoke_data.set_index(
        "wildfire_smoke"
    )["aqi"]

    if {"Smoke", "No Smoke"}.issubset(smoke_lookup.index):
        smoke_avg = smoke_lookup["Smoke"]
        no_smoke_avg = smoke_lookup["No Smoke"]

        st.write(
            f"Average AQI with smoke: **{smoke_avg:.1f}**"
        )

        st.write(
            f"Average AQI without smoke: **{no_smoke_avg:.1f}**"
        )
    else:
        st.write(
            "Both smoke and non-smoke observations "
            "are needed for comparison."
        )

with insight2:
    st.subheader("🏠 Home Energy")

    highest_home = home_data.iloc[0]

    st.write(
        f"**{highest_home['home_type']}** homes have "
        "the highest average electricity use "
        "among the selected home types."
    )

    st.write(
        f"Average: **{highest_home['kwh_used']:,.0f} kWh**"
    )

with insight3:
    st.subheader("🚗 Electric Vehicles")

    ev_lookup = ev_data.set_index("has_ev")["kwh_used"]

    if {"Has EV", "No EV"}.issubset(ev_lookup.index):
        ev_avg = ev_lookup["Has EV"]
        no_ev_avg = ev_lookup["No EV"]

        difference = ev_avg - no_ev_avg

        st.write(
            f"Households with EVs average **{ev_avg:,.0f} kWh**."
        )

        st.write(
            f"Households without EVs average "
            f"**{no_ev_avg:,.0f} kWh**."
        )

        st.write(
            f"Difference: **{difference:+,.0f} kWh**"
        )
    else:
        st.write(
            "Select both EV ownership groups "
            "to compare their electricity use."
        )

st.divider()

# ---- Dataset Explorer ----
st.header("📁 Explore the Data")

tab1, tab2 = st.tabs([
    "🌤️ Air Quality Dataset",
    "⚡ Home Energy Dataset"
])

with tab1:
    st.dataframe(
        filtered_air,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Air Quality Data",
        filtered_air.to_csv(index=False),
        file_name="filtered_air_quality.csv",
        mime="text/csv"
    )

with tab2:
    st.dataframe(
        filtered_energy,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Home Energy Data",
        filtered_energy.to_csv(index=False),
        file_name="filtered_home_energy.csv",
        mime="text/csv"
    )

# ---- Dashboard Information ----
with st.expander("ℹ️ About This Dashboard"):
    st.write(
        "This dashboard uses two synthetic datasets "
        "created for DSML 2120."
    )

    st.write(
        "The Colorado Air Quality dataset contains "
        "information about pollution, temperature, "
        "and wildfire smoke."
    )

    st.write(
        "The Home Energy dataset contains information "
        "about electricity consumption, home types, "
        "solar panels, and electric vehicles."
    )

    st.write(
        "All charts use filtered data and update "
        "when sidebar selections change."
    )

    st.write(
        "Comparisons show relationships in the data "
        "and do not prove cause and effect."
    )