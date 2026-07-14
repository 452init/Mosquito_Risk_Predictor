"""
Risk calculator service — implements the pseudocode risk scoring logic.
Steps 6, 7, and 8 from the pseudocode specification.
"""

from app.utils.constants import (
    RISK_TEMP_MIN,
    RISK_TEMP_MAX,
    RISK_HUMIDITY_MIN,
    RECENT_RAIN_WINDOW
)


def forecast_had_rain_within(forecast_data, hours_window):
    """
    Check if the forecast data indicates rain within the given time window.

    Examines forecast days to determine if rain occurred recently or
    is expected soon (within RECENT_RAIN_WINDOW hours).

    Args:
        forecast_data (dict): Forecast data from weather service.
        hours_window (int): Number of hours to check (48 by default).

    Returns:
        bool: True if rain is detected within the window.
    """
    days_to_check = max(1, hours_window // 24)
    forecast_days = forecast_data.get("days", [])

    for i, day in enumerate(forecast_days[:days_to_check]):
        if not isinstance(day, dict):
            continue

        # Check various possible rain/precipitation fields
        rain_fields = [
            "precipitation", "precip", "rain", "precip_mm",
            "totalprecip_mm", "total_precipitation",
            "precipitation_sum", "rain_sum"
        ]
        for field in rain_fields:
            value = day.get(field)
            if value is not None:
                try:
                    if float(value) > 0:
                        return True
                except (ValueError, TypeError):
                    continue

        # Check condition/description for rain keywords
        condition_fields = [
            "condition", "conditions", "weather", "description",
            "weather_description", "text"
        ]
        for field in condition_fields:
            value = day.get(field)
            if isinstance(value, str):
                rain_keywords = [
                    "rain", "shower", "drizzle", "storm",
                    "thunderstorm", "precipitation", "wet"
                ]
                if any(kw in value.lower() for kw in rain_keywords):
                    return True
            elif isinstance(value, dict):
                text = value.get("text", "")
                if isinstance(text, str) and any(
                    kw in text.lower()
                    for kw in ["rain", "shower", "drizzle", "storm"]
                ):
                    return True

        # Check chance_of_rain / probability fields
        chance_fields = [
            "chance_of_rain", "precipitation_probability",
            "rain_probability", "pop"
        ]
        for field in chance_fields:
            value = day.get(field)
            if value is not None:
                try:
                    if float(value) > 30:
                        return True
                except (ValueError, TypeError):
                    continue

    return False


def calculate_risk_score(current_data, forecast_data):
    """
    Step 6: Calculate Mosquito Risk Score.

    Scores 0–3 based on three factors:
        1. Temperature in ideal range (20–30°C)
        2. Humidity >= 60%
        3. Recent or upcoming rain within 48h

    Args:
        current_data (dict): Current weather data from weather service.
        forecast_data (dict): Forecast data from weather service.

    Returns:
        tuple: (score: int, reasons: list[str])
    """
    score = 0
    reasons = []

    # Factor 1: Temperature
    temperature = current_data.get("temperature")
    if temperature is not None:
        try:
            temp = float(temperature)
            if RISK_TEMP_MIN <= temp <= RISK_TEMP_MAX:
                score += 1
                reasons.append(
                    "Temperature is in the ideal range for mosquito activity "
                    f"({temp:.1f}°C is between {RISK_TEMP_MIN}–{RISK_TEMP_MAX}°C)"
                )
        except (ValueError, TypeError):
            pass

    # Factor 2: Humidity
    humidity = current_data.get("humidity")
    if humidity is not None:
        try:
            hum = float(humidity)
            if hum >= RISK_HUMIDITY_MIN:
                score += 1
                reasons.append(
                    "High humidity favors mosquito survival "
                    f"({hum:.0f}% ≥ {RISK_HUMIDITY_MIN}%)"
                )
        except (ValueError, TypeError):
            pass

    # Factor 3: Recent/upcoming rain
    if forecast_had_rain_within(forecast_data, RECENT_RAIN_WINDOW):
        score += 1
        reasons.append(
            "Recent or upcoming rain increases standing water / breeding sites"
        )

    return score, reasons


def determine_risk_category(score):
    """
    Step 7: Determine Risk Category.

    Args:
        score (int): Risk score from 0 to 3.

    Returns:
        str: "HIGH", "MEDIUM", or "LOW"
    """
    if score >= 3:
        return "HIGH"
    elif score == 2:
        return "MEDIUM"
    else:
        return "LOW"


def generate_advice(risk_category):
    """
    Step 8: Generate Reasons & Advice.

    Args:
        risk_category (str): "HIGH", "MEDIUM", or "LOW"

    Returns:
        str: Actionable recommendation for the user.
    """
    if risk_category == "HIGH":
        return (
            "Use a mosquito net tonight. Clear any standing water "
            "near your home."
        )
    elif risk_category == "MEDIUM":
        return "Consider using a mosquito net as a precaution."
    else:
        return (
            "Low mosquito risk today, but stay alert if the "
            "weather changes."
        )
