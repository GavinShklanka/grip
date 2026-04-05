"""API router for structural graph bounds."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from networkx.readwrite import json_graph

from backend.db.session import get_db
from backend.db.models import TopologyState
from backend.simulation.topology import TopologyLoader

router = APIRouter()

@router.get("/graph")
def get_topology_graph(db: Session = Depends(get_db)):
    """Returns the pure infrastructure edge-node layout bounds safely exported to JSON."""
    loader = TopologyLoader()
    G = loader.build_network()
    
    # Export NetworkX MultiGraph to a JSON compatible format
    data = json_graph.node_link_data(G)
    
    # We overlay any active outages immediately on top of the geometry
    stmt = select(TopologyState)
    states = db.execute(stmt).scalars().all()
    active_states = {s.edge_id: {"status": s.status, "reduced_cap": s.reduced_capacity_mw} for s in states}
    
    for link in data.get("links", []):
        edge_id = link.get("edge_id")
        if edge_id in active_states:
            st = active_states[edge_id]
            link["status"] = st["status"]
            if st["reduced_cap"] is not None:
                link["active_capacity_mw"] = st["reduced_cap"]
            else:
                if st["status"] == "offline":
                    link["active_capacity_mw"] = 0.0
                else:
                    link["active_capacity_mw"] = link.get("capacity_mw", 0.0)
        else:
            link["active_capacity_mw"] = link.get("capacity_mw", 0.0)
            
    return {"graph": data}


@router.get("/outages")
def get_active_outages(db: Session = Depends(get_db)):
    """Yields all infrastructure elements currently severed or operating inside degraded bands."""
    stmt = select(TopologyState).where(TopologyState.status.in_(["offline", "degraded"]))
    records = db.execute(stmt).scalars().all()
    
    outages = []
    for r in records:
        outages.append({
            "edge_id": r.edge_id,
            "status": r.status,
            "reduced_capacity_mw": r.reduced_capacity_mw,
            "reported_at": r.updated_at.isoformat() if r.updated_at else None
        })
        
    return {"outages": outages}
