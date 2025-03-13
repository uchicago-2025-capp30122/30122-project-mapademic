import streamlit as st   
import os
import subprocess
import requests


years = [2020, 2021, 2022, 2023, 2024]
# Import the new visualisation function in heatmap.py under the visualization branch.
from src.visualization.heatmap import combined_heatmaps_vertical_with_left_timeline
LOGO = "./doc/pics/mapademic-logo.png"
LOGO_SMALL = "./doc/pics/mapademic-logo-small.png"
st.set_page_config(page_title="Mapademic",
                   layout="centered",
                   page_icon=LOGO_SMALL,
                   initial_sidebar_state="expanded",
                   menu_items={
                       "Get Help": "mailto:peiyuch@uchicago.edu",
                       "About": "**Unfold the Map of Discovery**"
                    }
)

st.logo(
    LOGO,
    size="large"
)
st.sidebar.markdown("""
                    *Unfold the Map of Discovery*
                    """)

# 1. About Mapademic
st.sidebar.header("About")
st.sidebar.markdown("""
**Purpose**: Mapademic is an interactive platform that visualizes the global distribution and trends of academic research.  
**Approach**: We combine bibliometric data (via Scopus API) with geospatial analysis (via Natural Earth) to highlight research hotspots.  
""")

# 2. How to Use
st.sidebar.header("How to Use")
st.sidebar.markdown("""
- **Login**: Select your preferred login method (API key or University account).  
- **Enter Keywords**: Provide research keywords (e.g., “AI policy”).  
- **Select Year**: Pick the publication year or range you want to explore.  
- **View Results**: An interactive heatmap and other visualizations (word clouds, top features, etc.) will appear.
""")

# 3. Data & Method
st.sidebar.header("Data & Method")
st.sidebar.markdown("""
- **Bibliometric Data**: Retrieved from the Scopus API.  
- **Geospatial Data**: Based on Natural Earth's administrative boundaries.  
- **Research Density**: We use a custom CRDI (Comprehensive Research Density Index) to measure how concentrated research is in each region.  
""")

# 4. Team
st.sidebar.header("Team")
st.sidebar.markdown("""
- **[Allen Wu](https://github.com/songting-byte)**: API integrations, database building.  
- **[Peiyu Chen](https://github.com/Jalkey-Chen)**: Geospatial processing, heatmap visualization.  
- **[Shiyao Wang](https://github.com/Shiyao-611)**: Data cleaning, Lasso model, CRDI calculation.  
- **[Yue Pan](https://github.com/pppanyue17)**: Front-end design, user inputs, word cloud display.
""")

# 5. Cautions
st.sidebar.header("Cautions")
st.sidebar.markdown("""
- **API Key**: Keep an eye on the call limit; the project defaults to 2,000 requests per year.  
- **Geospatial Matching**: If you notice strange mismatches on the map, please report them on GitHub.
""")

# 6. Learn More
st.sidebar.header("Learn More")
st.sidebar.markdown("""
- **GitHub Repo**: https://github.com/uchicago-2025-capp30122/30122-project-mapademic  
- **Documentation**: Check out our [latest report](https://drive.google.com/file/d/1pSZaeGiK8_Asq8SryrE6Y0orglsRUPax/view?usp=sharing) for details on data sources, methods, and future improvements.  
- **Contact**: If you have any questions or find issues, please open a GitHub Issue or reach out to us. Or email peiyuch@uchicago.edu
""")

st.sidebar.markdown(
    '<p style="color: grey; font-size: 12px;">Version: 0.3 -- 12/3/2025 </p>',
    unsafe_allow_html=True
)

# 1) Initialise Session State
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False
if "global_keyword" not in st.session_state:
    st.session_state.global_keyword = ""

# 2) Application Title & Description
st.title("Mapademic")
st.write("Explore Global Academic Mobility and Knowledge Evolution")

# 3) User login
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

# 4) Global Input - Keywords
user_keyword_input = st.text_input(
    "Please enter keywords:",
    value=st.session_state.global_keyword,
    key="global_keyword_input_top"
)

if user_keyword_input:
    st.session_state.global_keyword = user_keyword_input
KEYWORDS = st.session_state.global_keyword

# 5) Main Logic: If logged in, search, visualise
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
                # Pass API Key and keywords to other function
                os.environ["API_KEY"] = api_key
                os.environ["SEARCH_KEYWORD"] = st.session_state.global_keyword

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
        #Display of combined heat maps for multiple years
        try:
            fig = combined_heatmaps_vertical_with_left_timeline(
                keywords=key_word,
                years=years
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating the visualisation chart: {e}")

        st.write("## Additional Visual Insights")


        # Addtional visulization 
        # 1) Top Features
        st.subheader("Top Features")
        # Dynamically generate multiple tabs based on year
        tabs1 = st.tabs([f"{yr}" for yr in years])

        # Bind each label to the corresponding year
        for i, yr in enumerate(years):
            with tabs1[i]:
                features_path = f"data/output_data/features/{key_word}_{yr}_features.png"
                if os.path.exists(features_path):
                    st.image(features_path, caption=f"Top features for {yr}")
                else:
                    st.warning(f"No features image found for year {yr}.")

        # 2) Word Cloud
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
        

else:
    st.warning("Please login or enter a valid API Key first.")
