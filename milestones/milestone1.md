# Mapademic

## Members

- Allen Wu <songting@uchicago.edu>
- Peiyu Chen <peiyuch@uchicago.edu>
- Shiyao Wang <shiyao611@uchicago.edu>
- Yue Pan <pany17@uchicago.edu>

## Abstract

The global distribution of academic fields and the institutional mobility of researchers are critical areas of study in scientometrics and computational social science. While existing tools often focus on displaying researchers' current institutional affiliations, they frequently overlook the dynamic nature of academic careers, including cross-institutional and cross-regional transitions. Furthermore, there is a notable lack of tools that effectively visualize the global distribution of academic fields and emerging research hotspots.

This project aims to bridge these gaps by developing a keyword-based application that leverages data from **ScienceDirect's API**. The application will analyze the global academic distribution of specific research fields, dynamically visualizing research hotspots and academic mobility patterns. By integrating researchers' career trajectories and institutional transitions, the tool will provide a comprehensive view of how academic fields evolve geographically and how researchers move across institutions and regions over time.

## Preliminary Data Sources

For each source please add a section with the following:

### Data Source #1: Google Scholar

- **Description:**  
  We will scrape the data from Google Scholar. Typically, for a given word, we will use it as a keyword and find the top papers related to it. Our data involves the titles, authors, institutions, date of publication, keywords, abstracts, etc.  
- **Data Source Type:** Web page data  
  **URL:** [Google Scholar](https://scholar.google.com/)  
- **Additional Details:**  
  Going further, we'll link directly to the original URL via Google Scholar when necessary, and read more detailed author and paper information from that page.

#### Challenges
- **HTML Structure Changes:** Google may update its webpage structure frequently, leading to a break of the scraper. We need to find ways to handle changes in HTML structure and fit in this flexible change.  
- **Pagination and Blocking:** Google Scholar shows search results across multiple pages and sometimes it may block you from scraping. We need to create a loop to scrape data from each page and add delays between requests to avoid getting blocked.

### Data Source #2: NCES

- **Description:**  
  We will use the bulk data from the National Center for Education Statistics (NCES) of the U.S. Department of Education. This dataset includes the geographic coordinates (latitude and longitude) for nearly all research locations of higher education institutions across the US.  
- **Data Source Type:** Bulk data  
  **URL:** [NCES](https://nces.ed.gov/)

### Data Source #3: Google Maps Geocoding API

- **Description:**  
  We will use the Google Maps Geocoding API to obtain geographic coordinates (latitude and longitude) for academic institutions based on their names. The API provides an efficient and reliable method to convert institution names into precise location data.  
- **Data Source Type:** API  
  **URL:** [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding)

#### Challenges
- **API Quotas and Costs:** Google Maps API imposes usage limits and charges for requests beyond the free tier. Careful monitoring of API usage and optimization of requests are necessary to stay within budget.  
- **Ambiguous Institution Names:** Some academic institutions may have similar or identical names, leading to inaccurate geocoding results. It is essential to include additional details like city or state to improve precision.

## Preliminary Project Plan

### Data Collection Module
- **Data Crawling:** Scrape information about researchers and papers related to keywords from Google Scholar.
    - **Keyword Search:** Simulate user input of keywords (e.g., "climate change") in Google Scholar.
    - **Field Extraction:** Navigate to paper pages on platforms like Springer, Elsevier, or arXiv to extract authorship and institutional data. Collect details such as paper titles, publication years, citation counts, authors, their current affiliations, and paper links.
    - **Pagination Handling:** Retrieve multi-page search results to ensure comprehensive data coverage.

### Data Cleaning and Parsing Module
- **Career Trajectory Analysis:** Extract researchers' institutional affiliations over different periods from original paper pages.
    - **Timeline Construction:** Bind institutional information to publication years to create career trajectories.
    - **Data Cleaning:** Deduplicate and standardize institutional names to address variations (e.g., unify "MIT" and "Massachusetts Institute of Technology").
- **Geolocation Parsing:** Convert institutional names into latitude and longitude for global distribution data.
    - **Geocoding Services:** Use Google Maps API or OpenCage Geocoder to map institutional names to coordinates.
    - **Batch Processing:** Resolve multiple names efficiently.
    - **Error Handling:** Manually supplement or replace failed geocoding results.

### Data Visualization Module
- **Dynamic Map and Timeline Construction:** Visualize global research distribution and career trajectories.
    - **Dynamic Maps:** Use tools like Folium or Plotly to create interactive maps with bubbles indicating research hotspots or institutional influence.
    - **Timelines:** Dynamically display career trajectories and institutional changes over time.
    - **Interface Enhancements:** Add features like hover-to-display details and filters for regions or time periods.

### User Interaction Module
- **Interface Development:** Create a user-friendly interface for keyword search, data visualization, and interactive maps.
    - **Design:** Build the interface using Streamlit, with keyword input fields and search buttons.
    - **Feature Integration:** Seamlessly combine backend crawlers with maps and timelines for dynamic results generation.
    - **Result Export:** Enable users to download analysis results (e.g., CSV files with researcher and institutional distribution data).

### Non-Functional Requirements
- **Performance:** Average response time should not exceed 2 seconds and support processing over 1,000 data entries.  
- **Usability:** Provide a simple, intuitive user interface and support short-term keyword translations into multiple UN official languages.  
- **Compatibility:** Undefined.  
- **Security:** Ensure compliance with privacy regulations like GDPR and implement robust data security and privacy protections.

## Questions

- The same research unit may be recorded by different people or journals using different abbreviations or full names. The fuzzy matching method of name-see-relationships is something we currently lack expertise in.  
- Some authors may sign the names of secondary sub-units of the primary institution. How can we categorize these secondary sub-units into the primary institution? Would we need to line up and organize a new database ourselves?
