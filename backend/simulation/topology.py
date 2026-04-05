"""Network topology loader for GRIP simulation."""

import json
import logging
from pathlib import Path
import networkx as nx

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"


class TopologyLoader:
    """Loads physical infrastructure networks into NetworkX models."""

    def __init__(self):
        with open(CONFIG_DIR / "topology.json", encoding="utf-8") as f:
            self.config = json.load(f)

        self.countries = {n["id"]: n for n in self.config["nodes"]["countries"]}
        self.interconnectors = self.config["nodes"]["interconnectors"]
        self.facilities = self.config["nodes"].get("facilities", [])

    def build_network(self) -> nx.MultiGraph:
        """Returns a generic multigraph with base capacities.
        
        Using MultiGraph because two countries might share 
        multiple lines (e.g. Estlink 1 and Estlink 2, plus Balticconnector).
        """
        G = nx.MultiGraph()

        # Add country nodes
        for cid, cd in self.countries.items():
            G.add_node(cid, **cd)

        # Add interconnectors as edges
        for edge in self.interconnectors:
            # We use the edge id as the MultiGraph edge key for direct lookup.
            cap_mw = edge.get("capacity_mw", 0.0)
            if "commercial_capacity_mw" in edge:
                 cap_mw = edge["commercial_capacity_mw"]
            
            cap_mcm = edge.get("capacity_mcm_day", 0.0)
            
            G.add_edge(
                edge["from"], 
                edge["to"], 
                key=edge["id"],
                edge_id=edge["id"],
                type=edge["type"],
                capacity_mw=float(cap_mw),
                capacity_mcm=float(cap_mcm),
                vulnerability=edge.get("vulnerability", "unknown"),
                status="active" # Base state is up
            )

        return G
