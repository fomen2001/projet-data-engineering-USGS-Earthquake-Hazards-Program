from __future__ import annotations
import requests
from typing import Dict, Any

DEFAULT_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

def fetch_usgs_geojson(url: str = DEFAULT_URL, timeout: int = 30) -> Dict[str, Any]:
    """
    Fetch USGS Earthquake GeoJSON feed.

    Parameters
    ----------
    url : str
        GeoJSON feed URL (e.g., all_day.geojson)
    timeout : int
        HTTP timeout in seconds

    Returns
    -------
    dict
        Parsed JSON payload (GeoJSON FeatureCollection)
    """
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
