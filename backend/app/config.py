"""
Application configuration loaded from environment variables.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(url):
    """Fix Render/Heroku postgres:// vs postgresql:// issue."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get("DATABASE_URL", "postgresql://localhost:5432/mosquito_risk")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")

    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173").rstrip("/")

    MAX_CITY_NAME_LENGTH = 100
    MAX_CONTENT_LENGTH = 16 * 1024  # 16 KB request body limit


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}


def validate_production_config(app):
    """Fail fast when required production secrets are missing."""
    if not app.config.get("SECRET_KEY") or app.config["SECRET_KEY"] == (
        "dev-secret-change-in-production"
    ):
        print("ERROR: SECRET_KEY must be set to a strong random value in production.", file=sys.stderr)
        sys.exit(1)

    if not app.config.get("WEATHER_API_KEY"):
        print("ERROR: WEATHER_API_KEY must be set in production.", file=sys.stderr)
        sys.exit(1)

    if not app.config.get("FRONTEND_URL") or app.config["FRONTEND_URL"].startswith(
        "http://localhost"
    ):
        print(
            "ERROR: FRONTEND_URL must be set to your deployed frontend URL in production.",
            file=sys.stderr,
        )
        sys.exit(1)
