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

# Here I load the code data frame and set as a global variable
CODE_DF = pd.read_csv('data/raw_data/code_country.csv')
CODE_DF = clean_columns(CODE_DF, ['state_code', 'state_name', 'country_name'])

def clean_duplicates(duplicate_final_df):
    """
    This function inputs a dataframe whose "statename" is a duplicated one.
    (i.e. different countries have the same states)
    
    Returns:
        I will check which country this state/province is really in and return a re-matched dataframe. 
    """
    
    duplicate_merged_df = duplicate_final_df.merge(
        AREA_DF,
        left_on=['state_name', 'affiliation_country'], 
        right_on=['state_name', 'country_name'],
        how='left'
    )
    selected_columns = ["state_name","affiliation_state", "affiliation_country", "affiliation_name","citied_by", "cover_date","area_km2"]
    return duplicate_merged_df[selected_columns]

def match_na_state(state_na):
    """
    This function inputs a dataframe where some samples' "affiliation_state" is "NA" (a string not nan)
    
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


def building_state_df(data,output_filename):
    """
    This function inputs a json file consists of the information for each paper
    
    Returns:
        The return is a csv file map the affiliation state to its area.
        We also do some calculations to construct an index of the academic power within the state
        Each piece of data is a state with its 
    """
    output_filename = Path(output_filename)
    paper_df = pd.DataFrame(data)
    paper_df = clean_columns(paper_df, ["affiliation_name", "affiliation_state","affiliation_city","affiliation_country"])
    state_na = paper_df[paper_df["affiliation_state"] == "na"]
    
    # First I matched the data with "NA" in "affiliation_state"
    match_na = match_na_state(state_na)
    
    # Second, match those data whose "affiliation_state" is not "NA"
    paper_df = paper_df[paper_df["affiliation_state"] != "na"]
    
    # We map the paper_df with code_df using 'state_code' and 'country_name'
    # To make sure they are for the same state/province in the same country
    # This ensures that we get the "state_name" with given code and country to match the area in provinces_area data
    merged_df = pd.merge(paper_df, CODE_DF[['state_code', 'state_name', 'country_name']], 
                        left_on=['affiliation_state', 'affiliation_country'], 
                        right_on=['state_code', 'country_name'], 
                        how='left',
                        indicator = True)
    matched_df = merged_df[merged_df["_merge"] == "both"].drop(columns=["_merge"])
    selected_columns = ["state_name", "affiliation_state", "affiliation_country", "affiliation_name","citied_by", "cover_date",]
    matched_df = matched_df[selected_columns]
    
    # Merge the mathced samples with province_area
    matched_df = matched_df.merge(
        AREA_DF,
        on = "state_name",
        how="left"
    )
    
    # We find those papers that can't match their state/province
    # Some of them don't have a code, instead, they just put the state/province name in 'affiliation_state'.
    # We can match directly with the province_area data using 'affiliation_state' for these samples.
    unmatched_df = merged_df[merged_df["_merge"] == "left_only"].drop(columns=["_merge"])
    
    # Just keep the columns in the paper_df for the unmatched samples
    unmatched_df = unmatched_df[paper_df.columns]
    unmatched_df = unmatched_df.merge(
        AREA_DF,
        left_on= 'affiliation_state',
        right_on = "state_name",
        how="left"
    )
    
    selected_columns = ["state_name", "affiliation_state", "affiliation_country", "affiliation_name","citied_by", "cover_date","area_km2"]
    unmatched_df = unmatched_df[selected_columns]

    cleaned_df = pd.concat([matched_df, unmatched_df,match_na], ignore_index=True)
    
    
    duplicate_final_df = cleaned_df[cleaned_df['state_name'].isin(DUPLICATE_STATES)]
    
    # Their area and country is unclear so we need to drop them first
    duplicate_final_df = duplicate_final_df.drop(columns=['country_name', 'area_km2'])
    duplicate_final_df = clean_duplicates(duplicate_final_df)
    
    # Merge the re-matched duplicate dataframe with the no-duplicate dataframe
    no_duplicate_df = cleaned_df[~cleaned_df['state_name'].isin(DUPLICATE_STATES)]
    final_df = pd.concat([no_duplicate_df, duplicate_final_df], ignore_index=True)
    final_df["citied_by"] = pd.to_numeric(final_df["citied_by"], errors="coerce")
    final_df.to_csv(output_filename, index=False, sep=';', encoding='utf-8')
    return final_df




def calculate_crdi(final_df, output_filename, year):
    final_df = final_df.dropna(subset=["state_name","affiliation_country","area_km2",])
    final_df["year"] = year
    final_df["month"] = final_df["cover_date"].str.extract(r"-(\d{2})-").astype(int)
    # Calculate_total num of papers for a state/province
    paper_counts = final_df.groupby(["state_name","affiliation_country"]).size().reset_index(name="total_paper_num")
    
    # Calculate_total num of total citations for a city
    citied_counts = final_df.groupby(["state_name","affiliation_country"])["citied_by"].sum().reset_index(name="total_cited_num")
    
    final_df = final_df.merge(paper_counts[["state_name","total_paper_num"]], on="state_name", how="left")
    final_df = final_df.merge(citied_counts[["state_name","total_cited_num"]], on="state_name", how="left")
    final_df["paper_num_density"] = final_df["total_paper_num"] / np.log(final_df["area_km2"] + 1)
    final_df["citation_density"] = final_df["total_cited_num"] / np.log(final_df["area_km2"] + 1)
    final_df["academic_index"] = final_df["total_cited_num"] / (final_df["total_paper_num"] + 1)
    final_df["crdi_index"] = (final_df["paper_num_density"] + final_df["citation_density"] + final_df["academic_index"]) / 3
    final_df = final_df[(final_df["state_name"] != "") & (final_df["affiliation_country"] != "")]

    selected_columns = ["state_name", "affiliation_state", "affiliation_country", "total_paper_num","total_cited_num", "area_km2", "paper_num_density", "citation_density", "academic_index", "crdi_index"]
    final_df = final_df[selected_columns]
    final_df = final_df[selected_columns].drop_duplicates(subset=["state_name", "affiliation_country"], keep="first")
    final_df = final_df.sort_values(by="crdi_index", ascending=False)

    # Output the file
    final_df.to_csv(output_filename, index=False, sep=';', encoding='utf-8')
    return final_df
    
def get_top_citations(final_df, output_filename):
    final_df["citied_by"] = pd.to_numeric(final_df["citied_by"], errors="coerce")
    grouped_df = final_df.groupby(['affiliation_name', 'state_name','affiliation_country'], as_index=False)['citied_by'].sum()
    grouped_df = grouped_df.sort_values(by='citied_by', ascending=False)
    grouped_df.to_csv( output_filename, index=False,  sep=';', encoding='utf-8')

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



YEARS = [2020,2021,2022,2023,2024]
KEY_WORDS = "machinelearningandpolicy"

if __name__ == "__main__":
    yearly_wordfrq_dict = {}
    for year in YEARS:
        data_file_name = f"data/raw_data/{KEY_WORDS}_{year}_paper.json"
        with open(data_file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Get the geography data for papers
        state_df = building_state_df(data,f"data/output_data/paper/{KEY_WORDS}_{year}_state_paper.csv")
        get_top_citations(state_df, f"data/output_data/institutions/{KEY_WORDS}_{year}_institution_citation.csv" )
        
        # Build crdi index to take the sqaure meteres into consideration
        calculate_crdi(state_df,f"data/output_data/state_crdi/{KEY_WORDS}_{year}_state_crdi.csv",year)
        word_freq = building_wordfrq_dict(data, f"data/output_data/word_frq/{KEY_WORDS}_{year}_word_frequency.csv")
        yearly_wordfrq_dict[year] = word_freq
        plot_word_cloud(word_freq, f"data/output_data/wordcloud/{KEY_WORDS}_{year}_word_cloud.png")
        print(f"Finished data-cleaning for year: {year}")
    generate_word_frq_yearlygif(yearly_wordfrq_dict)

    
   
   



