"""Escalation composite calculator."""

import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.db.models import DomainScore

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
with open(CONFIG_DIR / "domains.json", encoding="utf-8") as f:
    DOMAINS_CONFIG = json.load(f)

class EscalationComposite:
    """Calculates the composite escalation_risk score from 8 canonical domains."""
    
    def __init__(self, session: Session):
        self.session = session
        self.domain_weights = {
            d["id"]: d.get("weight_in_composite", 0.0) 
            for d in DOMAINS_CONFIG["domains"]
        }
        
    def calculate_for_country(self, country_id: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetches all domains and calculates the weighted escalation composite timeline."""
        
        stmt = (
            select(DomainScore)
            .where(DomainScore.entity_id == country_id)
            .where(DomainScore.entity_type == "country")
            .where(DomainScore.timestamp >= start_date)
            .where(DomainScore.timestamp <= end_date)
            # Only fetch canonical domains
            .where(DomainScore.domain_id.in_(self.domain_weights.keys()))
        )
        
        records = self.session.execute(stmt).scalars().all()
        if not records:
            return pd.DataFrame()
            
        df = pd.DataFrame([
            {
                "domain_id": r.domain_id,
                "timestamp": r.timestamp,
                "score": r.score,
                "data_coverage": r.data_coverage
            }
            for r in records
        ])
        
        # Deduplicate to handle multiple scoring runs
        df = df.drop_duplicates(subset=["domain_id", "timestamp"], keep="last")
        
        # Pivot so columns=domains, index=timestamp
        df_pivot = df.pivot(index="timestamp", columns="domain_id", values="score")
        
        # Multiply by weights and sum
        composite_components = []
        coverage_components = []
        
        for domain, weight in self.domain_weights.items():
            if weight == 0:
                continue
                
            if domain in df_pivot.columns:
                s = df_pivot[domain]
                composite_components.append(s * weight)
                coverage_components.append(pd.Series(np.where(s.notna(), weight, 0.0), index=s.index))
                
        if not composite_components:
            return pd.DataFrame()
            
        df_composite = pd.concat(composite_components, axis=1).sum(axis=1)
        df_active_weight = pd.concat(coverage_components, axis=1).sum(axis=1)
        
        total_weight = sum(self.domain_weights.values())
        
        df_coverage = df_active_weight / total_weight
        
        # Actual composite risk
        # The penalty structure applies here as well, so we use similar logic tracking
        # actual vs expected coverage.
        df_final = df_composite
        
        result_df = pd.DataFrame({
            "score": df_final,
            "data_coverage": df_coverage
        })
        
        result_df["country_id"] = country_id
        result_df["entity_type"] = "country"
        result_df["domain_id"] = "escalation_composite"
        
        return result_df.reset_index()

    def update_database(self, start_date: datetime, end_date: datetime) -> int:
        """Calculates for all focus countries and saves to DomainScore table."""
        # Get unique focus countries
        stmt = select(DomainScore.entity_id).distinct().where(DomainScore.entity_type == "country")
        countries = self.session.execute(stmt).scalars().all()
        
        now = datetime.utcnow()
        objects = []
        
        for c in countries:
            df = self.calculate_for_country(c, start_date, end_date)
            if df.empty:
                continue
                
            for _, row in df.iterrows():
                obj = DomainScore(
                    domain_id=row["domain_id"],
                    entity_type=row["entity_type"],
                    entity_id=row["country_id"],
                    timestamp=row["timestamp"],
                    score=float(row["score"]),
                    data_coverage=float(row["data_coverage"]),
                    computed_at=now
                )
                objects.append(obj)
                
        if objects:
            self.session.bulk_save_objects(objects)
            self.session.commit()
            
        return len(objects)
