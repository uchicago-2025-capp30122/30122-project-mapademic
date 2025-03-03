import json
import pandas as pd
from collections import Counter
from pathlib import Path
from utils import remove, ignore, process_word_list
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from visualize_words_yr import generate_word_frq_yearlygif

def building_city_df(data, output_filename: Path):
    output_filename = Path(output_filename)
    paper_df = pd.DataFrame(data)
    city_df = pd.read_excel('data/raw_data/cities.xlsx')
    merged_df = pd.merge(paper_df, city_df[['name', 'country_name', 'state_name','latitude', 'longitude']], 
                        left_on=['affiliation_city', 'affiliation_country'], 
                        right_on=['name', 'country_name'], 
                        how='left')
    selected_columns = ["name", "state_name", "country_name", "latitude", "longitude"]
    
    df_selected = merged_df[selected_columns]
    df_selected = df_selected.dropna(subset=["state_name"])
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
        building_city_df(data,f"data/output_data/{KEY_WORDS}_{year}_state_data.csv")
        word_freq = building_wordfrq_dict(data, f"data/output_data/{KEY_WORDS}_{year}_word_frequency.csv")
        yearly_wordfrq_dict[year] = word_freq
        plot_word_cloud(word_freq, f"data/output_data/{KEY_WORDS}_{year}_word_cloud.png")
    generate_word_frq_yearlygif(yearly_wordfrq_dict)

    
   
   



