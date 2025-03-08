import json
import re
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer
from .utils import remove,ignore
import matplotlib.pyplot as plt

def preprocess_title(title):
    title = title.lower()
    title = re.sub(r'\d+', '', title)
    words = title.split()
    words = ignore(remove(words))
    return ' '.join(words)

def get_feature(data_filename, output_filename: Path):
    with open(data_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    paper_df = pd.DataFrame(data)
    paper_df["cleaned_title"] = paper_df["paper_title"].apply(preprocess_title)
    
    # 1-gram and 2-gram are included in the model
    vectorizer = CountVectorizer(ngram_range=(1, 3))
    X = vectorizer.fit_transform(paper_df["cleaned_title"])
    word_freq_df = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())

    # Get the paper-author matrix
    author_matrix = pd.get_dummies(paper_df["paper_author"]).astype(int)
    
    # Final matrix is the combinition of frequency matrix and author matrix
    final_matrix = pd.concat([author_matrix, word_freq_df], axis=1)
    if "NA" in final_matrix.columns:
        final_matrix = final_matrix.drop(columns=["NA"])

    # Number of citations is a skewed distribution so I took the log of the number here
    paper_df["log_cited_by"] = np.log1p(paper_df["citied_by"].astype(int))
    
    # Fit a Lasso Model
    X = final_matrix
    y = paper_df["log_cited_by"]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    lasso = Lasso(alpha=0.01, max_iter=1000)
    lasso.fit(X_scaled, y)
    coef_series = pd.Series(lasso.coef_, index=X.columns)
    non_zero_coefs = coef_series[coef_series != 0].sort_values(key=abs, ascending=False)
    top_30_features = non_zero_coefs.head(30)
    inverse_top_30_features = top_30_features.iloc[::-1]
    
    # I used red to display the positive value and blue for the negative
    colors = ['red' if coef > 0 else 'blue' for coef in inverse_top_30_features.values]
    plt.figure(figsize=(10, 6))
    bars = plt.barh(inverse_top_30_features.index, inverse_top_30_features.values, color=colors, alpha=0.7)
    plt.axvline(0, color='black', linestyle='--', linewidth=1)
    plt.xlabel("Coefficient Value")
    plt.ylabel("Variables")
    plt.title("Top 30 Lasso Regression Coefficients")
    plt.savefig(output_filename, format='png', dpi=300)

YEARS = [2020,2021,2022,2023,2024]
KEY_WORDS = "machinelearningandpolicy"

if __name__ == "__main__":
    for year in YEARS:
        data_file_name = f"data/raw_data/{KEY_WORDS}_{year}_paper.json"  
        get_feature(data_file_name, f"data/output_data/features/{KEY_WORDS}_{year}_features.png")
