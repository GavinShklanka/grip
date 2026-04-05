import pytest
import pandas as pd
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base, IndicatorValue
from backend.ingestion.entso_e import EntsoeIngestionModule
from backend.config import get_settings


@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_entsoe_demo_mode(test_session, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "demo_mode", True)
    
    module = EntsoeIngestionModule()
    
    df_raw = module.fetch(datetime(2024, 1, 1), datetime(2024, 1, 2))
    assert not df_raw.empty
    
    df_trans = module.transform(df_raw)
    assert not df_trans.empty
    
    # Just to be safe not writing thousands in unit test memory casually
    rows = module.load(df_trans.head(10), test_session)
    assert rows > 0


def test_entsoe_transform():
    module = EntsoeIngestionModule()
    
    raw_data = pd.DataFrame({
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 01:00:00"],
        "flow_mw": [150.5, 0.0],
        "from_country": ["FI", "FI"],
        "to_country": ["EE", "EE"],
        "interconnector_id": ["estlink_1", "estlink_1"],
        "capacity_mw": [500.0, 500.0]
    })
    
    df_trans = module.transform(raw_data)
    assert not df_trans.empty
    
    inds = df_trans["indicator_id"].tolist()
    assert "estlink_utilization" in inds
    assert "interconnectors_offline" in inds


def test_entsoe_load(test_session):
    module = EntsoeIngestionModule()
    
    df_trans = pd.DataFrame([{
        "indicator_id": "estlink_utilization",
        "country_id": "EE",
        "region_id": None,
        "timestamp": datetime(2024, 1, 1),
        "raw_value": 0.5,
        "normalized_value": None,
        "source": "entso_e",
        "data_quality": "current",
    }])
    
    rows = module.load(df_trans, test_session)
    assert rows == 1
    
    db_items = test_session.query(IndicatorValue).all()
    assert db_items[0].indicator_id == "estlink_utilization"
