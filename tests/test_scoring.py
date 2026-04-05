import pytest
import pandas as pd
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base, IndicatorValue, DomainScore
from backend.scoring import ScoringOrchestrator


@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_scoring_engine(test_session):
    # Insert mock indicator data
    ts = datetime(2024, 1, 1)
    
    # "energy_dependence" has electricity_import_ratio (0.3)
    # let's mock it
    records = [
        IndicatorValue(
            indicator_id="electricity_import_ratio",
            country_id="FI",
            timestamp=ts,
            raw_value=0.5,
            source="entso_e"
        ),
        # another time point for velocity
        IndicatorValue(
            indicator_id="electricity_import_ratio",
            country_id="FI",
            timestamp=ts + timedelta(days=1),
            raw_value=0.9, # increasing stress
            source="entso_e"
        )
    ]
    test_session.bulk_save_objects(records)
    test_session.commit()
    
    engine = ScoringOrchestrator(test_session)
    rows = engine.run_scoring(ts, ts + timedelta(days=1))
    
    # We expect some DomainScore objects to be created
    assert rows > 0
    
    # Verify the energy_dependence domain for FI
    results = test_session.query(DomainScore).filter_by(
        domain_id="energy_dependence", 
        entity_id="FI"
    ).order_by(DomainScore.timestamp).all()
    
    assert len(results) == 2
    
    r0, r1 = results
    assert r0.timestamp == ts
    assert r1.timestamp == ts + timedelta(days=1)
    
    # Minmax is computed over the available data
    # 0.5 -> 0, 0.9 -> 100
    # score * weight: weight is 0.3
    # 0 * 0.3 = 0, 100 * 0.3 = 30.
    # Total sum is the final score, hence 0 and 30
    assert r0.score == 0.0
    assert r1.score == 20.0
    
    # Data coverage will reflect the fraction of total domain weight
    # 0.3 / sum(all meta weights in energy_dependence)
    assert r0.data_coverage > 0
    assert r0.data_coverage < 1.0 # 0.3 / 1.0 = 0.3
