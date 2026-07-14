"""
Constants for mosquito risk calculation.
Mapped directly from the pseudocode specification.
"""

# Temperature range (°C) considered ideal for mosquito activity
RISK_TEMP_MIN = 20
RISK_TEMP_MAX = 30

# Minimum humidity (%) that favors mosquito survival
RISK_HUMIDITY_MIN = 60

# Hours to look back/forward for recent rain
RECENT_RAIN_WINDOW = 48

# Maximum forecast days (free plan limit)
FORECAST_DAYS = 7

# Weather AI API base URL
WEATHER_API_BASE_URL = "https://api.weather-ai.co"

# Open-Meteo Geocoding API (free, no key needed)
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/v1/search"
