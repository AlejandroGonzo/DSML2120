import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Set the page title
st.title("Science Fiction Franchise Popularity")

# Locate and read the CSV file
DATA_PATH = Path(__file__).resolve().parent.parent / "Data" / "Pie_demo.csv"
df = pd.read_csv(DATA_PATH)

# Display the dataset
st.subheader("Science Fiction Dataset")
st.dataframe(df)

# Create an interactive pie chart
fig = px.pie(
    df,
    names="Franchise",
    values="Popularity",
    title="My Favorite Science Fiction Franchises"
)

# Display the pie chart
st.plotly_chart(fig, use_container_width=True)