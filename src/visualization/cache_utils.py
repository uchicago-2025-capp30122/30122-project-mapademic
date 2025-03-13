import re
import json
import pathlib
import pandas as pd
import streamlit as st
from unidecode import unidecode

@st.cache_data(show_spinner=False)
def load_geojson():
    geojson_path = pathlib.Path("data") / "raw_data" / "provinces_worldwide.json"
    with geojson_path.open("r", encoding="utf-8") as f:
        geodata = json.load(f)

        for province in geodata["features"]:
            name = province["properties"].get("name", "")
            if isinstance(name, str):
                name = name.lower()
                name = unidecode(name)
                name = re.sub(r'[^a-z0-9]', '', name)
            province["properties"]["clean_name"] = name

    return geodata

@st.cache_data(show_spinner=False)
def load_csv(keywords, year):
    csv_path = pathlib.Path("data") / "output_data" / "state_crdi" / f"{keywords}_{year}_state_crdi.csv"
    return pd.read_csv(csv_path, encoding="utf-8", sep=";")
