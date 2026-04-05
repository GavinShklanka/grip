"""API router for predictive machine learning vectors."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.db.session import get_db
from backend.ml.features import FeatureEngineer
from backend.ml.inference import InferenceEngine
from backend.ml.labels import LabelGenerator

router = APIRouter()


@router.get("/risk")
def get_predictive_risk(db: Session = Depends(get_db)):
    """Yields deterministic infrastructure breakage probabilities bound to 7-day feature paths."""
    # Build current features for recent window
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    eng = FeatureEngineer(db)
    df_features = eng.generate_features(start_date, end_date)
    
    inf = InferenceEngine()
    df_probs = inf.predict_risk(df_features)
    
    # Format latest probability per country
    latest = {}
    if not df_probs.empty:
        # Group by country and get the latest timestamp probability
        for country in df_probs["country_id"].unique():
            df_c = df_probs[df_probs["country_id"] == country].sort_values("timestamp")
            if not df_c.empty:
                last_row = df_c.iloc[-1]
                latest[country] = {
                    "country_id": country,
                    "timestamp": last_row["timestamp"].isoformat(),
                    "risk_probability": float(last_row["risk_probability"])
                }
                
    return {"predictions": list(latest.values())}


@router.get("/alerts")
def get_predictive_alerts(db: Session = Depends(get_db)):
    """Filters base probabilities isolating entities breaching deterministic threshold models."""
    res = get_predictive_risk(db)
    
    alerts = []
    # threshold = 0.5 binary classifier
    for p in res.get("predictions", []):
        if p["risk_probability"] >= 0.5:
            p["severity"] = "critical" if p["risk_probability"] >= 0.8 else "warning"
            alerts.append(p)
            
    return {"alerts": alerts}


@router.get("/backtest")
def get_backtest_overlap():
    """Surfaces the ground truth evaluation matrix displaying event mappings vs labels."""
    lg = LabelGenerator()
    
    return {
        "documented_disruptions": len(lg.events),
        "events": lg.events,
    }
