"""Cascade simulation engine.

Traces capacity reduction paths through the grid using capacity arithmetic.
If a country's margin turns negative, it curtail exports to neighboring countries,
which may trigger further cascading shortages.
"""

import logging
from sqlalchemy.orm import Session
import networkx as nx
from copy import deepcopy

from backend.simulation.topology import TopologyLoader
from backend.simulation.margin import MarginCalculator

logger = logging.getLogger(__name__)


class CascadeEngine:
    """Simulates cascading effects of infrastructure failures."""

    def __init__(self, session: Session):
        self.session = session
        self.loader = TopologyLoader()
        self.base_graph = self.loader.build_network()
        self.margin_calc = MarginCalculator(self.session)
        
        # Override the MarginCalculator's state to let us mock purely in memory
        # without committing TopologyState rows, since cascades are hypothetical
        # scenarios running in a workspace.
        self.nodes = self.margin_calc.nodes
        self.edges = self.margin_calc.edges

    def _calculate_margins_in_memory(self, mutated_edge_state: dict) -> list[dict]:
        """Calculates margins using a temporary edge state map instead of the DB."""
        # Swap the edge state out
        original_state = self.margin_calc.edge_state
        
        # Merge DB state with our scenario mutations 
        # (For this mock, we just use a simple dict mapping edge_id -> status obj)
        class MockState:
            def __init__(self, status, cap=None):
                self.status = status
                self.reduced_capacity_mw = cap
                
        sim_state = {}
        for k, v in original_state.items():
            sim_state[k] = MockState(v.status, v.reduced_capacity_mw)
            
        for k, status_str in mutated_edge_state.items():
            sim_state[k] = MockState(status_str)
            
        self.margin_calc.edge_state = sim_state
        
        try:
            results = self.margin_calc.calculate_all()
        finally:
            self.margin_calc.edge_state = original_state
            
        return results

    def run_cascade(self, initial_offline_edges: list[str]) -> dict:
        """Runs the cascade loop until equilibrium.
        
        Parameters
        ----------
        initial_offline_edges : list of str
            Edge IDs that are severed in the initial event.
            
        Returns
        -------
        dict
            Result trace containing steps, final_margins, and curtailed_edges.
        """
        trace = []
        current_offline = deepcopy(initial_offline_edges)
        mutated_state = {e: "offline" for e in current_offline}
        
        step = 0
        while True:
            step += 1
            margins = self._calculate_margins_in_memory(mutated_state)
            
            # Record state at this step
            trace.append({
                "step": step,
                "offline_edges": deepcopy(current_offline),
                "margins": margins
            })
            
            new_curtailments = []
            
            # Find countries with critical (red) margin deficits
            for m in margins:
                if m["margin_mw"] < 0:
                    country = m["country_id"]
                    
                    # Country needs to save itself by curtailing its exports
                    # Find all active export edges from this country
                    for edge in self.edges:
                        if edge["from"] == country and edge["id"] not in current_offline:
                            # It's an export line that is still active
                            # Shut it down to simulate export curtailment
                            new_curtailments.append(edge["id"])
                            
            if not new_curtailments:
                # Equilibrium reached
                break
                
            # Apply new curtailments for next loop
            for e in new_curtailments:
                if e not in current_offline:
                    current_offline.append(e)
                    mutated_state[e] = "offline"
                    
            # Prevent infinite loops in cyclic grids (though curtailments only monotonically increase)
            if step > 10:
                logger.warning("Cascade limit reached (10 steps). Bailing out.")
                break
                
        return {
            "equilibrium_steps": step,
            "initial_event": initial_offline_edges,
            "final_offline_edges": current_offline,
            "trace": trace,
            "impacted_countries": [m["country_id"] for m in trace[-1]["margins"] if m["status"] != "green"]
        }
