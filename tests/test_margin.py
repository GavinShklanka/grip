import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base, TopologyState
from backend.simulation.margin import MarginCalculator

@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_margin_calculator_base(test_session):
    calc = MarginCalculator(test_session)
    res = calc.calculate_all()
    
    assert len(res) == 4 # FI, EE, LV, LT
    
    fi = next(r for r in res if r["country_id"] == "FI")
    assert fi["demand_mw"] == 14500.0
    assert fi["reserve_requirement_mw"] == 0.0
    
    # max single failure should be 1650 for FI (Olkiluoto 3)
    # imported available from topology (without outages) = estlink_1 (358) + estlink_2 (650) = 1008
    # margins = 22000 (gen) + 1008 (import) - 14500 (demand) - 0 (reserve) - 1650 (N-1) = 6858
    assert fi["available_import_mw"] == 1008.0
    assert fi["margin_mw"] == 6858.0
    assert fi["status"] == "green"
    
def test_margin_calculator_with_outage(test_session):
    test_session.add(TopologyState(edge_id="estlink_2", status="offline"))
    test_session.commit()
    
    calc = MarginCalculator(test_session)
    res = calc.calculate_country_margin("FI")
    
    # 1008 - 650 = 358
    assert res["available_import_mw"] == 358.0
    # margin = 22000 + 358 - 14500 - 0 - 1650 = 6208
    assert res["margin_mw"] == 6208.0
