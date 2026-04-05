"""Feature Engineering Pipeline.

Extracts domain scores and synthensizes trailing statistical geometries
(velocity, volatility) tailored for Random Forest ingestion.
"""

import logging
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.db.models import DomainScore

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Pipelines raw DomainScore timelines into flat rectangular predictive features."""
    
    def __init__(self, session: Session):
        self.session = session

    def generate_features(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Reads domain bounds, pivots cleanly per country, and attaches derivates."""
        
        stmt = (
            select(DomainScore)
            .where(DomainScore.timestamp >= start_date)
            .where(DomainScore.timestamp <= end_date)
            .where(DomainScore.entity_type == "country")
        )
        records = self.session.execute(stmt).scalars().all()
        if not records:
            logger.warning("No records found for feature engineering window.")
            return pd.DataFrame()
            
        df_raw = pd.DataFrame([
            {
                "country_id": r.entity_id,
                "domain_id": r.domain_id,
                "timestamp": r.timestamp,
                "score": r.score
            }
            for r in records
        ])
        
        # Deduplicate artifacts overriding preceding runs
        df_raw = df_raw.drop_duplicates(subset=["country_id", "domain_id", "timestamp"], keep="last")
        
        # Reshape to multi-indexed rectangular set (Country -> Timestamp -> [Domains])
        try:
            df_pivot = df_raw.pivot(index=["timestamp", "country_id"], columns="domain_id", values="score")
        except ValueError as e:
            logger.error("Feature pivot failed. Duplicate indices likely unresolved.")
            raise e
            
        features = []
        countries = df_raw["country_id"].unique()
        
        for country in countries:
            # Slicing the hierarchical index for localized rolling maths
            df_c = df_pivot.xs(country, level="country_id").sort_index()
            df_c = df_c.resample("D").ffill().bfill() # Forward fill temporal gaps safely
            
            # Generate local synthetic geometric derivatives
            for col in list(df_c.columns):
                s = df_c[col]
                df_c[f"{col}_vel"] = s.diff().fillna(0.0)
                df_c[f"{col}_volatility_7d"] = s.rolling(7, min_periods=1).std().fillna(0.0)
                df_c[f"{col}_mean_7d"] = s.rolling(7, min_periods=1).mean().fillna(s)
                
            df_c["country_id"] = country
            features.append(df_c)
            
        df_final = pd.concat(features).reset_index()
        # Clean any terminal NaNs that escaped rolling bounds
        df_final = df_final.fillna(0.0)
        return df_final
