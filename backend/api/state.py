"""API router for platform state bounds."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta

from backend.db.session import get_db
from backend.db.models import DomainScore
from backend.simulation.margin import MarginCalculator
from backend.scoring.escalation_composite import EscalationComposite

router = APIRouter()

@router.get("/scores")
def get_global_scores(db: Session = Depends(get_db)):
    """Returns the latest scores for all domains across all focus countries."""
    # Efficient fetch of the latest records
    stmt = (
        select(DomainScore)
        .order_by(DomainScore.entity_id, DomainScore.domain_id, DomainScore.timestamp.desc())
    )
    # Deduplicate in Python to ensure strictly latest per entity-domain pair
    records = db.execute(stmt).scalars().all()
    
    latest = {}
    for r in records:
        key = (r.entity_id, r.domain_id)
        if key not in latest:
            latest[key] = {
                "country_id": r.entity_id,
                "domain_id": r.domain_id,
                "score": r.score,
                "velocity": r.velocity,
                "timestamp": r.timestamp.isoformat(),
                "data_coverage": r.data_coverage
            }
            
    return {"scores": list(latest.values())}


@router.get("/scores/{country_id}")
def get_country_scores(country_id: str, db: Session = Depends(get_db)):
    """Returns the comprehensive radar 8-domain bounds for a specific country."""
    stmt = (
        select(DomainScore)
        .where(DomainScore.entity_id == country_id)
        .order_by(DomainScore.timestamp.desc())
    )
    records = db.execute(stmt).scalars().all()
    
    latest_domains = {}
    for r in records:
        if r.domain_id not in latest_domains:
            latest_domains[r.domain_id] = {
                "domain_id": r.domain_id,
                "score": r.score,
                "velocity": r.velocity,
                "data_coverage": r.data_coverage,
                "anomaly_flag": r.anomaly_flag
            }
            
    if not latest_domains:
        raise HTTPException(status_code=404, detail="No domain scores found for this country")
        
    return {"country_id": country_id, "domains": list(latest_domains.values())}


@router.get("/margins")
def get_state_margins(db: Session = Depends(get_db)):
    """Fetches real-time dynamic N-1 constraint margins across the topology."""
    calc = MarginCalculator(db)
    margins = calc.calculate_all()
    return {"margins": margins}


@router.get("/alerts")
def get_active_alerts(db: Session = Depends(get_db)):
    """Surfaces any domains flagged synthetically via geometric z-score velocity variance."""
    stmt = (
        select(DomainScore)
        .where(DomainScore.anomaly_flag == True)
        # Bounding to recent window assuming live decay
        .where(DomainScore.timestamp >= datetime.utcnow() - timedelta(days=2))
    )
    records = db.execute(stmt).scalars().all()
    
    # Isolate uniquely anomalous domains
    alerts = []
    seen = set()
    for r in records:
        key = (r.entity_id, r.domain_id)
        if key not in seen:
            alerts.append({
                "country_id": r.entity_id,
                "domain_id": r.domain_id,
                "timestamp": r.timestamp.isoformat(),
                "velocity_deviation": r.velocity,
                "type": "statistical_anomaly"
            })
            seen.add(key)
            
    return {"alerts": alerts}
