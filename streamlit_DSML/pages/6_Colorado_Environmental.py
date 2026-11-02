import streamlit as st
import pandas as pd
from pathlib import Path

# ---- Load CSV Files ----
data_folder = Path(__file__).resolve().parent.parent / "Data"

air_quality = pd.read_csv(data_folder / "colorado_air_quality.csv")
energy = pd.read_csv(data_folder / "home_energy_use.csv")

# ---- Dashboard Title ----
st.title("Colorado Environmental Dashboard")

st.write("Exploring air quality and home energy consumption in Colorado during 2025.")

# ---- Row 1: Two Columns ----
st.write("### Row 1: Colorado Air Quality")

col1, col2 = st.columns(2)

col1.write("Air Quality Trends")
col2.write("Air Quality by City")

# ---- Row 2: Three Columns ----
st.write("### Row 2: Colorado Home Energy Use")

colA, colB, colC = st.columns(3)

colA.write("Monthly Electricity Consumption")
colB.write("Average Electricity Bills")
colC.write("Solar vs. Non-Solar Homes")

# ---- Display Air Quality Dataset ----
st.write("### Colorado Air Quality Dataset")

st.dataframe(air_quality.head())

# ---- Display Home Energy Dataset ----
st.write("### Colorado Home Energy Dataset")

st.dataframe(energy.head())