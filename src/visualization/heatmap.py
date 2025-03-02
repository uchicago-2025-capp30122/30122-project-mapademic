import json
import pandas as pd
import plotly.express as px
import pathlib
from mapadmic import KEY_WORDS, YEARS

def main_heatmap():
    """
    Generates a intertemporal heatmap from the given GeoJSON and CSV files.
    
    Parameters:
        geojson_file (str): Path to the GeoJSON file containing provinces' geographical data.
        csv_file (str): Path to the CSV file where each row represents a paper.
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object with the choropleth map.
    """
    # Load the GeoJSON file with provinces' boundaries
    geojsonpath = pathlib.Path("data") / "provinces_worldwide.json"
    with geojsonpath.open(mode="r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    # Read all CSV files containing paper information
    dfs = []
    for year in YEARS:
        csvpath = pathlib.Path("data") / "output_data" / f"{KEY_WORDS}_{year}_cleaned.csv"
        df = pd.read_csv(csvpath, encoding="utf-8")
        dfs.append(df)

    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Create an animated choropleth map using Plotly Express
    fig = px.choropleth_mapbox(
        merged_df,
        geojson=geojson_data,
        locations='state_name',           # DataFrame column with province names
        featureidkey='properties.name',   # Corresponding key in GeoJSON
        color='RDI',                      # Column to determine color intensity
        color_continuous_scale=[
            "#E9F8F6", "#C2DEDB", "#9CC4C1", "#75AAA6",
            "#4D908A", "#277670", "#005C55"
        ],  # Custom color scale
        mapbox_style="carto-positron",    # Base map style
        center={"lat": 20, "lon": 160},      # Map center coordinates
        zoom=0.8,                           # Zoom level
        opacity=0.7,                      # Map layer opacity
        labels={'paper_count': 'Number of Papers'},  # Label for the color bar
        animation_frame='year'            # Add time slider based on the "year" column
    )
    
    # Remove default margins for a cleaner layout
    fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    
    # Remove marker borders for a seamless appearance
    fig.update_traces(marker_line_width=0)
    
    return fig
