import streamlit as st
import os
import subprocess
import json
import requests
import pandas as pd

# 导入 visualization 分支下的 basic_vis.py 中的函数
from src.visualization.basic_vis import generate_basic_choropleth_map
# from ..visualization.basic_vis import generate_basic_choropleth_map

# 1) 初始化 Session State
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False

if "discipline" not in st.session_state:
    st.session_state.discipline = ""

if "global_keyword" not in st.session_state:
    st.session_state.global_keyword = ""

if "selected_year" not in st.session_state:
    st.session_state.selected_year = 2020

# 2) 应用标题 & 说明
st.title("Mapedemic-Demo")
st.write("Explore the geographic distribution of academic papers from Science Direct based on the keywords you enter.")

# 3) 用户登录方式
login_method = st.radio(
    "Please select the login method:",
    ("Login with API Key", "Login with University of Chicago Account Password"),
    key="login_method_radio" 
)

api_key = None
if login_method == "Login with API Key":
    api_key = st.text_input("Please enter your API Key:", type="password", key="api_key_input")
elif login_method == "Log in with your University of Chicago account password":
    uc_username = st.text_input("Please enter your University of Chicago account number:", key="uc_username_input")
    uc_password = st.text_input("Please enter your password:", type="password", key="uc_password_input")
    if st.button("Get API Key", key="get_api_btn"):
        login_url = "https://api.elsevier.com/authenticate"
        payload = {"username": uc_username, "password": uc_password}
        response = requests.post(login_url, json=payload)
        if response.status_code == 200:
            api_key = response.json().get("api_key")
            st.success("API Key Application successful: " + api_key)
        else:
            st.error("Login failed, please check your account and password.")

# 4) 全局输入 - 学科与关键词
#输入学科
st.session_state.discipline = st.text_input(
    "Please enter the subject you are interested in:",
    value=st.session_state.discipline,
    key="discipline_input_top"
)

#输入关键词
user_keyword_input = st.text_input(
    "Please enter keywords:",
    value=st.session_state.global_keyword,
    key="global_keyword_input_top"
)

# 若用户输入了新的关键词，更新 session_state
if user_keyword_input:
    st.session_state.global_keyword = user_keyword_input


# 5) 主逻辑： 若已登录，则可以进行搜索、可视化
if api_key:
    st.write("You have successfully logged in and your API Key has been authenticated.")

    #出现【Search】按钮
    if not st.session_state.search_completed:
        # key
        st.session_state.discipline = st.text_input(
            "Update the subject (optional):",
            value=st.session_state.discipline,
            key="discipline_input_search"
        )

        new_keyword_input = st.text_input(
            "Update the keywords (optional):",
            value=st.session_state.global_keyword,
            key="global_keyword_input_search"
        )

        if new_keyword_input:
            st.session_state.global_keyword = new_keyword_input

        if st.button("Search", key="search_btn"):
            if st.session_state.global_keyword and st.session_state.discipline:
                # 将 API Key 设置为环境变量，供外部脚本使用
                os.environ["API_KEY"] = api_key

                st.info("The API is being called to get the data, please wait...")
                subprocess.run(["python", "api-calling/keyword_search.py"])

                st.info("The data cleaning script is being called, please wait...")
                subprocess.run(["python", "cleaning/clean-data.py"])

                st.session_state.search_completed = True
                st.experimental_rerun()

    else:
        # 6) 显示可视化： 允许用户选择年份
        st.write("### The search and data processing is completed and the visualisation results are displayed:")

        st.session_state.selected_year = st.selectbox(
            "Please select a year from 2020 to 2024:",
            [2020, 2021, 2022, 2023, 2024],
            index=[2020, 2021, 2022, 2023, 2024].index(st.session_state.selected_year),
            key="year_selectbox"
        )
        st.write(f"**Selected year:** {st.session_state.selected_year}")

        try:
            fig = generate_basic_choropleth_map()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating a visualisation chart: {e}")

        # 提供按钮以继续搜索
        if st.button("🔄 Continue searching", key="continue_btn"):
            st.session_state.search_completed = False
            # st.session_state.discipline = ""
            # st.session_state.global_keyword = ""
            st.experimental_rerun()

else:
    st.warning("Please login or enter a valid API Key first.")
