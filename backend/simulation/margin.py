"""N-1 margin calculator."""

import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from backend.db.models import TopologyState
from backend.config import get_settings

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"

class MarginCalculator:
    """Computes capacity margins per country respecting N-1 constraints and active topology state."""

    def __init__(self, session: Session):
        self.session = session
        
        with open(CONFIG_DIR / "topology.json", encoding="utf-8") as f:
            self.topology = json.load(f)
            
        with open(CONFIG_DIR / "thresholds.json", encoding="utf-8") as f:
            self.thresholds = json.load(f)["margin_thresholds_mw"]
            
        self.nodes = {n["id"]: n for n in self.topology["nodes"]["countries"]}
        self.edges = [e for e in self.topology["nodes"]["interconnectors"] if "electric" in e.get("type", "")]
        self.facilities = self.topology["nodes"].get("facilities", [])
        
        state_objs = self.session.query(TopologyState).all()
        self.edge_state = {s.edge_id: s for s in state_objs}

    def calculate_country_margin(self, country_id: str) -> dict | None:
        """Calculates actual N-1 capacity margin: Generation + Import - Demand - Reserve - (Largest N-1 Unit)."""
        node = self.nodes.get(country_id)
        if not node or node.get("type") != "focus":
            return None
            
        generation = node.get("generation_capacity_mw", 0.0)
        demand = node.get("peak_demand_mw", 0.0)
        
        available_import = 0.0
        edge_capacities = []
        
        for edge in self.edges:
            if edge["to"] != country_id and edge["from"] != country_id:
                continue
                
            state = self.edge_state.get(edge["id"])
            cap = edge.get("commercial_capacity_mw", edge["capacity_mw"])
            
            if state:
                if state.status == "offline":
                    cap = 0.0
                elif state.status == "degraded" and state.reduced_capacity_mw is not None:
                    cap = state.reduced_capacity_mw
                    
            if cap > 0:
                available_import += cap
                edge_capacities.append(cap)
                    
        # N-1 constraint involves largest single failure (interconnector or generation unit)
        max_edge_fail = max(edge_capacities) if edge_capacities else 0.0
        max_gen_fail = 0.0
        
        # Facilities have discrete capacities (e.g. Olkiluoto 3, Narva plants might be composite but treated as single block if indicated)
        for fac in self.facilities:
            if fac["country"] == country_id and fac.get("capacity_mw"):
                if fac["capacity_mw"] > max_gen_fail:
                    # In true N-1, if Narva has many 200MW units, 1400MW is not lost at once. 
                    # But Olkiluoto 3 is a single 1650MW block.
                    # We will treat 'nuclear_plant' as a single block for safety constraint.
                    if fac["type"] == "nuclear_plant":
                        max_gen_fail = fac["capacity_mw"]
                        
        largest_single_failure = max(max_edge_fail, max_gen_fail)
        
        # Reserve balancing 
        reserve = 0.0
        if country_id in ["EE", "LV", "LT"]:
            # Baltics uniformly share the 1500MW requirement post-BRELL
            reserve = 500.0  
            
        margin_mw = float(generation) + available_import - float(demand) - reserve - largest_single_failure
        
        status = "red"
        if margin_mw >= self.thresholds.get("green_above", 500):
            status = "green"
        elif margin_mw >= self.thresholds.get("amber_above", 0):
            status = "amber"
            
        return {
            "country_id": country_id,
            "available_import_mw": float(available_import),
            "demand_mw": float(demand),
            "reserve_requirement_mw": float(reserve),
            "margin_mw": float(margin_mw),
            "status": status
        }
        
    def calculate_all(self):
        """Returns margins for all focus countries."""
        results = []
        for n in self.nodes.values():
            if n.get("type") == "focus":
                res = self.calculate_country_margin(n["id"])
                if res:
                    results.append(res)
                    
        return results
