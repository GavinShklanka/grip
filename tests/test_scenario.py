import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base
from backend.simulation.scenario import ScenarioEngine


@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_scenario_engine_list(test_session):
    engine = ScenarioEngine(test_session)
    scenarios = engine.list_scenarios()
    
    # We should have at least the estlink2_severance one from seed configs
    assert len(scenarios) > 0
    assert any(s["id"] == "estlink2_severance" for s in scenarios)


def test_scenario_engine_run(test_session):
    engine = ScenarioEngine(test_session)
    
    # Run the predefined scenario
    res = engine.run(scenario_id="estlink2_severance")
    
    assert res["scenario"] == "estlink2_severance"
    assert "metadata" in res
    assert res["metadata"]["category"] == "submarine_cable"
    
    # Ensure it passed properly to cascade_results
    assert "estlink_2" in res["cascade_results"]["initial_event"]
    assert res["cascade_results"]["equilibrium_steps"] >= 1
    
    
def test_scenario_engine_custom_overrides(test_session):
    engine = ScenarioEngine(test_session)
    
    custom = [
        {"edge_id": "nordbalt", "status": "offline", "rationale": "Manual toggle"}
    ]
    
    res = engine.run(custom_overrides=custom)
    
    assert res["scenario"] == "custom"
    assert "nordbalt" in res["cascade_results"]["initial_event"]
    assert res["applied_overrides"][0]["rationale"] == "Manual toggle"
