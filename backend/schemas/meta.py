"""Pydantic response models for /api/meta/ endpoints."""

from pydantic import BaseModel
from datetime import datetime


class AssumptionResponse(BaseModel):
    id: str
    statement: str
    layer: str  # scoring/dependency/forecasting/scenario/structural
    sensitivity: str  # high/medium/low
    testable: bool
    status: str  # confirmed/assumed/failed
    test_plan: str = ""


class ProvenanceIndicator(BaseModel):
    indicator_id: str
    name: str
    raw_value: float | None
    normalized_value: float | None
    weight: float
    source: str
    timestamp: datetime | None
    quality_flag: str  # current/stale/interpolated/missing


class ProvenanceResponse(BaseModel):
    domain_id: str
    country_id: str
    score: float
    indicators: list[ProvenanceIndicator]
    computation_method: str
    config_version: str


class DataQualityEntry(BaseModel):
    domain_id: str
    country_id: str
    coverage: float  # 0.0-1.0
    stale_indicators: int
    total_indicators: int
    oldest_data: datetime | None


class DataQualityResponse(BaseModel):
    entries: list[DataQualityEntry]
    overall_coverage: float


class SystemStatusResponse(BaseModel):
    last_ingestion: datetime | None
    indicators_total: int
    indicators_current: int
    indicators_stale: int
    scoring_last_run: datetime | None
    risk_model_last_run: datetime | None
    risk_model_confidence: str
    alerts_active: int
    demo_mode: bool
