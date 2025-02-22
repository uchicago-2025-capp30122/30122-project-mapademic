import json
import pandas as pd
import plotly.express as px
import streamlit as st
import pathlib

def generate_basic_choropleth_map():
    """
    Generates a choropleth map from the given GeoJSON and CSV files.
    
    Parameters:
        geojson_file (str): Path to the GeoJSON file containing provinces' geographical data.
        csv_file (str): Path to the CSV file where each row represents a paper.
        
    Returns:
        plotly.graph_objects.Figure: A Plotly figure object with the choropleth map.
    """
    # Load the GeoJSON file with provinces' boundaries
    geojsonpath = pathlib.Path("data") / "provinces_worldwide.json"
    with geojsonpath.open(mode ="r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    # Read the CSV file containing paper information
    csvpath = pathlib.Path("src") / "cleaning" / "output_geo_data.csv"
    df = pd.read_csv(csvpath, encoding="utf-8")
    
    # Group the data by province (state_name) and count the number of papers for each province
    df_grouped = df.groupby('state_name').size().reset_index(name='paper_count')
    
    # Create a choropleth map using Plotly Express
    fig = px.choropleth_mapbox(
        df_grouped,
        geojson=geojson_data,
        locations='state_name',           # Column in DataFrame representing province names
        featureidkey='properties.name',   # Corresponding key in GeoJSON (must match DataFrame names)
        color='paper_count',              # Column to determine the color intensity (number of papers)
        color_continuous_scale=[
            "#E9F8F6", "#C2DEDB", "#9CC4C1", "#75AAA6",
            "#4D908A", "#277670", "#005C55"
        ],  # Custom color scale
        mapbox_style="carto-positron",    # Base map style
        center={"lat": 20, "lon": 0},      # Map center coordinates
        zoom=1,                           # Zoom level
        opacity=0.7,                      # Map layer opacity
        labels={'paper_count': 'Number of Papers'}  # Label for the color bar
    )
    
    # Remove default margins for a cleaner layout
    fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    
    # Remove marker borders for a seamless appearance
    fig.update_traces(marker_line_width=0)
    
    return fig
