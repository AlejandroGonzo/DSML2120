
import streamlit as st

st.set_page_config(
    page_title="Future Work",
    page_icon="🧭",
    layout="wide"
)

st.title("🧭 Future Work")

st.write(
    "This page outlines possible improvements to my "
    "PSCO Electricity Grid Analysis project."
)

st.divider()

st.header("Future Improvements")

col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.subheader("1. Electricity Demand Forecasting")
        st.write(
            "Build a machine learning model to predict "
            "future electricity demand using historical "
            "demand, time of day, and seasonal patterns."
        )

    with st.container(border=True):
        st.subheader("2. Weather Data Integration")
        st.write(
            "Add Colorado weather data to explore how "
            "temperature and weather conditions relate "
            "to electricity demand."
        )

with col2:
    with st.container(border=True):
        st.subheader("3. Renewable Energy Analysis")
        st.write(
            "Expand the analysis of wind and solar "
            "generation to better understand how "
            "renewable energy changes throughout the year."
        )

    with st.container(border=True):
        st.subheader("4. Grid Region Comparisons")
        st.write(
            "Include additional balancing authorities "
            "to compare electricity demand and generation "
            "across different regions."
        )

st.divider()

st.header("Reflection: From Wireframe to Dashboard")

st.write(
    "During Lab 4.3, I designed a Colorado Environmental "
    "Dashboard using a simple wireframe. For Project 2, "
    "I expanded my work by analyzing a new electricity "
    "grid dataset and creating interactive charts. "
    "I also improved the layout by organizing information "
    "into sections and using filters to make the dashboard "
    "easier to explore."
)

st.write(
    "One important lesson I learned was that a dashboard "
    "should be easy to read and understand. I focused on "
    "clear chart labels, readable colors, and displaying "
    "important information first."
)

st.divider()

st.caption(
    "DSML2120 — Data Visualization | Project 2"
)
