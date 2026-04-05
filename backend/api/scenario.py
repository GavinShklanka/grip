"""API router for bounded cascade permutations."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.simulation.scenario import ScenarioEngine

router = APIRouter()


class CustomOverride(BaseModel):
    edge_id: str
    status: str
    rationale: str | None = None


class ScenarioRunRequest(BaseModel):
    scenario_id: str | None = None
    overrides: list[CustomOverride] = []


@router.post("/run")
def execute_scenario(payload: ScenarioRunRequest, db: Session = Depends(get_db)):
    """Fires the exact parameters into the simulated N-1 Cascade arithmetic."""
    engine = ScenarioEngine(db)
    
    ovrs = [o.model_dump() for o in payload.overrides]
    
    try:
        res = engine.run(scenario_id=payload.scenario_id, custom_overrides=ovrs)
        return res
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Scenario template not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prebuilt")
def get_prebuilt_scenarios(db: Session = Depends(get_db)):
    """Surfaces all JSON artifacts currently mapped within the backend scenarios directory."""
    engine = ScenarioEngine(db)
    scenarios = engine.list_scenarios()
    return {"scenarios": scenarios}


@router.get("/prebuilt/{scenario_id}")
def get_specific_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Exposes exact parameters governing a bounded prebuilt payload."""
    engine = ScenarioEngine(db)
    try:
        scenario = engine.load_scenario(scenario_id)
        return scenario
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Scenario template not found")
