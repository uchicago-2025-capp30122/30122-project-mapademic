import math
import pytest
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.visualization.heatmap import (
    main_heatmap,
    create_subplot_figure,
    generate_heatmaps,
    add_heatmaps_to_figure,
    add_timeline_and_arrows,
    combined_heatmaps_with_timeline_and_arrows
)

# --------------------------
# Dummy Functions for Testing
# --------------------------

def dummy_load_csv(keywords, year):
    """Return a simple DataFrame for testing."""
    data = {
        'country': ['TestState'],
        'state_name': ['TestCountry'],
        'CRDI': [1.0],
        'year': [year]
    }
    return pd.DataFrame(data)


def dummy_load_geojson():
    """Return a minimal GeoJSON object for testing."""
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"match_id": "TestCountry_TestState"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0,0], [0,1], [1,1], [1,0], [0,0]]]
            }
        }]
    }


def dummy_main_heatmap(keywords, year, geojson_data):
    """
    A dummy version of main_heatmap that returns a minimal figure
    with a Scattermapbox trace (compatible with mapbox subplots).
    """
    fig = go.Figure()
    # Use Scattermapbox instead of Scatter
    fig.add_trace(go.Scattermap(
        lat=[20],  # dummy latitude
        lon=[160], # dummy longitude
        mode='markers',
        marker=dict(size=10)
    ))
    fig.update_layout(
        title_text=f"{year} World Research Heat Distribution",
        map={"center": {"lat": 20, "lon": 160}, "zoom": 0.8, "style": "carto-positron"}
    )
    return fig

# --------------------------
# Monkeypatching Loader Functions
# --------------------------
# Because in heatmap.py the functions are imported via:
#   from .cache_utils import load_csv, load_geojson
# we must patch the names used in that module.
#
# Additionally, if caching from streamlit is wrapping load_csv, we patch the underlying function.
@pytest.fixture(autouse=True)
def patch_load_functions(monkeypatch):
    # Patch both in heatmap.py and in cache_utils.py to be safe.
    monkeypatch.setattr("src.visualization.heatmap.load_csv", dummy_load_csv)
    monkeypatch.setattr("src.visualization.heatmap.load_geojson", dummy_load_geojson)
    monkeypatch.setattr("src.visualization.cache_utils.load_csv", dummy_load_csv)
    monkeypatch.setattr("src.visualization.cache_utils.load_geojson", dummy_load_geojson)

# --------------------------
# Test Cases
# --------------------------

def test_main_heatmap():
    """Test that main_heatmap returns a valid figure with the expected title."""
    keywords = "test"
    year = 2021
    geojson_data = dummy_load_geojson()
    fig = main_heatmap(keywords, year, geojson_data)
    assert isinstance(fig, go.Figure)
    # Check that the title text contains the year.
    assert f"{year}" in fig.layout.title.text


def test_create_subplot_figure():
    """Test the creation of the subplot layout and returned layout parameters."""
    n = 4
    num_cols = 2
    timeline_height = 0.15
    fig, r_map, map_row_height = create_subplot_figure(n, num_cols, timeline_height)
    expected_r_map = math.ceil(n / num_cols)
    expected_map_row_height = (1 - timeline_height) / expected_r_map
    assert r_map == expected_r_map
    assert abs(map_row_height - expected_map_row_height) < 1e-6
    assert isinstance(fig, go.Figure)


def test_generate_heatmaps(monkeypatch):
    """Test that generate_heatmaps returns a dictionary with figures for each year."""
    keywords = "test"
    years = [2020, 2021]
    geojson_data = dummy_load_geojson()
    # Override main_heatmap to use our dummy version.
    monkeypatch.setattr("src.visualization.heatmap.main_heatmap", dummy_main_heatmap)
    heatmaps = generate_heatmaps(keywords, years, geojson_data)
    assert isinstance(heatmaps, dict)
    assert set(heatmaps.keys()) == set(years)
    for year in years:
        fig = heatmaps[year]
        assert isinstance(fig, go.Figure)
        # Check that each dummy figure has at least one trace.
        assert len(fig.data) > 0
        # Also check that the trace is of type 'scattermapbox'
        assert fig.data[0].type == "scattermap"


def test_add_heatmaps_to_figure():
    """
    Test adding dummy heatmaps to a subplot figure and computing arrow positions.
    Here we create dummy heatmap figures with Scattermapbox traces.
    """
    n = 2
    num_cols = 2
    timeline_height = 0.15
    fig, r_map, map_row_height = create_subplot_figure(n, num_cols, timeline_height)
    
    # Create a dummy heatmap figure with a Scattermapbox trace.
    dummy_fig = go.Figure()
    dummy_fig.add_trace(go.Scattermap(
        lat=[20],
        lon=[160],
        mode='markers',
        marker=dict(size=10)
    ))
    dummy_fig.update_layout(
        mapbox={"center": {"lat": 20, "lon": 160}, "zoom": 0.8, "style": "carto-positron"}
    )
    heatmap_results = {2020: dummy_fig, 2021: dummy_fig}
    years = [2020, 2021]
    arrow_info = add_heatmaps_to_figure(
        fig, heatmap_results, years, num_cols, map_row_height, timeline_height, r_map
    )
    # Verify that arrow_info is a list with one entry per year.
    assert isinstance(arrow_info, list)
    assert len(arrow_info) == len(years)
    # Each arrow_info dictionary should contain the required keys.
    for info in arrow_info:
        for key in ["map_x", "map_y", "timeline_x", "year"]:
            assert key in info
    # Also check that traces have been added to the figure.
    # Since each dummy_fig has one trace and we add one per year:
    assert len(fig.data) >= len(years)


def test_add_timeline_and_arrows():
    """
    Test that add_timeline_and_arrows correctly adds the timeline trace and dotted lines.
    This test uses a subplot figure created by create_subplot_figure.
    """
    # Create a dummy subplot figure. For timeline, we expect the last row.
    n = 2
    num_cols = 2
    timeline_height = 0.15
    fig, r_map, map_row_height = create_subplot_figure(n, num_cols, timeline_height)
    
    # Provide dummy arrow info.
    arrow_info = [
        {"map_x": 0.3, "map_y": 0.5, "timeline_x": 0.4, "year": 2020},
        {"map_x": 0.7, "map_y": 0.5, "timeline_x": 0.6, "year": 2021}
    ]
    # This function will add a timeline trace into the subplot grid.
    add_timeline_and_arrows(fig, arrow_info, timeline_height, r_map)
    
    # Find the timeline trace by checking its mode.
    timeline_traces = [trace for trace in fig.data if trace.mode == "markers+lines+text"]
    assert len(timeline_traces) == 1
    # Check that at least as many shapes (dotted lines) are added as arrow infos.
    assert len(fig.layout.shapes) >= len(arrow_info)


def test_combined_heatmaps_with_timeline_and_arrows(monkeypatch):
    """
    Integration test for the complete combined figure function.
    Ensure that the overall title is set and that a timeline trace exists.
    """
    keywords = "test"
    years = [2020, 2021]
    # Override main_heatmap to use our dummy_main_heatmap that returns a Scattermapbox trace.
    monkeypatch.setattr("src.visualization.heatmap.main_heatmap", dummy_main_heatmap)
    fig = combined_heatmaps_with_timeline_and_arrows(keywords, years)
    assert isinstance(fig, go.Figure)
    # Verify that the title is correctly set.
    assert "World Research Heat Distribution Timeline" in fig.layout.title.text
    # Check that a timeline trace is present (look for mode "markers+lines+text").
    timeline_traces = [trace for trace in fig.data if trace.mode == "markers+lines+text"]
    assert len(timeline_traces) == 1
