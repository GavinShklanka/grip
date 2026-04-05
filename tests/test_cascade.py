import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base
from backend.simulation.cascade import CascadeEngine


@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_cascade_engine_no_cascade(test_session):
    engine = CascadeEngine(test_session)
    
    # 1. No edges offline
    res_clean = engine.run_cascade([])
    assert res_clean["equilibrium_steps"] == 1
    assert len(res_clean["final_offline_edges"]) == 0
    
    # 2. Single outage that doesn't trigger negative margin
    # estlink_1 is 358 MW. For FI, 358 MW loss does not drop it below 0.
    res_minor = engine.run_cascade(["estlink_1"])
    assert res_minor["equilibrium_steps"] == 1
    assert res_minor["final_offline_edges"] == ["estlink_1"]


def test_cascade_engine_trigger(test_session):
    engine = CascadeEngine(test_session)
    
    # Let's forcefully cause a cascade by lowering FI generation artificially so it fails
    # when estlink_2 is cut.
    # Note: we mutate the engine's in-memory node data for testing.
    engine.margin_calc.nodes["FI"]["generation_capacity_mw"] = 15000.0
    # Demand is 14500. Reserve 0. 
    # Available import initially = 1008
    # N-1 max outage = 1650 (Olkiluoto 3)
    # Margin = 15000 + 1008 - 14500 - 1650 = -142! This means it's ALREADY negative.
    
    res = engine.run_cascade([])
    
    # Since FI margin is negative, it curtails ALL its exports!
    # FI has exports to EE (estlink_1, estlink_2).
    # So FI cuts them.
    assert "estlink_1" in res["final_offline_edges"]
    assert "estlink_2" in res["final_offline_edges"]
    
    # Then EE loses estlink_1 and 2 imports. 
    # Does EE go negative?
    # EE gen=2800. Demand=1600. Reserve=500. 
    # Available import initially had Balticconnector? Gas doesn't count.
    # Let's see if EE goes negative.
    assert res["equilibrium_steps"] > 1
    
    # Test outputs are structured correctly
    assert "trace" in res
    assert res["trace"][0]["step"] == 1
