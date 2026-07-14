"""
Weather service — calls Weather AI API for current conditions and forecasts.
API Docs: https://weather-ai.co/docs
"""

import requests
from app.utils.constants import WEATHER_API_BASE_URL, FORECAST_DAYS
from flask import current_app


class WeatherError(Exception):
    """Raised when the Weather API call fails."""
    pass


def _get_headers():
    """Build authorization headers using the API key from config."""
    api_key = current_app.config.get("WEATHER_API_KEY", "")
    return {
        "Authorization": f"Bearer {api_key}"
    }


def get_current_weather(lat, lon):
    """
    Step 3: Call Current Weather API.

    GET /v1/current?lat=...&lon=...&units=metric&ai=false

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        dict: Current weather data with temperature, humidity, conditions.

    Raises:
        WeatherError: If the API call fails.
    """
    try:
        response = requests.get(
            f"{WEATHER_API_BASE_URL}/v1/current",
            params={
                "lat": lat,
                "lon": lon,
                "units": "metric",
                "ai": "false"
            },
            headers=_get_headers(),
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        # Extract current weather data from the response.
        # The API may nest it under "current" or return it flat.
        current = data.get("current", data)

        return {
            "temperature": _extract_field(current, [
                "temperature", "temp", "temperature_2m", "temp_c"
            ]),
            "humidity": _extract_field(current, [
                "humidity", "relative_humidity", "relative_humidity_2m"
            ]),
            "condition": _extract_field(current, [
                "condition", "conditions", "weather", "description",
                "weather_description"
            ], default="N/A"),
            "wind_speed": _extract_field(current, [
                "wind_speed", "wind_kph", "wind_speed_10m"
            ], default=0),
            "feels_like": _extract_field(current, [
                "feels_like", "feelslike", "apparent_temperature"
            ], default=None),
            "raw": current
        }

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "unknown"
        raise WeatherError(
            f"Weather API returned status {status}. "
            f"Check your API key and plan limits."
        )
    except requests.exceptions.Timeout:
        raise WeatherError("Weather API timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise WeatherError(f"Weather API error: {str(e)}")


def get_forecast(lat, lon):
    """
    Step 4: Call Forecast Weather API.

    GET /v1/forecast?lat=...&lon=...&days=7&units=metric&ai=false

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        dict: Forecast data with daily breakdown.

    Raises:
        WeatherError: If the API call fails.
    """
    try:
        response = requests.get(
            f"{WEATHER_API_BASE_URL}/v1/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "days": FORECAST_DAYS,
                "units": "metric",
                "ai": "false"
            },
            headers=_get_headers(),
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        # Extract forecast array — may be under "forecast", "daily", or top-level
        forecast_list = (
            data.get("forecast")
            or data.get("daily")
            or data.get("days")
            or []
        )

        # If forecast is a dict with a nested list, extract it
        if isinstance(forecast_list, dict):
            forecast_list = (
                forecast_list.get("forecastday")
                or forecast_list.get("days")
                or forecast_list.get("daily")
                or []
            )

        return {
            "days": forecast_list,
            "raw": data
        }

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "unknown"
        raise WeatherError(
            f"Forecast API returned status {status}. "
            f"Check your API key and plan limits."
        )
    except requests.exceptions.Timeout:
        raise WeatherError("Forecast API timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        raise WeatherError(f"Forecast API error: {str(e)}")


def _extract_field(data, possible_keys, default=None):
    """
    Try multiple possible key names to extract a value from the response.
    Weather APIs vary in their field naming — this handles that gracefully.
    """
    if not isinstance(data, dict):
        return default

    for key in possible_keys:
        if key in data and data[key] is not None:
            return data[key]

    # Also check nested structures (e.g., data.condition.text)
    for key in possible_keys:
        parts = key.split(".")
        obj = data
        for part in parts:
            if isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                obj = None
                break
        if obj is not None:
            return obj

    return default
