import pytest
import pandas as pd
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base, IndicatorValue
from backend.ingestion.entsog import EntsogIngestionModule
from backend.config import get_settings


@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_entsog_demo_mode(test_session, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "demo_mode", True)
    
    module = EntsogIngestionModule()
    df_raw = module.fetch(datetime(2024, 1, 1), datetime(2024, 1, 2))
    assert not df_raw.empty
    
    df_trans = module.transform(df_raw)
    assert not df_trans.empty
    
    rows = module.load(df_trans.head(10), test_session)
    assert rows > 0


def test_entsog_transform():
    module = EntsogIngestionModule()
    
    raw_data = pd.DataFrame({
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 01:00:00"],
        "value": [10.5, 0.0],
        "point_id": ["Kiemenai", "Kiemenai"],
        "country": ["LV", "LV"],
        "capacity_mcm": [50.0, 50.0]
    })
    
    df_trans = module.transform(raw_data)
    assert not df_trans.empty
    inds = df_trans["indicator_id"].tolist()
    assert "gas_import_concentration" in inds


def test_entsog_load(test_session):
    module = EntsogIngestionModule()
    
    df_trans = pd.DataFrame([{
        "indicator_id": "gas_import_concentration",
        "country_id": "LV",
        "region_id": None,
        "timestamp": datetime(2024, 1, 1),
        "raw_value": 1.0,
        "normalized_value": None,
        "source": "entsog",
        "data_quality": "current",
    }])
    
    rows = module.load(df_trans, test_session)
    assert rows == 1
    
    db_items = test_session.query(IndicatorValue).all()
    assert db_items[0].indicator_id == "gas_import_concentration"
