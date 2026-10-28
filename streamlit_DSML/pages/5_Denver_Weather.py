import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

st.title("🌤️ Denver Live Weather Dashboard")

st.write("Live Denver temperature and wind speed using the Open-Meteo API.")

lat = 39.7392
lon = -104.9903

wurl = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={lat}&longitude={lon}"
    f"&current=temperature_2m,wind_speed_10m"
    f"&temperature_unit=fahrenheit"
    f"&timezone=America%2FDenver"
)

@st.cache_data(ttl=600)
def get_weather():
    response = requests.get(wurl, timeout=10)
    response.raise_for_status()
    current = response.json()["current"]

    return pd.DataFrame([
        {
            "time": pd.to_datetime(current["time"]),
            "temperature": current["temperature_2m"],
            "wind": current["wind_speed_10m"]
        }
    ])

if "weather_history" not in st.session_state:
    st.session_state.weather_history = pd.DataFrame(
        columns=["time", "temperature", "wind"]
    )

st.subheader("🔁 Refresh Settings")

refresh_sec = st.slider(
    "Refresh every (seconds)",
    min_value=60,
    max_value=600,
    value=120,
    step=60
)

auto_refresh = st.toggle(
    "Enable Auto-Refresh",
    value=False
)

@st.fragment(run_every=refresh_sec if auto_refresh else None)
def weather_dashboard():
    try:
        df = get_weather()
    except (requests.RequestException, ValueError, KeyError) as e:
        st.error(f"Unable to retrieve weather data: {e}")
        return

    temperature = float(df["temperature"].iloc[0])
    wind = float(df["wind"].iloc[0])
    weather_time = pd.to_datetime(df["time"].iloc[0])

    st.subheader("🌡️ Current Denver Weather")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Current Temperature",
            f"{temperature:.1f} °F"
        )

    with col2:
        st.metric(
            "Wind Speed",
            f"{wind:.1f} km/h"
        )

    st.caption(f"Weather observation time: {weather_time}")

    history = st.session_state.weather_history

    if history.empty or weather_time not in pd.to_datetime(history["time"]).tolist():
        history = pd.concat(
            [history, df],
            ignore_index=True
        )

    history = history.tail(50).reset_index(drop=True)

    st.session_state.weather_history = history

    st.subheader("📈 Denver Temperature Over Time")

    fig = px.line(
        history,
        x="time",
        y="temperature",
        markers=True,
        title="Denver Temperature History",
        labels={
            "time": "Time",
            "temperature": "Temperature (°F)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Weather History")

    st.dataframe(
        history,
        use_container_width=True
    )

    st.caption(
        f"Dashboard checked at: {datetime.now().strftime('%H:%M:%S')}"
    )

weather_dashboard()
