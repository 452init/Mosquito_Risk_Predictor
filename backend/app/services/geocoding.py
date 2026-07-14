"""
Geocoding service — resolves city names to lat/lon coordinates.
Uses the Open-Meteo Geocoding API (free, no API key required).
"""

import requests
from app.utils.constants import GEOCODING_API_URL


class GeocodingError(Exception):
    """Raised when a city cannot be resolved to coordinates."""
    pass


def resolve_coordinates(city_name):
    """
    Resolve a city name to latitude and longitude.

    Args:
        city_name (str): The name of the city to look up.

    Returns:
        dict: {
            "lat": float,
            "lon": float,
            "name": str,        # Resolved display name
            "country": str,     # Country code
            "admin1": str       # State/region (if available)
        }

    Raises:
        GeocodingError: If the city is not found or the API fails.
    """
    if not city_name or not city_name.strip():
        raise GeocodingError("City name cannot be empty.")

    try:
        response = requests.get(
            GEOCODING_API_URL,
            params={
                "name": city_name.strip(),
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Open-Meteo returns {"results": [...]} if found,
        # or no "results" key if nothing matches.
        results = data.get("results")
        if not results or len(results) == 0:
            raise GeocodingError(
                f"City '{city_name}' not recognized. Please try another name."
            )

        location = results[0]
        return {
            "lat": location["latitude"],
            "lon": location["longitude"],
            "name": location.get("name", city_name),
            "country": location.get("country_code", ""),
            "admin1": location.get("admin1", "")
        }

    except requests.exceptions.Timeout:
        raise GeocodingError("Geocoding service timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise GeocodingError(f"Geocoding service error: {str(e)}")
