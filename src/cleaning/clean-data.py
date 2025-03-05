import json
import pandas as pd
from collections import Counter
from pathlib import Path
from utils import remove, ignore, process_word_list
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from visualize_words_yr import generate_word_frq_yearlygif
from unidecode import unidecode

def building_city_df(data, output_filename: Path):
    output_filename = Path(output_filename)
    paper_df = pd.DataFrame(data)
    code_df = pd.read_csv('data/raw_data/code_country.csv')
    
    # We map the paper_df with code_df using 'state_code' and 'country_name'
    # To make sure they are for the same state/province in the same country
    merged_df = pd.merge(paper_df, code_df[['state_code', 'state_name', 'country_name']], 
                        left_on=['affiliation_state', 'affiliation_country'], 
                        right_on=['state_code', 'country_name'], 
                        how='left',
                        indicator = True)
    
    matched_df = merged_df[merged_df["_merge"] == "both"].drop(columns=["_merge"])
    
    # We find those papers that can't match their state/province
    unmatched_df = merged_df[merged_df["_merge"] == "left_only"].drop(columns=["_merge"])
    
    
    # Load the provinces area data
    with open('data/raw_data/provinces_area.json', "r", encoding="utf-8") as f:
        area_data = json.load(f)
    area_df = pd.DataFrame(area_data)
    area_df["name"] = area_df["name"].fillna("").str.lower().str.replace(r'\s+', '', regex=True).apply(unidecode)
    area_df = area_df.rename(columns={"name": "state_name"})
    
    unmatched_df["affiliation_state"] = unmatched_df["affiliation_state"].fillna("").str.lower().str.replace(r'\s+', '', regex=True).apply(unidecode)
    matched_df["state_name"] = matched_df["state_name"].fillna("").str.lower().str.replace(r'\s+', '', regex=True).apply(unidecode)
    
    # First, I try to match the matched data using state_name.
    matched_df = matched_df.merge(
        area_df[["state_name", "area_km2"]],
        on="state_name",
        how="left"
    )
    
    # Secondly, I try to match the unmatched data with the sqaure kilometers using affiliation_state.
    # For the unmatched data, some of them don't use a code for a state/province;
    # They just used the name of the state/province, so we may map them with the area directly
    unmatched_df = unmatched_df.merge(
        area_df[["state_name", "area_km2"]],
        left_on="affiliation_state",
        right_on="state_name",
        how="left"
    )

    final_df = pd.concat([matched_df, unmatched_df], ignore_index=True)

    
    selected_columns = ["name", "state_name", "country_name", "latitude", "longitude", "citied_by", "cover_date"]
    
    df_selected = merged_df[selected_columns]
    df_selected["citied_by"] = pd.to_numeric(df_selected["citied_by"], errors="coerce")
    df_selected = df_selected.dropna(subset=["state_name"])
    df_selected.to_csv(output_filename, index=False, sep=';', encoding='utf-8')
    state_citation_totals = df_selected.groupby(["state_name"])["citied_by"].sum().reset_index(name="citied_in_state")

    # 合并计算结果回 df_selected
    df_selected = df_selected.merge(state_citation_totals, on="state_name", how="left")
    print(df_selected[:5])
    return df_selected

def calculate_crdi(df_selected, output_filename, year):
    
    df_selected["state_name"] = df_selected["state_name"].fillna("").str.lower().str.replace(r'\s+', '', regex=True).apply(unidecode)
    #paper_counts = df_selected.groupby("state_name").size().reset_index(name="paper_num")
    
    # Calculate_total num of papers for a city
    paper_counts = df_selected.groupby("state_name").size().reset_index(name="paper_num")

    # Calculate_total num of total citations for a city
    cite_counts = df_selected.groupby("state_name")["citied_by"].sum().reset_index(name="total_cited_num")

    df_selected = df_selected.merge(paper_counts, on="state_name", how="left")
    df_selected = df_selected.merge(cite_counts, on="state_name", how="left")
    df_selected["total_cited_num"] = pd.to_numeric(df_selected["total_cited_num"], errors="coerce")
    
    
    
    
    
    #df_selected["area_km2"] = pd.to_numeric(df_selected["area_km2"], errors="coerce")

    # df_selected["crdi_paper"] = df_selected["paper_num"] / df_selected["area_km2"]
    # df_selected["crdi_cite"] = df_selected["total_cited_num"] / df_selected["area_km2"]
    # df_selected["crdi_paper"] = df_selected["crdi_paper"].fillna(0)
    # df_selected["crdi_cite"] = df_selected["crdi_cite"].fillna(0)
    
    
    # with open('data/raw_data/provinces_area.json', "r", encoding="utf-8") as f:
    #     area_data = json.load(f)
    # area_df = pd.DataFrame(area_data)
    # area_df["name"] = area_df["name"].fillna("").str.lower().str.replace(r'\s+', '', regex=True).apply(unidecode)
    # area_df = area_df.rename(columns={"name": "state_name"})

    # Firstly, I map the two data with the same city character
    # df_selected = df_selected.merge(
    #     area_df[["state_name", "area_km2"]],
    #     on="state_name",
    #     how="left"
    # )
    
    # # For those data points that don't match, I need to take into consideration that use diffent representations
    # # (i.e. : Dhaka District & Dhaka)
    # for i, row in df_selected.iterrows():
    #     if pd.isna(row["area_km2"]):  # 只处理没匹配上的
    #         for j, json_row in area_df.iterrows():
    #             if row["state_name"] in json_row["state_name"] or json_row["state_name"] in row["state_name"]:  # 只要是子字符串，就匹配
    #                 df_selected.at[i, "area_km2"] = json_row["area_km2"]
    #                 break
    
    # df_selected["year"] = year
    
    
    df_selected.to_csv(output_filename, index=False, sep=';', encoding='utf-8')
    
    

def building_wordfrq_dict(data, output_filename: Path):
    output_filename = Path(output_filename)
    
    paper_df = pd.DataFrame(data)
    abstract_list = paper_df["Abstract"].tolist()
    full_text = ignore(remove(" ".join(abstract_list).lower().split()))
    processed_list = process_word_list(full_text)
    
    filtered_list = []
    for word in processed_list:
        is_keyword_substring = False
        if word in KEY_WORDS:  # 检查 word 是否是 keyword 的子字符串
            is_keyword_substring  = True
        if not is_keyword_substring:
            filtered_list.append(word)  # 只有不是子字符串的词才加入 filtered_list

    word_freq = Counter(filtered_list)
    word_freq_df = pd.DataFrame(word_freq.items(), columns=["word", "frequency"])
    word_freq_df.to_csv(output_filename, index=False, encoding="utf-8")
    return word_freq

def plot_word_cloud(word_freq, output_filename: Path):
    wordcloud = WordCloud(background_color='white').generate_from_frequencies(word_freq)
    plt.figure(figsize=(10, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig(output_filename, format='png', dpi=300)

def plot_frq_barchart(word_freq, output_filename: Path):
    word_freq = 1
    pass 


YEARS = [2020,2021,2022,2023,2024]
KEY_WORDS = "machinelearningandpolicy"

if __name__ == "__main__":
    yearly_wordfrq_dict = {}
    for year in YEARS:
        data_file_name = f"data/raw_data/{KEY_WORDS}_{year}_paper.json"
        with open(data_file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Get the geography data for papers
        new_df = building_city_df(data,f"data/output_data/{KEY_WORDS}_{year}_state_data.csv")
        
        # Build crdi model to take the sqaure meteres into consideration
        # calculate_crdi(new_df,f"data/output_data/{KEY_WORDS}_{year}_state_data.csv",year)
        word_freq = building_wordfrq_dict(data, f"data/output_data/{KEY_WORDS}_{year}_word_frequency.csv")
        yearly_wordfrq_dict[year] = word_freq
        plot_word_cloud(word_freq, f"data/output_data/{KEY_WORDS}_{year}_word_cloud.png")
    generate_word_frq_yearlygif(yearly_wordfrq_dict)

    
   
   



