"""ENTSOG data ingestion module."""

import logging
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

try:
    from entsog.pandas import EntsogPandasClient
except ImportError:
    EntsogPandasClient = None

from backend.config import get_settings
from backend.ingestion.base import IngestionModule
from backend.db.models import IndicatorValue

logger = logging.getLogger(__name__)


class EntsogIngestionModule(IngestionModule):
    """Fetches and derives gas flows mapping generic domains."""

    def __init__(self):
        self.settings = get_settings()
        self.client = None
        if not self.settings.demo_mode and EntsogPandasClient:
            self.client = EntsogPandasClient()

        self.points = [
            {"point": "Balticconnector", "direction": "entry", "country": "FI", "indicator": "flow_balticconnector"},
            {"point": "Kiemenai", "direction": "entry", "country": "LV", "indicator": "flow_kiemenai"},
            {"point": "GIPL", "direction": "entry", "country": "LT", "indicator": "flow_gipl"},
            {"point": "Klaipeda", "direction": "entry", "country": "LT", "indicator": "flow_klaipeda_lng"},
        ]

    @property
    def source_name(self) -> str:
        return "entsog"

    def fetch(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        if self.settings.demo_mode:
            logger.info("DEMO_MODE=True: Loading ENTSOG offline seed.")
            seed_path = Path(__file__).parent.parent.parent / "data" / "seed" / "entsog_flows.csv"
            if seed_path.exists():
                df = pd.read_csv(seed_path)
                df = df.rename(columns={"date": "timestamp", "flow_mcm": "value"})
                
                point_map = {p["point"].lower(): p for p in self.points}
                def map_point(row):
                    pid = str(row.get("point_id", "")).lower()
                    if pid in point_map:
                        return point_map[pid]["country"]
                    return None
                    
                df["country"] = df.apply(map_point, axis=1)
                return df.dropna(subset=["country"])
                
            return pd.DataFrame()

        if not self.client:
            logger.error("ENTSOG client not initialized (library missing).")
            return pd.DataFrame()

        import pytz
        tz = pytz.timezone("Europe/Brussels")
        start_tz = pd.Timestamp(start_date).tz_localize("UTC").tz_convert(tz)
        end_tz = pd.Timestamp(end_date).tz_localize("UTC").tz_convert(tz)

        frames = []
        for p in self.points:
            try:
                df_point = self.client.query_operational_data(
                    start=start_tz,
                    end=end_tz,
                    point_label=p["point"],
                    direction=p["direction"]
                )
                df_point["point_id"] = p["point"]
                df_point["country"] = p["country"]
                # Default capacities for mocked live runs
                df_point["capacity_mcm"] = 10.0
                frames.append(df_point)
            except Exception as e:
                logger.error(f"Failed fetching ENTSOG flow {p['point']}: {e}")

        if not frames:
            return pd.DataFrame()

        df = pd.concat(frames)
        df = df.reset_index().rename(columns={"index": "timestamp"})
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
            
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        if df["timestamp"].dt.tz is not None:
            df["timestamp"] = df["timestamp"].dt.tz_convert("UTC").dt.tz_localize(None)

        result_rows = []
        dates = df["timestamp"].unique()
        
        for ts in dates:
            df_ts = df[df["timestamp"] == ts]
            
            # 1. gas_import_concentration
            # Simplistic mock HHI
            for country in df_ts["country"].unique():
                df_c = df_ts[df_ts["country"] == country]
                total = df_c["value"].sum()
                hhi = sum((v/total)**2 for v in df_c["value"]) if total > 0 else 1.0
                
                result_rows.append({
                    "indicator_id": "gas_import_concentration",
                    "country_id": country,
                    "region_id": None,
                    "timestamp": ts,
                    "raw_value": float(hhi),
                    "source": self.source_name,
                    "data_quality": "current",
                })
                
            # 2. lng_utilization (specifically Klaipeda LT)
            df_klaipeda = df_ts[df_ts["point_id"].str.lower() == "klaipeda"]
            if not df_klaipeda.empty:
                flow = df_klaipeda["value"].sum()
                cap = df_klaipeda["capacity_mcm"].sum()
                if cap > 0:
                    result_rows.append({
                        "indicator_id": "lng_utilization",
                        "country_id": "LT",
                        "region_id": None,
                        "timestamp": ts,
                        "raw_value": float(flow / cap),
                        "source": self.source_name,
                        "data_quality": "current",
                    })

        df_indicators = pd.DataFrame(result_rows)

        # 3. gas_flow_disruption (Z score 30d tracking Balticconnector + overall flows)
        new_rows = []
        for country in df["country"].unique():
            df_country = df[df["country"] == country].groupby("timestamp")["value"].sum().reset_index()
            if df_country.empty:
                continue
            df_country = df_country.sort_values("timestamp").set_index("timestamp")
            
            rolling_mean = df_country["value"].rolling("30D", min_periods=1).mean()
            rolling_std = df_country["value"].rolling("30D", min_periods=1).std().replace(0, np.nan)
            
            z_scores = (df_country["value"] - rolling_mean) / rolling_std
            z_scores = z_scores.fillna(0.0)
            
            for ts, z_val in z_scores.items():
                new_rows.append({
                    "indicator_id": "gas_flow_disruption",
                    "country_id": country,
                    "region_id": None,
                    "timestamp": ts,
                    # We report the absolute magnitude of disruption logically
                    "raw_value": float(abs(z_val)),
                    "source": self.source_name,
                    "data_quality": "current",
                })

        df_indicators = pd.concat([df_indicators, pd.DataFrame(new_rows)], ignore_index=True)
        return df_indicators

    def load(self, df: pd.DataFrame, session: Session) -> int:
        if df.empty:
            return 0
            
        objects = []
        for _, row in df.iterrows():
            obj = IndicatorValue(**row.to_dict())
            objects.append(obj)

        session.bulk_save_objects(objects)
        session.commit()
        return len(objects)
