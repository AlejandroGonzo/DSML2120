
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Professional Bio",
    page_icon="👨‍💻",
    layout="wide"
)

NAME = "Alejandro Gonzalez"
PROGRAM = "Data Science and Machine Learning | MSU Denver"

INTRO = (
    "I am currently studying Data Science and Machine Learning "
    "at Metropolitan State University of Denver. "
    "I am interested in using data to discover patterns, "
    "solve problems, and better understand real world situations. "
    "My areas of interest include energy and utilities, "
    "finance, and healthcare. "
    "I enjoy working with Python to analyze datasets "
    "and create visualizations that explain information clearly. "
    "My goal is to continue developing my technical skills "
    "and apply them to meaningful data science projects."
)

HIGHLIGHTS = [
    "Studying Data Science and Machine Learning at MSU Denver.",
    "Building a foundation in statistics, linear algebra, and machine learning.",
    "Experience with data analysis, visualization, and interactive applications using various tools and technologies.",
    "Working with Python, pandas, Plotly, Streamlit, and other data science tools.",
    "Interested in applying data science to energy, finance, and healthcare."
]

FUN_FACTS = [
    "I enjoy exploring different coffee shops.",
    "I enjoy reading comic books and science fiction.",
    "I like learning how data science connects to everyday life."
]

PHOTO_PATH = "Professional Office Headshot.png"

def find_photo(filename=PHOTO_PATH):
    script_dir = Path(__file__).resolve().parent

    candidates = [
        script_dir / "assets" / filename,
        script_dir.parent / "assets" / filename,
        Path("assets") / filename
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    return None

st.title("👨‍💻 About Me")

st.write(
    "Welcome to my data science portfolio. "
    "Here you can learn about my background, "
    "technical skills, and interests."
)

st.divider()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    photo_src = find_photo()

    if photo_src:
        st.image(
            photo_src,
            caption="Professional profile photo of Alejandro Gonzalez",
            use_container_width=True
        )
    else:
        st.info("Profile photo is currently unavailable.")

with col2:
    st.header(NAME)
    st.write(PROGRAM)
    st.write(INTRO)

st.divider()

st.header("💻 Professional Highlights")

for highlight in HIGHLIGHTS:
    st.write(f"- {highlight}")

st.divider()

st.header("📊 My Data Visualization Philosophy")

st.write(
    "I believe data visualizations should be simple, "
    "clear, and easy for everyone to understand. "
    "Charts should have readable labels, accessible colors, "
    "and accurate information. "
    "I also believe it is important to explain the limitations "
    "of a dataset and avoid misleading conclusions."
)

st.divider()

st.header("⚡ Featured Project")

st.subheader("Colorado Electricity Grid Analysis")

st.write(
    "For my DSML2120 Project 2, I am analyzing hourly "
    "electricity demand and generation using the EIA-930 "
    "dataset from the U.S. Energy Information Administration. "
    "The project explores peak electricity demand, seasonal "
    "patterns, and the contributions of different energy sources."
)

st.write(
    "Visit the PSCO EDA Gallery and PSCO Dashboard "
    "pages to explore my visualizations."
)

st.divider()

st.header("☕ A Few Things About Me")

for fact in FUN_FACTS:
    st.write(f"- {fact}")

st.divider()

st.caption(
    "Alejandro Gonzalez | Data Science and Machine Learning | MSU Denver"
)

