import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
from backend.main import app
from backend.db.session import get_db
from backend.db.models import Base

@pytest.fixture(scope="module")
def test_db():
    from sqlalchemy.pool import StaticPool
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def client(test_db):
    def override_get_db():
        yield test_db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_state_endpoints(client):
    response = client.get("/api/state/scores")
    assert response.status_code == 200
    assert "scores" in response.json()
    
    response = client.get("/api/state/margins")
    assert response.status_code == 200
    assert "margins" in response.json()
    
    # We haven't populated domains for a specific country in this basic test DB
    response = client.get("/api/state/scores/INVALID_COUNTRY")
    assert response.status_code == 404
    
    response = client.get("/api/state/alerts")
    assert response.status_code == 200
    assert "alerts" in response.json()


def test_topology_endpoints(client):
    response = client.get("/api/topology/graph")
    assert response.status_code == 200
    data = response.json()
    assert "graph" in data
    assert "links" in data["graph"]
    
    response = client.get("/api/topology/outages")
    assert response.status_code == 200
    assert "outages" in response.json()


def test_scenario_endpoints(client):
    response = client.get("/api/scenario/prebuilt")
    assert response.status_code == 200
    # Checks config/scenarios exist 
    assert "scenarios" in response.json()


def test_forecast_endpoints(client):
    response = client.get("/api/forecast/risk")
    assert response.status_code == 200
    assert "predictions" in response.json()
    
    response = client.get("/api/forecast/alerts")
    assert response.status_code == 200
    assert "alerts" in response.json()


def test_meta_endpoints(client):
    response = client.get("/api/meta/system-status")
    assert response.status_code == 200
    assert "api_bypassed" in response.json()
    
    response = client.get("/api/meta/provenance/energy_dependence/LT")
    assert response.status_code == 200
    assert response.json()["domain_id"] == "energy_dependence"
