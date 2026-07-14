"""
Flask application factory.
"""

import os
from flask import Flask
from app.config import config_by_name
from app.extensions import db, cors


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name (str): 'development' or 'production'.
                           Defaults to FLASK_ENV or 'development'.

    Returns:
        Flask: Configured Flask application instance.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, origins=[
        app.config["FRONTEND_URL"],
        "http://localhost:5173",
        "http://localhost:3000"
    ])

    # Register blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)

    # Create database tables
    with app.app_context():
        from app.models import RiskReport  # noqa: F401
        db.create_all()

    return app
