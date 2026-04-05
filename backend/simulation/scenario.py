"""Scenario Simulation Engine."""

import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from backend.simulation.cascade import CascadeEngine

logger = logging.getLogger(__name__)
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
SCENARIOS_DIR = CONFIG_DIR / "scenarios"


class ScenarioEngine:
    """Loads JSON scenarios and routes them through the Cascade Engine."""
    
    def __init__(self, session: Session):
        self.session = session
        self.cascade_eng = CascadeEngine(session)
        
    def load_scenario(self, scenario_id: str) -> dict:
        """Loads definition from disk."""
        file_path = SCENARIOS_DIR / f"{scenario_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Scenario file '{scenario_id}.json' not found in {SCENARIOS_DIR}")
            
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
            
    def list_scenarios(self) -> list[dict]:
        """Provides metadata for all predefined scenarios."""
        scenarios = []
        if SCENARIOS_DIR.exists():
            for filepath in SCENARIOS_DIR.glob("*.json"):
                try:
                    with open(filepath, encoding="utf-8") as f:
                        data = json.load(f)
                        scenarios.append({
                            "id": data.get("id"),
                            "name": data.get("name"),
                            "category": data.get("category"),
                            "description": data.get("description")
                        })
                except json.JSONDecodeError:
                    logger.error(f"Failed parsing scenario file {filepath}")
        return scenarios
            
    def run(self, scenario_id: str | None = None, custom_overrides: list[dict] | None = None) -> dict:
        """Executes a predefined scenario combined with optional custom overrides."""
        overrides = custom_overrides or []
        scenario_meta = {}
        
        if scenario_id:
            scenario_meta = self.load_scenario(scenario_id)
            # Combine predefined overrides with any custom ones
            overrides = scenario_meta.get("overrides", []) + overrides
            
        # Parse overrides to feed the CascadeEngine
        # CascadeEngine currently accepts a list of string edge_ids representing severed lines
        initial_offline = []
        for ovr in overrides:
            # We support fully severed edges for the standard cascade logic
            if ovr.get("status") == "offline" and ovr.get("edge_id"):
                initial_offline.append(ovr["edge_id"])
                
        # Process cascade arithmetic
        result = self.cascade_eng.run_cascade(initial_offline)

        # Calculate post-scenario margins
        from backend.simulation.margin import MarginCalculator
        from backend.db.models import TopologyState
        from datetime import datetime

        # Apply overrides to TopologyState temporarily
        for edge_id in initial_offline:
            existing = self.session.query(TopologyState).filter_by(edge_id=edge_id).first()
            if existing:
                existing.status = "offline"
                existing.reduced_capacity_mw = 0.0
            else:
                self.session.add(TopologyState(
                    edge_id=edge_id, status="offline", reduced_capacity_mw=0.0,
                    updated_at=datetime.utcnow()
                ))
        self.session.flush()

        calc = MarginCalculator(self.session)
        margins_after = calc.calculate_all()

        # Rollback the temp changes
        self.session.rollback()

        # Package for API
        return {
            "scenario": scenario_meta.get("id", "custom"),
            "metadata": scenario_meta,
            "applied_overrides": overrides,
            "cascade_results": result,
            "margins_after": margins_after,
        }
