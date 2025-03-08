import pytest
from pathlib import Path
import os
import sys
import pandas as pd
import json


from src.cleaning.utils import remove, process_word_list, ignore
from src.cleaning.clean_data import calculate_crdi, clean_columns, clean_duplicates, AREA_DF, match_na_state
from src.cleaning.feature_selecting import preprocess_title


@pytest.mark.parametrize("input_words, expected_output", [
    (["hello!", "world.", "test'case"], ["hello", "world", "testcase"]),
    (["@python#", "c@de$", "w@ve%"], ["python", "cde", "wve"]),
    (["clean", "list", "words"], ["clean", "list", "words"]),
    ([], []),                                                          
])

def test_remove(input_words, expected_output):
    """
    Test that remove function removes unwanted characters correctly.
    """
    assert remove(input_words) == expected_output


@pytest.mark.parametrize("input_words, expected_output", [
    # Keep the words end with "ss"
    (["class", "boss", "miss"], ["class", "boss", "miss"]),
    # Transform "ies" to "y"
    (["cities", "puppies", "bodies", "city", "puppy", "body"], ["city", "puppy", "body", "city", "puppy", "body"]),
    # Transform the plural form that ends with "es"
    (["boxes", "churches", "foxes", "box", "church", "fox"], ["box", "church", "fox", "box", "church", "fox"]),
    # Transform the plural form that ends with "s"
    (["cars", "dogs", "cats", "car", "dog", "cat"], ["car", "dog", "cat", "car", "dog", "cat"]),
    # Normal words
    (["apple", "banana", "grape"], ["apple", "banana", "grape"]),
    # Empty lists
    ([], []),
])
def test_process_word_list(input_words, expected_output):
    assert process_word_list(input_words) == expected_output



@pytest.mark.parametrize("input_words, expected_output", [
    (["am", "is", "are","research", "study","log"], []),
    (["python", "machine", "learning"], ["python", "machine", "learning"]),
    (["a", "an", "hi", "ok"], []),
    (["123", "2025"], []),
    (["the", "university", "of", "chicago", "computer", "science", "department", "james", "cool"], ["university", "chicago", "computer", "department", "james", "cool"]),
])
def test_ignore(input_words, expected_output):
    assert ignore(input_words) == expected_output

@pytest.fixture
def sample_testcrdi_df():
    file_path = f"data/output_data/paper/machinelearningandpolicy_2023_state_paper.csv"
    return pd.read_csv(file_path, sep=";")

def test_calculate_crdi(sample_testcrdi_df, tmp_path):
    """
    Make sure the crdi is unique for every state/province in a given country
    """
    output_filename = tmp_path / "test_crdi.csv"
    result_df = calculate_crdi(sample_testcrdi_df, output_filename, 2023)
    unique_counts = result_df.groupby(["state_name", "affiliation_country"])["affiliation_state"].nunique().reset_index()
    assert (unique_counts["affiliation_state"] == 1).all()

@pytest.fixture
def sample_testcrdi_df1():
    file_path = f"data/output_data/paper/machinelearningandpolicy_2021_state_paper.csv"
    return pd.read_csv(file_path, sep=";")

def test_calculate_crdi1(sample_testcrdi_df1, tmp_path):
    """
    Make sure the crdi is unique for every state/province in a given country
    """
    output_filename = tmp_path / "test_crdi.csv"
    result_df = calculate_crdi(sample_testcrdi_df1, output_filename, 2021)
    unique_counts = result_df.groupby(["state_name", "affiliation_country"])["affiliation_state"].nunique().reset_index()
    assert (unique_counts["affiliation_state"] == 1).all()



@pytest.fixture
def test_duplicate_sample():
    """ 伪造输入 dataframe，其中有同名但不同国家的州 """
    return pd.DataFrame({
        "state_name": ["saintpaul", "saintpaul", "maryland", "maryland"],
        "affiliation_state": ["saintpaul", "saintpaul", "maryland", "maryland"],
        "affiliation_name": ["A", "B", "C", "D"],
        "affiliation_country": ["dominica", "antiguaandbarbuda", "liberia", "unitedstates"],
        "citied_by": [100, 50, 200, 30],
        "cover_date": ["2023-03-07", "2023-03-07", "2023-03-07", "2023-03-07"]
    })

def test_clean_duplicates(test_duplicate_sample):
    """ Test if clean_duplicates can match the state with the same names in different countries """
    result_df = clean_duplicates(test_duplicate_sample)
    assert result_df.loc[result_df["state_name"] == "saintpaul", "area_km2"].tolist() == [61.72450344383447, 50.729172578075755]
    assert result_df.loc[result_df["state_name"] == "maryland", "area_km2"].tolist() == [2366.628147281247, 25461.83592494935]



def test_clean_duplicates(test_duplicate_sample):
    """ Test if clean_duplicates correctly matches states with the same name in different countries """
    result_df = clean_duplicates(test_duplicate_sample)
    # saintpaul in dominica
    assert result_df.loc[
        (result_df["state_name"] == "saintpaul") & (result_df["affiliation_country"] == "dominica"),
        "area_km2"
    ].values[0] == pytest.approx(61.72450344383447, rel=1e-6)  # 允许 1e-6 相对误差

    # saintpaul in antiguaandbarbuda
    assert result_df.loc[
        (result_df["state_name"] == "saintpaul") & (result_df["affiliation_country"] == "antiguaandbarbuda"),
        "area_km2"
    ].values[0] == pytest.approx(50.729172578075755, rel=1e-6)

    # maryland in liberia
    assert result_df.loc[
        (result_df["state_name"] == "maryland") & (result_df["affiliation_country"] == "liberia"),
        "area_km2"
    ].values[0] == pytest.approx(2366.628147281247, rel=1e-6)

    # maryland in unitedstates
    assert result_df.loc[
        (result_df["state_name"] == "maryland") & (result_df["affiliation_country"] == "unitedstates"),
        "area_km2"
    ].values[0] == pytest.approx(25461.83592494935, rel=1e-6)



@pytest.fixture
def test_NA_sample():
    """ 伪造输入 dataframe，其中有同名但不同国家的州 """
    return pd.DataFrame({
        "affiliation_city": ["beijing", "shanghai", "zabol", "washington,d.c."],
        "affiliation_state": ["NA", "NA", "NA", "NA", ],
        "affiliation_name": ["A", "B", "C", "D"],
        "affiliation_country": ["china", "china", "iran", "unitedstates"],
        "citied_by": [100, 50, 200, 30],
        "cover_date": ["2023-03-07", "2023-03-07", "2023-03-07", "2023-03-07"]
    })



def test_NA_match(test_NA_sample):
    """ Test if clean_duplicates correctly matches states with the same name in different countries """
    result_df = match_na_state(test_NA_sample)
    # saintpaul in dominica
    assert result_df.loc[(result_df["state_name"] == "beijing"), "area_km2"].values[0] == pytest.approx(16251.9254289633, rel=1e-6)
    assert result_df.loc[(result_df["state_name"] == "shanghai"), "area_km2"].values[0] == pytest.approx(6746.0374352377, rel=1e-6)
    assert result_df.loc[(result_df["state_name"] == "washington,d.c."), "area_km2"].values[0] == pytest.approx(174111.6091089331, rel=1e-6)
    assert len(result_df.loc[(result_df["state_name"] == "zabol"), "area_km2"].tolist()) == 0


@pytest.mark.parametrize("input_title, expected_output", [
    ("The 3 great Projects 2025", "great projects"),
    ("Hello World", "hello world"),
    ("", ""),
    ("@CAPP# Awesome!", "capp awesome"),
])
def test_preprocess_title(input_title, expected_output):
    """
    测试 preprocess_title 函数是否正确处理标题。
    """
    result = preprocess_title(input_title)
    assert result == expected_output