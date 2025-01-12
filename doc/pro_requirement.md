# Mapademic -- V0.1

## Global Academic Research Distribution and Career Trajectory Visualization Application

### Project Introduction
The global distribution of academic fields and the institutional mobility of researchers are critical topics in scientometrics and computational social science. However, existing tools often only display the current institutional affiliations of researchers and fail to capture their inter-institutional and inter-regional mobility throughout their careers. Moreover, tools that combine the global distribution of academic fields with research hotspots for visualization are still scarce.

This project aims to develop a keyword-based application that, through Google Scholar data crawling, analyzes the global academic distribution in a specific research field. It dynamically visualizes the geographical distribution of research hotspots and academic mobility by incorporating researchers' career trajectories and institutional changes.

---

### Project Objectives
1. **Keyword-driven Analysis**: Crawl Google Scholar data to obtain information on researchers and papers related to the user-input keyword.
2. **Global Distribution Visualization**: Build a dynamic map to display the regional distribution of research hotspots and institutional influence.
3. **Career Trajectory Tracking**: Analyze the institutional mobility in researchers' careers and present the changes using a timeline.
4. **Interactive Experience**: Provide a user-friendly interface to enable keyword search, data presentation, and result export functionalities.

---

### Project Workflow

#### Data Collection
- **Crawl Researcher and Paper Data**: Extract information related to the input keyword from Google Scholar.
  - **Keyword Search**: Simulate user input on Google Scholar (e.g., "climate change").
  - **Field Extraction**: Parse titles, publication years, citation counts, authors, institutions, and paper links by navigating to platforms such as Springer, Elsevier, or arXiv.
  - **Pagination Handling**: Retrieve data across multiple pages to ensure comprehensive coverage.

#### Career Trajectory Analysis
- **Institutional Tracking**: Extract institutional information across different time periods from the original paper pages.
  - **Timeline Construction**: Bind institutional data to publication years to create career trajectories.
- **Data Cleaning**:
  - De-duplicate and standardize institutional names (e.g., unify "MIT" and "Massachusetts Institute of Technology").

#### Geographic Data Parsing
- Parse institutional names into geographic coordinates to create global distribution data.
  - **Geocoding Services**: Use APIs like Google Maps or OpenCage Geocoder to convert institution names into latitude and longitude.
  - **Batch Processing**: Optimize efficiency by parsing multiple institution names simultaneously.
  - **Exception Handling**: Manually supplement or replace unmatched data.

#### Data Visualization
- Build dynamic maps and timelines to display global research distribution and career trajectories.
  - **Interactive Maps**: Use tools like Folium or Plotly to create interactive maps, with bubble sizes and colors denoting research hotspots or institutional influence.
  - **Timeline Visualization**: Show career trajectories and institutional changes dynamically.
  - **Enhanced Interactivity**: Include hover-over details and filtering by region or time.

#### Interactive Application
- Develop a user-friendly interface for keyword search, data display, and map interactions.
  - **Interface Design**: Use Streamlit for the frontend, offering input fields and search buttons.
  - **Feature Integration**: Seamlessly connect backend crawlers with visualization tools to generate results dynamically.
  - **Result Export**: Allow users to download analysis results (e.g., researcher information and institutional distribution data in CSV format).

---

### Timeline (10 Weeks)
- **Week 1-2**: Requirement analysis and technology selection; design and test crawler framework.
- **Week 3-4**: Implement data collection functionality, including keyword search and pagination crawling.
- **Week 5**: Complete institutional geolocation parsing and exception handling.
- **Week 6-7**: Build visualization functionalities for maps and timelines, ensuring smooth interactivity.
- **Week 8-9**: Develop the interactive interface and integrate module functionalities.
- **Week 10**: Conduct testing and optimization, finalize demo deployment, and document preparation.

---

### Future Iterations
1. **Expand Data Sources**: Integrate data from CrossRef, Semantic Scholar, or OpenAlex to complement Google Scholar.
2. **Collaboration Network Analysis**: Use co-author data to build academic collaboration networks and analyze inter-institutional collaboration patterns.
3. **Temporal Dynamics Analysis**: Trace the evolution of academic fields using keyword frequency over time; analyze changes in regional contributions.
4. **Enhanced Visualizations**: Mark thematic research distributions on maps; add bar charts, word clouds, and other supplementary visuals.
5. **Multi-user and Customization Features**: Enable simultaneous multi-user access and personalized analysis, allowing filtering by year, region, or institution.
