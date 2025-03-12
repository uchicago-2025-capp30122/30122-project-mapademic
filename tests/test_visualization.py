import math
import pytest
import pandas as pd
import plotly.graph_objects as go

# Import functions from the new visualization code
from src.visualization.heatmap import (
    main_heatmap,
    create_map_and_left_timeline_figure,
    generate_heatmaps,
    add_maps_and_left_timeline,
    combined_heatmaps_vertical_with_left_timeline
)

# --------------------------
# Dummy Functions for Testing
# --------------------------

def dummy_load_csv(keywords, year):
    """Return a simple DataFrame for testing with field names consistent with the new code."""
    data = {
        'country': ['TestState'],
        'state_name': ['testcountry'],
        'crdi_index': [1.0],
        'year': [year]
    }
    return pd.DataFrame(data)


def dummy_load_geojson():
    """Return a minimal GeoJSON object for testing with the 'name' property key."""
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"name": "TestCountry", 
                           "clean_name": "testcountry"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]]
            }
        }]
    }


def dummy_main_heatmap(keywords, year, geojson_data):
    """
    Dummy version of main_heatmap that returns a simple figure with a choroplethmap trace.
    This ensures compatibility with "map" subplots.
    """
    fig = go.Figure()
    fig.add_trace(go.Choroplethmap(
        locations=["TestCountry"],
        z=[1.0],
        geojson=dummy_load_geojson(),
        featureidkey='properties.name'
    ))
    fig.update_layout(title_text=f"{year} World Research Distribution")
    return fig

# --------------------------
# Monkeypatch Loader Functions
# --------------------------
@pytest.fixture(autouse=True)
def patch_load_functions(monkeypatch):
    monkeypatch.setattr("src.visualization.heatmap.load_csv", dummy_load_csv)
    monkeypatch.setattr("src.visualization.heatmap.load_geojson", dummy_load_geojson)
    monkeypatch.setattr("src.visualization.cache_utils.load_csv", dummy_load_csv)
    monkeypatch.setattr("src.visualization.cache_utils.load_geojson", dummy_load_geojson)

# --------------------------
# Test Cases
# --------------------------

def test_main_heatmap():
    """
    Test the main_heatmap function:
      - Ensure it returns a valid Figure object.
      - Check that the title contains the year and is centered (title_x == 0.5).
      - Verify that the trace type is one of: choropleth, choroplethmapbox, or choroplethmap.
    """
    keywords = "test"
    year = 2021
    geojson_data = dummy_load_geojson()
    fig = main_heatmap(keywords, year, geojson_data)
    assert isinstance(fig, go.Figure)
    # Verify title text and centering
    assert f"{year} World Research Distribution" in fig.layout.title.text
    assert fig.layout.title.x == 0.5
    # Allow for multiple trace types
    valid_types = ["choropleth", "choroplethmapbox", "choroplethmap"]
    assert len(fig.data) > 0
    assert fig.data[0].type in valid_types


def test_create_map_and_left_timeline_figure():
    """
    Test the creation of the subplot layout with a left timeline:
      - Verify that the returned object is a Figure.
      - Check that the left subplot's x-axis domain is close to [0.0, 0.2].
      - Ensure the number of right-side map subplots equals the number of rows.
    """
    n = 3
    fig = create_map_and_left_timeline_figure(n)
    assert isinstance(fig, go.Figure)
    # Check left subplot x-axis domain
    assert math.isclose(fig.layout.xaxis.domain[0], 0.0, abs_tol=1e-6)
    assert math.isclose(fig.layout.xaxis.domain[1], 0.2, rel_tol=0.02)
    # Only count layout keys that start with "map" but not "mapbox"
    map_keys = [key for key in fig.layout if key.startswith("map") and not key.startswith("mapbox")]
    assert len(map_keys) == n


def test_generate_heatmaps(monkeypatch):
    """
    Test the generate_heatmaps function:
      - Ensure it returns a dictionary with years as keys and corresponding heatmap Figures as values.
      - Use dummy_main_heatmap to simplify concurrent execution.
    """
    keywords = "test"
    years = [2020, 2021]
    geojson_data = dummy_load_geojson()
    monkeypatch.setattr("src.visualization.heatmap.main_heatmap", dummy_main_heatmap)
    heatmaps = generate_heatmaps(keywords, years, geojson_data)
    assert isinstance(heatmaps, dict)
    assert set(heatmaps.keys()) == set(years)
    valid_types = ["choropleth", "choroplethmapbox", "choroplethmap"]
    for year in years:
        fig = heatmaps[year]
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.data[0].type in valid_types


def test_add_maps_and_left_timeline():
    """
    Test the add_maps_and_left_timeline function:
      - Add a left timeline with year labels to the subplot.
      - Add heatmap traces for each year to the corresponding right-side subplot.
      - Verify that the timeline trace's mode is "lines+markers+text".
    """
    n = 2
    fig = create_map_and_left_timeline_figure(n)
    
    # Create a dummy heatmap Figure with a choroplethmap trace (compatible with "map" subplots)
    dummy_fig = go.Figure()
    dummy_fig.add_trace(go.Choroplethmap(
        locations=["TestCountry"],
        z=[1.0],
        geojson=dummy_load_geojson(),
        featureidkey='properties.name'
    ))
    dummy_fig.update_layout(
        map={'center': {'lat': 20, 'lon': 160}, 'zoom': 0.8, 'style': 'carto-positron'}
    )
    heatmap_results = {2020: dummy_fig, 2021: dummy_fig}
    years = [2020, 2021]
    add_maps_and_left_timeline(fig, heatmap_results, years)
    
    # Filter for scatter traces with the expected mode for the timeline
    timeline_traces = [
        trace for trace in fig.data 
        if getattr(trace, "type", None) == "scatter" and getattr(trace, "mode", None) == "lines+markers+text"
    ]
    assert len(timeline_traces) == 1
    timeline_text = timeline_traces[0].text
    for year in sorted(years):
        assert str(year) in timeline_text
    
    # Verify the first row "map" layout update
    assert "map" in fig.layout
    center = fig.layout["map"]["center"]
    assert math.isclose(center["lat"], 20, abs_tol=1e-6)
    assert math.isclose(center["lon"], 160, abs_tol=1e-6)


def test_combined_heatmaps_vertical_with_left_timeline(monkeypatch):
    """
    Integration test for the combined_heatmaps_vertical_with_left_timeline function:
      - Ensure the final figure is a valid Figure.
      - Check that the title is set as expected.
      - Confirm that the left timeline trace exists.
    """
    keywords = "test"
    years = [2020, 2021]
    monkeypatch.setattr("src.visualization.heatmap.main_heatmap", dummy_main_heatmap)
    fig = combined_heatmaps_vertical_with_left_timeline(keywords, years)
    assert isinstance(fig, go.Figure)
    assert "2020-2021 World Research Distribution" in fig.layout.title.text
    timeline_traces = [
        trace for trace in fig.data 
        if getattr(trace, "type", None) == "scatter" and getattr(trace, "mode", None) == "lines+markers+text"
    ]
    assert len(timeline_traces) == 1
