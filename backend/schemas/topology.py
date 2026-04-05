"""Pydantic response models for /api/topology/ endpoints."""

from pydantic import BaseModel
from datetime import datetime


class NodeResponse(BaseModel):
    id: str
    name: str
    type: str  # country/interconnector/facility
    node_type: str  # focus/context/electric_hvdc/gas_pipeline/etc
    attributes: dict = {}


class EdgeResponse(BaseModel):
    id: str
    name: str
    edge_type: str  # electric_hvdc/electric_ac/gas_pipeline
    from_node: str
    to_node: str
    capacity_mw: float | None = None
    capacity_mcm_day: float | None = None
    current_flow: float | None = None
    status: str = "active"  # active/degraded/offline
    vulnerability: str | None = None


class GraphResponse(BaseModel):
    nodes: list[NodeResponse]
    edges: list[EdgeResponse]
    reserve_requirement_mw: float


class OutageResponse(BaseModel):
    edge_id: str
    name: str
    status: str
    reason: str | None = None
    updated_at: datetime


class OutagesListResponse(BaseModel):
    outages: list[OutageResponse]
    total_offline: int
