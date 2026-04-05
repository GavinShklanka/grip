"""Scoring layer initialization and DB orchestrator."""

import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.db.models import IndicatorValue, DomainScore
from backend.scoring.domain_index import compute_domain_scores

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
with open(CONFIG_DIR / "domains.json") as f:
    DOMAINS_CONFIG = json.load(f)

class ScoringOrchestrator:
    """Database binding orchestrator mediating read/write loops for pure scoring engines."""
    
    def __init__(self, session: Session):
        self.session = session
        
    def _fetch_indicators(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        stmt = (
            select(IndicatorValue)
            .where(IndicatorValue.timestamp >= start_date)
            .where(IndicatorValue.timestamp <= end_date)
        )
        data = self.session.execute(stmt).scalars().all()
        if not data:
            return pd.DataFrame()
            
        return pd.DataFrame([
            {
                "indicator_id": d.indicator_id,
                "country_id": d.country_id,
                "timestamp": d.timestamp,
                "raw_value": d.raw_value
            }
            for d in data
        ])

    def run_scoring(self, start_date: datetime, end_date: datetime, target_freq: str = "D") -> int:
        """Pulls indicators from sqlite, runs pure function compute_domain_scores, commits to DB."""
        df_indicators = self._fetch_indicators(start_date, end_date)
        if df_indicators.empty:
            return 0
            
        df_scores = compute_domain_scores(df_indicators, DOMAINS_CONFIG, target_freq=target_freq)
        if df_scores.empty:
            return 0
            
        now = datetime.utcnow()
        domain_rows = []
        for _, row in df_scores.iterrows():
            domain_rows.append(DomainScore(
                domain_id=row["domain_id"],
                entity_type="country",
                entity_id=row["country_id"],
                timestamp=row["timestamp"],
                score=row["score"],
                velocity=row["velocity"],
                data_coverage=row["data_coverage"],
                anomaly_flag=row["anomaly_flag"],
                computed_at=now
            ))
            
        self.session.bulk_save_objects(domain_rows)
        self.session.commit()
        return len(domain_rows)
