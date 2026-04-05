"""Inference Engine.

Exposes strict predictive probabilities binding real-time topology arithmetic
to historical behavioral coefficients.
"""

import logging
import joblib
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

ARTEFACTS_DIR = Path(__file__).parent.parent / "models" / "artefacts"
MODEL_PATH = ARTEFACTS_DIR / "rf_risk_model.pkl"


class InferenceEngine:
    """Predictive inference router translating active structural geometries into risk boundaries."""
    
    def __init__(self, custom_model_path: Path | None = None):
        self.payload = None
        self.model = None
        self.feature_cols = []
        
        path = custom_model_path if custom_model_path else MODEL_PATH
        self._load_model(path)
        
    def _load_model(self, path: Path):
        """Deserializes weights from disk cache."""
        if path.exists():
            self.payload = joblib.load(path)
            self.model = self.payload.get("model")
            self.feature_cols = self.payload.get("feature_columns", [])
        else:
            logger.warning(f"No trained algorithm located at {path}. System defaulting to zero-risk.")

    def predict_risk(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """Determines likelihood [0-1 interval] tracking forward-looking infrastructure vulnerability."""
        if not self.model or df_features.empty:
            if df_features.empty:
                return pd.DataFrame(columns=["timestamp", "country_id", "risk_probability"])
            res = df_features[["timestamp", "country_id"]].copy()
            res["risk_probability"] = 0.0
            return res
            
        # Reconstruct canonical matrix respecting exact feature alignments
        X = pd.DataFrame(index=df_features.index)
        for col in self.feature_cols:
            if col in df_features.columns:
                X[col] = df_features[col]
            else:
                X[col] = 0.0 # Missing metric decay map
                
        # Derive structural probability scalar
        probs = self.model.predict_proba(X)
        
        # Scikit strictly returns (N, 2) when trained on binary classes
        if len(self.model.classes_) == 2:
            prob_1 = probs[:, 1]
        else:
            # Fallback for degenerate training sets avoiding dimension crashes
            prob_1 = [0.0] * len(X)
            
        if df_features.empty:
            return pd.DataFrame(columns=["timestamp", "country_id", "risk_probability"])
        res = df_features[["timestamp", "country_id"]].copy()
        res["risk_probability"] = prob_1
        
        return res
