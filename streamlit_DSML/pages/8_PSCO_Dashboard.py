
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime, timezone

# ---- Page Configuration ----
st.set_page_config(
    page_title="PSCO Electricity Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Dataset ----
DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "Data"
    / "psco_electricity_2025.csv"
)

SOURCE_URL = "https://www.eia.gov/electricity/gridmonitor/"

FUEL_COLUMNS = {
    "Natural Gas": "natural_gas_mw",
    "Coal": "coal_mw",
    "Wind": "wind_mw",
    "Solar": "solar_mw",
    "Hydro": "hydro_mw"
}

COLORS = {
    "Natural Gas": "#0072B2",
    "Coal": "#999999",
    "Wind": "#009E73",
    "Solar": "#E69F00",
    "Hydro": "#CC79A7"
}

SEASONS = ["Winter", "Spring", "Summer", "Fall"]

# ---- Load Data ----
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    df["date"] = pd.to_datetime(df["date"])
    df["utc_hour_end"] = pd.to_datetime(
        df["utc_hour_end"],
        utc=True
    )

    return df

try:
    df = load_data()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()

# ---- Reset Filters ----
def reset_filters():
    for key in [
        "psco_seasons",
        "psco_months",
        "psco_hours",
        "psco_fuels"
    ]:
        st.session_state.pop(key, None)

# ---- Sidebar ----
with st.sidebar:
    st.header("⚡ Grid Filters")

    st.caption(
        "Select a time period and energy sources."
    )

    st.button(
        "Reset Filters",
        on_click=reset_filters,
        use_container_width=True
    )

    st.divider()

    selected_seasons = st.multiselect(
        "Seasons",
        options=SEASONS,
        default=SEASONS,
        key="psco_seasons"
    )

    selected_months = st.slider(
        "Month Range",
        min_value=1,
        max_value=12,
        value=(1, 12),
        key="psco_months"
    )

    selected_hours = st.slider(
        "Local Hour Ending",
        min_value=0,
        max_value=23,
        value=(0, 23),
        key="psco_hours"
    )

    selected_fuels = st.multiselect(
        "Energy Sources",
        options=list(FUEL_COLUMNS.keys()),
        default=list(FUEL_COLUMNS.keys()),
        key="psco_fuels"
    )

    st.divider()

    st.caption(
        "Source: EIA-930, PSCO balancing authority, 2025."
    )

# ---- Apply Filters ----
filtered = df[
    df["season"].isin(selected_seasons)
    & df["month"].between(
        selected_months[0],
        selected_months[1]
    )
    & df["hour_end_local"].between(
        selected_hours[0],
        selected_hours[1]
    )
].copy()

if filtered.empty:
    st.warning(
        "No observations match these filters. "
        "Please adjust your selections."
    )
    st.stop()

# ---- Chart Styling ----
def style_chart(fig, height=380):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        margin=dict(l=25, r=25, t=35, b=40),
        font=dict(size=13),
        legend_title_text=""
    )

    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)

    return fig

# ---- Header ----
st.title("⚡ PSCO Electricity Dashboard")

st.write(
    "Explore electricity demand and generation "
    "in the Public Service Company of Colorado "
    "balancing authority during 2025."
)

st.caption(
    "PSCO covers a Colorado-area electricity system, "
    "not the entire state of Colorado."
)

st.markdown(
    f"[Official EIA-930 Data Source]({SOURCE_URL})"
)

refresh_time = datetime.now(
    timezone.utc
).strftime("%Y-%m-%d %H:%M UTC")

st.caption(
    f"Dashboard last refreshed: {refresh_time} "
    "(page calculation time; source data covers 2025)."
)

st.divider()

# ---- KPI Cards ----
st.header("Grid Overview")

average_demand = filtered["demand_mw"].mean()
peak_demand = filtered["demand_mw"].max()
average_generation = filtered["net_generation_mw"].mean()
total_observations = len(filtered)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Average Demand",
        f"{average_demand:,.0f} MW"
    )

with k2:
    st.metric(
        "Peak Demand",
        f"{peak_demand:,.0f} MW"
    )

with k3:
    st.metric(
        "Average Net Generation",
        f"{average_generation:,.0f} MW"
    )

with k4:
    st.metric(
        "Hourly Observations",
        f"{total_observations:,}"
    )

st.caption(
    "MW means megawatts, a unit of electrical power. "
    "All metrics update when time filters change."
)

st.divider()

# ---- Prepare Chart Data ----
daily_demand = (
    filtered.groupby("date", as_index=False)["demand_mw"]
    .mean()
    .sort_values("date")
)

hourly_demand = (
    filtered.groupby(
        "hour_end_local",
        as_index=False
    )["demand_mw"]
    .mean()
    .sort_values("hour_end_local")
)

# ---- Row 1: Linked Demand Charts ----
st.header("Electricity Demand")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("Demand Over Time")

    fig1 = px.line(
        daily_demand,
        x="date",
        y="demand_mw",
        labels={
            "date": "Date",
            "demand_mw": "Average Demand (MW)"
        },
        title="Average Daily Electricity Demand"
    )

    fig1.update_traces(
        line_color="#56B4E9",
        line_width=2.5
    )

    st.plotly_chart(
        style_chart(fig1),
        use_container_width=True
    )

    st.caption(
        "Daily average electricity demand for the "
        "selected months, seasons, and hours."
    )

with col2:
    st.subheader("Demand by Hour")

    fig2 = px.bar(
        hourly_demand,
        x="hour_end_local",
        y="demand_mw",
        text_auto=".0f",
        labels={
            "hour_end_local": "Local Hour Ending",
            "demand_mw": "Average Demand (MW)"
        },
        title="Average Electricity Demand by Hour",
        color_discrete_sequence=["#009E73"]
    )

    fig2.update_xaxes(dtick=2)

    st.plotly_chart(
        style_chart(fig2),
        use_container_width=True
    )

    st.caption(
        "Each bar shows average demand during "
        "one selected local hour."
    )

st.divider()

# ---- Row 2: Generation Analysis ----
st.header("Electricity Generation")

col3, col4 = st.columns(2, gap="large")

if selected_fuels:
    fuel_averages = pd.DataFrame({
        "Energy Source": selected_fuels,
        "Average MW": [
            filtered[FUEL_COLUMNS[name]].mean()
            for name in selected_fuels
        ]
    }).sort_values(
        "Average MW",
        ascending=False
    )

    with col3:
        st.subheader("Generation by Energy Source")

        fig3 = px.bar(
            fuel_averages,
            x="Average MW",
            y="Energy Source",
            orientation="h",
            color="Energy Source",
            color_discrete_map=COLORS,
            text="Average MW",
            labels={
                "Average MW": "Average Generation (MW)"
            },
            title="Average Reported Generation by Source"
        )

        fig3.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            cliponaxis=False
        )

        fig3.update_layout(
            showlegend=False,
            yaxis=dict(autorange="reversed")
        )

        st.plotly_chart(
            style_chart(fig3),
            use_container_width=True
        )

        st.caption(
            "Average hourly reported generation "
            "for selected energy sources."
        )

    # ---- Peak Demand Generation Mix ----
    threshold = filtered["demand_mw"].quantile(0.90)

    peak_data = filtered[
        filtered["demand_mw"] >= threshold
    ].copy()

    fuel_columns = [
        FUEL_COLUMNS[name]
        for name in selected_fuels
    ]

    # Clip negative readings only for the stacked chart.
    # Preserve original values in the source dataset.
    for column in fuel_columns:
        peak_data[column] = (
            peak_data[column].clip(lower=0)
        )

    peak_monthly = (
        peak_data.groupby("month")[fuel_columns]
        .mean()
        .reset_index()
    )

    peak_long = peak_monthly.melt(
        id_vars="month",
        value_vars=fuel_columns,
        var_name="fuel_column",
        value_name="Average MW"
    )

    name_lookup = {
        column: name
        for name, column in FUEL_COLUMNS.items()
    }

    peak_long["Energy Source"] = (
        peak_long["fuel_column"].map(name_lookup)
    )

    with col4:
        st.subheader("Generation During Peak Demand")

        fig4 = px.area(
            peak_long,
            x="month",
            y="Average MW",
            color="Energy Source",
            color_discrete_map=COLORS,
            category_orders={
                "Energy Source": selected_fuels
            },
            labels={
                "month": "Month",
                "Average MW": "Average Generation (MW)"
            },
            title="Generation During Top 10% Demand Hours"
        )

        fig4.update_xaxes(dtick=1)

        st.plotly_chart(
            style_chart(fig4),
            use_container_width=True
        )

        st.caption(
            "Monthly average generation during the "
            "highest-demand 10% of selected hours. "
            "The stacked height is not total grid demand."
        )

else:
    st.info(
        "Select at least one energy source to "
        "display the generation charts."
    )

st.divider()

# ---- Dynamic Insights ----
st.header("Key Insights")

highest_hour = hourly_demand.loc[
    hourly_demand["demand_mw"].idxmax()
]

lowest_hour = hourly_demand.loc[
    hourly_demand["demand_mw"].idxmin()
]

peak_day = daily_demand.loc[
    daily_demand["demand_mw"].idxmax()
]

insights = [
    (
        f"The highest average demand occurs at local "
        f"hour {int(highest_hour['hour_end_local']):02d}:00, "
        f"averaging {highest_hour['demand_mw']:,.0f} MW."
    ),
    (
        f"The lowest average demand occurs at local "
        f"hour {int(lowest_hour['hour_end_local']):02d}:00, "
        f"averaging {lowest_hour['demand_mw']:,.0f} MW."
    ),
    (
        f"The date with the highest daily average "
        f"demand in the selected period is "
        f"{peak_day['date']:%B %d, %Y}, "
        f"at {peak_day['demand_mw']:,.0f} MW."
    ),
    (
        f"The selected period contains "
        f"{total_observations:,} hourly observations."
    )
]

if selected_fuels:
    leading_fuel = fuel_averages.iloc[0]

    insights.append(
        f"{leading_fuel['Energy Source']} has the "
        f"highest average reported generation among "
        f"selected sources, at "
        f"{leading_fuel['Average MW']:,.0f} MW."
    )

    insights.append(
        f"The peak-demand threshold is "
        f"{threshold:,.0f} MW, based on the "
        "90th percentile of selected observations."
    )

for insight in insights:
    st.markdown(f"- {insight}")

st.caption(
    "Limitations: The dataset covers PSCO rather "
    "than the entire state of Colorado. The fuel "
    "comparisons exclude Other Fuel Sources because "
    "many readings are missing. Negative reported "
    "generation is displayed as zero only in the "
    "stacked area chart. These patterns do not "
    "establish cause and effect."
)

st.divider()

# ---- Data Explorer ----
st.header("Explore the Dataset")

with st.expander("View Filtered PSCO Data"):
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Filtered CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="psco_filtered_2025.csv",
        mime="text/csv"
    )

st.caption(
    "Source: U.S. Energy Information Administration, "
    "EIA-930 Hourly Electric Grid Monitor, 2025."
)
