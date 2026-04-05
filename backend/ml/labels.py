"""Label Generator for Predictive Risk Model.

Synthesizes backward-looking binary labels relative to historical
infrastructure disruption events for supervised learning backtesting.
"""

import json
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

SEED_DIR = Path(__file__).parent.parent.parent / "data" / "seed"


class LabelGenerator:
    """Reads structured seed event horizons to assign forward-looking risk labels."""
    
    def __init__(self):
        file_path = SEED_DIR / "disruption_events.json"
        
        if not file_path.exists():
            logger.warning("No disruption_events.json found. Defers to empty list.")
            self.events = []
        else:
            with open(file_path, encoding="utf-8") as f:
                self.events = json.load(f).get("events", [])

    def get_labels(self, df_features: pd.DataFrame, target_horizon_days: int = 7) -> pd.DataFrame:
        """Assigns '1' (Danger) if an energetic disruption event occurs within `horizon` days.
        
        Parameters
        ----------
        df_features : pd.DataFrame
            The flattened feature matrix requiring target mapping.
        target_horizon_days : int
            Lead-time mapping offset. e.g. 7 days means a 1 is assigned on timestamps
            that occur up to 7 days purely before an actual outage hits.
            
        Returns
        -------
        pd.DataFrame
            DataFrame holding identical [timestamp, country_id] indexes bound tightly with `label`.
        """
        
        if df_features.empty:
            return pd.DataFrame()
            
        df_labels = df_features[["timestamp", "country_id"]].copy()
        df_labels["label"] = 0
        df_labels["timestamp"] = pd.to_datetime(df_labels["timestamp"])
        
        # Strict Positive Risk Filtering
        disruptions = [e for e in self.events if e.get("is_energy_interconnector")]
        
        for event in disruptions:
            start_date = pd.to_datetime(event["start_date"])
            
            # The danger window is purely backward-looking from the event
            # model must learn to flag 1 *before* the disruption hits, avoiding leakage.
            end_window = start_date
            start_window = start_date - pd.Timedelta(days=target_horizon_days)
            
            # Apply to the grid. In GRIP Baltic-Nordic design, interconnector
            # severances hit the collective synchronous area equivalently, though
            # some events might be bounded strictly if the config supports "affected_countries".
            mask = (df_labels["timestamp"] > start_window) & (df_labels["timestamp"] <= end_window)
            
            # Currently maps collectively unless target constraint supplied
            df_labels.loc[mask, "label"] = 1
            
        return df_labels
