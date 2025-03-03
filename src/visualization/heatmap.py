import math
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from cache_utils import load_geojson, load_csv
from plotly.subplots import make_subplots
from concurrent.futures import ProcessPoolExecutor, as_completed
from cache_utils import load_geojson, load_csv


def main_heatmap(keywords, year, geojson_data=None):
    """
    Generates a choropleth map for a given year using pre-loaded data.

    Parameters:
        keywords (str): The research keywords used to filter the data.
        year (int): The reference year for the heatmap.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object with a choropleth map,
        including a title and customized hover information.
    """
    # Use pre-loaded GeoJSON if available
    if geojson_data is None:
        geojson_data = load_geojson()
    df = load_csv(keywords, year)
    
    # Create a choropleth map using Plotly Express
    fig = px.choropleth_mapbox(
        df,
        geojson=geojson_data,
        locations='state_name',               # Column with region names
        featureidkey='properties.name',       # Key in GeoJSON for matching regions
        color='CRDI',                         # Research density value
        color_continuous_scale=[
            "#E9F8F6", "#C2DEDB", "#9CC4C1", "#75AAA6",
            "#4D908A", "#277670", "#005C55"
        ],  # Custom color scale
        mapbox_style="carto-positron",        # Map style
        center={"lat": 20, "lon": 160},       # Map center coordinates
        zoom=0.8,                             # Zoom level
        opacity=0.7,                          # Map layer opacity
        labels={'CRDI': 'Research Density'},  # Label for the color bar
        animation_frame='year',               # Animation frame (not used in static figure)
        custom_data=['top3_institutions', 'top3_authors']  # Custom data for hover info
    )
    
    # Update layout: add a centered title
    fig.update_layout(
        title_text=f"{year} World Research Heat Distribution",
        title_x=0.5,
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )
    
    # Customize hover template to display additional information
    fig.update_traces(
        hovertemplate=(
            "<b>%{location}</b><br>"
            "Research Density: %{z}<br>"
            "Top3 Institutions: %{customdata[0]}<br>"
            "Top3 Cited Authors: %{customdata[1]}<extra></extra>"
        ),
        marker_line_width=0
    )
    
    return fig

def combined_heatmaps_with_timeline_and_arrows(keywords: str, years: list):
    """
    Combines individual heatmaps for each year in the 'years' list,
    arranged in a two-column grid (for larger maps) with maps staggered in rows.
    A timeline is added at the bottom, and dotted lines are drawn connecting
    each map's bottom center to its corresponding timeline node.
    
    Parameters:
        keywords (str): The research keywords.
        years (list of int): List of years to display.
        
    Returns:
        plotly.graph_objects.Figure: A combined figure with maps and a timeline.
    """
    n = len(years)
    num_cols = 2
    r_map = math.ceil(n / num_cols)  # Number of map rows
    timeline_height = 0.15           # Fraction of figure height for timeline
    map_row_height = (1 - timeline_height) / r_map
    
    # Build subplot specifications for mapbox and timeline
    specs = []
    for _ in range(r_map):
        specs.append([{'type': 'mapbox'}, {'type': 'mapbox'}])
    specs.append([{'type': 'xy', 'colspan': 2}, None])
    
    # Create the subplot figure with rows for maps and one for timeline
    fig = make_subplots(
        rows=r_map + 1, cols=num_cols,
        row_heights=[map_row_height] * r_map + [timeline_height],
        specs=specs,
        vertical_spacing=0.02
    )
    
    geojson_data = load_geojson()  # Pre-load GeoJSON once
    
    # Parallelize generation of heatmaps for each year
    heatmap_results = {}
    with ProcessPoolExecutor() as executor:
        future_to_year = {executor.submit(main_heatmap, keywords, year, geojson_data): year for year in years}
        for future in as_completed(future_to_year):
            yr = future_to_year[future]
            try:
                heatmap_results[yr] = future.result()
            except Exception as e:
                st.error(f"Error generating heatmap for {yr}: {e}")
    
    arrow_info = []
    # Process each generated heatmap and add it to the combined figure
    for idx, year in enumerate(years):
        row_idx = idx // num_cols + 1         # Map row index (1-indexed)
        col_idx = idx % num_cols + 1          # Column index
        
        single_fig = heatmap_results[year]
        # Add all traces from the single-year figure to the subplot
        for trace in single_fig.data:
            fig.add_trace(trace, row=row_idx, col=col_idx)
        
        # Update the current subplot's mapbox settings
        mapbox_key = "mapbox" if (row_idx - 1) * num_cols + col_idx == 1 else f"mapbox{(row_idx - 1) * num_cols + col_idx}"
        fig.layout[mapbox_key].update({
            "center": single_fig.layout['mapbox']['center'],
            "zoom": single_fig.layout['mapbox']['zoom'],
            "style": single_fig.layout['mapbox']['style']
        })
        
        # Calculate the center position of the current map cell (for connecting lines)
        cell_x0 = (col_idx - 1) / num_cols
        cell_x1 = col_idx / num_cols
        map_center_x = (cell_x0 + cell_x1) / 2
        map_bottom_y = 1 - row_idx * map_row_height
        
        # Determine timeline node position (evenly distributed along the width)
        timeline_node_x = (idx + 1) / (n + 1)
        timeline_node_y = timeline_height  # in paper coordinates
        
        arrow_info.append({
            "map_x": map_center_x,
            "map_y": map_bottom_y,
            "timeline_x": timeline_node_x,
            "year": year
        })
    
    # Add a timeline trace in the timeline subplot
    timeline_xs = [info["timeline_x"] for info in arrow_info]
    timeline_ys = [timeline_node_y] * len(arrow_info)
    timeline_trace = go.Scatter(
        x=timeline_xs,
        y=timeline_ys,
        mode='markers+lines+text',
        text=[str(info["year"]) for info in arrow_info],
        textposition='top center',
        marker=dict(size=10),
        line=dict(width=2)
    )
    fig.add_trace(timeline_trace, row=r_map + 1, col=1)
    
    # Add dotted lines connecting each map to its corresponding timeline node
    for info in arrow_info:
        fig.add_shape(
            type="line",
            xref="paper", yref="paper",
            x0=info["map_x"], y0=info["map_y"],
            x1=info["timeline_x"], y1=timeline_node_y,
            line=dict(color="black", width=1, dash="dot")
        )
    
    # Update the overall layout with a common title and margins
    fig.update_layout(
        title_text="World Research Heat Distribution Timeline",
        title_x=0.5,
        margin={"r": 20, "t": 50, "l": 20, "b": 20}
    )
    
    return fig
