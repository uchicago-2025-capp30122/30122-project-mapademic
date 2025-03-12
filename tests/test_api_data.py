import importlib.util
import json
import time
import os
import pytest
import sys
import pandas as pd
import importlib

test_sample = "tests/sample.json"
sample_filtered = "tests/sample_test.json"

# Due to initially filename with "-" (path: src/api-calling), cannot use from..import.. to directly import function
module_path = "src/api-calling/keyword_search.py"
module_name = "keyword_search"

path_spec = importlib.util.spec_from_file_location(module_name,module_path)
keyword_search_module = importlib.util.module_from_spec(path_spec)
path_spec.loader.exec_module(keyword_search_module)
build_function = getattr(keyword_search_module,"build_paper_json")

# Make sure the data process all the api search result, not dropping anyone
raw_api_data = pd.read_json("data/raw_data/raw_api_data/machinelearningandpolicy_2023_raw.json")
procress_api_data = pd.read_json("data/raw_data/machinelearningandpolicy_2023_paper.json")

def test_completeness():
    assert len(raw_api_data) == len(procress_api_data)

# Test with all the info, if the data filtering working
def test_build_paper_json_standard():
    build_function(test_sample,sample_filtered)

    with open(sample_filtered,"r") as f:
        paper_data = json.load(f)
        
    assert len(paper_data) == 3
    assert paper_data[0]["paper_title"] == "LEGAL INSTRUMENTS FOR ENVIRONMENTAL PROTECTION AND COMBATTING CLIMATE CHANGE IN THE COMMON AGRICULTURAL POLICY 2023–2027"
    assert paper_data[0]["affiliation_name"] == "Institute of Legal Studies of the Polish Academy of Sciences"
    assert paper_data[0]["paper_author"] == "Włodarczyk B."

# Test if without author_name, if the corresponding key with the value "0"
def test_build_paper_json_missing_author():
    with open(sample_filtered,"r") as f:
        paper_data = json.load(f)
        
    assert len(paper_data) == 3
    assert paper_data[1]["paper_title"] == "LEGAL INSTRUMENTS FOR ENVIRONMENTAL PROTECTION AND COMBATTING CLIMATE CHANGE IN THE COMMON AGRICULTURAL POLICY 2023–2027"
    assert paper_data[1]["affiliation_name"] == "NA"
    assert paper_data[1]["paper_author"] == "NA"

# Test if without affiliation, if the corresponding key with the value "0"
def test_build_paper_json_missing_affiliation():
    with open(sample_filtered,"r") as f:
        paper_data = json.load(f)
        
    assert len(paper_data) == 3
    assert paper_data[2]["paper_title"] == "LEGAL INSTRUMENTS FOR ENVIRONMENTAL PROTECTION AND COMBATTING CLIMATE CHANGE IN THE COMMON AGRICULTURAL POLICY 2023–2027"
    assert paper_data[2]["affiliation_name"] == "NA"
    assert paper_data[2]["paper_author"] == "Włodarczyk B."