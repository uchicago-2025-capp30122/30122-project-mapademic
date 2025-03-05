import json
import pandas as pd
import numpy as np
from collections import Counter
from pathlib import Path
from utils import remove, ignore, process_word_list
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from visualize_words_yr import generate_word_frq_yearlygif
from unidecode import unidecode


def clean_columns(df, columns):
    """
    This function inputs a df and clean specified columns:
    1. Filling NA values with an empty string.
    2. Converting text to lowercase.
    3. Removing all whitespace.
    4. Converting accented characters to ASCII.
    
    
    Returns:
        a cleaned-version dataframe.
    """
    for column in columns:
        df[column] = df[column].fillna("").str.lower().str.replace(r'\s+', '', regex=True).apply(unidecode)
    return df

# Here I load the provinces_area data and set as a global variable
with open('data/raw_data/provinces_area.json', "r", encoding="utf-8") as f:
    area_data = json.load(f)
AREA_DF = pd.DataFrame(area_data)
# Rename the column so it is easier to merge later
AREA_DF = AREA_DF.rename(columns={"name": "state_name"})
AREA_DF = AREA_DF.rename(columns={"admin": "country_name"})
AREA_DF = clean_columns(AREA_DF, ["state_name", "country_name"])
state_name_counts = AREA_DF['state_name'].value_counts()
DUPLICATE_STATES  = state_name_counts[state_name_counts > 1].index.tolist()
DUPLICATE_STATES = set(filter(None, DUPLICATE_STATES))

def match_na_state(state_na):
    """
    This function inputs a dataframe where "affiliation_state" is "NA" (a string not nan)
    
    Returns:
        I will check if we can match the data to the state_area. 
        If no match is found, state_name and area_km2 will remain NaN.
    """
    
    # For some "NA" data, they are the capital city in the country
    # So we may match directly using "affiliation_city" and 
    matched_df = state_na.merge(
        AREA_DF,
        left_on= "affiliation_city",
        right_on= "state_name",
        how="left",
        indicator=True
    )
    selected_columns = ["state_name","affiliation_state", "affiliation_country", "affiliation_name","citied_by", "cover_date","area_km2"]
    return matched_df[selected_columns]
    
def building_city_df(data,output_filename):
    """
    This function inputs a json file consists of the information for each paper
    
    Returns:
        The return is a csv file map the affiliation state to its area.
        We also do some calculations to construct an index of the academic power within the state
        Each piece of data is a state with its 
    """
    output_filename = Path(output_filename)
    paper_df = pd.DataFrame(data)
    paper_df = clean_columns(paper_df, ["affiliation_state","affiliation_city","affiliation_country"])
    state_na = paper_df[paper_df["affiliation_state"] == "na"]
    
    # First I matched the data with "NA" in "affiliation_state"
    match_na = match_na_state(state_na)
    print("NA:")
    print(match_na[:3])
    # Second, match those data whose "affiliation_state" is not "NA"
    paper_df = paper_df[paper_df["affiliation_state"] != "na"]
    
    
    code_df = pd.read_csv('data/raw_data/code_country.csv')
    code_df = clean_columns(code_df, ['state_code', 'state_name', 'country_name'])
    
    # We map the paper_df with code_df using 'state_code' and 'country_name'
    # To make sure they are for the same state/province in the same country
    merged_df = pd.merge(paper_df, code_df[['state_code', 'state_name', 'country_name']], 
                        left_on=['affiliation_state', 'affiliation_country'], 
                        right_on=['state_code', 'country_name'], 
                        how='left',
                        indicator = True)
    matched_df = merged_df[merged_df["_merge"] == "both"].drop(columns=["_merge"])
    
    selected_columns = ["state_name", "affiliation_state", "affiliation_country", "affiliation_name","citied_by", "cover_date",]
    matched_df = matched_df[selected_columns]
    matched_df = matched_df.merge(
        AREA_DF,
        on = "state_name",
        how="left"
    )
    print("看看什么Match上了：")
    print(matched_df[:5])
    
    # We find those papers that can't match their state/province
    # Some of them don't have a code, instead, they just put the state/province name in 'affiliation_state'.
    # We can match directly using the province_area data
    unmatched_df = merged_df[merged_df["_merge"] == "left_only"].drop(columns=["_merge"])
    unmatched_df = unmatched_df[selected_columns]
    # First, I try to match the matched data using state_name.
    unmatched_df = unmatched_df.merge(
        AREA_DF,
        left_on= 'affiliation_state',
        right_on = "state_name",
        how="left"
    )
    unmatched_df["state_name"] = unmatched_df["state_name_y"].fillna(unmatched_df["state_name_x"])
    unmatched_df.drop(columns=["state_name_x", "state_name_y"], inplace=True)
    print("看看没Match上的现在怎么了：")
    print(unmatched_df[:5])
    # Secondly, I try to match the unmatched data with the sqaure kilometers using affiliation_state.
    # For the unmatched data, some of them don't use a code for a state/province;
    # They just used the name of the state/province, so we may map them with the area directly
    

    final_df = pd.concat([matched_df, unmatched_df,match_na], ignore_index=True)
    # 筛选出 final_df 中 state_name 在 duplicates 中的行
    filtered_final_df = final_df[final_df['state_name'].isin(DUPLICATE_STATES)]
    filtered_final_df = filtered_final_df.drop(columns=['country_name', 'area_km2'])
    no_duplicate_df = final_df[~final_df['state_name'].isin(DUPLICATE_STATES)]
    # 使用 merge 将 filtered_final_df 和 AREA_DF 按照 'state_name' 和 'affiliation_country' / 'country_name' 进行匹配
    filter_merged_df = filtered_final_df.merge(
        AREA_DF,
        left_on=['state_name', 'affiliation_country'], 
        right_on=['state_name', 'country_name'],
        how='left'  # 选择左连接（如果匹配不到会填充 NaN）
    )
    final_df = pd.concat([no_duplicate_df, filter_merged_df], ignore_index=True)
    print("Finally!!!")
    print(final_df[:10])
    final_df.to_csv(output_filename, index=False, sep=';', encoding='utf-8')
    print("Finished")
    return final_df

def calculate_crdi(final_df, output_filename, year):
    final_df = final_df.dropna(subset=["state_name"])
    final_df = final_df.dropna(subset=["area_km2"])
    final_df["year"] = year
    final_df["month"] = final_df["cover_date"].str.extract(r"-(\d{2})-").astype(int)
    final_df["citied_by"] = pd.to_numeric(final_df["citied_by"], errors="coerce")
    
    #final_df = pd.to_numeric(final_df["area_km2"], errors="coerce")
    # Calculate_total num of papers for a state/province
    paper_counts = final_df.groupby("state_name").size().reset_index(name="total_paper_num")
    
    # Calculate_total num of total citations for a city
    citied_counts = final_df.groupby("state_name")["citied_by"].sum().reset_index(name="total_cited_num")

    final_df = final_df.merge(paper_counts, on="state_name", how="left")
    final_df = final_df.merge(citied_counts, on="state_name", how="left")
    final_df["paper_num_density"] = final_df["total_paper_num"] / np.log(final_df["area_km2"] + 1)
    final_df["citation_density"] = final_df["total_cited_num"] / np.log(final_df["area_km2"] + 1)
    final_df["academic_index"] = final_df["total_cited_num"] / (final_df["total_paper_num"] + 1)
    final_df["crdi_index"] = (final_df["paper_num_density"] + final_df["citation_density"] + final_df["academic_index"]) / 3
    print(final_df[:3])
    
    
    
    final_df.to_csv(output_filename, index=False, sep=';', encoding='utf-8')
    
def get_top_citations(final_df):
    final_df["citied_by"] = pd.to_numeric(final_df["citied_by"], errors="coerce")
    grouped_df = final_df.groupby(['affiliation_name', 'affiliation_country'], as_index=False)['citied_by'].sum()
    grouped_df = grouped_df.sort_values(by='citied_by', ascending=False)
    grouped_df.to_csv('grouped_cited_by.csv', index=False)

    # 输出结果
    print(grouped_df)

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



#YEARS = [2020,2021,2022,2023,2024]
YEARS = [2020]
KEY_WORDS = "machinelearningandpolicy"

if __name__ == "__main__":
    yearly_wordfrq_dict = {}
    for year in YEARS:
        data_file_name = f"data/raw_data/{KEY_WORDS}_{year}_paper.json"
        with open(data_file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Get the geography data for papers
        new_df = building_city_df(data,f"data/output_data/{KEY_WORDS}_{year}_state_data1.csv")
        get_top_citations(new_df)
        # Build crdi model to take the sqaure meteres into consideration
        calculate_crdi(new_df,f"data/output_data/province/{KEY_WORDS}_{year}_state_data.csv",year)
        
        #这里是对的但我先注释掉
        # word_freq = building_wordfrq_dict(data, f"data/output_data/{KEY_WORDS}_{year}_word_frequency.csv")
        # yearly_wordfrq_dict[year] = word_freq
        # plot_word_cloud(word_freq, f"data/output_data/{KEY_WORDS}_{year}_word_cloud.png")
    #这里也是对的
    # generate_word_frq_yearlygif(yearly_wordfrq_dict)

    
   
   



