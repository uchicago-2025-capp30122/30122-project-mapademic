import pathlib
import json
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def load_geojson():
    # Load GeoJSON file once
    geojson_path = pathlib.Path("data") / "provinces_worldwide.json"
    with geojson_path.open("r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(show_spinner=False)
def load_csv(keywords, year):
    # Load CSV file for the given keyword and year
    csv_path = pathlib.Path("data") / "output_data" / f"{keywords}_{year}_cleaned.csv"
    return pd.read_csv(csv_path, encoding="utf-8")
