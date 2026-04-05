"""Shared test fixtures for GRIP test suite.

Uses SQLite in-memory for speed. Tests validate logic, not Postgres-specific features.
"""

import json
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import Base, IndicatorValue, DomainScore, TopologyState

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"
SEED_DIR = ROOT / "data" / "seed"


@pytest.fixture
def test_engine():
    """In-memory SQLite engine with all tables created."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Database session for testing."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def topology_config():
    """Load topology.json as dict."""
    with open(CONFIG_DIR / "topology.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def domains_config():
    """Load domains.json as dict."""
    with open(CONFIG_DIR / "domains.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def thresholds_config():
    """Load thresholds.json as dict."""
    with open(CONFIG_DIR / "thresholds.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def disruption_events():
    """Load disruption events as dict."""
    with open(SEED_DIR / "disruption_events.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def seed_electricity_flows():
    """Load electricity flow seed data as DataFrame."""
    return pd.read_csv(SEED_DIR / "entso_e_flows.csv", parse_dates=["date"])


@pytest.fixture
def seed_gas_flows():
    """Load gas flow seed data as DataFrame."""
    return pd.read_csv(SEED_DIR / "entsog_flows.csv", parse_dates=["date"])


@pytest.fixture
def seed_gdelt():
    """Load GDELT seed data as DataFrame."""
    return pd.read_csv(SEED_DIR / "gdelt_events.csv", parse_dates=["week_start"])


@pytest.fixture
def sample_indicator_values(test_session):
    """Insert a small set of indicator values for testing scoring logic."""
    base_date = datetime(2024, 12, 1)
    records = []
    for day_offset in range(60):
        ts = base_date + timedelta(days=day_offset)
        for country in ["FI", "EE", "LV", "LT"]:
            # Electricity flow indicator
            flow = 400.0 if country != "EE" else 300.0
            # Simulate Estlink 2 outage starting Dec 25
            if country == "EE" and day_offset >= 24:
                flow = 100.0  # reduced after outage

            records.append(IndicatorValue(
                indicator_id="flow_estlink_2",
                country_id=country,
                timestamp=ts,
                raw_value=flow,
                source="entso_e",
                data_quality="current",
            ))
            records.append(IndicatorValue(
                indicator_id="gdelt_event_intensity",
                country_id=country,
                timestamp=ts,
                raw_value=150.0 + day_offset * 2,
                source="gdelt",
                data_quality="current",
            ))

    test_session.bulk_save_objects(records)
    test_session.commit()
    return test_session


@pytest.fixture
def sample_domain_scores(test_session):
    """Insert sample domain scores for testing composite and anomaly logic."""
    base_date = datetime(2024, 11, 1)
    records = []
    for day_offset in range(90):
        ts = base_date + timedelta(days=day_offset)
        for country in ["FI", "EE", "LV", "LT"]:
            base_score = 35.0
            if country == "EE" and day_offset >= 54:  # ~Dec 25
                base_score = 72.0  # spike during Estlink 2 outage

            for domain_id in ["energy_dependence", "infrastructure_vulnerability",
                              "supply_route_disruption", "sanctions_pressure"]:
                score = base_score + (hash(domain_id) % 10)
                records.append(DomainScore(
                    domain_id=domain_id,
                    entity_type="country",
                    entity_id=country,
                    timestamp=ts,
                    score=min(100, max(0, score)),
                    velocity=0.5 if day_offset > 54 and country == "EE" else 0.0,
                    data_coverage=1.0,
                    anomaly_flag=False,
                ))

    test_session.bulk_save_objects(records)
    test_session.commit()
    return test_session


@pytest.fixture
def estlink2_scenario():
    """Load the Estlink 2 severance scenario."""
    with open(CONFIG_DIR / "scenarios" / "estlink2_severance.json", encoding="utf-8") as f:
        return json.load(f)
