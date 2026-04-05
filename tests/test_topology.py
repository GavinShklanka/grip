import pytest
import networkx as nx

from backend.simulation.topology import TopologyLoader


def test_topology_loader():
    loader = TopologyLoader()
    G = loader.build_network()
    
    # Needs to be a MultiGraph since FI and EE share estlink_1, estlink_2, balticconnector
    assert isinstance(G, nx.MultiGraph)
    
    # Check node FI
    assert "FI" in G.nodes
    assert G.nodes["FI"]["name"] == "Finland"
    assert G.nodes["FI"]["generation_capacity_mw"] == 22000
    
    # Verify edge presence via key
    assert G.has_edge("FI", "EE", key="estlink_1")
    assert G.has_edge("FI", "EE", key="estlink_2")
    assert G.has_edge("FI", "EE", key="balticconnector")
    
    # Verify edge attributes
    edge_data = G.get_edge_data("FI", "EE", key="estlink_1")
    assert edge_data["capacity_mw"] == 358.0
    assert edge_data["status"] == "active"
    
    bc_data = G.get_edge_data("FI", "EE", key="balticconnector")
    assert bc_data["capacity_mcm"] == 7.2
    assert bc_data["type"] == "gas_pipeline"
