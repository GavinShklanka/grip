"""Pydantic response models for /api/forecast/ endpoints."""

from pydantic import BaseModel, Field
from datetime import datetime


class RiskResponse(BaseModel):
    probability: float = Field(ge=0, le=1)
    ci_lower_80: float = Field(ge=0, le=1)
    ci_upper_80: float = Field(ge=0, le=1)
    ci_lower_95: float = Field(ge=0, le=1)
    ci_upper_95: float = Field(ge=0, le=1)
    model_confidence: str  # good/moderate/poor
    horizon_days: int = 30
    generated_at: datetime
    features_summary: dict = {}


class BacktestEventResult(BaseModel):
    event_id: str
    event_name: str
    event_date: str
    peak_risk_30d_prior: float
    was_risk_elevated: bool
    risk_trajectory: list[dict] = []  # [{date, probability}]


class BacktestResponse(BaseModel):
    brier_score: float
    naive_baseline_brier: float
    beats_baseline: bool
    events_detected: int
    events_total: int
    recall: float
    per_event_results: list[BacktestEventResult]


class CalibrationBin(BaseModel):
    bin_lower: float
    bin_upper: float
    predicted_avg: float
    observed_frequency: float
    sample_count: int


class CalibrationResponse(BaseModel):
    bins: list[CalibrationBin]
    brier_score: float
