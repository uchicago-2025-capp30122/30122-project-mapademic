import json
import re
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer
from utils import remove
import matplotlib.pyplot as plt

def preprocess_title(title):
    title = title.lower()  # 转小写
    title = re.sub(r'\d+', '', title)  # 去除所有数字
    words = title.split()  # 分词
    words = remove(words)  # 去除特殊字符
    return ' '.join(words)  # 重新组合成字符串

def get_feature(output_filename: Path):
    with open('data/keyword_with_abstract.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    paper_df = pd.DataFrame(data)
    # 预处理标题


    # 处理文章-词频矩阵
    paper_df["cleaned_title"] = paper_df["paper_title"].astype(str).apply(preprocess_title)
    vectorizer = CountVectorizer(ngram_range=(1, 3))
    X = vectorizer.fit_transform(paper_df["cleaned_title"])
    word_freq_df = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())

    # 处理文章-作者矩阵
    author_matrix = pd.get_dummies(paper_df["paper_author"]).astype(int)

    # 合并文章-作者矩阵和文章-词频矩阵
    final_matrix = pd.concat([author_matrix, word_freq_df], axis=1)

    # 结果
    if "NA" in final_matrix.columns:
        final_matrix = final_matrix.drop(columns=["NA"])


    paper_df["log_cited_by"] = np.log1p(paper_df["citied_by"].astype(int))

    X = final_matrix  # 文章-作者 + 文章-词频 矩阵
    y = paper_df["log_cited_by"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)



    lasso = Lasso(alpha=0.01, max_iter=1000)  # 设定一个合适的 alpha
    lasso.fit(X_scaled, y)

    coef_series = pd.Series(lasso.coef_, index=X.columns)
    non_zero_coefs = coef_series[coef_series != 0].abs().sort_values(ascending=True)
    
    non_zero_coefs = coef_series[coef_series != 0].sort_values(key=abs, ascending=False)
    top_30_features = non_zero_coefs.head(30)
    inverse_top_30_features = top_30_features.iloc[::-1]
    # 颜色映射：红色表示正向影响，蓝色表示负向影响
    colors = ['red' if coef > 0 else 'blue' for coef in inverse_top_30_features.values]

    # 绘制水平条形图
    plt.figure(figsize=(10, 6))
    bars = plt.barh(inverse_top_30_features.index, inverse_top_30_features.values, color=colors, alpha=0.7)

    # 在 0 处添加垂直参考线
    plt.axvline(0, color='black', linestyle='--', linewidth=1)

    # 添加标题和标签
    plt.xlabel("Coefficient Value")
    plt.ylabel("Variables")
    plt.title("Top 30 Lasso Regression Coefficients")
    plt.savefig(output_filename, format='png', dpi=300)
    print("The top k features for citing:")
    print(top_30_features[:10])
    

if __name__ == "__main__":
    # building_city_df("data/output_geo_data.csv")
    # word_freq = building_wordfrq_dict("data/word_frequency.csv")
    # plot_word_cloud(word_freq, "data/word_cloud.png")
    get_feature("data/features.png")