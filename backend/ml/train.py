"""Model Training Pipeline.

Trains a Random Forest Classifier aligning retrospective domain geometry arrays
with temporal outage bounding boxes.
"""

import logging
import joblib
import pandas as pd
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.ml.features import FeatureEngineer
from backend.ml.labels import LabelGenerator

logger = logging.getLogger(__name__)

ARTEFACTS_DIR = Path(__file__).parent.parent / "models" / "artefacts"


class ModelTrainer:
    """Supervised learning harness spanning features from DB and JSON ground truth."""
    
    def __init__(self, session: Session):
        self.session = session
        self.feature_eng = FeatureEngineer(session)
        self.label_gen = LabelGenerator()
        
    def create_dataset(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fully aligned training matrix binding flat features to predictive labels."""
        df_features = self.feature_eng.generate_features(start_date, end_date)
        if df_features.empty:
            return pd.DataFrame()
            
        df_labels = self.label_gen.get_labels(df_features)
        
        # Inner join perfectly overlapping datasets matching by exact temporal keys
        df_merged = pd.merge(df_features, df_labels, on=["timestamp", "country_id"])
        return df_merged

    def train_and_save(self, start_date: datetime, end_date: datetime) -> str:
        """Trains calibration weights using RF Classifier and serializes the binary model payload."""
        df = self.create_dataset(start_date, end_date)
        if df.empty:
            raise ValueError("No temporal overlap mapped. Check feature timeframe bindings.")
            
        # Isolate numerical predictors
        drop_cols = ["timestamp", "country_id", "label"]
        X = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
        X = X.select_dtypes(include=['number'])
        y = df["label"]
        
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            # Class weight balanced explicitly to surface rare infrastructure disruptions structurally
            ("rf", RandomForestClassifier(n_estimators=100, max_depth=5, class_weight="balanced", random_state=42))
        ])
        
        try:
            pipeline.fit(X, y)
        except ValueError as e:
            logger.error(f"Fitting algorithm crashed (usually caused by single-class arrays in short windows). {e}")
            raise e
        
        ARTEFACTS_DIR.mkdir(parents=True, exist_ok=True)
        model_path = ARTEFACTS_DIR / "rf_risk_model.pkl"
        
        payload = {
            "model": pipeline,
            "feature_columns": list(X.columns),
            "trained_at": datetime.utcnow().isoformat(),
            "samples": len(X)
        }
        
        joblib.dump(payload, model_path)
        logger.info(f"Predictive artifact committed to {model_path} ({len(X)} instances).")
        
        return str(model_path)
