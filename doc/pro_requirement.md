# Mapademic  
**Global Academic Research Distribution and Career Trajectory Visualization Application**

## Project Overview

The global distribution of academic fields and the institutional mobility of researchers are key topics in scientometrics and computational social science. However, existing tools often only display researchers' current institutional information, failing to capture their cross-institutional and cross-regional career trajectories. Additionally, tools that visualize the global distribution of academic fields and research hotspots remain scarce.

This project aims to develop a keyword-based application that leverages data from Google Scholar to analyze the global academic distribution of a research field. It dynamically visualizes research hotspots and academic mobility by integrating researchers' career trajectories and institutional transitions.

## Project Objectives

- **Keyword-Driven Analysis:** Allow users to input keywords, crawl Google Scholar data, and obtain information about researchers and papers related to the keywords.
- **Global Distribution Visualization:** Build a dynamic map to display the regional distribution of research hotspots and institutional influence.
- **Career Trajectory Tracking:** Analyze researchers' institutional mobility over their careers, presenting their career transitions on a timeline.
- **Interactive Experience:** Provide a user-friendly interface for keyword searches, data visualization, and result export functionality.

## Requirements Analysis

### Functional Requirements

#### Data Collection Module
- **Data Crawling:** Scrape information about researchers and papers related to keywords from Google Scholar.
  - **Keyword Search:** Simulate user input of keywords (e.g., "climate change") in Google Scholar.
  - **Field Extraction:** Navigate to paper pages on platforms like Springer, Elsevier, or arXiv to extract authorship and institutional data. Collect details such as paper titles, publication years, citation counts, authors, their current affiliations, and paper links.
  - **Pagination Handling:** Retrieve multi-page search results to ensure comprehensive data coverage.

#### Data Cleaning and Parsing Module
- **Career Trajectory Analysis:** Extract researchers' institutional affiliations over different periods from original paper pages.
  - **Timeline Construction:** Bind institutional information to publication years to create career trajectories.
  - **Data Cleaning:** Deduplicate and standardize institutional names to address variations (e.g., unify "MIT" and "Massachusetts Institute of Technology").
- **Geolocation Parsing:** Convert institutional names into latitude and longitude for global distribution data.
  - **Geocoding Services:** Use Google Maps API or OpenCage Geocoder to map institutional names to coordinates.
  - **Batch Processing:** Resolve multiple names efficiently.
  - **Error Handling:** Manually supplement or replace failed geocoding results.

#### Data Visualization Module
- **Dynamic Map and Timeline Construction:** Visualize global research distribution and career trajectories.
  - **Dynamic Maps:** Use tools like Folium or Plotly to create interactive maps with bubbles indicating research hotspots or institutional influence.
  - **Timelines:** Dynamically display career trajectories and institutional changes over time.
  - **Interface Enhancements:** Add features like hover-to-display details and filters for regions or time periods.

#### User Interaction Module
- **Interface Development:** Create a user-friendly interface for keyword search, data visualization, and interactive maps.
  - **Design:** Build the interface using Streamlit, with keyword input fields and search buttons.
  - **Feature Integration:** Seamlessly combine backend crawlers with maps and timelines for dynamic results generation.
  - **Result Export:** Enable users to download analysis results (e.g., CSV files with researcher and institutional distribution data).

### Non-Functional Requirements
- **Performance:** Average response time should not exceed 2 seconds and support processing over 1,000 data entries.
- **Usability:** Provide a simple, intuitive user interface and support short-term keyword translations into multiple UN official languages.
- **Compatibility:** Undefined.
- **Security:** Ensure compliance with privacy regulations like GDPR and implement robust data security and privacy protections.

## System Architecture

### Module Division
1. **Data Collection Module:** Scrape keyword-related information from Google Scholar and navigate to original pages for detailed data.
2. **Data Processing Module:** Clean and standardize data, complete geolocation parsing.
3. **Data Storage Module:** Store data using MongoDB or PostgreSQL.
4. **Visualization Module:** Display academic distribution and career trajectories using dynamic maps and timelines.
5. **Frontend Interaction Module:** Provide a user interface with data filtering functionality.

## Timeline (10 Weeks)
1. **Weeks 1-2:** Conduct requirements analysis and technology selection; design the crawler framework.
2. **Weeks 3-4:** Build and test the crawler framework; implement data collection features, including keyword search and pagination.
3. **Week 5:** Complete institutional geolocation parsing and error handling.
4. **Weeks 6-7:** Build visualization features for maps and timelines, ensuring smooth interactions.
5. **Weeks 8-9:** Develop an interactive interface and integrate module functionalities.
6. **Week 10:** Test, optimize, and complete demo deployment and documentation.

## Future Iterations and Goals
- **Expand Data Sources:** Integrate data from CrossRef, Semantic Scholar, or OpenAlex to complement Google Scholar.
- **Collaboration Network Analysis:** Use co-authorship data to construct academic collaboration networks and analyze institutional cooperation patterns.
- **Temporal Dynamics Analysis:** Track the development of academic fields over time using keyword frequency trends and analyze how specific regions' contributions evolve.
- **Enhanced Visualizations:** Add annotations for specific topics on maps and include supplementary visualizations like bar charts and word clouds.
- **Multi-User and Custom Features:** Allow multiple users to use the application simultaneously and save personalized analyses. Enable users to target specific years, regions, or institutions for analysis.
