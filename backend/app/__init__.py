"""
Flask application factory.
"""

import os

from flask import Flask, jsonify

from app.config import config_by_name, validate_production_config
from app.extensions import cors, db


def _cors_origins(app):
    """Allow localhost only in development; production uses FRONTEND_URL only."""
    origins = [app.config["FRONTEND_URL"]]
    if app.config.get("DEBUG"):
        origins.extend(["http://localhost:5173", "http://localhost:3000"])
    return [origin for origin in origins if origin]


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

    if config_name == "production":
        validate_production_config(app)

    db.init_app(app)
    cors.init_app(
        app,
        origins=_cors_origins(app),
        supports_credentials=False,
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    from app.routes.api import api_bp

    app.register_blueprint(api_bp)

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if not app.config.get("DEBUG"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify({"error": "Request body too large."}), 413

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"error": "An internal server error occurred."}), 500

    with app.app_context():
        from app.models import RiskReport  # noqa: F401

        db.create_all()

    return app
