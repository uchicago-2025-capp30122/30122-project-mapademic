import streamlit as st  
import requests

st.title("Mapedemic")
st.write("根据您输入的关键词，探索来自 Science Direct 的学术论文的地理分布情况。")

# 选择登录方式
login_method = st.radio("请选择登录方式：", ("使用 API Key 登录", "使用芝加哥大学账号密码登录"))

api_key = None

if login_method == "使用 API Key 登录":
    api_key = st.text_input("请输入您的 API Key：", type="password")
elif login_method == "使用芝加哥大学账号密码登录":
    uc_username = st.text_input("请输入您的芝加哥大学账号：")
    uc_password = st.text_input("请输入您的密码：", type="password")

    # 申请 Elsevier API Key
    if st.button("获取 API Key"):
        login_url = "https://api.elsevier.com/authenticate"
        payload = {"username": uc_username, "password": uc_password}
        response = requests.post(login_url, json=payload)

        if response.status_code == 200:
            api_key = response.json().get("api_key")
            st.success("API Key 申请成功：" + api_key)
        else:
            st.error("登录失败，请检查您的账号和密码。")

# **确保 `st.session_state` 变量存在**
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False
if "discipline" not in st.session_state:
    st.session_state.discipline = ""
if "keyword" not in st.session_state:
    st.session_state.keyword = ""

# **如果 API Key 已验证**
if api_key:
    st.write("您已成功登录，API Key 已认证。")

    # **如果搜索尚未完成，显示输入框**
    if not st.session_state.search_completed:
        st.session_state.discipline = st.text_input("请输入您感兴趣的学科：", value=st.session_state.discipline)
        st.session_state.keyword = st.text_input(f"现在请输入一个关键词，以在 {st.session_state.discipline} 学科内进行细化搜索：", value=st.session_state.keyword)

        if st.button("搜索"):
            if st.session_state.keyword and st.session_state.discipline:
                st.session_state.search_completed = True  # 设置搜索完成状态
                st.rerun()  # 重新运行 Streamlit，触发页面刷新

    else:
        # **搜索完成，显示搜索结果**
        discipline = st.session_state.discipline
        keyword = st.session_state.keyword

        # **模拟爬虫数据**
        def fetch_papers(keyword, api_key):
            papers = [
                {"title": "Research on Neuroscience", "authors": ["Author 75", "Author 140"], "year": 2018,
                 "url": "https://example.com/paper0", "abstract": "This paper discusses various advancements in the field.",
                 "institution": "Tsinghua University", "coordinates": (39.9997, 116.3266)},
                
                {"title": "Research on Climate Change", "authors": ["Author 13", "Author 165"], "year": 2015,
                 "url": "https://example.com/paper1", "abstract": "This paper discusses various advancements in the field.",
                 "institution": "University of Oxford", "coordinates": (51.7548, -1.2544)},
                
                {"title": "Research on AI", "authors": ["Author 24", "Author 123"], "year": 2024,
                 "url": "https://example.com/paper3", "abstract": "This paper discusses various advancements in the field.",
                 "institution": "Massachusetts Institute of Technology", "coordinates": (42.3601, -71.0942)},
                
                {"title": "Research on AI", "authors": ["Author 62", "Author 120"], "year": 2024,
                 "url": "https://example.com/paper4", "abstract": "This paper discusses various advancements in the field.",
                 "institution": "California Institute of Technology", "coordinates": (34.1377, -118.1253)}
            ]

            filtered_papers = [p for p in papers if keyword.lower() in p["title"].lower()]
            return filtered_papers if filtered_papers else papers  # 返回匹配结果或全部论文

        # **可视化占位**
        def visualize_papers(papers):
            """可视化模块"""
            st.write("📍📍 地理分布图（等待可视化模块接入）")

        papers = fetch_papers(keyword, api_key)

        if papers:
            st.write(f"### 🔎 搜索结果（关键词：{keyword}）")

            for paper in papers:
                st.markdown(f"**[{paper['title']}]({paper['url']})**")
                st.write(f"📍 机构: {paper['institution']}")
                st.write(f"📝 摘要: {paper['abstract']}")
                st.write("---")

            # **调用可视化模块**
            visualize_papers(papers)
        else:
            st.write(f"未找到关键词 '{keyword}' 相关的论文。")

        # **"继续搜索" 按钮**
        if st.button("🔄 继续搜索"):
            st.session_state.search_completed = False  
            st.session_state.discipline = ""  
            st.session_state.keyword = ""  
            st.rerun()  # 重新运行 Streamlit
