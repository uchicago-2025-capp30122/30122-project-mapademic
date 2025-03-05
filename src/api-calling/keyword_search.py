import requests
import json
import time
import os

# Remember to use the command 'export API_KEY = "your API Key"' at the every beginning
try:
    API_KEY = os.environ["API_KEY"]
except KeyError:
    raise Exception(
        "Make sure that you have set the API Key environment variable as "
        "described in the README."
    )


"""Part I: Get the raw data from API"""
# Scopus API Configuration
SEARCH_URL = "https://api.elsevier.com/content/search/scopus"
HEADERS = {
    "Accept": "application/json",
    "X-ELS-APIKey": API_KEY
}

# RESULTS_JSON = "data/scopus_cursor_results_demo.json"
PAGE_SIZE = 25 # When set the parameter "view" as "COMPLETE", MAXIMUM be 25 !!!
               # when set the parameter "view" as "STANDARD", Maximum could be 200

def get_total_results(keywords, year):
    # Fetch total number of search results to check how many exist.
    # Season: for every search, api would response the total number of the searching results 
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
    MAX_RESULTS = 100 # Using for demo
    # MAX_RESULTS = total_available # Number of results to fetch

    while retrieved_count < min(MAX_RESULTS, total_available):
        params = {
            "query": f"TITLE-ABS-KEY({keywords}) AND PUBYEAR = {year}",
            "httpAccept": "application/json",
            "count": PAGE_SIZE,  # Max results per request
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

            # Debugging: Print the cursor
            print(f"Next Cursor: {next_cursor}")

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
        filename = f"data/raw_data/{keyword_lower}_{year}_paper.json"
        year_filenames.append((year, filename))
    return year_filenames

def save_results(results):
    # Save results to a JSON file
    with open(FILENAME, "w", encoding="utf-8") as f:
        keyword_result = []
        for each_search in results:
            # Important!! Using dict.get is necessary and safe, since there exsists missing part of the imfo          
            search_result = {
                "paper_title": each_search.get("dc:title","NA"),
                "paper_author": each_search.get("dc:creator","NA"),
                "publication": each_search.get("prism:publicationName","NA"),
                "citied_by": each_search.get("citedby-count","NA"),
                "cover_date" : each_search.get("prism:coverDate","NA"),
                "Abstract": each_search.get("dc:description","NA"),
                "DOI": each_search.get("prism:doi","NA")
            }

            affiliation = each_search.get("affiliation", [])
            if affiliation and isinstance(affiliation, list) and len(affiliation) > 0:
                search_result["affiliation_name"] = affiliation[0].get("affilname", "NA")
                search_result["affiliation_city"] = affiliation[0].get("affiliation-city", "NA")
                search_result["affiliation_country"] = affiliation[0].get("affiliation-country", "NA")
                search_result["affiliation_id"] = affiliation[0].get("afid","NA")
            else:
                search_result["affiliation_name"] = "NA"
                search_result["affiliation_city"] = "NA"
                search_result["affiliation_country"] = "NA"
                search_result["affiliation_id"] = "NA"

            keyword_result.append(search_result)

        json.dump(keyword_result, f, ensure_ascii=False, indent=4)

    print(f"Results saved to {FILENAME}")

# Demo Example
keywords = "machine learning and policy"
# year = 2023

FILENAME_LST = generate_filenames(keywords, 2020, 2024)
for each_year_result in FILENAME_LST:
    year, FILENAME = each_year_result[0], each_year_result[1]
    fetch_results_with_cursor(keywords, year)