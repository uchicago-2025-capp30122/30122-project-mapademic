import matplotlib.pyplot as plt
import imageio
import os
KEY_WORDS = "machinelearningandpolicy"

def generate_word_frq_yearlygif(word_freq_year):
    
    sorted_years = sorted(word_freq_year.keys())
    all_data = []
    for year in sorted_years:
        year_dict = word_freq_year[year]
        sorted_items = sorted(year_dict.items(), key=lambda x: (-x[1], x[0]))[:10]
        words = [item[0] for item in sorted_items]
        freqs = [item[1] for item in sorted_items]
        all_data.append((year, words, freqs))

    # 计算最大频率用于统一x轴
    max_freq = max(max(freqs) for _, _, freqs in all_data) * 1.1

    # 生成每帧图像
    filenames = []
    for idx, (year, words, freqs) in enumerate(all_data):
        plt.figure(figsize=(12, 7))
        
        # 创建水平条形图
        bars = plt.barh(words, freqs, color='skyblue')
        plt.title(f'Top 10 Keywords in {year}', fontsize=14)
        plt.xlabel('Frequency', fontsize=12)
        plt.ylabel('Keywords', fontsize=12)
        plt.gca().invert_yaxis()  # 将最高频显示在最上方
        plt.xlim(0, max_freq)
        
        # 在条形末端显示频率值
        for bar in bars:
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2,
                     f' {width}',
                     va='center', ha='left')
        
        plt.tight_layout()
        
        # 保存图像
        filename = f'data/output_data/dynamic_wordfrq/frame_{idx:03d}.png'
        # filename = f'frame_{idx:03d}.png'
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        filenames.append(filename)

    # 创建GIF（需要安装imageio）
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(f'data/output_data/dynamic_wordfrq/{KEY_WORDS}_dynamic_wordfreq.gif', images, duration=1000)
