import streamlit as st
import os
import subprocess
import json
import requests
import pandas as pd

# 导入 visualization 分支下的 heatmap.py 中的新可视化函数
from src.visualization.heatmap import combined_heatmaps_with_timeline_and_arrows

# 1) 初始化 Session State
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False
if "discipline" not in st.session_state:
    st.session_state.discipline = ""
if "global_keyword" not in st.session_state:
    st.session_state.global_keyword = ""

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
elif login_method == "Login with University of Chicago Account Password":
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
st.session_state.discipline = st.text_input(
    "Please enter the subject you are interested in:",
    value=st.session_state.discipline,
    key="discipline_input_top"
)

user_keyword_input = st.text_input(
    "Please enter keywords:",
    value=st.session_state.global_keyword,
    key="global_keyword_input_top"
)

if user_keyword_input:
    st.session_state.global_keyword = user_keyword_input

# 5) 主逻辑： 若已登录，则可以进行搜索、可视化
if api_key:
    st.write("You have successfully logged in and your API Key has been authenticated.")
    
    if not st.session_state.search_completed:
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
                # 将 API Key 及关键词传递给外部脚本
                os.environ["API_KEY"] = api_key
                os.environ["SEARCH_KEYWORD"] = st.session_state.global_keyword  # 供 keyword_search.py 使用

                st.info("Calling the API to get the data, please wait...")
                subprocess.run(["python", "src/api-calling/keyword_search.py"])
                subprocess.run(["python", "src/api-calling/affiliation_state_match.py"])
                st.info("Calling the data cleaning script, please wait...")
                subprocess.run(["python", "-m", "src.cleaning.clean_data"])
                subprocess.run(["python", "-m", "src.cleaning.feature_selecting"])

                st.session_state.search_completed = True

                # 不使用 experimental_rerun，改用 st.stop() 停止执行，让页面立即呈现新状态
                st.success("Search completed. Please scroll down or proceed to the next step.")
                st.stop()

    else:
        st.write("### The search and data processing is completed. Displaying visualisation results:")

        # 直接展示多年份(2020~2024)的组合热力图
        years = [2020, 2021, 2022, 2023, 2024]
        try:
            fig = combined_heatmaps_with_timeline_and_arrows(
                keywords="machinelearningandpolicy",
                years=years
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating the visualisation chart: {e}")

        if st.button("🔄 Continue searching", key="continue_btn"):
            st.session_state.search_completed = False
            # 移除 rerun；只要用户再次点击“Search”，就会重新跑流程
            st.stop()

else:
    st.warning("Please login or enter a valid API Key first.")
