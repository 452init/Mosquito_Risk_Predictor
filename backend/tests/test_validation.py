"""Tests for API input validation."""

from app.utils.validation import validate_city_name


class TestCityNameValidation:
    def test_accepts_valid_city(self):
        name, error = validate_city_name("Nairobi")
        assert name == "Nairobi"
        assert error is None

    def test_rejects_empty_string(self):
        name, error = validate_city_name("   ")
        assert name is None
        assert error is not None

    def test_rejects_too_long_name(self):
        name, error = validate_city_name("A" * 101, max_length=100)
        assert name is None
        assert "too long" in error

    def test_rejects_control_characters(self):
        name, error = validate_city_name("Nairobi\x00")
        assert name is None
        assert "invalid characters" in error

    def test_rejects_non_string(self):
        name, error = validate_city_name(123)
        assert name is None
        assert "string" in error
