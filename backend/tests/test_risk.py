"""Unit tests for the mosquito risk scoring service."""

from app.services.risk import (
    calculate_risk_score,
    determine_risk_category,
    forecast_had_rain_within,
    generate_advice,
)


class TestForecastRainDetection:
    def test_detects_precipitation_in_forecast(self):
        forecast = {"days": [{"precipitation": 2.5}]}
        assert forecast_had_rain_within(forecast, 48) is True

    def test_no_rain_when_forecast_empty(self):
        assert forecast_had_rain_within({"days": []}, 48) is False

    def test_detects_rain_from_condition_text(self):
        forecast = {"days": [{"condition": "Light rain showers"}]}
        assert forecast_had_rain_within(forecast, 48) is True


class TestRiskScore:
    def test_high_risk_when_all_factors_present(self):
        current = {"temperature": 25, "humidity": 75}
        forecast = {"days": [{"precipitation": 10}]}

        score, reasons = calculate_risk_score(current, forecast)

        assert score == 3
        assert len(reasons) == 3

    def test_low_risk_when_no_factors_match(self):
        current = {"temperature": 10, "humidity": 30}
        forecast = {"days": [{"precipitation": 0, "condition": "Clear sky"}]}

        score, reasons = calculate_risk_score(current, forecast)

        assert score == 0
        assert reasons == []

    def test_medium_risk_with_two_factors(self):
        current = {"temperature": 24, "humidity": 65}
        forecast = {"days": [{"precipitation": 0, "condition": "Sunny"}]}

        score, _ = calculate_risk_score(current, forecast)

        assert score == 2


class TestRiskCategory:
    def test_category_mapping(self):
        assert determine_risk_category(3) == "HIGH"
        assert determine_risk_category(2) == "MEDIUM"
        assert determine_risk_category(1) == "LOW"
        assert determine_risk_category(0) == "LOW"


class TestAdvice:
    def test_advice_for_each_category(self):
        assert "mosquito net" in generate_advice("HIGH").lower()
        assert "mosquito net" in generate_advice("MEDIUM").lower()
        assert "low mosquito risk" in generate_advice("LOW").lower()
