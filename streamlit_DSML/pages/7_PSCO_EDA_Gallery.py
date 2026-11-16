
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="PSCO EDA Gallery",
    page_icon="📊",
    layout="wide"
)

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

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])
    df["utc_hour_end"] = pd.to_datetime(
        df["utc_hour_end"], utc=True
    )
    return df

try:
    df = load_data()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()

def show_chart(fig, key):
    fig.update_layout(
        template="plotly_dark",
        height=440,
        font=dict(size=13),
        margin=dict(l=25, r=25, t=35, b=40),
        legend_title_text=""
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key
    )

def show_guide(points):
    st.markdown("#### How to Read This Chart")
    for point in points:
        st.markdown(f"- {point}")

def show_observations(points):
    st.markdown("#### Observations")
    for point in points:
        st.markdown(f"- {point}")

def show_source(note):
    st.caption(
        f"Source: EIA-930, PSCO, 2025. {note}"
    )

st.title("📊 PSCO Electricity — EDA Gallery")

st.write(
    "Exploring hourly electricity demand and generation "
    "for Public Service Company of Colorado (PSCO) in 2025."
)

st.info(
    f"Dataset: {len(df):,} hourly observations. "
    "All power measurements are in megawatts (MW). "
    "PSCO is a balancing authority, not the entire state "
    "of Colorado."
)

st.markdown(
    f"[Official EIA Data Source]({SOURCE_URL})"
)

st.divider()

# ---- Chart 1: Line Chart ----
st.header("1. Electricity Demand by Hour")

st.write(
    "Research question: What time of day does the "
    "PSCO grid experience the highest electricity demand?"
)

hourly = (
    df.groupby("hour_end_local", as_index=False)["demand_mw"]
    .mean()
    .sort_values("hour_end_local")
)

fig1 = px.line(
    hourly,
    x="hour_end_local",
    y="demand_mw",
    markers=True,
    labels={
        "hour_end_local": "Local Hour Ending (0–23)",
        "demand_mw": "Average Demand (MW)"
    },
    title="Average Electricity Demand by Local Hour"
)

fig1.update_traces(
    line_color="#56B4E9",
    line_width=3,
    marker=dict(size=7)
)

fig1.update_xaxes(dtick=2)

show_chart(fig1, "hourly_demand")

show_guide([
    "The horizontal axis shows the local hour of the day.",
    "The vertical axis shows average electricity demand in megawatts (MW).",
    "Higher points indicate hours with greater average demand."
])

peak_hour = hourly.loc[hourly["demand_mw"].idxmax()]
low_hour = hourly.loc[hourly["demand_mw"].idxmin()]

hour_difference = (
    peak_hour["demand_mw"] - low_hour["demand_mw"]
)

show_observations([
    f"The highest average demand occurs at hour {int(peak_hour['hour_end_local']):02d}:00, reaching {peak_hour['demand_mw']:,.0f} MW.",
    f"The lowest average demand occurs at hour {int(low_hour['hour_end_local']):02d}:00, averaging {low_hour['demand_mw']:,.0f} MW.",
    f"The difference between the highest and lowest hourly averages is {hour_difference:,.0f} MW.",
    "These patterns show when demand is higher, but do not establish why customers use electricity at those times."
])

show_source(
    "Hourly demand averaged by local hour across 2025."
)

st.divider()

# ---- Chart 2: Box Plot ----
st.header("2. Seasonal Electricity Demand")

st.write(
    "Research question: How does electricity demand "
    "change across winter, spring, summer, and fall?"
)

fig2 = px.box(
    df,
    x="season",
    y="demand_mw",
    color="season",
    category_orders={"season": SEASONS},
    points="outliers",
    labels={
        "season": "Season",
        "demand_mw": "Electricity Demand (MW)"
    },
    title="Distribution of Electricity Demand by Season",
    color_discrete_map={
        "Winter": "#56B4E9",
        "Spring": "#009E73",
        "Summer": "#E69F00",
        "Fall": "#CC79A7"
    }
)

fig2.update_layout(showlegend=False)

show_chart(fig2, "seasonal_boxplot")

show_guide([
    "Each box represents electricity demand during one season.",
    "The middle line inside each box shows the median demand.",
    "The box shows the middle half of observations; points beyond the whiskers highlight potential outliers."
])

seasonal = (
    df.groupby("season")["demand_mw"]
    .agg(["mean", "median", "min", "max"])
    .reindex(SEASONS)
)

highest_season = seasonal["mean"].idxmax()
lowest_season = seasonal["mean"].idxmin()

largest_spread = (
    seasonal["max"] - seasonal["min"]
).idxmax()

show_observations([
    f"{highest_season} has the highest average demand at {seasonal.loc[highest_season, 'mean']:,.0f} MW.",
    f"{lowest_season} has the lowest average demand at {seasonal.loc[lowest_season, 'mean']:,.0f} MW.",
    f"{largest_spread} has the largest difference between its minimum and maximum hourly demand.",
    f"The median demand in summer is {seasonal.loc['Summer', 'median']:,.0f} MW, compared with {seasonal.loc['Winter', 'median']:,.0f} MW in winter."
])

show_source(
    "Each box summarizes hourly demand observations for one season."
)

st.divider()

# ---- Chart 3: Bar Chart ----
st.header("3. Electricity Generation by Source")

st.write(
    "Research question: Which energy sources contribute "
    "the most electricity to the PSCO grid?"
)

fuel_averages = pd.DataFrame({
    "Energy Source": list(FUEL_COLUMNS.keys()),
    "Average MW": [
        df[column].mean()
        for column in FUEL_COLUMNS.values()
    ]
}).sort_values("Average MW", ascending=False)

fig3 = px.bar(
    fuel_averages,
    x="Average MW",
    y="Energy Source",
    orientation="h",
    color="Energy Source",
    color_discrete_map=COLORS,
    text="Average MW",
    labels={"Average MW": "Average Generation (MW)"},
    title="Average Reported Generation by Energy Source"
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

show_chart(fig3, "fuel_bar")

show_guide([
    "Each bar represents one reported electricity generation source.",
    "The horizontal axis shows average generation in megawatts (MW).",
    "Longer bars indicate sources with greater average reported generation."
])

top_fuel = fuel_averages.iloc[0]
bottom_fuel = fuel_averages.iloc[-1]

renewable_average = fuel_averages.loc[
    fuel_averages["Energy Source"].isin(
        ["Wind", "Solar", "Hydro"]
    ),
    "Average MW"
].sum()

show_observations([
    f"{top_fuel['Energy Source']} has the highest average reported generation at {top_fuel['Average MW']:,.0f} MW.",
    f"{bottom_fuel['Energy Source']} has the lowest average among these five sources at {bottom_fuel['Average MW']:,.0f} MW.",
    f"Wind, solar, and hydro together average {renewable_average:,.0f} MW across the dataset.",
    "These comparisons exclude the Other Fuel Sources category because many of its readings are missing."
])

show_source(
    "Average hourly reported generation by fuel type. "
    "Other fuel sources are excluded."
)

st.divider()

# ---- Chart 4: Stacked Area Chart ----
st.header("4. Energy Sources During Peak Demand")

st.write(
    "Research question: During periods of high "
    "electricity demand, which energy sources "
    "provide the most electricity?"
)

threshold = df["demand_mw"].quantile(0.90)

peak_data = df[
    df["demand_mw"] >= threshold
].copy()

# Negative reported generation values are kept in the
# original dataset but clipped to zero for this stacked
# area visualization, which shows positive contributions.
for column in FUEL_COLUMNS.values():
    peak_data[column] = peak_data[column].clip(lower=0)

monthly_peak = (
    peak_data.groupby("month")[
        list(FUEL_COLUMNS.values())
    ]
    .mean()
    .reset_index()
)

long_peak = monthly_peak.melt(
    id_vars="month",
    value_vars=list(FUEL_COLUMNS.values()),
    var_name="fuel_column",
    value_name="Average MW"
)

name_lookup = {
    column: name
    for name, column in FUEL_COLUMNS.items()
}

long_peak["Energy Source"] = (
    long_peak["fuel_column"].map(name_lookup)
)

fig4 = px.area(
    long_peak,
    x="month",
    y="Average MW",
    color="Energy Source",
    color_discrete_map=COLORS,
    category_orders={
        "Energy Source": list(FUEL_COLUMNS.keys())
    },
    labels={
        "month": "Month of 2025",
        "Average MW": "Average Generation (MW)"
    },
    title="Generation Mix During Top 10% Demand Hours"
)

fig4.update_xaxes(
    dtick=1,
    range=[0.5, 12.5]
)

show_chart(fig4, "peak_area")

show_guide([
    "The horizontal axis shows the month, and the vertical axis shows average generation during peak-demand hours.",
    "Each colored area represents an energy source; its thickness shows that source's average contribution.",
    "The stacked height shows the combined average of the five displayed sources, not total grid demand."
])

peak_fuel_means = pd.Series({
    name: peak_data[column].mean()
    for name, column in FUEL_COLUMNS.items()
}).sort_values(ascending=False)

peak_leader = peak_fuel_means.index[0]

peak_month_counts = (
    peak_data.groupby("month").size()
)

busiest_peak_month = peak_month_counts.idxmax()

show_observations([
    f"The peak-demand threshold is {threshold:,.0f} MW, representing the top 10% of hourly demand observations.",
    f"{peak_leader} provides the highest average reported generation during these peak-demand hours, at {peak_fuel_means.iloc[0]:,.0f} MW.",
    f"Month {int(busiest_peak_month)} contains the most peak-demand observations, with {int(peak_month_counts.max()):,} hours.",
    "The generation mix varies across months. The chart does not include net imports or the incomplete Other Fuel Sources category."
])

show_source(
    "Monthly averages calculated using only hours "
    "at or above the 90th percentile of demand. "
    "Negative generation values are displayed as zero "
    "in this stacked chart."
)

st.divider()

# ---- Data Quality and Limitations ----
st.header("Data Quality & Limitations")

missing_other = df["other_fuel_mw"].isna().sum()
negative_solar = (df["solar_mw"] < 0).sum()
negative_wind = (df["wind_mw"] < 0).sum()

st.write(
    f"The dataset contains {len(df):,} hourly observations. "
    f"The Other Fuel Sources column has {missing_other:,} "
    "missing readings, so it is excluded from the "
    "generation charts."
)

st.write(
    f"There are {negative_solar:,} negative solar readings "
    f"and {negative_wind:,} negative wind readings. "
    "These values are retained in the original dataset. "
    "For the stacked area chart only, negative values "
    "are displayed as zero to show positive generation."
)

st.write(
    "The charts show patterns and associations, not "
    "proof of cause and effect. PSCO covers a balancing "
    "authority area rather than all of Colorado."
)

with st.expander("View Dataset"):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "Source: U.S. Energy Information Administration, "
    "EIA-930 Hourly Electric Grid Monitor, 2025."
)
