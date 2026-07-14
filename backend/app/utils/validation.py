"""
Input validation helpers for API routes.
"""

import re

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def validate_city_name(raw_value, max_length=100):
    """
    Validate and sanitize a city name from user input.

    Returns:
        tuple: (city_name, error_message). error_message is None when valid.
    """
    if raw_value is None:
        return None, "Missing required field: city_name"

    if not isinstance(raw_value, str):
        return None, "city_name must be a string."

    city_name = raw_value.strip()

    if not city_name:
        return None, "City name cannot be empty."

    if len(city_name) > max_length:
        return None, f"City name is too long (max {max_length} characters)."

    if _CONTROL_CHARS.search(city_name):
        return None, "City name contains invalid characters."

    return city_name, None
