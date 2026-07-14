"""
Database models for the Mosquito Risk Predictor.
"""

from datetime import datetime, timezone
from app.extensions import db


class RiskReport(db.Model):
    """Stores each mosquito risk assessment for search history."""

    __tablename__ = "risk_reports"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city_name = db.Column(db.String(100), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=True)
    humidity = db.Column(db.Float, nullable=True)
    condition = db.Column(db.String(100), nullable=True)
    risk_score = db.Column(db.Integer, nullable=False)
    risk_category = db.Column(db.String(10), nullable=False)
    reasons = db.Column(db.JSON, nullable=False, default=list)
    advice = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        """Serialize the report to a JSON-friendly dictionary."""
        return {
            "id": self.id,
            "city_name": self.city_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "condition": self.condition,
            "risk_score": self.risk_score,
            "risk_category": self.risk_category,
            "reasons": self.reasons,
            "advice": self.advice,
            "created_at": self.created_at.isoformat() + "Z"
        }
