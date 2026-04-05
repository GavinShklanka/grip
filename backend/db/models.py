"""GRIP database models. Five tables: indicator_values, domain_scores, forecasts, alerts, topology_state."""

from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Enum, Text,
    Index, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase
import enum


class Base(DeclarativeBase):
    pass


class DataQuality(str, enum.Enum):
    current = "current"
    stale = "stale"
    interpolated = "interpolated"
    missing = "missing"


class AlertSeverity(str, enum.Enum):
    watch = "watch"
    warning = "warning"
    critical = "critical"


class EdgeStatus(str, enum.Enum):
    active = "active"
    degraded = "degraded"
    offline = "offline"


class IndicatorValue(Base):
    """Raw indicator values from ingestion. One row per indicator per entity per timestamp."""
    __tablename__ = "indicator_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(String(100), nullable=False, index=True)
    country_id = Column(String(3), nullable=True, index=True)
    region_id = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    raw_value = Column(Float, nullable=True)
    normalized_value = Column(Float, nullable=True)
    source = Column(String(50), nullable=False)
    data_quality = Column(String(20), default="current")
    ingested_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_indicator_ts", "indicator_id", "country_id", "timestamp"),
    )


class DomainScore(Base):
    """Computed domain scores. One row per domain per entity per timestamp."""
    __tablename__ = "domain_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(10), nullable=False)  # 'country' or 'region'
    entity_id = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    score = Column(Float, nullable=False)
    velocity = Column(Float, nullable=True)  # points per day, 7-day smoothed
    data_coverage = Column(Float, default=1.0)  # 0.0-1.0
    anomaly_flag = Column(Boolean, default=False)
    computed_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_domain_entity_ts", "domain_id", "entity_id", "timestamp"),
    )


class Forecast(Base):
    """Risk model outputs. One row per forecast run."""
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    horizon_days = Column(Integer, default=30)
    probability = Column(Float, nullable=False)
    ci_lower_80 = Column(Float, nullable=True)
    ci_upper_80 = Column(Float, nullable=True)
    ci_lower_95 = Column(Float, nullable=True)
    ci_upper_95 = Column(Float, nullable=True)
    model_confidence = Column(String(20), default="moderate")  # good/moderate/poor
    features_used = Column(Text, nullable=True)  # JSON string of feature values
    model_version = Column(String(20), default="1.0")


class Alert(Base):
    """Active alerts from rule-based and model-based triggers."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), nullable=False)  # rule name
    severity = Column(String(20), nullable=False)  # watch/warning/critical
    description = Column(Text, nullable=False)
    affected_countries = Column(String(50), nullable=True)  # comma-separated
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class TopologyState(Base):
    """Current status of infrastructure edges. Updated by ingestion or manual override."""
    __tablename__ = "topology_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    edge_id = Column(String(50), nullable=False, unique=True, index=True)
    status = Column(String(20), nullable=False, default="active")  # active/degraded/offline
    reduced_capacity_mw = Column(Float, nullable=True)  # only set if degraded
    reason = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
