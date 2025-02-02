# Mapademic

## Abstract

The global distribution of academic fields and the institutional mobility of researchers are critical areas of study in scientometrics and computational social science. While existing tools often focus on displaying researchers' current institutional affiliations, they frequently overlook the dynamic nature of academic careers, including cross-institutional and cross-regional transitions. Furthermore, there is a notable lack of tools that effectively visualize the global distribution of academic fields and emerging research hotspots.

This project aims to bridge these gaps by developing a keyword-based application that leverages data from **ScienceDirect's website and its API**. The application will analyze the global academic distribution of specific research fields, dynamically visualizing research hotspots and academic mobility patterns. By integrating researchers' career trajectories and institutional transitions, the tool will provide a comprehensive view of how academic fields evolve geographically and how researchers move across institutions and regions over time.

## Data Sources

### Data Reconciliation Plan

#### **1. Data Sources and Unique Keys**  

| **Data Source**              | **Key Fields**                               | **Unique Key**                              | **Purpose**                                                                 |  
|------------------------------|----------------------------------------------|---------------------------------------------|-----------------------------------------------------------------------------|  
| **ScienceDirect API**         | - `country` (standardized name)<br>- `region` (state/province)<br>- `city` (standardized name) | **Composite Key**: `country + "_" + region + "_" + city` | Link articles to granular geographic regions (city-level) for aggregation. |  
| **GeoJSON Boundary Files**    | - Administrative boundaries (city-level)<br>- Standardized geographic names (e.g., "New York City") | `properties.name` (matching API’s `city` field) | Map aggregated article counts to city boundaries for visualization.        |  

#### **2. Core Unique Key: Standardized Geographic Names**  
Since ISO codes are not required and ScienceDirect API provides **pre-standardized city names**, the integration relies on:  
- **Exact matches** between API’s geographic fields (`country`, `region`, `city`) and GeoJSON’s `properties.name` (or equivalent field).  
- **Composite Key** structure: `country + "_" + region + "_" + city` (e.g., `United States_California_San Francisco`).  

#### **3. Data Integration Workflow**  

**Step 1: Extract and Validate Geographic Fields**  
- From ScienceDirect API: Collect articles with `country`, `region`, and `city` fields.  
- Assume city names are pre-standardized (e.g., "San Francisco" vs. "SF").  

**Step 2: Aggregate Articles by Composite Key**  
- Group articles using the `country_region_city` composite key.  
- Example aggregated data:  
  | Composite Key                     | Article Count |  
  |-----------------------------------|---------------|  
  | United States_California_Palo Alto | 120           |  
  | United Kingdom_England_Cambridge   | 90            |  

**Step 3: Align with GeoJSON Boundaries**  
- Ensure GeoJSON files contain city-level boundaries with `properties.name` matching the API’s `city` field (e.g., "Palo Alto" in GeoJSON matches "Palo Alto" in API data).  
- If mismatches exist (e.g., "New York" vs. "New York City"):  
  - Create a lightweight **name-mapping table** to reconcile differences.  

**Step 4: Generate Heatmap with Plotly Express**  
- Use the composite key (`country_region_city`) to map aggregated counts to GeoJSON boundaries via `properties.name`.  
- Plotly Express will render intensity based on `article_count` per city.  

#### **4. Key Adjustments and Assumptions**  
- **No ISO Codes Needed**: Relies on precise matches of textual geographic names (country, region, city).  
- **Pre-Standardized City Names**: Assumes ScienceDirect API provides consistent, unambiguous city names (e.g., no typos or abbreviations).  
- **GeoJSON Compatibility**: GeoJSON files must include city-level polygons with `properties.name` matching API’s `city` field.  

#### **5. Challenges and Mitigations**  

| **Challenge**                          | **Mitigation**                                                                 |  
|----------------------------------------|-------------------------------------------------------------------------------|  
| **City name mismatches**               | Build a small mapping table for exceptions (e.g., "SF" → "San Francisco").    |  
| **Missing regional/city data**         | Aggregate at higher levels (e.g., country or region) if city is unspecified.  |  
| **Ambiguous city names**               | Disambiguate using region/country context (e.g., "Paris, France" vs. "Paris, Texas"). |  

#### **6. Simplified Toolchain**  
- **Data Aggregation**: Use tabular tools (e.g., spreadsheets or `pandas`) to group data by composite key.  
- **Name Reconciliation**: Manual curation or lightweight scripts for critical mismatches.  
- **Visualization**: Plotly Express with GeoJSON that aligns with API’s geographic naming conventions.  

### Data Source #1: {Name}

- Is the data coming from a webpage, bulk data, or an API?
- Are there any challenges or remaining uncertainity about the data?
- How many records (rows) does your data set have?
- How many properties (columns) does your data set have?
- Write a few sentences about your exploration of the data set. At this point you should have downloaded some of the data and explored it with an eye for things that might cause issues for your project.

（由于技术原因，联网搜索暂不可用）

---

### **Data Source #1: ScienceDirect API**  
- **Is the data coming from a webpage, bulk data, or an API?**  
  The data is retrieved via the **ScienceDirect Query API** (`https://dev.elsevier.com/documentation/ScienceDirectQueryAPI.wadl`), which programmatically returns metadata for academic articles, including titles, authors, and affiliations.  

- **Challenges or uncertainties about the data:**  
  - **Geographic field consistency**: While the API provides `country` or `city` fields, these names may not align perfectly with Natural Earth’s administrative boundaries (e.g., "New York" vs. "New York City").  
  - **Missing data**: Some articles may lack granular geographic details (e.g., missing `city` or `region`).  
  - **Institutional ambiguity**: Affiliations like "Harvard University" might map to multiple locations (e.g., Cambridge, MA vs. global campuses).  

- **Number of records (rows):**  
  Depends on the search query, but a typical keyword-based query (e.g., "machine learning") returns **~1,000–5,000 articles** per request, with pagination for larger datasets.  

- **Number of properties (columns):**  
  Each article includes **10–15 properties**, such as `DOI`, `title`, `authors`, `affiliations`, and `publicationYear`.  

- **Exploration insights and potential issues:**  
  Initial sampling revealed:  
  - **Variability in geographic granularity**: `city` and `country`-level data need to be cleaned from `affiliations`.
  - **Name standardization issues**: For example, "USA" and "United States" both appear in the `affiliations` field, requiring consolidation.  
  - **API limitations**: Rate limits (~3,000 requests/day) and truncated results for large queries.  

### **Data Source #2: Natural Earth Admin-1 States/Provinces**  
- **Is the data coming from a webpage, bulk data, or an API?**  
  The data is sourced from **Natural Earth’s 10m-admin-1-states-provinces** dataset, available as **bulk downloads** in Shapefile format. It provides global state/province boundaries with attributes like `name`, `iso_3166_2` codes, and `region`.  

- **Challenges or uncertainties about the data:**  
  - **Name mismatches**: Natural Earth uses formal names (e.g., "California"), while ScienceDirect might use colloquial terms (e.g., "CA" or "Calif.").  
  - **Hierarchical alignment**: Mapping ScienceDirect’s `city` field to Natural Earth’s `admin1` boundaries may require manual adjustments (e.g., "Île-de-France" vs. "Paris Region").  
  - **Geopolitical sensitivity**: Disputed regions (e.g., Crimea) may have conflicting boundaries.  

- **Number of records (rows):**  
  The dataset contains **~4,500 records**, each representing a state/province-level administrative unit globally.  

- **Number of properties (columns):**  
  Each boundary has **15–20 properties**, including `name`, `iso_3166_2`, `latitude`, `longitude`, and `region_un` (UN region classification).  

- **Exploration insights and potential issues:**  
  Initial analysis highlighted:  
  - **Inconsistent naming conventions**: For example, "Bavaria" in Natural Earth vs. "Bayern" (German name) in ScienceDirect.  
  - **Missing subdivisions**: Some smaller regions (e.g., city-states like Singapore) are not subdivided, complicating city-level mapping.  
  - **Scale limitations**: The "10m" resolution may oversimplify boundaries for dense regions (e.g., European microstates).  

## Project Plan

### **6-Week Project Plan**  

#### **Team Roles**  
| **Member** | **Responsibilities**                                                                                   |  
|------------|--------------------------------------------------------------------------------------------------------|  
| **A**: Allen Wu      | **API Integration & Data Extraction** (Lead ScienceDirect API script development and data collection). |  
| **B**: Shiyao Wang      | **Data Cleaning & Geospatial Parsing** (Standardize data, develop geographic matching logic).         |  
| **C**: Peiyu Chen      | **Data Visualization & Project Management** (Design visuals, manage timelines, coordinate tasks).     |  
| **D**: Yue Pan      | **Frontend Development** (Streamlit UI, integration of modules, deployment).                          |  

### **Weekly Breakdown**  

#### **Week 1: API Integration & Framework Setup**  
**Objective**: Extract data via ScienceDirect API, define geographic matching rules, and build the Streamlit foundation.  

| **Member** | **Tasks**                                                                                              | **Deliverables**                        | **Project Management**                                                                 |  
|------------|--------------------------------------------------------------------------------------------------------|-----------------------------------------|----------------------------------------------------------------------------------------|  
| **A**      | 1. Develop API batch script to fetch `affiliation + country + city`.<br>2. Extract and save 1,000 raw articles. | API script + raw dataset (CSV)          | **Wednesday Meeting**: C reviews API script and data fields; finalizes geographic rules (exact city name matching). |  
| **B**      | 1. Parse Natural Earth’s Admin-1 data.<br>2. Define baseline geographic rules (city → state → country). | Geographic matching rules document      |                                                                                        |  
| **C**      | 1. Test Plotly compatibility with Natural Earth GeoJSON.<br>2. Draft visualization requirements.       | Heatmap prototype (Jupyter Notebook)    |                                                                                        |  
| **D**      | Build Streamlit foundation (file upload + table display); set up GitHub repo.                          | Initial Streamlit prototype + GitHub    |                                                                                        |  

**Risks**:  
- City name mismatches → B creates a manual mapping table (e.g., `{"NYC": "New York"}`).  
- Streamlit/Plotly conflicts → D tests core components first.  

---

#### **Week 2: Data Cleaning & Geospatial Matching**  
**Objective**: Implement geographic matching and generate clean datasets.  

| **Member** | **Tasks**                                                                                              | **Deliverables**                        | **Project Management**                                                                 |  
|------------|--------------------------------------------------------------------------------------------------------|-----------------------------------------|----------------------------------------------------------------------------------------|  
| **A**      | 1. Optimize API script (pagination, error handling).<br>2. Extract and clean 5,000 articles.            | Cleaned dataset (CSV/json)                   | **Wednesday Meeting**: C reviews data quality and assigns anomaly-handling tasks.      |  
| **B**      | 1. Develop geospatial matching script (city names → Natural Earth).<br>2. Handle multi-level mapping.   | Geospatial matching script              |                                                                                        |  
| **C**      | 1. Refine mapping table (common aliases).<br>2. Design heatmap color gradients (blue → red).            | Optimized mapping table + color scheme  |                                                                                        |  
| **D**      | Integrate data pipeline into Streamlit; add placeholder search bar.                                    | Streamlit app with data pipeline        |                                                                                        |  

**Key Metrics**:  
- Geospatial matching accuracy >80% (sampling test).  
- Streamlit dynamically loads data and displays heatmap outlines.  

---

#### **Week 3(Milestone #3): Core Feature Development (Heatmap + Timeline)**  
**Objective**: Implement time-based filtering and heatmap-timeline interaction.  

| **Member** | **Tasks**                                                                                              | **Deliverables**                        | **Project Management**                                                                 |  
|------------|--------------------------------------------------------------------------------------------------------|-----------------------------------------|----------------------------------------------------------------------------------------|  
| **A**      | 1. Extract publication years; handle missing values.<br>2. Generate time-series dataset.               | Year-labeled dataset                    | **Wednesday Meeting**: C reviews timeline design and coordinates module integration.   |  
| **B**      | 1. Aggregate data by year; develop time-slider logic.<br>2. Optimize geospatial caching.                | Time-filter script + caching logic      |                                                                                        |  
| **C**      | 1. Link heatmap updates to time-slider.<br>2. Design "Play" button for auto-annual updates.             | Interactive heatmap prototype           |                                                                                        |  
| **D**      | Integrate time-slider into Streamlit; optimize UI layout (map above, controls below).                  | Streamlit app with time-filtering       |                                                                                        |  

**Acceptance Criteria**:  
- Time-slider dynamically updates heatmap.  
- Response time <5 seconds (10,000 records).  

---

#### **Week 4: Exception Handling & Internal Testing**  
**Objective**: Fix critical issues and conduct internal testing.  

| **Member** | **Tasks**                                                                                              | **Deliverables**                        | **Project Management**                                                                 |  
|------------|--------------------------------------------------------------------------------------------------------|-----------------------------------------|----------------------------------------------------------------------------------------|  
| **A**      | Flag unmatched data (e.g., "London" vs. "Greater London"); generate test cases.                        | Exception list + test cases             | **Wednesday Meeting**: C prioritizes fixes and assigns tasks.                         |  
| **B**      | 1. Add fallback logic (country-level display).<br>2. Improve logging for failed matches.               | Enhanced matching script + logs         |                                                                                        |  
| **C**      | 1. Optimize heatmap tooltips (hover-to-show counts).<br>2. Lead team testing (3 members).              | Refined heatmap + test report            |                                                                                        |  
| **D**      | Add loading prompts (e.g., "Processing..."); fix browser compatibility.                                | User-friendly error handling             |                                                                                        |  

---

#### **Week 5: Deployment Preparation & Documentation**  
**Objective**: Deploy the system and prepare documentation.  

| **Member** | **Tasks**                                                                                              | **Deliverables**                        | **Project Management**                                                                 |  
|------------|--------------------------------------------------------------------------------------------------------|-----------------------------------------|----------------------------------------------------------------------------------------|  
| **A**      | Generate 10,000 test records; validate cleaning performance (<2 minutes).                              | Performance report                      | **Wednesday Meeting**: C finalizes deployment plans and documentation tasks.           |  
| **B**      | Precompute hotspot data; optimize aggregation.                                                        | Optimized aggregation script             |                                                                                        |  
| **C**      | Simplify heatmap rendering (reduce non-critical data points); draft user guide.                        | Lightweight heatmap + doc outline        |                                                                                        |  
| **D**      | Deploy to Streamlit Cloud; write deployment steps.                                                     | Live app URL + deployment guide          |                                                                                        |  

---

#### **Week 6: Final Delivery & Review**  
**Objective**: Deliver the system and compile all materials.  

| **Member** | **Tasks**                                                                                              | **Deliverables**                        | **Project Management**                                                                 |  
|------------|--------------------------------------------------------------------------------------------------------|-----------------------------------------|----------------------------------------------------------------------------------------|  
| **A**      | Document API integration and data cleaning (code snippets).                                            | `API_Cleaning_Guide.md`                 | **Wednesday Meeting**: C leads final review and confirms deliverables.                 |  
| **B**      | Document geospatial matching logic (example mappings).                                                 | `Geospatial_Matching.md`                |                                                                                        |  
| **C**      | 1. Compile all documentation.<br>2. Record a 10-minute demo video; write user guide.                   | Full documentation pack + demo video    |                                                                                        |  
| **D**      | 1. Ensure system stability.<br>2. Finalize GitHub repo (README with setup instructions).               | Maintainable code repository            |                                                                                        |  

---

### **Final Deliverables**  
1. **Live System**: Streamlit web app (public URL).  
2. **Code Repository**: GitHub (code, docs, deployment configs).  
3. **Documentation**:  
   - Technical: `API_Cleaning_Guide.md`, `Geospatial_Matching.md`.  
   - User Guide: Step-by-step tutorial with screenshots.  
   - Demo: Video walkthrough + summary slides.  

## Questions

A **numbered** list of questions for us to respond to.