"""Pydantic response models for /api/state/ endpoints."""

from pydantic import BaseModel, Field
from datetime import datetime


class ScoreResponse(BaseModel):
    country_id: str
    domain_id: str
    score: float = Field(ge=0, le=100)
    velocity: float | None = None
    data_coverage: float = Field(ge=0, le=1, default=1.0)
    anomaly_flag: bool = False
    timestamp: datetime


class MarginResponse(BaseModel):
    country_id: str
    available_import_mw: float
    demand_mw: float
    reserve_requirement_mw: float
    margin_mw: float
    status: str  # green/amber/red


class FlowResponse(BaseModel):
    interconnector_id: str
    from_country: str
    to_country: str
    flow_mw: float
    capacity_mw: float
    utilization: float = Field(ge=0, le=1)
    timestamp: datetime


class AlertResponse(BaseModel):
    alert_type: str
    severity: str  # watch/warning/critical
    description: str
    affected_countries: list[str] = []
    triggered_at: datetime
    is_active: bool = True


class ScoresListResponse(BaseModel):
    scores: list[ScoreResponse]
    last_computed: datetime | None = None


class MarginsListResponse(BaseModel):
    margins: list[MarginResponse]


class AlertsListResponse(BaseModel):
    alerts: list[AlertResponse]
    active_count: int
