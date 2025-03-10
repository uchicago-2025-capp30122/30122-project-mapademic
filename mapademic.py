import streamlit as st   
import os
import subprocess
import json
import requests
import pandas as pd

years = [2020, 2021, 2022, 2023, 2024]
# 导入 visualization 分支下的 heatmap.py 中的新可视化函数
from src.visualization.heatmap import combined_heatmaps_vertical_with_left_timeline

# 1) 初始化 Session State
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False
if "global_keyword" not in st.session_state:
    st.session_state.global_keyword = ""

# 2) 应用标题 & 说明
st.title("Mapedemic")
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

# 4) 全局输入 - 仅关键词
user_keyword_input = st.text_input(
    "Please enter keywords:",
    value=st.session_state.global_keyword,
    key="global_keyword_input_top"
)

if user_keyword_input:
    st.session_state.global_keyword = user_keyword_input
KEYWORDS = st.session_state.global_keyword

# 5) 主逻辑： 若已登录，则可以进行搜索、可视化
if api_key:
    st.write("You have successfully logged in and your API Key has been authenticated.")
    
    if not st.session_state.search_completed:
        new_keyword_input = st.text_input(
            "Update the keywords (optional):",
            value=st.session_state.global_keyword,
            key="global_keyword_input_search"
        )
        if new_keyword_input:
            st.session_state.global_keyword = new_keyword_input

        if st.button("Search", key="search_btn"):
            if st.session_state.global_keyword:
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

                st.success("Search completed. Please click on the SEARCH button and we'll start making visualizations!")
                st.stop()
    
    else:
        st.write("### The search and data processing is completed. Displaying visualisation results:")
        key_word = st.session_state.global_keyword.lower().replace(" ", "")
        # 直接展示多年份(2020~2024)的组合热力图
        try:
            fig = combined_heatmaps_vertical_with_left_timeline(
                keywords=key_word,
                years=years
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating the visualisation chart: {e}")

        st.write("## Additional Visual Insights")

        # 1) Top Features - 遍历所有年份显示
        st.subheader("Top Features")
        # 根据年份动态生成多个标签页
        tabs1 = st.tabs([f"{yr}" for yr in years])

        # 将每个标签与对应的年份绑定
        for i, yr in enumerate(years):
            with tabs1[i]:
                features_path = f"data/output_data/features/{key_word}_{yr}_features.png"
                if os.path.exists(features_path):
                    st.image(features_path, caption=f"Top features for {yr}")
                else:
                    st.warning(f"No features image found for year {yr}.")

        # 2) Word Cloud - 遍历所有年份显示
        st.subheader("Word Cloud")
        tabs2 = st.tabs([f"{yr}" for yr in years])
        for i, yr in enumerate(years):
            with tabs2[i]:
                wordcloud_path = f"data/output_data/wordcloud/{key_word}_{yr}_word_cloud.png"
                if os.path.exists(wordcloud_path):
                    st.image(wordcloud_path, caption=f"Word cloud for {yr}")
                else:
                    st.warning(f"No word cloud image found for year {yr}.")

        # 3) Dynamic Word Frequency
        st.write("## Dynamic Word Frequency")
        gif_path = f"data/output_data/dynamic_wordfrq/{key_word}_dynamic_wordfreq.gif"

        if os.path.exists(gif_path):
            st.image(gif_path)
        else:
            st.warning("No dynamic word frequency image found.")
        
        # 按钮：点击后保留 API Key，清空关键词以进行新搜索
        if st.button("Try a new search", key="new_search_btn"):
            st.session_state.search_completed = False
            st.session_state.global_keyword = ""
            st.experimental_rerun()

else:
    st.warning("Please login or enter a valid API Key first.")
