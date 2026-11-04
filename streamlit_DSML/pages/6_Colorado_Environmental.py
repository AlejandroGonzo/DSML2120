
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---- Page Configuration ----
st.set_page_config(
    page_title="Colorado Environmental Dashboard",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Dark Theme ----
st.markdown("""
<style>
.stApp {
    background-color: #0B1220;
    color: #E8EEF7;
}
.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
[data-testid="stSidebar"] {
    background-color: #111D30;
}
h1, h2, h3 {
    color: #F1F5FA;
}
[data-testid="stMetric"] {
    background-color: #16243A;
    border: 1px solid #30425B;
    border-radius: 12px;
    padding: 18px;
}
[data-testid="stMetricValue"] {
    color: #73D7D0;
}
</style>
""", unsafe_allow_html=True)

# ---- Load Data ----
DATA_FOLDER = Path(__file__).resolve().parent.parent / "Data"

@st.cache_data
def load_data():
    air = pd.read_csv(
        DATA_FOLDER / "colorado_air_quality.csv"
    )
    energy = pd.read_csv(
        DATA_FOLDER / "home_energy_use.csv"
    )

    air["date"] = pd.to_datetime(air["date"])
    energy["month"] = pd.to_datetime(energy["month"])

    return air, energy

try:
    air_quality, energy = load_data()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Unable to load the datasets: {error}")
    st.stop()

# ---- Reset Filters ----
def reset_filters():
    for key in [
        "city_filter",
        "month_filter",
        "region_filter",
        "home_filter",
        "ev_filter",
        "solar_filter"
    ]:
        st.session_state.pop(key, None)

# ---- Sidebar Filters ----
with st.sidebar:
    st.title("🏔️ Dashboard Filters")

    st.caption("Explore Colorado environmental data")

    st.button(
        "🔄 Reset Filters",
        on_click=reset_filters,
        use_container_width=True
    )

    st.divider()
    st.subheader("🌤️ Air Quality")

    cities = sorted(air_quality["city"].dropna().unique())

    selected_cities = st.multiselect(
        "Colorado Cities",
        options=cities,
        default=cities,
        key="city_filter"
    )

    st.subheader("📅 Time Period")

    month_range = st.slider(
        "Months of 2025",
        min_value=1,
        max_value=12,
        value=(1, 12),
        key="month_filter"
    )

    st.divider()
    st.subheader("⚡ Home Energy")

    regions = sorted(energy["region"].dropna().unique())

    selected_regions = st.multiselect(
        "Colorado Regions",
        options=regions,
        default=regions,
        key="region_filter"
    )

    with st.expander("Additional Filters"):
        home_types = sorted(
            energy["home_type"].dropna().unique()
        )

        selected_home_types = st.multiselect(
            "Home Types",
            options=home_types,
            default=home_types,
            key="home_filter"
        )

        selected_ev = st.selectbox(
            "Electric Vehicle Ownership",
            ["All Households", "Yes", "No"],
            key="ev_filter"
        )

        selected_solar = st.selectbox(
            "Solar Panel Ownership",
            ["All Households", "Yes", "No"],
            key="solar_filter"
        )

    st.divider()
    st.caption("Synthetic classroom datasets, 2025")

# ---- Filter Data ----
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
        "No data matches your selected filters. "
        "Please adjust your selections."
    )
    st.stop()

# ---- Chart Styling ----
COLORS = {
    "blue": "#62A8F7",
    "teal": "#55D6C2",
    "purple": "#AE91FA",
    "orange": "#F5B66C",
    "red": "#F27C83"
}

def style_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=15, r=15, t=20, b=35),
        paper_bgcolor="#16243A",
        plot_bgcolor="#16243A",
        font=dict(size=12, color="#E8EEF7"),
        legend=dict(
            orientation="h",
            y=-0.3,
            x=0
        )
    )

    fig.update_xaxes(
        showgrid=False,
        automargin=True
    )

    fig.update_yaxes(
        gridcolor="#30425B",
        automargin=True
    )

    return fig

# ---- Dashboard Header ----
st.title("🏔️ Colorado Environmental Dashboard")

st.write(
    "Explore how wildfire smoke, temperature, "
    "home types, and electric vehicles relate "
    "to air quality and electricity use in Colorado."
)

st.caption(
    "2025 | Colorado | Synthetic classroom data"
)

st.divider()

# ---- KPI Overview ----
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

kpi1, kpi2, kpi3 = st.columns(3, gap="medium")

with kpi1:
    st.metric(
        "Average Air Quality Index",
        f"{average_aqi:.1f}"
    )

with kpi2:
    st.metric(
        "Average Electricity Use",
        f"{average_energy:,.0f} kWh"
    )

with kpi3:
    st.metric(
        "Households With Solar",
        f"{solar_percentage:.1f}%"
    )

st.caption(
    "Metrics update with the selected filters. "
    "Electricity use is averaged per household-month."
)

st.divider()

# ---- Air Quality Analysis ----
st.header("🌤️ Colorado Air Quality Analysis")

col1, col2 = st.columns(2, gap="large")

# ---- Question 1 ----
with col1:
    with st.container(border=True):
        st.subheader("Wildfire Smoke vs. Air Quality")

        st.write(
            "Does wildfire smoke make Colorado's "
            "air quality worse?"
        )

        smoke_data = (
            filtered_air.groupby(
                "wildfire_smoke",
                as_index=False
            )["aqi"].mean()
        )

        smoke_data["group"] = smoke_data[
            "wildfire_smoke"
        ].replace({
            "Yes": "Smoke",
            "No": "No Smoke"
        })

        fig1 = px.bar(
            smoke_data,
            x="group",
            y="aqi",
            color="group",
            color_discrete_map={
                "Smoke": COLORS["red"],
                "No Smoke": COLORS["blue"]
            },
            text_auto=".1f",
            labels={
                "group": "Wildfire Smoke",
                "aqi": "Average AQI"
            }
        )

        fig1.update_layout(showlegend=False)

        st.plotly_chart(
            style_chart(fig1),
            use_container_width=True
        )

        st.caption(
            "Average Air Quality Index (AQI) with "
            "and without wildfire smoke. "
            "Higher AQI means worse air quality."
        )

# ---- Question 2 ----
with col2:
    with st.container(border=True):
        st.subheader("Temperature vs. Air Pollution")

        st.write(
            "Is there a relationship between "
            "temperature and air pollution in Colorado?"
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

        st.plotly_chart(
            style_chart(fig2),
            use_container_width=True
        )

        st.caption(
            "Each point represents one city-day. "
            "PM2.5 measures fine particle pollution "
            "in micrograms per cubic meter."
        )

st.divider()

# ---- Home Energy Analysis ----
st.header("⚡ Colorado Home Energy Analysis")

col3, col4 = st.columns(2, gap="large")

# ---- Question 3 ----
with col3:
    with st.container(border=True):
        st.subheader("Electricity Use by Home Type")

        st.write(
            "Do different types of homes use "
            "different amounts of electricity?"
        )

        home_data = (
            filtered_energy.groupby(
                "home_type",
                as_index=False
            )["kwh_used"]
            .mean()
            .sort_values(
                "kwh_used",
                ascending=False
            )
        )

        fig3 = px.bar(
            home_data,
            x="home_type",
            y="kwh_used",
            text_auto=".0f",
            color_discrete_sequence=[COLORS["teal"]],
            labels={
                "home_type": "Home Type",
                "kwh_used": "Average Electricity Use (kWh)"
            }
        )

        st.plotly_chart(
            style_chart(fig3),
            use_container_width=True
        )

        st.caption(
            "Average monthly electricity use "
            "in kilowatt-hours (kWh) by home type."
        )

# ---- Question 4 ----
with col4:
    with st.container(border=True):
        st.subheader("Electric Vehicles & Energy Use")

        st.write(
            "Do households with electric vehicles "
            "use more electricity than those without?"
        )

        ev_data = (
            filtered_energy.groupby(
                "has_ev",
                as_index=False
            )["kwh_used"].mean()
        )

        ev_data["group"] = ev_data["has_ev"].replace({
            "Yes": "Has EV",
            "No": "No EV"
        })

        fig4 = px.bar(
            ev_data,
            x="group",
            y="kwh_used",
            color="group",
            color_discrete_map={
                "Has EV": COLORS["purple"],
                "No EV": COLORS["blue"]
            },
            text_auto=".0f",
            labels={
                "group": "EV Ownership",
                "kwh_used": "Average Electricity Use (kWh)"
            }
        )

        fig4.update_layout(showlegend=False)

        st.plotly_chart(
            style_chart(fig4),
            use_container_width=True
        )

        st.caption(
            "Average monthly electricity use "
            "for households with and without "
            "electric vehicles (EVs)."
        )

st.divider()

# ---- Key Insights ----
st.header("💡 Key Insights")

smoke_lookup = smoke_data.set_index("group")["aqi"]
ev_lookup = ev_data.set_index("group")["kwh_used"]

insight1, insight2 = st.columns(2, gap="large")

with insight1:
    with st.container(border=True):
        st.subheader("🔥 Wildfire Smoke")

        if {"Smoke", "No Smoke"}.issubset(
            smoke_lookup.index
        ):
            smoke_avg = smoke_lookup["Smoke"]
            no_smoke_avg = smoke_lookup["No Smoke"]
            difference = smoke_avg - no_smoke_avg

            st.write(
                f"Average AQI is {smoke_avg:.1f} "
                f"with smoke and {no_smoke_avg:.1f} "
                "without smoke."
            )

            st.write(
                f"Difference: {difference:+.1f} AQI points."
            )
        else:
            st.write(
                "Both smoke groups are needed "
                "for comparison."
            )

with insight2:
    with st.container(border=True):
        st.subheader("🌡️ Temperature & Pollution")

        if len(pollution_data) >= 2:
            correlation = pollution_data[
                ["temp_f", "pm25_ugm3"]
            ].corr().iloc[0, 1]

            if pd.notna(correlation):
                st.write(
                    "The correlation between temperature "
                    f"and PM2.5 is {correlation:.2f}."
                )

                st.write(
                    "A value near zero suggests a "
                    "weak linear relationship."
                )
            else:
                st.write(
                    "Not enough variation to calculate "
                    "a correlation."
                )
        else:
            st.write(
                "Not enough observations to calculate "
                "a correlation."
            )

insight3, insight4 = st.columns(2, gap="large")

with insight3:
    with st.container(border=True):
        st.subheader("🏠 Home Types")

        highest_home = home_data.iloc[0]

        st.write(
            f"{highest_home['home_type']} homes have "
            "the highest average electricity use "
            "among the selected home types."
        )

        st.write(
            f"Average use: "
            f"{highest_home['kwh_used']:,.0f} kWh per month."
        )

with insight4:
    with st.container(border=True):
        st.subheader("🚗 Electric Vehicles")

        if {"Has EV", "No EV"}.issubset(
            ev_lookup.index
        ):
            ev_avg = ev_lookup["Has EV"]
            no_ev_avg = ev_lookup["No EV"]
            difference = ev_avg - no_ev_avg

            st.write(
                f"Households with EVs average "
                f"{ev_avg:,.0f} kWh per month."
            )

            st.write(
                f"Households without EVs average "
                f"{no_ev_avg:,.0f} kWh per month."
            )

            st.write(
                f"Difference: {difference:+,.0f} kWh."
            )
        else:
            st.write(
                "Both EV ownership groups are needed "
                "for comparison."
            )

st.caption(
    "These results show associations in synthetic "
    "data, not proof of cause and effect."
)

# ---- Missing Data Handling ----
missing_pm25 = air_quality["pm25_ugm3"].isna().sum()

st.caption(
    f"Missing-data handling: {missing_pm25} PM2.5 "
    "readings are missing from the original dataset. "
    "Those rows are excluded only from the "
    "temperature-versus-pollution chart and "
    "correlation calculation. Other available "
    "observations are retained."
)

st.divider()

# ---- Dataset Explorer ----
st.header("📁 Explore the Datasets")

tab1, tab2 = st.tabs([
    "Air Quality Data",
    "Home Energy Data"
])

with tab1:
    st.write("Colorado Air Quality Dataset")

    st.dataframe(
        filtered_air,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Filtered Air Quality CSV",
        data=filtered_air.to_csv(index=False).encode("utf-8"),
        file_name="filtered_colorado_air_quality.csv",
        mime="text/csv",
        key="download_air"
    )

with tab2:
    st.write("Colorado Home Energy Dataset")

    st.dataframe(
        filtered_energy,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Filtered Home Energy CSV",
        data=filtered_energy.to_csv(index=False).encode("utf-8"),
        file_name="filtered_home_energy_use.csv",
        mime="text/csv",
        key="download_energy"
    )

# ---- About Dashboard ----
with st.expander("ℹ️ About This Dashboard"):
    st.write(
        "This dashboard uses two synthetic 2025 "
        "Colorado classroom datasets: "
        "colorado_air_quality.csv and home_energy_use.csv."
    )

    st.write(
        "The air quality dataset contains daily "
        "observations for six Colorado cities."
    )

    st.write(
        "The home energy dataset contains monthly "
        "household electricity consumption and "
        "information about home types, solar panels, "
        "and electric vehicles."
    )

    st.write(
        "The datasets are analyzed separately. "
        "They are not joined together."
    )

    st.write(
        "Sidebar filters update the charts, metrics, "
        "insights, and data tables."
    )

    st.write(
        "The dashboard is for educational purposes "
        "and does not represent real Colorado measurements."
    )
