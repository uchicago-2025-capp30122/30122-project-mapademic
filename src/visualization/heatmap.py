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
    
    # Create a choropleth map using Plotly Express
    fig = px.choropleth_map(
        df,
        geojson=geojson_data,
        locations='state_name',                     # Column with region names
        featureidkey='properties.name',             # Key in GeoJSON for matching regions
        color='crdi_index',                         # Research density value
        color_continuous_scale=[
            "#E9F8F6", "#C2DEDB", "#9CC4C1", "#75AAA6",
            "#4D908A", "#277670", "#005C55"
        ],                                          # Custom color scale
        map_style="carto-positron",                 # Map style
        center={"lat": 20, "lon": 160},             # Map center coordinates
        zoom=0.8,                                   # Zoom level
        opacity=0.7,                                # Map layer opacity
        labels={'crdi_index': 'Research Density'},  # Label for the color bar
    )
    
    # Update layout: add a centered title
    fig.update_layout(
        title_text=f"{year} World Research Distribution",
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


def create_map_and_left_timeline_figure(n: int):
    """
    Creates a subplot figure with two columns:
      - The left column is reserved for a vertical timeline that spans all n rows.
      - The right column contains the maps, with one map per row.
      
    Parameters:
        n (int): Number of rows (i.e., number of years/maps to display).

    Returns:
        plotly.graph_objects.Figure: A subplot figure configured with n rows and 2 columns,
        where the left column is for the timeline and the right column for the maps.
    """
    # In the first row, the left subplot is set to span all n rows using "rowspan".
    specs = [[{'type': 'xy', 'rowspan': n}, {'type': 'map'}]]
    # For the remaining n-1 rows, leave the left cell empty and continue to create map subplots on the right.
    for _ in range(n - 1):
        specs.append([None, {'type': 'map'}])
    fig = make_subplots(
        rows=n, cols=2,
        specs=specs,
        row_heights=[1/n] * n,
        column_widths=[0.17, 0.65],
        horizontal_spacing=0.02,
        vertical_spacing=0.02
    )
    return fig


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


def add_maps_and_left_timeline(fig, heatmap_results: dict, years: list):
    """
    Adds the timeline and maps to the given subplot figure.
    
    This function performs the following:
      1. Adds a vertical timeline (with year labels) in the left column (cell (1,1)) that spans all rows.
      2. Adds the corresponding map for each year into the right column (cell (row, 2)), in ascending order of years.
    
    Parameters:
        fig (plotly.graph_objects.Figure): The subplot figure to which traces are added.
        heatmap_results (dict): A dictionary mapping each year to its corresponding heatmap figure.
        years (list): A list of years.
    
    Returns:
        None
    """
    # Assume that 'years' is already in ascending order (e.g., [2000, 2001, 2002, 2003, 2004])
    sorted_years = sorted(years)
    n = len(sorted_years)
    
    # Create the timeline trace for the left column (cell (1,1)) that spans all rows.
    # Use the actual year values as y-coordinates.
    time_x = [0] * n
    time_y = sorted_years  # e.g., [2000, 2001, ..., 2004]
    timeline_trace = go.Scatter(
        x=time_x,
        y=time_y,
        mode='lines+markers+text',
        text=[str(y) for y in time_y],
        textposition='middle right',
        line=dict(
            width=6,
            color='#c78247'
        ),
        marker=dict(size=10),
        showlegend=False
    )
    fig.add_trace(timeline_trace, row=1, col=1)
    
    # Update the left subplot's x-axis and y-axis: hide x-axis, and configure y-axis.
    fig.update_xaxes(visible=False, row=1, col=1)
    # Manually set the domain of the left subplot to fill the entire left column.
    fig.layout.xaxis.domain = [0.0, 0.2]
    fig.layout.yaxis.domain = [0, 1]
    # Configure the y-axis ticks: hide tick labels (if desired) or set them to display actual years.
    fig.update_yaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=False,
        showline=False,
        tickvals=sorted_years,
        ticktext=[str(y) for y in sorted_years],
        autorange="reversed",  # Reverse to have the smallest year at the top if needed
        row=1, col=1
    )
    
    # Add maps to the right column (col=2) in each row.
    for idx, year in enumerate(sorted_years):
        row_idx = idx + 1
        single_fig = heatmap_results[year]
        for trace in single_fig.data:
            # Bind the trace to a common coloraxis.
            trace.update(coloraxis='coloraxis')
            fig.add_trace(trace, row=row_idx, col=2)
        map_key = "map" if row_idx == 1 else f"map{row_idx}"
        if map_key in fig.layout:
            fig.layout[map_key].update({
                "center": {"lat": 20, "lon": 160},
                "zoom": 0.1,
                "style": single_fig.layout['map']['style']
            })


def combined_heatmaps_vertical_with_left_timeline(keywords: str, years: list):
    """
    Combines multiple year-based heatmaps (arranged vertically) with a left-side timeline.
    
    The left column displays a vertical timeline with year labels (without axis tick numbers or gridlines),
    while the right column displays the corresponding heatmaps for each year.
    
    Parameters:
        keywords (str): The research keywords used to filter the data.
        years (list): A list of integer years to be visualized.
    
    Returns:
        plotly.graph_objects.Figure: The final Plotly figure combining the left timeline and vertical heatmaps.
    """
    n = len(years)
    fig = create_map_and_left_timeline_figure(n)
    geojson_data = load_geojson()
    heatmap_results = generate_heatmaps(keywords, years, geojson_data)
    add_maps_and_left_timeline(fig, heatmap_results, years)
    
    # Apply unified coloraxis settings and overall layout configuration.
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        height=1500,
        width=1000,
        title_text="Dummy Research Heatmaps + Left Timeline",
        title_x=0.5,
        margin={"r": 20, "t": 50, "l": 20, "b": 20},
        coloraxis=dict(
            colorscale=[
                "#D1D4FC", "#B0B5FA", "#8E96F5", "#6E7CEF",
                "#5A65C9", "#464FA0", "#333C80"
            ],
            colorbar=dict(title='Research Density')
        )
    )
    return fig
