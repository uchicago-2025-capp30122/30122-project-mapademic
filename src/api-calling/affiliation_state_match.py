import json
import requests
import os
import streamlit as st

KEYWORDS = os.environ.get("SEARCH_KEYWORD", "default_keyword_if_none")

def generate_filenames(keyword, start_year, end_year):
    year_filenames = []
    keyword_lower = keyword.lower().replace(" ","")
    for year in range(start_year, end_year + 1):
        filename = f"data/raw_data/{keyword_lower}_{year}_paper.json"
        year_filenames.append((year, filename))
    return year_filenames

keywords = KEYWORDS
FILENAME_LST = generate_filenames(keywords, 2020, 2024)

SEARCH_RESULT = set()
STATE_DICT = {}

try:
    API_KEY = os.environ["API_KEY"]
except KeyError:
    raise Exception(
        "Make sure that you have set the API Key environment variable as "
        "described in the README."
    )

# Scopus API Configuration for affiliation search function
AFFILIATION_URL = "https://api.elsevier.com/content/affiliation"
HEADERS = {
    "Accept": "application/json",
    "X-ELS-APIKey": API_KEY
}

def affiliation_state(afid):
    affiliation_url = f"{AFFILIATION_URL}/affiliation_id/{afid}"
    try:
        response = requests.get(affiliation_url, headers=HEADERS)
        response.raise_for_status()  # Raise error for bad HTTP response

        data = response.json()

        # Initialize state_info with default value
        state_info = "NA"

        affiliation_retrieval_response = data.get("affiliation-retrieval-response")
        if affiliation_retrieval_response:
            institution_profile = affiliation_retrieval_response.get("institution-profile")
            if institution_profile:
                address = institution_profile.get("address")
                if address:
                    state_info = address.get("state", "NA")
        
        return state_info

    # Using try..except.. here to make sure even if the building dict meets problem, the program can keep running
    # At the same time, the problem can easily been seen and fixed, majorly due to too many API calling
    except requests.exceptions.RequestException as e: 
        print(f"Error fetching affiliation data for {afid}: {e}")
        return "NA"

def generate_state_date(filename):
    with open (filename, "r") as resource:
        raw_data = json.load(resource)
        for each_search in raw_data:
            SEARCH_RESULT.add(each_search.get("affiliation_id"))
    
    return SEARCH_RESULT

# Using magic number [0:5] here and bolew showing 5 elements (5 years through 2020-2024)
for filename in FILENAME_LST[0:5]:
    generate_state_date(filename[1])

# print(FILENAME_LST[0:5])
print(len(SEARCH_RESULT))

file_path = "data/raw_data/afid_state_dataset.json"

if os.path.exists(file_path):
    # Keeping updating the JSON(dict), without covering anything written before
    try:
        with open(file_path, "r") as base_dataset:
            STATE_DICT = json.load(base_dataset)
    except json.JSONDecodeError:  # Handle empty or broken JSON file
        STATE_DICT = {}  
else:
    STATE_DICT = {}

# print statement in this loop, is to let users know the program is actually working, since large amount of searching results cost time.
for each_ID in SEARCH_RESULT:
    if each_ID in STATE_DICT:
        print(f"{each_ID} already here") 
        continue
    else:
        print(f"Added {each_ID}")
        STATE_DICT[each_ID] = affiliation_state(each_ID)
    
with open ("data/raw_data/afid_state_dataset.json", "w") as base_dataset:
    json.dump(STATE_DICT, base_dataset, ensure_ascii=False, indent=4)

    for filename in FILENAME_LST[0:5]:
        # Since the each element's struction in FILENAME_LST is (year, filename), filename[1] below indicates the file name
        with open(filename[1], "r") as resource:
            paper_data = json.load(resource)

        for each_paper in paper_data:
            each_paper["affiliation_state"] = STATE_DICT.get(each_paper["affiliation_id"], "NA")
        
        with open(filename[1], "w") as resource:
            json.dump(paper_data, resource, ensure_ascii=False, indent=4)