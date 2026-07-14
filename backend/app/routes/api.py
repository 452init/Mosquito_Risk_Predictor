"""
API routes — main flow matching the pseudocode diagram exactly.

POST /api/risk    → Steps 1–9 (full risk assessment)
GET  /api/history → Recent search history
GET  /api/health  → Health check
"""

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import RiskReport
from app.services.geocoding import resolve_coordinates, GeocodingError
from app.services.weather import get_current_weather, get_forecast, WeatherError
from app.services.risk import (
    calculate_risk_score,
    determine_risk_category,
    generate_advice
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "mosquito-risk-api"}), 200


@api_bp.route("/risk", methods=["POST"])
def assess_risk():
    """
    Main flow — matches the pseudocode MAIN block:

    1. get_city_input()              → from request body
    2. resolve_coordinates()         → geocoding service
    3. collect_weather_data()        → weather service (current + forecast)
    4. calculate_risk_score()        → risk service
    5. determine_risk_category()     → risk service
    6. generate_advice()             → risk service
    7. display_results()             → JSON response (+ save to DB)
    """
    # ---- Step 1: Get city name from request ----
    data = request.get_json(silent=True)
    if not data or not data.get("city_name"):
        return jsonify({
            "error": "Missing required field: city_name"
        }), 400

    city_name = data["city_name"].strip()

    # ---- Step 2: Resolve coordinates ----
    try:
        location = resolve_coordinates(city_name)
    except GeocodingError as e:
        return jsonify({"error": str(e)}), 404

    lat = location["lat"]
    lon = location["lon"]
    resolved_name = location["name"]
    country = location.get("country", "")
    display_name = (
        f"{resolved_name}, {country}" if country else resolved_name
    )

    # ---- Step 3 & 4: Collect weather data ----
    try:
        current_data = get_current_weather(lat, lon)
        forecast_data = get_forecast(lat, lon)
    except WeatherError as e:
        return jsonify({"error": str(e)}), 502

    # ---- Step 5: Calculate risk score ----
    score, reasons = calculate_risk_score(current_data, forecast_data)

    # ---- Step 6: Determine risk category ----
    risk_category = determine_risk_category(score)

    # ---- Step 7: Generate advice ----
    advice = generate_advice(risk_category)

    # ---- Save to database ----
    try:
        report = RiskReport(
            city_name=display_name,
            latitude=lat,
            longitude=lon,
            temperature=current_data.get("temperature"),
            humidity=current_data.get("humidity"),
            condition=current_data.get("condition"),
            risk_score=score,
            risk_category=risk_category,
            reasons=reasons,
            advice=advice
        )
        db.session.add(report)
        db.session.commit()
    except Exception:
        db.session.rollback()
        # Non-critical: don't fail the request if DB save fails

    # ---- Step 8: Return results ----
    return jsonify({
        "city_name": display_name,
        "location": {
            "latitude": lat,
            "longitude": lon,
            "country": country,
            "region": location.get("admin1", "")
        },
        "current_weather": {
            "temperature": current_data.get("temperature"),
            "humidity": current_data.get("humidity"),
            "condition": current_data.get("condition"),
            "wind_speed": current_data.get("wind_speed"),
            "feels_like": current_data.get("feels_like")
        },
        "risk": {
            "score": score,
            "max_score": 3,
            "category": risk_category,
            "reasons": reasons,
            "advice": advice
        },
        "forecast_summary": _summarize_forecast(forecast_data)
    }), 200


@api_bp.route("/history", methods=["GET"])
def get_history():
    """Return the 10 most recent risk reports."""
    try:
        reports = (
            RiskReport.query
            .order_by(RiskReport.created_at.desc())
            .limit(10)
            .all()
        )
        return jsonify({
            "reports": [r.to_dict() for r in reports]
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"Could not fetch history: {str(e)}",
            "reports": []
        }), 200


def _summarize_forecast(forecast_data):
    """Build a lightweight forecast summary for the frontend."""
    days = forecast_data.get("days", [])
    summary = []

    for day in days[:7]:
        if not isinstance(day, dict):
            continue

        entry = {}

        # Date
        for key in ["date", "day", "datetime", "time"]:
            if key in day:
                entry["date"] = str(day[key])
                break

        # Temperature
        for key in [
            "temperature_max", "temp_max", "maxtemp_c",
            "max_temp", "high"
        ]:
            if key in day:
                entry["temp_high"] = day[key]
                break

        for key in [
            "temperature_min", "temp_min", "mintemp_c",
            "min_temp", "low"
        ]:
            if key in day:
                entry["temp_low"] = day[key]
                break

        # Precipitation
        for key in [
            "precipitation", "precip", "rain", "precip_mm",
            "totalprecip_mm", "precipitation_sum"
        ]:
            if key in day:
                entry["precipitation"] = day[key]
                break

        # Condition
        for key in [
            "condition", "conditions", "weather",
            "description", "weather_description"
        ]:
            val = day.get(key)
            if isinstance(val, str):
                entry["condition"] = val
                break
            elif isinstance(val, dict) and "text" in val:
                entry["condition"] = val["text"]
                break

        if entry:
            summary.append(entry)

    return summary
