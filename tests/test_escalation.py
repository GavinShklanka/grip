import pytest
from datetime import datetime
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base, DomainScore
from backend.scoring.escalation_composite import EscalationComposite


@pytest.fixture
def test_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_escalation_composite(test_session):
    ts = datetime(2024, 1, 1)
    
    # insert domain scores
    records = [
        DomainScore(
            domain_id="energy_dependence", # weight ~0.20
            entity_type="country",
            entity_id="LT",
            timestamp=ts,
            score=80.0,
            data_coverage=1.0
        ),
        DomainScore(
            domain_id="infrastructure_vulnerability", # weight ~0.25 (depends on config)
            entity_type="country",
            entity_id="LT",
            timestamp=ts,
            score=50.0,
            data_coverage=1.0
        )
    ]
    test_session.bulk_save_objects(records)
    test_session.commit()
    
    comp = EscalationComposite(test_session)
    
    # Direct calculate
    df = comp.calculate_for_country("LT", ts, ts)
    assert not df.empty
    
    row = df.iloc[0]
    assert row["domain_id"] == "escalation_composite"
    
    energy_w = comp.domain_weights.get("energy_dependence", 0)
    infra_w = comp.domain_weights.get("infrastructure_vulnerability", 0)
    
    expected_score = (80.0 * energy_w) + (50.0 * infra_w)
    
    # Just close enough approx because config might have these exact
    assert abs(row["score"] - expected_score) < 0.01
    
    # Database update
    rows = comp.update_database(ts, ts)
    assert rows == 1
    
    db_items = test_session.query(DomainScore).filter_by(domain_id="escalation_composite").all()
    assert len(db_items) == 1
    assert db_items[0].score == row["score"]
