import math
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from .cache_utils import load_geojson, load_csv
from plotly.subplots import make_subplots
from concurrent.futures import ProcessPoolExecutor, as_completed

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
    df["match_id"] = df["country"].astype(str) + "_" + df["state_name"].astype(str)
    
    # Create a choropleth map using Plotly Express
    fig = px.choropleth_map(
        df,
        geojson=geojson_data,
        locations='match_id',               # Column with region names
        featureidkey='properties.match_id',   # Key in GeoJSON for matching regions
        color='CRDI',                         # Research density value
        color_continuous_scale=[
            "#E9F8F6", "#C2DEDB", "#9CC4C1", "#75AAA6",
            "#4D908A", "#277670", "#005C55"
        ],  # Custom color scale
        map_style="carto-positron",           # Map style
        center={"lat": 20, "lon": 160},       # Map center coordinates
        zoom=0.8,                             # Zoom level
        opacity=0.7,                          # Map layer opacity
        labels={'CRDI': 'Research Density'},  # Label for the color bar
        animation_frame='year',               # Animation frame (not used in static figure)
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
        ),
        marker_line_width=0
    )
    
    return fig


def create_subplot_figure(n: int, num_cols: int = 2, timeline_height: float = 0.15):
    """
    Create the overall figure with map subplots and a timeline subplot.

    Parameters:
        n (int): Total number of years.
        num_cols (int): Number of maps per row (default is 2).
        timeline_height (float): Proportion of the figure's height allocated for the timeline.

    Returns:
        tuple: (fig, r_map, map_row_height)
            fig: The subplot figure object.
            r_map: Number of map rows.
            map_row_height: Height proportion for each map row.
    """
    r_map = math.ceil(n / num_cols)
    map_row_height = (1 - timeline_height) / r_map

    # Build subplot specs: first r_map rows for maps, last row for the timeline
    specs = [[{'type': 'map'} for _ in range(num_cols)] for _ in range(r_map)]
    specs.append([{'type': 'xy', 'colspan': num_cols}, None])

    fig = make_subplots(
        rows=r_map + 1, cols=num_cols,
        row_heights=[map_row_height] * r_map + [timeline_height],
        specs=specs,
        vertical_spacing=0.02
    )
    return fig, r_map, map_row_height


def generate_heatmaps(keywords: str, years: list, geojson_data):
    """
    Generate heatmaps for each year in parallel.

    Parameters:
        keywords (str): Research keywords.
        years (list): List of years.
        geojson_data: Preloaded GeoJSON data.

    Returns:
        dict: Mapping of year to its corresponding heatmap figure.
    """
    heatmap_results = {}
    with ProcessPoolExecutor() as executor:
        future_to_year = {executor.submit(main_heatmap, keywords, year, geojson_data): year for year in years}
        for future in as_completed(future_to_year):
            year = future_to_year[future]
            try:
                heatmap_results[year] = future.result()
            except Exception as e:
                st.error(f"Error generating heatmap for {year}: {e}")
    return heatmap_results


def add_heatmaps_to_figure(fig, heatmap_results: dict, years: list, num_cols: int, map_row_height: float, timeline_height: float, r_map: int):
    """
    Add each year's heatmap to the combined figure and calculate positions for connecting lines.

    Parameters:
        fig: The subplot figure object.
        heatmap_results (dict): Mapping of year to heatmap figure.
        years (list): List of years.
        num_cols (int): Number of maps per row.
        map_row_height (float): Height proportion for each map row.
        timeline_height (float): Proportion of the figure's height allocated for the timeline.
        r_map (int): Number of map rows.

    Returns:
        list: A list of dictionaries containing each map's center position and its corresponding timeline node position.
    """
    arrow_info = []
    n = len(years)
    for idx, year in enumerate(years):
        row_idx = idx // num_cols + 1         # Map row index (1-indexed)
        col_idx = idx % num_cols + 1          # Column index

        single_fig = heatmap_results[year]
        # Add all traces from the single-year figure to the appropriate subplot
        for trace in single_fig.data:
            fig.add_trace(trace, row=row_idx, col=col_idx)

        # Update the current subplot's mapbox settings
        map_key = "map" if (row_idx - 1) * num_cols + col_idx == 1 else f"map{(row_idx - 1) * num_cols + col_idx}"
        fig.layout[map_key].update({
            "center": single_fig.layout['map']['center'],
            "zoom": single_fig.layout['map']['zoom'],
            "style": single_fig.layout['map']['style']
        })

        # Calculate the center position of the current map cell (for connecting lines)
        cell_x0 = (col_idx - 1) / num_cols
        cell_x1 = col_idx / num_cols
        map_center_x = (cell_x0 + cell_x1) / 2
        map_bottom_y = 1 - row_idx * map_row_height

        # Calculate the timeline node position (evenly distributed along the width)
        timeline_node_x = (idx + 1) / (n + 1)

        arrow_info.append({
            "map_x": map_center_x,
            "map_y": map_bottom_y,
            "timeline_x": timeline_node_x,
            "year": year
        })
    return arrow_info


def add_timeline_and_arrows(fig, arrow_info: list, timeline_height: float, r_map: int):
    """
    Add the timeline subplot and dotted lines connecting each map to its corresponding timeline node.

    Parameters:
        fig: The subplot figure object.
        arrow_info (list): List of dictionaries containing map center and timeline node positions.
        timeline_height (float): Proportion of the figure's height allocated for the timeline.
        r_map (int): Number of map rows.
    """
    timeline_node_y = timeline_height  # Y-coordinate in paper reference
    timeline_xs = [info["timeline_x"] for info in arrow_info]
    timeline_ys = [timeline_node_y] * len(arrow_info)

    # Add the timeline trace
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

    # Add dotted lines connecting each map to the corresponding timeline node
    for info in arrow_info:
        fig.add_shape(
            type="line",
            xref="paper", yref="paper",
            x0=info["map_x"], y0=info["map_y"],
            x1=info["timeline_x"], y1=timeline_node_y,
            line=dict(color="black", width=1, dash="dot")
        )


def combined_heatmaps_with_timeline_and_arrows(keywords: str, years: list):
    """
    Combine heatmaps for different years arranged in a two-column grid and add a timeline with connecting dotted lines.

    Parameters:
        keywords (str): Research keywords.
        years (list): List of years.

    Returns:
        plotly.graph_objects.Figure: The complete combined figure.
    """
    n = len(years)
    num_cols = 2
    timeline_height = 0.15

    # Create subplot layout and get layout parameters
    fig, r_map, map_row_height = create_subplot_figure(n, num_cols, timeline_height)

    geojson_data = load_geojson()  # Assume load_geojson is defined elsewhere

    # Generate heatmaps in parallel for each year
    heatmap_results = generate_heatmaps(keywords, years, geojson_data)

    # Add heatmaps to the subplots and calculate arrow positions for connecting lines
    arrow_info = add_heatmaps_to_figure(fig, heatmap_results, years, num_cols, map_row_height, timeline_height, r_map)

    # Add timeline and connecting dotted lines
    add_timeline_and_arrows(fig, arrow_info, timeline_height, r_map)

    # Update overall layout with a title and margins
    fig.update_layout(
        title_text="World Research Heat Distribution Timeline",
        title_x=0.5,
        margin={"r": 20, "t": 50, "l": 20, "b": 20}
    )

    return fig
