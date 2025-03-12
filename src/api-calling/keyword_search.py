import requests
import json
import time
import os
import streamlit as st

# Remember to use the command 'export API_KEY="your API Key"' at the every beginning
try:
    API_KEY = os.environ["API_KEY"]
except KeyError:
    raise Exception(
        "Make sure that you have set the API Key environment variable as "
        "described in the README."
    )

KEYWORDS = os.environ.get("SEARCH_KEYWORD", "default_keyword_if_none")

# Scopus API Configuration for keyword search function
SEARCH_URL = "https://api.elsevier.com/content/search/scopus"
HEADERS = {
    "Accept": "application/json",
    "X-ELS-APIKey": API_KEY
}

PAGE_SIZE = 25 # When set the parameter "view" as "COMPLETE", MAXIMUM be 25 !!!
               # when set the parameter "view" as "STANDARD", Maximum could be 200

def get_total_results(keywords, year):
    # Fetch total number of search results to check how many exist.
    # Reason: for every search, api would response the total number of the searching results 
    params = {
        "query": f"TITLE-ABS-KEY({keywords}) AND PUBYEAR = {year}",
        "httpAccept": "application/json",
        "count": 1  # Only fetch metadata
    }

    response = requests.get(SEARCH_URL, headers=HEADERS, params=params)

    if response.status_code == 200:
        data = response.json()
        total_results = int(data["search-results"]["opensearch:totalResults"])
        print(f"Total available results: {total_results}")
        return total_results
    else:
        print(f"❌ Error fetching total results: {response.status_code}")
        return 0
    
def fetch_results_with_cursor(keywords, year):
    # Fetch results using cursor-based pagination and save to JSON
    total_available = get_total_results(keywords, year)  # Check total results

    if total_available == 0:
        print("⚠️ No results found. Exiting.")
        return

    results = []
    cursor = "*"  # First request starts with cursor="*"
    retrieved_count = 0
    MAX_RESULTS = 25 # Using for demo
    # MAX_RESULTS = total_available # Number of results to fetch

    while retrieved_count < min(MAX_RESULTS, total_available):
        params = {
            "query": f"TITLE-ABS-KEY({keywords}) AND PUBYEAR = {year}",
            "httpAccept": "application/json",
            "count": PAGE_SIZE,  # Max results per request
            "sort": "-citedby-count", # Sort the search result by the cited amout ("-" in front means descending)
            "cursor": cursor,  # Cursor-based pagination
            "view": "COMPLETE" # The "COMPLETE" option can only be used through school network, comfired by scopus support team
                                # Again! Important, under "COMPLETE", PAGE_SIZE can maximum be set as 25
        }

        response = requests.get(SEARCH_URL, headers=HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            entries = data.get("search-results", {}).get("entry", [])

            if not entries:
                print("⚠️ No more results found. Stopping pagination.")
                break  # Stop if no more results

            results.extend(entries)
            retrieved_count += len(entries)
            print(f"✅ Retrieved {retrieved_count}/{min(MAX_RESULTS, total_available)} results...")

            # Extract next cursor
            next_cursor = data["search-results"].get("cursor", {}).get("@next", None)

            # Debugging for the cursor
            # print(f"Next Cursor: {next_cursor}")

            if not next_cursor:
                print("No further cursor available. Ending fetch.")
                break  # Stop if cursor is missing

            # Update cursor for next request
            cursor = next_cursor

            # Avoid hitting API rate limits
            time.sleep(0.5)

        # Major error type presented in the offical documentation. (400 majorly due to cursor; 429 is about api limit)
        elif response.status_code == 400:
            print(f"❌ Error 400: Bad Request - Possible Query or Cursor Issue. Response: {response.text}")
            break

        elif response.status_code == 401:
            print("❌ Error 401: Access Denied - Missing/invalid credentials.")

        elif response.status_code == 403:
            print("❌ Error 403: Access Denied - Check API Key Permissions.")
            break

        elif response.status_code == 404:
            print("❌ Error 404: Requested resource not found.")
            break

        elif response.status_code == 405:
            print("❌ Error 405: Invalid http method.")
            break

        elif response.status_code == 406:
            print("❌ Error 405: Invalid mime method.")
            break

        elif response.status_code == 429:
            print("⚠️ API Quota Exceeded! Waiting before retrying...")
            time.sleep(10)  # Wait 10 seconds before retrying
            continue

        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            break

    # Save results as JSON
    save_results(results)

def generate_filenames(keyword, start_year, end_year):
    year_filenames = []
    keyword_lower = keyword.lower().replace(" ","")
    for year in range(start_year, end_year + 1):
        filename = f"data/raw_data/raw_api_data/{keyword_lower}_{year}_raw.json"
        year_filenames.append((year, filename))
    return year_filenames

def save_results(results):
    # Save results to a JSON file
    with open(FILENAME, "w", encoding="utf-8") as f:
        # ensure_ascii=False here and below is necessary to encoding some "hard-to-read" code in the result
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"Results saved to {FILENAME}")

if __name__ == "__main__":
    FILENAME_LST = generate_filenames(KEYWORDS, 2020, 2024)

    for each_year_result in FILENAME_LST:
        year, FILENAME = each_year_result[0], each_year_result[1]

        if os.path.exists(FILENAME):  # Check if the file exists
            print(f"File already exists: {FILENAME}, skipping fetch.")
        else:
            print(f"Fetching data for {year}...")
            fetch_results_with_cursor(KEYWORDS, year)
    
def build_paper_json(FILENAME,filename_filtered):
    with open (filename_filtered,"w") as f:
        with open (FILENAME, "r") as resource:
            keyword_result = []
            raw_data = json.load(resource)
            for each_search in raw_data:
                # Important!! Using dict.get is necessary and safe, since there exsists missing part of the imfo          
                search_result = {
                    "paper_title": each_search.get("dc:title","NA"),
                    # "paper_author": each_search.get("dc:creator","NA"),
                    "publication": each_search.get("prism:publicationName","NA"),
                    "citied_by": each_search.get("citedby-count","NA"),
                    "cover_date" : each_search.get("prism:coverDate","NA"),
                    "Abstract": each_search.get("dc:description","NA"),
                    "DOI": each_search.get("prism:doi","NA")
                }

                author = each_search.get("author",[])
                if author and isinstance(author, list) and len(author) > 0:
                    search_result["paper_author"] = author[0].get("authname", "NA")

                    author_afid = author[0].get("afid", [])
                    if isinstance(author_afid, list) and len(author_afid) > 0:
                        author_afid = author_afid[0].get("$", "NA") 
                    else:
                        author_afid = "NA"
                else:
                    search_result["paper_author"] = "NA"
                    author_afid = "NA"

                affiliation = each_search.get("affiliation", [])

                search_result["affiliation_name"] = "NA"
                search_result["affiliation_city"] = "NA"
                search_result["affiliation_country"] = "NA"
                search_result["affiliation_id"] = "NA"

                if affiliation and isinstance(affiliation, list) and len(affiliation) > 0:
                    for each_affiliation in affiliation:
                        if each_affiliation.get("afid") == author_afid:
                            search_result["affiliation_name"] = each_affiliation.get("affilname", "NA")
                            search_result["affiliation_city"] = each_affiliation.get("affiliation-city", "NA")
                            search_result["affiliation_country"] = each_affiliation.get("affiliation-country", "NA")
                            search_result["affiliation_id"] =  each_affiliation.get("afid","NA")
                            break

                keyword_result.append(search_result)
            json.dump(keyword_result, f, ensure_ascii=False, indent=4)

    print(f"📂 Results saved to {filename_filtered}")

if __name__ == "__main__":
    for each_year_result in FILENAME_LST:
        year, FILENAME = each_year_result[0], each_year_result[1]
        keyword_lower = KEYWORDS.lower().replace(" ","")
        filename_filtered = f"data/raw_data/{keyword_lower}_{year}_paper.json"
        build_paper_json(FILENAME,filename_filtered)
