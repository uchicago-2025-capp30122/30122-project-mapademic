import json
import pandas as pd
from collections import Counter
from pathlib import Path
from utils import remove, ignore, process_word_list
#from wordcloud import WordCloud
import matplotlib.pyplot as plt

def building_city_df(output_filename: Path):
    output_filename = Path(output_filename)
    with open('keyword_with_abstract.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    paper_df = pd.DataFrame(data)
    
    city_df = pd.read_excel('../../data/cities.xlsx')
    merged_df = pd.merge(paper_df, city_df[['name', 'country_name', 'state_name','latitude', 'longitude']], 
                        left_on=['affiliation_city', 'affiliation_country'], 
                        right_on=['name', 'country_name'], 
                        how='left')
    selected_columns = ["name", "state_name", "country_name", "latitude", "longitude"]
    
    df_selected = merged_df[selected_columns]
    df_selected = df_selected.dropna(subset=["state_name"])
    df_selected.to_csv(output_filename, index=False, sep=';', encoding='utf-8')

def building_wordfrq_dict(output_filename: Path):
    with open('keyword_with_abstract.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    paper_df = pd.DataFrame(data)
    abstract_list = paper_df["Abstract"].tolist()
    full_text = ignore(remove(" ".join(abstract_list).lower().split()))
    processed_list = process_word_list(full_text)
    word_freq = Counter(processed_list)
    word_freq_df = pd.DataFrame(word_freq.items(), columns=["word", "frequency"])
    word_freq_df.to_csv(output_filename, index=False, encoding="utf-8")
    # wordcloud = WordCloud(background_color='white').generate_from_frequencies(word_freq)
    # plt.figure(figsize=(10, 8))
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis('off')
    # plt.savefig('../../data/WordCloud.jpg', format='jpg', dpi=300)

if __name__ == "__main__":
    building_city_df("../../data/output_geo_data.csv")
    building_wordfrq_dict("../../data/word_frequency.csv")





# merged_freq = Counter()
# for word, freq in word_freq.items():
#     merged_freq[word] += freq

# Plot the word-cloud

# wordcloud = WordCloud(background_color='white').generate_from_frequencies(merged_freq)
# plt.figure(figsize=(10, 8))
# plt.imshow(wordcloud, interpolation='bilinear')
# plt.axis('off')
# plt.savefig('WordCloud.jpg', format='jpg', dpi=300)


# Clean city data


###

