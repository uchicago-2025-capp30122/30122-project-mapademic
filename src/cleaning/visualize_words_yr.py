import matplotlib.pyplot as plt
import imageio
import os

KEY_WORDS = os.environ.get("SEARCH_KEYWORD", "default_keyword_if_none").lower().replace(" ","")
YEARS = [2020,2021,2022,2023,2024]

def generate_word_frq_yearlygif(word_freq_year):
    """
    This function inputs a dictionary. Keys are the years and values are the word and frequency in that year.
    
    Returns:
        Generates the dynamic word frequency gif.
    """
    sorted_years = sorted(word_freq_year.keys())
    all_data = []
    for year in sorted_years:
        year_dict = word_freq_year[year]
        # Sort the words by frequency per year and pick the top 10
        sorted_items = sorted(year_dict.items(), key=lambda x: (-x[1], x[0]))[:10]
        words = []
        freqs = []
        # Use a tuple to save year, word list, frequency list
        for item in sorted_items:
            words.append(item[0])
            freqs.append(item[1])
        all_data.append((year, words, freqs))
    
    max_freq = 0
    for year, words, freqs in all_data:
        yearly_max = max(freqs)
        if yearly_max > max_freq:
            max_freq = yearly_max        
    max_freq = max_freq * 1.1

    filenames = []
    for idx, (year, words, freqs) in enumerate(all_data):
        plt.figure(figsize=(12, 7))
        bars = plt.barh(words, freqs, color='skyblue')
        plt.title(f'Top 10 Keywords in {year}', fontsize=14)
        plt.xlabel('Frequency', fontsize=12)
        plt.ylabel('Keywords', fontsize=12)
        plt.gca().invert_yaxis()
        plt.xlim(0, max_freq)
        for bar in bars:
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2,
                     f' {width}',
                     va='center', ha='left')
        
        plt.tight_layout()
        filename = f'data/output_data/dynamic_wordfrq/{KEY_WORDS}_{idx:03d}.png'
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        filenames.append(filename)
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(f'data/output_data/dynamic_wordfrq/{KEY_WORDS}_dynamic_wordfreq.gif', images, duration=1000, loop = 0)
