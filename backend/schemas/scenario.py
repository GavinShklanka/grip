"""Pydantic models for /api/scenario/ endpoints."""

from pydantic import BaseModel


class ScenarioOverride(BaseModel):
    edge_id: str | None = None
    facility_id: str | None = None
    indicator_id: str | None = None
    status: str | None = None  # for edge overrides: offline/degraded
    override_value: float | None = None  # for indicator overrides
    rationale: str = ""


class ScenarioRequest(BaseModel):
    name: str = "Custom Scenario"
    overrides: list[ScenarioOverride]


class CountryDelta(BaseModel):
    country_id: str
    current_margin_mw: float
    simulated_margin_mw: float
    margin_delta_mw: float
    current_status: str
    simulated_status: str


class CascadeStep(BaseModel):
    step: int
    action: str  # e.g., "edge estlink_2 set to offline"
    affected_countries: list[str]
    capacity_change_mw: float


class CascadeTrace(BaseModel):
    steps: list[CascadeStep]
    total_capacity_lost_mw: float


class ScenarioResult(BaseModel):
    scenario_name: str
    country_deltas: list[CountryDelta]
    cascade_trace: CascadeTrace
    warnings: list[str] = []


class PrebuiltScenarioSummary(BaseModel):
    id: str
    name: str
    description: str
    category: str
    override_count: int


class PrebuiltListResponse(BaseModel):
    scenarios: list[PrebuiltScenarioSummary]
