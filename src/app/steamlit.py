import streamlit as st
import os
import subprocess
import json
import requests
import pandas as pd

# 导入 visualization 分支下的 basic_vis.py 中的函数
from src.visualization.basic_vis import generate_basic_choropleth_map

st.title("Mapedemic-Demo")
st.write("Explore the geographic distribution of academic papers from Science Direct based on the keywords you enter.")

# 选择登录方式
login_method = st.radio("Please select the login method:", ("Login with API Key", "Login with University of Chicago Account Password"))

api_key = None
if login_method == "Login with API Key":
    api_key = st.text_input("Please enter your API Key:", type="password")
elif login_method == "Log in with your University of Chicago account password":
    uc_username = st.text_input("Please enter your University of Chicago account number:")
    uc_password = st.text_input("Please enter your password:", type="password")
    if st.button("Get API Key"):
        login_url = "https://api.elsevier.com/authenticate"
        payload = {"username": uc_username, "password": uc_password}
        response = requests.post(login_url, json=payload)
        if response.status_code == 200:
            api_key = response.json().get("api_key")
            st.success("API Key Application successful:" + api_key)
        else:
            st.error("Login failed, please check your account and password.")

# 确保 st.session_state 中相关变量存在
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False
if "discipline" not in st.session_state:
    st.session_state.discipline = ""
if "keyword" not in st.session_state:
    st.session_state.keyword = ""

if api_key:
    st.write("You have successfully logged in and your API Key has been authenticated.")
    if not st.session_state.search_completed:
        st.session_state.discipline = st.text_input("Please enter the subject you are interested in:", value=st.session_state.discipline)
        st.session_state.keyword = st.text_input("Please enter keywords：", value=st.session_state.keyword)
        if st.button("Search"):
            if st.session_state.keyword and st.session_state.discipline:
                # 将 API Key 设置为环境变量，供外部脚本使用
                os.environ["API_KEY"] = api_key

                st.info("The API is being called to get the data, please wait...")
                # 调用 api-calling 分支下的 keyword_search.py 脚本
                subprocess.run(["python", "api-calling/keyword_search.py"])

                st.info("The data cleaning script is being called, please wait...")
                # 调用 cleaning 分支下的 clean-data.py 脚本
                subprocess.run(["python", "cleaning/clean-data.py"])

                st.session_state.search_completed = True
                st.experimental_rerun()
    else:
        st.write("### The search and data processing is completed and the visualisation results are displayed:")
        # 使用 basic_vis.py 中的函数生成 choropleth 地图
        try:
            fig = generate_basic_choropleth_map()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating a visualisation chart:{e}")
        
        if st.button("🔄 Continue searching"):
            st.session_state.search_completed = False  
            st.session_state.discipline = ""  
            st.session_state.keyword = ""  
            st.experimental_rerun()
else:
    st.warning("Please login or enter a valid API Key first.")
