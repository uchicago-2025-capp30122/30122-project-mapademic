import pathlib
import json
import pandas as pd
import streamlit as st
from unidecode import unidecode
import re

@st.cache_data(show_spinner=False)
def load_geojson():
    # Load GeoJSON file once
    geojson_path = pathlib.Path("data") / "raw_data" / "provinces_worldwide.json"
    with geojson_path.open("r", encoding="utf-8") as f:
        geodata = json.load(f)

        for province in geodata["features"]:
            name = province["properties"].get("name", "")  # 取 name，防止 KeyError
            if isinstance(name, str):  # 确保 name 是字符串
                name = name.lower()  # 转小写
                name = unidecode(name)  # 去掉重音字符等特殊字符
                name = re.sub(r'[^a-z0-9]', '', name)  # 只保留字母和数字，去掉特殊字符

            province["properties"]["name"] = name  # 更新 JSON 数据

    return geodata

@st.cache_data(show_spinner=False)
def load_csv(keywords, year):
    # Load CSV file for the given keyword and year
    csv_path = pathlib.Path("data") / "output_data" / "state_crdi" / f"{keywords}_{year}_state_crdi.csv"
    return pd.read_csv(csv_path, encoding="utf-8", sep=";")
