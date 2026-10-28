import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

st.title("📡 Live Cryptocurrency Prices")

st.write("This page displays live Bitcoin and Ethereum prices using CoinGecko.")

# Coins we want to track
COINS = ["bitcoin", "ethereum"]
VS = "usd"

# API settings
HEADERS = {
    "User-Agent": "msudenver-dataviz-class/1.0",
    "Accept": "application/json"
}

# Build the API URL
def build_url(ids):
    return (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={','.join(ids)}&vs_currencies={VS}"
    )

API_URL = build_url(COINS)

# Cache API results for 5 minutes
@st.cache_data(ttl=300, show_spinner=False)
def fetch_prices(url):
    try:
        # Request cryptocurrency prices
        response = requests.get(
            url,
            timeout=10,
            headers=HEADERS
        )

        # Check for API rate limiting
        if response.status_code == 429:
            return None, "Too many requests. Please try again later."

        # Check for other HTTP errors
        response.raise_for_status()

        # Convert JSON response into a DataFrame
        data = response.json()

        df = pd.DataFrame(data).T.reset_index()
        df = df.rename(columns={"index": "coin"})

        return df, None

    except (requests.RequestException, ValueError) as e:
        return None, f"API error: {e}"
    
# Sample data in case the API is unavailable
SAMPLE_DF = pd.DataFrame([
    {"coin": "bitcoin", "usd": 68000},
    {"coin": "ethereum", "usd": 3500}
])

# Fetch cryptocurrency prices
st.subheader("Current Cryptocurrency Prices")

df, err = fetch_prices(API_URL)

# Use sample data if the API fails
if err:
    st.warning(f"{err}\nShowing sample data instead.")
    df = SAMPLE_DF.copy()

# Display the data as a table
st.dataframe(df, use_container_width=True)

# Create an interactive bar chart
fig = px.bar(
    df,
    x="coin",
    y="usd",
    title="Current Bitcoin and Ethereum Prices",
    labels={"coin": "Cryptocurrency", "usd": "Price (USD)"}
)

st.plotly_chart(fig, use_container_width=True)

# Auto-refresh settings
st.subheader("🔁 Auto Refresh Settings")

# Choose how often the page refreshes
refresh_sec = st.slider(
    "Refresh every (seconds)",
    min_value=10,
    max_value=120,
    value=30
)

# Turn automatic refreshing on or off
auto_refresh = st.toggle(
    "Enable auto-refresh",
    value=False
)

# Display the current refresh time
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# Automatically refresh the page
if auto_refresh:
    time.sleep(refresh_sec)
    fetch_prices.clear()
    st.rerun()